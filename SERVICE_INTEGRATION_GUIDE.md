# Service 层集成快速指南

## 快速查询表

### Service 返回格式（统一）

所有 Service 方法返回标准格式：

```python
{
    "success": bool,           # 操作是否成功
    "error": str,              # 错误代码（失败时）
    "message": str,            # 用户友好的消息
    "data" or "[field]": any   # 具体数据（成功时）
}
```

### API 端点映射

| API 端点 | Service 方法 | 功能 |
|---------|-------------|------|
| `POST /api/v1/users/register` | `UserService.register_user()` | 用户注册 |
| `POST /api/v1/auth/login` | `UserService.authenticate_user()` | 用户登录 |
| `PUT /api/v1/users/{id}` | `UserService.update_user_profile()` | 更新用户资料 |
| `POST /api/v1/users/{id}/change-password` | `UserService.change_password()` | 修改密码 |
| `POST /api/v1/projects` | `ProjectService.create_project()` | 创建项目 |
| `PUT /api/v1/projects/{id}` | `ProjectService.update_project()` | 更新项目 |
| `DELETE /api/v1/projects/{id}` | `ProjectService.delete_project()` | 删除项目 |
| `GET /api/v1/projects/{id}/stats` | `ProjectService.get_project_statistics()` | 项目统计 |
| `POST /api/v1/data/logs` | `DataService.upload_well_log()` | 上传测井 |
| `DELETE /api/v1/data/logs/{id}` | `DataService.delete_log_with_data()` | 删除测井 |
| `POST /api/v1/predictions` | `PredictionService.create_prediction()` | 创建预测 |
| `POST /api/v1/predictions/{id}/rerun` | `PredictionService.rerun_prediction()` | 重新运行预测 |

---

## Service 层 API 参考

### UserService

```python
from app.services import UserService

# 注册用户
result = UserService.register_user(
    db=db,
    username="john_doe",
    email="john@example.com",
    password="SecurePass123!",
    full_name="John Doe"
)
# 返回: {"success": true, "user": User, "message": "..."}

# 认证用户
result = UserService.authenticate_user(
    db=db,
    username="john_doe",
    password="SecurePass123!"
)
# 返回: {"success": true, "token": "jwt_token", "user": User}

# 获取用户资料
result = UserService.get_user_profile(db=db, user_id=1)
# 返回: {"success": true, "user": {...}, "stats": {...}}

# 更新用户资料
from app.schemas import UserUpdate
result = UserService.update_user_profile(
    db=db,
    user_id=1,
    user_update=UserUpdate(full_name="John Updated")
)
# 返回: {"success": true, "user": User}

# 修改密码
result = UserService.change_password(
    db=db,
    user_id=1,
    old_password="OldPass123!",
    new_password="NewPass456!"
)
# 返回: {"success": true, "message": "..."}

# 获取用户统计
result = UserService.get_user_statistics(db=db, user_id=1)
# 返回: {"success": true, "statistics": {...}}

# 禁用账户
result = UserService.deactivate_account(db=db, user_id=1)
# 返回: {"success": true, "message": "..."}
```

### ProjectService

```python
from app.services import ProjectService
from app.schemas import ProjectCreate, ProjectUpdate

# 创建项目
result = ProjectService.create_project(
    db=db,
    user_id=1,
    project_data=ProjectCreate(
        name="Project Name",
        description="Description",
        location="Beijing, China",
        depth_from=0.0,
        depth_to=3000.0,
        well_diameter=200.0
    )
)
# 返回: {"success": true, "project": Project}

# 获取项目详情
result = ProjectService.get_project_details(db=db, project_id=1)
# 返回: {"success": true, "project": {...}}

# 更新项目
result = ProjectService.update_project(
    db=db,
    project_id=1,
    project_update=ProjectUpdate(description="Updated")
)
# 返回: {"success": true, "project": Project}

# 删除项目
result = ProjectService.delete_project(db=db, project_id=1)
# 返回: {"success": true, "message": "..."} 或 {"success": false, "error": "project_has_data"}

# 获取项目统计
result = ProjectService.get_project_statistics(db=db, project_id=1)
# 返回: {"success": true, "statistics": {...}}

# 存档项目
result = ProjectService.archive_project(db=db, project_id=1)
# 返回: {"success": true, "message": "..."}

# 完成项目
result = ProjectService.complete_project(db=db, project_id=1)
# 返回: {"success": true, "message": "..."}

# 列出用户项目
result = ProjectService.list_user_projects(
    db=db,
    user_id=1,
    skip=0,
    limit=10
)
# 返回: {"success": true, "projects": [...], "count": 10}
```

