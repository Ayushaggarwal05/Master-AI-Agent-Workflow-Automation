import React, { useState, useRef } from "react";
import {
  Upload,
  X,
  Play,
  RotateCcw,
  Sliders,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Package,
  Tag,
  Copy,
  Megaphone,
  Truck,
  Users,
  Command,
} from "lucide-react";
import { uploadInputFile } from "@/api";

interface RequestPanelProps {
  message: string;
  onMessageChange: (msg: string) => void;
  inputs: Record<string, any>;
  onInputsChange: (inputs: Record<string, any>) => void;
  onExecute: () => void;
  onClear: () => void;
  isLoading: boolean;
}

const QUICK_SUGGESTIONS = [
  {
    text: "Which products need restocking?",
    icon: <Package className="h-3.5 w-3.5 text-orange-400" />,
  },
  {
    text: "Validate our vendor prices.",
    icon: <Tag className="h-3.5 w-3.5 text-orange-400" />,
  },
  {
    text: "Find duplicate products.",
    icon: <Copy className="h-3.5 w-3.5 text-orange-400" />,
  },
  {
    text: "Create a marketing campaign brief.",
    icon: <Megaphone className="h-3.5 w-3.5 text-orange-400" />,
  },
  {
    text: "Check the status of order ORD-9021.",
    icon: <Truck className="h-3.5 w-3.5 text-orange-400" />,
  },
  {
    text: "Assign employee to develop Python ETL pipeline.",
    icon: <Users className="h-3.5 w-3.5 text-orange-400" />,
  },
];

const RobotAvatar: React.FC = () => (
  <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-orange-500 via-orange-600 to-amber-600 p-2 shadow-md shadow-orange-500/25 flex-shrink-0 flex items-center justify-center border border-orange-400/40">
    <svg
      viewBox="0 0 24 24"
      className="w-full h-full"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Antenna */}
      <line
        x1="12"
        y1="2"
        x2="12"
        y2="4.5"
        stroke="#ffffff"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="12" cy="1.75" r="1.25" fill="#ffffff" />
      {/* Ears */}
      <rect x="2" y="8.5" width="2" height="5" rx="1" fill="#ffffff" />
      <rect x="20" y="8.5" width="2" height="5" rx="1" fill="#ffffff" />
      {/* Solid White Head / Face */}
      <rect x="4" y="5" width="16" height="14" rx="3.5" fill="#ffffff" />
      {/* Vivid Orange Eyes */}
      <circle cx="8.5" cy="10.5" r="1.75" fill="#ea580c" />
      <circle cx="15.5" cy="10.5" r="1.75" fill="#ea580c" />
      {/* Subtle Digital Smile */}
      <path
        d="M8.5 14.8C9.5 16 14.5 16 15.5 14.8"
        stroke="#ea580c"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  </div>
);

