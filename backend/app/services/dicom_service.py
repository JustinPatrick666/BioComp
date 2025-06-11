import pydicom
from pathlib import Path
from pydicom.errors import InvalidDicomError
import logging
from typing import List, Dict, Optional
from app.models.schemas import DicomResult
import nibabel as nib

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义必需和可选标签
required_tags = {
    'PatientID': True,  # 必需且非空
    'StudyDate': False,  # 可选
    'Modality': False   # 可选
}

def validate_dicom(file_path: Path) -> bool:
    """验证医学影像文件有效性（支持DICOM和NIfTI格式）"""
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return False

    filename_lower = str(file_path).lower()
    
    try:
        # 处理DICOM文件
        if filename_lower.endswith('.dcm'):
            ds = pydicom.dcmread(file_path)
            logger.info(f"成功读取DICOM文件: {file_path}")

            for tag, required in required_tags.items():
                if required:
                    if tag not in ds or not ds[tag].value:
                        logger.warning(f"必需的标签缺失或无效: {tag} in {file_path}")
                        return False
                else:
                    if tag in ds and ds[tag].value:
                        logger.info(f"标签 {tag}: {ds[tag].value}")
                    else:
                        logger.info(f"标签 {tag} 不存在或为空")
            return True
            
        # 处理NIfTI文件
        elif filename_lower.endswith('.nii') or filename_lower.endswith('.nii.gz'):
            img = nib.load(str(file_path))
            logger.info(f"成功读取NIfTI文件: {file_path}, 形状: {img.shape}")
            
            # NIfTI文件基本验证：检查是否有有效的数据形状
            if len(img.shape) < 3:
                logger.warning(f"NIfTI文件维度不足: {file_path}, 形状: {img.shape}")
                return False
                
            return True
        else:
            logger.error(f"不支持的文件格式: {file_path}")
            return False
            
    except InvalidDicomError as e:
        logger.error(f"无效的DICOM文件: {file_path}, 错误信息: {e}")
        return False
    except Exception as e:
        logger.error(f"处理文件时发生错误: {file_path}, 错误信息: {e}")
        return False

def get_dicom_results(directory: Path) -> List[DicomResult]:
    """获取指定目录下所有医学影像文件的处理结果"""
    results = []
    
    # 支持的文件扩展名
    patterns = ["*.dcm", "*.nii", "*.nii.gz"]
    
    for pattern in patterns:
        for file_path in directory.glob(pattern):
            try:
                filename_lower = str(file_path).lower()
                
                if filename_lower.endswith('.dcm'):
                    # 处理DICOM文件
                    ds = pydicom.dcmread(file_path)
                    result = DicomResult(
                        filename=file_path.name,
                        patient_id=getattr(ds, 'PatientID', None),
                        study_date=getattr(ds, 'StudyDate', None),
                        modality=getattr(ds, 'Modality', None),
                        additional_info={
                            "file_type": "DICOM",
                            "rows": str(getattr(ds, 'Rows', 'Unknown')),
                            "columns": str(getattr(ds, 'Columns', 'Unknown'))
                        }
                    )
                elif filename_lower.endswith('.nii') or filename_lower.endswith('.nii.gz'):
                    # 处理NIfTI文件
                    img = nib.load(str(file_path))
                    result = DicomResult(
                        filename=file_path.name,
                        patient_id=f"nifti_{file_path.stem}",  # 为NIfTI文件生成ID
                        study_date=None,
                        modality="Unknown",  # NIfTI文件通常不包含模态信息
                        additional_info={
                            "file_type": "NIfTI",
                            "shape": str(img.shape),
                            "data_type": str(img.get_fdata().dtype),
                            "affine_matrix": "present"
                        }
                    )
                else:
                    continue
                    
                results.append(result)
                
            except Exception as e:
                logger.error(f"无法读取医学影像文件 {file_path}: {e}")
                
    return results