import { useCallback } from "react";
import { Group } from "@visx/group";

import { scaleLinear } from "@visx/scale";
// import { Point } from "@visx/point";
import { LineRadial, Line } from "@visx/shape";
import { useTooltip, Tooltip, defaultStyles } from "@visx/tooltip";
import { Point } from "@visx/point";
import { Text } from "@visx/text";

import { SpeechScores } from "@/types/const";

type RadarDataEntry = {
  letter: keyof typeof SpeechScores;
  frequency: number;
};

const orange = "#ff9933";
export const pumpkin = "#f5810c";
const silver = "#d9d9d9";
export const background = "#FAF7E9";

const degrees = 360;

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
  const pointString: string = new Array(dataArray.length)
    .fill("")
    .reduce((res, _, i) => {
      if (i > dataArray.length) return res;
      const xVal = scale(getValue(dataArray[i])) * Math.sin(i * step);
      const yVal = scale(getValue(dataArray[i])) * Math.cos(i * step);
      points[i] = { x: xVal, y: yVal };
      res += `${xVal},${yVal} `;
      return res;
    }, []);

  return { points, pointString };
}

const defaultMargin = { top: 0, left: 80, right: 80, bottom: 80 };

export type RadarProps = {
  width: number;
  height: number;
  margin?: { top: number; right: number; bottom: number; left: number };
  levels?: number;
  data: RadarDataEntry[];
};

export default function Radar({
  width,
  height,
  levels = 5,
  margin = defaultMargin,
  data,
}: RadarProps) {
  const xMax = width - margin.left - margin.right;
  const yMax = height - margin.top - margin.bottom;
  const radius = Math.min(xMax, yMax) / 2;
  const y = (d: RadarDataEntry) => d.frequency;
  const zeroPoint = new Point({ x: 0, y: 0 });

  const radialScale = scaleLinear<number>({
    range: [0, Math.PI * 2],
    domain: [degrees, 0],
  });

  const yScale = scaleLinear<number>({
    range: [0, radius],
    domain: [0, Math.max(...data.map(y))],
  });
  const webs = genAngles(data.length);
  const points = genPoints(data.length, radius);
  const polygonPoints = genPolygonPoints(data, (d) => yScale(d) ?? 0, y);

  const {
    tooltipData,
    tooltipLeft,
    tooltipTop,
    tooltipOpen,
    showTooltip,
    hideTooltip,
  } = useTooltip<{ x: number; y: number; datum: string }>();

  const tooltipStyles = {
    ...defaultStyles,
    backgroundColor: "rgba(53,71,125,0.8)",
    color: "white",
    padding: 12,
  };

  const handleMouseOver = useCallback(
    (
      coords: {
        x: number;
        y: number;
      },
      datum: string
    ) => {
      showTooltip({
        tooltipLeft: coords.x,
        tooltipTop: coords.y,
        tooltipData: { x: 0, y: 0, datum },
      });
    },
    [showTooltip]
  );

  return width < 10 ? null : (
    <>
      <svg width={width} height={height}>
        <rect fill={background} width={width} height={height} rx={14} />
        <Group top={height / 2 - margin.top} left={width / 2}>
          {[...new Array(levels)].map((_, i) => (
            <LineRadial
              key={`web-${i}`}
              data={webs}
              angle={(d) => radialScale(d.angle) ?? 0}
              radius={((i + 1) * radius) / levels}
              fill="none"
              stroke={silver}
              strokeWidth={2}
              strokeOpacity={0.8}
              strokeLinecap="round"
            />
          ))}
          {data.map((_, i) => (
            <Group key={`group-${i}`}>
              <Line
                key={`radar-line-${i}`}
                from={zeroPoint}
                to={points[i]}
                stroke={silver}
              />
              <Text
                key={`text-${i}`}
                textAnchor="middle"
                verticalAnchor="middle"
                dx={points[i].x}
                dy={points[i].y}
              >
                {data[i].letter}
              </Text>
            </Group>
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
              onMouseOver={() => {
                handleMouseOver(
                  point,
                  `${SpeechScores[data[i].letter]}: ${data[i].frequency}`
                );
              }}
              onMouseLeave={hideTooltip}
            />
          ))}
        </Group>
      </svg>

      {tooltipOpen && (
        <Tooltip
          key={Math.random()}
          top={tooltipTop ? tooltipTop + height / 2 : 0}
          left={tooltipLeft ? tooltipLeft + width / 2 : 0}
          style={tooltipStyles}
        >
          <strong>{tooltipData?.datum}</strong>
        </Tooltip>
      )}
    </>
  );
}
