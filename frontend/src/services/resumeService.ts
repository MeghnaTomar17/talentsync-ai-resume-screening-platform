import { apiClient, unwrapResponse } from '@/api/client';
import type {
  AnalyzeResumeData,
  CareerRoadmapData,
  CareerRoadmapRequest,
  ResumeFeedbackData,
  ResumeFeedbackRequest,
  ResumeUploadData,
} from '@/types/api';

export async function uploadResume(file: File): Promise<ResumeUploadData> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('enable_ocr', 'true');

  return unwrapResponse<ResumeUploadData>(
    apiClient.post('/upload_resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: () => undefined,
    })
  );
}

export async function analyzeResume(
  resumeText: string
): Promise<AnalyzeResumeData> {
  return unwrapResponse<AnalyzeResumeData>(
    apiClient.post('/analyze_resume', {
      resume_text: resumeText,
      enable_llm: false,
    })
  );
}

export async function getResumeFeedback(
  payload: ResumeFeedbackRequest
): Promise<ResumeFeedbackData> {
  return unwrapResponse<ResumeFeedbackData>(
    apiClient.post('/resume_feedback', payload)
  );
}

export async function getCareerRoadmap(
  payload: CareerRoadmapRequest
): Promise<CareerRoadmapData> {
  return unwrapResponse<CareerRoadmapData>(
    apiClient.post('/career_roadmap', payload)
  );
}
