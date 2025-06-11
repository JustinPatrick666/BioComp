import { defineStore } from 'pinia';

interface DicomRecord {
  id: string;
  uploadTime: string;
  fileName: string;
  patientInfo: {
    name: string;
    age: string;
    gender: string;
  };
  imageInfo: {
    modality: string;
    seriesDescription: string;
    studyDate: string;
    rows: number;
    columns: number;
  };
  imageId?: string; // 用于重新加载图像
}

export const useDicomHistoryStore = defineStore('dicomHistory', {
  state: () => ({
    records: [] as DicomRecord[]
  }),

  actions: {
    addRecord(record: DicomRecord) {
      this.records.unshift(record); // 添加到开头
      this.saveToLocalStorage();
    },

    removeRecord(id: string) {
      const index = this.records.findIndex(r => r.id === id);
      if (index > -1) {
        this.records.splice(index, 1);
        this.saveToLocalStorage();
      }
    },

    loadFromLocalStorage() {
      const saved = localStorage.getItem('dicom-history');
      if (saved) {
        try {
          this.records = JSON.parse(saved);
        } catch (e) {
          console.error('加载历史记录失败:', e);
        }
      }
    },

    saveToLocalStorage() {
      localStorage.setItem('dicom-history', JSON.stringify(this.records));
    }
  }
});
