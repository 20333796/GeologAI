# GeologAI WebOS 系统设计文档

## 1. 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                        │
├──────────────────┬──────────────────┬──────────────────────┤
│  官网首页         │   主应用平台      │   管理后台            │
│  (Marketing)     │   (Platform)     │   (Admin)            │
└──────────────────┼──────────────────┼──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    API网关层 (Gateway)                      │
│  - 路由转发  - 认证授权  - 限流降级  - 日志监控             │
└─────────────────────────────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 用户服务 │  │ 项目服务 │  │ 数据服务 │
│(Auth)    │  │(Project) │  │(Data)    │
└──────────┘  └──────────┘  └──────────┘
      │            │            │
      ├────────────┼────────────┤
      │            ▼            │
      │   ┌──────────────┐      │
      │   │   业务逻辑   │      │
      │   │   服务层      │      │
      │   └──────────────┘      │
      │            │            │
      └────────────┼────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              数据访问层 (Data Access Layer)                 │
│  ORM (SQLAlchemy) - 缓存 (Redis) - 搜索 (Elasticsearch)    │
└─────────────────────────────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
   ┌──────┐    ┌──────┐     ┌──────────┐
   │ 数据库│    │ 缓存  │    │ 文件存储  │
   │(MySQL)    │(Redis)     │ (OSS)    │
   └──────┘    └──────┘     └──────────┘
```

## 2. 数据库设计

### 2.1 核心表结构

```sql
-- 用户表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    avatar_url VARCHAR(255),
    phone VARCHAR(20),
    role ENUM('admin', 'manager', 'user') DEFAULT 'user',
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 项目表
CREATE TABLE projects (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    owner_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    depth_from FLOAT,
    depth_to FLOAT,
    well_diameter FLOAT,
    status ENUM('planning', 'ongoing', 'completed') DEFAULT 'planning',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 测井数据表
CREATE TABLE well_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_id BIGINT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512),
    file_size BIGINT,
    depth_from FLOAT,
    depth_to FLOAT,
    sample_count INT,
    curves_json JSON,
    upload_user_id BIGINT,
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (upload_user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 曲线数据表
CREATE TABLE curve_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    log_id BIGINT NOT NULL,
    curve_name VARCHAR(50),
    depth FLOAT,
    value FLOAT,
    quality_flag TINYINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES well_logs(id),
    KEY idx_log_depth (log_id, depth)
) ENGINE=InnoDB;

-- AI模型表
CREATE TABLE ai_models (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    description TEXT,
    model_type ENUM('predictor', 'classifier', 'analyzer') DEFAULT 'predictor',
    accuracy FLOAT,
    model_path VARCHAR(512),
    parameters_json JSON,
    creator_id BIGINT,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 预测结果表
CREATE TABLE predictions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    log_id BIGINT NOT NULL,
    model_id BIGINT NOT NULL,
    depth_from FLOAT,
    depth_to FLOAT,
    results_json JSON,
    confidence FLOAT,
    execution_time INT,
    status ENUM('success', 'failed') DEFAULT 'success',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES well_logs(id),
    FOREIGN KEY (model_id) REFERENCES ai_models(id)
) ENGINE=InnoDB;

