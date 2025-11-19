================================================================================
                        GeologAI API 快速参考指南
                        Quick Reference Guide for API
================================================================================

🔐 认证流程
================================================================================

1. 用户注册
   POST /api/v1/auth/register
   {
       "username": "user123",
       "email": "user@example.com",
       "password": "SecurePass123",
       "real_name": "张三"
   }
   
   响应:
   {
       "id": 1,
       "username": "user123",
       "email": "user@example.com",
       "role": "user",
       "status": "active"
   }

2. 用户登录
   POST /api/v1/auth/login
   {
       "username": "user123",    // 或 email
       "password": "SecurePass123"
   }
   
   响应:
   {
       "access_token": "eyJhbGc...",
       "refresh_token": "eyJhbGc...",
       "token_type": "bearer",
       "user": { ... }
   }

3. 使用访问令牌 (所有后续请求)
   Headers:
   Authorization: Bearer eyJhbGc...

4. 刷新令牌
   POST /api/v1/auth/refresh
   {
       "refresh_token": "eyJhbGc..."
   }
   
   响应:
   {
       "access_token": "new_token",
       "token_type": "bearer"
   }

================================================================================
📊 项目管理工作流
================================================================================

1. 创建项目
   POST /api/v1/projects
   {
       "name": "华东油田井1234",
       "description": "测试项目",
       "location": "上海浦东",
       "depth_from": 0.0,
       "depth_to": 3000.0,
       "well_diameter": 0.3
   }

2. 获取用户的项目列表
   GET /api/v1/projects/my-projects?skip=0&limit=10

3. 获取项目详情
   GET /api/v1/projects/{project_id}

4. 更新项目
   PUT /api/v1/projects/{project_id}
   {
       "description": "更新后的描述"
   }

5. 获取项目统计
   GET /api/v1/projects/{project_id}/stats

6. 改变项目状态 (active, archived, completed)
   PATCH /api/v1/projects/{project_id}/status
   {
       "status": "archived"
   }

================================================================================
📁 数据管理工作流
================================================================================

1. 上传测井数据
   POST /api/v1/data/logs?project_id=1
   {
       "filename": "well_1234.las",
       "file_path": "/data/uploads/well_1234.las",
       "file_size": 102400,
       "depth_from": 0.0,
       "depth_to": 3000.0,
       "sample_count": 3000,
       "curves_json": {
           "curves": ["GR", "ILD", "SP"]
       }
   }

2. 获取项目的测井数据
   GET /api/v1/data/logs?project_id=1&skip=0&limit=10

3. 获取特定测井的曲线数据
   GET /api/v1/data/logs/{log_id}/curves

4. 获取深度范围内的曲线数据
   GET /api/v1/data/logs/{log_id}/curves?depth_from=100&depth_to=200

5. 获取特定曲线的所有数据
   GET /api/v1/data/logs/{log_id}/curves?curve_name=GR

6. 添加曲线数据点
   POST /api/v1/data/logs/{log_id}/curves
   {
       "curve_name": "GR",
       "depth": 150.5,
       "value": 75.3,
       "quality_flag": "good"
   }

================================================================================
🤖 AI 预测工作流
================================================================================

1. 创建预测任务
   POST /api/v1/predictions
   {
       "log_id": 1,
       "model_id": 1,
       "results_json": {
           "predicted_lithology": "sandstone",
           "confidence": 0.95
       },
       "confidence": 0.95,
       "execution_time": 2.5
   }

2. 获取预测结果列表
   GET /api/v1/predictions?skip=0&limit=10

3. 获取测井的所有预测
   GET /api/v1/predictions?log_id=1

4. 获取模型的所有预测
   GET /api/v1/predictions?model_id=1

5. 获取预测详情
   GET /api/v1/predictions/{prediction_id}

6. 重新运行预测
   POST /api/v1/predictions/{prediction_id}/rerun

7. 获取预测统计
   GET /api/v1/predictions/{prediction_id}/stats

================================================================================
👥 用户管理工作流 (仅管理员)
================================================================================

1. 获取所有用户
   GET /api/v1/users?skip=0&limit=10

2. 按角色筛选用户
   GET /api/v1/users?role=admin

3. 按状态筛选用户
   GET /api/v1/users?status=active

4. 获取用户详情
   GET /api/v1/users/{user_id}

5. 更新用户信息
   PUT /api/v1/users/{user_id}
   {
       "real_name": "新名字",
       "phone": "13800138000"
   }

6. 改变用户状态
   PATCH /api/v1/users/{user_id}/status
   {
       "status": "suspended"  // active, inactive, suspended
   }

7. 重置用户密码
   POST /api/v1/admin/users/{user_id}/reset-password
   {
       "new_password": "NewPassword123"
   }

