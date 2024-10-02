import { useCallback } from "react";

export interface voiceData {
  prompt: string;
  description: string;
  recordID: string;
}

export default function useVoiceApi({
  prompt,
  description,
  recordID = localStorage.getItem("record_id") || "",
}: voiceData) {
  const playVoice: () => void = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/tts/generate-voice", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          prompt,
          description,
          original_record_id: recordID,
        }),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio
        .play()
        .catch((error) => console.error("Error playing audio:", error));
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  }, [description, prompt, recordID]);

  return {
    playVoice,
  };
}
