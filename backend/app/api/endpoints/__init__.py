"""API端点子模块初始化"""

from app.api.endpoints import auth, users, projects, data, predictions, admin

__all__ = [
    "auth",
    "users", 
    "projects",
    "data",
    "predictions",
    "admin"
]
