# GeologAI WebOS - 项目概览

## 🎯 项目目标

打造一个功能完善的地球物理测井AI分析WebOS系统，包括:
- ✅ 完整的后端API服务
- ✅ 功能丰富的主应用平台
- ✅ 专业的管理后台
- ✅ 营销型官网首页
- ✅ 完整的数据库和缓存系统
- ✅ 企业级的认证和权限管理

## 🏗️ 系统架构

### 微服务架构设计

```
┌─────────────────────────────────────────────────────────────┐
│              前端层 - 三个独立应用                            │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ 官网首页     │ 主应用平台   │ 管理后台                 │ │
│  │ Marketing    │ Platform     │ Admin                    │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────┬─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│           API网关 (Nginx)                                   │
│  - 路由转发   - 负载均衡   - SSL/TLS   - 性能优化           │
└────────┬─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│       后端服务层 - FastAPI (Python)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API v1                                               │  │
│  │ ├─ /auth       (认证服务)                           │  │
│  │ ├─ /users      (用户管理)                           │  │
│  │ ├─ /projects   (项目管理)                           │  │
│  │ ├─ /data       (数据管理)                           │  │
│  │ ├─ /predictions(AI预测)                            │  │
│  │ └─ /admin      (系统管理)                           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────┬─────────────────────────────────────────────────────┘
         │
      ┌──┴──┬──────┬──────────┐
      ▼     ▼      ▼          ▼
   ┌────┐┌────┐┌────────┐┌──────────┐
   │MySQL││Redis││文件系统││消息队列│
   │数据库││缓存 ││OSS   ││MQ      │
   └────┘└────┘└────────┘└──────────┘
```

## 📊 数据库设计 (7个核心表)

### 1. users (用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| username | VARCHAR | 用户名 |
| email | VARCHAR | 邮箱 |
| password_hash | VARCHAR | 密码哈希 |
| role | ENUM | 角色(admin/manager/user) |
| status | ENUM | 状态(active/inactive/banned) |

### 2. projects (项目表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| owner_id | BIGINT | 所有者ID |
| name | VARCHAR | 项目名称 |
| location | VARCHAR | 地点 |
| depth_from/to | FLOAT | 深度范围 |
| status | ENUM | 状态 |

### 3. well_logs (测井数据表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| project_id | BIGINT | 项目ID |
| filename | VARCHAR | 文件名 |
| file_path | VARCHAR | 文件路径 |
| curves_json | JSON | 曲线信息 |
| status | ENUM | 处理状态 |

### 4. curve_data (曲线数据表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| log_id | BIGINT | 日志ID |
| curve_name | VARCHAR | 曲线名 |
| depth | FLOAT | 深度 |
| value | FLOAT | 数值 |

### 5. ai_models (模型表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| name | VARCHAR | 模型名称 |
| version | VARCHAR | 版本 |
| model_type | VARCHAR | 模型类型 |
| accuracy | FLOAT | 精度 |
| status | ENUM | 状态 |

### 6. predictions (预测结果表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| log_id | BIGINT | 日志ID |
| model_id | BIGINT | 模型ID |
| results_json | JSON | 结果 |
| confidence | FLOAT | 置信度 |
| status | ENUM | 状态 |

### 7. audit_logs (审计日志表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| action | VARCHAR | 操作 |
| resource_type | VARCHAR | 资源类型 |
| changes_json | JSON | 变更内容 |

## 🛠️ 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.104+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.0+ | 数据验证 |
| MySQL | 8.0+ | 关系数据库 |
| Redis | 7.0+ | 缓存 |
| PyJWT | 2.8+ | JWT认证 |
| Passlib | 1.7+ | 密码加密 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18+ | UI框架 |
| TypeScript | 5+ | 类型安全 |
| Next.js | 14+ | SSR框架 |
| Tailwind CSS | 3+ | 样式框架 |
| Axios | 1.6+ | HTTP客户端 |
| Zustand | 4+ | 状态管理 |

### 现有前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Streamlit | 1.51+ | 数据应用 |
| Plotly | 6.3+ | 数据可视化 |
| NumPy | 2.2+ | 数据处理 |

### DevOps
| 技术 | 版本 | 用途 |
|------|------|------|
| Docker | 24+ | 容器化 |
| Docker Compose | 2+ | 容器编排 |
| Nginx | 1.25+ | 反向代理 |
| GitHub Actions | - | CI/CD |

