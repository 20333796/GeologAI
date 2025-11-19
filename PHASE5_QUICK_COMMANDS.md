# 🚀 Phase 5 快速命令参考

## 启动应用

### 1️⃣ 启动后端服务
```powershell
cd d:\GeologAI\backend
python -m uvicorn app.main:app --reload
```
✅ 访问地址: http://localhost:8000
📚 API 文档: http://localhost:8000/docs

### 2️⃣ 启动前端应用
```powershell
cd d:\GeologAI\web\frontend
streamlit run app.py
```
✅ 访问地址: http://localhost:8501

### 3️⃣ 同时启动（使用 docker-compose）
```powershell
cd d:\GeologAI
docker-compose up -d
```
✅ 所有服务将在后台运行

---

## 推送到 GitHub

### 步骤 1: 选择认证方法

**方法 A: GitHub CLI（推荐）**
```powershell
gh auth login
# 选择：
# - What is your preferred protocol? HTTPS
# - Authenticate with? Login with a web browser
# 完成后可以推送
```

**方法 B: Personal Access Token**
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择 "repo" 权限
4. 复制 token 并保存
5. Git 会提示输入，粘贴 token 即可

**方法 C: SSH 密钥**
```powershell
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 启动 SSH Agent
Start-Service ssh-agent -ErrorAction SilentlyContinue
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# 添加公钥到 GitHub: https://github.com/settings/keys
```

### 步骤 2: 推送代码
```powershell
cd d:\GeologAI
git add .
git commit -m "Phase 5 启动: Streamlit 前端集成"
git push -u origin main
```

### 步骤 3: 验证 CI/CD
访问: https://github.com/USERNAME/GeologAI/actions
等待工作流完成（通常 3-5 分钟）

---

## 开发工作流

### 运行测试
```powershell
cd d:\GeologAI\backend

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_crud.py -v

# 显示覆盖率
python -m pytest tests/ --cov=app --cov-report=html
```

### 查看测试覆盖率报告
```powershell
# 生成 HTML 报告
python -m pytest tests/ --cov=app --cov-report=html

# 打开浏览器查看
start htmlcov\index.html
```

### 检查代码质量
```powershell
# 使用 ruff 检查代码
ruff check app/

# 使用 pylint 检查
pylint app/

# 使用 mypy 类型检查
mypy app/
```

---

## 前端开发

### 编辑 Streamlit 应用
主文件: `web/frontend/app.py`

常用操作:
```python
# 导入 Streamlit
import streamlit as st

# 添加标题
st.title("我的应用")

# 添加输入框
name = st.text_input("输入你的名字")

# 调用后端 API
import requests
response = requests.post("http://localhost:8000/api/users/", json={"name": name})

# 显示结果
st.success(f"响应: {response.json()}")
```

### 重新加载应用
- **自动重载**: 编辑保存后自动重新加载（Streamlit 监听文件变化）
- **手动重载**: 在浏览器中按 `R` 键

---

## 数据库操作

### 连接数据库
```python
# 后端已配置连接字符串
# MySQL: mysql://user:password@localhost/geologai
# SQLite (开发): sqlite:///./test.db
```

### 创建数据表
```powershell
cd d:\GeologAI\backend
python

# 在 Python 交互式环境中
>>> from app.db.database import Base, engine
>>> Base.metadata.create_all(engine)
```

### 查看数据库内容
```powershell
# 使用 SQLite 浏览器（推荐）
sqlite3 test.db
```

---

## 调试

### 启用详细日志
```python
# 在 backend/app/main.py 中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 使用 FastAPI 调试器
```python
# 在 backend/app/main.py 中
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 查看 API 请求/响应
访问 http://localhost:8000/docs 使用 Swagger UI 测试所有 API

---

## Docker

### 构建镜像
```powershell
# 后端镜像
docker build -t geologai-backend backend/

# 前端镜像
docker build -t geologai-frontend web/frontend/
```

