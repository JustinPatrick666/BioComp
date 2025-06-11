<template>
  <div id="app">
    <header class="navbar">
      <div class="nav-left">
        <h1>肿瘤影像自动分析系统</h1>
      </div>
      <nav class="nav-menu">
        <router-link to="/" active-class="active-link" exact>图像分析</router-link>
        <router-link to="/history" active-class="active-link">历史记录</router-link>
        <router-link to="/about" active-class="active-link">关于</router-link>
      </nav>
    </header>
    <main class="main-container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DicomViewer from './components/DicomViewer.vue';
import Sidebar from './components/Sidebar.vue';

const dicomViewerRef = ref(null);
const showInfoPanel = ref(true);
const patientInfo = ref({
  name: '',
  age: '',
  gender: ''
});
const imageInfo = ref({
  modality: '',
  seriesDescription: '',
  studyDate: '',
  rows: '',
  columns: ''
});

// 处理工具栏事件
function handleLoadDicom() {
  console.log("触发加载DICOM事件");
  if (dicomViewerRef.value) {
    dicomViewerRef.value.loadDicom(); 
  }
}

// 添加示例DICOM加载处理函数
function handleLoadSampleDicom() {
  console.log("触发加载示例DICOM事件");
  if (dicomViewerRef.value) {
    dicomViewerRef.value.loadSampleDicom();
  }
}

function handleResetView() {
  console.log("触发重置视图事件");
  if (dicomViewerRef.value) {
    dicomViewerRef.value.resetView();
  }
}

function handleSetTool(toolName) {
  console.log("切换工具:", toolName);
  if (dicomViewerRef.value) {
    // 确保传递的工具名称与cornerstoneTools中的一致
    dicomViewerRef.value.setActiveTool(toolName);
  }
}

function handleAdjustSettings(settings) {
  console.log("调整图像设置:", settings);
  if (dicomViewerRef.value) {
    dicomViewerRef.value.adjustImageSettings(settings);
  }
}

function handleToggleInfo(show) {
  showInfoPanel.value = show;
}

// 在script标签中添加
// 监听DICOM加载事件和检查DicomViewer准备状态
onMounted(() => {
  // 监听DICOM事件
  window.addEventListener('dicom-loaded', (event) => {
    console.log('接收到DICOM加载事件:', event.detail);
    if (event.detail.patientInfo) {
      patientInfo.value = event.detail.patientInfo;
    }
    if (event.detail.imageInfo) {
      imageInfo.value = event.detail.imageInfo;
    }
  });
  
  // 添加定时检查，确保DicomViewer组件已经准备好
  const checkInterval = setInterval(() => {
    if (dicomViewerRef.value && typeof dicomViewerRef.value.setToolActive === 'function') {
      console.log('DicomViewer组件已准备好');
      clearInterval(checkInterval);
      
      // 可以在这里进行任何需要DicomViewer准备好的操作
      // 例如预加载示例图像
      // dicomViewerRef.value.loadLocalDicomExample();
    }
  }, 500); // 每500毫秒检查一次
  
  // 为安全起见，5秒后清除Interval
  setTimeout(() => clearInterval(checkInterval), 5000);
});
</script>

<style>
:root {
  --sidebar-bg: #1a1a2e;
  --main-bg: #0f0f1b;
  --text-light: #e6e6e6;
  --accent-color: #0bc5e6;
  --header-height: 50px;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: var(--main-bg);
  color: var(--text-light);
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  height: var(--header-height);
  background-color: var(--sidebar-bg);
  color: var(--text-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.nav-left h1 {
  font-size: 1.3rem;
  margin: 0;
  color: var(--accent-color);
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-menu a {
  color: var(--text-light);
  text-decoration: none;
  font-size: 1rem;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.nav-menu a.active-link,
.nav-menu a.router-link-exact-active {
  background: var(--accent-color);
  color: #fff;
}

.main-container {
  flex: 1;
  background-color: var(--main-bg);
  overflow: auto;
}

.info-panel {
  background-color: var(--sidebar-bg);
  padding: 15px;
  overflow-y: auto;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.info-panel h3 {
  margin: 10px 0;
  color: var(--accent-color);
  font-size: 1rem;
}

.info-row {
  margin: 8px 0;
  font-size: 0.9rem;
}
</style>
