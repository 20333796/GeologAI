"""管理后台API端点"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user, get_current_admin, SecurityUtility
from app.crud import UserCRUD, ProjectCRUD, WellLogCRUD, AIModelCRUD, PredictionCRUD

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
def get_system_stats(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取系统统计信息（仅管理员）"""
    users_count = UserCRUD.count(db)
    projects_count = ProjectCRUD.count(db)
    logs_count = WellLogCRUD.count(db)
    models_count = AIModelCRUD.count(db)
    predictions_count = PredictionCRUD.count(db)
    
    return {
        "users": users_count,
        "projects": projects_count,
        "logs": logs_count,
        "models": models_count,
        "predictions": predictions_count
    }


@router.get("/users")
def get_all_users(
    skip: int = 0,
    limit: int = 10,
    role: str = None,
    status: str = None,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有用户（仅管理员）"""
    users = UserCRUD.list_users(db, skip=skip, limit=limit, role=role, status=status)
    total = UserCRUD.count(db)
    
    return {
        "data": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/projects")
def get_all_projects(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有项目（仅管理员）"""
    projects = ProjectCRUD.list_projects(db, skip=skip, limit=limit, status=status)
    total = ProjectCRUD.count(db)
    
    return {
        "data": projects,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/models")
def get_all_models(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有AI模型（仅管理员）"""
    models = AIModelCRUD.list_models(db, skip=skip, limit=limit)
    total = AIModelCRUD.count(db)
    
    return {
        "data": models,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/models")
def create_ai_model(
    model_data: dict,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建新的AI模型（仅管理员）
    
    - **name**: 模型名称
    - **version**: 模型版本
    - **model_type**: 模型类型（classification, regression等）
    - **accuracy**: 精确度
    - **model_path**: 模型路径
    - **parameters_json**: 模型参数（JSON格式）
    """
    try:
        from app.schemas import AIModelCreate
        
        model_create = AIModelCreate(
            name=model_data["name"],
            version=model_data["version"],
            model_type=model_data["model_type"],
            accuracy=model_data.get("accuracy", 0.0),
            model_path=model_data["model_path"],
            parameters_json=model_data.get("parameters_json", {})
        )
        
        new_model = AIModelCRUD.create(db, model_create)
        return {
            "id": new_model.id,
            "name": new_model.name,
            "message": "模型已创建"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建模型失败"
        )


@router.get("/health")
def system_health(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取系统健康状态（仅管理员）"""
    try:
        # 测试数据库连接
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = "unhealthy"
    
    return {
        "status": "ok",
        "database": db_status,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    password_data: dict,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """重置用户密码（仅管理员）
    
    - **new_password**: 新密码
    """
    user = UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    from app.schemas import UserUpdate
    
    new_password = password_data.get("new_password")
    if not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少新密码"
        )
    
    user_update = UserUpdate(password=new_password)
    updated_user = UserCRUD.update(db, user_id, user_update)
    
    return {
        "user_id": user_id,
        "username": updated_user.username,
        "message": "密码已重置"
    }


@router.delete("/clean-old-predictions")
def clean_old_predictions(
    days: int = 30,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """清理旧的预测结果（仅管理员）
    
    - **days**: 保留天数（默认30天）
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # 删除旧预测
        deleted_count = db.query(PredictionCRUD).filter(
            PredictionCRUD.created_at < cutoff_date
        ).delete()
        db.commit()
        
        return {
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "message": f"已删除{deleted_count}条旧预测"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清理失败"
        )


@router.post("/audit-logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取审计日志（仅管理员）"""
    # 这是一个占位符实现
    # 实际应该查询 AuditLog 表
    
    return {
        "data": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "message": "审计日志功能待实现"
    }
