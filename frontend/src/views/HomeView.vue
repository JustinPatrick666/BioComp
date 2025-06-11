<template>
  <div class="home">
    <div class="layout-container">
      <Sidebar 
        class="sidebar"
        @load-dicom="handleLoadDicom"
        @load-sample="handleLoadSampleDicom"
        @reset-view="handleResetView"
        @set-tool="handleSetTool"
        @adjust-settings="handleAdjustSettings"
        @toggle-info="handleToggleInfo"
      />
      <div class="viewer-container">
        <DicomViewer ref="dicomViewerRef" />
      </div>
      <div v-if="showInfo" class="info-panel">
        <div class="info-section">
          <h3>患者信息</h3>
          <div class="info-row">姓名: {{ patientInfo.name }}</div>
          <div class="info-row">年龄: {{ patientInfo.age }}</div>
          <div class="info-row">性别: {{ patientInfo.gender }}</div>
        </div>
        <div class="info-section">
          <h3>图像信息</h3>
          <div class="info-row">模态: {{ imageInfo.modality }}</div>
          <div class="info-row">序列: {{ imageInfo.seriesDescription }}</div>
          <div class="info-row">日期: {{ imageInfo.studyDate }}</div>
          <div class="info-row">尺寸: {{ imageInfo.rows }}x{{ imageInfo.columns }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DicomViewer from '@/components/DicomViewer.vue';
import Sidebar from '@/components/Sidebar.vue';
import { useRoute } from 'vue-router';
import { useDicomHistoryStore } from '@/stores/dicomHistory';

const route = useRoute();
const dicomViewerRef = ref(null);
const showInfo = ref(true);
const historyStore = useDicomHistoryStore();

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

// DICOM 操作处理函数
function handleLoadDicom() {
  dicomViewerRef.value?.loadDicom();
}

function handleLoadSampleDicom() {
  dicomViewerRef.value?.loadSampleDicom();
}

function handleResetView() {
  dicomViewerRef.value?.resetView();
}

function handleSetTool(toolName) {
  dicomViewerRef.value?.setActiveTool(toolName);
}

function handleAdjustSettings(settings) {
  dicomViewerRef.value?.adjustImageSettings(settings);
}

function handleToggleInfo(show) {
  showInfo.value = show;
}

onMounted(async () => {
  // 监听DICOM事件
  window.addEventListener('dicom-loaded', ((event) => {
    const { patientInfo: newPatientInfo, imageInfo: newImageInfo } = event.detail;
    if (newPatientInfo) {
      patientInfo.value = newPatientInfo;
    }
    if (newImageInfo) {
      imageInfo.value = newImageInfo;
    }
  }));

  // 检查是否需要从历史记录加载图像
  const imageId = route.query.imageId;
  if (imageId && dicomViewerRef.value) {
    console.log('从历史记录加载图像:', imageId);
    // 使用已有的imageId加载图像
    await dicomViewerRef.value.loadAndViewImage(imageId, dicomViewerRef.value.dicomContainer);
  }
});
</script>

<style scoped>
.home {
  width: 100%;
  height: 100%;
  background-color: var(--main-bg, #0f0f1b);
}

.layout-container {
  display: flex;
  height: calc(100vh - var(--header-height, 50px));
  overflow: hidden;
}

.sidebar {
  width: 260px;
  flex-shrink: 0;
}

.viewer-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  background-color: black;
}

.info-panel {
  width: 250px;
  flex-shrink: 0;
  background-color: var(--sidebar-bg, #1a1a2e);
  padding: 1rem;
  overflow-y: auto;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.info-section {
  margin-bottom: 1.5rem;
}

.info-section h3 {
  color: var(--accent-color, #0bc5e6);
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.info-row {
  font-size: 0.9rem;
  color: var(--text-light, #e6e6e6);
  margin: 0.5rem 0;
}
</style>
