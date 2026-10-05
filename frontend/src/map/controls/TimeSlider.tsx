import { useState } from 'react';

export const TimeSlider = () => {
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const maxTime = 7200; // 2 hours

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[600px] bg-slate-900/90 backdrop-blur-md rounded-lg border border-slate-700 p-3 flex items-center space-x-4 shadow-2xl z-20">
      <div className="flex space-x-2">
        <button className="text-slate-300 hover:text-white p-1 bg-slate-800 rounded">⏮</button>
        <button 
          onClick={() => setPlaying(!playing)}
          className="text-white p-1 bg-cyan-600 hover:bg-cyan-500 rounded w-8 flex justify-center"
        >
          {playing ? '⏸' : '▶'}
        </button>
        <button className="text-slate-300 hover:text-white p-1 bg-slate-800 rounded">⏭</button>
      </div>

      <div className="text-cyan-400 font-mono text-sm font-medium w-16 text-right">
        {Math.floor(time / 3600).toString().padStart(2, '0')}:
        {Math.floor((time % 3600) / 60).toString().padStart(2, '0')}
      </div>

      <div className="flex-1 px-2 flex items-center">
        <input 
          type="range" 
          min="0" 
          max={maxTime} 
          value={time}
          onChange={(e) => setTime(Number(e.target.value))}
          className="w-full accent-cyan-500 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer" 
        />
      </div>

      <select className="bg-slate-800 border border-slate-600 rounded text-slate-300 text-xs px-2 py-1 outline-none">
        <option>1x</option>
        <option>2x</option>
        <option>5x</option>
        <option>10x</option>
      </select>
    </div>
  );
};
