import "../app/globals.css";
import "./App.css";
import { useCallback, useEffect, useState } from "react";
import AudioWaveform from "@/components/audioWaveForm";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface SystemInfo {
  cpu_count: number;
  total_memory_gb: number;
  free_disk_space_gb: number;
  os_info: string;
  has_gpu: boolean;
  is_compatible: boolean;
}

function AlertSystemInfo({ isAlert }: { isAlert: boolean }) {
  return (
    <AlertDialog open={isAlert}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            Your System is currently incompatible
          </AlertDialogTitle>
          <AlertDialogDescription>
            Please make sure your system is compatible with the application.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Sorry!</AlertDialogCancel>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

function App() {
  const [isSystemCompatible, setIsSystemCompatible] = useState<boolean>(false);
  const getSystemInfo = async (): Promise<SystemInfo> => {
    const res = await fetch("http://localhost:8000/checkSystem");
    const data = await res.json();
    return data;
  };

  const getSystemInfoCB = useCallback(async () => {
    const data = await getSystemInfo();
    if (data.is_compatible === false) {
      setIsSystemCompatible(true);
    }
  }, []);

  useEffect(() => {
    getSystemInfoCB();
    return () => {
      setIsSystemCompatible(false);
    };
  }, [getSystemInfoCB]);

  return (
    <div className="bg-white/60  rounded ">
      <AlertSystemInfo isAlert={isSystemCompatible}></AlertSystemInfo>
      <AudioWaveform></AudioWaveform>
    </div>
  );
}

export default App;
