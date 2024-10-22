import { useCallback } from "react";

interface StreamApiProps {
  setText: React.Dispatch<React.SetStateAction<string>>;
  timeStamp: boolean;
}

type Transcription<T> = T extends true
  ? {
      transcription: { timestamp: [number, number]; text: string }[];
      record_id: number;
    }
  : {
      transcription: string;
      record_id: number;
    };

export default function useStreamApi({ setText, timeStamp }: StreamApiProps) {
  type CurrentTranscription = Transcription<typeof timeStamp>;

  const transcribeStreamApi = useCallback(
    async (formData: FormData) => {
      localStorage.removeItem("record_id");
      try {
        const uploadResponse = await fetch(
          "http://localhost:8000/transcription/transcribe-stream",
          {
            method: "POST",
            body: formData,
          }
        );

        if (!uploadResponse.ok || !uploadResponse.body) {
          throw new Error(
            `File upload failed with status ${uploadResponse.status}`
          );
        }

        const reader = uploadResponse.body.getReader();
        const decoder = new TextDecoder();

        setText("");

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });

          try {
            const transcribeChunk = chunk.trim().replace(/^data: /, "");
            const rawChunkJson = JSON.parse(transcribeChunk);
            const rawChunkJsonTranscription = JSON.parse(
              rawChunkJson.chunk.trim().replace(/^data: /, "")
            );

            const data: {
              transcription: { timestamp: [number, number]; text: string };
            } = rawChunkJsonTranscription;
            localStorage.setItem("record_id", rawChunkJson.voice_record_id);
            if (data.transcription && timeStamp) {
              const { timestamp, text } = data.transcription;
              const time = `(${
                timestamp[0] !== null ? timestamp[0].toFixed(2) : "Unknown"
              }s - ${
                timestamp[1] !== null ? timestamp[1].toFixed(2) : "Unknown"
              }s)`;
              setText((prevText) => prevText + `\n${time}: ${text}`);
            } else if (!timeStamp && typeof data.transcription) {
              setText((prevText) => prevText + `${data.transcription}`);
            } else {
              console.error(
                "Transcription failed or returned unexpected format."
              );
            }
          } catch (e) {
            console.error("Failed to parse chunk as JSON", e);
          }
        }
      } catch (error) {
        console.error("Error during transcription process:", error);
      }
    },
    [setText, timeStamp]
  );

  const transcribeApi = useCallback(
    async (formData: FormData) => {
      localStorage.removeItem("record_id");
      try {
        const response = await fetch(
          "http://localhost:8000/transcription/transcribe",
          {
            method: "POST",
            body: formData,
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: CurrentTranscription = await response.json();
        setText("");
        localStorage.setItem("record_id", data.record_id.toString());

        if (timeStamp && Array.isArray(data.transcription)) {
          data.transcription.forEach(({ timestamp, text }) => {
            const time = `(${timestamp[0]?.toFixed(2) || "Unknown"}s - ${
              timestamp[1]?.toFixed(2) || "Unknown"
            }s)`;

            setText((prevText) => prevText + `\n${time}: ${text}`);
          });
        } else if (!timeStamp && typeof data.transcription === "string") {
          setText(data.transcription);
        } else {
          console.error("Transcription failed or returned unexpected format.");
        }
      } catch (error) {
        console.error("Error during transcription request:", error);
      }
    },
    [setText, timeStamp]
  );

  return { transcribeStreamApi, transcribeApi };
}
