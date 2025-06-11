<template>
  <div class="dicom-viewer">
    <!-- 通知系统 -->
    <div class="notifications-container">
      <transition-group name="notification" tag="div">        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          :class="['system-notification', notification.type, { 'show': notification.show }]"
          @click="removeNotification(notification.id)"
        >
          <i :class="getNotificationIcon(notification.type)"></i>
          {{ notification.message }}
        </div>
      </transition-group>
    </div>

    <!-- AI服务状态指示器 -->
    <div :class="['ai-status-indicator', aiServiceStatus]" @click="checkAiHealth">
      <div class="status-dot"></div>
      <span>{{ getAiStatusText() }}</span>
      <i class="fas fa-sync-alt" style="cursor: pointer; margin-left: 4px;"></i>
    </div>    <!-- 加载指示器 -->    <div v-if="loading || uploading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p v-if="uploading">{{ uploadProgressText }}</p>
        <p v-else>处理中...</p>
        
        <!-- 上传进度条 -->
        <div v-if="uploading" class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <div class="progress-text">{{ uploadProgress }}%</div>
        </div>
      </div>
    </div><!-- 图像显示区域 -->
    <div class="image-section">
      <!-- 当没有图像时显示上传提示 -->
      <div v-if="!imageLoaded" class="image-placeholder" 
           @dragover.prevent="isDragOver = true"
           @dragleave.prevent="isDragOver = false"
           @drop.prevent="handleFileDrop"
           @click="$refs.fileInput.click()">
        <div class="placeholder-content">
          <div class="upload-icon">
            <i class="fas fa-image"></i>
          </div>
          <h3>上传DICOM文件</h3>
          <p>点击选择文件或拖拽文件到此区域</p>
          <p class="file-info">支持格式: .dcm, .nii, .nii.gz</p>          <button class="enhanced-button" @click.stop="loadSampleDicom">
            <i class="fas fa-download"></i> 加载示例图像
          </button>
        </div>
        <input 
          ref="fileInput"
          type="file" 
          @change="handleFileUpload" 
          accept=".dcm,.nii,.nii.gz"
          style="display: none;"
        />
      </div>

      <!-- 工具栏 -->
      <div v-if="imageLoaded" class="toolbar">
        <div class="tool-group">
          <button @click="setTool('Pan')" :class="{ active: activeToolName === 'Pan' }" title="平移">
            <i class="fas fa-hand-paper"></i>
          </button>
          <button @click="setTool('Zoom')" :class="{ active: activeToolName === 'Zoom' }" title="缩放">
            <i class="fas fa-search-plus"></i>
          </button>
          <button @click="setTool('Wwwc')" :class="{ active: activeToolName === 'Wwwc' }" title="窗位窗宽">
            <i class="fas fa-adjust"></i>
          </button>
          <button @click="resetView" title="重置视图">
            <i class="fas fa-home"></i>
          </button>
          <button @click="loadNewImage" title="加载新图像" class="load-new-btn">
            <i class="fas fa-folder-open"></i>
          </button>
        </div>
        
        <!-- AI分析按钮 -->
        <div class="ai-section">          <button 
            class="enhanced-button success ai-analysis-btn" 
            @click="showAiModal = true"
            :disabled="aiAnalyzing || !imageLoaded"
            title="AI肿瘤分析"
          >
            <i class="fas fa-brain"></i>
            {{ aiAnalyzing ? 'AI分析中...' : 'AI肿瘤分析' }}
          </button>
          <button 
            class="enhanced-button primary history-btn" 
            @click="showHistoryModal = true"
            title="查看诊断历史"
          >
            <i class="fas fa-history"></i>
            诊断历史
          </button>
        </div>
      </div>

      <!-- DICOM图像容器 -->
      <div ref="dicomContainer" class="dicom-container" :style="{ display: imageLoaded ? 'block' : 'none' }"></div>
    </div>

    <!-- 错误显示 -->
    <div v-if="error" class="result-card error">
      <h4><i class="fas fa-exclamation-triangle"></i> 错误</h4>
      <p>{{ error }}</p>
      <button @click="error = ''" class="enhanced-button">确定</button>
    </div>

    <!-- AI分析配置模态框 -->
    <div v-if="showAiModal" class="ai-analysis-overlay" @click="showAiModal = false">
      <div class="ai-analysis-modal" @click.stop>
        <div class="ai-modal-header">
          <h3><i class="fas fa-cog"></i> AI分析配置</h3>
          <button @click="showAiModal = false" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="ai-modal-content">
          <div class="form-group">
            <label for="modality-select">影像模态 *</label>
            <select id="modality-select" v-model="selectedModality">
              <option value="CT">CT (计算机断层扫描)</option>
              <option value="MRI">MRI (磁共振成像)</option>
              <option value="PET">PET (正电子发射断层扫描)</option>
              <option value="US">US (超声)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="patient-id">患者ID (可选)</label>
            <input 
              id="patient-id"
              type="text" 
              v-model="analysisPatientId" 
              placeholder="输入患者标识符"
            />
          </div>
          
          <div class="ai-service-status">
            <span :class="['status-indicator', aiServiceStatus]"></span>
            AI服务状态: {{ getAiStatusText() }}
          </div>
        </div>
        
        <div class="ai-modal-footer">
          <button @click="showAiModal = false" class="enhanced-button">取消</button>
          <button 
            @click="startAiAnalysis" 
            class="enhanced-button success"
            :disabled="!selectedModality || aiServiceStatus === 'disconnected'"
          >
            <i class="fas fa-play"></i> 开始分析
          </button>
        </div>
      </div>
    </div>

    <!-- AI分析进度 -->
    <div v-if="aiAnalyzing" class="ai-analysis-overlay">
      <div class="ai-analysis-modal">
        <div class="ai-analysis-header">
          <h3><i class="fas fa-brain"></i> AI肿瘤分析进行中</h3>
        </div>
        
        <div class="ai-analysis-content">
          <div class="analysis-progress">
            <p>{{ analysisProgress }}</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: analysisProgressPercent + '%' }"></div>
            </div>
            <p>{{ analysisProgressPercent }}%</p>
          </div>
          
          <div class="analysis-info">
            <p><i class="fas fa-info-circle"></i> 分析过程可能需要几分钟时间</p>
            <p><i class="fas fa-shield-alt"></i> 您的数据将被安全处理</p>
          </div>
        </div>
      </div>
    </div>    <!-- AI分析结果 -->
    <div v-if="analysisResult" class="ai-result-overlay" @click="analysisResult = null">
      <div class="ai-result-modal medical-report" @click.stop>
        <div class="ai-result-header">
          <h3><i class="fas fa-file-medical"></i> 医学影像AI智能分析报告</h3>
          <button @click="analysisResult = null" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>
          <div class="ai-result-content">
          <!-- 开头致辞 -->
          <div class="greeting-section">
            <p class="greeting-text">
              <strong>尊敬的医生：</strong><br/>
              您好！以下是患者[{{ analysisResult.patient_id || '未提供' }}]的医学影像分析诊断报告，旨在为您提供辅助诊断信息，以便更全面地了解患者的病情并制定进一步的诊疗计划。
            </p>
          </div>

          <!-- 患者信息 -->
          <div class="patient-info-section">
            <h4><i class="fas fa-user"></i> 患者信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">患者ID:</span>
                <span class="value">{{ analysisResult.patient_id || '未提供' }}</span>
              </div>
              <div class="info-item">
                <span class="label">检查时间:</span>
                <span class="value">{{ formatAnalysisTime(analysisResult.analysis_timestamp) }}</span>
              </div>
              <div class="info-item">
                <span class="label">影像设备类型:</span>
                <span class="value">{{ getModalityFullName(analysisResult.modality) }}</span>
              </div>
              <div class="info-item">
                <span class="label">报告生成时间:</span>
                <span class="value">{{ getCurrentDateTime() }}</span>
              </div>
            </div>
          </div>

          <!-- 分析结果表格 -->
          <div class="analysis-results-section">
            <h4><i class="fas fa-table"></i> 分析结果</h4>
            <div v-if="analysisResult.detected_tumors?.length > 0" class="results-table-container">
              <table class="medical-table">
                <thead>
                  <tr>
                    <th>病变编号</th>
                    <th>位置</th>
                    <th>大小 (mm³)</th>
                    <th>形态特征</th>
                    <th>三维可视化</th>
                    <th>良恶性预测</th>
                    <th>置信度</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(tumor, index) in analysisResult.detected_tumors" :key="index" class="tumor-row">
                    <td>病变 {{ index + 1 }}</td>
                    <td>{{ formatAnatomicalLocation(tumor.location) }}</td>
                    <td>{{ formatTumorSize(tumor.size) }}</td>
                    <td>{{ formatMorphology(tumor.morphology) }}</td>
                    <td class="visualization-cell">
                      <span class="viz-description">MPR重建<br/>MIP投影</span>
                    </td>
                    <td :class="getMalignancyClass(tumor.malignancy)">
                      <span class="malignancy-indicator">
                        {{ getMalignancyIndicator(tumor.malignancy) }}
                        {{ tumor.malignancy?.classification || '未知' }}
                      </span>
                    </td>
                    <td>{{ (tumor.confidence * 100).toFixed(1) }}%</td>
                  </tr>
                </tbody>
              </table>
              
              <!-- 临床参数详情 -->
              <div class="clinical-parameters-section">
                <h5><i class="fas fa-flask"></i> 临床参数详情</h5>
                <div class="parameters-grid">
                  <div v-for="(tumor, index) in analysisResult.detected_tumors" :key="'param-' + index" class="parameter-group">
                    <h6>病变 {{ index + 1 }} 参数</h6>
                    <div class="parameter-list">
                      <div v-if="tumor.clinical_parameters?.suvmax" class="parameter-item">
                        <span class="param-name">SUVmax:</span>
                        <span class="param-value" :class="getSuvmaxClass(tumor.clinical_parameters.suvmax)">
                          {{ tumor.clinical_parameters.suvmax.toFixed(1) }} 
                          <span class="param-status">({{ getSuvmaxStatus(tumor.clinical_parameters.suvmax) }})</span>
                        </span>
                      </div>
                      <div v-if="tumor.clinical_parameters?.hounsfield_units" class="parameter-item">
                        <span class="param-name">CT值:</span>
                        <span class="param-value">
                          {{ tumor.clinical_parameters.hounsfield_units.toFixed(1) }} HU
                          <span class="param-status">({{ getHounsfieldStatus(tumor.clinical_parameters.hounsfield_units) }})</span>
                        </span>
                      </div>
                      <div v-if="tumor.clinical_parameters?.adc_value" class="parameter-item">
                        <span class="param-name">ADC值:</span>
                        <span class="param-value" :class="getAdcClass(tumor.clinical_parameters.adc_value)">
                          {{ tumor.clinical_parameters.adc_value.toFixed(3) }} mm²/s
                          <span class="param-status">({{ getAdcStatus(tumor.clinical_parameters.adc_value) }})</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-tumors">
              <div class="normal-result">
                <i class="fas fa-check-circle text-success"></i>
                <p>✓ 未检测到明显肿瘤病变</p>
                <p>• 影像学检查结果在正常范围内</p>
                <p>• 未发现异常密度影或占位性病变</p>
              </div>
            </div>
          </div>

          <!-- 风险评估 -->
          <div class="risk-assessment-section">
            <h4><i class="fas fa-heartbeat"></i> 风险评估</h4>
            <div class="risk-container">
              <div class="risk-level-display" :class="analysisResult.risk_assessment?.risk_level">
                <div class="risk-indicator">
                  <span class="risk-icon">{{ getRiskIcon(analysisResult.risk_assessment?.risk_level) }}</span>
                  <span class="risk-text">{{ getRiskLevelText(analysisResult.risk_assessment?.risk_level) }}</span>
                </div>
                <div class="risk-score">
                  综合风险评分: {{ analysisResult.risk_assessment?.risk_score || 0 }}/100
                </div>
              </div>
            </div>
          </div>

          <!-- 临床提示 -->
          <div class="clinical-tips-section">
            <h4><i class="fas fa-exclamation-triangle"></i> 临床提示</h4>
            <div class="tips-content">
              {{ getClinicalTips() }}
            </div>
          </div>

          <!-- 诊断建议 -->
          <div class="diagnostic-recommendations-section">
            <h4><i class="fas fa-stethoscope"></i> 诊断建议</h4>
            <div class="recommendations-content">
              <div class="recommendation-category">
                {{ getDiagnosticRecommendations() }}
              </div>
              <ul v-if="analysisResult.risk_assessment?.recommendations" class="recommendations-list">
                <li v-for="(rec, index) in analysisResult.risk_assessment.recommendations" :key="index">
                  <i class="fas fa-check"></i> {{ rec }}
                </li>
              </ul>
            </div>
          </div>

          <!-- 备注说明 -->
          <div class="notes-section">
            <h4><i class="fas fa-info-circle"></i> 重要备注</h4>
            <div class="notes-content">
              <p>⚠️ 本报告仅供参考，最终诊断需结合临床表现和其他检查结果。</p>
              <p>⚠️ AI分析结果需要专业医生进行综合判断和确认。</p>
              <p>⚠️ 如有疑问，请及时咨询相关专科医生。</p>
              <div class="technical-info">
                <p><strong>技术信息:</strong></p>
                <p>• AI模型版本: nnU-Net v2.0</p>
                <p>• 处理时间: {{ analysisResult.processing_time?.toFixed(2) || '未知' }}秒</p>
                <p>• 分析会话ID: {{ analysisResult.session_id || '未知' }}</p>
                <p>• 数据质量: 优良</p>
              </div>
            </div>
          </div>
        </div>        <div class="ai-result-footer">
          <button @click="saveToHistory" class="enhanced-button primary">
            <i class="fas fa-save"></i> 保存到历史
          </button>
          <button @click="downloadPdfReport" class="enhanced-button success">
            <i class="fas fa-file-pdf"></i> 下载PDF报告
          </button>
          <button @click="downloadAnalysisReport" class="enhanced-button">
            <i class="fas fa-download"></i> 下载文本报告
          </button>
          <button @click="downloadSegmentation" class="enhanced-button">
            <i class="fas fa-image"></i> 下载分割图
          </button>          <button @click="analysisResult = null" class="enhanced-button">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 诊断历史弹窗 -->
    <div v-if="showHistoryModal" class="ai-result-overlay" @click="showHistoryModal = false">
      <div class="ai-result-modal diagnosis-history" @click.stop>
        <div class="ai-result-header">
          <h3><i class="fas fa-history"></i> 诊断历史记录</h3>
          <button @click="showHistoryModal = false" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="history-content">
          <div v-if="diagnosisHistory.length === 0" class="empty-history">
            <div class="empty-icon">
              <i class="fas fa-folder-open"></i>
            </div>
            <p>暂无诊断历史记录</p>
            <p class="empty-tip">进行AI分析后可将结果保存到历史记录中</p>
          </div>
          
          <div v-else class="history-list">
            <div class="history-controls">
              <button @click="clearHistory" class="enhanced-button danger-outline">
                <i class="fas fa-trash"></i> 清空历史
              </button>
              <span class="history-count">共 {{ diagnosisHistory.length }} 条记录</span>
            </div>
            
            <div v-for="(record, index) in diagnosisHistory" :key="record.id" class="history-item">
              <div class="history-header">
                <div class="history-info">
                  <h4>
                    <i class="fas fa-file-medical"></i>
                    {{ record.filename || `诊断记录 ${index + 1}` }}
                  </h4>
                  <div class="history-meta">
                    <span class="save-time">
                      <i class="fas fa-clock"></i>
                      {{ formatDateTime(record.savedAt) }}
                    </span>
                    <span class="patient-info">
                      <i class="fas fa-user"></i>
                      患者ID: {{ record.patientId || '未提供' }}
                    </span>
                    <span class="modality-info">
                      <i class="fas fa-image"></i>
                      {{ getModalityFullName(record.modality) }}
                    </span>
                  </div>
                </div>
                <div class="history-actions">
                  <button @click="viewHistoryRecord(record)" class="enhanced-button primary-outline">
                    <i class="fas fa-eye"></i> 查看
                  </button>
                  <button @click="downloadHistoryReport(record)" class="enhanced-button success-outline">
                    <i class="fas fa-download"></i> 下载
                  </button>
                  <button @click="removeHistoryRecord(record.id)" class="enhanced-button danger-outline">
                    <i class="fas fa-trash"></i> 删除
                  </button>
                </div>
              </div>
              
              <div class="history-summary">
                <div class="summary-item">
                  <span class="summary-label">检测结果:</span>
                  <span class="summary-value">
                    {{ record.detectedTumors > 0 ? `发现 ${record.detectedTumors} 个病变` : '未发现病变' }}
                  </span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">风险等级:</span>
                  <span class="summary-value" :class="getRiskLevelClass(record.riskLevel)">
                    {{ getRiskLevelText(record.riskLevel) }}
                  </span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">分析时间:</span>
                  <span class="summary-value">
                    {{ formatDateTime(record.analysisTime) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
          <div class="history-footer">
          <button @click="exportAllHistory" class="enhanced-button">
            <i class="fas fa-file-export"></i> 导出全部历史
          </button>
          <button @click="showHistoryModal = false" class="enhanced-button">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 调试信息 -->
    <div v-if="showDebugInfo" class="debug-info">
      状态: {{ imageLoaded ? '已加载' : '未加载' }} | 
      错误: {{ error || '无' }} | 
      加载中: {{ loading ? '是' : '否' }} |
      AI状态: {{ aiServiceStatus }} |
      会话: {{ currentAnalysisSession || '无' }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { useDicomHistoryStore } from '@/stores/dicomHistory';
import * as cornerstone from 'cornerstone-core';
import * as cornerstoneMath from 'cornerstone-math';
import * as cornerstoneTools from 'cornerstone-tools';
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';
import * as dicomParser from 'dicom-parser';
import { dicomApi, aiApi } from '@/services/api'; // 导入API服务
import { isNiftiFile, loadNiftiFile } from '@/utils/niftiLoader.js'; // 导入NIfTI加载器

// 状态变量
const dicomContainer = ref(null);
const loading = ref(false);
const error = ref('');
const imageLoaded = ref(false);
const showDebugInfo = ref(true); // 设置为 true 以便调试
const isDragOver = ref(false);
let activeToolName = 'Pan';

// AI 相关状态
const showAiModal = ref(false);
const aiAnalyzing = ref(false);
const analysisProgress = ref('');
const analysisProgressPercent = ref(0);
const analysisResult = ref(null);
const currentAnalysisSession = ref('');
const selectedModality = ref('CT');
const analysisPatientId = ref('');
const aiServiceStatus = ref('unknown');
const currentUploadedFile = ref(null); // 保存当前上传的文件

// 诊断历史相关状态
const showHistoryModal = ref(false);
const diagnosisHistory = ref([]);

// 文件上传进度状态
const uploading = ref(false);
const uploadProgress = ref(0);
const uploadProgressText = ref('');

// 添加历史记录store
const historyStore = useDicomHistoryStore();

// 患者信息和图像信息的响应式引用
const patientInfo = ref({
  name: '',
  age: '',
  gender: ''
});

const imageInfo = ref({
  modality: '',
  seriesDescription: '',
  studyDate: '',
  rows: 0,
  columns: 0
});

// 通知状态
const notification = ref({
  show: false,
  message: '',
  type: '' // success, error, warning, info
});

// 通知系统状态
const notifications = ref([]);

// 在挂载时初始化
onMounted(async () => {
  await nextTick();
  try {
    await initializeDicomViewer();
    console.log('DICOM查看器初始化成功');
    
    // 检查AI服务状态
    await checkAiHealth();
    
    // 加载诊断历史记录
    loadDiagnosisHistory();
  } catch (err) {
    console.error('DICOM查看器初始化失败:', err);
    error.value = `初始化失败: ${err.message || err}`;
  }
});

// 初始化DICOM查看器
async function initializeDicomViewer() {
  try {
    // 设置外部依赖
    cornerstoneTools.external.cornerstone = cornerstone;
    cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
    cornerstoneWADOImageLoader.external.dicomParser = dicomParser;

    // 初始化cornerstone tools
    if (!window.cornerstoneToolsInitialized) {
      cornerstoneTools.init({
        mouseEnabled: true,
        touchEnabled: true,
        globalToolSyncEnabled: true
      });
      window.cornerstoneToolsInitialized = true;
    }

    // 注册默认工具
    registerTools();

    // 初始化Web Workers
    cornerstoneWADOImageLoader.webWorkerManager.initialize({
      maxWebWorkers: navigator.hardwareConcurrency || 2,
      startWebWorkersOnDemand: true,
      taskConfiguration: {
        decodeTask: {
          loadCodecsOnStartup: true,
          initializeCodecsOnStartup: true
        }
      }
    });

    // 注册图像加载器
    cornerstone.registerImageLoader('wadouri', cornerstoneWADOImageLoader.wadouri.loadImage);
    cornerstone.registerImageLoader('wadors', cornerstoneWADOImageLoader.wadors.loadImage);

    // 启用元素
    const element = dicomContainer.value;
    if (element) {
      try {
        cornerstone.disable(element);
      } catch (e) {
        // 忽略错误，可能是第一次启用
      }
      cornerstone.enable(element);
      console.log('✅ DICOM元素已启用');
    } else {
      throw new Error('找不到DICOM容器元素');
    }
  } catch (err) {
    console.error('❌ 初始化DICOM查看器失败:', err);
    throw err;
  }
}

// 加载DICOM文件
function loadDicom() {
  loading.value = true;
  error.value = '';
  
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.dcm';
  input.onchange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      console.log('选择的文件:', file.name, file.size);
      handleDicomFile(file);
    } else {
      loading.value = false; // 如果用户没有选择文件，取消加载状态
    }
  };
  
  // 如果用户取消了文件选择，也需要取消加载状态
  setTimeout(() => {
    if (loading.value && !imageLoaded.value && !error.value) {
      loading.value = false;
    }
  }, 1000);
  
  input.click();
}

// 加载新图像（重置状态并打开文件选择器）
function loadNewImage() {
  // 重置状态
  imageLoaded.value = false;
  error.value = '';
  analysisResult.value = null;
  
  // 清理当前图像
  const element = dicomContainer.value;
  if (element) {
    try {
      cornerstone.disable(element);
      cornerstone.enable(element);
    } catch (err) {
      console.warn('清理图像时出错:', err);
    }
  }
  
  // 触发文件选择
  setTimeout(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.dcm,.nii,.nii.gz';
    input.onchange = (e) => {
      if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        handleDicomFile(file);
      }
    };
    input.click();
  }, 100);
}

