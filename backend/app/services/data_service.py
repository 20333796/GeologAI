"""数据管理业务逻辑服务"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging
import json

from app.models import WellLog, CurveData
from app.schemas import WellLogCreate, WellLogUpdate
from app.crud import WellLogCRUD, CurveDataCRUD, ProjectCRUD

logger = logging.getLogger(__name__)


class DataService:
    """数据管理业务逻辑服务"""

    @staticmethod
    def upload_well_log(db: Session, project_id: int, log_data: WellLogCreate) -> Dict[str, Any]:
        """上传测井数据 - 业务逻辑处理"""
        # 验证项目存在
        project = ProjectCRUD.get_by_id(db, project_id)
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        # 检查文件大小
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        if log_data.file_size > MAX_FILE_SIZE:
            return {
                "success": False,
                "error": "file_too_large",
                "message": "文件过大（最大100MB）"
            }

        # 检查文件名是否重复
        existing_log = db.query(WellLog).filter(
            WellLog.project_id == project_id,
            WellLog.filename == log_data.filename
        ).first()
        
        if existing_log:
            return {
                "success": False,
                "error": "file_exists",
                "message": f"文件'{log_data.filename}'已存在"
            }

        try:
            new_log = WellLogCRUD.create(db, log_data, project_id)
            logger.info(f"测井数据已上传: {new_log.filename} (ID: {new_log.id}, Project: {project.name})")
            
            return {
                "success": True,
                "log": new_log,
                "message": "测井数据上传成功"
            }
        except Exception as e:
            logger.error(f"测井数据上传失败: {str(e)}")
            return {
                "success": False,
                "error": "upload_failed",
                "message": "上传失败"
            }

    @staticmethod
    def get_log_summary(db: Session, log_id: int) -> Dict[str, Any]:
        """获取测井数据摘要信息"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        # 获取曲线统计
        curves_count = CurveDataCRUD.count_by_log(db, log_id)
        
        # 解析曲线信息
        curves_info = []
        if log.curves_json:
            try:
                curves_data = json.loads(log.curves_json) if isinstance(log.curves_json, str) else log.curves_json
                curves_info = curves_data.get('curves', []) if isinstance(curves_data, dict) else curves_data
            except:
                pass

        return {
            "success": True,
            "summary": {
                "id": log.id,
                "filename": log.filename,
                "file_size": log.file_size,
                "file_path": log.file_path,
                "depth_from": log.depth_from,
                "depth_to": log.depth_to,
                "sample_count": log.sample_count,
                "curves_count": len(curves_info),
                "curves": curves_info,
                "data_points_count": curves_count,
                "status": log.status,
                "created_at": log.created_at
            },
            "message": "获取摘要成功"
        }

    @staticmethod
    def delete_log_with_data(db: Session, log_id: int) -> Dict[str, Any]:
        """删除测井及其所有曲线数据"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        try:
            # 删除所有曲线数据
            CurveDataCRUD.delete_by_log(db, log_id)
            
            # 删除测井记录
            WellLogCRUD.delete(db, log_id)
            
            logger.info(f"测井数据已删除: {log.filename} (ID: {log_id})")
            
            return {
                "success": True,
                "message": "测井数据删除成功"
            }
        except Exception as e:
            logger.error(f"测井数据删除失败: {str(e)}")
            return {
                "success": False,
                "error": "deletion_failed",
                "message": "删除失败"
            }

    @staticmethod
    def analyze_log_statistics(db: Session, log_id: int) -> Dict[str, Any]:
        """分析测井数据统计信息"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        try:
            # 获取所有曲线数据
            from sqlalchemy import func
            
            # 统计数据点
            total_points = db.query(func.count(CurveData.id)).filter(
                CurveData.log_id == log_id
            ).scalar() or 0

            # 获取唯一曲线名称
            curve_names = db.query(CurveData.curve_name).filter(
                CurveData.log_id == log_id
            ).distinct().all()
            
            curves_list = [name[0] for name in curve_names]

            # 获取深度范围
            depth_stats = db.query(
                func.min(CurveData.depth),
                func.max(CurveData.depth)
            ).filter(CurveData.log_id == log_id).first()

            return {
                "success": True,
                "statistics": {
                    "log_id": log_id,
                    "filename": log.filename,
                    "total_data_points": total_points,
                    "curves_count": len(curves_list),
                    "curves": curves_list,
                    "depth_range": {
                        "min": depth_stats[0] if depth_stats and depth_stats[0] else log.depth_from,
                        "max": depth_stats[1] if depth_stats and depth_stats[1] else log.depth_to
                    },
                    "status": log.status
                },
                "message": "分析成功"
            }
        except Exception as e:
            logger.error(f"测井分析失败: {str(e)}")
            return {
                "success": False,
                "error": "analysis_failed",
                "message": "分析失败"
            }

    @staticmethod
    def get_curve_data_range(db: Session, log_id: int, curve_name: str, 
                            depth_from: float = None, depth_to: float = None) -> Dict[str, Any]:
        """获取特定曲线的数据范围"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        try:
            if depth_from is not None and depth_to is not None:
                curves = CurveDataCRUD.get_by_log_and_depth(db, log_id, depth_from, depth_to)
                # 筛选曲线名称
                curves = [c for c in curves if c.curve_name == curve_name]
            else:
                curves = CurveDataCRUD.get_by_curve_name(db, log_id, curve_name)

            return {
                "success": True,
                "data": {
                    "curve_name": curve_name,
                    "data_count": len(curves),
                    "data_points": [{
                        "depth": c.depth,
                        "value": c.value,
                        "quality": c.quality_flag
                    } for c in curves]
                },
                "message": "获取曲线数据成功"
            }
        except Exception as e:
            logger.error(f"获取曲线数据失败: {str(e)}")
            return {
                "success": False,
                "error": "query_failed",
                "message": "查询失败"
            }

    @staticmethod
    def batch_import_curves(db: Session, log_id: int, curves_data: List[Dict]) -> Dict[str, Any]:
        """批量导入曲线数据"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        imported_count = 0
        failed_count = 0
        errors = []

        try:
            for i, curve_point in enumerate(curves_data):
                try:
                    CurveDataCRUD.create(
                        db,
                        curve_point.get('curve_name', 'unknown'),
                        curve_point.get('depth', 0),
                        curve_point.get('value', 0),
                        curve_point.get('quality_flag', 'good'),
                        log_id
                    )
                    imported_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"第 {i+1} 行失败: {str(e)}")

            logger.info(f"曲线数据导入完成: {imported_count} 成功, {failed_count} 失败")
            
            return {
                "success": True,
                "imported_count": imported_count,
                "failed_count": failed_count,
                "errors": errors if errors else None,
                "message": f"已导入 {imported_count} 条数据"
            }
        except Exception as e:
            logger.error(f"批量导入失败: {str(e)}")
            return {
                "success": False,
                "error": "import_failed",
                "message": "导入失败"
            }

    @staticmethod
    def export_log_data(db: Session, log_id: int, format: str = "json") -> Dict[str, Any]:
        """导出测井数据"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        try:
            if format == "json":
                # 获取所有曲线数据
                curves_query = db.query(CurveData).filter(CurveData.log_id == log_id).all()
                
                export_data = {
                    "metadata": {
                        "filename": log.filename,
                        "depth_from": log.depth_from,
                        "depth_to": log.depth_to,
                        "sample_count": log.sample_count
                    },
                    "data": [{
                        "curve_name": c.curve_name,
                        "depth": c.depth,
                        "value": c.value,
                        "quality_flag": c.quality_flag
                    } for c in curves_query]
                }
                
                return {
                    "success": True,
                    "export_data": export_data,
                    "message": "导出成功"
                }
            else:
                return {
                    "success": False,
                    "error": "unsupported_format",
                    "message": "不支持的格式"
                }
        except Exception as e:
            logger.error(f"导出失败: {str(e)}")
            return {
                "success": False,
                "error": "export_failed",
                "message": "导出失败"
            }