## 📈 功能模块

### 1. 认证系统 (Auth)
- ✅ 用户注册/登录
- ✅ JWT令牌管理
- ✅ 权限验证
- ✅ 角色控制
- ✅ 密码重置

### 2. 用户管理 (User)
- 个人资料管理
- 头像上传
- 团队管理
- 权限配置

### 3. 项目管理 (Project)
- 项目CRUD
- 项目共享
- 统计分析
- 数据导出

### 4. 数据管理 (Data)
- LAS文件上传
- 数据解析
- 数据校验
- 数据预览

### 5. 分析预测 (Analysis)
- 曲线分析
- AI预测
- 结果展示
- 报告生成

### 6. 系统管理 (Admin)
- 用户管理
- 系统配置
- 日志查看
- 模型管理

## 📦 已创建的文件

```
✅ backend/
   ├── app/
   │   ├── core/
   │   │   ├── settings.py          # 配置管理
   │   │   └── security.py          # 认证系统
   │   ├── models/
   │   │   └── __init__.py          # SQLAlchemy模型 (7个)
   │   ├── schemas/
   │   │   └── __init__.py          # Pydantic Schema (20+)
   │   ├── crud/                    # 数据库操作层
   │   ├── api/endpoints/           # API端点
   │   ├── services/                # 业务逻辑
   │   ├── utils/                   # 工具函数
   │   ├── db/
   │   │   ├── session.py           # 数据库连接
   │   │   └── init_db.py           # 初始化脚本
   │   └── main.py                  # FastAPI应用
   ├── requirements.txt             # 依赖
   ├── .env.example                 # 环境变量示例
   └── Dockerfile                   # 容器配置

✅ 基础设施
   ├── docker-compose.yml           # Docker编排
   ├── nginx.conf                   # Nginx配置
   ├── SYSTEM_DESIGN.md             # 系统设计
   ├── REDESIGN_SUMMARY.md          # 重新设计总结
   └── QUICKSTART.md                # 快速启动指南
```

## 🚀 快速开始

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库
```

### 3. 初始化数据库
```bash
python -m app.db.init_db
```

### 4. 启动服务
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. 访问应用
- API文档: http://localhost:8000/api/docs
- API状态: http://localhost:8000/api/v1/status
- 健康检查: http://localhost:8000/health

## 📝 开发计划

### Week 1 (本周)
- ✅ 系统架构设计
- ✅ 数据库设计
- ✅ 后端项目结构
- [ ] CRUD层实现
- [ ] API端点实现

### Week 2
- [ ] 业务逻辑服务
- [ ] 文件上传处理
- [ ] AI预测集成
- [ ] 数据缓存

### Week 3
- [ ] React主应用
- [ ] React管理后台
- [ ] 官网首页

### Week 4
- [ ] 完整测试
- [ ] 部署配置
- [ ] 文档完善

## 🔑 默认账户

| 项 | 值 |
|----|----|
| 用户名 | admin |
| 密码 | Admin@123456 |
| 邮箱 | admin@geologai.com |
| 角色 | admin |

## 📚 文档

| 文档 | 说明 |
|------|------|
| SYSTEM_DESIGN.md | 完整系统设计文档 |
| REDESIGN_SUMMARY.md | 重新设计总结 |
| QUICKSTART.md | 快速启动指南 |
| API文档 | /api/docs (Swagger) |

## 🎨 系统特性

- ✅ **微服务架构** - 模块化设计，易于扩展
- ✅ **完整认证** - JWT + 角色权限管理
- ✅ **企业级数据库** - MySQL + Redis + 缓存策略
- ✅ **规范API设计** - RESTful + 版本管理
- ✅ **容器化部署** - Docker + Docker Compose
- ✅ **反向代理** - Nginx负载均衡
- ✅ **数据验证** - Pydantic自动验证
- ✅ **自动文档** - Swagger UI + ReDoc

## 🤝 技术支持

需要帮助？
1. 查看 QUICKSTART.md
2. 查看 SYSTEM_DESIGN.md
3. 查看 API文档 (/api/docs)
4. 检查日志文件

## 📞 联系方式

- 技术支持: support@geologai.com
- 官方网站: https://geologai.com
- GitHub: https://github.com/geologai/webos

---

**GeologAI WebOS - 地球物理测井AI分析平台**  
版本: 1.0.0 | 最后更新: 2025年11月19日