export const RequestPanel: React.FC<RequestPanelProps> = ({
  message,
  onMessageChange,
  inputs,
  onInputsChange,
  onExecute,
  onClear,
  isLoading,
}) => {
  const [selectedFile, setSelectedFile] = useState<{
    name: string;
    size: number;
    path?: string;
  } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [rawJsonInputs, setRawJsonInputs] = useState(
    JSON.stringify(inputs, null, 2),
  );
  const [jsonError, setJsonError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const res = await uploadInputFile(file);
      setSelectedFile({
        name: file.name,
        size: file.size,
        path: res.file_path,
      });

      const updated = {
        ...inputs,
        file_path: res.file_path,
      };
      onInputsChange(updated);
      setRawJsonInputs(JSON.stringify(updated, null, 2));
    } catch (err: any) {
      alert(`File upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    const updated = { ...inputs };
    delete updated.file_path;
    delete updated.csv_data;
    onInputsChange(updated);
    setRawJsonInputs(JSON.stringify(updated, null, 2));
  };

  const handleJsonChange = (text: string) => {
    setRawJsonInputs(text);
    try {
      if (text.trim() === "") {
        onInputsChange({});
        setJsonError(null);
      } else {
        const parsed = JSON.parse(text);
        onInputsChange(parsed);
        setJsonError(null);
      }
    } catch (err: any) {
      setJsonError(err.message);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      if (message.trim() && !isLoading) {
        onExecute();
      }
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xl shadow-slate-200/50 overflow-hidden">
      {/* Header */}
      <div className="px-7 py-5 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <RobotAvatar />
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
              Agent Command Interface
            </h2>
            <p className="text-xs sm:text-[13px] text-slate-500 mt-0.5 leading-normal">
              Tell the AI agent what you want to automate. It will select the
              best workflow for your request.
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-600 font-mono bg-white px-3.5 py-2 rounded-xl border border-slate-200/90 shadow-xs">
          <Command className="h-3.5 w-3.5 text-slate-500" />
          <span>
            Press{" "}
            <strong className="text-slate-900 font-bold">Ctrl + Enter</strong>{" "}
            to run
          </span>
        </div>
      </div>

      <div className="p-7 space-y-5">
        {/* Main Prompt Textarea (Centered & Clean) */}
        <div className="relative">
          <textarea
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            disabled={isLoading}
            placeholder='What would you like the AI workflow agent to automate? (e.g., "Which products are low on stock?" or "Validate our vendor prices?")'
            className="w-full bg-white text-sm text-slate-900 placeholder-slate-400 rounded-xl px-5 py-4 border border-slate-200 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/25 resize-none transition-all shadow-inner leading-relaxed font-normal"
          />
        </div>

        {/* Quick Suggestion Pills */}
        <div className="space-y-2">
          <div className="text-xs text-slate-500 font-medium">Suggestions:</div>
          <div className="flex items-center flex-wrap gap-2.5">
            {QUICK_SUGGESTIONS.map((sug, i) => (
              <button
                key={i}
                type="button"
                disabled={isLoading}
                onClick={() => onMessageChange(sug.text)}
                className="text-xs bg-orange-50/70 hover:bg-orange-100 text-slate-800 hover:text-slate-950 px-3.5 py-1.5 rounded-xl border border-orange-200/90 hover:border-orange-300 flex items-center space-x-1.5 transition-all shadow-2xs font-medium cursor-pointer"
              >
                {sug.icon}
                <span>{sug.text}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Supporting File Attachment & Action Toolbar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3.5 pt-4 border-t border-slate-100">
          <div className="flex items-center space-x-2.5">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".csv,.xlsx,.xls,.txt"
              className="hidden"
            />

            {selectedFile ? (
              <div className="flex items-center space-x-2 bg-orange-50 border border-orange-300 text-xs px-3.5 py-2 rounded-xl text-orange-900 font-mono font-medium shadow-xs">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                <span className="max-w-[160px] truncate">
                  {selectedFile.name}
                </span>
                <span className="text-slate-500">
                  ({(selectedFile.size / 1024).toFixed(1)} KB)
                </span>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="text-slate-400 hover:text-rose-600 ml-1"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                disabled={isLoading || isUploading}
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-300 px-3.5 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
              >
                <Upload className="h-3.5 w-3.5 text-orange-500" />
                <span>
                  {isUploading ? "Uploading file..." : "Attach CSV / XLSX"}
                </span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className={`flex items-center space-x-1.5 text-xs font-medium px-3.5 py-2 rounded-xl border transition-all shadow-xs cursor-pointer ${
                showAdvanced
                  ? "bg-orange-50 border-orange-300 text-orange-800"
                  : "bg-white border-slate-300 text-slate-700 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <Sliders className="h-3.5 w-3.5 text-orange-500" />
              <span>Inputs (JSON)</span>
              {showAdvanced ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2.5 w-full sm:w-auto justify-end">
            <button
              type="button"
              disabled={
                isLoading || (!message && Object.keys(inputs).length === 0)
              }
              onClick={() => {
                onClear();
                handleRemoveFile();
                setRawJsonInputs("{}");
              }}
              className="px-4 py-2.5 text-xs font-semibold text-slate-700 hover:text-slate-950 hover:bg-slate-50 rounded-xl border border-slate-300 transition-colors flex items-center space-x-1.5 shadow-xs cursor-pointer"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset</span>
            </button>

            <button
              type="button"
              disabled={
                isLoading ||
                (!message.trim() && Object.keys(inputs).length === 0)
              }
              onClick={onExecute}
              className="px-6 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-orange-600 via-orange-500 to-amber-500 hover:from-orange-500 hover:to-amber-400 disabled:from-slate-200 disabled:to-slate-200 disabled:text-slate-400 rounded-xl shadow-lg shadow-orange-500/35 active:scale-[0.98] transition-all flex items-center space-x-2 border border-orange-400/30 disabled:border-slate-200 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  <span>Routing Workflow...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current text-white" />
                  <span>Run Workflow</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Expandable JSON Inputs Drawer */}
        {showAdvanced && (
          <div className="pt-3 border-t border-slate-100 space-y-2 animate-fadeIn">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Direct JSON Parameters (Overrides):</span>
              {jsonError ? (
                <span className="text-rose-600 text-[11px] font-mono">
                  Invalid JSON syntax
                </span>
              ) : (
                <span className="text-emerald-600 text-[11px] font-mono">
                  Valid JSON schema
                </span>
              )}
            </div>
            <textarea
              value={rawJsonInputs}
              onChange={(e) => handleJsonChange(e.target.value)}
              rows={4}
              placeholder='{\n  "minimum_stock_threshold": 10\n}'
              className="w-full font-mono text-xs bg-slate-50 text-slate-800 p-3 rounded-xl border border-slate-200 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500/20"
            />
          </div>
        )}
      </div>
    </div>
  );
};
