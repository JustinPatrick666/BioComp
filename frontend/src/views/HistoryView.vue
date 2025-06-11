<template>
  <div class="history">
    <h1>历史记录</h1>    <div class="history-list">
      <div v-if="records.length === 0" class="empty-history">
        <i class="fas fa-history"></i>
        <p>暂无历史记录</p>
      </div>
      <div v-else v-for="record in records" :key="record.id" class="history-item">
        <div class="history-item-header">
          <h3>{{ record.fileName }}</h3>
          <span class="upload-time">{{ record.uploadTime }}</span>
        </div>
        <div class="history-item-content">
          <div class="info-group">
            <h4>患者信息</h4>
            <div class="info-row">
              <span class="label">姓名:</span>
              <span class="value">{{ record.patientInfo.name }}</span>
            </div>
            <div class="info-row">
              <span class="label">年龄:</span>
              <span class="value">{{ record.patientInfo.age }}</span>
            </div>
            <div class="info-row">
              <span class="label">性别:</span>
              <span class="value">{{ record.patientInfo.gender }}</span>
            </div>
          </div>
          <div class="info-group">
            <h4>图像信息</h4>
            <div class="info-row">
              <span class="label">模态:</span>
              <span class="value">{{ record.imageInfo.modality }}</span>
            </div>
            <div class="info-row">
              <span class="label">序列:</span>
              <span class="value">{{ record.imageInfo.seriesDescription }}</span>
            </div>
            <div class="info-row">
              <span class="label">日期:</span>
              <span class="value">{{ record.imageInfo.studyDate }}</span>
            </div>
            <div class="info-row">
              <span class="label">尺寸:</span>
              <span class="value">{{ record.imageInfo.rows }}x{{ record.imageInfo.columns }}</span>
            </div>
          </div>
        </div>
        <div class="history-item-actions">
          <button @click="reloadImage(record)" class="action-button">
            <i class="fas fa-eye"></i> 查看图像
          </button>
          <button @click="removeRecord(record.id)" class="action-button delete">
            <i class="fas fa-trash"></i> 删除记录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDicomHistoryStore } from '@/stores/dicomHistory';

const router = useRouter();
const historyStore = useDicomHistoryStore();
const records = ref(historyStore.records);

onMounted(() => {
  historyStore.loadFromLocalStorage();
  records.value = historyStore.records;
});

function reloadImage(record: any) {
  // 使用图像ID导航到主页
  router.push({
    path: '/',
    query: { imageId: record.imageId }
  });
}

function removeRecord(id: string) {
  historyStore.removeRecord(id);
  records.value = historyStore.records;
}
</script>

<style scoped>
.history {
  padding: 2rem;
  background-color: var(--main-bg, #0f0f1b);
  min-height: calc(100vh - var(--header-height, 50px));
}

.history h1 {
  color: var(--accent-color, #0bc5e6);
  margin-bottom: 2rem;
}

.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

.empty-history {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background-color: var(--sidebar-bg, #1a1a2e);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.empty-history i {
  font-size: 3rem;
  color: var(--accent-color, #0bc5e6);
  margin-bottom: 1rem;
}

.empty-history p {
  color: var(--text-light, #e6e6e6);
  font-size: 1.2rem;
  margin: 0;
}

.history-item {
  background-color: var(--sidebar-bg, #1a1a2e);
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-item-header h3 {
  color: var(--text-light, #e6e6e6);
  margin: 0;
  font-size: 1.1rem;
}

.upload-time {
  color: var(--text-light, #e6e6e6);
  opacity: 0.7;
  font-size: 0.9rem;
}

.history-item-content {
  display: grid;
  gap: 1.5rem;
}

.info-group {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 1rem;
}

.info-group h4 {
  color: var(--accent-color, #0bc5e6);
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
}

.info-row {
  display: flex;
  margin: 0.5rem 0;
}

.info-row .label {
  color: var(--text-light, #e6e6e6);
  opacity: 0.7;
  width: 60px;
  flex-shrink: 0;
}

.info-row .value {
  color: var(--text-light, #e6e6e6);
}

.history-item-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.action-button {
  flex: 1;
  padding: 0.5rem 1rem;
  background-color: var(--accent-color, #0bc5e6);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.action-button:hover {
  filter: brightness(1.2);
}

.action-button.delete {
  background-color: #e63c3c;
}

.action-button i {
  font-size: 0.9rem;
}
</style>
