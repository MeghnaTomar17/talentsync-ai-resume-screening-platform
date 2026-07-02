export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  timestamp: string;
  processing_time: number;
}

export interface HealthCheckData {
  status: string;
  version: string;
  services: Record<string, string>;
}

export interface ExtractionMetadata {
  parser_used?: string;
  confidence?: number;
  ocr_used?: boolean;
  fallback_count?: number;
  success?: boolean;
  extraction_time?: number;
}

export interface ResumeUploadData {
  resume_id?: string | null;
  resume_text?: string;
  cleaned_text?: string;
  extraction_metadata?: ExtractionMetadata;
}

export interface AnalyzeResumeRequest {
  resume_text: string;
  enable_llm?: boolean;
}

export interface JobMatch {
  job_title: string;
  job_description: string;
  semantic_score: number;
  skill_overlap_score?: number;
  ats_score?: number;
}

export interface QualityReport {
  quality_score?: number;
  quality_level?: string;
  ats_score?: number;
  resume_type?: string;
  warnings?: string[];
  recommendations?: string[];
  text_length?: number;
  skill_count?: number;
  sections_detected?: number;
}

export interface AnalyzeResumeData {
  extracted_skills: string[];
  categorized_skills: Record<string, string[]>;
  skill_confidence: number;
  skill_count: number;
  extraction_method: string;
  top_jobs: JobMatch[];
  best_match?: JobMatch | null;
  matched_skills: string[];
  missing_skills: string[];
  semantic_score?: number | null;
  skill_overlap_score?: number | null;
  ats_score?: number | null;
  quality_report?: QualityReport | null;
}

export interface ResumeFeedbackRequest {
  resume_text: string;
  resume_skills: string[];
  job_title?: string;
  job_description?: string;
}

export interface ResumeFeedbackData {
  feedback: string;
  suggestions: string[];
}

export interface CareerRoadmapRequest {
  resume_skills: string[];
  missing_skills: string[];
  target_role?: string;
}

export interface CareerRoadmapData {
  target_role: string;
  roadmap: string;
  recommendations: string[];
}

export interface ResumeWorkspaceState {
  uploaded?: ResumeUploadData;
  analysis?: AnalyzeResumeData;
}
