import { useCallback } from "react";

interface StreamApiProps {
  setText: React.Dispatch<React.SetStateAction<string>>;
}

export default function useStreamApi({ setText }: StreamApiProps) {
  const transcribeStreamApi = useCallback(async (formData: FormData) => {
    try {
      // 通过 fetch 上传文件
      const uploadResponse = await fetch(
        "http://localhost:8000/transcribe-stream",
        {
          method: "POST",
          body: formData,
        }
      );

      if (
        !uploadResponse.ok ||
        uploadResponse.status !== 200 ||
        !uploadResponse.body
      ) {
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
          const rawChunk = chunk.trim().replace(/^data: /, "");
          const data: {
            transcription: { timestamp: [number, number]; text: string };
          } = JSON.parse(rawChunk);

          if (data.transcription) {
            const { timestamp, text } = data.transcription;
            const time = `(${
              timestamp[0] !== null ? timestamp[0].toFixed(2) : "Unknown"
            }s - ${
              timestamp[1] !== null ? timestamp[1].toFixed(2) : "Unknown"
            }s)`;

            setText((prevText) => prevText + `\n${time}: ${text}`);
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
  }, []);

  const transcribeApi = useCallback(async (formData: FormData) => {
    fetch("http://localhost:8000/transcribe", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then(
        (data: {
          transcription: { timestamp: [number, number]; text: string }[];
        }) => {
          setText("");
          if (data.transcription && Array.isArray(data.transcription)) {
            data.transcription.forEach((item) => {
              const { timestamp, text } = item;
              const time = `(${
                timestamp[0] !== null
                  ? timestamp[0].toString().padStart(0)
                  : "Unknown"
              }s - ${
                timestamp[1] !== null
                  ? timestamp[1].toString().padStart(0)
                  : "Unknown"
              }s)`;
              setText((prevText) => prevText + `\n${time}: ${text}`);
            });
          } else {
            console.error(
              "Transcription failed or returned unexpected format."
            );
          }
        }
      )
      .catch((error) => {
        console.error("Error during transcription request:", error);
      });
  }, []);

  return { transcribeStreamApi, transcribeApi };
}
