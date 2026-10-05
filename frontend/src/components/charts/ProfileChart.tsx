import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export interface ProfileProps {
  data: {
    distance: number;
    elevation: number;
    water_surface?: number;
  }[];
}

export const ProfileChart: React.FC<ProfileProps> = ({ data }) => {
  return (
    <div className="w-full h-48 bg-slate-900/80 border border-slate-700 rounded-md p-2">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis dataKey="distance" stroke="#94a3b8" tickFormatter={(val) => `${val}m`} />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
          {data[0]?.water_surface !== undefined && (
            <Area type="monotone" dataKey="water_surface" name="Water Surface" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.4} />
          )}
          <Area type="monotone" dataKey="elevation" name="Terrain" stroke="#8b5cf6" fill="#4c1d95" fillOpacity={0.6} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
