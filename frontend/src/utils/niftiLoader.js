/**
 * NIfTI文件加载器
 * 支持.nii和.nii.gz格式的医学影像文件
 */

import * as nifti from 'nifti-reader-js';
import pako from 'pako';

/**
 * 检测文件是否为NIfTI格式
 * @param {string} filename - 文件名
 * @returns {boolean} - 是否为NIfTI格式
 */
export function isNiftiFile(filename) {
  const lowerName = filename.toLowerCase();
  return lowerName.endsWith('.nii') || lowerName.endsWith('.nii.gz');
}

/**
 * 检测文件是否为压缩的NIfTI格式
 * @param {string} filename - 文件名
 * @returns {boolean} - 是否为压缩格式
 */
export function isCompressedNifti(filename) {
  return filename.toLowerCase().endsWith('.nii.gz');
}

/**
 * 加载NIfTI文件
 * @param {File} file - 文件对象
 * @returns {Promise<Object>} - 返回包含图像数据和头信息的对象
 */
export async function loadNiftiFile(file) {
  try {
    console.log('🔄 开始加载NIfTI文件:', file.name);
    
    // 读取文件为ArrayBuffer
    const arrayBuffer = await file.arrayBuffer();
    console.log('📂 文件读取完成，大小:', arrayBuffer.byteLength, 'bytes');
    
    let data = arrayBuffer;
    
    // 如果是压缩文件，先解压
    if (isCompressedNifti(file.name)) {
      console.log('📦 检测到.gz压缩文件，正在解压...');
      try {
        const uint8Array = new Uint8Array(arrayBuffer);
        const decompressed = pako.ungzip(uint8Array);
        data = decompressed.buffer;
        console.log('✅ 解压完成，解压后大小:', data.byteLength, 'bytes');
      } catch (decompressError) {
        console.error('❌ 解压失败:', decompressError);
        throw new Error(`解压.gz文件失败: ${decompressError.message}`);
      }
    }
    
    // 检查是否为有效的NIfTI文件
    if (!nifti.isNIFTI(data)) {
      throw new Error('不是有效的NIfTI文件格式');
    }
    
    console.log('✅ NIfTI格式验证通过');
    
    // 解析NIfTI头信息
    const header = nifti.readHeader(data);
    console.log('📋 NIfTI头信息:', {
      dims: header.dims,
      pixDims: header.pixDims,
      datatype: header.datatypeCode,
      description: header.description,
      cal_max: header.cal_max,
      cal_min: header.cal_min
    });
      // 读取图像数据
    const imageData = nifti.readImage(header, data);
    console.log('🖼️ 图像数据读取完成，数据长度:', imageData.byteLength);
    
    // 创建NIfTI数据对象
    const niftiData = {
      header: header,
      imageData: imageData,
      filename: file.name
    };
    
    // 转换为Cornerstone兼容的图像对象
    console.log('🔄 转换为Cornerstone格式...');
    const cornerstoneImage = convertNiftiToCornerstone(niftiData);
    console.log('✅ NIfTI加载和转换完成');
    
    return cornerstoneImage;
    
  } catch (error) {
    console.error('❌ 加载NIfTI文件失败:', error);
    throw error;
  }
}

/**
 * 将NIfTI数据转换为Cornerstone兼容的图像对象
 * @param {Object} niftiData - NIfTI数据对象
 * @param {number} sliceIndex - 切片索引（默认为中间切片）
 * @returns {Object} - Cornerstone图像对象
 */