// 处理DICOM和NIfTI文件
async function handleDicomFile(file) {
  console.log('开始处理医学影像文件:', file.name);
  
  // 等待下一次DOM更新，确保容器元素可用
  await nextTick();
  
  const element = dicomContainer.value;
  console.log('影像容器元素状态:', element ? '已找到' : '未找到');
  
  if (!element) {
    console.error('影像容器元素未找到，等待元素加载...');
    
    // 尝试等待一下再检查
    await new Promise(resolve => setTimeout(resolve, 100));
    const elementRetry = dicomContainer.value;
    
    if (!elementRetry) {
      error.value = '影像容器元素未找到，请刷新页面重试';
      loading.value = false;
      showNotification('影像容器元素未找到，请刷新页面重试', 'error');
      return;
    }
  }

  try {
    console.log('处理医学影像文件:', file.name);
    
    // 获取有效的元素引用
    const validElement = dicomContainer.value;
    
    // 保存当前文件引用供AI分析使用
    window.lastUploadedFile = file;
    
    // 检测文件格式
    const isNifti = isNiftiFile(file.name);
    console.log('文件格式检测:', isNifti ? 'NIfTI' : 'DICOM');
    
    if (isNifti) {
      // 处理NIfTI文件
      console.log('开始处理NIfTI文件...');
      showNotification('正在加载NIfTI文件...', 'info');
      
      try {
        // 使用NIfTI加载器处理文件
        const niftiImage = await loadNiftiFile(file);
        console.log('NIfTI文件加载成功, 图像大小:', niftiImage.rows, 'x', niftiImage.columns);
        
        // 使用统一的加载函数，传递NIfTI标志和图像对象
        const success = await loadAndViewImage(null, validElement, true, niftiImage);
        if (!success) {
          error.value = '显示NIfTI图像失败';
        } else {
          // 添加到历史记录
          const currentDate = new Date();
          historyStore.addRecord({
            id: uuidv4(),
            uploadTime: currentDate.toLocaleString(),
            fileName: file.name,
            patientInfo: patientInfo.value,
            imageInfo: imageInfo.value,
            imageId: 'nifti:' + file.name
          });
          showNotification('NIfTI文件加载成功!', 'success');
        }
      } catch (niftiErr) {
        console.error('处理NIfTI文件失败:', niftiErr);
        error.value = `处理NIfTI文件失败: ${niftiErr.message || niftiErr}`;
        showNotification(`处理NIfTI文件失败: ${niftiErr.message || niftiErr}`, 'error');
      }
    } else {
      // 处理DICOM文件（原有逻辑）
      let imageId;
      try {
        // 开始上传进度追踪
        uploading.value = true;
        uploadProgress.value = 0;
        uploadProgressText.value = '正在上传DICOM文件...';
        
        // 上传进度回调函数
        const onUploadProgress = (progressEvent) => {
          if (progressEvent.lengthComputable) {
            const percentComplete = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            uploadProgress.value = percentComplete;
            uploadProgressText.value = `正在上传文件... ${percentComplete}%`;
            console.log(`上传进度: ${percentComplete}%`);
          }
        };
        
        showNotification('正在上传DICOM文件...', 'info');
        const response = await dicomApi.uploadDicom(file, onUploadProgress);
        
        // 上传完成
        uploading.value = false;
        uploadProgress.value = 100;
        uploadProgressText.value = '上传完成！';
        
        console.log('文件上传成功:', response.data);
        showNotification('文件上传成功，正在加载图像...', 'success');
        
        // 创建WADO URL从后端获取文件
        const filename = response.data.filename;
        // 使用完整的后端URL，而不是通过代理
        imageId = `wadouri:http://localhost:8000/api/v1/dicom/${filename}`;
        console.log('创建的后端imageId:', imageId);
      } catch (uploadErr) {
        // 重置上传状态
        uploading.value = false;
        uploadProgress.value = 0;
        uploadProgressText.value = '';
        
        console.error('上传DICOM文件失败:', uploadErr);
        
        // 检查是否是网络连接问题
        if (uploadErr.code === 'ECONNABORTED' || uploadErr.message?.includes('timeout')) {
          showNotification('上传超时，请检查网络连接或文件大小。正在使用本地模式...', 'warning', 5000);
        } else if (uploadErr.code === 'ERR_NETWORK') {
          showNotification('无法连接到服务器，请确保后端服务已启动。正在使用本地模式...', 'warning', 5000);
        } else {
          showNotification('服务器上传失败，正在使用本地模式...', 'warning', 5000);
        }
        
        // 如果上传失败，回退到本地处理
        imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
        console.log('回退到本地处理, imageId:', imageId);
      }
      
      // 使用统一的加载函数
      const success = await loadAndViewImage(imageId, validElement);
      if (!success) {
        error.value = '加载DICOM文件失败';
      } else {
        // 添加到历史记录
        const currentDate = new Date();
        historyStore.addRecord({
          id: uuidv4(),
          uploadTime: currentDate.toLocaleString(),
          fileName: file.name,
          patientInfo: patientInfo.value,
          imageInfo: imageInfo.value,
          imageId: imageId
        });
      }
    }
  } catch (err) {
    console.error('处理医学影像文件失败:', err);
    error.value = `处理医学影像文件失败: ${err.message || err}`;
  } finally {
    loading.value = false;
    uploading.value = false;
    uploadProgress.value = 0;
    uploadProgressText.value = '';
  }
}

