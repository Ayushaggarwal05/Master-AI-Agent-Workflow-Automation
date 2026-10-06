import React, { useState } from 'react';
import { AlertTriangle, ArrowRight, Upload, CheckCircle2, X } from 'lucide-react';
import { uploadInputFile } from '@/api';

interface MissingInputResolverProps {
  workflowId: string;
  workflowName: string;
  missingInputs: string[];
  originalMessage: string;
  existingInputs: Record<string, any>;
  onResolveAndExecute: (filledInputs: Record<string, any>) => void;
  onDismiss: () => void;
}

export const MissingInputResolver: React.FC<MissingInputResolverProps> = ({
  workflowId,
  workflowName,
  missingInputs,
  existingInputs,
  onResolveAndExecute,
  onDismiss,
}) => {
  const [formData, setFormData] = useState<Record<string, any>>(() => {
    const initial: Record<string, any> = { ...existingInputs };
    missingInputs.forEach((inp) => {
      const lower = inp.toLowerCase();
      if (lower.includes('threshold') && !initial.minimum_stock_threshold) {
        initial.minimum_stock_threshold = 10;
      } else if (lower.includes('order') && !initial.order_id) {
        initial.order_id = 'ORD-9021';
      } else if (lower.includes('dates') && !initial.dates) {
        initial.dates = 'April 15 - May 30, 2026';
      } else if (lower.includes('goal') && !initial.campaign_goal) {
        initial.campaign_goal = 'Increase Q2 sales conversions by 25%';
      }
    });
    return initial;
  });

  const [uploadingField, setUploadingField] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<Record<string, string>>({});

  const handleFileUpload = async (fieldName: string, file: File) => {
    setUploadingField(fieldName);
    try {
      const res = await uploadInputFile(file);
      setUploadedFiles((prev) => ({ ...prev, [fieldName]: file.name }));
      setFormData((prev) => ({
        ...prev,
        file_path: res.file_path,
        [fieldName]: res.file_path,
      }));
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploadingField(null);
    }
  };

  const handleUseSampleFile = (fieldName: string, samplePath: string, label: string) => {
    setUploadedFiles((prev) => ({ ...prev, [fieldName]: label }));
    setFormData((prev) => ({
      ...prev,
      file_path: samplePath,
      [fieldName]: samplePath,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onResolveAndExecute(formData);
  };

  return (
    <div className="bg-dark-850 rounded-xl border border-accent-amber/40 shadow-2xl p-5 space-y-5 animate-fadeIn">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-dark-750 pb-3">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-accent-amber/10 border border-accent-amber/30 flex items-center justify-center text-accent-amber">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-white">
                Additional Information Required
              </h3>
              <span className="font-mono text-xs font-semibold bg-brand-500/20 text-brand-300 px-2 py-0.5 rounded border border-brand-500/30">
                {workflowId}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              <strong>{workflowName}</strong> requires the following parameters to complete execution:
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onDismiss}
          className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-dark-800 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Form Fields */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-3.5">
          {missingInputs.map((inp, idx) => {
            const lower = inp.toLowerCase();
            const isFileField = lower.includes('csv') || lower.includes('file') || lower.includes('catalog') || lower.includes('logs') || lower.includes('data');

            return (
              <div key={idx} className="bg-dark-950 p-3.5 rounded-lg border border-dark-750 space-y-2">
                <label className="text-xs font-semibold text-slate-200 flex items-center justify-between">
                  <span>{inp}</span>
                  <span className="text-[10px] text-accent-amber uppercase font-mono">Required</span>
                </label>

                {isFileField ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <label className="flex items-center space-x-2 px-3 py-1.5 bg-dark-900 hover:bg-dark-800 border border-dark-750 rounded-lg text-xs text-slate-300 hover:text-white cursor-pointer transition-colors">
                        <Upload className="h-3.5 w-3.5 text-brand-400" />
                        <span>{uploadingField === inp ? 'Uploading...' : 'Upload File (CSV/XLSX)'}</span>
                        <input
                          type="file"
                          accept=".csv,.xlsx,.xls,.txt"
                          className="hidden"
                          disabled={uploadingField !== null}
                          onChange={(e) => {
                            const f = e.target.files?.[0];
                            if (f) handleFileUpload(inp, f);
                          }}
                        />
                      </label>

                      {/* Quick Sample Selector */}
                      <span className="text-xs text-slate-500">or</span>
                      <button
                        type="button"
                        onClick={() => {
                          if (lower.includes('inventory')) {
                            handleUseSampleFile(inp, 'sample_data/inventory.csv', 'sample_data/inventory.csv');
                          } else if (lower.includes('vendor')) {
                            handleUseSampleFile(inp, 'sample_data/vendor_products.csv', 'sample_data/vendor_products.csv');
                          } else if (lower.includes('keyword')) {
                            handleUseSampleFile(inp, 'sample_data/keywords.csv', 'sample_data/keywords.csv');
                          } else if (lower.includes('log')) {
                            handleUseSampleFile(inp, 'sample_data/workflow_logs.csv', 'sample_data/workflow_logs.csv');
                          } else {
                            handleUseSampleFile(inp, 'sample_data/products.csv', 'sample_data/products.csv');
                          }
                        }}
                        className="text-xs text-brand-400 hover:text-brand-300 underline font-mono"
                      >
                        Use Sample Dataset
                      </button>
                    </div>

                    {uploadedFiles[inp] && (
                      <div className="flex items-center space-x-2 text-xs text-accent-emerald bg-accent-emerald/10 px-2.5 py-1.5 rounded border border-accent-emerald/20 font-mono">
                        <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0" />
                        <span>Attached: {uploadedFiles[inp]}</span>
                      </div>
                    )}
                  </div>
                ) : lower.includes('threshold') ? (
                  <input
                    type="number"
                    value={formData.minimum_stock_threshold ?? 10}
                    onChange={(e) => setFormData({ ...formData, minimum_stock_threshold: parseFloat(e.target.value) })}
                    className="w-full bg-dark-900 text-xs text-slate-100 p-2.5 rounded border border-dark-750 focus:outline-none focus:border-brand-500"
                    placeholder="e.g. 10"
                  />
                ) : lower.includes('dates') || lower.includes('timeline') ? (
                  <input
                    type="text"
                    value={formData.dates ?? ''}
                    onChange={(e) => setFormData({ ...formData, dates: e.target.value })}
                    className="w-full bg-dark-900 text-xs text-slate-100 p-2.5 rounded border border-dark-750 focus:outline-none focus:border-brand-500"
                    placeholder="e.g. April 15 - May 30, 2026"
                  />
                ) : lower.includes('goal') || lower.includes('objective') ? (
                  <input
                    type="text"
                    value={formData.campaign_goal ?? ''}
                    onChange={(e) => setFormData({ ...formData, campaign_goal: e.target.value })}
                    className="w-full bg-dark-900 text-xs text-slate-100 p-2.5 rounded border border-dark-750 focus:outline-none focus:border-brand-500"
                    placeholder="e.g. Boost Q2 sales conversions by 25%"
                  />
                ) : lower.includes('order') || lower.includes('email') ? (
                  <input
                    type="text"
                    value={formData.order_id ?? ''}
                    onChange={(e) => setFormData({ ...formData, order_id: e.target.value })}
                    className="w-full bg-dark-900 text-xs text-slate-100 p-2.5 rounded border border-dark-750 focus:outline-none focus:border-brand-500"
                    placeholder="e.g. ORD-9021 or alice@example.com"
                  />
                ) : (
                  <input
                    type="text"
                    value={formData[inp] ?? ''}
                    onChange={(e) => setFormData({ ...formData, [inp]: e.target.value })}
                    className="w-full bg-dark-900 text-xs text-slate-100 p-2.5 rounded border border-dark-750 focus:outline-none focus:border-brand-500"
                    placeholder={`Enter ${inp}...`}
                  />
                )}
              </div>
            );
          })}
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-end space-x-2 pt-2 border-t border-dark-750">
          <button
            type="button"
            onClick={onDismiss}
            className="px-3.5 py-2 text-xs font-medium text-slate-400 hover:text-white hover:bg-dark-800 rounded-lg transition-colors"
          >
            Cancel
          </button>

          <button
            type="submit"
            className="px-5 py-2 text-xs font-semibold text-white bg-gradient-to-r from-accent-amber to-amber-600 hover:from-amber-500 hover:to-amber-400 rounded-lg shadow-md shadow-amber-500/20 transition-all flex items-center space-x-1.5"
          >
            <span>Continue Workflow Execution</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
