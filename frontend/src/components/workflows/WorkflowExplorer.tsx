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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-dark-750 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <FileSpreadsheet className="h-6 w-6 text-accent-emerald" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Excel Workflow Registry Explorer
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Browse and inspect all dynamic workflow specifications parsed from <code className="text-brand-400">data/workflows.xlsx</code>.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="h-4 w-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search workflows, triggers, tools..."
            className="w-full bg-dark-950 text-xs text-slate-100 pl-9 pr-4 py-2.5 rounded-lg border border-dark-750 focus:outline-none focus:border-brand-500"
          />
        </div>
      </div>

      {/* Grid of Workflows */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse bg-dark-850 h-64 rounded-xl border border-dark-750" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 bg-dark-850 rounded-xl border border-dark-750 text-slate-500 text-sm">
          No workflows match your search query.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filtered.map((wf) => (
            <div
              key={wf.id}
              className="bg-dark-850 rounded-xl border border-dark-750 p-5 space-y-4 hover:border-dark-700 transition-all shadow-lg flex flex-col justify-between"
            >
              <div className="space-y-3">
                {/* Header Badge & Name */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono text-xs font-bold bg-brand-500/20 text-brand-300 px-2.5 py-1 rounded-md border border-brand-500/30">
                      {wf.id}
                    </span>
                    <h3 className="text-sm font-bold text-white">
                      {wf.name}
                    </h3>
                  </div>

                  <button
                    type="button"
                    onClick={() => onSelectAndRun(wf)}
                    className="flex items-center space-x-1 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 px-3 py-1.5 rounded-lg transition-colors shadow-sm"
                  >
                    <Play className="h-3 w-3 fill-current" />
                    <span>Test Workflow</span>
                  </button>
                </div>

                {/* Trigger */}
                <div className="text-xs text-slate-300 bg-dark-950 p-2.5 rounded-lg border border-dark-750">
                  <strong className="text-slate-400">Trigger Condition:</strong> {wf.trigger}
                </div>

                {/* Ordered Step Pipeline */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Execution Step Pipeline ({wf.steps.length} Steps)
                  </span>
                  <div className="space-y-1">
                    {wf.steps.map((step, idx) => (
                      <div
                        key={idx}
                        className="flex items-center space-x-2 text-xs text-slate-300 bg-dark-900/60 px-2.5 py-1 rounded border border-dark-750/70"
                      >
                        <span className="font-mono text-[10px] text-brand-400 font-bold">0{idx + 1}</span>
                        <ArrowRight className="h-3 w-3 text-slate-600 flex-shrink-0" />
                        <span className="truncate">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Decision Logic & Tools */}
                <div className="space-y-2 pt-1">
                  <div className="text-xs text-accent-amber bg-accent-amber/5 p-2.5 rounded-lg border border-accent-amber/20">
                    <strong className="text-accent-amber font-semibold block mb-0.5">Decision Logic:</strong>
                    {wf.decision}
                  </div>

                  <div className="flex items-center flex-wrap gap-1.5">
                    <span className="text-[11px] text-slate-500 font-medium mr-1">Tools:</span>
                    {wf.tools.map((t, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] font-mono bg-dark-950 text-slate-300 px-2 py-0.5 rounded border border-dark-750"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Expected Output Spec */}
              <div className="pt-3 border-t border-dark-750 text-[11px] text-slate-400">
                <strong className="text-slate-300">Expected Output:</strong> {wf.output}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
