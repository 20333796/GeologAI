"""项目管理API端点"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse
)
from app.crud import ProjectCRUD
from app.core.security import get_current_user, get_current_admin, SecurityUtility
from app.services import ProjectService

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出项目
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **status**: 筛选状态（可选）
    """
    projects = ProjectCRUD.list_projects(db, skip=skip, limit=limit, status=status)
    total = ProjectCRUD.count(db)
    
    return {
        "data": projects,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/my-projects", response_model=ProjectListResponse)
def get_my_projects(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的项目"""
    projects = ProjectCRUD.get_by_owner(db, current_user.id, skip=skip, limit=limit)
    total = ProjectCRUD.count_by_owner(db, current_user.id)
    
    return {
        "data": projects,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    project = ProjectCRUD.get_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 权限检查
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新项目
    
    - **name**: 项目名称
    - **description**: 项目描述
    - **location**: 地理位置
    - **depth_from**: 开始深度
    - **depth_to**: 结束深度
    - **well_diameter**: 井径
    """
    # 使用服务层创建项目
    result = ProjectService.create_project(db, current_user.id, project_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return result.get("project")


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    # 权限检查
    project = ProjectCRUD.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层更新
    result = ProjectService.update_project(db, project_id, project_update)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return result.get("project")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除项目"""
    project = ProjectCRUD.get_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 权限检查
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层删除（包含级联检查）
    result = ProjectService.delete_project(db, project_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return None


@router.patch("/{project_id}/status")
def change_project_status(
    project_id: int,
    status_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """改变项目状态"""
    project = ProjectCRUD.get_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 权限检查
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    status_value = status_data.get("status")
    
    if status_value not in ["active", "archived", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的状态值"
        )
    
    updated_project = ProjectCRUD.change_status(db, project_id, status_value)
    return {
        "id": updated_project.id,
        "name": updated_project.name,
        "status": updated_project.status
    }


@router.get("/{project_id}/stats")
def get_project_stats(
    project_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目统计信息"""
    project = ProjectCRUD.get_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 权限检查
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层获取统计
    result = ProjectService.get_project_statistics(db, project_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return result.get("statistics")
