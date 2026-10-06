import React, { useState } from "react";
import {
  Search,
  Wrench,
  Layers,
  ChevronRight,
  Lock,
  Tag,
  FileText,
  Edit3,
  Truck,
  Copy,
  Megaphone,
  Sparkles,
  Users,
  BarChart3,
  Play,
  FileSpreadsheet,
} from "lucide-react";
import { Workflow } from "@/types";

interface SidebarProps {
  workflows: Workflow[];
  loading: boolean;
  selectedWorkflowId: string | null;
  onSelectWorkflow: (workflow: Workflow) => void;
  onRunWorkflowPrompt: (
    prompt: string,
    defaultInputs?: Record<string, any>,
  ) => void;
}

const WORKFLOW_ICONS: Record<string, React.ReactNode> = {
  WF001: <Lock className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF002: <Tag className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF003: <FileText className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF004: <Edit3 className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF005: <Truck className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF006: <Copy className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF007: <Megaphone className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF008: <Sparkles className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF009: <Users className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
  WF010: <BarChart3 className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />,
};

const SAMPLE_PROMPTS: Record<
  string,
  { prompt: string; inputs?: Record<string, any> }
> = {
  WF001: {
    prompt:
      "Which products are running low on stock and need restocking right now?",
    inputs: { minimum_stock_threshold: 10 },
  },
  WF002: {
    prompt: "Validate our product prices against current vendor price lists.",
    inputs: {},
  },
  WF003: {
    prompt:
      "Clean and validate this vendor product file and report invalid rows.",
    inputs: { file_path: "sample_data/vendor_products.csv" },
  },
  WF004: {
    prompt:
      "Generate eCommerce product descriptions and SEO metadata for the new Ergonomic Wireless Mouse.",
    inputs: {
      product_name: "Ergonomic Wireless Mouse",
      category: "Peripherals",
      attributes: "DPI: 4000; Bluetooth 5.0; Rechargeable",
      material: "Recycled Plastic",
      color: "Matte Black",
      target_audience: "Office Professionals",
    },
  },
  WF005: {
    prompt: "Check shipment tracking and order status for order ORD-9021",
    inputs: { order_id: "ORD-9021" },
  },
  WF006: {
    prompt:
      "Scan product catalog to detect duplicate products and SKU overlaps.",
    inputs: {},
  },
  WF007: {
    prompt:
      "Create a marketing campaign brief for our upcoming Q2 Spring Launch promotion.",
    inputs: {
      campaign_goal: "Increase Q2 sales conversions by 25%",
      product_list: ["Ergonomic Wireless Mouse", "Mechanical Gaming Keyboard"],
      dates: "April 15 - May 30, 2026",
      promotion: "15% Off Spring Bundle",
    },
  },
  WF008: {
    prompt:
      "Classify uploaded SEO search keywords by search intent and category priority.",
    inputs: {},
  },
  WF009: {
    prompt:
      "Who is the best engineer to assign this Python FastAPI backend development task to?",
    inputs: {
      task_description:
        "Develop async Python FastAPI backend with automated ETL pipeline",
      skills: ["Python", "FastAPI", "ETL", "SQL"],
      priority: "High",
      deadline: "Friday",
    },
  },
  WF010: {
    prompt:
      "Generate workflow execution performance report and flag slow or failing workflows.",
    inputs: {},
  },
};

export const Sidebar: React.FC<SidebarProps> = ({
  workflows,
  loading,
  selectedWorkflowId,
  onSelectWorkflow,
  onRunWorkflowPrompt,
}) => {
  const [search, setSearch] = useState("");

  const filtered = workflows.filter(
    (wf) =>
      wf.id.toLowerCase().includes(search.toLowerCase()) ||
      wf.name.toLowerCase().includes(search.toLowerCase()) ||
      wf.trigger.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <aside className="w-96 flex-shrink-0 border-r border-[#1c202d] bg-[#0c0e14] flex flex-col h-[calc(100vh-72px)] select-none">
      {/* Header & Search */}
      <div className="p-4 border-b border-[#1c202d] space-y-3 bg-[#0a0c11]">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-bold text-white uppercase tracking-wider">
            <Layers className="h-4 w-4 text-orange-500" />
            <span>Workflow Registry</span>
          </div>
          <span className="text-[11px] font-mono font-bold bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full border border-orange-500/40">
            {workflows.length}
          </span>
        </div>

        {/* Search input with proper icon positioning and left padding */}
        <div className="relative flex items-center">
          <Search className="h-4 w-4 absolute left-3 text-slate-500 pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search workflows..."
            className="w-full bg-[#06070a] text-xs text-slate-100 pl-10 pr-3 py-2.5 rounded-xl border border-[#1e2332] focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500/30 placeholder-slate-500 transition-all shadow-inner"
          />
        </div>
      </div>

      {/* Workflow Cards List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5 no-scrollbar">
        {loading ? (
          <div className="space-y-3 p-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="animate-pulse bg-[#141722] h-20 rounded-xl border border-[#1e2332]"
              />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-500">
            No matching workflows found.
          </div>
        ) : (
          filtered.map((wf) => {
            const isSelected = selectedWorkflowId === wf.id;
            const sample = SAMPLE_PROMPTS[wf.id];
            const icon = WORKFLOW_ICONS[wf.id] || (
              <Layers className="h-4 w-4 text-orange-400 flex-shrink-0 mt-0.5" />
            );

            return (
              <div
                key={wf.id}
                onClick={() => onSelectWorkflow(wf)}
                className={`group p-3.5 rounded-xl border text-left cursor-pointer transition-all duration-200 relative ${
                  isSelected
                    ? "bg-[#181d2c] border-orange-500/80 border-l-4 border-l-orange-500 shadow-md shadow-orange-950/40"
                    : "bg-[#12151f] hover:bg-[#181c28] border-[#1c202d] hover:border-[#282e40]"
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">{icon}</div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[10px] font-bold text-orange-300 bg-orange-500/20 px-1.5 py-0.5 rounded border border-orange-500/40">
                        {wf.id}
                      </span>
                      <h3 className="text-xs font-bold text-white truncate group-hover:text-orange-200">
                        {wf.name}
                      </h3>
                    </div>

                    <p className="text-[11px] text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                      {wf.trigger}
                    </p>

                    <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-400">
                      <span className="flex items-center space-x-1">
                        <Wrench className="h-2.5 w-2.5 text-slate-400" />
                        <span>{wf.tools.length} tools</span>
                      </span>

                      {sample && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onRunWorkflowPrompt(sample.prompt, sample.inputs);
                          }}
                          title="Load sample query"
                          className="flex items-center space-x-1 text-orange-400 hover:text-orange-300 font-semibold opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Play className="h-2.5 w-2.5 fill-current" />
                          <span>Try</span>
                        </button>
                      )}
                    </div>
                  </div>

                  <ChevronRight
                    className={`h-4 w-4 self-center transition-transform ${isSelected ? "text-orange-400 translate-x-0.5" : "text-slate-600 group-hover:text-slate-300"}`}
                  />
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Elegant Sleek Registry Footer */}
      <div className="p-4 border-t border-[#1c202d] bg-[#080a0f] flex items-center justify-between text-xs select-none">
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="h-8 w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
            <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="min-w-0">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">
              Registry Source
            </span>
            <code className="text-xs font-mono font-bold text-white truncate block">
              data/workflows.xlsx
            </code>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-full text-xs font-semibold flex-shrink-0 shadow-sm shadow-emerald-500/10">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400"></span>
          <span>Live Synced</span>
        </div>
      </div>
    </aside>
  );
};
