// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './assets/base.css'
import './assets/main.css'
import router from './router'
import * as cornerstone from 'cornerstone-core'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from 'cornerstone-tools'
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader'
import * as dicomParser from 'dicom-parser'
import { initCornerstone } from '@/composables/useDicom'

const startApp = async () => {
  try {
    
    // 配置外部依赖
    cornerstoneTools.external.cornerstone = cornerstone
    cornerstoneTools.external.cornerstoneMath = cornerstoneMath
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone
    cornerstoneWADOImageLoader.external.dicomParser = dicomParser

    // 初始化图像加载器
    cornerstoneWADOImageLoader.webWorkerManager.initialize({
      maxWebWorkers: navigator.hardwareConcurrency || 1,
      startWebWorkersOnDemand: true,
      taskConfiguration: {
        decodeTask: {
          loadCodecsOnStartup: true,
          initializeCodecsOnStartup: false,
        },
      },
    })

    // 注册图像加载器
    cornerstone.registerImageLoader('wadouri', cornerstoneWADOImageLoader.wadouri.loadImage)
    cornerstone.registerImageLoader('wadors', cornerstoneWADOImageLoader.wadors.loadImage)

    // 初始化cornerstone工具
    await initCornerstone()

    // 创建并配置Vue应用
    const app = createApp(App)
    const pinia = createPinia()
    
    app.use(pinia)
    app.use(router)
    
    // 挂载应用
    app.mount('#app')
    
    console.log('✅ 应用初始化成功')
  } catch (error) {
    console.error('❌ 应用初始化失败:', error)
    throw error
  }
}

startApp().catch(console.error)
