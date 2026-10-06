import { apiClient } from './client';
import { UploadResponse } from '@/types';

export async function uploadInputFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return apiClient<UploadResponse>('/upload', {
    method: 'POST',
    body: formData,
  });
}
