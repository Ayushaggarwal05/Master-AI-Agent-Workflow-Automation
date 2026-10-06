import React from 'react';
import { History, CheckCircle2, AlertCircle, Clock, Trash2, ArrowRight } from 'lucide-react';
import { SessionHistoryItem } from '@/types';

interface ExecutionHistoryProps {
  history: SessionHistoryItem[];
  onSelectHistoryItem: (item: SessionHistoryItem) => void;
  onClearHistory: () => void;
}

export const ExecutionHistory: React.FC<ExecutionHistoryProps> = ({
  history,
  onSelectHistoryItem,
  onClearHistory,
}) => {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-dark-750 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <History className="h-6 w-6 text-brand-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Session Execution History
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Review recent workflow executions, decision outcomes, and audit traces from the active session.
          </p>
        </div>

        {history.length > 0 && (
          <button
            type="button"
            onClick={onClearHistory}
            className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-accent-rose bg-dark-850 hover:bg-dark-800 border border-dark-750 px-3 py-1.5 rounded-lg transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* History List */}
      {history.length === 0 ? (
        <div className="text-center py-20 bg-dark-850 rounded-xl border border-dark-750 space-y-2">
          <History className="h-10 w-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-300">No Executions in Current Session</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Run a workflow from the Workspace to see real-time execution logs and audit records appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item) => {
            const timeStr = item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            return (
              <div
                key={item.id}
                onClick={() => onSelectHistoryItem(item)}
                className="bg-dark-850 hover:bg-dark-800/80 p-4 rounded-xl border border-dark-750 hover:border-dark-700 cursor-pointer transition-all shadow-md flex items-center justify-between group"
              >
                <div className="flex items-center space-x-4">
                  <div
                    className={`h-9 w-9 rounded-lg flex items-center justify-center border ${
                      item.success
                        ? 'bg-accent-emerald/10 border-accent-emerald/30 text-accent-emerald'
                        : 'bg-accent-rose/10 border-accent-rose/30 text-accent-rose'
                    }`}
                  >
                    {item.success ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                  </div>

                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-brand-300 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">
                        {item.workflowId}
                      </span>
                      <h4 className="text-sm font-semibold text-white">
                        {item.workflowName}
                      </h4>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-1 italic">
                      "{item.message}"
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 text-xs text-slate-400 font-mono">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3.5 w-3.5 text-slate-500" />
                    <span>{timeStr}</span>
                  </div>
                  <span className="bg-dark-950 px-2 py-1 rounded border border-dark-750 text-slate-300">
                    {item.durationMs} ms
                  </span>
                  <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-white transition-colors" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