### DataService

```python
from app.services import DataService
from app.schemas import WellLogCreate

# 上传测井数据
result = DataService.upload_well_log(
    db=db,
    project_id=1,
    log_data=WellLogCreate(
        filename="well_log.las",
        file_path="/uploads/well_log.las",
        file_size=102400,
        depth_from=0.0,
        depth_to=3000.0
    )
)
# 返回: {"success": true, "log": WellLog}

# 获取日志摘要
result = DataService.get_log_summary(db=db, log_id=1)
# 返回: {"success": true, "summary": {...}}

# 删除测井及关联数据
result = DataService.delete_log_with_data(db=db, log_id=1)
# 返回: {"success": true, "message": "..."}

# 分析日志统计
result = DataService.analyze_log_statistics(db=db, log_id=1)
# 返回: {"success": true, "statistics": {...}}

# 获取曲线数据范围
result = DataService.get_curve_data_range(
    db=db,
    log_id=1,
    depth_from=100.0,
    depth_to=500.0
)
# 返回: {"success": true, "data": [...]}

# 批量导入曲线
result = DataService.batch_import_curves(
    db=db,
    log_id=1,
    curve_data_list=[
        {"depth": 100.0, "curve_name": "GR", "value": 50.5},
        {"depth": 100.1, "curve_name": "GR", "value": 51.2},
        ...
    ]
)
# 返回: {"success": true, "imported": 100, "failed": 0}

# 导出测井数据
result = DataService.export_log_data(
    db=db,
    log_id=1,
    format="json"
)
# 返回: {"success": true, "data": {...}}
```

### PredictionService

```python
from app.services import PredictionService
from app.schemas import PredictionCreate

# 创建预测
result = PredictionService.create_prediction(
    db=db,
    prediction_data=PredictionCreate(
        log_id=1,
        model_id=1,
        results_json='{"prediction": [...]}',
        confidence=0.92,
        execution_time=5.2
    )
)
# 返回: {"success": true, "prediction": Prediction}

# 获取预测详情
result = PredictionService.get_prediction_details(db=db, prediction_id=1)
# 返回: {"success": true, "prediction": {...}}

# 重新运行预测
result = PredictionService.rerun_prediction(db=db, prediction_id=1)
# 返回: {"success": true, "new_prediction": Prediction}

# 获取测井的预测列表
result = PredictionService.get_log_predictions(db=db, log_id=1)
# 返回: {"success": true, "predictions": [...], "count": 5}

# 获取模型统计
result = PredictionService.get_model_statistics(db=db, model_id=1)
# 返回: {"success": true, "statistics": {...}}

# 比较预测结果
result = PredictionService.compare_predictions(
    db=db,
    log_id=1,
    model_ids=[1, 2, 3]
)
# 返回: {"success": true, "comparison": [...]}

# 删除预测
result = PredictionService.delete_prediction(db=db, prediction_id=1)
# 返回: {"success": true, "message": "..."}
```

### FileParserService

```python
from app.services import FileParserService

# 检测文件类型
result = FileParserService.detect_file_type(
    filename="well_log.las",
    file_content=file_bytes
)
# 返回: {"type": "LAS", "detected": true}

# 智能解析文件
result = FileParserService.parse_file(
    filename="well_log.las",
    file_content=file_bytes
)
# 返回: {"success": true, "file_type": "LAS", "curves": [...]}

# 解析LAS文件
result = FileParserService.parse_las_file(file_content)
# 返回: {"success": true, "curves": [...], "data_points": 1000}

# 解析CSV文件
result = FileParserService.parse_csv_file(file_content)
# 返回: {"success": true, "headers": [...], "data": [...]}

# 解析Excel文件
result = FileParserService.parse_excel_file(
    file_content,
    sheet_name="Sheet1"
)
# 返回: {"success": true, "sheets": [...], "data": [...]}

# 验证数据结构
result = FileParserService.validate_data_structure(parsed_data)
# 返回: {"valid": true, "message": "数据结构验证通过"}
```

---

## 错误代码参考

### 常见错误代码

