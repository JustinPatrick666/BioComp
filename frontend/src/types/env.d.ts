/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// cornerstone 相关模块声明
declare module 'cornerstone-core'
declare module 'cornerstone-math'
declare module 'cornerstone-tools'
declare module 'cornerstone-wado-image-loader'
declare module 'dicom-parser'
declare module 'hammerjs'

// 全局类型声明
interface Window {
  cornerstone: any
  cornerstoneTools: any
  cornerstoneWADOImageLoader: any
  cornerstoneToolsInitialized?: boolean
}
