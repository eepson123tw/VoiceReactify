import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { type RecordData } from "@/composables/useTableApi";
import ParentSize from "@visx/responsive/lib/components/ParentSize";

import { useEffect, useState } from "react";

import Example from "@/components/chart/radar";

interface AssignmentDialogProps {
  children?: React.ReactNode;
  data: RecordData;
}

const AssignmentDialog = ({ children, data }: AssignmentDialogProps) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    console.log(data);
  }, [open, data]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="mb-2 text-center">
            Voice Assignment
          </DialogTitle>
          <DialogDescription className=" overflow-y-auto">
            <ParentSize>
              {({ width }) => <Example width={width} height={300} />}
            </ParentSize>
            This action cannot be undone. This will permanently delete your
            account and remove your data from our servers.
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default AssignmentDialog;
