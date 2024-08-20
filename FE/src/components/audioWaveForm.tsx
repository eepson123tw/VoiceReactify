import { useRef, useEffect, useCallback, useState } from "react";
import RecordButton from "@/components/recordButton";
import useRecorder from "@/composables/useRecorder";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

import { SpeakerLoudIcon } from "@radix-ui/react-icons";

const AudioWaveform = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawAudioRef = useRef<number | null>(null);
  const [text, setText] = useState("");

  const transcribeApi = useCallback(async (formData: FormData) => {
    fetch("http://localhost:8000/transcribe", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.transcription) {
          setText("");
          setText(data.transcription);
        } else {
          console.error("Transcription failed or returned unexpected format.");
        }
      })
      .catch((error) => {
        console.error("Error during transcription request:", error);
      });
  }, []);

  const playVoice = () => {
    fetch("http://localhost:8000/generate-voice", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        prompt: text,
        description: "This is a test description",
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob(); // We expect a WAV file in response
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio
          .play()
          .catch((error) => console.error("Error playing audio:", error));
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  };

  const {
    startRecording,
    stopRecording,
    isRecording,
    dataArrayRef,
    analyserRef,
  } = useRecorder({
    transcribeApi,
  });

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
    <div className="shadow-xl  px-4 py-6 rounded">
      <div>
        <h2 className=" font-mono text-2xl my-2">Audio Recorder</h2>
        <canvas
          ref={canvasRef}
          width="600"
          height="200"
          className=" border-black border-2 mb-4"
        ></canvas>
        <RecordButton
          record={isRecording ? stopRecording : startRecording}
          isRecording={isRecording}
        >
          {isRecording ? "Stop" : "Start"}
        </RecordButton>
      </div>
      <div className="flex flex-col gap-1">
        <Textarea
          className="mt-2"
          placeholder="Press button to transcribe"
          defaultValue={text}
        ></Textarea>
        <Button variant="outline" size="icon" onClick={playVoice}>
          <SpeakerLoudIcon className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default AudioWaveform;
