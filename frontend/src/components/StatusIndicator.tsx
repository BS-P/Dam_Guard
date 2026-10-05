type StatusType = 'ready' | 'processing' | 'completed' | 'failed' | 'unavailable' | 'pending';

export const StatusIndicator = ({ status, label }: { status: StatusType; label?: string }) => {
  const config = {
    ready: { bg: 'bg-blue-500', text: 'text-blue-400' },
    processing: { bg: 'bg-cyan-500 animate-pulse shadow-[0_0_8px_rgba(6,182,212,0.6)]', text: 'text-cyan-400' },
    completed: { bg: 'bg-green-500', text: 'text-green-400' },
    failed: { bg: 'bg-red-500', text: 'text-red-400' },
    unavailable: { bg: 'bg-gray-600', text: 'text-gray-500' },
    pending: { bg: 'bg-yellow-500', text: 'text-yellow-400' }
  };

  const { bg, text } = config[status];

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2.5 h-2.5 rounded-full ${bg}`} />
      {label && <span className={`text-sm font-medium ${text}`}>{label}</span>}
    </div>
  );
};
