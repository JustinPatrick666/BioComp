# filepath: d:\医学竞赛\backend\app\api\v1\ai.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import httpx
import json
import os
from datetime import datetime
from ...models.schemas import (
    HealthCheckResponse, 
    SupportedModalitiesResponse, 
    ModelInfoResponse,
    PredictRequest,
    PredictResponse,
    BatchPredictRequest,
    BatchPredictResponse
)

router = APIRouter(tags=["AI Analysis"])

# AI服务地址
AI_SERVICE_URL = "http://localhost:5002"

async def get_ai_client():
    """获取AI服务客户端"""
    return httpx.AsyncClient(base_url=AI_SERVICE_URL, timeout=300.0)

@router.get("/health", response_model=HealthCheckResponse)
async def check_ai_health():
    """检查AI服务健康状态"""
    try:
        print(f"[DEBUG] 尝试连接 AI 服务: {AI_SERVICE_URL}/health")
        
        # 创建连接配置，添加更多的连接参数
        timeout = httpx.Timeout(10.0, connect=5.0)
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            response = await client.get(f"{AI_SERVICE_URL}/health")
            print(f"[DEBUG] AI 服务响应状态码: {response.status_code}")
            print(f"[DEBUG] AI 服务响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] 解析后的数据: {data}")
                print(f"[DEBUG] 数据类型: {type(data)}")
                print(f"[DEBUG] 数据字段: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # 验证数据结构
                try:
                    health_response = HealthCheckResponse(**data)
                    print(f"[DEBUG] HealthCheckResponse创建成功: {health_response}")
                    return health_response
                except Exception as pydantic_error:
                    print(f"[ERROR] Pydantic验证失败: {pydantic_error}")
                    print(f"[DEBUG] 尝试手动创建响应...")
                    return HealthCheckResponse(
                        status=data.get("status", "unknown"),
                        service=data.get("service"),
                        version=data.get("version"),
                        timestamp=data.get("timestamp", datetime.now().isoformat()),
                        gpu_available=data.get("gpu_available"),
                        model_loaded=data.get("model_loaded")
                    )
            else:
                print(f"[ERROR] AI 服务返回非200状态码: {response.status_code}")
                # 返回断开连接状态而不是抛出异常
                return HealthCheckResponse(
                    status="disconnected",
                    timestamp=datetime.now().isoformat(),
                    service="AI Analysis Service",
                    version="unknown"
                )
    except httpx.RequestError as e:
        print(f"[ERROR] 连接 AI 服务失败: {type(e).__name__}: {str(e)}")
        # 返回断开连接状态而不是抛出异常
        return HealthCheckResponse(
            status="disconnected", 
            timestamp=datetime.now().isoformat(),
            service="AI Analysis Service",
            version="unknown"
        )
    except Exception as e:
        print(f"[ERROR] 处理 AI 健康检查时发生未知错误: {type(e).__name__}: {str(e)}")
        # 返回错误状态而不是抛出异常  
        return HealthCheckResponse(
            status="error",
            timestamp=datetime.now().isoformat(), 
            service="AI Analysis Service",
            version="unknown"
        )

@router.get("/supported_modalities", response_model=SupportedModalitiesResponse)
async def get_supported_modalities():
    """获取支持的影像模态"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/supported_modalities")
            response.raise_for_status()
            data = response.json()
            return SupportedModalitiesResponse(**data)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")

@router.get("/model_info", response_model=ModelInfoResponse)
async def get_model_info():
    """获取AI模型信息"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/model_info")
            response.raise_for_status()
            data = response.json()
            return ModelInfoResponse(**data)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")