export function convertNiftiToCornerstone(niftiData, sliceIndex = null) {
  try {
    const { header, imageData } = niftiData;
      // 获取图像尺寸，确保是数字类型
    const width = Number(header.dims[1]);
    const height = Number(header.dims[2]);
    const depth = Number(header.dims[3]) || 1;
    
    console.log(`🔍 图像尺寸: ${width}x${height}x${depth}`);
    
    // 验证尺寸有效性
    if (!width || !height || width <= 0 || height <= 0) {
      throw new Error(`无效的图像尺寸: ${width}x${height}`);
    }
    
    // 如果没有指定切片索引，使用中间切片
    if (sliceIndex === null) {
      sliceIndex = Math.floor(depth / 2);
    }
    
    // 确保切片索引在有效范围内
    sliceIndex = Math.max(0, Math.min(sliceIndex, depth - 1));
    console.log('🔖 选择切片索引:', sliceIndex);
    
    // 根据数据类型创建像素数据
    let pixelData;
    let minPixelValue = Infinity;
    let maxPixelValue = -Infinity;
    
    // 计算单个切片的像素数量
    const pixelsPerSlice = width * height;
    const sliceOffset = sliceIndex * pixelsPerSlice;
    
    // 根据NIfTI数据类型处理像素数据
    switch (header.datatypeCode) {
      case 2: // DT_UNSIGNED_CHAR
        pixelData = new Uint8Array(imageData, sliceOffset, pixelsPerSlice);
        break;
      case 4: // DT_SIGNED_SHORT
        pixelData = new Int16Array(imageData, sliceOffset * 2, pixelsPerSlice);
        break;
      case 8: // DT_SIGNED_INT
        pixelData = new Int32Array(imageData, sliceOffset * 4, pixelsPerSlice);
        break;
      case 16: // DT_FLOAT
        pixelData = new Float32Array(imageData, sliceOffset * 4, pixelsPerSlice);
        break;
      case 64: // DT_DOUBLE
        pixelData = new Float64Array(imageData, sliceOffset * 8, pixelsPerSlice);
        break;
      default:
        // 默认尝试使用16位有符号整数
        console.warn('⚠️ 未知的数据类型:', header.datatypeCode, '，使用默认Int16Array');
        pixelData = new Int16Array(imageData, sliceOffset * 2, pixelsPerSlice);
    }
    
    // 计算像素值范围
    for (let i = 0; i < pixelData.length; i++) {
      const value = pixelData[i];
      if (value < minPixelValue) minPixelValue = value;
      if (value > maxPixelValue) maxPixelValue = value;
    }
    
    console.log('📊 像素值范围:', minPixelValue, '~', maxPixelValue);    // 创建Cornerstone兼容的图像对象
    const cornerstoneImage = {
      imageId: `nifti:${niftiData.filename}:${sliceIndex}`,
      minPixelValue: minPixelValue,
      maxPixelValue: maxPixelValue,
      slope: header.scl_slope || 1,
      intercept: header.scl_inter || 0,
      windowCenter: (maxPixelValue + minPixelValue) / 2,
      windowWidth: maxPixelValue - minPixelValue,
      rows: height,
      columns: width,
      height: height,
      width: width,
      color: false,
      columnPixelSpacing: header.pixDims[1] || 1,
      rowPixelSpacing: header.pixDims[2] || 1,
      sliceThickness: header.pixDims[3] || 1,
      pixelSpacing: [header.pixDims[1] || 1, header.pixDims[2] || 1],
      sizeInBytes: pixelData.length * pixelData.BYTES_PER_ELEMENT,
      getPixelData: () => pixelData,
      // 确保Cornerstone所需的基本属性
      invert: false,
      photometricInterpretation: 'MONOCHROME2',
      samplesPerPixel: 1,
      pixelRepresentation: 1,
      bitsAllocated: 16,
      bitsStored: 16,
      highBit: 15,
      // 额外的NIfTI信息
      niftiHeader: header,
      currentSlice: sliceIndex,
      totalSlices: depth
    };
    
    // 验证创建的图像对象
    console.log('🔍 验证Cornerstone图像对象:');
    console.log('  - width:', cornerstoneImage.width, '(类型:', typeof cornerstoneImage.width, ')');
    console.log('  - height:', cornerstoneImage.height, '(类型:', typeof cornerstoneImage.height, ')');
    console.log('  - getPixelData:', typeof cornerstoneImage.getPixelData);
    
    if (typeof cornerstoneImage.width !== 'number' || typeof cornerstoneImage.height !== 'number') {
      throw new Error(`图像尺寸必须为数字类型: width=${cornerstoneImage.width}, height=${cornerstoneImage.height}`);
    }
    
    console.log('✅ NIfTI到Cornerstone转换完成');
    return cornerstoneImage;
    
  } catch (error) {
    console.error('❌ NIfTI到Cornerstone转换失败:', error);
    throw error;
  }
}

/**
 * 从NIfTI头信息中提取患者信息
 * @param {Object} header - NIfTI头信息
 * @returns {Object} - 患者信息对象
 */
export function extractNiftiPatientInfo(header) {
  return {
    patientName: header.description || '未知患者',
    patientId: 'N/A',
    studyDate: 'N/A',
    modality: 'MR', // NIfTI文件通常是MRI
    institution: 'N/A'
  };
}

/**
 * 从NIfTI头信息中提取图像信息
 * @param {Object} header - NIfTI头信息
 * @param {Object} cornerstoneImage - Cornerstone图像对象
 * @returns {Object} - 图像信息对象
 */
export function extractNiftiImageInfo(header, cornerstoneImage) {
  return {
    width: header.dims[1],
    height: header.dims[2],
    depth: header.dims[3] || 1,
    pixelSpacing: `${header.pixDims[1]?.toFixed(2) || '1.00'} mm x ${header.pixDims[2]?.toFixed(2) || '1.00'} mm`,
    sliceThickness: `${header.pixDims[3]?.toFixed(2) || '1.00'} mm`,
    dataType: getNiftiDataTypeName(header.datatypeCode),
    fileSize: formatFileSize(header.vox_offset + (header.dims[1] * header.dims[2] * (header.dims[3] || 1) * getBytesPerPixel(header.datatypeCode))),
    currentSlice: cornerstoneImage.currentSlice + 1,
    totalSlices: cornerstoneImage.totalSlices,
    windowCenter: cornerstoneImage.windowCenter.toFixed(0),
    windowWidth: cornerstoneImage.windowWidth.toFixed(0)
  };
}

/**
 * 获取NIfTI数据类型名称
 * @param {number} datatypeCode - 数据类型代码
 * @returns {string} - 数据类型名称
 */
function getNiftiDataTypeName(datatypeCode) {
  const dataTypes = {
    2: 'UINT8',
    4: 'INT16',
    8: 'INT32',
    16: 'FLOAT32',
    64: 'FLOAT64'
  };
  return dataTypes[datatypeCode] || `未知(${datatypeCode})`;
}

/**
 * 获取每个像素的字节数
 * @param {number} datatypeCode - 数据类型代码
 * @returns {number} - 字节数
 */
function getBytesPerPixel(datatypeCode) {
  const bytesPerPixel = {
    2: 1,  // UINT8
    4: 2,  // INT16
    8: 4,  // INT32
    16: 4, // FLOAT32
    64: 8  // FLOAT64
  };
  return bytesPerPixel[datatypeCode] || 2;
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} - 格式化后的文件大小
 */
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}
