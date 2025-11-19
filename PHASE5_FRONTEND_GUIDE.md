# 🎨 Phase 5 - Streamlit 前端开发指南

## 📊 项目现状回顾

**已完成** (Phase 1-4):
- ✅ FastAPI 后端框架完整
- ✅ 84/86 核心测试通过
- ✅ 60% 代码覆盖率
- ✅ GitHub Actions CI/CD 配置

**即将开始** (Phase 5):
- 🎨 Streamlit 前端应用
- 🔗 端到端集成测试
- 🐳 Docker Compose 完整栈部署

---

## 🎯 Phase 5 目标

### 功能需求

| 页面 | 功能 | 优先级 |
|------|------|--------|
| **登录/注册** | 用户认证，JWT 令牌管理 | P0 |
| **项目管理** | 创建、查看、编辑、删除项目 | P0 |
| **数据上传** | LAS 文件上传，预处理 | P0 |
| **数据浏览** | 井日志可视化，曲线数据展示 | P1 |
| **预测分析** | 运行 AI 预测，结果查看 | P1 |
| **统计仪表板** | 用户/项目/预测统计 | P1 |
| **用户资料** | 个人信息管理，密码修改 | P2 |

### 技术栈

```
Frontend:
  ├── Streamlit 1.40+        # Web 框架
  ├── Plotly 5.0+            # 交互式图表
  ├── Pandas 2.0+            # 数据处理
  ├── Requests 2.31+         # HTTP 请求
  └── Python 3.10+           # 运行环境

Backend (已有):
  ├── FastAPI 0.100+
  ├── SQLAlchemy 2.0+
  ├── Pydantic 2.0+
  └── PyJWT 2.8+

Deployment:
  ├── Docker Compose          # 容器编排
  ├── Nginx                   # 反向代理
  └── MySQL 8.0+              # 数据库
```

---

## 🚀 快速启动 (15 分钟)

### 步骤 1: 环境检查

```bash
# 激活 Conda 环境
conda activate geologai

# 验证核心包
python -c "import streamlit, plotly, pandas; print('✅ All packages ready')"
```

### 步骤 2: 启动后端服务

#### 方式 A: 直接运行 (开发模式)
```bash
cd d:\GeologAI\backend
python -m uvicorn app.main:app --reload --port 8000
# 访问: http://localhost:8000/docs
```

#### 方式 B: 使用 Docker
```bash
cd d:\GeologAI
docker-compose up -d backend
```

### 步骤 3: 启动 Streamlit 前端

```bash
cd d:\GeologAI\web\frontend
streamlit run app.py --server.port 8501
# 自动打开: http://localhost:8501
```

### 步骤 4: 验证连接

在浏览器中:
1. 访问 http://localhost:8501 (Streamlit 前端)
2. 注册新用户或登录
3. 创建测试项目
4. 上传示例数据

---

## 📁 前端项目结构

### 当前结构

```
web/frontend/
├── app.py                  # 主应用入口
├── .streamlit/
│   └── config.toml        # Streamlit 配置
├── pages/                  # 多页面应用 (新建)
│   ├── 1_Projects.py      # 项目管理
│   ├── 2_Upload.py        # 数据上传
│   ├── 3_Visualize.py     # 数据可视化
│   ├── 4_Predictions.py   # 预测分析
│   └── 5_Dashboard.py     # 统计仪表板
├── utils/                  # 工具模块 (新建)
│   ├── api_client.py      # API 交互
│   ├── auth.py            # 认证管理
│   ├── plotting.py        # 图表绘制
│   └── validators.py      # 数据验证
├── data/                   # 本地数据 (新建)
│   └── sample_las.las     # 示例 LAS 文件
└── requirements.txt        # 依赖列表

### 建议的目录创建

```bash
cd d:\GeologAI\web\frontend

# 创建必要的目录
mkdir pages
mkdir utils
mkdir data
mkdir assets

# 创建空文件作为包
touch pages/__init__.py
touch utils/__init__.py
```

---

## 💻 核心代码实现

### 1. 主应用入口 (app.py)

```python
import streamlit as st
import requests
from utils.auth import login_page, register_page
from utils.api_client import APIClient

