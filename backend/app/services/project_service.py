"""项目业务逻辑服务"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate
from app.crud import ProjectCRUD, UserCRUD, WellLogCRUD
from app.core.security import SecurityUtility

logger = logging.getLogger(__name__)


class ProjectService:
    """项目业务逻辑服务"""

    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, user_id: int) -> Dict[str, Any]:
        """创建项目 - 业务逻辑处理"""
        # 验证用户存在
        user = UserCRUD.get_by_id(db, user_id)
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        # 检查项目名称是否重复
        existing_project = db.query(Project).filter(
            Project.name == project_data.name,
            Project.owner_id == user_id
        ).first()
        
        if existing_project:
            return {
                "success": False,
                "error": "project_exists",
                "message": f"项目'{project_data.name}'已存在"
            }

        # 创建项目
        try:
            new_project = ProjectCRUD.create(db, project_data, user_id)
            logger.info(f"项目已创建: {new_project.name} (ID: {new_project.id}, Owner: {user.username})")
            
            return {
                "success": True,
                "project": new_project,
                "message": "项目创建成功"
            }
        except Exception as e:
            logger.error(f"项目创建失败: {str(e)}")
            return {
                "success": False,
                "error": "creation_failed",
                "message": "项目创建失败"
            }

    @staticmethod
    def get_project_details(db: Session, project_id: int) -> Dict[str, Any]:
        """获取项目详细信息"""
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        # 获取关联数据
        logs_count = WellLogCRUD.count_by_project(db, project_id)
        owner = UserCRUD.get_by_id(db, project.owner_id)

        return {
            "success": True,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "location": project.location,
                "depth_from": project.depth_from,
                "depth_to": project.depth_to,
                "well_diameter": project.well_diameter,
                "owner": {
                    "id": owner.id,
                    "username": owner.username,
                    "real_name": owner.real_name
                } if owner else None,
                "status": project.status,
                "logs_count": logs_count,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            },
            "message": "获取项目成功"
        }

    @staticmethod
    def update_project(db: Session, project_id: int, update_data: ProjectUpdate = None, project_update: ProjectUpdate = None) -> Dict[str, Any]:
        """更新项目信息

        支持使用参数名 `update_data` 或 `project_update`（tests 使用 `project_update`）。
        """
        if project_update and not update_data:
            update_data = project_update
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        try:
            updated_project = ProjectCRUD.update(db, project_id, update_data)
            logger.info(f"项目已更新: {project.name} (ID: {project_id})")
            
            return {
                "success": True,
                "project": updated_project,
                "message": "项目更新成功"
            }
        except Exception as e:
            logger.error(f"项目更新失败: {str(e)}")
            return {
                "success": False,
                "error": "update_failed",
                "message": "项目更新失败"
            }

    @staticmethod
    def delete_project(db: Session, project_id: int) -> Dict[str, Any]:
        """删除项目"""
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        # 检查是否有关联的测井数据
        logs_count = WellLogCRUD.count_by_project(db, project_id)
        if logs_count > 0:
            return {
                "success": False,
                "error": "project_has_data",
                "message": f"项目包含 {logs_count} 条测井数据，请先删除数据",
                "logs_count": logs_count
            }

        try:
            ProjectCRUD.delete(db, project_id)
            logger.info(f"项目已删除: {project.name} (ID: {project_id})")
            
            return {
                "success": True,
                "message": "项目删除成功"
            }
        except Exception as e:
            logger.error(f"项目删除失败: {str(e)}")
            return {
                "success": False,
                "error": "deletion_failed",
                "message": "项目删除失败"
            }

    @staticmethod
    def get_project_statistics(db: Session, project_id: int) -> Dict[str, Any]:
        """获取项目统计信息"""
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        logs_count = WellLogCRUD.count_by_project(db, project_id)

        return {
            "success": True,
            "statistics": {
                "project_id": project_id,
                "name": project.name,
                "location": project.location,
                "depth_range": {
                    "from": project.depth_from,
                    "to": project.depth_to
                },
                "logs_count": logs_count,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            },
            "message": "获取统计成功"
        }

    @staticmethod
    def archive_project(db: Session, project_id: int) -> Dict[str, Any]:
        """归档项目"""
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        if project.status == "archived":
            return {
                "success": False,
                "error": "already_archived",
                "message": "项目已归档"
            }

        try:
            ProjectCRUD.change_status(db, project_id, "archived")
            logger.info(f"项目已归档: {project.name} (ID: {project_id})")
            
            return {
                "success": True,
                "message": "项目已归档"
            }
        except Exception as e:
            logger.error(f"项目归档失败: {str(e)}")
            return {
                "success": False,
                "error": "archival_failed",
                "message": "项目归档失败"
            }

    @staticmethod
    def complete_project(db: Session, project_id: int) -> Dict[str, Any]:
        """完成项目"""
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {
                "success": False,
                "error": "project_not_found",
                "message": "项目不存在"
            }

        if project.status == "completed":
            return {
                "success": False,
                "error": "already_completed",
                "message": "项目已完成"
            }

        try:
            ProjectCRUD.change_status(db, project_id, "completed")
            logger.info(f"项目已完成: {project.name} (ID: {project_id})")
            
            return {
                "success": True,
                "message": "项目已完成"
            }
        except Exception as e:
            logger.error(f"项目完成失败: {str(e)}")
            return {
                "success": False,
                "error": "completion_failed",
                "message": "项目完成失败"
            }

    @staticmethod
    def list_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """列出用户的所有项目"""
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        projects = ProjectCRUD.get_by_owner(db, user_id, skip=skip, limit=limit)
        total = ProjectCRUD.count_by_owner(db, user_id)

        return {
            "success": True,
            "projects": projects,
            "total": total,
            "skip": skip,
            "limit": limit,
            "message": "获取项目列表成功"
        }
