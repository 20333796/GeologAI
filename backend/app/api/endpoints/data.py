"""数据管理API端点"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import json

from app.db.session import get_db
from app.schemas import (
    WellLogResponse, WellLogCreate, WellLogUpdate, 
    WellLogListResponse, CurveDataResponse
)
from app.crud import WellLogCRUD, CurveDataCRUD, ProjectCRUD
from app.core.security import get_current_user, get_current_admin, SecurityUtility
from app.services import DataService

router = APIRouter(prefix="/api/v1/data", tags=["data"])


@router.get("/logs", response_model=WellLogListResponse)
def list_logs(
    skip: int = 0,
    limit: int = 10,
    project_id: int = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出测井数据
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **project_id**: 项目ID（可选，筛选特定项目）
    """
    if project_id:
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
        
        logs = WellLogCRUD.get_by_project(db, project_id, skip=skip, limit=limit)
        total = WellLogCRUD.count_by_project(db, project_id)
    else:
        logs = WellLogCRUD.list_logs(db, skip=skip, limit=limit)
        total = WellLogCRUD.count(db)
    
    return {
        "data": logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/logs/{log_id}", response_model=WellLogResponse)
def get_log(
    log_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测井数据详情"""
    log = WellLogCRUD.get_by_id(db, log_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测井数据不存在"
        )
    
    # 权限检查
    project = ProjectCRUD.get_by_id(db, log.project_id)
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return log


@router.post("/logs", response_model=WellLogResponse, status_code=status.HTTP_201_CREATED)
def create_log(
    project_id: int,
    log_data: WellLogCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传新的测井数据
    
    - **project_id**: 项目ID
    - **filename**: 文件名
    - **file_path**: 文件路径
    - **file_size**: 文件大小
    - **depth_from**: 开始深度
    - **depth_to**: 结束深度
    - **sample_count**: 样本数
    - **curves_json**: 曲线数据（JSON格式）
    """
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
    
    # 使用服务层创建测井数据
    result = DataService.upload_well_log(db, project_id, log_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return result.get("log")


@router.put("/logs/{log_id}", response_model=WellLogResponse)
def update_log(
    log_id: int,
    log_update: WellLogUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新测井数据"""
    log = WellLogCRUD.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测井数据不存在"
        )
    
    # 权限检查
    project = ProjectCRUD.get_by_id(db, log.project_id)
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    updated_log = WellLogCRUD.update(db, log_id, log_update)
    return updated_log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除测井数据"""
    log = WellLogCRUD.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测井数据不存在"
        )
    
    # 权限检查
    project = ProjectCRUD.get_by_id(db, log.project_id)
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层删除（级联删除相关数据）
    result = DataService.delete_log_with_data(db, log_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return None


@router.get("/logs/{log_id}/curves")
def get_log_curves(
    log_id: int,
    depth_from: float = None,
    depth_to: float = None,
    curve_name: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测井的曲线数据
    
    - **depth_from**: 深度起点（可选）
    - **depth_to**: 深度终点（可选）
    - **curve_name**: 曲线名称（可选）
    """
    log = WellLogCRUD.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测井数据不存在"
        )
    
    # 权限检查
    project = ProjectCRUD.get_by_id(db, log.project_id)
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    if curve_name:
        curves = CurveDataCRUD.get_by_curve_name(db, log_id, curve_name)
    elif depth_from is not None and depth_to is not None:
        curves = CurveDataCRUD.get_by_log_and_depth(db, log_id, depth_from, depth_to)
    else:
        curves = []
    
    return {
        "log_id": log_id,
        "curve_count": len(curves),
        "curves": curves
    }


@router.post("/logs/{log_id}/curves")
def add_curve_data(
    log_id: int,
    curve_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加曲线数据点
    
    - **curve_name**: 曲线名称
    - **depth**: 深度
    - **value**: 数值
    - **quality_flag**: 质量标志
    """
    log = WellLogCRUD.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测井数据不存在"
        )
    
    # 权限检查
    project = ProjectCRUD.get_by_id(db, log.project_id)
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    try:
        new_curve = CurveDataCRUD.create(
            db,
            curve_data["curve_name"],
            curve_data["depth"],
            curve_data["value"],
            curve_data.get("quality_flag", "good"),
            log_id
        )
        return {
            "id": new_curve.id,
            "message": "曲线数据已添加"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加曲线数据失败"
        )
