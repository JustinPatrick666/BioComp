// src/composables/useDicom.ts
import * as cornerstone from 'cornerstone-core'
import * as cornerstoneTools from 'cornerstone-tools'
import * as cornerstoneMath from 'cornerstone-math'
import Hammer from 'hammerjs'

export async function initCornerstone() {
  try {
    // 设置外部依赖
    cornerstoneTools.external.cornerstone = cornerstone
    cornerstoneTools.external.Hammer = Hammer
    cornerstoneTools.external.cornerstoneMath = cornerstoneMath

    // 初始化工具库
    await cornerstoneTools.init({
      globalToolSyncEnabled: true,
      showSVGCursors: true,
      mouseEnabled: true,
      touchEnabled: true
    })

    // 添加所有需要的工具
    cornerstoneTools.addTool(cornerstoneTools.PanTool)
    cornerstoneTools.addTool(cornerstoneTools.ZoomTool)
    cornerstoneTools.addTool(cornerstoneTools.WwwcTool)
    cornerstoneTools.addTool(cornerstoneTools.LengthTool)
    cornerstoneTools.addTool(cornerstoneTools.AngleTool)
    cornerstoneTools.addTool(cornerstoneTools.RectangleRoiTool)
    cornerstoneTools.addTool(cornerstoneTools.EllipticalRoiTool)

    // 设置默认工具状态
    cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 })
    cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 2 })
    cornerstoneTools.setToolEnabled('Wwwc', { mouseButtonMask: 4 })

    console.log('✅ Cornerstone初始化成功')
    return true
  } catch (error) {
    console.error('❌ Cornerstone初始化失败:', error)
    throw error
  }
}
