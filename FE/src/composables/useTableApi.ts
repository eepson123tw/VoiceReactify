import { useCallback } from "react";

export interface RecordData {
  id: number;
  filename: string;
  filetype: string;
  duration: number;
  size: number;
  createtime: string;
  filepath: string;
  transcript: string;
  language: string;
  status: string;
  error_message: string;
  parent_id: number;
}

export default function useTableApi() {
  const getAllTableData: () => Promise<RecordData[]> = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/voice-records");
      if (!response.ok) {
        throw new Error(`Failed to fetch data with status ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(error);
    }
  }, []);
  return {
    getAllTableData,
  };
}