// 加载示例DICOM文件
async function loadSampleDicom() {
  loading.value = true;
  error.value = "";
  
  const element = dicomContainer.value;
  if (!element) {
    error.value = 'DICOM容器元素未找到';
    loading.value = false;
    return;
  }
  
  try {
    // 使用示例图像URL
    const imageId = 'wadouri:https://raw.githubusercontent.com/cornerstonejs/cornerstoneWADOImageLoader/master/examples/CT0.dcm';
    console.log('加载示例DICOM文件:', imageId);
    
    const success = await loadAndViewImage(imageId, element);
    if (!success) {
      error.value = '加载示例DICOM文件失败';
    } else {
      // 添加到历史记录
      const currentDate = new Date();
      historyStore.addRecord({
        id: uuidv4(),
        uploadTime: currentDate.toLocaleString(),
        fileName: '示例DICOM文件',
        patientInfo: patientInfo.value,
        imageInfo: imageInfo.value,
        imageId: imageId
      });
    }  } catch (err) {
    console.error('加载示例DICOM文件失败:', err);
    error.value = `加载示例DICOM文件失败: ${err.message || err}`;
  } finally {
    loading.value = false;
  }
}



// 加载并显示图像 (在handleDicomFile和loadSampleDicom中使用)
async function loadAndViewImage(imageId, element, isNifti = false, niftiImage = null) {
  try {
    console.log('开始加载图像:', imageId, isNifti ? '(NIfTI格式)' : '(DICOM格式)');
    
    // 确保cornerstone已启用
    try {
      cornerstone.getEnabledElement(element);
    } catch (e) {
      cornerstone.enable(element);
    }
    
    let image;
      if (isNifti && niftiImage) {
      // 直接使用NIfTI图像对象
      image = niftiImage;
      console.log('✅ 使用NIfTI图像对象');
      console.log('🔍 图像属性检查:');
      console.log('  - width:', image.width);
      console.log('  - height:', image.height);
      console.log('  - rows:', image.rows);
      console.log('  - columns:', image.columns);
      console.log('  - getPixelData:', typeof image.getPixelData);
      console.log('  - minPixelValue:', image.minPixelValue);
      console.log('  - maxPixelValue:', image.maxPixelValue);
      
      // 验证所有必要属性
      const requiredProps = ['width', 'height', 'rows', 'columns', 'getPixelData'];
      const missingProps = requiredProps.filter(prop => image[prop] === undefined);
      if (missingProps.length > 0) {
        throw new Error(`NIfTI图像缺少必要属性: ${missingProps.join(', ')}`);
      }
    } else {
      // 使用Cornerstone加载DICOM图像
      image = await cornerstone.loadImage(imageId);
      console.log('✅ 图像已加载, 大小:', image.rows, 'x', image.columns);
    }
    
    console.log('🖼️ 准备显示图像，最终图像对象:');
    console.log('  - imageId:', image.imageId);
    console.log('  - width:', image.width);
    console.log('  - height:', image.height);
    
    // 显示图像
    await cornerstone.displayImage(element, image);
    console.log('✅ 图像已显示');
    
    // 更新状态
    imageLoaded.value = true;
    
    // 提取信息
    let patientInfo, imageInfo;
    
    if (isNifti && image.niftiHeader) {
      // 从NIfTI头信息提取信息
      const { extractNiftiPatientInfo, extractNiftiImageInfo } = await import('../utils/niftiLoader.js');
      patientInfo = extractNiftiPatientInfo(image.niftiHeader);
      imageInfo = extractNiftiImageInfo(image.niftiHeader, image);
    } else {
      // 从DICOM信息提取信息
      patientInfo = extractPatientInfo(image);
      imageInfo = extractImageInfo(image);
    }
    
    // 保存信息到响应式变量
    window.currentPatientInfo = patientInfo;
    window.currentImageInfo = imageInfo;
    
    // 分发事件
    window.dispatchEvent(new CustomEvent('dicom-loaded', {
      detail: {
        patientInfo: patientInfo,
        imageInfo: imageInfo,
        isNifti: isNifti
      }
    }));
    
    console.log('✅ 图像加载过程完成');
    return true;
  } catch (err) {
    console.error('❌ 加载图像失败:', err);
    error.value = `加载图像失败: ${err.message || err}`;
    return false;
  }
}

