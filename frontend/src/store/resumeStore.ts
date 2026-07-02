import type { AnalyzeResumeData, ResumeUploadData } from '@/types/api';

const UPLOAD_KEY = 'talentsync.upload';
const ANALYSIS_KEY = 'talentsync.analysis';

export function saveUpload(upload: ResumeUploadData) {
  sessionStorage.setItem(UPLOAD_KEY, JSON.stringify(upload));
}

export function getUpload(): ResumeUploadData | undefined {
  const raw = sessionStorage.getItem(UPLOAD_KEY);
  return raw ? (JSON.parse(raw) as ResumeUploadData) : undefined;
}

export function saveAnalysis(analysis: AnalyzeResumeData) {
  sessionStorage.setItem(ANALYSIS_KEY, JSON.stringify(analysis));
}

export function getAnalysis(): AnalyzeResumeData | undefined {
  const raw = sessionStorage.getItem(ANALYSIS_KEY);
  return raw ? (JSON.parse(raw) as AnalyzeResumeData) : undefined;
}
