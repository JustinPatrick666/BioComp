
// DICOM相关类型
export interface DicomFile {
  filename: string;
  patientId?: string;
  studyDate?: string;
  modality?: string;
  additionalInfo?: any;
}

export interface UploadResponse {
  filename: string;
  saved_path: string;
  message?: string;
}

// AI分析相关类型
export interface HealthCheckResponse {
  status: string;
  message: string;
  timestamp: string;
}

export interface SupportedModalitiesResponse {
  modalities: string[];
  description: { [key: string]: string };
}

export interface ModelInfoResponse {
  model_name: string;
  version: string;
  supported_modalities: string[];
  input_formats: string[];
  model_status: string;
  description: string;
}

export interface TumorDetection {
  tumor_id: string;
  location: { [key: string]: any };
  size: { [key: string]: number };
  volume: number;
  confidence: number;
}

export interface RiskAssessment {
  risk_level: 'low' | 'medium' | 'high';
  risk_score: number;
  factors: string[];
  recommendations: string[];
}

export interface TumorAnalysisResult {
  session_id: string;
  patient_id?: string;
  modality: string;
  analysis_timestamp: string;
  detected_tumors: TumorDetection[];
  risk_assessment: RiskAssessment;
  segmentation_map_url?: string;
  summary: string;
  processing_time: number;
}

export interface PredictResponse {
  success: boolean;
  session_id?: string;
  result?: TumorAnalysisResult;
  error?: string;
}

export interface BatchPredictResponse {
  success: boolean;
  batch_id: string;
  session_ids: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  estimated_time?: number;
}

export interface AnalysisSession {
  session_id: string;
  filename: string;
  modality: string;
  patient_id?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: TumorAnalysisResult;
  created_at: string;
  updated_at: string;
}

// 分析历史记录
export interface AnalysisHistory {
  sessions: AnalysisSession[];
  totalCount: number;
  lastUpdated: string;
}
