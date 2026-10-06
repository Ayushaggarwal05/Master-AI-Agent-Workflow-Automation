import React, { useState } from 'react';
import {
  CheckCircle2,
  Truck,
  Users,
  Code2,
  Sparkles
} from 'lucide-react';

interface ResultRendererProps {
  workflowId: string;
  workflowName?: string;
  expectedOutputSpec: string;
  resultData: Record<string, any>;
}

export const ResultRenderer: React.FC<ResultRendererProps> = ({
  workflowId,
  expectedOutputSpec,
  resultData,
}) => {
  const [viewJson, setViewJson] = useState(false);
  const artifacts = resultData?.artifacts || {};

  return (
    <div className="bg-dark-850 rounded-xl border border-dark-750 shadow-xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-dark-750 bg-dark-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-4 w-4 text-accent-emerald" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Execution Result Artifacts
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
            {workflowId}
          </span>
        </div>

        <button
          type="button"
          onClick={() => setViewJson(!viewJson)}
          className={`flex items-center space-x-1 text-xs px-2.5 py-1 rounded-md border transition-colors ${
            viewJson
              ? 'bg-brand-600 text-white border-brand-500'
              : 'bg-dark-950 text-slate-400 border-dark-750 hover:text-slate-200'
          }`}
        >
          <Code2 className="h-3.5 w-3.5" />
          <span>{viewJson ? 'Formatted View' : 'View JSON'}</span>
        </button>
      </div>

      <div className="p-5 space-y-4">
        {/* Specification Note */}
        <div className="text-xs text-slate-400 bg-dark-950 p-3 rounded-lg border border-dark-750">
          <strong className="text-slate-300">Expected Output Specification:</strong> {expectedOutputSpec}
        </div>

        {viewJson ? (
          <pre className="text-xs font-mono text-brand-300 bg-dark-950 p-4 rounded-lg border border-dark-750 overflow-x-auto max-h-[500px]">
            {JSON.stringify(resultData, null, 2)}
          </pre>
        ) : (
          <div className="space-y-4">
            {/* WF001: Inventory Restock */}
            {workflowId === 'WF001' && artifacts.restock_report && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Restock Summary: {artifacts.restock_report.restock_required_count} Products Need Reorder
                  </h4>
                </div>

                <div className="overflow-x-auto rounded-lg border border-dark-750">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-dark-950 text-slate-400 font-mono border-b border-dark-750">
                      <tr>
                        <th className="p-2.5">SKU</th>
                        <th className="p-2.5">Product Name</th>
                        <th className="p-2.5">Current Stock</th>
                        <th className="p-2.5">Threshold</th>
                        <th className="p-2.5">Status</th>
                        <th className="p-2.5">Suggested Reorder</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-750/70 bg-dark-900/40">
                      {artifacts.restock_report.restock_items?.map((item: any, i: number) => (
                        <tr key={i} className="hover:bg-dark-800/50">
                          <td className="p-2.5 font-mono text-brand-400">{item.sku}</td>
                          <td className="p-2.5 text-slate-200 font-medium">{item.name}</td>
                          <td className="p-2.5 font-mono text-accent-rose font-bold">{item.current_stock}</td>
                          <td className="p-2.5 font-mono text-slate-400">{item.minimum_stock}</td>
                          <td className="p-2.5">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-accent-rose/10 text-accent-rose border border-accent-rose/20">
                              Low Stock
                            </span>
                          </td>
                          <td className="p-2.5 font-mono font-bold text-accent-emerald">+{item.suggested_reorder_qty} units</td>
                        </tr>
                      ))}
                      {artifacts.restock_report.adequate_items?.map((item: any, i: number) => (
                        <tr key={`ok-${i}`} className="hover:bg-dark-800/50 opacity-60">
                          <td className="p-2.5 font-mono text-slate-400">{item.sku}</td>
                          <td className="p-2.5 text-slate-300">{item.name}</td>
                          <td className="p-2.5 font-mono text-slate-300">{item.current_stock}</td>
                          <td className="p-2.5 font-mono text-slate-500">{item.minimum_stock}</td>
                          <td className="p-2.5">
                            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-dark-800 text-slate-400 border border-dark-700">
                              Adequate
                            </span>
                          </td>
                          <td className="p-2.5 font-mono text-slate-500">—</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* WF002: Price Validation */}
            {workflowId === 'WF002' && artifacts.price_validation_report && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Price Validation: {artifacts.price_validation_report.exception_count} Price Exceptions (&gt;10%)
                  </h4>
                </div>

                <div className="overflow-x-auto rounded-lg border border-dark-750">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-dark-950 text-slate-400 font-mono border-b border-dark-750">
                      <tr>
                        <th className="p-2.5">SKU</th>
                        <th className="p-2.5">Product</th>
                        <th className="p-2.5">Internal Price</th>
                        <th className="p-2.5">Vendor Price</th>
                        <th className="p-2.5">Difference (%)</th>
                        <th className="p-2.5">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-750/70 bg-dark-900/40">
                      {artifacts.price_validation_report.matched_products?.map((item: any, i: number) => (
                        <tr key={i} className="hover:bg-dark-800/50">
                          <td className="p-2.5 font-mono text-brand-400">{item.sku}</td>
                          <td className="p-2.5 text-slate-200">{item.name}</td>
                          <td className="p-2.5 font-mono text-slate-300">${item.internal_price.toFixed(2)}</td>
                          <td className="p-2.5 font-mono text-slate-300">${item.vendor_price.toFixed(2)}</td>
                          <td className={`p-2.5 font-mono font-bold ${item.is_exception ? 'text-accent-rose' : 'text-accent-emerald'}`}>
                            {item.difference_pct}%
                          </td>
                          <td className="p-2.5">
                            {item.is_exception ? (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-accent-rose/10 text-accent-rose border border-accent-rose/20">
                                Exception (&gt;10%)
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20">
                                Matched
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* WF003: Vendor File Validation */}
            {workflowId === 'WF003' && artifacts.validation_summary && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-dark-950 p-3 rounded-lg border border-accent-emerald/30">
                    <span className="text-xs text-slate-400">Valid Rows Cleaned:</span>
                    <p className="text-xl font-mono font-bold text-accent-emerald">{artifacts.validation_summary.valid_count}</p>
                  </div>
                  <div className="bg-dark-950 p-3 rounded-lg border border-accent-rose/30">
                    <span className="text-xs text-slate-400">Invalid Rows Detected:</span>
                    <p className="text-xl font-mono font-bold text-accent-rose">{artifacts.validation_summary.invalid_count}</p>
                  </div>
                </div>

                {artifacts.validation_summary.invalid_rows?.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-accent-rose">Invalid Row Exception Details:</span>
                    <div className="space-y-1">
                      {artifacts.validation_summary.invalid_rows.map((inv: any, i: number) => (
                        <div key={i} className="text-xs bg-dark-950 p-2.5 rounded border border-accent-rose/20 flex justify-between items-center">
                          <span className="font-mono text-slate-400">Row #{inv.row_index}</span>
                          <span className="text-accent-rose font-medium">{inv.reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* WF004: Product Description Generator */}
            {workflowId === 'WF004' && artifacts.generated_content && (
              <div className="space-y-3 bg-dark-950 p-4 rounded-lg border border-dark-750">
                <div className="border-b border-dark-750 pb-2">
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">SEO Title</span>
                  <p className="text-sm font-semibold text-brand-300 mt-0.5">{artifacts.generated_content.seo_title}</p>
                </div>

                <div className="border-b border-dark-750 pb-2">
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Short Description</span>
                  <p className="text-xs text-slate-200 mt-0.5">{artifacts.generated_content.short_description}</p>
                </div>

                <div className="border-b border-dark-750 pb-2">
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Full Product Copy</span>
                  <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">{artifacts.generated_content.product_description}</p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Meta Description</span>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{artifacts.generated_content.meta_description}</p>
                </div>

                {artifacts.generated_content.explicitly_missing_attributes?.length > 0 && (
                  <div className="pt-2 border-t border-dark-750 text-xs text-accent-amber bg-accent-amber/5 p-2 rounded">
                    <strong>Missing Attributes Handled:</strong> {artifacts.generated_content.explicitly_missing_attributes.join(', ')} (Explicitly flagged per decision rules).
                  </div>
                )}
              </div>
            )}

            {/* WF005: Order Status & Shipment */}
            {workflowId === 'WF005' && artifacts.order && (
              <div className="space-y-3 bg-dark-950 p-4 rounded-lg border border-dark-750">
                <div className="flex items-center justify-between border-b border-dark-750 pb-3">
                  <div className="flex items-center space-x-2">
                    <Truck className="h-4 w-4 text-brand-400" />
                    <span className="font-mono text-sm font-bold text-white">{artifacts.order.order_id}</span>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    {artifacts.order.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500 block">Customer</span>
                    <span className="text-slate-200 font-medium">{artifacts.order.customer_name} ({artifacts.order.customer_email})</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Carrier & Tracking</span>
                    <span className="text-slate-200 font-mono">{artifacts.order.shipment_carrier} — {artifacts.order.tracking_number}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Purchased Items</span>
                    <span className="text-slate-200">{artifacts.order.items}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Estimated Delivery</span>
                    <span className="text-accent-emerald font-mono font-medium">{artifacts.order.estimated_delivery}</span>
                  </div>
                </div>
              </div>
            )}

            {/* WF006: Duplicate Product Detection */}
            {workflowId === 'WF006' && artifacts.duplicate_report && (
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Duplicate Product Groups ({artifacts.duplicate_report.duplicates_found_count} Pairs Detected)
                </h4>

                <div className="space-y-2">
                  {artifacts.duplicate_report.duplicate_groups?.map((dup: any, i: number) => (
                    <div key={i} className="bg-dark-950 p-3 rounded-lg border border-dark-750 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-accent-amber">{dup.match_type}</span>
                        <span className="font-mono text-slate-400">Confidence: {Math.round(dup.confidence * 100)}%</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-dark-750/70">
                        <div className="p-2 rounded bg-dark-900">
                          <span className="font-mono text-brand-400 text-[11px] block">{dup.product_1.sku}</span>
                          <span className="text-slate-200">{dup.product_1.name}</span>
                        </div>
                        <div className="p-2 rounded bg-dark-900">
                          <span className="font-mono text-brand-400 text-[11px] block">{dup.product_2.sku}</span>
                          <span className="text-slate-200">{dup.product_2.name}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* WF007: Marketing Campaign Brief */}
            {workflowId === 'WF007' && artifacts.campaign_brief && (
              <div className="space-y-3 bg-dark-950 p-4 rounded-lg border border-dark-750">
                <div className="border-b border-dark-750 pb-2">
                  <span className="text-[11px] text-slate-400 uppercase font-semibold">Objective</span>
                  <p className="text-sm font-semibold text-white mt-0.5">{artifacts.campaign_brief.campaign_objective}</p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500 block">Target Audience</span>
                    <span className="text-slate-200">{artifacts.campaign_brief.target_audience}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Timeline</span>
                    <span className="text-accent-emerald font-mono font-medium">{artifacts.campaign_brief.timeline}</span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] text-slate-400 uppercase font-semibold block mb-1.5">Action Checklist</span>
                  <div className="space-y-1">
                    {artifacts.campaign_brief.campaign_checklist?.map((chk: string, i: number) => (
                      <div key={i} className="flex items-center space-x-2 text-xs text-slate-300 bg-dark-900 px-2.5 py-1.5 rounded">
                        <CheckCircle2 className="h-3.5 w-3.5 text-accent-emerald flex-shrink-0" />
                        <span>{chk}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* WF008: Keyword Classification */}
            {workflowId === 'WF008' && artifacts.keyword_classification_report && (
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Classified Keywords ({artifacts.keyword_classification_report.unique_keywords_analyzed} Analyzed)
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {artifacts.keyword_classification_report.classification_results?.map((kw: any, i: number) => (
                    <div key={i} className="bg-dark-950 p-3 rounded-lg border border-dark-750 flex items-center justify-between">
                      <div>
                        <span className="text-xs font-semibold text-slate-200 block">{kw.keyword}</span>
                        <span className="text-[11px] text-slate-500 font-mono">{kw.recommended_target_page}</span>
                      </div>
                      <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                        {kw.search_intent}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* WF009: Employee Task Assignment */}
            {workflowId === 'WF009' && artifacts.assignment_result && (
              <div className="space-y-3 bg-dark-950 p-4 rounded-lg border border-dark-750">
                <div className="flex items-center justify-between border-b border-dark-750 pb-3">
                  <div className="flex items-center space-x-2">
                    <Users className="h-4 w-4 text-accent-purple" />
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase">Recommended Candidate</span>
                      <h4 className="text-sm font-bold text-white">
                        {artifacts.assignment_result.recommended_employee?.name} ({artifacts.assignment_result.recommended_employee?.role})
                      </h4>
                    </div>
                  </div>
                  <span className="text-base font-mono font-bold text-accent-emerald bg-accent-emerald/10 px-3 py-1 rounded-md border border-accent-emerald/20">
                    Score: {artifacts.assignment_result.recommended_employee?.score}/100
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {artifacts.assignment_result.reasoning}
                </p>
              </div>
            )}

            {/* WF010: Workflow Performance Report */}
            {workflowId === 'WF010' && artifacts.performance_report && (
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-dark-950 p-3 rounded-lg border border-dark-750">
                    <span className="text-[11px] text-slate-400">Total Executions</span>
                    <p className="text-lg font-mono font-bold text-white">{artifacts.performance_report.summary_metrics.total_executions}</p>
                  </div>
                  <div className="bg-dark-950 p-3 rounded-lg border border-dark-750">
                    <span className="text-[11px] text-slate-400">Success Rate</span>
                    <p className="text-lg font-mono font-bold text-accent-emerald">{artifacts.performance_report.summary_metrics.success_rate_pct}%</p>
                  </div>
                  <div className="bg-dark-950 p-3 rounded-lg border border-dark-750">
                    <span className="text-[11px] text-slate-400">Avg Duration</span>
                    <p className="text-lg font-mono font-bold text-brand-400">{artifacts.performance_report.summary_metrics.average_execution_time_sec}s</p>
                  </div>
                </div>

                {artifacts.performance_report.recommendations?.length > 0 && (
                  <div className="bg-dark-950 p-3 rounded-lg border border-accent-amber/20 text-xs space-y-1.5">
                    <span className="font-semibold text-accent-amber block">Optimization Recommendations:</span>
                    {artifacts.performance_report.recommendations.map((rec: string, i: number) => (
                      <p key={i} className="text-slate-300">• {rec}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
