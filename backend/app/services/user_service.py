"""用户业务逻辑服务"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.crud import UserCRUD
from app.core.security import SecurityUtility

logger = logging.getLogger(__name__)


class UserService:
    """用户业务逻辑服务"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate = None, **kwargs) -> Dict[str, Any]:
        """注册新用户 - 业务逻辑处理

        支持直接传入 UserCreate 对象，或通过关键字参数（例如 username/email/password/full_name）调用。
        """
        # 检查用户名是否已存在
        # 支持 kwargs 风格调用（tests 使用 username/email/password/full_name）
        if kwargs:
            # 兼容 full_name -> real_name
            if "full_name" in kwargs and "real_name" not in kwargs:
                kwargs["real_name"] = kwargs.pop("full_name")
            try:
                user_data = UserCreate(**kwargs)
            except Exception:
                return {"success": False, "error": "invalid_input", "message": "无效的用户数据"}

        existing_username = UserCRUD.get_by_username(db, user_data.username)
        if existing_username:
            return {"success": False, "error": "user_exists", "message": "用户名已被使用"}

        # 检查邮箱是否已注册
        existing_email = UserCRUD.get_by_email(db, user_data.email)
        if existing_email:
            return {"success": False, "error": "email_exists", "message": "邮箱已被注册"}

        # 创建用户
        try:
            new_user = UserCRUD.create(db, user_data)
            logger.info(f"新用户注册: {new_user.username} ({new_user.email})")
            
            return {"success": True, "user": new_user, "message": "用户注册成功"}
        except Exception as e:
            logger.error(f"用户注册失败: {str(e)}")
            return {
                "success": False,
                "error": "registration_failed",
                "message": "注册过程出错"
            }

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Dict[str, Any]:
        """用户认证 - 业务逻辑处理"""
        # 查询用户
        user = UserCRUD.get_by_username(db, username)
        if not user:
            # 尝试按邮箱查询
            user = UserCRUD.get_by_email(db, username)

        if not user:
            logger.warning(f"登录失败 - 用户不存在: {username}")
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        # 验证密码
        if not SecurityUtility.verify_password(password, user.password_hash):
            logger.warning(f"登录失败 - 密码错误: {username}")
            return {
                "success": False,
                "error": "invalid_password",
                "message": "密码错误"
            }

        # 检查账户状态
        if user.status != "active":
            logger.warning(f"登录失败 - 账户被禁用: {username} (状态: {user.status})")
            return {
                "success": False,
                "error": "account_disabled",
                "message": "账户已被禁用"
            }

        # 更新最后登录时间
        try:
            user.last_login = datetime.utcnow()
            db.commit()
        except Exception as e:
            logger.error(f"更新最后登录时间失败: {str(e)}")

        logger.info(f"用户登录成功: {username}")

        # 生成访问 token 并返回
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else user.role
        }
        token = SecurityUtility.create_access_token(payload)

        return {"success": True, "user": user, "token": token, "message": "登录成功"}

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户完整资料"""
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "real_name": user.real_name,
                "phone": getattr(user, 'phone', None),
                "role": user.role,
                "status": user.status,
                "avatar_url": getattr(user, 'avatar_url', None),
                "last_login": user.last_login,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            "message": "获取资料成功"
        }

    @staticmethod
    def update_user_profile(db: Session, user_id: int, update_data: UserUpdate) -> Dict[str, Any]:
        """更新用户资料"""
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        try:
            updated_user = UserCRUD.update(db, user_id, update_data)
            logger.info(f"用户资料已更新: {user.username}")
            
            return {
                "success": True,
                "user": updated_user,
                "message": "资料更新成功"
            }
        except Exception as e:
            logger.error(f"更新用户资料失败: {str(e)}")
            return {
                "success": False,
                "error": "update_failed",
                "message": "更新失败"
            }

    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改用户密码"""
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        # 验证旧密码
        if not SecurityUtility.verify_password(old_password, user.password_hash):
            logger.warning(f"密码修改失败 - 旧密码错误: {user.username}")
            return {"success": False, "error": "invalid_password", "message": "旧密码错误"}

        # 检查新密码是否与旧密码相同
        if old_password == new_password:
            return {
                "success": False,
                "error": "same_password",
                "message": "新密码不能与旧密码相同"
            }

        # 更新密码
        try:
            update_data = UserUpdate(password=new_password)
            UserCRUD.update(db, user_id, update_data)
            logger.info(f"用户密码已修改: {user.username}")
            
            return {
                "success": True,
                "message": "密码修改成功"
            }
        except Exception as e:
            logger.error(f"密码修改失败: {str(e)}")
            return {
                "success": False,
                "error": "password_change_failed",
                "message": "密码修改失败"
            }

    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户统计信息"""
        from app.crud import ProjectCRUD, WellLogCRUD, PredictionCRUD
        
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        # 获取统计数据
        projects_count = ProjectCRUD.count_by_owner(db, user_id)
        
        return {
            "success": True,
            "statistics": {
                "user_id": user_id,
                "username": user.username,
                "projects_count": projects_count,
                "role": user.role,
                "status": user.status,
                "joined_at": user.created_at
            },
            "message": "获取统计成功"
        }

    @staticmethod
    def deactivate_account(db: Session, user_id: int) -> Dict[str, Any]:
        """停用用户账户"""
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "用户不存在"
            }

        try:
            UserCRUD.change_status(db, user_id, "inactive")
            logger.info(f"用户账户已停用: {user.username}")
            
            return {
                "success": True,
                "message": "账户已停用"
            }
        except Exception as e:
            logger.error(f"停用账户失败: {str(e)}")
            return {
                "success": False,
                "error": "deactivation_failed",
                "message": "停用失败"
            }
