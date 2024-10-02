import { useCallback } from "react";
import type { ChartData } from "@/types/const";

export default function useAssignmentApi({
  reference_text,
  reference_path,
}: {
  reference_text: string;
  reference_path: string;
}) {
  const getAssignmentData: () => Promise<ChartData> = useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/voice-assignment/analysis",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            reference_text,
            reference_path,
          }),
        }
      );
      if (!response.ok) {
        throw new Error(`Failed to fetch data with status ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(error);
      throw error;
    }
  }, [reference_text, reference_path]);

  return {
    getAssignmentData,
  };
}
