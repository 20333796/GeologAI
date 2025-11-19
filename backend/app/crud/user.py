"""用户数据库操作层"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import SecurityUtility


class UserCRUD:
    """用户数据库操作"""

    @staticmethod
    def create(db: Session, user: UserCreate) -> User:
        """创建新用户"""
        db_user = User(
            username=user.username,
            email=user.email,
            real_name=user.real_name,
            password_hash=SecurityUtility.hash_password(user.password),
            role="user",  # 默认角色为 user
            status="active"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def list_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[User]:
        """列出用户"""
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if status:
            query = query.filter(User.status == status)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取用户总数"""
        return db.query(User).count()

    @staticmethod
    def update(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        # 如果更新密码，需要加密
        if "password" in update_data:
            update_data["password_hash"] = SecurityUtility.hash_password(update_data.pop("password"))
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """删除用户"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def change_status(db: Session, user_id: int, status: str) -> Optional[User]:
        """改变用户状态"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.status = status
        db.commit()
        db.refresh(db_user)
        return db_user
