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
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4 text-slate-800">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="h-4 w-4 text-orange-500" />
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            AI Semantic Routing & Intent Analysis
          </h3>
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-mono">Confidence:</span>
          <div className="flex items-center space-x-1.5 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
            <div className="w-12 bg-slate-200 h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  confidencePct >= 85
                    ? 'bg-emerald-500'
                    : confidencePct >= 60
                    ? 'bg-amber-500'
                    : 'bg-rose-500'
                }`}
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <span
              className={`text-xs font-mono font-semibold ${
                confidencePct >= 85
                  ? 'text-emerald-700'
                  : confidencePct >= 60
                  ? 'text-amber-700'
                  : 'text-rose-700'
              }`}
            >
              {confidencePct}%
            </span>
          </div>
        </div>
      </div>

      {/* Selected Workflow Banner */}
      <div className="bg-orange-50/60 p-4 rounded-xl border border-orange-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-sm">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-mono font-bold bg-orange-100 text-orange-800 px-2.5 py-1 rounded-lg border border-orange-300">
            {routing.workflow_id}
          </span>
          <div>
            <h4 className="text-sm font-bold text-slate-900">
              {workflow?.name || routing.workflow_id}
            </h4>
            <p className="text-xs text-slate-600">
              {workflow?.trigger || 'Trigger matching intent'}
            </p>
          </div>
        </div>

        {workflow && (
          <div className="flex items-center space-x-2 text-xs text-slate-600 font-mono">
            <span className="bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-sm">
              {workflow.step_count} Steps
            </span>
            <span className="bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-sm">
              {workflow.tools.length} Tools
            </span>
          </div>
        )}
      </div>

      {/* Reasoning */}
      <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-700 leading-relaxed">
        <span className="text-orange-600 font-semibold block mb-1">Reasoning:</span>
        {routing.reasoning}
      </div>

      {/* Inputs Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        {/* Required Inputs */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            Declared Inputs ({routing.required_inputs.length})
          </span>
          <div className="space-y-1">
            {routing.required_inputs.length === 0 ? (
              <span className="text-xs text-slate-400">No explicit inputs declared</span>
            ) : (
              routing.required_inputs.map((inp, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-2 text-xs text-slate-700 bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-200"
                >
                  <ShieldCheck className="h-3.5 w-3.5 text-orange-500 flex-shrink-0" />
                  <span>{inp}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Missing Inputs Status */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            Missing Inputs Status
          </span>
          {routing.missing_inputs.length === 0 ? (
            <div className="flex items-center space-x-2 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 p-2.5 rounded-lg">
              <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-600" />
              <span>All required inputs satisfied</span>
            </div>
          ) : (
            <div className="space-y-1">
              {routing.missing_inputs.map((missing, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-2 text-xs text-amber-800 bg-amber-50 border border-amber-200 p-2 rounded-lg"
                >
                  <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0 text-amber-600" />
                  <span>Requires: <strong>{missing}</strong></span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
