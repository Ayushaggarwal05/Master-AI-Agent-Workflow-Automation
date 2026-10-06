import React, { useState } from 'react';
import { Search, Play, Wrench, FileSpreadsheet } from 'lucide-react';
import { Workflow } from '@/types';

interface SidebarProps {
  workflows: Workflow[];
  loading: boolean;
  selectedWorkflowId: string | null;
  onSelectWorkflow: (workflow: Workflow) => void;
  onRunWorkflowPrompt: (prompt: string, defaultInputs?: Record<string, any>) => void;
}

const SAMPLE_PROMPTS: Record<string, { prompt: string; inputs?: Record<string, any> }> = {
  WF001: {
    prompt: 'Which products are running low on stock and need restocking right now?',
    inputs: { minimum_stock_threshold: 10 }
  },
  WF002: {
    prompt: 'Validate our product prices against current vendor price lists.',
    inputs: {}
  },
  WF003: {
    prompt: 'Clean and validate this vendor product file and report invalid rows.',
    inputs: { file_path: 'sample_data/vendor_products.csv' }
  },
  WF004: {
    prompt: 'Generate eCommerce product descriptions and SEO metadata for the new Ergonomic Wireless Mouse.',
    inputs: {
      product_name: 'Ergonomic Wireless Mouse',
      category: 'Peripherals',
      attributes: 'DPI: 4000; Bluetooth 5.0; Rechargeable',
      material: 'Recycled Plastic',
      color: 'Matte Black',
      target_audience: 'Office Professionals'
    }
  },
  WF005: {
    prompt: 'Check shipment tracking and order status for order ORD-9021',
    inputs: { order_id: 'ORD-9021' }
  },
  WF006: {
    prompt: 'Scan product catalog to detect duplicate products and SKU overlaps.',
    inputs: {}
  },
  WF007: {
    prompt: 'Create a marketing campaign brief for our upcoming Q2 Spring Launch promotion.',
    inputs: {
      campaign_goal: 'Increase Q2 sales conversions by 25%',
      product_list: ['Ergonomic Wireless Mouse', 'Mechanical Gaming Keyboard'],
      dates: 'April 15 - May 30, 2026',
      promotion: '15% Off Spring Bundle'
    }
  },
  WF008: {
    prompt: 'Classify uploaded SEO search keywords by search intent and category priority.',
    inputs: {}
  },
  WF009: {
    prompt: 'Who is the best engineer to assign this Python FastAPI backend development task to?',
    inputs: {
      task_description: 'Develop async Python FastAPI backend with automated ETL pipeline',
      skills: ['Python', 'FastAPI', 'ETL', 'SQL'],
      priority: 'High',
      deadline: 'Friday'
    }
  },
  WF010: {
    prompt: 'Generate workflow execution performance report and flag slow or failing workflows.',
    inputs: {}
  }
};

export const Sidebar: React.FC<SidebarProps> = ({
  workflows,
  loading,
  selectedWorkflowId,
  onSelectWorkflow,
  onRunWorkflowPrompt,
}) => {
  const [search, setSearch] = useState('');

  const filtered = workflows.filter(
    (wf) =>
      wf.id.toLowerCase().includes(search.toLowerCase()) ||
      wf.name.toLowerCase().includes(search.toLowerCase()) ||
      wf.trigger.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside className="w-80 flex-shrink-0 border-r border-dark-750 bg-dark-900/50 flex flex-col h-[calc(100vh-4rem)]">
      {/* Search Header */}
      <div className="p-4 border-b border-dark-750">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
            <FileSpreadsheet className="h-4 w-4 text-accent-emerald" />
            <span>Workflow Registry</span>
          </div>
          <span className="text-xs font-mono bg-dark-800 text-slate-400 px-2 py-0.5 rounded border border-dark-750">
            {workflows.length} Loaded
          </span>
        </div>

        <div className="relative">
          <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter workflows..."
            className="w-full bg-dark-950 text-xs text-slate-200 pl-9 pr-3 py-2 rounded-lg border border-dark-750 focus:outline-none focus:border-brand-500 placeholder-slate-600"
          />
        </div>
      </div>

      {/* Workflow List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {loading ? (
          <div className="space-y-3 p-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="animate-pulse bg-dark-800 h-16 rounded-lg border border-dark-750" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            No matching workflows found.
          </div>
        ) : (
          filtered.map((wf) => {
            const isSelected = selectedWorkflowId === wf.id;
            const sample = SAMPLE_PROMPTS[wf.id];

            return (
              <div
                key={wf.id}
                onClick={() => onSelectWorkflow(wf)}
                className={`group p-3 rounded-lg border text-left cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-dark-800 border-brand-500/60 shadow-sm shadow-brand-500/10'
                    : 'bg-dark-950/60 hover:bg-dark-800/80 border-dark-750 hover:border-dark-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-semibold text-brand-400 bg-brand-500/10 px-1.5 py-0.5 rounded border border-brand-500/20">
                      {wf.id}
                    </span>
                    <h3 className="text-xs font-medium text-slate-200 line-clamp-1 group-hover:text-white">
                      {wf.name}
                    </h3>
                  </div>
                </div>

                <p className="text-[11px] text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                  {wf.trigger}
                </p>

                <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-dark-750/50">
                  <span className="flex items-center space-x-1">
                    <Wrench className="h-3 w-3 text-slate-400" />
                    <span>{wf.tools.length} Tools</span>
                  </span>

                  {sample && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRunWorkflowPrompt(sample.prompt, sample.inputs);
                      }}
                      title="Load sample query into prompt"
                      className="flex items-center space-x-1 text-brand-400 hover:text-brand-300 font-medium opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Play className="h-3 w-3 fill-current" />
                      <span>Try Query</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Registry Footer */}
      <div className="p-3 border-t border-dark-750 bg-dark-950 text-[11px] text-slate-500 flex items-center justify-between">
        <span>Source: <code className="text-slate-400">workflows.xlsx</code></span>
        <span className="text-accent-emerald font-medium">Synced</span>
      </div>
    </aside>
  );
};
