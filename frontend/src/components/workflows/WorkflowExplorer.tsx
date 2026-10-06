import React, { useState } from 'react';
import { Search, Play, ArrowRight, FileSpreadsheet } from 'lucide-react';
import { Workflow } from '@/types';

interface WorkflowExplorerProps {
  workflows: Workflow[];
  loading: boolean;
  onSelectAndRun: (workflow: Workflow) => void;
}

export const WorkflowExplorer: React.FC<WorkflowExplorerProps> = ({
  workflows,
  loading,
  onSelectAndRun,
}) => {
  const [search, setSearch] = useState('');

  const filtered = workflows.filter((wf) => {
    const matchesSearch =
      wf.id.toLowerCase().includes(search.toLowerCase()) ||
      wf.name.toLowerCase().includes(search.toLowerCase()) ||
      wf.trigger.toLowerCase().includes(search.toLowerCase()) ||
      wf.tools.some((t) => t.toLowerCase().includes(search.toLowerCase()));

    return matchesSearch;
  });

  return (
    <div className="space-y-6 text-slate-800">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <FileSpreadsheet className="h-6 w-6 text-emerald-600" />
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              Excel Workflow Registry Explorer
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Browse and inspect all dynamic workflow specifications parsed from <code className="text-orange-600 font-mono">data/workflows.xlsx</code>.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="h-4 w-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search workflows, triggers, tools..."
            className="w-full bg-white text-xs text-slate-800 pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-orange-500 shadow-sm"
          />
        </div>
      </div>

      {/* Grid of Workflows */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse bg-white h-64 rounded-xl border border-slate-200 shadow-sm" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm shadow-sm">
          No workflows match your search query.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filtered.map((wf) => (
            <div
              key={wf.id}
              className="bg-white rounded-xl border border-slate-200 p-5 space-y-4 hover:border-orange-300 transition-all shadow-sm flex flex-col justify-between"
            >
              <div className="space-y-3">
                {/* Header Badge & Name */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono text-xs font-bold bg-orange-50 text-orange-700 px-2.5 py-1 rounded-md border border-orange-200">
                      {wf.id}
                    </span>
                    <h3 className="text-sm font-bold text-slate-900">
                      {wf.name}
                    </h3>
                  </div>

                  <button
                    type="button"
                    onClick={() => onSelectAndRun(wf)}
                    className="flex items-center space-x-1 text-xs font-semibold text-white bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 px-3 py-1.5 rounded-lg transition-colors shadow-sm"
                  >
                    <Play className="h-3 w-3 fill-current" />
                    <span>Test Workflow</span>
                  </button>
                </div>

                {/* Trigger */}
                <div className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                  <strong className="text-slate-900">Trigger Condition:</strong> {wf.trigger}
                </div>

                {/* Ordered Step Pipeline */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                    Execution Step Pipeline ({wf.steps.length} Steps)
                  </span>
                  <div className="space-y-1">
                    {wf.steps.map((step, idx) => (
                      <div
                        key={idx}
                        className="flex items-center space-x-2 text-xs text-slate-700 bg-slate-50 px-2.5 py-1 rounded border border-slate-200"
                      >
                        <span className="font-mono text-[10px] text-orange-600 font-bold">0{idx + 1}</span>
                        <ArrowRight className="h-3 w-3 text-slate-400 flex-shrink-0" />
                        <span className="truncate">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Decision Logic & Tools */}
                <div className="space-y-2 pt-1">
                  <div className="text-xs text-amber-800 bg-amber-50/80 p-2.5 rounded-lg border border-amber-200">
                    <strong className="text-amber-900 font-semibold block mb-0.5">Decision Logic:</strong>
                    {wf.decision}
                  </div>

                  <div className="flex items-center flex-wrap gap-1.5">
                    <span className="text-[11px] text-slate-500 font-medium mr-1">Tools:</span>
                    {wf.tools.map((t, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] font-mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Expected Output Spec */}
              <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500">
                <strong className="text-slate-700">Expected Output:</strong> {wf.output}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
