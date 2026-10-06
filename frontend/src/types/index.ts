export interface Workflow {
  id: string;
  name: string;
  trigger: string;
  inputs: string[];
  steps: string[];
  decision: string;
  tools: string[];
  output: string;
  metadata?: Record<string, any>;
}

export interface WorkflowSummary {
  id: string;
  name: string;
  trigger: string;
  tools: string[];
  step_count: number;
}

export interface WorkflowListResponse {
  total: number;
  workflows: Workflow[];
}

export interface WorkflowDetailResponse {
  workflow: Workflow;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  workflows_loaded: number;
  excel_path: string;
}

export interface WorkflowSelection {
  workflow_id: string;
  confidence: number;
  reasoning: string;
  required_inputs: string[];
  missing_inputs: string[];
}

export type ExecutionEventType =
  | 'request_received'
  | 'workflow_selected'
  | 'input_validation'
  | 'step_started'
  | 'tool_called'
  | 'tool_result'
  | 'condition_evaluated'
  | 'step_completed'
  | 'final_result'
  | 'warning'
  | 'error';

export interface ExecutionEvent {
  timestamp: string;
  type: ExecutionEventType;
  step?: string | null;
  tool?: string | null;
  details?: Record<string, any> | null;
  elapsed_ms?: number | null;
}

export interface ExecutionSummary {
  status: 'completed' | 'failed' | 'running';
  total_duration_ms: number;
  events_count: number;
  trace: ExecutionEvent[];
}

export interface ErrorDetails {
  code: string;
  message: string;
  failed_step?: string | null;
  tool?: string | null;
  details?: Record<string, any>;
}

export interface ExecuteRequest {
  message: string;
  inputs?: Record<string, any>;
  workflow_id?: string | null;
}

export interface ExecuteResponse {
  success: boolean;
  workflow?: WorkflowSummary | null;
  routing: WorkflowSelection;
  execution: ExecutionSummary;
  result?: Record<string, any> | null;
  error?: ErrorDetails | null;
}

export interface SessionHistoryItem {
  id: string;
  timestamp: Date;
  message: string;
  workflowId: string;
  workflowName: string;
  success: boolean;
  durationMs: number;
  response: ExecuteResponse;
}

export interface UploadResponse {
  success: boolean;
  filename: string;
  file_path: string;
  size_bytes: number;
  content_type: string;
  message: string;
}