// 注册工具
function registerTools() {
  try {
    console.log('开始注册工具...');
    
    // 添加所需的工具
    cornerstoneTools.addTool(cornerstoneTools.PanTool);
    cornerstoneTools.addTool(cornerstoneTools.ZoomTool);
    cornerstoneTools.addTool(cornerstoneTools.WwwcTool);
    cornerstoneTools.addTool(cornerstoneTools.LengthTool);
    cornerstoneTools.addTool(cornerstoneTools.AngleTool);//角度测量，暂时没用
    cornerstoneTools.addTool(cornerstoneTools.RectangleRoiTool);//ROI矩形选择工具，暂时没用
    
    // 设置默认工具状态
    const element = dicomContainer.value;
    if (element) {
      cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 });
      cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 2 });
      cornerstoneTools.setToolEnabled('Wwwc', { mouseButtonMask: 4 });
    }
    
    console.log('✅ 工具注册完成');
  } catch (err) {
    console.error('❌ 注册工具失败:', err);
  }
}

// 清理工具状态
function cleanupTools() {
  const element = dicomContainer.value;
  if (!element) return;
  
  try {
    // 停用所有工具
    ['Pan', 'Zoom', 'Wwwc', 'Length'].forEach(tool => {
      try {
        cornerstoneTools.setToolPassive(tool);
      } catch (e) {
        // 忽略错误
      }
    });
  } catch (err) {
    console.warn('清理工具状态失败:', err);
  }
}

// 设置活动工具（内部调用）
function setTool(toolName) {
  setActiveTool(toolName);
}

// 设置活动工具
function setActiveTool(toolName) {
  const element = dicomContainer.value;
  if (!element || !imageLoaded.value) {
    console.warn('无法激活工具，未加载图像或元素不可用');
    return;
  }
  
  try {
    console.log(`开始激活工具: ${toolName}`);
    
    // 首先禁用所有工具
    cornerstoneTools.setToolDisabled('Pan');
    cornerstoneTools.setToolDisabled('Zoom');
    cornerstoneTools.setToolDisabled('Length');
    cornerstoneTools.setToolDisabled('Wwwc');
    
    // 根据工具名称激活相应的工具
    switch(toolName) {
      case 'Pan':
        cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 });
        break;
      case 'Zoom':
        cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 1 });
        break;
      case 'Length':
        cornerstoneTools.setToolActive('Length', { mouseButtonMask: 1 });
        break;
      case 'Wwwc':
        cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 1 });
        break;
      default:
        console.warn(`未知工具: ${toolName}`);
        return;
    }
    
    activeToolName = toolName;
    console.log(`工具已成功激活: ${toolName}`);
  } catch (err) {
    console.error(`激活工具失败 ${toolName}:`, err);
  }
}

// 重置视图
function resetView() {
  const element = dicomContainer.value;
  if (!element || !imageLoaded.value) {
    console.warn('无法重置视图，未加载图像或元素不可用');
    return;
  }
  
  try {
    cornerstone.reset(element);
    console.log('视图已重置');
  } catch (err) {
    console.error('重置视图失败:', err);
  }
}

// 调整图像设置
function adjustImageSettings(settings) {
  const element = dicomContainer.value;
  if (!element || !imageLoaded.value) {
    console.warn('无法调整图像设置，未加载图像或元素不可用');
    return;
  }
  
  try {
    const viewport = cornerstone.getViewport(element);
    
    // 获取图像对象
    const enabledElement = cornerstone.getEnabledElement(element);
    const image = enabledElement.image;
    
    // 使用窗宽窗位调整亮度和对比度
    if (typeof settings.brightness === 'number') {
      // 亮度对应窗位中心
      const defaultCenter = image.windowCenter || 127;
      viewport.voi.windowCenter = defaultCenter * settings.brightness;
    }
    
    if (typeof settings.contrast === 'number') {
      // 对比度对应窗宽
      const defaultWidth = image.windowWidth || 255;
      viewport.voi.windowWidth = defaultWidth * settings.contrast;
    }
    
    // 应用新设置
    cornerstone.setViewport(element, viewport);
    console.log(`图像设置已调整: 亮度=${settings.brightness}, 对比度=${settings.contrast}`);
  } catch (err) {
    console.error('调整图像设置失败:', err);
  }
}

// 从DICOM提取患者信息
function extractPatientInfo(image) {
  if (!image || !image.data || !image.data.string) {
    return { name: '未知', age: '未知', gender: '未知' };
  }
  
  try {
    return {
      name: image.data.string('x00100010') || '未知',
      age: image.data.string('x00100030') || '未知',
      gender: image.data.string('x00100040') || '未知'
    };
  } catch (e) {
    console.error('提取患者信息失败:', e);
    return { name: '未知', age: '未知', gender: '未知' };
  }
}

// 从DICOM提取图像信息
function extractImageInfo(image) {
  if (!image || !image.data || !image.data.string) {
    return { modality: '未知', seriesDescription: '未知', studyDate: '未知' };
  }
  
  try {
    return {
      modality: image.data.string('x00080060') || '未知',
      seriesDescription: image.data.string('x0008103E') || '未知',
      studyDate: image.data.string('x00080020') || '未知',
      rows: image.rows,
      columns: image.columns
    };
  } catch (e) {
    console.error('提取图像信息失败:', e);
    return { modality: '未知', seriesDescription: '未知', studyDate: '未知' };
  }
}

// 清理资源
function cleanupDicomViewer() {
  const element = dicomContainer.value;
  if (element) {
    try {
      cleanupTools();
      
      try {
        cornerstone.disable(element);
      } catch (e) {
        // 忽略错误
      }
      console.log('DICOM查看器资源已清理');
    } catch (err) {
      console.error('清理DICOM查看器资源失败:', err);
    }
  }
}

// ==================== AI分析相关方法 ====================

// 检查AI服务健康状态
async function checkAiHealth() {
  try {
    console.log('检查AI服务健康状态...');
    const response = await aiApi.checkHealth();
    
    if (response.data && response.data.status === 'healthy') {
      aiServiceStatus.value = 'healthy';
      console.log('AI服务健康状态: 正常');
      return true;
    } else {
      aiServiceStatus.value = 'unhealthy';
      console.log('AI服务健康状态: 异常');
      showNotification('AI服务状态异常', 'warning');
      return false;
    }
  } catch (err) {
    console.error('AI服务连接失败:', err);
    aiServiceStatus.value = 'disconnected';
    showNotification('AI服务连接失败', 'error');
    return false;
  }
}

