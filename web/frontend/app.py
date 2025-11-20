"""
GeologAI 前端应用 - Phase 5a 初始架构
基础认证系统和项目管理框架
"""

import streamlit as st
import requests
import time
from datetime import datetime

# ===================== 配置 =====================
st.set_page_config(
    page_title="GeologAI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8001"

# ===================== 样式 =====================
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: white; }
    .stApp { background: #f5f7fa; }
    .metric-container { background: white; padding: 20px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ===================== 会话状态 =====================
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ===================== API 调用 =====================

def api_login(username: str, password: str) -> tuple:
    """用户登录
    
    Returns:
        (success: bool, token: str or message: str, user: str or error_msg)
    """
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            return True, token, username
        else:
            error_msg = r.json().get("detail", "登录失败")
            return False, None, error_msg
    except Exception as e:
        return False, None, f"连接错误: {str(e)}"

def api_register(username: str, email: str, password: str) -> tuple:
    """用户注册
    
    Returns:
        (success: bool, message: str)
    """
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        if r.status_code in [200, 201]:
            return True, "注册成功，请登录"
        else:
            error_msg = r.json().get("detail", "注册失败")
            return False, error_msg
    except Exception as e:
        return False, f"连接错误: {str(e)}"

def api_get_projects() -> list:
    """获取用户项目列表"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        r = requests.get(
            f"{API_BASE_URL}/api/v1/projects/my-projects",
            headers=headers,
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # 处理嵌套响应格式
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        st.error(f"获取项目失败: {e}")
        return []

def api_create_project(name: str, project_type: str, description: str = "") -> tuple:
    """创建新项目
    
    Returns:
        (success: bool, message: str)
    """
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        r = requests.post(
            f"{API_BASE_URL}/api/v1/projects",
            json={
                "name": name,
                "type": project_type,
                "description": description
            },
            headers=headers,
            timeout=10
        )
        if r.status_code in [200, 201]:
            return True, "项目创建成功"
        else:
            error_msg = r.json().get("detail", "创建失败")
            return False, error_msg
    except Exception as e:
        return False, f"连接错误: {str(e)}"

# ===================== 侧边栏导航 =====================

with st.sidebar:
    st.title("🌍 GeologAI")
    st.markdown("*地质智能分析平台*")
    st.divider()
    
    if st.session_state.token:
        # 已登录状态
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        
        # 导航菜单
        st.markdown("**导航**")
        nav_items = [
            ("🏠 主页", "home"),
            ("📁 项目", "projects"),
            ("📊 仪表板", "dashboard"),
        ]
        
        for label, page_name in nav_items:
            if st.button(label, use_container_width=True, key=f"nav_{page_name}"):
                st.session_state.page = page_name
                st.rerun()
        
        st.divider()
        
        if st.button("🚪 退出登录", use_container_width=True, type="secondary"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
    else:
        # 未登录状态
        st.markdown("**请登录或注册**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 登录", use_container_width=True, type="primary"):
                st.session_state.page = "login"
                st.rerun()
        with col2:
            if st.button("📝 注册", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

# ===================== 主要内容 =====================

if not st.session_state.token:
    # ===== 认证页面 =====
    
    if st.session_state.page == "register":
        # 注册页面
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("📝 用户注册")
            
            with st.form("register_form"):
                username = st.text_input("用户名", placeholder="输入用户名")
                email = st.text_input("邮箱", placeholder="输入邮箱")
                password = st.text_input("密码", type="password", placeholder="输入密码")
                password_confirm = st.text_input("确认密码", type="password", placeholder="再次输入密码")
                
                submitted = st.form_submit_button("✅ 注册", use_container_width=True)
                
                if submitted:
                    if not all([username, email, password, password_confirm]):
                        st.error("❌ 请填写所有字段")
                    elif password != password_confirm:
                        st.error("❌ 两次密码输入不一致")
                    elif len(password) < 6:
                        st.error("❌ 密码至少 6 位")
                    else:
                        success, msg = api_register(username, email, password)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
            
            st.divider()
            if st.button("← 返回登录", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
    else:
        # 登录页面（默认）
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 用户登录")
            
            with st.form("login_form"):
                username = st.text_input("用户名", placeholder="输入用户名")
                password = st.text_input("密码", type="password", placeholder="输入密码")
                
                submitted = st.form_submit_button("✅ 登录", use_container_width=True, type="primary")
                
                if submitted:
                    if not username or not password:
                        st.error("❌ 请输入用户名和密码")
                    else:
                        with st.spinner("正在验证..."):
                            success, token, result = api_login(username, password)
                        
                        if success:
                            st.session_state.token = token
                            st.session_state.user = username
                            st.session_state.page = "home"
                            st.success("✅ 登录成功")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
            
            st.divider()
            if st.button("→ 去注册", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

else:
    # ===== 已登录页面 =====
    
    if st.session_state.page == "home":
        st.title("🏠 主页")
        st.markdown("欢迎使用 GeologAI 地质智能分析平台")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 项目", "0")
        with col2:
            st.metric("💾 数据集", "0")
        with col3:
            st.metric("📊 任务", "0")
        
        st.divider()
        st.markdown("""
        ### 功能特性
        - 📁 **项目管理** - 创建和管理地质项目
        - 📤 **数据上传** - 支持 LAS、CSV、Excel 等格式
        - 📊 **数据分析** - 专业的地质数据分析工具
        - 🎨 **可视化** - 交互式数据展示
        - 🤖 **AI预测** - 基于机器学习的预测
        """)
    
    elif st.session_state.page == "projects":
        st.title("📁 项目管理")
        
        tab1, tab2 = st.tabs(["项目列表", "创建项目"])
        
        with tab1:
            st.subheader("我的项目")
            projects = api_get_projects()
            
            if projects:
                for project in projects:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        project_id = project.get("id") or project.get("project_id")
                        project_name = project.get("name", "未命名")
                        project_type = project.get("type", "")
                        project_desc = project.get("description", "暂无描述")
                        
                        st.markdown(f"**{project_name}** ({project_type})")
                        st.caption(project_desc)
                    
                    st.divider()
                
                if not projects:
                    st.info("💡 暂无项目")
            else:
                st.info("💡 暂无项目，点击下方选项卡创建新项目")
        
        with tab2:
            st.subheader("创建新项目")
            
            with st.form("create_project_form"):
                name = st.text_input("项目名称", placeholder="例：南海油气田勘探")
                project_type = st.selectbox("项目类型", [
                    "地震数据分析",
                    "测井数据分析",
                    "矿产评估",
                    "油气勘探",
                    "其他"
                ])
                description = st.text_area("项目描述", placeholder="描述项目目标和内容", height=100)
                
                submitted = st.form_submit_button("✅ 创建项目", use_container_width=True)
                
                if submitted:
                    if not name:
                        st.error("❌ 项目名称不能为空")
                    else:
                        with st.spinner("正在创建..."):
                            success, msg = api_create_project(name, project_type, description)
                        
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
    
    elif st.session_state.page == "dashboard":
        st.title("📊 仪表板")
        
        projects = api_get_projects()
        st.markdown(f"### 概览")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 项目数", len(projects))
        with col2:
            st.metric("📊 任务数", 0)
        with col3:
            st.metric("✅ 已完成", 0)
        with col4:
            st.metric("⏳ 进行中", 0)
        
        st.divider()
        st.info("ℹ️ Phase 5a 架构初始化完成。后续阶段将添加更多功能。")

# ===================== 底部信息 =====================
st.divider()
st.caption(f"GeologAI Phase 5a · {datetime.now().strftime('%Y-%m-%d %H:%M')}")

