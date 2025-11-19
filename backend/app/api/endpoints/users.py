"""用户管理API端点"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas import (
    UserResponse, UserUpdate, UserListResponse, PaginationParams
)
from app.crud import UserCRUD
from app.core.security import get_current_user, get_current_admin
from app.services import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def list_users(
    skip: int = 0,
    limit: int = 10,
    role: str = None,
    status: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出用户
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **role**: 筛选角色（可选）
    - **status**: 筛选状态（可选）
    """
    users = UserCRUD.list_users(db, skip=skip, limit=limit, role=role, status=status)
    total = UserCRUD.count(db)
    
    return {
        "data": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    user = UserCRUD.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息
    
    - 普通用户只能更新自己的信息
    - 管理员可以更新任何用户信息
    """
    # 权限检查
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 使用服务层更新用户
    result = UserService.update_user_profile(db, user_id, user_update)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return result.get("user")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    db_user = UserCRUD.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    UserCRUD.delete(db, user_id)
    return None


@router.patch("/{user_id}/status")
def change_user_status(
    user_id: int,
    status_data: dict,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """改变用户状态（仅管理员）
    
    - **status**: 新状态（active, inactive, suspended）
    """
    status_value = status_data.get("status")
    
    if status_value not in ["active", "inactive", "suspended"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的状态值"
        )
    
    db_user = UserCRUD.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    updated_user = UserCRUD.change_status(db, user_id, status_value)
    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "status": updated_user.status
    }


@router.post("/{user_id}/change-password")
def change_password(
    user_id: int,
    password_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码
    
    - 用户只能修改自己的密码
    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")
    
    if not old_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要参数"
        )
    
    # 使用服务层更改密码
    result = UserService.change_password(db, user_id, old_password, new_password)
    
    if not result.get("success"):
        if result.get("error") == "invalid_password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message")
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    
    return {
        "message": "密码已更新"
    }