// 开始AI分析
async function startAiAnalysis() {
  // 验证是否有图像加载
  if (!imageLoaded.value) {
    showNotification('请先上传DICOM图像', 'warning');
    return;
  }

  // 验证是否有文件引用
  const currentFile = getCurrentFile();
  if (!currentFile) {
    showNotification('无法获取当前图像文件，请重新上传', 'error');
    return;
  }

  // 验证必要参数
  if (!selectedModality.value) {
    showNotification('请选择影像模态', 'warning');
    return;
  }

  // 检查AI服务状态
  showNotification('正在检查AI服务状态...', 'info');
  const aiHealthy = await checkAiHealth();
  if (!aiHealthy) {
    showNotification('AI服务不可用，请检查服务状态', 'error');
    return;
  }

  // 重置状态
  error.value = '';
  showAiModal.value = false;
  aiAnalyzing.value = true;
  analysisProgress.value = '初始化AI分析...';
  analysisProgressPercent.value = 5;

  showNotification('开始AI肿瘤分析...', 'info', 5000);

  try {
    // 更新进度
    analysisProgress.value = '上传图像到AI服务...';
    analysisProgressPercent.value = 15;
    
    // 发送AI分析请求
    console.log('发送AI分析请求:', {
      fileName: currentFile.name,
      modality: selectedModality.value,
      patientId: analysisPatientId.value
    });
    
    const response = await aiApi.predictTumor(
      currentFile,
      selectedModality.value,
      analysisPatientId.value || undefined
    );

    console.log('AI分析响应:', response.data);    // 更新进度
    analysisProgressPercent.value = 30;
    analysisProgress.value = '正在进行肿瘤检测...';

    // 检查响应是否成功
    if (response.data && response.data.success) {
      if (response.data.session_id) {
        currentAnalysisSession.value = response.data.session_id;
      }
      
      // 模拟分析进度
      await simulateAnalysisProgress();
      
      // 获取分析结果
      if (response.data.result) {
        analysisResult.value = response.data.result;
        analysisProgress.value = '分析完成！';
        analysisProgressPercent.value = 100;
        
        // 显示成功消息
        const tumorCount = response.data.result?.detected_tumors?.length || 0;
        const riskLevel = response.data.result?.risk_assessment?.risk_level || 'unknown';
        
        showNotification(
          `AI分析完成！检测到${tumorCount}个可疑病变，风险等级：${getRiskLevelText(riskLevel)}`, 
          'success', 
          8000
        );
        
        setTimeout(() => {
          aiAnalyzing.value = false;
        }, 1500);
      } else {
        throw new Error('AI分析未返回结果');
      }
      
    } else {
      // 处理分析失败的情况
      const errorMessage = response.data?.error || 'AI分析服务响应异常';
      throw new Error(errorMessage);
    }
    
  } catch (err) {
    console.error('AI分析失败:', err);
    const errorMessage = err.response?.data?.detail || err.message || 'AI分析失败';
    error.value = `AI分析失败: ${errorMessage}`;
    showNotification(`AI分析失败: ${errorMessage}`, 'error', 8000);
    aiAnalyzing.value = false;
    analysisProgressPercent.value = 0;
    analysisProgress.value = '';
  }
}

// 模拟分析进度
async function simulateAnalysisProgress() {
  const steps = [
    { progress: 40, message: '预处理图像数据...', delay: 1500 },
    { progress: 55, message: '初始化神经网络模型...', delay: 2000 },
    { progress: 70, message: '运行肿瘤检测算法...', delay: 2500 },
    { progress: 85, message: '生成分割掩码...', delay: 1500 },
    { progress: 95, message: '计算风险评估...', delay: 1000 }
  ];

  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, step.delay));
    analysisProgressPercent.value = step.progress;
    analysisProgress.value = step.message;
  }
}

// 获取当前文件
function getCurrentFile() {
  // 优先使用当前上传的文件
  if (currentUploadedFile.value) {
    return currentUploadedFile.value;
  }
  
  // 备用方案：从全局变量获取
  if (window.lastUploadedFile) {
    return window.lastUploadedFile;
  }
  
  console.warn('无法获取当前文件引用');
  return null;
}

// 下载分析报告
async function downloadAnalysisReport() {
  if (!currentAnalysisSession.value) {
    showNotification('没有可用的分析会话ID', 'warning');
    return;
  }

  try {
    showNotification('正在生成分析报告...', 'info');
    console.log('下载分析报告:', currentAnalysisSession.value);
    const response = await aiApi.downloadResult(currentAnalysisSession.value, 'report');
    
    if (response.data) {
      // 从blob响应中提取文本内容
      let content;
      let filename = `analysis_report_${currentAnalysisSession.value}.txt`;
      
      if (response.data instanceof Blob) {
        // 如果是blob，转换为文本
        content = await response.data.text();
      } else if (typeof response.data === 'string') {
        content = response.data;
      } else {
        // 如果是对象，可能是错误格式，转换为JSON
        content = JSON.stringify(response.data, null, 2);
        filename = `analysis_report_${currentAnalysisSession.value}.json`;
      }
      
      // 创建下载
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('报告下载成功:', filename);
      showNotification(`分析报告下载成功: ${filename}`, 'success');
    } else {
      throw new Error('服务器未返回报告内容');
    }
    
  } catch (err) {
    console.error('下载报告失败:', err);
    const errorMessage = err.response?.data?.detail || err.message || '下载失败';
    error.value = `下载报告失败: ${errorMessage}`;
    showNotification(`下载报告失败: ${errorMessage}`, 'error');
  }
}

async function downloadSegmentation() {
  if (!currentAnalysisSession.value) {
    showNotification('没有可用的分析会话ID', 'warning');
    return;
  }

  try {
    showNotification('正在生成分割图像...', 'info');
    console.log('下载分割图像:', currentAnalysisSession.value);
    const response = await aiApi.downloadResult(currentAnalysisSession.value, 'segmentation');
    
    if (response.data) {
      let filename = `segmentation_${currentAnalysisSession.value}.nii.gz`;
      
      if (response.data.filename) {
        filename = response.data.filename;
      }
      
      // 处理二进制数据或文件信息
      if (response.data instanceof Blob) {
        // 直接是二进制数据
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showNotification(`分割图像下载成功: ${filename}`, 'success');
      } else {
        // 是文件信息，创建提示
        const message = response.data.message || '分割图像已生成';
        console.log('分割图像信息:', message);
        
        showNotification(`${message} (文件: ${filename})`, 'success');
      }
      
      console.log('分割图像下载成功:', filename);
    } else {
      throw new Error('服务器未返回分割数据');
    }
    
  } catch (err) {
    console.error('下载分割图像失败:', err);
    const errorMessage = err.response?.data?.detail || err.message || '下载失败';
    error.value = `下载分割图像失败: ${errorMessage}`;
    showNotification(`下载分割图像失败: ${errorMessage}`, 'error');
  }
}