@router.post("/predict", response_model=PredictResponse)
async def predict_tumor(
    file: UploadFile = File(...),
    modality: str = Form(...),
    patient_id: Optional[str] = Form(None)
):
    """肿瘤分析预测"""
    # 验证文件类型
    allowed_extensions = ['.dcm', '.dicom', '.nii', '.nii.gz']
    file_extension = os.path.splitext(file.filename.lower())[1]
    if file_extension == '.gz':
        # 处理 .nii.gz 文件
        base_name = os.path.splitext(file.filename[:-3])[0]
        if base_name.endswith('.nii'):
            file_extension = '.nii.gz'
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    # 验证影像模态
    allowed_modalities = ['MRI', 'CT', 'PET', 'US']
    if modality.upper() not in allowed_modalities:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported modality. Allowed: {allowed_modalities}"
        )
    
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 准备发送到AI服务的文件数据
        files = {"file": (file.filename, file_content, file.content_type)}
        data = {
            "modality": modality.upper(),
            "patient_id": patient_id
        }
        
        # 发送到AI服务
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/predict",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result_data = response.json()
                return PredictResponse(
                    success=True,
                    session_id=result_data.get("session_id"),
                    result=result_data.get("result")
                )
            else:
                error_detail = response.text
                return PredictResponse(
                    success=False,
                    error=f"AI analysis failed: {error_detail}"
                )
                
    except httpx.RequestError as e:
        return PredictResponse(
            success=False,
            error=f"Connection error: {str(e)}"
        )
    except Exception as e:
        return PredictResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@router.post("/batch_predict", response_model=BatchPredictResponse)
async def batch_predict_tumors(
    files: List[UploadFile] = File(...),
    modality: str = Form(...),
    batch_name: Optional[str] = Form(None),
    patient_ids: Optional[str] = Form(None)  # JSON字符串形式的patient_ids列表
):
    """批量肿瘤分析"""
    # 解析patient_ids
    patient_id_list = []
    if patient_ids:
        try:
            patient_id_list = json.loads(patient_ids)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid patient_ids format")
    
    # 验证文件数量
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # 验证影像模态
    allowed_modalities = ['MRI', 'CT', 'PET', 'US']
    if modality.upper() not in allowed_modalities:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported modality. Allowed: {allowed_modalities}"
        )
    
    try:
        # 准备批量文件数据
        file_data = []
        for i, file in enumerate(files):
            content = await file.read()
            file_data.append(("files", (file.filename, content, file.content_type)))
        
        # 准备表单数据
        data = {
            "modality": modality.upper(),
            "batch_name": batch_name or f"batch_{len(files)}_files"
        }
        
        if patient_id_list:
            data["patient_ids"] = json.dumps(patient_id_list)
        
        # 发送到AI服务
        async with httpx.AsyncClient(timeout=600.0) as client:  # 批量处理需要更长超时
            response = await client.post(
                f"{AI_SERVICE_URL}/batch_predict",
                files=file_data,
                data=data
            )
            
            response.raise_for_status()
            result_data = response.json()
            return BatchPredictResponse(**result_data)
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@router.get("/download/{session_id}/{file_type}")
async def download_analysis_result(session_id: str, file_type: str):
    """下载分析结果文件"""
    # 验证文件类型
    allowed_file_types = ['segmentation', 'report', 'raw_output', 'pdf']
    if file_type not in allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {allowed_file_types}"
        )
    
    try:
        # 代理下载请求到AI服务
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{AI_SERVICE_URL}/download/{session_id}/{file_type}",
                follow_redirects=True
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 如果是PDF文件，需要解码base64内容
                if file_type == "pdf":
                    import base64
                    pdf_content = base64.b64decode(result["content"])
                    return StreamingResponse(
                        iter([pdf_content]),
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f"attachment; filename={result['filename']}"
                        }
                    )
                elif file_type == "report":
                    # 文本报告
                    content = result["content"].encode('utf-8')
                    return StreamingResponse(
                        iter([content]),
                        media_type="text/plain; charset=utf-8",
                        headers={
                            "Content-Disposition": f"attachment; filename={result['filename']}"
                        }
                    )
                else:
                    # 其他文件类型
                    return StreamingResponse(
                        iter([response.content]),
                        media_type=response.headers.get('content-type', 'application/octet-stream'),
                        headers={
                            "Content-Disposition": f"attachment; filename={session_id}_{file_type}"
                        }
                    )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to download file from AI service"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Download error: {str(e)}")

@router.get("/sessions/{session_id}/status")
async def get_analysis_status(session_id: str):
    """获取分析会话状态"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/sessions/{session_id}/status")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_analysis_session(session_id: str):
    """删除分析会话"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{AI_SERVICE_URL}/sessions/{session_id}")
            response.raise_for_status()
            return {"message": f"Session {session_id} deleted successfully"}
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")