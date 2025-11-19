"""预测结果数据库操作层"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Prediction
from app.schemas import PredictionCreate, PredictionUpdate


class PredictionCRUD:
    """预测结果数据库操作"""

    @staticmethod
    def create(db: Session, prediction: PredictionCreate) -> Prediction:
        """创建新的预测结果"""
        db_prediction = Prediction(
            log_id=prediction.log_id,
            model_id=prediction.model_id,
            results_json=prediction.results_json,
            confidence=prediction.confidence,
            execution_time=prediction.execution_time,
            status="success"
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction

    @staticmethod
    def get_by_id(db: Session, prediction_id: int) -> Optional[Prediction]:
        """通过ID获取预测结果"""
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    @staticmethod
    def get_by_log(db: Session, log_id: int, skip: int = 0, limit: int = 10) -> List[Prediction]:
        """获取测井的所有预测结果"""
        query = db.query(Prediction).filter(Prediction.log_id == log_id)
        query = query.order_by(Prediction.created_at.desc())
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_by_model(db: Session, model_id: int, skip: int = 0, limit: int = 10) -> List[Prediction]:
        """获取模型的所有预测结果"""
        query = db.query(Prediction).filter(Prediction.model_id == model_id)
        query = query.order_by(Prediction.created_at.desc())
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def list_predictions(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[Prediction]:
        """列出预测结果"""
        query = db.query(Prediction)
        
        if status:
            query = query.filter(Prediction.status == status)
        query = query.order_by(Prediction.created_at.desc())
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取预测结果总数"""
        return db.query(Prediction).count()

    @staticmethod
    def update(db: Session, prediction_id: int, prediction_update: PredictionUpdate) -> Optional[Prediction]:
        """更新预测结果"""
        db_prediction = PredictionCRUD.get_by_id(db, prediction_id)
        if not db_prediction:
            return None
        
        update_data = prediction_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_prediction, key, value)
        
        db_prediction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_prediction)
        return db_prediction

    @staticmethod
    def delete(db: Session, prediction_id: int) -> bool:
        """删除预测结果"""
        db_prediction = PredictionCRUD.get_by_id(db, prediction_id)
        if not db_prediction:
            return False
        
        db.delete(db_prediction)
        db.commit()
        return True

    @staticmethod
    def count_by_log(db: Session, log_id: int) -> int:
        """获取测井的预测结果数"""
        return db.query(Prediction).filter(Prediction.log_id == log_id).count()

    @staticmethod
    def count_by_model(db: Session, model_id: int) -> int:
        """获取模型的预测数"""
        return db.query(Prediction).filter(Prediction.model_id == model_id).count()
