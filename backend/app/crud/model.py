"""AI模型数据库操作层"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import AIModel
from app.schemas import AIModelCreate, AIModelUpdate


class AIModelCRUD:
    """AI模型数据库操作"""

    @staticmethod
    def create(db: Session, model: AIModelCreate) -> AIModel:
        """创建新的AI模型"""
        db_model = AIModel(
            name=model.name,
            version=model.version,
            model_type=model.model_type,
            accuracy=model.accuracy,
            model_path=model.model_path,
            parameters_json=model.parameters_json,
            status="active"
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    @staticmethod
    def get_by_id(db: Session, model_id: int) -> Optional[AIModel]:
        """通过ID获取模型"""
        return db.query(AIModel).filter(AIModel.id == model_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[AIModel]:
        """通过名称获取模型"""
        return db.query(AIModel).filter(AIModel.name == name).first()

    @staticmethod
    def list_models(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        model_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[AIModel]:
        """列出模型"""
        query = db.query(AIModel)
        
        if model_type:
            query = query.filter(AIModel.model_type == model_type)
        if status:
            query = query.filter(AIModel.status == status)
        
        return query.offset(skip).limit(limit).order_by(AIModel.created_at.desc()).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取模型总数"""
        return db.query(AIModel).count()

    @staticmethod
    def update(db: Session, model_id: int, model_update: AIModelUpdate) -> Optional[AIModel]:
        """更新模型"""
        db_model = AIModelCRUD.get_by_id(db, model_id)
        if not db_model:
            return None
        
        update_data = model_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_model, key, value)
        
        db_model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_model)
        return db_model

    @staticmethod
    def delete(db: Session, model_id: int) -> bool:
        """删除模型"""
        db_model = AIModelCRUD.get_by_id(db, model_id)
        if not db_model:
            return False
        
        db.delete(db_model)
        db.commit()
        return True

    @staticmethod
    def change_status(db: Session, model_id: int, status: str) -> Optional[AIModel]:
        """改变模型状态"""
        db_model = AIModelCRUD.get_by_id(db, model_id)
        if not db_model:
            return None
        
        db_model.status = status
        db_model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_model)
        return db_model
