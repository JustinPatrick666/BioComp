import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',  // 这会匹配到vite.config.ts中的代理配置
  timeout: 30000,   // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// DICOM相关接口
export const dicomApi = {  // 上传DICOM文件
  async uploadDicom(file: File, onProgress?: (progressEvent: any) => void) {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/v1/dicom/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 10000, // 10秒超时，提供更好的用户体验
      onUploadProgress: onProgress // 添加上传进度回调
    });
  },// 获取所有DICOM文件结果
  async getDicomResults() {
    return api.get('/v1/dicom/results');
  },
  
  // 获取指定DICOM文件
  async getDicomFile(filename: string) {
    return api.get(`/v1/dicom/${filename}`, {
      responseType: 'blob'
    });
  }
};

// AI分析相关接口
export const aiApi = {
  // 检查AI服务健康状态
  async checkHealth() {
    return api.get('/v1/ai/health');
  },

  // 获取支持的影像模态
  async getSupportedModalities() {
    return api.get('/v1/ai/supported_modalities');
  },

  // 获取AI模型信息
  async getModelInfo() {
    return api.get('/v1/ai/model_info');
  },

  // 单文件肿瘤分析
  async predictTumor(file: File, modality: string, patientId?: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('modality', modality);
    if (patientId) {
      formData.append('patient_id', patientId);
    }

    return api.post('/v1/ai/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000 // AI分析需要更长时间
    });
  },

  // 批量肿瘤分析
  async batchPredictTumors(files: File[], modality: string, batchName?: string, patientIds?: string[]) {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    formData.append('modality', modality);
    
    if (batchName) {
      formData.append('batch_name', batchName);
    }
    
    if (patientIds && patientIds.length > 0) {
      formData.append('patient_ids', JSON.stringify(patientIds));
    }

    return api.post('/v1/ai/batch_predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 600000 // 批量处理需要更长时间
    });
  },
  // 下载分析结果
  async downloadResult(sessionId: string, fileType: 'segmentation' | 'report' | 'raw_output' | 'pdf') {
    return api.get(`/v1/ai/download/${sessionId}/${fileType}`, {
      responseType: 'blob'
    });
  },

  // 获取分析会话状态
  async getSessionStatus(sessionId: string) {
    return api.get(`/v1/ai/sessions/${sessionId}/status`);
  },

  // 删除分析会话
  async deleteSession(sessionId: string) {
    return api.delete(`/v1/ai/sessions/${sessionId}`);
  }
};

export default api;
