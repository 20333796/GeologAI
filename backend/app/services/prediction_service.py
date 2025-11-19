"""预测管理业务逻辑服务"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
import json
from datetime import datetime

from app.models import Prediction, WellLog, AIModel
from app.schemas import PredictionCreate, PredictionUpdate
from app.crud import PredictionCRUD, WellLogCRUD, AIModelCRUD

logger = logging.getLogger(__name__)


class PredictionService:
    """预测管理业务逻辑服务"""

    @staticmethod
    def create_prediction(db: Session, prediction_data: PredictionCreate) -> Dict[str, Any]:
        """创建预测任务 - 业务逻辑处理"""
        # 验证测井数据存在
        log = WellLogCRUD.get_by_id(db, prediction_data.log_id)
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        # 验证模型存在
        model = AIModelCRUD.get_by_id(db, prediction_data.model_id)
        if not model:
            return {
                "success": False,
                "error": "model_not_found",
                "message": "模型不存在"
            }

        # 检查模型状态
        if model.status != "active":
            return {
                "success": False,
                "error": "model_inactive",
                "message": f"模型已禁用（状态: {model.status}）"
            }

        # 验证置信度范围
        if not (0 <= prediction_data.confidence <= 1):
            return {
                "success": False,
                "error": "invalid_confidence",
                "message": "置信度必须在0-1之间"
            }

        try:
            # 兼容 tests 中将 results_json 作为字符串传入的情况，尝试解析为 dict
            if getattr(prediction_data, 'results_json', None) and isinstance(prediction_data.results_json, str):
                try:
                    parsed = json.loads(prediction_data.results_json)
                except Exception:
                    parsed = prediction_data.results_json

                prediction_data = PredictionCreate(
                    log_id=prediction_data.log_id,
                    model_id=prediction_data.model_id,
                    results_json=parsed,
                    confidence=prediction_data.confidence,
                    execution_time=prediction_data.execution_time
                )

            new_prediction = PredictionCRUD.create(db, prediction_data)
            logger.info(f"预测任务已创建: ID={new_prediction.id}, Log={log.filename}, Model={model.name}")
            
            return {
                "success": True,
                "prediction": new_prediction,
                "message": "预测任务创建成功"
            }
        except Exception as e:
            logger.error(f"预测任务创建失败: {str(e)}")
            return {
                "success": False,
                "error": "creation_failed",
                "message": "预测任务创建失败"
            }

    @staticmethod
    def get_prediction_details(db: Session, prediction_id: int) -> Dict[str, Any]:
        """获取预测详细信息"""
        prediction = PredictionCRUD.get_by_id(db, prediction_id)
        
        if not prediction:
            return {
                "success": False,
                "error": "prediction_not_found",
                "message": "预测结果不存在"
            }

        # 获取关联信息
        log = WellLogCRUD.get_by_id(db, prediction.log_id)
        model = AIModelCRUD.get_by_id(db, prediction.model_id)

        # 解析结果
        results = None
        if prediction.results_json:
            try:
                results = json.loads(prediction.results_json) if isinstance(prediction.results_json, str) else prediction.results_json
            except:
                results = prediction.results_json

        return {
            "success": True,
            "prediction": {
                "id": prediction.id,
                "log": {
                    "id": log.id,
                    "filename": log.filename
                } if log else None,
                "model": {
                    "id": model.id,
                    "name": model.name,
                    "version": model.version
                } if model else None,
                "results": results,
                "confidence": prediction.confidence,
                "execution_time": prediction.execution_time,
                "status": prediction.status,
                "created_at": prediction.created_at,
                "updated_at": prediction.updated_at
            },
            "message": "获取预测成功"
        }

    @staticmethod
    def rerun_prediction(db: Session, prediction_id: int) -> Dict[str, Any]:
        """重新运行预测"""
        prediction = PredictionCRUD.get_by_id(db, prediction_id)
        
        if not prediction:
            return {
                "success": False,
                "error": "prediction_not_found",
                "message": "预测结果不存在"
            }

        # 验证原始资源仍然存在
        log = WellLogCRUD.get_by_id(db, prediction.log_id)
        model = AIModelCRUD.get_by_id(db, prediction.model_id)

        if not log or not model:
            return {
                "success": False,
                "error": "resources_not_found",
                "message": "关联的资源已被删除"
            }

        try:
            # 创建新预测任务
            new_prediction_data = PredictionCreate(
                log_id=prediction.log_id,
                model_id=prediction.model_id,
                results_json=prediction.results_json,
                confidence=prediction.confidence,
                execution_time=prediction.execution_time
            )
            
            new_prediction = PredictionCRUD.create(db, new_prediction_data)
            logger.info(f"预测已重新运行: 原始ID={prediction_id}, 新ID={new_prediction.id}")
            
            return {
                "success": True,
                "new_prediction": new_prediction,
                "original_prediction_id": prediction_id,
                "message": "预测已重新运行"
            }
        except Exception as e:
            logger.error(f"预测重新运行失败: {str(e)}")
            return {
                "success": False,
                "error": "rerun_failed",
                "message": "重新运行失败"
            }

    @staticmethod
    def get_log_predictions(db: Session, log_id: int) -> Dict[str, Any]:
        """获取测井的所有预测结果"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        try:
            predictions = PredictionCRUD.get_by_log(db, log_id, skip=0, limit=100)
            
            return {
                "success": True,
                "predictions": predictions,
                "count": len(predictions),
                "message": "获取预测列表成功"
            }
        except Exception as e:
            logger.error(f"获取预测列表失败: {str(e)}")
            return {
                "success": False,
                "error": "query_failed",
                "message": "查询失败"
            }

    @staticmethod
    def get_model_statistics(db: Session, model_id: int) -> Dict[str, Any]:
        """获取模型预测统计"""
        model = AIModelCRUD.get_by_id(db, model_id)
        
        if not model:
            return {
                "success": False,
                "error": "model_not_found",
                "message": "模型不存在"
            }

        try:
            predictions = PredictionCRUD.get_by_model(db, model_id, skip=0, limit=1000)
            total_predictions = PredictionCRUD.count_by_model(db, model_id)

            # 计算统计信息
            avg_confidence = 0
            avg_execution_time = 0
            
            if predictions:
                avg_confidence = sum(p.confidence for p in predictions) / len(predictions)
                avg_execution_time = sum(p.execution_time or 0 for p in predictions) / len(predictions)

            return {
                "success": True,
                "statistics": {
                    "model_id": model_id,
                    "model_name": model.name,
                    "model_version": model.version,
                    "total_predictions": total_predictions,
                    "avg_confidence": round(avg_confidence, 4),
                    "avg_execution_time": round(avg_execution_time, 2),
                    "model_accuracy": model.accuracy,
                    "status": model.status
                },
                "message": "获取统计成功"
            }
        except Exception as e:
            logger.error(f"统计计算失败: {str(e)}")
            return {
                "success": False,
                "error": "calculation_failed",
                "message": "统计失败"
            }

    @staticmethod
    def compare_predictions(db: Session, log_id: int, model_ids: list) -> Dict[str, Any]:
        """比较不同模型的预测结果"""
        log = WellLogCRUD.get_by_id(db, log_id)
        
        if not log:
            return {
                "success": False,
                "error": "log_not_found",
                "message": "测井数据不存在"
            }

        try:
            comparison = []
            
            for model_id in model_ids:
                model = AIModelCRUD.get_by_id(db, model_id)
                if not model:
                    continue
                    
                # 获取最新的预测结果
                predictions = PredictionCRUD.get_by_log(db, log_id, skip=0, limit=1)
                
                if predictions:
                    latest_pred = None
                    for p in predictions:
                        if p.model_id == model_id:
                            latest_pred = p
                            break
                    
                    if latest_pred:
                        comparison.append({
                            "model_id": model_id,
                            "model_name": model.name,
                            "confidence": latest_pred.confidence,
                            "execution_time": latest_pred.execution_time,
                            "status": latest_pred.status,
                            "created_at": latest_pred.created_at
                        })

            return {
                "success": True,
                "comparison": comparison,
                "message": "比较完成"
            }
        except Exception as e:
            logger.error(f"预测比较失败: {str(e)}")
            return {
                "success": False,
                "error": "comparison_failed",
                "message": "比较失败"
            }

    @staticmethod
    def delete_prediction(db: Session, prediction_id: int) -> Dict[str, Any]:
        """删除预测结果"""
        prediction = PredictionCRUD.get_by_id(db, prediction_id)
        
        if not prediction:
            return {
                "success": False,
                "error": "prediction_not_found",
                "message": "预测结果不存在"
            }

        try:
            PredictionCRUD.delete(db, prediction_id)
            logger.info(f"预测结果已删除: ID={prediction_id}")
            
            return {
                "success": True,
                "message": "预测结果删除成功"
            }
        except Exception as e:
            logger.error(f"预测结果删除失败: {str(e)}")
            return {
                "success": False,
                "error": "deletion_failed",
                "message": "删除失败"
            }
