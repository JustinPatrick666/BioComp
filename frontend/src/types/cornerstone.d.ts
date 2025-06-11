declare module 'cornerstone-core'
declare module 'cornerstone-math'
declare module 'cornerstone-tools'
declare module 'cornerstone-wado-image-loader'
declare module 'dicom-parser'

// 为 Window 对象添加自定义属性
interface Window {
  cornerstone: any;
  cornerstoneTools: any;
  cornerstoneWADOImageLoader: any;
  cornerstoneToolsInitialized?: boolean;
}
