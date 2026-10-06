import { apiClient } from './client';
import {
  WorkflowListResponse,
  WorkflowDetailResponse,
  WorkflowSummary,
  HealthResponse,
} from '@/types';

export async function getHealth(): Promise<HealthResponse> {
  return apiClient<HealthResponse>('/health');
}

export async function getWorkflows(): Promise<WorkflowListResponse> {
  return apiClient<WorkflowListResponse>('/workflows');
}

export async function getWorkflowById(id: string): Promise<WorkflowDetailResponse> {
  return apiClient<WorkflowDetailResponse>(`/workflows/${encodeURIComponent(id)}`);
}

export async function getWorkflowSummaries(): Promise<WorkflowSummary[]> {
  return apiClient<WorkflowSummary[]>('/workflows/summaries');
}
