import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck, BrainCircuit } from 'lucide-react';
import { WorkflowSelection, WorkflowSummary } from '@/types';

interface RoutingCardProps {
  routing: WorkflowSelection;
  workflow?: WorkflowSummary | null;
}

export const RoutingCard: React.FC<RoutingCardProps> = ({ routing, workflow }) => {
  const confidencePct = Math.round(routing.confidence * 100);

  return (
    <div className="bg-dark-850 rounded-xl border border-dark-750 shadow-lg p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-dark-750/70 pb-3">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="h-4 w-4 text-accent-purple" />
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            AI Semantic Routing & Intent Analysis
          </h3>
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-mono">Confidence:</span>
          <div className="flex items-center space-x-1.5 bg-dark-950 px-2.5 py-1 rounded-full border border-dark-750">
            <div className="w-12 bg-dark-800 h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  confidencePct >= 85
                    ? 'bg-accent-emerald'
                    : confidencePct >= 60
                    ? 'bg-accent-amber'
                    : 'bg-accent-rose'
                }`}
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <span
              className={`text-xs font-mono font-semibold ${
                confidencePct >= 85
                  ? 'text-accent-emerald'
                  : confidencePct >= 60
                  ? 'text-accent-amber'
                  : 'text-accent-rose'
              }`}
            >
              {confidencePct}%
            </span>
          </div>
        </div>
      </div>

      {/* Selected Workflow Banner */}
      <div className="bg-gradient-to-r from-dark-950 to-dark-900 p-3.5 rounded-lg border border-brand-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-mono font-bold bg-brand-500/20 text-brand-300 px-2.5 py-1 rounded-md border border-brand-500/30">
            {routing.workflow_id}
          </span>
          <div>
            <h4 className="text-sm font-semibold text-white">
              {workflow?.name || routing.workflow_id}
            </h4>
            <p className="text-xs text-slate-400">
              {workflow?.trigger || 'Trigger matching intent'}
            </p>
          </div>
        </div>

        {workflow && (
          <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono">
            <span className="bg-dark-800 px-2 py-0.5 rounded border border-dark-750">
              {workflow.step_count} Steps
            </span>
            <span className="bg-dark-800 px-2 py-0.5 rounded border border-dark-750">
              {workflow.tools.length} Tools
            </span>
          </div>
        )}
      </div>

      {/* Reasoning */}
      <div className="bg-dark-950/60 p-3.5 rounded-lg border border-dark-750/70 text-xs text-slate-300 leading-relaxed">
        <span className="text-slate-400 font-medium block mb-1">Reasoning:</span>
        {routing.reasoning}
      </div>

      {/* Inputs Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        {/* Required Inputs */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            Declared Inputs ({routing.required_inputs.length})
          </span>
          <div className="space-y-1">
            {routing.required_inputs.length === 0 ? (
              <span className="text-xs text-slate-500">No explicit inputs declared</span>
            ) : (
              routing.required_inputs.map((inp, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-1.5 text-xs text-slate-300 bg-dark-950 px-2.5 py-1 rounded border border-dark-750"
                >
                  <CheckCircle2 className="h-3.5 w-3.5 text-accent-emerald flex-shrink-0" />
                  <span className="truncate">{inp}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Missing Inputs (if any) */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            Missing Inputs Status
          </span>
          {routing.missing_inputs.length === 0 ? (
            <div className="flex items-center space-x-1.5 text-xs text-accent-emerald bg-accent-emerald/10 px-2.5 py-2 rounded border border-accent-emerald/20 font-medium">
              <ShieldCheck className="h-4 w-4 flex-shrink-0" />
              <span>All required inputs satisfied</span>
            </div>
          ) : (
            <div className="space-y-1">
              {routing.missing_inputs.map((inp, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-1.5 text-xs text-accent-rose bg-accent-rose/10 px-2.5 py-1 rounded border border-accent-rose/20 font-medium"
                >
                  <AlertTriangle className="h-3.5 w-3.5 text-accent-rose flex-shrink-0" />
                  <span className="truncate">{inp} (Missing)</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
