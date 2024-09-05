import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

interface ToggleEventOptionProps {
  isOption: Array<"StreamApi" | "TimeStamp">;
  setIsOption: (isStream: Array<"StreamApi" | "TimeStamp">) => void;
}

const ToggleEventOption = ({ setIsOption }: ToggleEventOptionProps) => {
  return (
    <div className="flex items-center space-x-2">
      <ToggleGroup
        variant="outline"
        type="multiple"
        onValueChange={(value: Array<"StreamApi" | "TimeStamp">) => {
          setIsOption(value);
        }}
      >
        <ToggleGroupItem value="StreamApi">StreamAPI</ToggleGroupItem>
        <ToggleGroupItem value="TimeStamp">TimeStamp</ToggleGroupItem>
      </ToggleGroup>
    </div>
  );
};

export default ToggleEventOption;