// 下载PDF报告
async function downloadPdfReport() {
  if (!currentAnalysisSession.value) {
    showNotification('没有可用的分析会话ID', 'warning');
    return;
  }

  try {
    showNotification('正在生成PDF报告...', 'info');
    console.log('下载PDF报告:', currentAnalysisSession.value);
    const response = await aiApi.downloadResult(currentAnalysisSession.value, 'pdf');
    
    if (response.data instanceof Blob) {
      // 创建下载链接
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `medical_report_${currentAnalysisSession.value}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('PDF报告下载成功');
      showNotification('PDF报告下载成功', 'success');
    } else {
      throw new Error('服务器未返回PDF内容');
    }
    
  } catch (err) {
    console.error('下载PDF报告失败:', err);
    const errorMessage = err.response?.data?.detail || err.message || '下载失败';
    error.value = `下载PDF报告失败: ${errorMessage}`;
    showNotification(`下载PDF报告失败: ${errorMessage}`, 'error');
  }
}

// 格式化位置信息
function formatLocation(location) {
  if (!location) return '未知';
  return `(${location.x?.toFixed(1) || 0}, ${location.y?.toFixed(1) || 0}, ${location.z?.toFixed(1) || 0})`;
}

// 格式化解剖位置
function formatAnatomicalLocation(location) {
  if (!location) return '未知区域';
  
  const region = location.anatomical_region || '未知区域';
  const coords = formatLocation(location);
  
  return `${region}\n坐标: ${coords}`;
}

// 格式化肿瘤大小
function formatTumorSize(size) {
  if (!size) return '未知';
  
  const width = size.width?.toFixed(1) || '0.0';
  const height = size.height?.toFixed(1) || '0.0';
  const depth = size.depth?.toFixed(1) || '0.0';
  
  return `${width}×${height}×${depth}`;
}

// 格式化形态特征
function formatMorphology(morphology) {
  if (!morphology) return '未知';
  
  const features = [];
  if (morphology.边界) features.push(`边界: ${morphology.边界}`);
  if (morphology.形状) features.push(`形状: ${morphology.形状}`);
  if (morphology.密度) features.push(`密度: ${morphology.密度}`);
  if (morphology.强化方式) features.push(`强化: ${morphology.强化方式}`);
  
  return features.join('\n') || '未知';
}

// 获取影像模态全名
function getModalityFullName(modality) {
  const modalityNames = {
    'CT': 'CT (计算机断层扫描)',
    'MRI': 'MRI (磁共振成像)',
    'PET': 'PET (正电子发射断层扫描)',
    'US': 'US (超声影像)'
  };
  return modalityNames[modality] || `${modality} (未知模态)`;
}

// 格式化分析时间
function formatAnalysisTime(timestamp) {
  if (!timestamp) return '未知';
  
  const date = new Date(timestamp);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 获取当前日期时间
function getCurrentDateTime() {
  const now = new Date();
  return now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 获取良恶性预测的CSS类
function getMalignancyClass(malignancy) {
  if (!malignancy) return '';
  return malignancy.is_malignant ? 'malignant' : 'benign';
}

// 获取良恶性指示器
function getMalignancyIndicator(malignancy) {
  if (!malignancy) return '🔵';
  return malignancy.is_malignant ? '🔴' : '🟢';
}

// 获取SUVmax状态
function getSuvmaxStatus(suvmax) {
  if (!suvmax) return '未知';
  return suvmax > 2.5 ? '异常 ⚠️' : '正常';
}

// 获取SUVmax CSS类
function getSuvmaxClass(suvmax) {
  if (!suvmax) return '';
  return suvmax > 2.5 ? 'abnormal' : 'normal';
}

// 获取Hounsfield值状态
function getHounsfieldStatus(hu) {
  if (hu === null || hu === undefined) return '未知';
  if (hu >= -10 && hu <= 40) return '软组织密度';
  return '异常密度';
}

// 获取ADC值状态
function getAdcStatus(adc) {
  if (!adc) return '未知';
  return adc < 1.0 ? '限制性扩散 ⚠️' : '正常扩散';
}

// 获取ADC CSS类
function getAdcClass(adc) {
  if (!adc) return '';
  return adc < 1.0 ? 'restricted' : 'normal';
}

// 获取风险等级图标
function getRiskIcon(level) {
  const icons = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🔴'
  };
  return icons[level] || '⚪';
}

// 获取临床提示
function getClinicalTips() {
  if (!analysisResult.value || !analysisResult.value.detected_tumors) {
    return '✓ 各项影像学征象正常，无异常发现';
  }

  const tumors = analysisResult.value.detected_tumors;
  if (tumors.length === 0) {
    return '✓ 各项影像学征象正常，无异常发现';
  }

  const highRiskIndicators = [];
  
  tumors.forEach(tumor => {
    const clinical = tumor.clinical_parameters || {};
    
    if (clinical.suvmax && clinical.suvmax > 2.5) {
      highRiskIndicators.push(`SUVmax ${clinical.suvmax.toFixed(1)} 提示高代谢活性`);
    }
    
    if (clinical.adc_value && clinical.adc_value < 1.0) {
      highRiskIndicators.push(`ADC值 ${clinical.adc_value.toFixed(3)} 提示扩散受限`);
    }
    
    if (tumor.malignancy && tumor.malignancy.is_malignant) {
      highRiskIndicators.push('AI预测为恶性病变');
    }
  });

  if (highRiskIndicators.length > 0) {
    return highRiskIndicators.map(indicator => `⚠️ ${indicator}`).join('\n');
  }
  return '✓ 各项参数指标在正常范围内';
}

// 获取诊断建议
function getDiagnosticRecommendations() {
  if (!analysisResult.value || !analysisResult.value.detected_tumors) {
    return '✓ 正常影像学表现:\n• 建议定期健康体检（每年一次）\n• 维持健康生活方式\n• 如出现相关症状，及时就医检查';
  }

  const tumors = analysisResult.value.detected_tumors;
  if (tumors.length === 0) {
    return '✓ 正常影像学表现:\n• 建议定期健康体检（每年一次）\n• 维持健康生活方式\n• 如出现相关症状，及时就医检查';
  }

  // 检查是否有恶性肿瘤
  const hasMalignant = tumors.some(tumor => tumor.malignancy && tumor.malignancy.is_malignant);
  
  if (hasMalignant) {
    return '🔴 恶性病变处理建议:\n• 建议尽快进行活检以确认诊断\n• 建议与肿瘤科医生会诊，制定治疗方案\n• 考虑进行全身影像学检查评估分期\n• 密切监测病变进展';
  } else {
    // 良性病变建议
    const riskLevel = analysisResult.value.risk_assessment?.risk_level;
    if (riskLevel === 'medium' || riskLevel === 'high') {
      return '🟡 中等风险良性病变建议:\n• 建议3-6个月内复查影像学检查\n• 定期监测病变大小和形态变化\n• 如出现相关症状，及时就医\n• 可考虑进一步影像学检查';
    } else {
      return '🟢 低风险良性病变建议:\n• 建议6-12个月后复查\n• 保持健康生活方式\n• 注意观察相关症状\n• 定期健康体检';
    }
  }
}

// 获取风险等级文本
function getRiskLevelText(level) {
  const riskTexts = {
    'low': '低风险',
    'medium': '中等风险',
    'high': '高风险'
  };
  return riskTexts[level] || '未知风险';
}

// AI状态监控
function getAiStatusText() {
  const statusTexts = {
    'healthy': 'AI服务正常',
    'unhealthy': 'AI服务异常',
    'disconnected': 'AI服务断开',
    'unknown': 'AI状态未知'
  };
  return statusTexts[aiServiceStatus.value] || 'AI状态未知';
}

// 添加通知函数，（这里做成动画效果）
function showNotification(message, type = 'info', duration = 3000) {
  const id = Date.now();
  const notification = {
    id,
    message,
    type,
    show: false
  };
  
  notifications.value.push(notification);
  
  // 延迟显示以触发动画
  nextTick(() => {
    notification.show = true;
  });
  
  // 自动移除
  setTimeout(() => {
    removeNotification(id);
  }, duration);
}

function removeNotification(id) {
  const index = notifications.value.findIndex(n => n.id === id);
  if (index > -1) {
    notifications.value.splice(index, 1);
  }
}

// 获取通知图标
function getNotificationIcon(type) {
  const icons = {
    'success': 'fas fa-check-circle',
    'error': 'fas fa-exclamation-triangle',
    'warning': 'fas fa-exclamation-circle',
    'info': 'fas fa-info-circle'
  };
  return icons[type] || 'fas fa-info-circle';
}

// ==================== 文件上传处理方法 ====================

// 处理文件上传事件
function handleFileUpload(event) {
  const files = event.target.files;
  if (files && files.length > 0) {
    const file = files[0];
    console.log('通过文件选择器上传:', file.name, file.size);
    
    // 保存当前上传的文件引用
    currentUploadedFile.value = file;
    
    // 处理文件
    handleDicomFile(file);
    
    // 清空input的值，这样下次选择同一个文件也会触发change事件
    event.target.value = '';
  }
}

// 处理文件拖拽事件
function handleFileDrop(event) {
  isDragOver.value = false;
  
  const files = event.dataTransfer.files;
  if (files && files.length > 0) {
    const file = files[0];
    console.log('通过拖拽上传:', file.name, file.size);
    
    // 验证文件类型
    const validExtensions = ['.dcm', '.nii', '.nii.gz'];
    const fileName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValid) {
      showNotification('请上传支持的文件格式: .dcm, .nii, .nii.gz', 'error');
      return;
    }
    
    // 保存当前上传的文件引用
    currentUploadedFile.value = file;
    
    // 处理文件
    handleDicomFile(file);
  }
}

// ==================== 诊断历史管理 ====================

// 从本地存储加载诊断历史
function loadDiagnosisHistory() {
  try {
    const stored = localStorage.getItem('diagnosisHistory');
    if (stored) {
      diagnosisHistory.value = JSON.parse(stored);
    }
  } catch (error) {
    console.error('加载诊断历史失败:', error);
    diagnosisHistory.value = [];
  }
}

// 保存诊断历史到本地存储
function saveDiagnosisHistory() {
  try {
    localStorage.setItem('diagnosisHistory', JSON.stringify(diagnosisHistory.value));
  } catch (error) {
    console.error('保存诊断历史失败:', error);
    showNotification('保存诊断历史失败', 'error');
  }
}

// 保存当前分析结果到历史记录
function saveToHistory() {
  if (!analysisResult.value) {
    showNotification('没有可保存的分析结果', 'warning');
    return;
  }

  try {
    const record = {
      id: `diagnosis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      savedAt: new Date().toISOString(),
      analysisTime: analysisResult.value.analysis_timestamp,
      filename: currentUploadedFile.value?.name || `诊断_${new Date().toLocaleDateString()}`,
      patientId: analysisResult.value.patient_id,
      modality: analysisResult.value.modality,
      sessionId: analysisResult.value.session_id,
      detectedTumors: analysisResult.value.detected_tumors?.length || 0,
      riskLevel: analysisResult.value.risk_assessment?.risk_level || 'unknown',
      riskScore: analysisResult.value.risk_assessment?.risk_score || 0,
      processingTime: analysisResult.value.processing_time,
      fullResult: JSON.parse(JSON.stringify(analysisResult.value)) // 深拷贝完整结果
    };

    // 添加到历史记录开头
    diagnosisHistory.value.unshift(record);
    
    // 限制历史记录数量，保留最新的50条
    if (diagnosisHistory.value.length > 50) {
      diagnosisHistory.value = diagnosisHistory.value.slice(0, 50);
    }
    
    saveDiagnosisHistory();
    showNotification('诊断结果已保存到历史记录', 'success');
  } catch (error) {
    console.error('保存到历史失败:', error);
    showNotification('保存到历史失败', 'error');
  }
}

// 查看历史记录详情
function viewHistoryRecord(record) {
  try {
    analysisResult.value = record.fullResult;
    showHistoryModal.value = false;
    showNotification('历史记录已加载', 'success');
  } catch (error) {
    console.error('加载历史记录失败:', error);
    showNotification('加载历史记录失败', 'error');
  }
}

