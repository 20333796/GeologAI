"""项目数据库操作层"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Project, ProjectStatus
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectCRUD:
    """项目数据库操作"""

    @staticmethod
    def create(db: Session, project: ProjectCreate, owner_id: int) -> Project:
        """创建新项目"""
        db_project = Project(
            name=project.name,
            description=project.description,
            location=project.location,
            depth_from=project.depth_from,
            depth_to=project.depth_to,
            well_diameter=project.well_diameter,
            owner_id=owner_id,
            status=ProjectStatus.PLANNING
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        """通过ID获取项目"""
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 10) -> List[Project]:
        """获取用户的所有项目"""
        return db.query(Project).filter(
            Project.owner_id == owner_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def list_projects(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[Project]:
        """列出项目"""
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == status)
        
        return query.offset(skip).limit(limit).order_by(Project.created_at.desc()).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取项目总数"""
        return db.query(Project).count()

    @staticmethod
    def update(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        """更新项目"""
        db_project = ProjectCRUD.get_by_id(db, project_id)
        if not db_project:
            return None
        
        update_data = project_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_project, key, value)
        
        db_project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def delete(db: Session, project_id: int) -> bool:
        """删除项目"""
        db_project = ProjectCRUD.get_by_id(db, project_id)
        if not db_project:
            return False
        
        db.delete(db_project)
        db.commit()
        return True

    @staticmethod
    def change_status(db: Session, project_id: int, status: str) -> Optional[Project]:
        """改变项目状态"""
        db_project = ProjectCRUD.get_by_id(db, project_id)
        if not db_project:
            return None
        
        db_project.status = status
        db_project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def count_by_owner(db: Session, owner_id: int) -> int:
        """获取用户项目数"""
        return db.query(Project).filter(Project.owner_id == owner_id).count()
