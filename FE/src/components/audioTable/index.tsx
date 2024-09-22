import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableFooter,
} from "@/components/ui/table";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";

import useTableApi, { type RecordData } from "@/composables/useTableApi";
import { useState, useEffect } from "react";

const AudioRecordTable = () => {
  const { getAllTableData } = useTableApi();
  const [recordData, setRecordData] = useState<RecordData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    setIsLoading(true);
    getAllTableData().then((data) => {
      setIsLoading(false);
      if (data.length === 0) {
        return;
      }
      setRecordData(data);
    });
  }, [getAllTableData]);
  return (
    <Table>
      <TableCaption className="hidden">A list of your record!</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Filename</TableHead>
          <TableHead>Duration</TableHead>
          <TableHead>Createtime</TableHead>
          <TableHead>Transcript</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      {isLoading && (
        <TableBody>
          <TableRow>
            <TableCell colSpan={5} className="text-center text-2xl font-bold">
              Loading...
            </TableCell>
          </TableRow>
        </TableBody>
      )}
      {!isLoading && (
        <TableBody>
          {recordData.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-2xl font-bold">
                No record found!
              </TableCell>
            </TableRow>
          ) : (
            recordData.map((record) => (
              <TableRow key={record.createtime}>
                <TableCell className="font-medium">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <p className="w-24 truncate">{record.filename}</p>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{record.filename}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </TableCell>
                <TableCell>{record.duration.toFixed(1)}s</TableCell>
                <TableCell className="text-left">
                  <p className="block text-nowrap">{record.createtime}</p>
                </TableCell>
                <TableCell className="text-left">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <p className=" text-nowrap">See Text Record</p>
                      </TooltipTrigger>
                      <TooltipContent>
                        {/* TODO:change to the text api  or dialog */}
                        <p>{record.transcript}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </TableCell>
                <TableCell className="text-left">
                  <Badge variant="outline">{record.status}</Badge>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      )}
      {!isLoading && (
        <TableFooter>
          <TableRow>
            <TableCell colSpan={1} className="text-left">
              Total
            </TableCell>
            <TableCell colSpan={4} className="text-right">
              {recordData?.length} of Records
            </TableCell>
          </TableRow>
        </TableFooter>
      )}
    </Table>
  );
};

export default AudioRecordTable;
