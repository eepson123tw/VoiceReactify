import { RadiobuttonIcon, PlayIcon } from "@radix-ui/react-icons";

import { cn } from "@/lib/utils";

import { Button } from "@/components/ui/button";

export default function RecordButton({
  record,
  children,
  isRecording,
}: {
  record: () => void;
  children: React.ReactNode;
  isRecording: boolean;
}) {
  const computedClass = isRecording ? "bg-red-500" : "bg-black";
  const hoverClass = isRecording ? "hover:bg-red-600" : "hover:bg-white";
  return (
    <div className="flex flex-col items-center">
      <Button
        variant="outline"
        size="icon"
        className={cn(
          computedClass,
          hoverClass,
          "group p-2 w-20 h-20 rounded-full"
        )}
        onClick={record}
      >
        {!isRecording ? (
          <PlayIcon className="h-20 w-20  text-white group-hover:text-black"></PlayIcon>
        ) : (
          <RadiobuttonIcon className="h-20 w-20  text-black group-hover:text-white"></RadiobuttonIcon>
        )}
      </Button>
      {children}
    </div>
  );
}