# 页面配置
st.set_page_config(
    page_title="GeologAI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# 主页面
def main():
    st.title("🌍 GeologAI - 地质数据智能管理系统")
    
    # 侧边栏
    with st.sidebar:
        st.image("assets/logo.png", width=200)  # 如有 logo
        
        if not st.session_state.logged_in:
            tab1, tab2 = st.tabs(["登录", "注册"])
            
            with tab1:
                login_page()
            
            with tab2:
                register_page()
        else:
            st.write(f"👤 欢迎，{st.session_state.user['username']}")
            
            # 导航菜单
            page = st.radio(
                "📑 导航",
                ["仪表板", "项目", "数据上传", "可视化", "预测分析", "设置"]
            )
            
            if st.button("🚪 退出登录"):
                st.session_state.logged_in = False
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
            
            return page
    
    if not st.session_state.logged_in:
        st.info("👈 请在左侧登录或注册以继续")
    else:
        page = st.session_state.page if "page" in st.session_state else "仪表板"
        
        if page == "仪表板":
            from pages.dashboard import show
            show()
        # ... 其他页面路由

if __name__ == "__main__":
    main()
```

### 2. API 客户端 (utils/api_client.py)

```python
import requests
import streamlit as st
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = st.session_state.get("token")
    
    def _headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, username: str, email: str, password: str, full_name: str) -> Dict:
        """用户注册"""
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        return response.json()
    
    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        return response.json()
    
    def get_projects(self, skip: int = 0, limit: int = 100) -> Dict:
        """获取项目列表"""
        response = requests.get(
            f"{self.base_url}/api/projects?skip={skip}&limit={limit}",
            headers=self._headers()
        )
        return response.json()
    
    def create_project(self, name: str, description: str = "") -> Dict:
        """创建项目"""
        response = requests.post(
            f"{self.base_url}/api/projects",
            json={"name": name, "description": description},
            headers=self._headers()
        )
        return response.json()
    
    def upload_file(self, project_id: int, file_bytes: bytes, filename: str) -> Dict:
        """上传数据文件"""
        files = {"file": (filename, file_bytes)}
        response = requests.post(
            f"{self.base_url}/api/data/upload?project_id={project_id}",
            files=files,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()
    
    def create_prediction(self, well_log_id: int, model_id: int) -> Dict:
        """创建预测"""
        response = requests.post(
            f"{self.base_url}/api/predictions",
            json={"well_log_id": well_log_id, "model_id": model_id},
            headers=self._headers()
        )
        return response.json()

# 单例实例
@st.cache_resource
def get_api_client():
    return APIClient()
```

### 3. 认证页面 (utils/auth.py)

```python
import streamlit as st
from utils.api_client import get_api_client

def login_page():
    """登录页面"""
    st.subheader("🔐 用户登录")
    
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")
    
    if submit:
        if not username or not password:
            st.error("❌ 用户名和密码不能为空")
            return
        
        api = get_api_client()
        try:
            response = api.login(username, password)
            
            if "access_token" in response:
                st.session_state.token = response["access_token"]
                st.session_state.logged_in = True
                st.session_state.user = response.get("user", {"username": username})
                st.success("✅ 登录成功!")
                st.rerun()
            else:
                st.error(f"❌ 登录失败: {response.get('detail', '未知错误')}")
        except Exception as e:
            st.error(f"❌ 错误: {str(e)}")

def register_page():
    """注册页面"""
    st.subheader("📝 用户注册")
    
    with st.form("register_form"):
        username = st.text_input("用户名")
        email = st.text_input("邮箱")
        full_name = st.text_input("真实姓名")
        password = st.text_input("密码", type="password")
        password_confirm = st.text_input("确认密码", type="password")
        submit = st.form_submit_button("注册")
    
    if submit:
        if not all([username, email, full_name, password]):
            st.error("❌ 所有字段都是必需的")
            return
        
        if password != password_confirm:
            st.error("❌ 两次输入的密码不一致")
            return
        
        api = get_api_client()
        try:
            response = api.register(username, email, password, full_name)
            
            if "id" in response:
                st.success("✅ 注册成功! 请使用新账户登录")
            else:
                st.error(f"❌ 注册失败: {response.get('detail', '未知错误')}")
        except Exception as e:
            st.error(f"❌ 错误: {str(e)}")
```

### 4. 项目管理页面 (pages/1_Projects.py)

```python
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import get_api_client

def show():
    st.title("📊 项目管理")
    
    api = get_api_client()
    
    # 两列布局
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("我的项目")
    
    with col2:
        if st.button("➕ 新建项目"):
            st.session_state.show_create_form = not st.session_state.get("show_create_form", False)
    
    # 创建项目表单
    if st.session_state.get("show_create_form"):
        with st.form("create_project"):
            name = st.text_input("项目名称")
            description = st.text_area("项目描述")
            submit = st.form_submit_button("创建")
            
            if submit:
                if not name:
                    st.error("❌ 项目名称不能为空")
                else:
                    try:
                        response = api.create_project(name, description)
                        st.success(f"✅ 项目 '{name}' 创建成功!")
                        st.session_state.show_create_form = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 错误: {str(e)}")
    
    # 项目列表
    try:
        projects = api.get_projects()
        
        if projects:
            df = pd.DataFrame([
                {
                    "项目名": p["name"],
                    "描述": p.get("description", ""),
                    "状态": p.get("status", "active"),
                    "创建时间": p.get("created_at", ""),
                    "操作": "📂 打开"
                }
                for p in projects
            ])
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 暂无项目，请创建新项目")
    except Exception as e:
        st.error(f"❌ 获取项目列表失败: {str(e)}")

if __name__ == "__main__":
    show()
```

---

## 📦 依赖安装

### 更新 requirements.txt

```txt
# 已有 (后端)
fastapi==0.100.0
uvicorn==0.24.0
sqlalchemy==2.0.21
pydantic==2.4.2
pydantic-settings==2.0.3
pymysql==1.1.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.0

# 前端
streamlit==1.40.0
plotly==5.17.0
pandas==2.1.3
requests==2.31.0
python-dateutil==2.8.2

# 测试
pytest==7.4.3
pytest-cov==4.1.0
```

### 安装依赖

```bash
pip install -r web/frontend/requirements.txt
```

---

## 🧪 本地测试工作流

### 1. 启动完整栈

```bash
# 终端 1: 启动后端
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 终端 2: 启动前端
cd web/frontend
streamlit run app.py --server.port 8501

# 终端 3: 可选 - 运行数据库 (如需本地 MySQL)
# docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0
```

### 2. 测试用户流程

```
1. 访问 http://localhost:8501
2. 点击 "注册"
3. 填写表单:
   - 用户名: testuser
   - 邮箱: test@example.com
   - 密码: TestPass123!
4. 点击 "注册"
5. 使用新账户登录
6. 创建项目
7. 上传示例 LAS 文件
8. 查看数据和预测
```

### 3. 常见问题排查

| 问题 | 解决方案 |
|------|--------|
| **连接被拒绝** | 确保后端在 8000 端口运行: `python -m uvicorn app.main:app --reload --port 8000` |
| **Streamlit 缓存问题** | 清除缓存: `streamlit cache clear` |
| **CORS 错误** | 后端已配置 CORS，前端需配置相同的 base_url |
| **文件上传失败** | 检查 multipart 依赖: `pip install python-multipart` |

---

## 🎨 UI/UX 最佳实践

### 1. 页面导航
```python
# 使用 Streamlit 的多页面应用
# pages/ 目录中的每个 .py 文件都变成一个页面
# 自动在侧边栏显示导航
```

### 2. 数据可视化
```python
import plotly.express as px
import plotly.graph_objects as go

# 例: 绘制井日志曲线
fig = px.line(df, x="depth", y="porosity", title="孔隙度曲线")
st.plotly_chart(fig, use_container_width=True)
```

### 3. 会话状态管理
```python
# 保存认证状态
st.session_state.logged_in = True
st.session_state.token = "jwt_token"
st.session_state.user = {"id": 1, "username": "user"}

# 在页面重新加载时保留状态
```

---

## 📊 开发进度跟踪

### 第 1 周: 基础框架
- [ ] 项目结构搭建
- [ ] 认证页面实现
- [ ] API 客户端封装
- [ ] 基本路由配置

### 第 2 周: 核心功能
- [ ] 项目管理页面
- [ ] 数据上传功能
- [ ] 数据浏览展示
- [ ] 预测分析页面

### 第 3 周: 高级功能
- [ ] 统计仪表板
- [ ] 可视化增强
- [ ] 用户资料管理
- [ ] 错误处理和日志

### 第 4 周: 测试和部署
- [ ] 端到端集成测试
- [ ] Docker Compose 配置
- [ ] 性能优化
- [ ] 文档完善

---

## 🚀 下一步命令

```bash
# 准备前端开发
cd d:\GeologAI\web\frontend

# 创建必要目录
mkdir -p pages utils data assets

# 创建包文件
touch pages/__init__.py
touch utils/__init__.py

# 启动开发环境
streamlit run app.py --server.port 8501
```

---

**预计完成时间**: 2-3 周  
**下一个里程碑**: 完整的前端应用 + 端到端测试通过

