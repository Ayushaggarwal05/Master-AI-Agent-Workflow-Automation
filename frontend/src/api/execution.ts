import { apiClient } from './client';
import { ExecuteRequest, ExecuteResponse } from '@/types';

export async function runWorkflowExecution(
  payload: ExecuteRequest
): Promise<ExecuteResponse> {
  return apiClient<ExecuteResponse>('/execute', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
