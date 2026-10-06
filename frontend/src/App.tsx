import React, { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { RequestPanel } from '@/components/request/RequestPanel';
import { MissingInputResolver } from '@/components/request/MissingInputResolver';
import { RoutingCard } from '@/components/execution/RoutingCard';
import { ExecutionTraceView } from '@/components/trace/ExecutionTraceView';
import { ResultRenderer } from '@/components/results/ResultRenderer';
import { WorkflowExplorer } from '@/components/workflows/WorkflowExplorer';
import { getHealth, getWorkflows, runWorkflowExecution } from '@/api';
import {
  Workflow,
  HealthResponse,
  ExecuteResponse,
} from '@/types';
import { AlertCircle } from 'lucide-react';
import { Toast, ToastProps } from '@/components/common/Toast';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'workspace' | 'explorer'>('workspace');
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [workflowsLoading, setWorkflowsLoading] = useState(true);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);

  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);

  const [message, setMessage] = useState('');
  const [inputs, setInputs] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [executionResponse, setExecutionResponse] = useState<ExecuteResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [toast, setToast] = useState<Omit<ToastProps, 'onClose'> | null>(null);

  const [missingInputsState, setMissingInputsState] = useState<{
    workflowId: string;
    workflowName: string;
    missingInputs: string[];
  } | null>(null);

  // Load backend health and workflows on startup
  const fetchHealthStatus = async () => {
    setHealthLoading(true);
    try {
      const res = await getHealth();
      setHealth(res);
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  };

  const fetchWorkflowsList = async () => {
    setWorkflowsLoading(true);
    try {
      const res = await getWorkflows();
      setWorkflows(res.workflows);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load workflows from backend registry.');
    } finally {
      setWorkflowsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthStatus();
    fetchWorkflowsList();
  }, []);

  const executeWithInputs = async (currentMessage: string, currentInputs: Record<string, any>) => {
    if (!currentMessage.trim() || isLoading) return;

    setIsLoading(true);
    setErrorMessage(null);
    setMissingInputsState(null);
    setExecutionResponse(null);

    try {
      const res = await runWorkflowExecution({
        message: currentMessage,
        inputs: currentInputs,
      });

      setExecutionResponse(res);



      // Check if execution was halted due to missing required inputs
      if (!res.success && res.error?.code === 'MISSING_INPUT' && res.routing.missing_inputs.length > 0) {
        setMissingInputsState({
          workflowId: res.routing.workflow_id,
          workflowName: res.workflow?.name || res.routing.workflow_id,
          missingInputs: res.routing.missing_inputs,
        });
      } else if (!res.success && res.error) {
        setErrorMessage(res.error.message);
        setToast({
          type: res.error.code === 'AI_ROUTING_ERROR' ? 'error' : 'warning',
          title: res.error.code === 'AI_ROUTING_ERROR' ? 'AI Routing Failure' : 'Execution Notice',
          message: res.error.message,
        });
      }
    } catch (err: any) {
      const msg = err.message || 'An unexpected error occurred executing the workflow.';
      setErrorMessage(msg);
      setToast({
        type: 'error',
        title: 'System Exception',
        message: msg,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunWorkflow = () => {
    executeWithInputs(message, inputs);
  };

  const handleResolveMissingInputsAndContinue = (filledInputs: Record<string, any>) => {
    setInputs(filledInputs);
    executeWithInputs(message, filledInputs);
  };

  const handleClear = () => {
    setMessage('');
    setInputs({});
    setExecutionResponse(null);
    setErrorMessage(null);
    setMissingInputsState(null);
    setSelectedWorkflowId(null);
  };

  const handleSelectWorkflowPrompt = (prompt: string, defaultInputs?: Record<string, any>) => {
    setMessage(prompt);
    if (defaultInputs) {
      setInputs(defaultInputs);
    }
    setActiveTab('workspace');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectWorkflowFromExplorer = (wf: Workflow) => {
    setSelectedWorkflowId(wf.id);
    setMessage(wf.trigger);
    setInputs({});
    setActiveTab('workspace');
  };

  return (
    <div className="min-h-screen bg-[#f4f6f9] text-slate-900 flex flex-col">
      {/* Global Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        health={health}
        healthLoading={healthLoading}
        onRefreshHealth={fetchHealthStatus}
      />

      {/* Main Container */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === 'workspace' && (
          <>
            {/* Left Sidebar: Workflow Registry */}
            <Sidebar
              workflows={workflows}
              loading={workflowsLoading}
              selectedWorkflowId={selectedWorkflowId}
              onSelectWorkflow={(wf) => {
                setSelectedWorkflowId(wf.id);
                setMessage(wf.trigger);
              }}
              onRunWorkflowPrompt={handleSelectWorkflowPrompt}
            />

            {/* Center Workspace */}
            <main className="flex-1 overflow-y-auto p-6 md:p-8">
              <div className="max-w-6xl mx-auto space-y-6">
                {/* Command Request Panel */}
                <RequestPanel
                  message={message}
                  onMessageChange={setMessage}
                  inputs={inputs}
                  onInputsChange={setInputs}
                  onExecute={handleRunWorkflow}
                  onClear={handleClear}
                  isLoading={isLoading}
                />

                {/* Missing Inputs Interactive Resolution Card */}
                {missingInputsState && (
                  <MissingInputResolver
                    workflowId={missingInputsState.workflowId}
                    workflowName={missingInputsState.workflowName}
                    missingInputs={missingInputsState.missingInputs}
                    originalMessage={message}
                    existingInputs={inputs}
                    onResolveAndExecute={handleResolveMissingInputsAndContinue}
                    onDismiss={() => setMissingInputsState(null)}
                  />
                )}

                {/* Error Banner */}
                {errorMessage && !missingInputsState && (
                  <div className="bg-accent-rose/10 border border-accent-rose/30 rounded-xl p-4 flex items-start space-x-3 text-accent-rose text-xs">
                    <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-sm">Execution Notification</h4>
                      <p className="mt-0.5 text-slate-300">{errorMessage}</p>
                    </div>
                  </div>
                )}

                {/* Execution Results Section */}
                {executionResponse && (
                  <div className="space-y-6 animate-fadeIn">
                    {/* AI Routing Card */}
                    <RoutingCard
                      routing={executionResponse.routing}
                      workflow={executionResponse.workflow}
                    />

                    {/* Execution Trace */}
                    <ExecutionTraceView execution={executionResponse.execution} />

                    {/* Final Result Artifacts (if successful) */}
                    {executionResponse.success && executionResponse.result && (
                      <ResultRenderer
                        workflowId={executionResponse.routing.workflow_id}
                        workflowName={executionResponse.workflow?.name || executionResponse.routing.workflow_id}
                        expectedOutputSpec={executionResponse.result.expected_output_spec || 'Completed output'}
                        resultData={executionResponse.result}
                      />
                    )}
                  </div>
                )}
              </div>
            </main>
          </>
        )}

        {/* Workflow Registry Explorer Tab */}
        {activeTab === 'explorer' && (
          <main className="flex-1 overflow-y-auto p-6 md:p-8">
            <div className="max-w-6xl mx-auto">
              <WorkflowExplorer
                workflows={workflows}
                loading={workflowsLoading}
                onSelectAndRun={handleSelectWorkflowFromExplorer}
              />
            </div>
          </main>
        )}


      </div>

      {/* Floating Interactive Toast Notifications */}
      {toast && (
        <Toast
          type={toast.type}
          title={toast.title}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};
