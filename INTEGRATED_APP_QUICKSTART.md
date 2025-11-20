# 🌍 GeologAI 集成应用 - 快速开始指南

## 📋 应用概述

GeologAI 已从多页面应用重构为**单页面集成应用**，所有功能集成在一个统一的界面中。

### ✨ 核心功能

| 功能 | 描述 |
|------|------|
| 🔐 **认证** | 用户登录/注册 |
| 📊 **概览** | 平台统计、活动日志 |
| 📁 **项目管理** | 创建、查看、管理项目 |
| 💾 **数据管理** | 上传、查看、管理测井数据 |
| 🔍 **数据分析** | 数据预处理、分析、预测 |

---

## 🚀 快速启动

### 方法1：使用批处理文件（Windows推荐）
```bash
# 直接双击运行
D:\GeologAI\start_integrated_app.bat
```

### 方法2：命令行启动
```bash
# 激活环境
conda activate geologai

# 启动后端（一个终端）
cd D:\GeologAI\backend
python run_backend.py

# 启动前端（另一个终端）
cd D:\GeologAI
streamlit run web/frontend/app.py --server.port 8501 --logger.level=error
```

### 方法3：使用 Python 启动脚本
```bash
conda activate geologai
python D:\GeologAI\start_integrated_app.py
```

---

## 📍 访问应用

启动后，访问以下地址：

- **前端应用**: http://localhost:8501
- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

---

## 🔄 工作流程

### 1. **登录/注册**
   - 首次访问显示认证页面
   - 支持用户注册和登录
   - 登录成功后进入仪表板

### 2. **创建项目**
   - 进入"📁 项目管理"标签页
   - 点击"➕ 创建项目"按钮
   - 填写项目信息并提交

### 3. **上传数据**
   - 进入"💾 数据管理"标签页
   - 选择目标项目
   - 上传测井数据文件（LAS/CSV/Excel）

### 4. **分析数据**
   - 进入"🔍 数据分析"标签页
   - 选择项目和数据
   - 选择分析方式并启动分析

---

## 🛠️ 技术架构

### 前端技术栈
- **框架**: Streamlit（Python Web框架）
- **UI组件**: Streamlit内置组件 + 自定义CSS
- **状态管理**: Streamlit session_state

### 后端技术栈
- **框架**: FastAPI
- **数据库**: SQLAlchemy ORM
- **认证**: JWT令牌

### API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/projects` | GET/POST | 查询/创建项目 |
| `/api/v1/data/upload` | POST | 上传数据 |
| `/api/v1/data` | GET | 查询数据 |

---

## 📝 状态管理

应用使用 Streamlit 的 session_state 管理以下数据：

```python
st.session_state.auth_token          # 认证令牌
st.session_state.user_info           # 用户信息
st.session_state.current_page        # 当前页面
st.session_state.show_create_project # 项目表单显示状态
st.session_state.show_user_menu      # 用户菜单显示状态
```

---

## 🔧 开发说明

### 添加新功能

1. **在仪表板中添加新标签页**
   ```python
   with tab_new:
       st.markdown("## 📌 新功能")
       # 添加功能代码
   ```

2. **调用后端API**
   ```python
   response = requests.get(
       f"{API_BASE_URL}/api/{API_VERSION}/your_endpoint",
       headers=get_headers(),
       timeout=10
   )
   ```

3. **使用会话状态存储状态**
   ```python
   st.session_state.your_state = value
   ```

### 页面结构

```
D:\GeologAI\web\frontend\
├── app.py                    # 主应用（集成应用）
├── INTEGRATION_NOTES.md      # 集成说明
├── pages/                    # 旧页面文件（可删除）
│   ├── 00_home.py
│   ├── 01_auth.py
│   ├── 02_dashboard.py
│   └── ...
└── ...
```

---

## 🐛 故障排除

### 问题1：后端连接失败
**原因**: 后端未启动或端口被占用
**解决**:
```bash
# 检查端口
netstat -ano | findstr ":8001"

# 杀死进程
taskkill /PID <PID> /F

# 重启后端
python D:\GeologAI\backend\run_backend.py
```

### 问题2：登录失败
**原因**: 后端服务未运行或用户名/密码错误
**解决**: 检查后端是否启动，确认用户名密码正确

### 问题3：数据上传超时
**原因**: 文件过大或网络连接慢
**解决**: 检查网络连接，尝试上传较小的文件

---

## 📚 参考资源

- [Streamlit 官方文档](https://docs.streamlit.io)
- [FastAPI 官方文档](https://fastapi.tiangolo.com)
- [GeologAI 项目文档](../DOCUMENTATION_INDEX.md)

---

## ✅ 更新日志

### v2.1 (2025-11-20)
- ✨ 整合多页面应用为单页面应用
- ✨ 统一UI设计和交互
- ✨ 改进用户体验
- ✨ 添加快速启动脚本

### v2.0 (旧版)
- 多页面应用架构
- 分离认证、项目、数据模块

---

**最后更新**: 2025-11-20  
**维护者**: GeologAI Team