### 运行容器
```powershell
# 后端容器
docker run -p 8000:8000 geologai-backend

# 前端容器
docker run -p 8501:8501 geologai-frontend
```

### 清理 Docker 资源
```powershell
# 停止所有容器
docker-compose down

# 删除镜像
docker rmi geologai-backend geologai-frontend
```

---

## 常见问题

### 问题 1: Streamlit 连接不到后端
**解决方案:**
```python
# 确保后端已启动
# 在 web/frontend/app.py 中更改 API URL
BASE_URL = "http://localhost:8000"  # 改为 127.0.0.1 如果 localhost 不工作
```

### 问题 2: 端口已被占用
```powershell
# 查找占用端口的进程
Get-Process | Where-Object { $_.Handles -match "8000" }

# 杀死进程
Stop-Process -Id <PID> -Force

# 或使用其他端口
streamlit run app.py --server.port 8502
```

### 问题 3: 认证失败
```powershell
# 重置 Git 凭证
git config --global --unset credential.helper

# 重新输入凭证
git push -u origin main
```

### 问题 4: pytest 配置错误
```powershell
# 如果遇到 pytest.ini 问题，可以删除它
rm pytest.ini

# 使用命令行参数代替
python -m pytest tests/ --tb=short -v
```

---

## 文件结构参考

```
d:\GeologAI\
├── backend/                 # 后端 FastAPI 应用
│   ├── app/
│   │   ├── main.py         # 主应用
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 数据验证
│   │   ├── crud/           # 数据库操作
│   │   ├── services/       # 业务逻辑
│   │   ├── api/            # API 路由
│   │   ├── db/             # 数据库配置
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试
│   └── requirements.txt     # 依赖
│
├── web/frontend/            # 前端 Streamlit 应用
│   ├── app.py              # 主应用
│   ├── pages/              # 页面
│   ├── components/         # 组件
│   ├── utils/              # 工具函数
│   └── .streamlit/         # 配置
│
├── configs/                 # 配置文件
├── data/                    # 数据目录
├── tests/                   # 集成测试
└── docker-compose.yml       # Docker 配置
```

---

## 性能优化

### 前端性能
```python
# 使用 @st.cache_data 缓存
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

# 使用 @st.cache_resource 缓存资源
@st.cache_resource
def init_model():
    return load_model("model.pkl")
```

### 后端性能
```python
# 使用异步操作
@app.get("/api/data/")
async def get_data():
    # 异步数据库查询
    return await db.query(Data).all()

# 添加缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation():
    pass
```

---

## 更新日志

### Phase 5a (本周)
- ✅ 项目环境设置完成
- ✅ 后端服务验证
- ✅ 前端框架验证
- ⏳ 开始认证页面开发

### Phase 5b (下周)
- ⏳ 项目管理功能
- ⏳ 数据上传功能
- ⏳ 基本可视化

### Phase 5c (第 2 周)
- ⏳ 高级可视化
- ⏳ AI 预测集成
- ⏳ E2E 测试

---

## 获取帮助

### 相关文档
- 📖 `START_HERE.md` - 项目导航
- 📖 `NEXT_STEPS_QUICK_START.md` - 5 分钟快速开始
- 📖 `GITHUB_AUTHENTICATION_GUIDE.md` - GitHub 认证指南
- 📖 `PHASE5_FRONTEND_GUIDE.md` - 前端开发指南
- 📖 `API_QUICK_REFERENCE.md` - API 参考

### 相关资源
- 📚 FastAPI 官方文档: https://fastapi.tiangolo.com
- 📚 Streamlit 官方文档: https://docs.streamlit.io
- 📚 SQLAlchemy 官方文档: https://docs.sqlalchemy.org

---

**最后更新**: 2024 年
**项目**: GeologAI
**阶段**: Phase 5 (Frontend Integration)
**状态**: 🟢 就绪
