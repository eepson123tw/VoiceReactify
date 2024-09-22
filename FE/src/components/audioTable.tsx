import AudioRecordTable from "@/components/audioTable/index";

const AudioTable = () => {
  return (
    <div className="px-4 py-6  overflow-x-auto ">
      <h2 className="font-mono text-2xl my-2">Record Table</h2>
      <AudioRecordTable></AudioRecordTable>
    </div>
  );
};

export default AudioTable;
