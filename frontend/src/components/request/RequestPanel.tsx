import React, { useState, useRef } from 'react';
import { Sparkles, Upload, X, Play, RotateCcw, Sliders, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import { uploadInputFile } from '@/api';

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
  'Which products need restocking?',
  'Validate our vendor prices.',
  'Find duplicate products.',
  'Create a marketing campaign brief.',
  'Check the status of order ORD-9021.',
  'Assign employee to develop Python ETL pipeline.'
];

export const RequestPanel: React.FC<RequestPanelProps> = ({
  message,
  onMessageChange,
  inputs,
  onInputsChange,
  onExecute,
  onClear,
  isLoading,
}) => {
  const [selectedFile, setSelectedFile] = useState<{ name: string; size: number; path?: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [rawJsonInputs, setRawJsonInputs] = useState(JSON.stringify(inputs, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      // Execute real multipart upload to backend
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
    if (fileInputRef.current) fileInputRef.current.value = '';
    const updated = { ...inputs };
    delete updated.file_path;
    delete updated.csv_data;
    onInputsChange(updated);
    setRawJsonInputs(JSON.stringify(updated, null, 2));
  };

  const handleJsonChange = (text: string) => {
    setRawJsonInputs(text);
    try {
      if (text.trim() === '') {
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
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      if (message.trim() && !isLoading) {
        onExecute();
      }
    }
  };

  return (
    <div className="bg-dark-850 rounded-xl border border-dark-750 shadow-xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-dark-750 bg-dark-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-4 w-4 text-brand-400" />
          <h2 className="text-sm font-semibold text-slate-200">
            Agent Command Interface
          </h2>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          Press Ctrl + Enter to run
        </span>
      </div>

      <div className="p-5 space-y-4">
        {/* Main Prompt Textarea */}
        <div className="relative">
          <textarea
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            disabled={isLoading}
            placeholder="What would you like the AI workflow agent to automate? (e.g., 'Which products are low on stock?' or 'Validate our vendor prices')"
            className="w-full bg-dark-950 text-sm text-slate-100 placeholder-slate-500 rounded-lg p-3.5 border border-dark-750 focus:outline-none focus:border-brand-500/80 focus:ring-1 focus:ring-brand-500/50 resize-none transition-all"
          />
        </div>

        {/* Quick Suggestion Pills */}
        <div className="flex items-center flex-wrap gap-1.5">
          <span className="text-xs text-slate-400 mr-1 font-medium">Suggestions:</span>
          {QUICK_SUGGESTIONS.map((sug, i) => (
            <button
              key={i}
              type="button"
              disabled={isLoading}
              onClick={() => onMessageChange(sug)}
              className="text-xs bg-dark-950 hover:bg-dark-750 text-slate-300 hover:text-white px-2.5 py-1 rounded-md border border-dark-750 transition-colors"
            >
              {sug}
            </button>
          ))}
        </div>

        {/* Supporting File Attachment & Advanced Settings */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2 border-t border-dark-750/70">
          <div className="flex items-center space-x-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".csv,.xlsx,.xls,.txt"
              className="hidden"
            />

            {selectedFile ? (
              <div className="flex items-center space-x-2 bg-dark-950 border border-brand-500/40 text-xs px-3 py-1.5 rounded-lg text-brand-300 font-mono">
                <CheckCircle2 className="h-3.5 w-3.5 text-accent-emerald" />
                <span className="max-w-[160px] truncate">{selectedFile.name}</span>
                <span className="text-slate-500">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="text-slate-400 hover:text-accent-rose ml-1"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                disabled={isLoading || isUploading}
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center space-x-1.5 text-xs text-slate-300 hover:text-white bg-dark-950 hover:bg-dark-800 border border-dark-750 px-3 py-1.5 rounded-lg transition-colors"
              >
                <Upload className="h-3.5 w-3.5 text-slate-400" />
                <span>{isUploading ? 'Uploading file...' : 'Attach CSV / XLSX'}</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className={`flex items-center space-x-1 text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                showAdvanced
                  ? 'bg-dark-800 border-brand-500/50 text-brand-300'
                  : 'bg-dark-950 border-dark-750 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sliders className="h-3.5 w-3.5" />
              <span>Inputs (JSON)</span>
              {showAdvanced ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2 w-full sm:w-auto justify-end">
            <button
              type="button"
              disabled={isLoading || (!message && Object.keys(inputs).length === 0)}
              onClick={() => {
                onClear();
                handleRemoveFile();
                setRawJsonInputs('{}');
              }}
              className="px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-dark-800 rounded-lg border border-dark-750 transition-colors flex items-center space-x-1"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset</span>
            </button>

            <button
              type="button"
              disabled={isLoading || !message.trim()}
              onClick={onExecute}
              className="flex-1 sm:flex-none px-5 py-2 text-xs font-semibold text-white bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 rounded-lg shadow-md shadow-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>AI Reasoning & Executing...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Run Workflow</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Advanced JSON Parameters Drawer */}
        {showAdvanced && (
          <div className="pt-3 border-t border-dark-750/70 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>Explicit Parameter Overrides (JSON):</span>
              {jsonError && <span className="text-accent-rose text-[11px]">{jsonError}</span>}
            </div>
            <textarea
              rows={4}
              value={rawJsonInputs}
              onChange={(e) => handleJsonChange(e.target.value)}
              className="w-full bg-dark-950 font-mono text-xs text-brand-300 p-2.5 rounded-lg border border-dark-750 focus:outline-none focus:border-brand-500"
              placeholder="{ 'minimum_stock_threshold': 10 }"
            />
          </div>
        )}
      </div>
    </div>
  );
};
