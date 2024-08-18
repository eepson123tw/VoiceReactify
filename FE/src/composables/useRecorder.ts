import { useState, useRef, useCallback, useEffect } from "react";

const useRecorder = () => {
  const audioContextRef = useRef<AudioContext | null>(null); // AudioContext 物件的引用，用來處理音訊信號。
  const analyserRef = useRef<AnalyserNode | null>(null); // AnalyserNode 的引用，用於分析音訊信號，視覺化或獲取頻譜數據。
  const audioChunksRef = useRef<Blob[]>([]); // 儲存錄音數據的引用 Blob 物件。
  const mediaRecorderRef = useRef<MediaRecorder | null>(null); // MediaRecorder 的引用，用來處理錄音的控制
  const dataArrayRef = useRef<Uint8Array | null>(null); // 儲存 AnalyserNode 數據的 Uint8Array 的引用，用於處理分析結果
  const [isRecording, setIsRecording] = useState(false);

  const initAudio = () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext ||
        window.AudioContext)({ sampleRate: 48000 });
      analyserRef.current = audioContextRef.current.createAnalyser();
    }
    return audioContextRef.current.state === "suspended"
      ? audioContextRef.current.resume()
      : Promise.resolve();
  };
  const startRecording = useCallback(async () => {
    await initAudio();

    if (!audioContextRef.current || !analyserRef.current) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      // 創建一個 MediaStreamAudioSourceNode 來處理音訊流，並將其連接到 analyserRef 進行分析
      mediaRecorderRef.current = new MediaRecorder(stream);

      // 每個音訊片段存儲在 audioChunksRef 中
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      mediaRecorderRef.current.start();
      source.connect(analyserRef.current); // 麥克風的音訊數據進行實時分析的步驟。
      const bufferLength = analyserRef.current.frequencyBinCount; // 代表頻譜數據的數組大小
      dataArrayRef.current = new Uint8Array(bufferLength); // Uint8Array 是一個無符號的 8 位整數數組，適合用來存儲頻譜分析結果中的每個頻率值。
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    setIsRecording(false);
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = "recording.wav";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        audioChunksRef.current = []; // Clear audio chunks
      };
    }
  }, []);

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
  };
};

export default useRecorder;
