/**
 * API Type Definitions
 * TypeScript types matching FastAPI backend models
 */

export interface HealthCheckResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  timestamp: string;
  processing_time: number;
}

export interface ResumeUploadResponse {
  success: boolean;
  message: string;
  resume_id?: string;
  resume_text?: string;
  cleaned_text?: string;
  extraction_metadata?: ExtractionMetadata;
}

export interface ExtractionMetadata {
  parser_used?: string;
  confidence?: number;
  ocr_used?: boolean;
  fallback_count?: number;
  success?: boolean;
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

export interface AnalyzeResumeResponse {
  success: boolean;
  message: string;
  extracted_skills: string[];
  categorized_skills: Record<string, string[]>;
  skill_confidence: number;
  skill_count: number;
  extraction_method: string;
  top_jobs: JobMatch[];
  best_match?: JobMatch;
  matched_skills: string[];
  missing_skills: string[];
  semantic_score?: number;
  skill_overlap_score?: number;
  ats_score?: number;
  quality_report?: Record<string, any>;
}

export interface ResumeFeedbackRequest {
  resume_text: string;
  resume_skills: string[];
  job_title?: string;
  job_description?: string;
}

export interface ResumeFeedbackResponse {
  success: boolean;
  message: string;
  feedback: string;
  suggestions: string[];
}

export interface CareerRoadmapRequest {
  resume_skills: string[];
  missing_skills: string[];
  target_role?: string;
}

export interface RoadmapMilestone {
  phase: string;
  skills_to_learn: string[];
  timeline: string;
  resources: string[];
}

export interface CareerRoadmapResponse {
  success: boolean;
  message: string;
  target_role: string;
  roadmap: string;
  recommendations: string[];
}
