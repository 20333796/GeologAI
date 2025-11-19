# GeologAI WebOS - 快速启动指南

## 📋 前提条件

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (可选)
- Node.js 18+ (用于前端)

## 🚀 快速启动 (5分钟)

### 方式 A: 使用 Docker Compose (推荐)

```bash
# 1. 克隆项目
cd D:\GeologAI

# 2. 启动所有服务
docker-compose up -d

# 3. 初始化数据库
docker-compose exec backend python -m app.db.init_db

# 4. 访问应用
# API: http://localhost:8000/api/docs
# 前端: http://localhost:3000
# 管理后台: http://localhost:3001
# 官网: http://localhost:3002
```

### 方式 B: 本地开发环境

#### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
copy .env.example .env

# 编辑 .env 文件，配置数据库连接
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/geologai

# 初始化数据库
python -m app.db.init_db

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 2. 前端设置

```bash
# 进入前端目录
cd ../web/frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

#### 3. 管理后台设置

```bash
# 进入管理后台目录
cd ../../admin

# 安装依赖
npm install

# 启动开发服务器
npm start
```

## 📚 核心功能

### 已实现
- ✅ 完整的数据库设计 (7个表)
- ✅ FastAPI框架
- ✅ JWT认证系统
- ✅ Pydantic数据验证
- ✅ SQLAlchemy ORM
- ✅ Docker容器化
- ✅ Nginx反向代理
- ✅ 前端应用 (Streamlit)

### 待实现
- [ ] CRUD API端点
- [ ] 用户认证端点
- [ ] 文件上传处理
- [ ] AI预测引擎
- [ ] 管理后台UI
- [ ] 官网首页
- [ ] 完整测试套件

## 🔑 默认凭据

### 管理员账户
- 用户名: `admin`
- 密码: `Admin@123456`
- 邮箱: `admin@geologai.com`

## 📁 项目结构

```
GeologAI/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── core/           # 配置、安全
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # 验证模式
│   │   ├── crud/           # 数据库操作
│   │   ├── api/            # API端点
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   ├── db/             # 数据库配置
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── web/
│   ├── frontend/           # Streamlit前端 (现有)
│   └── backend/            # 旧的后端代码
│
├── admin/                  # React管理后台 (待开发)
├── marketing/              # 官网首页 (待开发)
│
├── docker-compose.yml      # Docker编排
├── nginx.conf              # Nginx配置
├── SYSTEM_DESIGN.md        # 系统设计文档
├── REDESIGN_SUMMARY.md     # 重新设计总结
└── README.md              # 项目说明

```

## 🛠️ API 端点示例

### 健康检查
```bash
GET http://localhost:8000/health
```

### API状态
```bash
GET http://localhost:8000/api/v1/status
```

### API文档
```
http://localhost:8000/api/docs
http://localhost:8000/api/redoc
```

## 💾 数据库初始化

```bash
# 方式1: 使用脚本
python -m app.db.init_db

# 方式2: 使用交互式CLI
from app.db.session import init_db
init_db()
```

## 📊 监控和调试

### 查看日志
```bash
# 实时日志
docker-compose logs -f backend

# 查看特定服务
docker-compose logs mysql
docker-compose logs redis
```

### 访问MySQL
```bash
docker-compose exec mysql mysql -u root -p
# 密码: root_password

# 查看数据库
SHOW DATABASES;
USE geologai;
SHOW TABLES;
```

### 访问Redis
```bash
docker-compose exec redis redis-cli

# 查看所有键
KEYS *

# 查看缓存
GET key_name
```

## 🔐 安全建议

1. **生产环境**:
   - 修改 `SECRET_KEY` 在 `.env` 文件
   - 使用强密码
   - 启用HTTPS
   - 配置防火墙

2. **数据库**:
   - 定期备份
   - 使用连接池
   - 启用SSL连接
   - 创建应用专用用户

3. **API**:
   - 启用速率限制
   - 验证所有输入
   - 使用CORS白名单
   - 记录所有操作

## 🐛 故障排除

### 数据库连接错误
```
解决方案:
1. 检查MySQL是否运行: docker-compose ps
2. 验证DATABASE_URL正确性
3. 检查MySQL日志: docker-compose logs mysql
```

### Redis连接错误
```
解决方案:
1. 检查Redis是否运行: docker-compose ps
2. 测试连接: docker-compose exec redis redis-cli ping
3. 查看日志: docker-compose logs redis
```

### 端口冲突
```
解决方案:
1. 修改docker-compose.yml中的端口映射
2. 或使用: lsof -i :8000 (Linux/Mac)
3. netstat -ano | findstr 8000 (Windows)
```

## 📖 文档

- [系统设计文档](./SYSTEM_DESIGN.md)
- [重新设计总结](./REDESIGN_SUMMARY.md)
- [API文档](http://localhost:8000/api/docs)
- [数据库设计](./SYSTEM_DESIGN.md#2-数据库设计)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📝 许可证

MIT License

## 📞 技术支持

如有问题，请:
1. 查看文档
2. 检查日志
3. 提交Issue
