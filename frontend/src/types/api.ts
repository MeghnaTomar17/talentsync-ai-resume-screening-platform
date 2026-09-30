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
  job_description?: string;
  job_title?: string;
}

export interface PartialMatch {
  skill: string;
  related_skills: string[];
}

export interface ScoreComponent {
  score: number;
  weight: number;
  contribution: number;
  max_contribution: number;
}

export interface ScoreBreakdown {
  ats_score: number;
  formula: string;
  components: {
    semantic_similarity: ScoreComponent;
    skill_overlap: ScoreComponent;
    resume_quality: ScoreComponent;
  };
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
  partial_matches?: PartialMatch[];
  score_breakdown?: ScoreBreakdown | null;
  explanation?: string[];
  job_source?: 'provided' | 'dataset';
}

export interface ResumeFeedbackRequest {
  resume_text: string;
  resume_skills: string[];
  job_title?: string;
  job_description?: string;
  missing_skills?: string[];
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

export interface CandidateInput {
  candidate_id: string;
  resume_text: string;
}

export interface RankCandidatesRequest {
  job_description: string;
  job_title?: string;
  candidates: CandidateInput[];
  enable_llm?: boolean;
}

export interface CandidateRanking {
  rank: number;
  candidate_id: string;
  ats_score: number;
  semantic_score: number;
  skill_overlap_score: number;
  quality_score: number;
  extracted_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  partial_matches: PartialMatch[];
  explanation: string[];
}

export interface SkillCount {
  skill: string;
  count: number;
}

export interface RankingSummary {
  total_candidates: number;
  average_ats_score?: number;
  highest_ats_score?: number;
  lowest_ats_score?: number;
  top_candidate?: string;
  most_common_missing_skills?: SkillCount[];
  most_common_matched_skills?: SkillCount[];
}

export interface RankCandidatesData {
  job_title: string;
  job_skills: string[];
  candidates: CandidateRanking[];
  summary: RankingSummary;
}
