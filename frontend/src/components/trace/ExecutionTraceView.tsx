import React, { useState } from 'react';
import {
  GitCommit,
  CheckCircle2,
  Clock,
  Wrench,
  AlertCircle,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Terminal,
  Zap,
  Sliders
} from 'lucide-react';
import { ExecutionSummary } from '@/types';

interface ExecutionTraceViewProps {
  execution: ExecutionSummary;
}

export const ExecutionTraceView: React.FC<ExecutionTraceViewProps> = ({ execution }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [showAllDetails, setShowAllDetails] = useState(false);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'workflow_selected':
        return <GitCommit className="h-3.5 w-3.5 text-accent-purple" />;
      case 'tool_called':
      case 'tool_result':
        return <Wrench className="h-3.5 w-3.5 text-orange-400" />;
      case 'condition_evaluated':
        return <Sliders className="h-3.5 w-3.5 text-accent-amber" />;
      case 'step_started':
      case 'step_completed':
        return <CheckCircle2 className="h-3.5 w-3.5 text-accent-emerald" />;
      case 'error':
        return <AlertCircle className="h-3.5 w-3.5 text-accent-rose" />;
      case 'warning':
        return <AlertTriangle className="h-3.5 w-3.5 text-accent-amber" />;
      case 'final_result':
        return <Zap className="h-3.5 w-3.5 text-accent-emerald" />;
      default:
        return <Clock className="h-3.5 w-3.5 text-slate-400" />;
    }
  };

  const getEventBadgeClass = (type: string) => {
    switch (type) {
      case 'tool_called':
      case 'tool_result':
        return 'bg-orange-50 text-orange-800 border-orange-200';
      case 'condition_evaluated':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'error':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      case 'final_result':
      case 'step_completed':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden text-slate-800">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/40 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <Terminal className="h-4 w-4 text-orange-500" />
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Live Execution Trace & Tool Audits
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-50 text-orange-700 border border-orange-200 font-bold">
            {execution.events_count} Events
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <button
            type="button"
            onClick={() => setShowAllDetails(!showAllDetails)}
            className="text-slate-500 hover:text-slate-800 text-xs font-medium"
          >
            {showAllDetails ? 'Collapse All' : 'Expand All'}
          </button>
          <span className="text-slate-400 font-mono">
            {execution.total_duration_ms} ms
          </span>
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="p-5 overflow-x-auto">
        <div className="relative border-l-2 border-slate-200 ml-3 space-y-4">
          {execution.trace.map((evt, idx) => {
            const isExpanded = showAllDetails || expandedIndex === idx;
            const hasDetails = evt.details && Object.keys(evt.details).length > 0;

            return (
              <div key={idx} className="relative pl-6 group">
                {/* Timeline Dot */}
                <div className="absolute -left-[9px] top-1.5 h-4 w-4 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center group-hover:border-orange-500 transition-colors">
                  <div className="h-1.5 w-1.5 rounded-full bg-orange-500" />
                </div>

                {/* Event Row */}
                <div
                  onClick={() => hasDetails && setExpandedIndex(isExpanded ? null : idx)}
                  className={`p-3 rounded-lg border transition-all ${
                    hasDetails ? 'cursor-pointer hover:bg-slate-100/80' : 'bg-slate-50/60'
                  } ${
                    evt.type === 'error'
                      ? 'bg-rose-50/70 border-rose-200'
                      : evt.type === 'condition_evaluated'
                      ? 'bg-amber-50/60 border-amber-200'
                      : evt.type === 'tool_called' || evt.type === 'tool_result'
                      ? 'bg-white border-slate-200 shadow-xs'
                      : 'bg-slate-50/70 border-slate-200/80'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center space-x-2 flex-wrap">
                      <span className="p-1 rounded bg-slate-100 border border-slate-200">
                        {getEventIcon(evt.type)}
                      </span>

                      <span
                        className={`text-[11px] font-mono px-2 py-0.5 rounded border uppercase font-medium ${getEventBadgeClass(
                          evt.type
                        )}`}
                      >
                        {evt.type.replace('_', ' ')}
                      </span>

                      {evt.tool && (
                        <span className="text-xs font-mono font-semibold text-orange-800 bg-orange-50 px-2 py-0.5 rounded border border-orange-200">
                          tool: {evt.tool}
                        </span>
                      )}

                      {evt.step && (
                        <span className="text-xs font-medium text-slate-800">
                          {evt.step}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono flex-shrink-0">
                      {evt.elapsed_ms !== null && evt.elapsed_ms !== undefined && (
                        <span>+{evt.elapsed_ms}ms</span>
                      )}
                      {hasDetails && (
                        <span>{isExpanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}</span>
                      )}
                    </div>
                  </div>

                  {/* Condition Evaluation Special Highlight */}
                  {evt.type === 'condition_evaluated' && evt.details && (
                    <div className="mt-2 text-xs bg-amber-50/80 p-2.5 rounded border border-amber-200 space-y-1">
                      <div className="flex items-center justify-between text-slate-800">
                        <span className="font-mono text-amber-900 font-semibold">Rule: {evt.details.condition || evt.details.rule}</span>
                        {evt.details.status && (
                          <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-amber-200 text-amber-900">
                            {evt.details.status}
                          </span>
                        )}
                      </div>
                      {evt.details.action_taken && (
                        <p className="text-slate-600 text-[11px]">Action: {evt.details.action_taken}</p>
                      )}
                    </div>
                  )}

                  {/* Expanded JSON details */}
                  {isExpanded && hasDetails && evt.type !== 'condition_evaluated' && (
                    <div className="mt-2.5 pt-2.5 border-t border-slate-200">
                      <pre className="text-[11px] font-mono text-slate-800 bg-slate-100 p-2.5 rounded border border-slate-200 overflow-x-auto">
                        {JSON.stringify(evt.details, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
