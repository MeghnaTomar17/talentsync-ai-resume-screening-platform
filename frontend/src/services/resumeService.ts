import { apiClient, unwrapResponse } from '@/api/client';
import type {
  AnalyzeResumeData,
  CareerRoadmapData,
  CareerRoadmapRequest,
  RankCandidatesData,
  RankCandidatesRequest,
  ResumeFeedbackData,
  ResumeFeedbackRequest,
  ResumeUploadData,
} from '@/types/api';

export async function uploadResume(file: File): Promise<ResumeUploadData> {
  const formData = new FormData();
  formData.append('file', file);

  return unwrapResponse<ResumeUploadData>(
    apiClient.post('/upload_resume', formData, {
      // enable_ocr is a query parameter on the FastAPI endpoint
      params: { enable_ocr: true },
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: () => undefined,
    })
  );
}

export interface TargetJob {
  description?: string;
  title?: string;
}

export async function analyzeResume(
  resumeText: string,
  targetJob?: TargetJob
): Promise<AnalyzeResumeData> {
  const jobDescription = targetJob?.description?.trim();
  return unwrapResponse<AnalyzeResumeData>(
    apiClient.post('/analyze_resume', {
      resume_text: resumeText,
      enable_llm: false,
      // Without a job description the backend uses the best dataset match
      job_description: jobDescription || undefined,
      job_title: jobDescription ? targetJob?.title?.trim() || undefined : undefined,
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

export async function rankCandidates(
  payload: RankCandidatesRequest
): Promise<RankCandidatesData> {
  return unwrapResponse<RankCandidatesData>(
    apiClient.post('/rank_candidates', payload)
  );
}
