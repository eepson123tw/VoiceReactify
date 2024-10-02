import { useCallback } from "react";

interface UseDrawProps {
  analyserRef: React.MutableRefObject<AnalyserNode | null>;
  canvasRef: React.MutableRefObject<HTMLCanvasElement | null>;
  dataArrayRef: React.MutableRefObject<Uint8Array | null>;
  drawAudioRef: React.MutableRefObject<number | null>;
  getSamples: () => number[] | undefined;
}

export default function useDraw({
  analyserRef,
  canvasRef,
  dataArrayRef,
  drawAudioRef,
  getSamples,
}: UseDrawProps) {
  const drawWaveform = useCallback(() => {
    if (!analyserRef.current || !canvasRef.current || !dataArrayRef.current)
      return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext("2d")!;

    const bar = ({
      x,
      y,
      width,
      height,
      color,
      i,
    }: {
      x: number;
      y: number;
      width: number;
      height: number;
      color: string;
      i: number;
    }) => {
      const barItem = {
        x: x,
        y: y,
        width: width,
        height: height,
        color: color,
        i,
      };
      const update = (micInput: number) => {
        const sound = micInput * 1000;
        if (sound > barItem.height) {
          barItem.height = sound;
        } else {
          barItem.height -= barItem.height * 0.05;
        }
      };
      const draw = (canvasCtx: CanvasRenderingContext2D) => {
        canvasCtx.strokeStyle = barItem.color;
        canvasCtx.save();

        canvasCtx.translate(canvas.width / 2, canvas.height / 2);
        canvasCtx.rotate(i * 0.05);

        canvasCtx.beginPath();
        canvasCtx.moveTo(0, 0);
        canvasCtx.lineTo(0, barItem.height);
        canvasCtx.stroke();

        canvasCtx.restore();
      };
      return { update, draw };
    };

    const bars = [] as ReturnType<typeof bar & { i: number }>[];

    const createBars = () => {
      for (let i = 0; i < 256; i++) {
        const colors = `hsl(${i * 2},100%,50%)`;
        bars.push(
          bar({
            x: 0,
            y: i * 1.5,
            width: 5,
            height: 10,
            color: colors,
            i,
          })
        );
      }
    };

    createBars();

    const draw = () => {
      if (dataArrayRef.current) {
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        bars.forEach((bar, i) => {
          const samples = getSamples()!;

          bar.update(samples[i]);
          bar.draw(canvasCtx);
        });
      }

      drawAudioRef.current = requestAnimationFrame(draw);
    };
    draw();
  }, [dataArrayRef, analyserRef, getSamples, canvasRef, drawAudioRef]);
  return { drawWaveform };
}
