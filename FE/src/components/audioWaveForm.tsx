import { useRef, useEffect, useCallback, useState } from "react";
import ToggleEventOption from "@/components/toggleEventOption";
import RecordButton from "@/components/recordButton";
import useRecorder from "@/composables/useRecorder";
import useStreamApi from "@/composables/useStreamApi";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

import { SpeakerLoudIcon } from "@radix-ui/react-icons";

const AudioWaveform = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawAudioRef = useRef<number | null>(null);
  const [text, setText] = useState("");
  const [isOption, setIsOption] = useState<Array<"StreamApi" | "TimeStamp">>(
    []
  );
  // TODO: add playapi and useDrawBar composable
  const playVoice = () => {
    fetch("http://localhost:8000/tts/generate-voice", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        prompt: text,
        description: "You are a voice model",
        original_record_id: localStorage.getItem("record_id") || "",
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

  const { transcribeStreamApi, transcribeApi } = useStreamApi({
    setText,
    timeStamp: isOption.includes("TimeStamp"),
  });

  const {
    startRecording,
    stopRecording,
    isRecording,
    dataArrayRef,
    analyserRef,
    getSamples,
  } = useRecorder({
    transcribeApi: isOption.includes("StreamApi")
      ? transcribeStreamApi
      : transcribeApi,
    timeStamp: isOption.includes("TimeStamp"),
  });

  const drawWaveform = useCallback(() => {
    if (!analyserRef.current || !canvasRef.current || !dataArrayRef.current)
      return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext("2d")!;

    const bar = ({
      x,
      y,
      width,
      height,
      color,
      i,
    }: {
      x: number;
      y: number;
      width: number;
      height: number;
      color: string;
      i: number;
    }) => {
      const barItem = {
        x: x,
        y: y,
        width: width,
        height: height,
        color: color,
        i,
      };
      const update = (micInput: number) => {
        const sound = micInput * 1000;
        if (sound > barItem.height) {
          barItem.height = sound;
        } else {
          barItem.height -= barItem.height * 0.05;
        }
      };
      const draw = (canvasCtx: CanvasRenderingContext2D) => {
        canvasCtx.strokeStyle = barItem.color;
        canvasCtx.save();

        canvasCtx.translate(canvas.width / 2, canvas.height / 2);
        canvasCtx.rotate(i * 0.05);

        canvasCtx.beginPath();
        canvasCtx.moveTo(0, 0);
        canvasCtx.lineTo(0, barItem.height);
        canvasCtx.stroke();

        canvasCtx.restore();
      };
      return { update, draw };
    };

    const bars = [] as ReturnType<typeof bar & { i: number }>[];

    const createBars = () => {
      for (let i = 0; i < 256; i++) {
        const colors = `hsl(${i * 2},100%,50%)`;
        bars.push(
          bar({
            x: 0,
            y: i * 1.5,
            width: 5,
            height: 10,
            color: colors,
            i,
          })
        );
      }
    };

    createBars();

    const draw = () => {
      if (dataArrayRef.current) {
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        bars.forEach((bar, i) => {
          const samples = getSamples()!;

          bar.update(samples[i]);
          bar.draw(canvasCtx);
        });
      }

      drawAudioRef.current = requestAnimationFrame(draw);
    };
    draw();
  }, [dataArrayRef, analyserRef, getSamples]);

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
    <div className="px-4 py-6">
      <div>
        <h2 className="font-mono text-2xl my-2">VoiceReactify</h2>
        <div className="flex my-2 justify-end">
          <ToggleEventOption
            isOption={isOption}
            setIsOption={setIsOption}
          ></ToggleEventOption>
        </div>
        <div className="mb-4 w-full">
          <canvas
            ref={canvasRef}
            className=" border-white border-2 w-full h-[200px] bg-gray-200"
          ></canvas>
        </div>
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
          placeholder="TTS record text"
          rows={6}
          disabled
          defaultValue={text}
        />
        <Button variant="outline" size="icon" onClick={playVoice}>
          <SpeakerLoudIcon className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default AudioWaveform;
