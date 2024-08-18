import { useRef, useEffect, useCallback } from "react";
import RecordButton from "@/components/recordButton";
import useRecorder from "@/composables/useRecorder";

const AudioWaveform = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawAudioRef = useRef<number | null>(null);
  const {
    startRecording,
    stopRecording,
    isRecording,
    dataArrayRef,
    analyserRef,
  } = useRecorder();

  const drawWaveform = useCallback(() => {
    if (!analyserRef.current || !canvasRef.current || !dataArrayRef.current)
      return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext("2d");
    if (!canvasCtx) return;

    const bufferLength = analyserRef.current.frequencyBinCount;

    const draw = () => {
      drawAudioRef.current = requestAnimationFrame(draw);

      analyserRef.current!.getByteTimeDomainData(dataArrayRef.current!);

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas

      // Set up styles for the heart-like waveform
      canvasCtx.lineWidth = 2;
      const gradient = canvasCtx.createLinearGradient(0, 0, canvas.width, 0);
      gradient.addColorStop(0, "red"); // Start with red
      gradient.addColorStop(0.5, "green"); // Transition to green
      gradient.addColorStop(1, "blue"); // End with blue
      canvasCtx.strokeStyle = gradient;
      canvasCtx.beginPath();

      const sliceWidth = (canvas.width * 1.0) / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArrayRef.current![i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }

        // To make it look more like a heart rate monitor, add some variability
        if (i % 20 === 0) {
          x += sliceWidth * 2; // Create a small jump in the waveform
        } else {
          x += sliceWidth;
        }
      }

      canvasCtx.lineTo(canvas.width, canvas.height / 2);
      canvasCtx.stroke();
    };

    draw();
  }, [dataArrayRef, analyserRef]);

  useEffect(() => {
    if (isRecording) {
      drawWaveform();
    } else {
      if (drawAudioRef.current) {
        cancelAnimationFrame(drawAudioRef.current);
      }
    }
    return () => {
      if (drawAudioRef.current) {
        cancelAnimationFrame(drawAudioRef.current);
      }
    };
  }, [isRecording, drawWaveform]);

  return (
    <div>
      <canvas
        ref={canvasRef}
        width="600"
        height="200"
        className=" border-black border-2 mb-2"
      ></canvas>
      <RecordButton
        record={isRecording ? stopRecording : startRecording}
        isRecording={isRecording}
      >
        {isRecording ? "Stop Recording" : "Start Recording"}
      </RecordButton>
    </div>
  );
};

export default AudioWaveform;