8. 删除用户
   DELETE /api/v1/users/{user_id}

================================================================================
⚙️  管理后台功能 (仅管理员)
================================================================================

1. 获取系统统计
   GET /api/v1/admin/stats
   
   响应:
   {
       "users": 10,
       "projects": 5,
       "logs": 25,
       "models": 3,
       "predictions": 100
   }

2. 获取所有用户 (分页、筛选)
   GET /api/v1/admin/users?skip=0&limit=20

3. 获取所有项目
   GET /api/v1/admin/projects?skip=0&limit=20

4. 获取所有模型
   GET /api/v1/admin/models?skip=0&limit=20

5. 创建新模型
   POST /api/v1/admin/models
   {
       "name": "lithology_v1",
       "version": "1.0.0",
       "model_type": "classification",
       "accuracy": 0.92,
       "model_path": "/models/lithology_v1.pkl",
       "parameters_json": {
           "algorithm": "RandomForest",
           "n_trees": 100
       }
   }

6. 系统健康检查
   GET /api/v1/admin/health
   
   响应:
   {
       "status": "ok",
       "database": "healthy",
       "timestamp": "2025-11-19T10:30:00"
   }

7. 清理旧预测记录
   DELETE /api/v1/admin/clean-old-predictions?days=30
   
   删除超过30天的预测记录

8. 获取审计日志
   POST /api/v1/admin/audit-logs?skip=0&limit=20

================================================================================
🛠️  常见请求示例
================================================================================

使用 curl 命令:

# 1. 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123",
    "real_name": "Test User"
  }'

# 2. 登录获取令牌
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'

# 3. 使用令牌获取用户信息
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. 创建项目
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Project",
    "description": "Project description",
    "location": "Beijing"
  }'

# 5. 获取项目列表
curl -X GET "http://localhost:8000/api/v1/projects/my-projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

================================================================================
📝 HTTP 状态码说明
================================================================================

200 OK
    请求成功，返回数据

201 Created
    资源创建成功

204 No Content
    请求成功，但无返回内容（如删除操作）

400 Bad Request
    请求参数错误或验证失败

401 Unauthorized
    需要身份验证或令牌无效

403 Forbidden
    权限不足，无法访问该资源

404 Not Found
    请求的资源不存在

422 Unprocessable Entity
    请求数据验证失败，返回详细错误信息

500 Internal Server Error
    服务器内部错误

================================================================================
🔍 调试技巧
================================================================================

1. 查看 API 文档
   http://localhost:8000/api/docs (Swagger UI)
   http://localhost:8000/api/redoc (ReDoc)

2. 查看应用状态
   GET http://localhost:8000/api/v1/status

3. 健康检查
   GET http://localhost:8000/health

4. 查看日志
   # 在应用启动的终端查看实时日志

5. 测试 API
   - 使用 Postman 或 Insomnia 导入 /api/docs 的 OpenAPI 规范
   - 使用 curl 命令行工具测试
   - 在浏览器中访问 /api/docs 进行交互式测试

================================================================================
⚠️  常见错误和解决方案
================================================================================

问题: 401 Unauthorized
原因: 缺少或无效的令牌
解决: 
  1. 确保添加了 Authorization header
  2. 检查令牌是否过期
  3. 尝试使用 refresh_token 获取新令牌

问题: 403 Forbidden
原因: 权限不足
解决:
  1. 确认当前用户的角色
  2. 只有项目所有者或管理员可以修改/删除
  3. 某些操作仅管理员可用

问题: 422 Unprocessable Entity
原因: 请求数据验证失败
解决:
  1. 查看返回的 errors 字段，了解具体验证失败原因
  2. 检查必填字段是否提供
  3. 检查数据类型和格式是否正确

问题: 404 Not Found
原因: 资源不存在
解决:
  1. 检查资源 ID 是否正确
  2. 确认资源尚未被删除
  3. 验证权限（可能无法访问他人的资源）

问题: 500 Internal Server Error
原因: 服务器内部错误
解决:
  1. 查看服务器日志了解详细错误信息
  2. 检查数据库连接
  3. 确保所有依赖服务都在运行

================================================================================
📞 获取帮助
================================================================================

1. 查看完整文档
   - SYSTEM_DESIGN.md - 系统设计文档
   - QUICKSTART.md - 快速启动指南
   - README.md - 项目概览
   - PHASE1_COMPLETION.md - 本阶段完成情况

2. API 交互式文档
   http://localhost:8000/api/docs

3. 查看源代码
   backend/app/api/endpoints/ - API 端点实现
   backend/app/crud/ - 数据库操作
   backend/app/schemas/ - 数据验证模型

================================================================================
                    Happy API Testing! 🚀
================================================================================
