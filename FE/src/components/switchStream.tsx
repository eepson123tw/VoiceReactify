import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

interface SwitchStreamProps {
  isStream: boolean;
  setIsStream: (isStream: boolean) => void;
}

const SwitchStream = ({ isStream, setIsStream }: SwitchStreamProps) => {
  return (
    <div className="flex items-center space-x-2">
      <Switch
        id="airplane-mode"
        checked={isStream}
        onCheckedChange={() => setIsStream(!isStream)}
      />
      <Label htmlFor="airplane-mode">
        {!isStream ? "normal" : "streamApi"}
      </Label>
    </div>
  );
};

export default SwitchStream;
