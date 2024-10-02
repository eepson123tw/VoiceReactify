import { useRef, useEffect, useState } from "react";
import ToggleEventOption from "@/components/toggleEventOption";
import RecordButton from "@/components/recordButton";
import useRecorder from "@/composables/useRecorder";
import useStreamApi from "@/composables/useStreamApi";
import useVoiceApi from "@/composables/useVoiceApi";
import useDraw from "@/composables/useDraw";

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
  const useTimeStamp = isOption.includes("TimeStamp");
  // to use voice api gen voice
  const { playVoice } = useVoiceApi({
    prompt: text,
    description: "You are a voice model",
    recordID: localStorage.getItem("record_id") || "",
  });
  // to define use stream api or not
  const { transcribeStreamApi, transcribeApi } = useStreamApi({
    setText,
    timeStamp: isOption.includes("TimeStamp"),
  });
  // to use recorder composable
  const {
    startRecording,
    stopRecording,
    isRecording,
    dataArrayRef,
    analyserRef,
    getSamples,
  } = useRecorder({
    transcribeApi: useTimeStamp ? transcribeStreamApi : transcribeApi,
    timeStamp: isOption.includes("TimeStamp"),
  });

  const { drawWaveform } = useDraw({
    analyserRef,
    canvasRef,
    dataArrayRef,
    drawAudioRef,
    getSamples,
  });

  useEffect(() => {
    const currentDrawAudioRef = drawAudioRef.current;
    if (isRecording) {
      drawWaveform();
    } else {
      if (currentDrawAudioRef) {
        cancelAnimationFrame(currentDrawAudioRef);
      }
    }
    // Cleanup function uses the copied ref value
    return () => {
      if (currentDrawAudioRef) {
        cancelAnimationFrame(currentDrawAudioRef);
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
