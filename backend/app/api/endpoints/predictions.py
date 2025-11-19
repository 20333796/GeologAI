"""预测管理API端点"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.db.session import get_db
from app.schemas import (
    PredictionResponse, PredictionCreate, PredictionUpdate,
    PredictionListResponse
)
from app.crud import PredictionCRUD, WellLogCRUD, AIModelCRUD, ProjectCRUD
from app.core.security import get_current_user, get_current_admin, SecurityUtility
from app.services import PredictionService

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.get("", response_model=PredictionListResponse)
def list_predictions(
    skip: int = 0,
    limit: int = 10,
    log_id: int = None,
    model_id: int = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出预测结果
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **log_id**: 测井ID（可选）
    - **model_id**: 模型ID（可选）
    """
    if log_id:
        predictions = PredictionCRUD.get_by_log(db, log_id, skip=skip, limit=limit)
        total = PredictionCRUD.count_by_log(db, log_id)
    elif model_id:
        predictions = PredictionCRUD.get_by_model(db, model_id, skip=skip, limit=limit)
        total = PredictionCRUD.count_by_model(db, model_id)
    else:
        predictions = PredictionCRUD.list_predictions(db, skip=skip, limit=limit)
        total = PredictionCRUD.count(db)
    
    return {
        "data": predictions,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预测结果详情"""
    prediction = PredictionCRUD.get_by_id(db, prediction_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预测结果不存在"
        )
    
    # 权限检查
    log = WellLogCRUD.get_by_id(db, prediction.log_id)
    project = ProjectCRUD.get_by_id(db, log.project_id)
    
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return prediction


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    prediction_data: PredictionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的预测任务
    
    - **log_id**: 测井数据ID
    - **model_id**: AI模型ID
    - **results_json**: 预测结果（JSON格式）
    - **confidence**: 置信度（0-1）
    - **execution_time**: 执行时间（秒）
    """
    # 权限检查
    log = WellLogCRUD.get_by_id(db, prediction_data.log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测井数据不存在"
        )
    
    project = ProjectCRUD.get_by_id(db, log.project_id)
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层创建预测
    result = PredictionService.create_prediction(db, prediction_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return result.get("prediction")


@router.put("/{prediction_id}", response_model=PredictionResponse)
def update_prediction(
    prediction_id: int,
    prediction_update: PredictionUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新预测结果（仅管理员）"""
    prediction = PredictionCRUD.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预测结果不存在"
        )
    
    updated_prediction = PredictionCRUD.update(db, prediction_id, prediction_update)
    return updated_prediction


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
    prediction_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除预测结果（仅管理员）"""
    prediction = PredictionCRUD.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预测结果不存在"
        )
    
    PredictionCRUD.delete(db, prediction_id)
    return None


@router.post("/{prediction_id}/rerun")
def rerun_prediction(
    prediction_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新运行预测
    
    这个端点会创建一个新的预测任务，基于已有预测的参数。
    """
    prediction = PredictionCRUD.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预测结果不存在"
        )
    
    # 权限检查
    log = WellLogCRUD.get_by_id(db, prediction.log_id)
    project = ProjectCRUD.get_by_id(db, log.project_id)
    
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层重新运行预测
    result = PredictionService.rerun_prediction(db, prediction_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return {
        "old_prediction_id": prediction_id,
        "new_prediction_id": result.get("new_prediction").id,
        "message": result.get("message")
    }


@router.get("/{prediction_id}/stats")
def get_prediction_stats(
    prediction_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预测统计信息"""
    prediction = PredictionCRUD.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预测结果不存在"
        )
    
    # 权限检查
    log = WellLogCRUD.get_by_id(db, prediction.log_id)
    project = ProjectCRUD.get_by_id(db, log.project_id)
    
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    model = AIModelCRUD.get_by_id(db, prediction.model_id)
    
    return {
        "prediction_id": prediction_id,
        "log_id": prediction.log_id,
        "model_name": model.name,
        "confidence": prediction.confidence,
        "execution_time": prediction.execution_time,
        "status": prediction.status,
        "created_at": prediction.created_at
    }
