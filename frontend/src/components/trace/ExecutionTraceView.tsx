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
        return <Wrench className="h-3.5 w-3.5 text-brand-400" />;
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
        return 'bg-brand-500/10 text-brand-300 border-brand-500/20';
      case 'condition_evaluated':
        return 'bg-accent-amber/10 text-accent-amber border-accent-amber/20';
      case 'error':
        return 'bg-accent-rose/10 text-accent-rose border-accent-rose/20';
      case 'final_result':
      case 'step_completed':
        return 'bg-accent-emerald/10 text-accent-emerald border-accent-emerald/20';
      default:
        return 'bg-dark-950 text-slate-400 border-dark-750';
    }
  };

  return (
    <div className="bg-dark-850 rounded-xl border border-dark-750 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-dark-750 bg-dark-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Terminal className="h-4 w-4 text-brand-400" />
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Live Execution Trace & Tool Audits
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-dark-800 text-slate-400 border border-dark-750">
            {execution.events_count} Events
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <button
            type="button"
            onClick={() => setShowAllDetails(!showAllDetails)}
            className="text-slate-400 hover:text-slate-200 text-xs font-medium"
          >
            {showAllDetails ? 'Collapse All' : 'Expand All'}
          </button>
          <span className="text-slate-500 font-mono">
            {execution.total_duration_ms} ms
          </span>
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="p-5 overflow-x-auto">
        <div className="relative border-l-2 border-dark-750 ml-3 space-y-4">
          {execution.trace.map((evt, idx) => {
            const isExpanded = showAllDetails || expandedIndex === idx;
            const hasDetails = evt.details && Object.keys(evt.details).length > 0;

            return (
              <div key={idx} className="relative pl-6 group">
                {/* Timeline Dot */}
                <div className="absolute -left-[9px] top-1.5 h-4 w-4 rounded-full bg-dark-900 border-2 border-dark-700 flex items-center justify-center group-hover:border-brand-500 transition-colors">
                  <div className="h-1.5 w-1.5 rounded-full bg-brand-400" />
                </div>

                {/* Event Row */}
                <div
                  onClick={() => hasDetails && setExpandedIndex(isExpanded ? null : idx)}
                  className={`p-3 rounded-lg border transition-all ${
                    hasDetails ? 'cursor-pointer hover:bg-dark-800/90' : 'bg-dark-950/40'
                  } ${
                    evt.type === 'error'
                      ? 'bg-accent-rose/5 border-accent-rose/30'
                      : evt.type === 'condition_evaluated'
                      ? 'bg-accent-amber/5 border-accent-amber/20'
                      : evt.type === 'tool_called' || evt.type === 'tool_result'
                      ? 'bg-dark-950/80 border-dark-750'
                      : 'bg-dark-950/40 border-dark-750/70'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center space-x-2 flex-wrap">
                      <span className="p-1 rounded bg-dark-900 border border-dark-750">
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
                        <span className="text-xs font-mono font-semibold text-brand-300 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">
                          tool: {evt.tool}
                        </span>
                      )}

                      {evt.step && (
                        <span className="text-xs font-medium text-slate-200">
                          {evt.step}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 text-[11px] text-slate-500 font-mono flex-shrink-0">
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
                    <div className="mt-2 text-xs bg-dark-900 p-2.5 rounded border border-accent-amber/20 space-y-1">
                      <div className="flex items-center justify-between text-slate-300">
                        <span className="font-mono text-accent-amber">Rule: {evt.details.condition || evt.details.rule}</span>
                        {evt.details.status && (
                          <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-accent-amber/20 text-accent-amber">
                            {evt.details.status}
                          </span>
                        )}
                      </div>
                      {evt.details.action_taken && (
                        <p className="text-slate-400 text-[11px]">Action: {evt.details.action_taken}</p>
                      )}
                    </div>
                  )}

                  {/* Expanded JSON details */}
                  {isExpanded && hasDetails && evt.type !== 'condition_evaluated' && (
                    <div className="mt-2.5 pt-2.5 border-t border-dark-750/70">
                      <pre className="text-[11px] font-mono text-slate-300 bg-dark-950 p-2.5 rounded border border-dark-800 overflow-x-auto">
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
