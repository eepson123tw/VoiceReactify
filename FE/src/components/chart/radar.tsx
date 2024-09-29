import { useMemo, useCallback } from "react";
import { Group } from "@visx/group";
import letterFrequency, {
  LetterFrequency,
} from "@visx/mock-data/lib/mocks/letterFrequency";
import { scaleLinear } from "@visx/scale";
// import { Point } from "@visx/point";
import { LineRadial, Line } from "@visx/shape";
import { voronoi } from "@visx/voronoi";
import { useTooltip, TooltipWithBounds } from "@visx/tooltip";
import { Point } from "@visx/point";
import { localPoint } from "@visx/event";
import { EventType } from "@visx/event/lib/types";

const orange = "#ff9933";
export const pumpkin = "#f5810c";
const silver = "#d9d9d9";
export const background = "#FAF7E9";

const degrees = 360;
const data = letterFrequency.slice(2, 12);

const genAngles = (length: number) =>
  [...new Array(length + 1)].map((_, i) => ({
    angle: i * (degrees / length),
  }));

const genPoints = (length: number, radius: number) => {
  const step = (Math.PI * 2) / length;
  return [...new Array(length)].map((_, i) => ({
    x: radius * Math.sin(i * step),
    y: radius * Math.cos(i * step),
  }));
};

function genPolygonPoints<Datum>(
  dataArray: Datum[],
  scale: (n: number) => number,
  getValue: (d: Datum) => number
) {
  const step = (Math.PI * 2) / dataArray.length;
  const points: { x: number; y: number }[] = new Array(dataArray.length).fill({
    x: 0,
    y: 0,
  });
  const pointString: string = new Array(dataArray.length + 1)
    .fill("")
    .reduce((res, _, i) => {
      if (i > dataArray.length) return res;
      const xVal = scale(getValue(dataArray[i - 1])) * Math.sin(i * step);
      const yVal = scale(getValue(dataArray[i - 1])) * Math.cos(i * step);
      points[i - 1] = { x: xVal, y: yVal };
      res += `${xVal},${yVal} `;
      return res;
    });

  return { points, pointString };
}

const defaultMargin = { top: 40, left: 80, right: 80, bottom: 80 };

export type RadarProps = {
  width: number;
  height: number;
  margin?: { top: number; right: number; bottom: number; left: number };
  levels?: number;
};

export default function Example({
  width,
  height,
  levels = 5,
  margin = defaultMargin,
}: RadarProps) {
  const xMax = width - margin.left - margin.right;
  const yMax = height - margin.top - margin.bottom;
  const radius = Math.min(xMax, yMax) / 2;
  const y = (d: LetterFrequency) => d.frequency;
  const points = genPoints(data.length, radius);
  const zeroPoint = new Point({ x: 0, y: 0 });
  const radialScale = useMemo(
    () =>
      scaleLinear<number>({
        range: [0, Math.PI * 2],
        domain: [degrees, 0],
      }),
    []
  );

  const yScale = useMemo(
    () =>
      scaleLinear<number>({
        range: [0, radius],
        domain: [0, Math.max(...data.map(y))],
      }),
    [radius]
  );

  const webs = useMemo(() => genAngles(data.length), []);
  // const points = useMemo(() => genPoints(data.length, radius), [radius]);
  const polygonPoints = useMemo(
    () => genPolygonPoints(data, yScale, y),
    [yScale]
  );

  const {
    tooltipData,
    tooltipLeft,
    tooltipTop,
    tooltipOpen,
    showTooltip,
    hideTooltip,
  } = useTooltip<{ x: number; y: number }>();

  const voronoiLayout = useMemo(
    () =>
      voronoi<{ x: number; y: number }>({
        x: (d) => d.x + width / 2,
        y: (d) => d.y + height / 2 - margin.top,
        width: width,
        height: height,
      })(polygonPoints.points),
    [width, height, margin, polygonPoints.points]
  );

  const handleMouseMove = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (event: any) => {
      if (!event) return;
      const target = event.target;
      const coords = localPoint(target.ownerSVGElement, event as EventType)!;
      const closest = voronoiLayout.find(coords.x, coords.y, 500)!;

      showTooltip({
        tooltipLeft: coords.x,
        tooltipTop: coords.y,
        tooltipData: closest.data,
      });
    },
    [showTooltip, voronoiLayout]
  );

  return width < 10 ? null : (
    <>
      <svg width={width} height={height}>
        <rect fill={background} width={width} height={height} rx={14} />
        {/** just to troubleshoot the voronoi positions */}
        {/* {voronoiLayout.polygons().map((polygon, i) => (
          <VoronoiPolygon
            key={`polygon-${i}`}
            polygon={polygon}
            stroke="transparent"
            strokeWidth={1}
          />
        ))} */}
        <Group top={height / 2 - margin.top} left={width / 2}>
          {[...new Array(levels)].map((_, i) => (
            <LineRadial
              key={`web-${i}`}
              data={webs}
              angle={(d) => radialScale(d.angle)}
              radius={((i + 1) * radius) / levels}
              fill="none"
              stroke={silver}
              strokeWidth={2}
              strokeOpacity={0.8}
              strokeLinecap="round"
            />
          ))}
          {[...new Array(data.length)].map((_, i) => (
            <Line
              key={`radar-line-${i}`}
              from={zeroPoint}
              to={points[i]}
              stroke={silver}
            />
          ))}

          <polygon
            points={polygonPoints.pointString}
            fill={orange}
            fillOpacity={0.3}
            stroke={orange}
            strokeWidth={1}
          />
          {polygonPoints.points.map((point, i) => (
            <circle
              key={`radar-point-${i}`}
              cx={point.x}
              cy={point.y}
              r={4}
              fill={pumpkin}
            />
          ))}

          <polygon
            points={polygonPoints.pointString}
            fill={orange}
            fillOpacity={0.3}
            stroke={orange}
            strokeWidth={1}
          />
          {polygonPoints.points.map((point, i) => (
            <circle
              key={`radar-point-${i}`}
              cx={point.x}
              cy={point.y}
              r={4}
              fill={pumpkin}
            />
          ))}
        </Group>
        {/** capture all mouse events */}
        <rect
          fill="transparent"
          width={width}
          height={height}
          onMouseMove={handleMouseMove}
          onMouseLeave={hideTooltip}
        />
      </svg>

      {tooltipOpen && tooltipData && (
        <TooltipWithBounds
          // set this to random so it correctly updates with parent bounds
          key={Math.random()}
          top={tooltipTop}
          left={tooltipLeft}
        >
          Data value
          <div>
            x:<strong>{tooltipData.x.toFixed(1)}</strong>
            <br />
            y:<strong>{tooltipData.y.toFixed(1)}</strong>
          </div>
        </TooltipWithBounds>
      )}
    </>
  );
}
