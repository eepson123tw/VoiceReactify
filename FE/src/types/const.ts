import { type RecordData } from "@/composables/useTableApi";

export interface AssignmentDialogProps {
  data: RecordData;
}

export interface ChartData {
  pronunciation_score: number;
  accuracy_score: number;
  completeness_score: number;
  fluency_score: number;
  prosody_score: number;
  words: {
    word: string;
    error_type: keyof typeof SpeechIssues;
    accuracy_score: number;
  }[];
}

export enum SpeechScores {
  accuracy_score = "準確度分數",
  completeness_score = "完整度分數",
  fluency_score = "流暢度分數",
  pronunciation_score = "發音分數",
  prosody_score = "韻律分數",
  words = "單字總平均",
}

export type ScoreKey = keyof ChartData;

export type RadarDataMap = {
  letter: ScoreKey;
  frequency: number;
}[];

export interface WordObj {
  word: string;
  error_type: keyof typeof SpeechIssues;
}

export interface ReadAlongTextProps {
  words: WordObj[];
}
export enum SpeechIssues {
  Mispronunciation = "發音錯誤",
  UnexpectedBreak = "意外中斷",
  MissingBreak = "缺少中斷",
  Monotone = "單調",
  None = "None",
}