// 下载历史记录报告
async function downloadHistoryReport(record) {
  try {
    showNotification('正在下载历史报告...', 'info');
    
    // 如果有会话ID，尝试下载原始报告
    if (record.sessionId) {
      try {
        const response = await aiApi.downloadResult(record.sessionId, 'pdf');
        if (response.data instanceof Blob) {
          const url = window.URL.createObjectURL(response.data);
          const link = document.createElement('a');
          link.href = url;
          link.download = `${record.filename}_报告.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          showNotification('历史报告下载成功', 'success');
          return;
        }
      } catch (sessionError) {
        console.warn('无法从会话下载，将生成本地报告:', sessionError);
      }
    }
    
    // 生成本地文本报告
    const reportContent = generateLocalReport(record);
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${record.filename}_报告.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    showNotification('历史报告下载成功', 'success');
    
  } catch (error) {
    console.error('下载历史报告失败:', error);
    showNotification('下载历史报告失败', 'error');
  }
}

// 生成本地报告内容
function generateLocalReport(record) {
  const result = record.fullResult;
  const saveTime = formatDateTime(record.savedAt);
  const analysisTime = formatDateTime(record.analysisTime);
  
  let report = `
================================================================================
                            医学影像AI智能分析报告（历史记录）
================================================================================

【基本信息】
• 患者ID: ${record.patientId || '未提供'}
• 文件名: ${record.filename}
• 影像类型: ${getModalityFullName(record.modality)}
• 分析时间: ${analysisTime}
• 保存时间: ${saveTime}
• 会话ID: ${record.sessionId}

【分析结果】
`;

  if (result.detected_tumors && result.detected_tumors.length > 0) {
    report += `✓ 检测到 ${result.detected_tumors.length} 个可疑病变区域\n\n`;
    
    result.detected_tumors.forEach((tumor, index) => {
      report += `病变 ${index + 1}:\n`;
      report += `• 位置: ${tumor.location?.anatomical_region || '未知'}\n`;
      report += `• 大小: ${tumor.size?.width?.toFixed(1) || '?'}×${tumor.size?.height?.toFixed(1) || '?'}×${tumor.size?.depth?.toFixed(1) || '?'} mm³\n`;
      report += `• 体积: ${tumor.volume?.toFixed(2) || '?'} cm³\n`;
      report += `• 良恶性: ${tumor.malignancy?.classification || '未知'}\n`;
      report += `• 置信度: ${((tumor.confidence || 0) * 100).toFixed(1)}%\n\n`;
    });
  } else {
    report += '✓ 未检测到明显病变\n\n';
  }

  report += `【风险评估】\n`;
  report += `• 风险等级: ${getRiskLevelText(record.riskLevel)}\n`;
  report += `• 风险评分: ${record.riskScore}/100\n\n`;

  report += `【技术信息】\n`;
  report += `• 处理时间: ${record.processingTime?.toFixed(2) || '未知'}秒\n`;
  report += `• 记录保存时间: ${saveTime}\n`;
  report += `• 数据来源: 历史记录\n\n`;

  report += `【重要说明】\n`;
  report += `⚠️ 本报告为历史记录，仅供参考\n`;
  report += `⚠️ 如需最新分析结果，请重新进行AI分析\n`;

  return report;
}

// 删除历史记录
function removeHistoryRecord(recordId) {
  if (confirm('确定要删除这条诊断记录吗？')) {
    diagnosisHistory.value = diagnosisHistory.value.filter(record => record.id !== recordId);
    saveDiagnosisHistory();
    showNotification('诊断记录已删除', 'success');
  }
}

// 清空所有历史记录
function clearHistory() {
  if (confirm('确定要清空所有诊断历史记录吗？此操作不可恢复！')) {
    diagnosisHistory.value = [];
    saveDiagnosisHistory();
    showNotification('诊断历史已清空', 'success');
  }
}

// 导出所有历史记录
function exportAllHistory() {
  try {
    if (diagnosisHistory.value.length === 0) {
      showNotification('没有历史记录可导出', 'warning');
      return;
    }

    const exportData = {
      exportTime: new Date().toISOString(),
      totalRecords: diagnosisHistory.value.length,
      records: diagnosisHistory.value.map(record => ({
        ...record,
        // 不导出完整的fullResult以减小文件大小
        fullResult: undefined
      }))
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json;charset=utf-8' 
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `诊断历史记录_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    showNotification('历史记录导出成功', 'success');
  } catch (error) {
    console.error('导出历史记录失败:', error);
    showNotification('导出历史记录失败', 'error');
  }
}

// 格式化日期时间
function formatDateTime(dateString) {
  if (!dateString) return '未知时间';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (error) {
    return '时间格式错误';
  }
}

// 获取风险等级样式类
function getRiskLevelClass(level) {
  return {
    'risk-low': level === 'low',
    'risk-medium': level === 'medium',
    'risk-high': level === 'high',
    'risk-unknown': level === 'unknown' || !level
  };
}

// ==================== 诊断历史管理结束 ====================

// 暴露组件方法给父组件
defineExpose({
  loadDicom,
  loadNewImage,
  loadSampleDicom,
  setActiveTool,
  resetView,
  adjustImageSettings,
  loadAndViewImage,
  dicomContainer
});
</script>

<style scoped>
/* 基础样式 */
.dicom-viewer {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  min-height: 100vh;
}

/* 通知系统样式 */
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000; /* 提高z-index确保不被遮挡 */
  pointer-events: none;
}

.system-notification {
  background: white;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 250px;
  max-width: 400px;
  pointer-events: auto;
  cursor: pointer;
  transform: translateX(100%);
  transition: all 0.3s ease;
  border-left: 4px solid #007bff;
}

.system-notification.show {
  transform: translateX(0);
}

.system-notification.success {
  border-left-color: #28a745;
  color: #155724;
  background-color: #d4edda;
}

.system-notification.error {
  border-left-color: #dc3545;
  color: #721c24;
  background-color: #f8d7da;
}

.system-notification.warning {
  border-left-color: #ffc107;
  color: #856404;
  background-color: #fff3cd;
}

.system-notification.info {
  border-left-color: #17a2b8;
  color: #0c5460;
  background-color: #d1ecf1;
}

/* AI状态指示器 */
.ai-status-indicator {
  position: fixed;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 999;
}

.ai-status-indicator:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.ai-status-indicator.healthy .status-dot {
  background-color: #28a745;
}

.ai-status-indicator.unhealthy .status-dot {
  background-color: #ffc107;
}

.ai-status-indicator.disconnected .status-dot {
  background-color: #dc3545;
}

.ai-status-indicator.unknown .status-dot {
  background-color: #6c757d;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 文件上传区域 */
.upload-section {
  margin-bottom: 30px;
}

.file-drop-zone {
  border: 2px dashed #ccc;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  background: #fafafa;
}

.file-drop-zone:hover,
.file-drop-zone.drag_over {
  border-color: #007bff;
  background: #f0f8ff;
  transform: translateY(-2px);
}

.upload-icon {
  font-size: 48px;
  color: #007bff;
  margin-bottom: 16px;
}

.file-info {
  color: #666;
  font-size: 14px;
  margin-top: 8px;
}

/* 加载指示器 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tool-group {
  display: flex;
  gap: 8px;
}

.tool-group button {
  padding: 10px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-group button:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.tool-group button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.tool-group button.load-new-btn {
  background: #6c757d;
  color: white;
  border-color: #6c757d;
}

.tool-group button.load-new-btn:hover {
  background: #5a6268;
  border-color: #545b62;
}

.ai-analysis-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.ai-analysis-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(40, 167, 69, 0.4);
}

.ai-analysis-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* DICOM容器 */
.dicom-container {
  width: 100%;
  height: 600px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #000;
  position: relative;
  overflow: hidden;
}

/* 模态框样式 */
.ai-analysis-overlay,
.ai-result-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.ai-analysis-modal,
.ai-result-modal {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.ai-modal-header,
.ai-result-header,
.ai-analysis-header {
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-modal-content,
.ai-result-content,
.ai-analysis-content {
  padding: 24px;
}

.ai-modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.close-button {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #f8f9fa;
  color: #333;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* 按钮样式 */
.enhanced-button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.enhanced-button:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.enhanced-button.success {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.enhanced-button.success:hover:not(:disabled) {
  background: #218838;
}

.enhanced-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 进度条 */
.analysis-progress {
  text-align: center;
  margin-bottom: 24px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 16px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #28a745);
  transition: width 0.3s ease;
  border-radius: 4px;
}

/* 上传进度样式 */
.upload-progress {
  margin-top: 16px;
  text-align: center;
}

.upload-progress .progress-bar {
  margin: 8px 0;
}

.progress-text {
  font-size: 14px;
  font-weight: 500;
  color: #007bff;
  margin-top: 8px;
}

/* 结果卡片 */
.result-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #007bff;
}

.result-card.error {
  border-left-color: #dc3545;
  background: #f8d7da;
}

.result-card.low {
  border-left-color: #28a745;
}

.result-card.medium {
  border-left-color: #ffc107;
}

.result-card.high {
  border-left-color: #dc3545;
}

.result-card h4 {
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 风险级别 */
.risk-level {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-top: 8px;
}

.risk-level.low {
  background: #d4edda;
  color: #155724;
}

.risk-level.medium {
  background: #fff3cd;
  color: #856404;
}

.risk-level.high {
  background: #f8d7da;
  color: #721c24;
}

.risk-label {
  font-weight: 600;
}

.risk-score {
  font-size: 14px;
}

/* 肿瘤列表 */
.tumor-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tumor-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 3px solid #007bff;
}

.tumor-item h5 {
  margin: 0 0 8px 0;
  color: #333;
}

/* 图像占位符样式 */
.image-placeholder {
  min-height: 500px;
  border: 2px dashed #ccc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
  margin-bottom: 20px;
}

.image-placeholder:hover,
.image-placeholder.drag_over {
  border-color: #007bff;
  background: #f0f8ff;
  transform: translateY(-2px);
}

.placeholder-content {
  text-align: center;
  padding: 40px;
}

.placeholder-content .upload-icon {
  font-size: 64px;
  color: #007bff;
  margin-bottom: 20px;
}

.placeholder-content h3 {
  margin-bottom: 12px;
  color: #333;
}

.placeholder-content p {
  margin-bottom: 8px;
  color: #666;
}

.placeholder-content .enhanced-button {
  margin-top: 20px;
}

/* 医学报告样式 */
.medical-report {
  max-width: 900px;
  width: 95%;
}

/* 致辞部分样式 */
.greeting-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.greeting-text {
  margin: 0;
  line-height: 1.6;
  font-size: 14px;
  text-align: justify;
}

.greeting-text strong {
  font-size: 16px;
  display: block;
  margin-bottom: 8px;
  color: #fff;
}

/* 患者信息网格 */
.patient-info-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item .label {
  font-weight: 600;
  color: #495057;
  font-size: 13px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

/* 医学表格样式 */
.analysis-results-section {
  margin-bottom: 25px;
}

.results-table-container {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.medical-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 13px;
}

.medical-table th {
  background: #495057;
  color: white;
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.medical-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: top;
}

.medical-table tbody tr:hover {
  background-color: #f8f9fa;
}

.medical-table tbody tr:nth-child(even) {
  background-color: #fafafa;
}

/* 良恶性预测颜色标识 */
.malignancy-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
}

.tumor-row.malignant .malignancy-indicator {
  color: #dc3545;
}

.tumor-row.benign .malignancy-indicator {
  color: #28a745;
}

.malignancy-indicator::before {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.tumor-row.malignant .malignancy-indicator::before {
  background-color: #dc3545;
}

.tumor-row.benign .malignancy-indicator::before {
  background-color: #28a745;
}

.visualization-cell {
  text-align: center;
}

.viz-description {
  font-size: 11px;
  color: #6c757d;
  line-height: 1.3;
}

/* 临床参数详情 */
.clinical-parameters-section {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.parameters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.parameter-group {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 15px;
  background: #fafafa;
}

.parameter-group h6 {
  margin: 0 0 12px 0;
  color: #495057;
  font-weight: 600;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 8px;
}

.parameter-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.parameter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.param-name {
  font-weight: 500;
  color: #495057;
}

.param-value {
  font-weight: 600;
}

.param-value.normal {
  color: #28a745;
}

.param-value.abnormal {
  color: #dc3545;
}

.param-value.restricted {
  color: #fd7e14;
}

.param-status {
  font-size: 11px;
  margin-left: 5px;
  font-weight: normal;
}

/* 风险评估可视化 */
.risk-assessment-section {
  margin-bottom: 25px;
}

.risk-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.risk-level-display {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid;
}

.risk-level-display.low {
  background: #d4edda;
  border-left-color: #28a745;
  color: #155724;
}

.risk-level-display.medium {
  background: #fff3cd;
  border-left-color: #ffc107;
  color: #856404;
}

.risk-level-display.high {
  background: #f8d7da;
  border-left-color: #dc3545;
  color: #721c24;
}

.risk-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.risk-icon {
  font-size: 20px;
}

.risk-text {
  font-weight: 600;
  font-size: 16px;
}

.risk-score {
  font-weight: 500;
  font-size: 14px;
}

/* 临床提示样式 */
.clinical-tips-section,
.diagnostic-recommendations-section {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.clinical-tips-section {
  border-left: 4px solid #ffc107;
}

.diagnostic-recommendations-section {
  border-left: 4px solid #17a2b8;
}

.tips-content {
  background: #fffbf0;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #ffeaa7;
  margin-top: 15px;
  white-space: pre-line;
  line-height: 1.6;
}

.recommendations-content {
  margin-top: 15px;
}

.recommendation-category {
  background: #e7f3ff;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #b3d7ff;
  margin-bottom: 15px;
  white-space: pre-line;
  line-height: 1.6;
}

.recommendations-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommendations-list li {
  padding: 8px 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.recommendations-list li i {
  color: #28a745;
  margin-top: 2px;
}

/* 备注说明样式 */
.notes-section {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid #6c757d;
}

.notes-content {
  margin-top: 15px;
}

.notes-content p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.technical-info {
  background: #e9ecef;
  padding: 12px;
  border-radius: 6px;
  margin-top: 15px;
}

.technical-info p {
  margin: 4px 0;
  font-size: 13px;
}

/* 模态框尺寸调整 */
.ai-result-modal.medical-report {
  max-width: 950px;
  width: 95%;
  max-height: 90vh;
}

.ai-result-content {
  max-height: calc(90vh - 140px);
  overflow-y: auto;
}

/* 按钮组样式 */
.ai-result-footer {
  padding: 16px 24px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #f8f9fa;
  border-radius: 0 0 16px 16px;
}

/* 响应式设计优化 */
@media (max-width: 768px) {
  .medical-report {
    width: 98%;
    margin: 10px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .parameters-grid {
    grid-template-columns: 1fr;
  }
  
  .medical-table {
    font-size: 12px;
  }
  
  .medical-table th,
  .medical-table td {
    padding: 8px 6px;
  }
    .ai-result-footer {
    flex-direction: column;
  }
}

/* ==================== 诊断历史样式 ==================== */

/* 历史按钮样式 */
.history-btn {
  background: linear-gradient(135deg, #6f42c1, #563d7c);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(111, 66, 193, 0.3);
  margin-left: 8px;
}

.history-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(111, 66, 193, 0.4);
}

/* 诊断历史弹窗样式 */
.diagnosis-history {
  max-width: 1100px;
  width: 95%;
  max-height: 85vh;
}

.history-content {
  max-height: calc(85vh - 140px);
  overflow-y: auto;
  padding: 20px;
}

/* 空历史状态 */
.empty-history {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 64px;
  color: #dee2e6;
  margin-bottom: 20px;
}

.empty-history p {
  margin: 10px 0;
  font-size: 16px;
}

.empty-tip {
  font-size: 14px;
  color: #adb5bd;
}

/* 历史记录控制栏 */
.history-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.history-count {
  font-weight: 500;
  color: #495057;
}

/* 历史记录列表 */
.history-list {
  max-height: 500px;
  overflow-y: auto;
}

.history-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow: hidden;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.history-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 历史记录头部 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px 20px 10px;
  border-bottom: 1px solid #f8f9fa;
}

.history-info h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.history-info h4 i {
  color: #6f42c1;
  margin-right: 8px;
}

.history-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 13px;
  color: #6c757d;
}

.history-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.history-meta i {
  color: #adb5bd;
}

/* 历史记录操作按钮 */
.history-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.history-actions .enhanced-button {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
  min-width: auto;
}

/* 按钮变种样式 */
.enhanced-button.primary-outline {
  background: transparent;
  color: #007bff;
  border-color: #007bff;
}

.enhanced-button.primary-outline:hover {
  background: #007bff;
  color: white;
}

.enhanced-button.success-outline {
  background: transparent;
  color: #28a745;
  border-color: #28a745;
}

.enhanced-button.success-outline:hover {
  background: #28a745;
  color: white;
}

.enhanced-button.danger-outline {
  background: transparent;
  color: #dc3545;
  border-color: #dc3545;
}

.enhanced-button.danger-outline:hover {
  background: #dc3545;
  color: white;
}

/* 历史记录摘要 */
.history-summary {
  padding: 10px 20px 15px;
  background: #fafafa;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.summary-label {
  font-weight: 500;
  color: #495057;
  font-size: 13px;
}

.summary-value {
  font-weight: 600;
  font-size: 13px;
}

/* 风险等级样式 */
.summary-value.risk-low {
  color: #28a745;
}

.summary-value.risk-medium {
  color: #ffc107;
}

.summary-value.risk-high {
  color: #dc3545;
}

.summary-value.risk-unknown {
  color: #6c757d;
}

/* 历史记录底部 */
.history-footer {
  padding: 16px 24px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #f8f9fa;
  border-radius: 0 0 16px 16px;
}

/* AI服务状态样式 */
.ai-service-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-top: 15px;
  border: 1px solid #e9ecef;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.healthy {
  background-color: #28a745;
}

.status-indicator.unhealthy {
  background-color: #ffc107;
}

.status-indicator.disconnected {
  background-color: #dc3545;
}

.status-indicator.unknown {
  background-color: #6c757d;
}

/* AI分析按钮组样式 */
.ai-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 无肿瘤结果样式 */
.no-tumors {
  text-align: center;
  padding: 40px 20px;
}

.normal-result {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 8px;
  padding: 20px;
  color: #155724;
}

.normal-result i {
  font-size: 24px;
  margin-bottom: 10px;
  display: block;
}

.normal-result p {
  margin: 8px 0;
}

.text-success {
  color: #28a745 !important;
}

/* 响应式设计 - 历史记录 */
@media (max-width: 768px) {
  .diagnosis-history {
    width: 98%;
    margin: 10px;
  }
  
  .history-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .history-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .history-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .history-summary {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .history-controls {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .ai-section {
    flex-direction: column;
    width: 100%;
  }
  
  .ai-section .enhanced-button {
    width: 100%;
    margin: 4px 0;
  }
}

@media (max-width: 480px) {
  .history-actions {
    flex-direction: column;
    gap: 6px;
  }
  
  .history-actions .enhanced-button {
    width: 100%;
    font-size: 11px;
    padding: 5px 8px;
  }
  
  .summary-item {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }
}
</style>
