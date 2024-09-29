import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { type RecordData } from "@/composables/useTableApi";

import ParentSize from "@visx/responsive/lib/components/ParentSize";

import { useEffect, useState } from "react";

import Radar from "@/components/chart/radar";
import ReadAlongText from "@/components/audioTable/readAlongText"; // 请根据实际路径调整导入

const chartData: ChartData = {
  pronunciation_score: 67.96,
  accuracy_score: 69.5,
  completeness_score: 50.0,
  fluency_score: 92.0,
  prosody_score: 58.8,
  words: [
    {
      word: "hei",
      accuracy_score: 66.0,
      error_type: "Insertion",
    },
    {
      word: "hei",
      accuracy_score: 86.0,
      error_type: "None",
    },
    {
      word: "kolo",
      accuracy_score: 53.0,
      error_type: "Mispronunciation",
    },
  ],
};
interface AssignmentDialogProps {
  data: RecordData;
}

interface ChartData {
  pronunciation_score: number;
  accuracy_score: number;
  completeness_score: number;
  fluency_score: number;
  prosody_score: number;
  words: {
    word: string;
    accuracy_score: number;
    error_type: string;
  }[];
}

type ScoreKey = keyof ChartData;

type RadarDataMap = {
  letter: ScoreKey;
  frequency: number;
}[];

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
  const [, setDataInfo] = useState<RecordData | null>(null);

  useEffect(() => {
    if (data) {
      setDataInfo(data);
    }
    return () => {
      setDataInfo(null);
    };
  }, [data]);

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

            {/* 包含 ReadAlongText 组件 */}
            <ReadAlongText words={chartData.words} />
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default AssignmentDialog;
