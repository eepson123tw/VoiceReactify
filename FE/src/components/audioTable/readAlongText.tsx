import React from "react";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface WordObj {
  word: string;
  error_type: keyof typeof SpeechIssues;
}

interface ReadAlongTextProps {
  words: WordObj[];
}
enum SpeechIssues {
  Mispronunciation = "發音錯誤",
  UnexpectedBreak = "意外中斷",
  MissingBreak = "缺少中斷",
  Monotone = "單調",
  None = "None",
}

const ReadAlongText: React.FC<ReadAlongTextProps> = ({ words }) => {
  return (
    <div className="mt-4 w-[460px]">
      <h2 className="text-lg font-semibold">Assignment</h2>
      <p className="mt-2 break-words">
        {words.map((wordObj, index) => {
          const { word, error_type } = wordObj;
          const hasError = error_type !== "None";
          return (
            <span
              key={index}
              className={`mr-2 ${hasError ? "text-red-500 underline" : ""}`}
            >
              {hasError ? (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <span className="text-nowrap">{word}</span>
                    </TooltipTrigger>
                    <TooltipContent>
                      <span>{SpeechIssues[error_type]}</span>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              ) : (
                word
              )}
            </span>
          );
        })}
      </p>
    </div>
  );
};

export default ReadAlongText;
