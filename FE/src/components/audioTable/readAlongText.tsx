import React from "react";

interface WordObj {
  word: string;
  error_type: string;
}

interface ReadAlongTextProps {
  words: WordObj[];
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
              {word}
            </span>
          );
        })}
      </p>
    </div>
  );
};

export default ReadAlongText;
