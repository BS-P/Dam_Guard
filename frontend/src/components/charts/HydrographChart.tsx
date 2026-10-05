import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export interface HydrographDataPoint {
  time_s?: number;
  time_min?: number;
  discharge_m3s: number;
  water_level_m?: number;
  breach_width_m?: number;
}

export interface HydrographProps {
  data: HydrographDataPoint[];
  peakQ?: number;
  timeToPeakMin?: number;
}

export const HydrographChart: React.FC<HydrographProps> = ({ data }) => {
  const formattedData = (data || []).map(pt => ({
    ...pt,
    time_s: pt.time_s !== undefined ? pt.time_s : (pt.time_min || 0) * 60
  }));

  return (
    <div className="w-full h-48 bg-slate-950/80 border border-slate-800 rounded-md p-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formattedData} margin={{ top: 5, right: 15, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis 
            dataKey="time_s" 
            stroke="#94a3b8" 
            tickFormatter={(val) => `${(val / 60).toFixed(0)}m`} 
            style={{ fontSize: '10px' }}
          />
          <YAxis yAxisId="left" stroke="#06b6d4" style={{ fontSize: '10px' }} />
          <YAxis yAxisId="right" orientation="right" stroke="#f97316" style={{ fontSize: '10px' }} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', borderColor: '#334155', color: '#f8fafc', fontSize: '11px' }}
            labelFormatter={(label) => `Time: ${((label as number) / 60).toFixed(0)} min`}
          />
          <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '4px' }} />
          <Line yAxisId="left" type="monotone" dataKey="discharge_m3s" name="Discharge Q (m³/s)" stroke="#06b6d4" strokeWidth={2} dot={false} />
          {formattedData[0]?.water_level_m !== undefined && (
            <Line yAxisId="right" type="monotone" dataKey="water_level_m" name="Level (m)" stroke="#f97316" strokeWidth={1.5} dot={false} />
          )}
          {formattedData[0]?.breach_width_m !== undefined && (
            <Line yAxisId="right" type="monotone" dataKey="breach_width_m" name="Width (m)" stroke="#22c55e" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