-- 操作日志表
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id BIGINT,
    changes_json JSON,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    KEY idx_user_time (user_id, created_at)
) ENGINE=InnoDB;
```

## 3. 模块功能划分

### 3.1 用户认证模块 (auth)
- 用户注册、登录、登出
- JWT令牌管理
- 密码重置、修改
- 社交登录（可选）

### 3.2 用户管理模块 (user)
- 个人信息管理
- 头像上传
- 权限管理
- 团队管理

### 3.3 项目管理模块 (project)
- 项目CRUD
- 项目共享
- 项目统计
- 数据导出

### 3.4 数据管理模块 (data)
- LAS文件上传
- 数据解析
- 数据校验
- 数据预览

### 3.5 分析预测模块 (analysis)
- 曲线分析
- AI预测
- 结果展示
- 报告生成

### 3.6 系统管理模块 (admin)
- 用户管理
- 系统配置
- 日志查看
- 模型管理

## 4. API设计规范

### 4.1 URL规范
```
/api/v1/{resource}          GET    获取列表
/api/v1/{resource}          POST   创建
/api/v1/{resource}/{id}     GET    获取单个
/api/v1/{resource}/{id}     PUT    完全更新
/api/v1/{resource}/{id}     PATCH  部分更新
/api/v1/{resource}/{id}     DELETE 删除
```

### 4.2 响应格式
```json
{
    "code": 200,
    "message": "Success",
    "data": {},
    "timestamp": "2025-11-19T12:00:00Z"
}
```

### 4.3 错误处理
```json
{
    "code": 400,
    "message": "Bad Request",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ]
}
```

## 5. 技术栈

### 后端
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- MySQL 8.0+
- Redis 7.0+
- PyJWT

### 前端
- React 18+ / Next.js
- TypeScript
- Tailwind CSS
- Axios
- Zustand/Redux

### 前端管理后台
- React Admin / Ant Design Pro
- ECharts for visualization

### DevOps
- Docker & Docker Compose
- Nginx (反向代理)
- GitHub Actions CI/CD

## 6. 文件夹结构（最终）

```
GeologAI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI应用
│   │   ├── config.py            # 配置管理
│   │   ├── dependencies.py      # 依赖注入
│   │   ├── middleware.py        # 中间件
│   │   ├── security.py          # 安全认证
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # 应用配置
│   │   │   ├── security.py      # JWT及密码处理
│   │   │   └── settings.py      # 环境变量
│   │   │
│   │   ├── models/              # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── data.py
│   │   │   ├── model.py
│   │   │   └── prediction.py
│   │   │
│   │   ├── schemas/             # Pydantic模式
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── data.py
│   │   │   └── prediction.py
│   │   │
│   │   ├── crud/                # 数据库操作
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── data.py
│   │   │   └── prediction.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── api_v1.py
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── projects.py
│   │   │       ├── data.py
│   │   │       ├── predictions.py
│   │   │       └── admin.py
│   │   │
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   ├── project_service.py
│   │   │   ├── data_service.py
│   │   │   ├── prediction_service.py
│   │   │   └── file_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── las_parser.py
│   │   │   ├── excel_parser.py
│   │   │   ├── validators.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   │
│   │   └── logs/
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   ├── .env
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── styles/
│   │   └── App.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── admin/                      # 管理后台
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── dashboard/
│   │   │   ├── users/
│   │   │   ├── projects/
│   │   │   ├── models/
│   │   │   └── system/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── marketing/                  # 官网
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── home/
│   │   │   ├── features/
│   │   │   ├── pricing/
│   │   │   ├── about/
│   │   │   └── contact/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── nginx.conf
├── README.md
├── SYSTEM_DESIGN.md
├── API_DOCS.md
└── DEPLOYMENT.md
```

## 7. 开发路线图

### Phase 1: 核心基础设施 (Week 1-2)
- [ ] 项目结构重构
- [ ] 数据库设计和初始化
- [ ] FastAPI基础框架
- [ ] 认证系统

### Phase 2: 用户和项目管理 (Week 3-4)
- [ ] 用户管理模块
- [ ] 项目管理模块
- [ ] 权限系统

### Phase 3: 数据管理和分析 (Week 5-6)
- [ ] 文件上传模块
- [ ] 数据解析服务
- [ ] 曲线分析功能

### Phase 4: AI预测功能 (Week 7-8)
- [ ] AI模型集成
- [ ] 预测引擎
- [ ] 结果管理

### Phase 5: 前端应用 (Week 9-10)
- [ ] 主应用UI
- [ ] 管理后台UI
- [ ] 官网首页

### Phase 6: 部署和优化 (Week 11-12)
- [ ] Docker容器化
- [ ] 性能优化
- [ ] 文档完善
