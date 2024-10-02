import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type {
  ChartData,
  AssignmentDialogProps,
  ScoreKey,
  RadarDataMap,
} from "@/types/const";

import ParentSize from "@visx/responsive/lib/components/ParentSize";

import { useEffect, useState } from "react";

import useAssignmentApi from "@/composables/useAssignmentApi";
import Radar from "@/components/chart/radar";
import ReadAlongText from "@/components/audioTable/readAlongText";

const chartDataFormatFn = (data: ChartData): RadarDataMap => {
  const dataMap: RadarDataMap = Object.entries(data).map(([key, value]) => {
    if (key === "words") {
      const wordScores = (value as ChartData["words"]).map(
        (word) => word.accuracy_score / word.word.length
      );
      const averageScore =
        wordScores.reduce((sum, score) => sum + score, 0) / wordScores.length;
      return {
        letter: key as ScoreKey,
        frequency: +averageScore.toFixed(2),
      };
    } else {
      return {
        letter: key as ScoreKey,
        frequency: +Number(value).toFixed(2),
      };
    }
  });

  return dataMap.sort((a, b) => a.letter.localeCompare(b.letter));
};

const AssignmentDialog = ({ data }: AssignmentDialogProps) => {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [chartData, setDataInfo] = useState<ChartData | null>(null);
  const { getAssignmentData } = useAssignmentApi({
    reference_text: data.transcript,
    reference_path: data.filepath
      .replace("transcriptions/", "")
      .replace(".txt", "_converted.wav"),
  });

  useEffect(() => {
    if (!open) {
      return;
    }
    setIsLoading(true);
    getAssignmentData().then((data) => {
      setDataInfo(data);
      setIsLoading(false);
    });
    return () => {
      setDataInfo(null);
    };
  }, [open, getAssignmentData]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger>
        <Button variant="link" className="m-0">
          Assignment
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="mb-2 text-center">
            Voice Assignment
          </DialogTitle>
          {isLoading
            ? "Loading..."
            : chartData && (
                <DialogDescription className="overflow-y-auto h-[500px]">
                  <div className="h-[300px]">
                    <ParentSize>
                      {({ width, height }) => (
                        <Radar
                          width={width}
                          height={height}
                          data={chartDataFormatFn(chartData)}
                        />
                      )}
                    </ParentSize>
                  </div>
                  <ReadAlongText words={chartData.words} />
                </DialogDescription>
              )}
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default AssignmentDialog;
