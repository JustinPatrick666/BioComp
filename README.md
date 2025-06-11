<<<<<<< HEAD
# 医学影像肿瘤分析系统 - 使用指南

## 🏥 系统概述

这是一个基于AI的医学影像肿瘤分析系统，集成了Vue 3前端、FastAPI后端和nnU-Net AI分析服务。系统支持MRI、CT、PET、US等多种影像模态的肿瘤检测、分割和风险评估。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue 3)   │    │  后端 (FastAPI) │    │ AI服务 (nnU-Net)│
│   localhost:5175 │◄──►│  localhost:8000 │◄──►│  localhost:5001 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速启动

### 方法1: 使用启动脚本（推荐）

```bash
# 启动完整系统
python start_system.py
```

### 方法2: 手动启动

1. **启动模拟AI服务**
```bash
python mock_ai_service.py
```

2. **启动后端服务**
```bash
cd backend
python run_backend.py
```

3. **启动前端服务**
```bash
cd frontend
npm run dev
```

## 🔧 功能特性

### 核心功能
- ✅ DICOM文件上传和查看
- ✅ 多模态医学影像支持 (MRI/CT/PET/US)
- ✅ AI肿瘤检测和分割
- ✅ 风险评估和建议
- ✅ 分析报告生成和下载
- ✅ 历史记录管理

### AI分析能力
- 🧠 肿瘤自动检测
- 📏 肿瘤体积测量
- 🎯 精确位置定位
- 📊 风险等级评估
- 💡 治疗建议生成
- 🖼️ 分割图像导出

## 📱 用户界面指南

### 主界面
- **文件上传区**: 拖拽或点击上传DICOM文件
- **图像查看器**: 支持缩放、平移、窗位窗宽调节
- **工具栏**: 缩放、重置、测量等工具
- **AI分析按钮**: 启动智能分析功能

### AI分析流程
1. **上传图像**: 支持.dcm、.nii、.nii.gz格式
2. **配置参数**: 选择影像模态和患者ID
3. **开始分析**: 实时显示分析进度
4. **查看结果**: 详细的检测结果和风险评估
5. **下载报告**: 导出分析报告和分割图像

## 🔍 API接口

### AI分析接口

#### 健康检查
```http
GET /api/v1/ai/health
```

#### 支持的模态
```http
GET /api/v1/ai/supported_modalities
```

#### 单文件分析
```http
POST /api/v1/ai/predict
Content-Type: multipart/form-data

file: (binary)
modality: string
patient_id: string (optional)
```

#### 批量分析
```http
POST /api/v1/ai/batch_predict
Content-Type: multipart/form-data

files: (binary array)
modality: string
batch_name: string (optional)
patient_ids: string (JSON array, optional)
```

#### 下载结果
```http
GET /api/v1/ai/download/{session_id}/{file_type}
```

## 🧪 测试指南

### 运行系统测试
```bash
python test_system.py
```

### 测试内容
- ✅ AI服务连接性
- ✅ 后端API代理
- ✅ 文件分析流程
- ✅ 下载功能
- ✅ 前端界面访问

### 手动测试步骤
1. **访问前端**: http://localhost:5175
2. **上传DICOM文件**: 使用`backend/uploads/image-00000.dcm`或Dataset中的文件
3. **启动AI分析**: 选择CT模态，输入患者ID
4. **查看结果**: 检查检测结果和风险评估
5. **下载报告**: 测试报告和分割图下载

## 📂 项目结构

```
d:\医学竞赛\
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── services/         # API服务
│   │   ├── views/           # 页面
│   │   └── stores/          # 状态管理
│   └── package.json
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/          # API路由
│   │   ├── models/          # 数据模型
│   │   └── services/        # 业务逻辑
│   ├── uploads/             # 上传文件
│   └── requirements.txt
├── Dataset/                  # 测试数据
│   ├── CT/images/           # CT图像
│   └── MRI/images/          # MRI图像
├── mock_ai_service.py       # 模拟AI服务
├── start_system.py          # 系统启动脚本
└── test_system.py           # 系统测试脚本
```

## 🔧 配置说明

### 后端配置 (backend/app/config.py)
```python
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
UPLOAD_DIR = "uploads"
AI_SERVICE_URL = "http://localhost:5001"
```

### 前端配置 (frontend/vite.config.ts)
```typescript
server: {
  port: 5175,
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## 🚨 故障排除

### 常见问题

1. **AI服务连接失败**
   - 检查模拟AI服务是否启动 (localhost:5001)
   - 查看控制台错误信息
   - 重新启动AI服务

2. **文件上传失败**
   - 检查文件格式 (.dcm, .nii, .nii.gz)
   - 确认后端服务运行正常
   - 检查文件大小限制

3. **前端无法访问**
   - 确认npm依赖已安装
   - 检查端口5175是否被占用
   - 清除浏览器缓存

4. **分析结果异常**
   - 检查AI服务健康状态
   - 验证上传的文件格式
   - 查看后端日志

### 日志查看
- **前端**: 浏览器开发者工具 → Console
- **后端**: 启动终端输出
- **AI服务**: AI服务终端输出

## 📈 性能优化

### 建议配置
- **内存**: 最少8GB，推荐16GB+
- **存储**: SSD硬盘，至少10GB可用空间
- **网络**: 低延迟连接，确保服务间通信顺畅

### 优化建议
1. 使用生产环境配置部署
2. 配置反向代理 (Nginx)
3. 启用数据库连接池
4. 配置文件缓存策略

## 🔐 安全注意事项

1. **数据隐私**: 确保患者数据安全
2. **访问控制**: 生产环境需要身份验证
3. **文件验证**: 严格验证上传文件类型
4. **网络安全**: 使用HTTPS协议

## 📞 技术支持

### 开发团队
- **前端开发**: Vue 3 + Element Plus
- **后端开发**: FastAPI + Python
- **AI集成**: nnU-Net + PyTorch

## 📝 更新日志

### v1.0.0 (当前版本)
- ✅ 完成基础系统架构
- ✅ 实现AI服务集成
- ✅ 完成前后端通信
- ✅ 支持多模态影像分析
- ✅ 实现结果下载功能

### 计划功能
- 🔄 用户认证系统
- 🔄 数据库持久化
- 🔄 批量处理优化
- 🔄 移动端适配
- 🔄 云端部署支持

---

**最后更新**: 2025年5月29日  
**版本**: v1.0.0  
**维护团队**: 医学影像AI开发组
=======
# BioComp
>>>>>>> be363bdde94cf25773d8f300311c13b048cd43b0
