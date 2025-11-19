"""测井数据库操作层"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import WellLog, CurveData
from app.schemas import WellLogCreate, WellLogUpdate


class WellLogCRUD:
    """测井数据库操作"""

    @staticmethod
    def create(db: Session, well_log: WellLogCreate, project_id: int) -> WellLog:
        """创建新的测井数据"""
        db_log = WellLog(
            filename=well_log.filename,
            file_path=well_log.file_path,
            file_size=well_log.file_size,
            project_id=project_id,
            depth_from=well_log.depth_from,
            depth_to=well_log.depth_to,
            sample_count=well_log.sample_count,
            curves_json=well_log.curves_json,
            status="processing"
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def get_by_id(db: Session, log_id: int) -> Optional[WellLog]:
        """通过ID获取测井数据"""
        return db.query(WellLog).filter(WellLog.id == log_id).first()

    @staticmethod
    def get_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 10) -> List[WellLog]:
        """获取项目的所有测井数据"""
        query = db.query(WellLog).filter(WellLog.project_id == project_id)
        query = query.order_by(WellLog.created_at.desc())
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def list_logs(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[WellLog]:
        """列出测井数据"""
        query = db.query(WellLog)
        
        if status:
            query = query.filter(WellLog.status == status)
        query = query.order_by(WellLog.created_at.desc())
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取测井数据总数"""
        return db.query(WellLog).count()

    @staticmethod
    def update(db: Session, log_id: int, log_update: WellLogUpdate) -> Optional[WellLog]:
        """更新测井数据"""
        db_log = WellLogCRUD.get_by_id(db, log_id)
        if not db_log:
            return None
        
        update_data = log_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_log, key, value)
        
        db_log.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def delete(db: Session, log_id: int) -> bool:
        """删除测井数据"""
        db_log = WellLogCRUD.get_by_id(db, log_id)
        if not db_log:
            return False
        
        db.delete(db_log)
        db.commit()
        return True

    @staticmethod
    def count_by_project(db: Session, project_id: int) -> int:
        """获取项目测井数据数"""
        return db.query(WellLog).filter(WellLog.project_id == project_id).count()


class CurveDataCRUD:
    """曲线数据库操作"""

    @staticmethod
    def create(db: Session, curve_name: str, depth: float, value: float, 
               quality_flag: str, log_id: int) -> CurveData:
        """创建新的曲线数据点"""
        db_curve = CurveData(
            curve_name=curve_name,
            depth=depth,
            value=value,
            quality_flag=quality_flag,
            log_id=log_id
        )
        db.add(db_curve)
        db.commit()
        db.refresh(db_curve)
        return db_curve

    @staticmethod
    def get_by_log_and_depth(db: Session, log_id: int, depth_from: float, depth_to: float) -> List[CurveData]:
        """获取指定深度范围的曲线数据"""
        return db.query(CurveData).filter(
            CurveData.log_id == log_id,
            CurveData.depth >= depth_from,
            CurveData.depth <= depth_to
        ).all()

    @staticmethod
    def get_by_curve_name(db: Session, log_id: int, curve_name: str) -> List[CurveData]:
        """获取特定曲线的所有数据"""
        return db.query(CurveData).filter(
            CurveData.log_id == log_id,
            CurveData.curve_name == curve_name
        ).order_by(CurveData.depth.asc()).all()

    @staticmethod
    def count_by_log(db: Session, log_id: int) -> int:
        """获取测井数据点数"""
        return db.query(CurveData).filter(CurveData.log_id == log_id).count()

    @staticmethod
    def delete_by_log(db: Session, log_id: int) -> bool:
        """删除一条测井的所有曲线数据"""
        db.query(CurveData).filter(CurveData.log_id == log_id).delete()
        db.commit()
        return True
