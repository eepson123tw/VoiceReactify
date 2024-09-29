interface ReadAlongTextProps {
  words: {
    word: string;
    accuracy_score: number;
    error_type: string;
  }[];
}

const ReadAlongText = ({ words }: ReadAlongTextProps) => {
  return (
    <div className="mt-4">
      <h2 className="text-lg font-semibold">Assignment</h2>
      <p className="mt-2">
        {words.map((wordObj, index) => {
          const { word, error_type } = wordObj;
          const hasError = error_type !== "None";
          return (
            <span
              key={index}
              style={{
                color: hasError ? "red" : "inherit",
                textDecoration: hasError ? "underline" : "none",
                marginRight: "8px",
              }}
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
