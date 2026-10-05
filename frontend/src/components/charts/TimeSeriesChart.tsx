import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

export interface TimeSeriesProps {
  data: {
    time: number;
    depth: number;
    velocity?: number;
  }[];
  currentTime?: number;
}

export const TimeSeriesChart: React.FC<TimeSeriesProps> = ({ data, currentTime }) => {
  const hasVelocity = data.length > 0 && data[0].velocity !== undefined;

  return (
    <div className="w-full h-48 bg-slate-900/80 border border-slate-700 rounded-md p-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="time" stroke="#94a3b8" tickFormatter={(val) => `${val}h`} />
          <YAxis yAxisId="left" stroke="#0ea5e9" label={{ value: 'Depth (m)', angle: -90, position: 'insideLeft', fill: '#0ea5e9', fontSize: 10 }} />
          {hasVelocity && (
            <YAxis yAxisId="right" orientation="right" stroke="#10b981" label={{ value: 'Vel (m/s)', angle: 90, position: 'insideRight', fill: '#10b981', fontSize: 10 }} />
          )}
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
          <Legend wrapperStyle={{ fontSize: '10px' }} />
          <Line yAxisId="left" type="monotone" dataKey="depth" name="Depth (m)" stroke="#0ea5e9" dot={false} strokeWidth={2} />
          {hasVelocity && (
            <Line yAxisId="right" type="monotone" dataKey="velocity" name="Velocity (m/s)" stroke="#10b981" dot={false} strokeWidth={2} />
          )}
          {currentTime !== undefined && (
            <ReferenceLine x={currentTime} stroke="#ef4444" strokeDasharray="3 3" />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
