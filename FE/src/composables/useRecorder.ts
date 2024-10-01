import { useState, useRef, useCallback, useEffect } from "react";

interface UseRecorderProps {
  transcribeApi: (file: FormData) => Promise<void>;
  timeStamp: boolean;
}

const useRecorder = ({ transcribeApi, timeStamp }: UseRecorderProps) => {
  const audioContextRef = useRef<AudioContext | null>(null); // AudioContext 物件的引用，用來處理音訊信號，產生播放和分析屬性。
  const analyserRef = useRef<AnalyserNode | null>(null); // AnalyserNode 的引用，用於分析音訊信號，視覺化或獲取頻譜數據。
  const audioChunksRef = useRef<Blob[]>([]); // 儲存錄音數據的引用 Blob 物件。
  const mediaRecorderRef = useRef<MediaRecorder | null>(null); // MediaRecorder 的引用，用來處理錄音的控制
  const dataArrayRef = useRef<Uint8Array | null>(null); // 儲存 AnalyserNode 數據的 Uint8Array 的引用，用於處理分析結果
  const [isRecording, setIsRecording] = useState(false);

  const initAudio = () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext ||
        window.AudioContext)({ sampleRate: 48000 });
      analyserRef.current = audioContextRef.current.createAnalyser(); // expose audio time and frequency data to create visualizations
    }
    return audioContextRef.current.state === "suspended"
      ? audioContextRef.current.resume()
      : Promise.resolve();
  };

  const startRecording = useCallback(async () => {
    await initAudio();

    if (!audioContextRef.current || !analyserRef.current) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); //媒體串流的解析 promise incudes audio and video, need user apply to use audio
      const source = audioContextRef.current.createMediaStreamSource(stream); // cover the stream to audio nodes
      // 創建一個 MediaStreamAudioSourceNode 來處理音訊流，並將其連接到 analyserRef 進行分析
      mediaRecorderRef.current = new MediaRecorder(stream);
      analyserRef.current.fftSize = 512; // 設置 FFT 的大小，這將影響分析的精度 must be a power of 2
      const bufferLength = analyserRef.current.frequencyBinCount; // 代表頻譜數據的數組大小 = fftSize / 2 => 256
      dataArrayRef.current = new Uint8Array(bufferLength); // Uint8Array 是一個無符號的 8 位整數數組，適合用來存儲頻譜分析結果中的每個頻率值。 0~255
      source.connect(analyserRef.current); // 麥克風的音訊數據進行實時分析的步驟。
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data); // 每個音訊片段存儲在 audioChunksRef 中
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  }, []);

  const getSamples = (): number[] | undefined => {
    if (!analyserRef.current || !dataArrayRef.current) return;
    analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
    const normSamples = Array.from(dataArrayRef.current).map(
      (sample) => sample / 128 - 1
    ); // Normalize the samples to [-1, 1]

    return normSamples;
  };

  const getVolumes = () => {
    if (!analyserRef.current || !dataArrayRef.current) return;
    analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
    const normSamples = Array.from(dataArrayRef.current).map(
      (sample) => sample / 128 - 1
    ); // Normalize the samples to [-1, 1]
    let sum = 0;
    normSamples.forEach((sample) => {
      sum += sample * sample; // use the square of the sample as the volume
    });
    const volume = Math.sqrt(sum / normSamples.length); // calculate the root mean square of the volume
    return volume;
  };

  const stopRecording = useCallback(() => {
    setIsRecording(false);
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        // 清空音頻片段數據
        audioChunksRef.current = [];
        // 創建FormData並附加音頻文件
        const formData = new FormData();
        formData.append("file", blob, "recording.wav");
        formData.append("return_timestamps", `${timeStamp}`);
        transcribeApi(formData); // send the audio file to the transcribeApi
      };
    }
  }, [transcribeApi, timeStamp]);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return {
    initAudio,
    startRecording,
    stopRecording,
    isRecording,
    dataArrayRef,
    analyserRef,
    getSamples,
    getVolumes,
  };
};

export default useRecorder;