| 错误代码 | HTTP状态 | 含义 | 处理方式 |
|---------|---------|------|---------|
| `user_exists` | 400 | 用户已存在 | 使用不同的用户名或邮箱 |
| `user_not_found` | 404 | 用户不存在 | 确认用户ID |
| `invalid_password` | 401 | 密码错误 | 确认密码 |
| `user_inactive` | 403 | 账户已禁用 | 联系管理员 |
| `project_exists` | 400 | 项目已存在 | 使用不同的项目名称 |
| `project_not_found` | 404 | 项目不存在 | 确认项目ID |
| `project_has_data` | 400 | 项目有关联数据 | 先删除关联数据 |
| `log_not_found` | 404 | 测井不存在 | 确认测井ID |
| `file_too_large` | 413 | 文件过大 | 文件大小限制100MB |
| `model_inactive` | 400 | 模型已禁用 | 激活模型后重试 |
| `invalid_confidence` | 400 | 置信度无效 | 置信度必须在0-1之间 |

---

## 常见集成模式

### 模式1：简单CRUD操作

```python
@router.post("", status_code=201)
def create_resource(data: CreateSchema, db: Session = Depends(get_db)):
    result = ResourceService.create_resource(db, data)
    
    if not result.get("success"):
        raise HTTPException(400, result.get("message"))
    
    return result.get("resource")
```

### 模式2：带权限检查的操作

```python
@router.put("/{resource_id}")
def update_resource(
    resource_id: int,
    data: UpdateSchema,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 先检查权限
    resource = get_resource(db, resource_id)
    if resource.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "权限不足")
    
    # 再调用Service
    result = ResourceService.update_resource(db, resource_id, data)
    
    if not result.get("success"):
        raise HTTPException(400, result.get("message"))
    
    return result.get("resource")
```

### 模式3：复杂操作

```python
@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    current_user = Depends(get_current_admin),  # 仅管理员
    db: Session = Depends(get_db)
):
    # 直接调用Service（Service进行业务验证）
    result = ResourceService.delete_resource(db, resource_id)
    
    # 根据错误类型返回不同的状态码
    if not result.get("success"):
        error_code = result.get("error")
        
        if error_code == "not_found":
            raise HTTPException(404, result.get("message"))
        elif error_code == "has_related_data":
            raise HTTPException(400, result.get("message"))
        else:
            raise HTTPException(500, "内部错误")
    
    return {"message": result.get("message")}
```

---

## 调试技巧

### 1. 打印Service返回结果

```python
result = UserService.create_user(db, user_data)
print(f"Success: {result.get('success')}")
print(f"Error: {result.get('error')}")
print(f"Message: {result.get('message')}")
print(f"Data: {result.get('user')}")
```

### 2. 检查服务日志

```bash
# Service层记录详细的日志
# 查看 app.log 文件
tail -f app.log | grep "UserService"
```

### 3. 单元测试Service

```python
def test_service_method():
    db = TestingSessionLocal()
    result = UserService.create_user(db, user_data)
    
    assert result.get("success") == True
    assert result.get("user") is not None
    
    db.close()
```

---

## 性能优化建议

### 1. 缓存统计结果

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_project_statistics_cached(project_id: int):
    # 缓存统计结果5分钟
    ...
```

### 2. 批量操作

```python
# 批量导入而不是逐条导入
result = DataService.batch_import_curves(db, log_id, curve_list)
# 比多次调用 upload_curve() 更高效
```

### 3. 使用异步处理

```python
# 对于耗时操作，考虑异步处理
@router.post("/predictions", background_tasks=BackgroundTasks)
def create_prediction_async(background_tasks: BackgroundTasks, ...):
    result = PredictionService.create_prediction(...)
    
    # 异步执行耗时的AI模型
    background_tasks.add_task(run_prediction_model, result.get("prediction").id)
    
    return result
```

---

## 常见问题

### Q: 为什么我的Service调用没有返回错误信息？
A: 检查Service是否正确初始化，确保传入的参数正确。查看日志文件获取详细错误信息。

### Q: Service返回success=False，但没有error字段？
A: 所有Service方法都应该返回完整的结构。如果缺少字段，可能是代码bug。提交Issue。

### Q: 如何在多个请求中保持上下文（如当前用户）？
A: 使用FastAPI的Depends注入机制：
```python
current_user = Depends(SecurityUtility.get_current_user)
```

### Q: 数据库事务如何处理？
A: Service层使用SQLAlchemy的会话自动处理事务。异常时自动回滚。

---

## 更新日志

- **2024-XX-XX**: 初始版本 - 5个Service类、35个方法、11个端点集成
