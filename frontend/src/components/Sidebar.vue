<template>
  <div class="sidebar">
    <div class="sidebar-section">
      <h4>DICOM操作</h4>
      <button @click="emitEvent('load-dicom')" class="sidebar-button">
        <i class="fas fa-upload"></i> 加载DICOM
      </button>
      <button @click="emitEvent('load-sample')" class="sidebar-button">
        <i class="fas fa-image"></i> 示例DICOM
      </button>
      <button @click="emitEvent('reset-view')" class="sidebar-button">
        <i class="fas fa-sync-alt"></i> 重置视图
      </button>
    </div>
    
    <div class="sidebar-section">
      <h4>工具选择</h4>
      <button 
        @click="setActiveTool('Pan')" 
        :class="['sidebar-button', { active: activeTool === 'Pan' }]">
        <i class="fas fa-arrows-alt"></i> 平移工具
      </button>
      <button 
        @click="setActiveTool('Zoom')" 
        :class="['sidebar-button', { active: activeTool === 'Zoom' }]">
        <i class="fas fa-search-plus"></i> 缩放工具
      </button>
      <button 
        @click="setActiveTool('Length')" 
        :class="['sidebar-button', { active: activeTool === 'Length' }]">
        <i class="fas fa-ruler"></i> 测量工具
      </button>
      <button 
        @click="setActiveTool('Wwwc')" 
        :class="['sidebar-button', { active: activeTool === 'Wwwc' }]">
        <i class="fas fa-adjust"></i> 窗宽窗位
      </button>
    </div>
    
    <div class="sidebar-section">
      <h4>显示设置</h4>
      <div class="slider-container">
        <label for="brightness" :data-value="brightness">亮度:</label>
        <input 
          type="range" 
          id="brightness" 
          min="0.1" 
          max="2" 
          step="0.1" 
          v-model="brightness"
          @input="adjustImageSettings"
        >
      </div>
      <div class="slider-container">
        <label for="contrast" :data-value="contrast">对比度:</label>
        <input 
          type="range" 
          id="contrast" 
          min="0.1" 
          max="2" 
          step="0.1" 
          v-model="contrast"
          @input="adjustImageSettings"
        >
      </div>
      <button @click="toggleInfoPanel" class="sidebar-button">
        <i class="fas fa-info-circle"></i> {{ showInfo ? '隐藏信息' : '显示信息' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue';

// 定义事件
const emit = defineEmits([
  'load-dicom', 
  'load-sample',
  'reset-view', 
  'set-tool', 
  'adjust-settings',
  'toggle-info'
]);

// 响应式状态
const activeTool = ref('Pan');
const brightness = ref(1.0);
const contrast = ref(1.0);
const showInfo = ref(true);

// 设置激活工具
function setActiveTool(toolName) {
  activeTool.value = toolName;
  emit('set-tool', toolName);
}

// 调整图像设置
function adjustImageSettings() {
  emit('adjust-settings', {
    brightness: parseFloat(brightness.value),
    contrast: parseFloat(contrast.value)
  });
}

// 切换信息面板
function toggleInfoPanel() {
  showInfo.value = !showInfo.value;
  emit('toggle-info', showInfo.value);
}

// 触发普通事件
function emitEvent(eventName) {
  emit(eventName);
}
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0.8rem;
  background-color: #141428; /* 更暗的背景色 */
  color: #f5f5f5; /* 更亮的文本颜色 */
  height: 100%;
  overflow-y: auto;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.sidebar-section h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #16d6ff; /* 更亮的蓝色 */
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 0.25rem;
}

.sidebar-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  background-color: rgba(22, 214, 255, 0.2); /* 半透明蓝色 */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  justify-content: flex-start;
}

.sidebar-button:hover {
  background-color: rgba(22, 214, 255, 0.4);
  transform: translateX(2px);
}

.sidebar-button.active {
  background-color: rgba(22, 214, 255, 0.9);
  color: #000; /* 激活时黑色文字在亮蓝背景上 */
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.slider-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
  margin-bottom: 0.5rem;
}

.slider-container label {
  font-size: 0.8rem;
  color: #aaa;
  display: flex;
  justify-content: space-between;
}

.slider-container label::after {
  content: attr(data-value);
}

input[type="range"] {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: var(--accent-color, #0bc5e6);
  border-radius: 50%;
  cursor: pointer;
}
</style>
