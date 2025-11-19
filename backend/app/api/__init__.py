"""API端点初始化和路由注册"""

from fastapi import APIRouter
from app.api.endpoints import auth, users, projects, data, predictions, admin

# 创建主路由器
api_router = APIRouter()

# 注册认证端点
api_router.include_router(auth.router)

# 注册用户端点
api_router.include_router(users.router)

# 注册项目端点
api_router.include_router(projects.router)

# 注册数据管理端点
api_router.include_router(data.router)

# 注册预测端点
api_router.include_router(predictions.router)

# 注册管理端点
api_router.include_router(admin.router)
