import { MixIcon } from "@radix-ui/react-icons";

import { Button } from "@/components/ui/button";

export default function RecordButton({
  record,
  children,
}: {
  record: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center">
      <Button
        variant="outline"
        size="icon"
        className="bg-black group hover:bg-white p-2 w-20 h-20 rounded-full"
        onClick={record}
      >
        <MixIcon className="h-20 w-20  text-white group-hover:text-black" />
      </Button>
      {children}
    </div>
  );
}
