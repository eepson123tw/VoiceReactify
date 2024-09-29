import "../app/globals.css";
import "./App.css";
import { useCallback, useEffect, useState } from "react";

import AudioWaveform from "@/components/audioWaveForm";
import AudioTable from "@/components/audioTable";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion, AnimatePresence } from "framer-motion";

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
  const [viewStatus, setViewStatus] = useState<"record" | "table">("table");
  const getSystemInfo = async (): Promise<SystemInfo> => {
    const res = await fetch("http://localhost:8000/system/resources");
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
    <div className="flex justify-center items-center flex-col md:flex-row">
      <Tabs
        defaultValue={viewStatus}
        className="w-[400px]"
        onValueChange={(val: string) =>
          setViewStatus(val as "record" | "table")
        }
      >
        <TabsList>
          <TabsTrigger value="record">VoiceReactify</TabsTrigger>
          <TabsTrigger value="table">Record Table</TabsTrigger>
        </TabsList>
        <TabsContent value="record">
          Record your voice and get the text!
        </TabsContent>
        <TabsContent value="table">
          The list of your record! Check it out!
        </TabsContent>
      </Tabs>
      <div className="bg-white/70 shadow-xl  rounded-xl">
        <AlertSystemInfo isAlert={isSystemCompatible}></AlertSystemInfo>
        <AnimatePresence mode="wait">
          <motion.div
            key={viewStatus}
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -10, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="w-[450px] sm:w-[650px] lg:w-[700px]  h-[658px] overflow-y-auto">
              {viewStatus === "record" && <AudioWaveform></AudioWaveform>}
              {viewStatus === "table" && <AudioTable></AudioTable>}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
