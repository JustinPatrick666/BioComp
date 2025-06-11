from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UploadResponse(BaseModel):
    """DICOM上传响应模型"""
    filename: str
    saved_path: str
    message: Optional[str] = None

class StatusResponse(BaseModel):
    """服务状态响应模型"""
    status: str
    message: str

class DicomResult(BaseModel):
    """DICOM文件处理结果"""
    filename: str
    patient_id: Optional[str] = None
    study_date: Optional[str] = None
    modality: Optional[str] = None
    additional_info: Optional[dict] = None  # 可选字段，用于存储额外的信息

class DicomResultsResponse(BaseModel):
    """多个DICOM文件处理结果"""
    results: List[DicomResult]

# AI服务相关模型
class HealthCheckResponse(BaseModel):
    """AI服务健康检查响应"""
    status: str
    service: Optional[str] = None
    version: Optional[str] = None
    timestamp: str
    gpu_available: Optional[bool] = None
    model_loaded: Optional[bool] = None

class SupportedModalitiesResponse(BaseModel):
    """支持的影像模态响应"""
    modalities: List[str]
    description: Dict[str, str]

class ModelInfoResponse(BaseModel):
    """AI模型信息响应"""
    model_name: str
    version: str
    supported_modalities: List[str]
    input_formats: List[str]
    model_status: str
    description: str

class TumorDetection(BaseModel):
    """肿瘤检测结果"""
    tumor_id: str
    location: Dict[str, Any]  # 肿瘤位置信息
    size: Dict[str, float]  # 肿瘤尺寸
    volume: float  # 肿瘤体积
    confidence: float  # 检测置信度

class RiskAssessment(BaseModel):
    """风险评估结果"""
    risk_level: str  # low, medium, high
    risk_score: float  # 0-100
    factors: List[str]  # 风险因素
    recommendations: List[str]  # 建议

class TumorAnalysisResult(BaseModel):
    """肿瘤分析结果"""
    session_id: str
    patient_id: Optional[str] = None
    modality: str
    analysis_timestamp: str
    detected_tumors: List[TumorDetection]
    risk_assessment: RiskAssessment
    segmentation_map_url: Optional[str] = None
    summary: str
    processing_time: float

class PredictRequest(BaseModel):
    """预测请求模型"""
    modality: str
    patient_id: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None

class PredictResponse(BaseModel):
    """预测响应模型"""
    success: bool
    session_id: Optional[str] = None
    result: Optional[TumorAnalysisResult] = None
    error: Optional[str] = None

class BatchPredictRequest(BaseModel):
    """批量预测请求"""
    modality: str
    patient_ids: Optional[List[str]] = None
    batch_name: Optional[str] = None

class BatchPredictResponse(BaseModel):
    """批量预测响应"""
    success: bool
    batch_id: str
    session_ids: List[str]
    status: str  # pending, processing, completed, failed
    estimated_time: Optional[int] = None  # 估计完成时间（秒）

class DownloadRequest(BaseModel):
    """下载请求"""
    session_id: str
    file_type: str  # segmentation, report, raw_output