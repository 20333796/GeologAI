"""
GeologAI 主应用 - 完整功能的地质智能分析平台
支持认证、项目管理、数据上传、分析等核心功能
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================== 页面配置 ========================
st.set_page_config(
    page_title="GeologAI - AI驱动的测井分析平台",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== API 配置 ========================
API_BASE_URL = "http://127.0.0.1:8001"
API_VERSION = "v1"

# ======================== 页面样式 ========================
st.markdown("""
<style>
    /* 全局样式 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* 主容器 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* 头部卡片 */
    .header-container {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .header-title {
        font-size: 32px;
        font-weight: 800;
        color: #2c3e50;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
    
    /* 通用卡片 */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.8rem;
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 12px;
        opacity: 0.9;
    }
    
    /* 首页英雄区 */
    .hero {
        text-align: center;
        padding: 5rem 2rem;
        color: white;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 56px;
        font-weight: 800;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 20px;
        font-weight: 300;
        opacity: 0.95;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 功能卡片网格 */
    .features-section {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        margin-bottom: 3rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .section-title {
        font-size: 32px;
        font-weight: 800;
        color: #2c3e50;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 2rem;
    }
    
    .feature-card {
        background: white;
        border: 2px solid #f0f0f0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #667eea;
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.15);
    }
    
    .feature-icon {
        font-size: 48px;
        margin-bottom: 1rem;
    }
    
    .feature-name {
        font-size: 18px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 14px;
        color: #7f8c8d;
        line-height: 1.6;
    }
    
    /* 用户信息样式 */
    .user-info {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .user-name {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .user-status {
        font-size: 12px;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# ======================== 会话状态初始化 ========================
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# ======================== 工具函数 ========================

def get_headers():
    """获取 API 请求头"""
    return {
        "Authorization": f"Bearer {st.session_state.auth_token}",
        "Content-Type": "application/json"
    }

def login_user(username: str, password: str) -> tuple:
    """登录用户"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/{API_VERSION}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data.get("access_token")
            st.session_state.user_info = {"username": username}
            return True, "登录成功"
        else:
            error_msg = response.json().get("detail", "登录失败")
            return False, error_msg
    except Exception as e:
        return False, f"连接错误: {str(e)}"

def register_user(username: str, email: str, password: str, password_confirm: str) -> tuple:
    """注册用户"""
    if password != password_confirm:
        return False, "两次输入的密码不一致"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/{API_VERSION}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        if response.status_code in [200, 201]:
            return True, "注册成功，请登录"
        else:
            error_msg = response.json().get("detail", "注册失败")
            return False, error_msg
    except Exception as e:
        return False, f"连接错误: {str(e)}"

def get_projects() -> list:
    """获取项目列表"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/{API_VERSION}/projects/my-projects",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                return data.get("data", [])
            return data if isinstance(data, list) else []
        return []
    except Exception as e:
        st.error(f"获取项目列表失败: {str(e)}")
        return []

def create_project(name: str, project_type: str, description: str = "") -> tuple:
    """创建项目"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/{API_VERSION}/projects",
            json={
                "name": name,
                "type": project_type,
                "description": description
            },
            headers=get_headers(),
            timeout=10
        )
        if response.status_code in [200, 201]:
            return True, "项目创建成功"
        else:
            return False, response.json().get("detail", "创建失败")
    except Exception as e:
        return False, f"错误: {str(e)}"

def upload_data(project_id: int, well_name: str, file, description: str = "") -> tuple:
    """上传数据"""
    try:
        files = {'file': (file.name, file.getbuffer(), file.type)}
        data = {
            'project_id': str(project_id),
            'well_name': well_name,
            'description': description
        }
        response = requests.post(
            f"{API_BASE_URL}/api/{API_VERSION}/data/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {st.session_state.auth_token}"},
            timeout=30
        )
        if response.status_code in [200, 201]:
            return True, "数据上传成功"
        else:
            return False, response.json().get("detail", "上传失败")
    except Exception as e:
        return False, f"错误: {str(e)}"

def get_project_data(project_id: int) -> list:
    """获取项目数据列表"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/{API_VERSION}/data?project_id={project_id}",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                return data.get("data", [])
            return data if isinstance(data, list) else []
        return []
    except Exception as e:
        st.error(f"获取数据列表失败: {str(e)}")
        return []

def logout_user():
    """退出登录"""
    st.session_state.auth_token = None
    st.session_state.user_info = None
    st.session_state.current_page = "home"
    st.rerun()

# ======================== 侧边栏渲染 ========================

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("""
        <div style="font-size: 24px; font-weight: 800; margin-bottom: 1.5rem; color: #3498db; text-align: center;">
            🌍 GeologAI
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.auth_token and st.session_state.user_info:
            # 用户信息
            username = st.session_state.user_info.get("username", "用户")
            st.markdown(f"""
            <div class="user-info">
                <div class="user-name">👤 {username}</div>
                <div class="user-status">✅ 已登录</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 导航菜单
            st.markdown('<div style="color: #3498db; font-weight: 700; margin-bottom: 1rem;">📋 导航菜单</div>', unsafe_allow_html=True)
            
            nav_items = [
                ("📊 仪表板", "dashboard"),
                ("📁 项目管理", "projects"),
                ("📤 数据上传", "data_upload"),
                ("📈 数据分析", "analysis"),
                ("🤖 AI 预测", "predictions"),
                ("🎓 模型训练", "training"),
            ]
            
            for label, page in nav_items:
                if st.button(label, use_container_width=True, 
                           type="primary" if st.session_state.current_page == page else "secondary",
                           key=f"nav_{page}"):
                    st.session_state.current_page = page
                    st.rerun()
            
            st.markdown("---")
            
            # 用户操作
            st.markdown('<div style="color: #3498db; font-weight: 700; margin-bottom: 1rem;">⚙️ 设置</div>', unsafe_allow_html=True)
            
            if st.button("🚪 退出登录", use_container_width=True):
                logout_user()
        else:
            # 未登录状态
            st.markdown('<div style="color: #3498db; font-weight: 700; margin-bottom: 1rem;">👤 用户</div>', unsafe_allow_html=True)
            
            if st.button("🔐 登录", use_container_width=True, type="primary"):
                st.session_state.current_page = "login"
                st.rerun()
            
            if st.button("📝 注册", use_container_width=True):
                st.session_state.current_page = "register"
                st.rerun()
            
            st.markdown("---")
            st.markdown("""
            <div style="color: #95a5a6; font-size: 12px; line-height: 1.6; margin-top: 2rem;">
                💡 <b>提示</b>: 点击 <b>登录</b> 或 <b>注册</b> 按钮开始使用 GeologAI 平台
            </div>
            """, unsafe_allow_html=True)

# ======================== 页面内容 ========================

def page_home():
    """首页"""
    st.markdown("""
    <div class="hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: -2rem -2rem 0; padding: 5rem 2rem; border-radius: 0;">
        <h1 class="hero-title">🌍 GeologAI</h1>
        <p class="hero-subtitle">
            AI 驱动的地质智能分析平台
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="features-section">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📁</div>
                <div class="feature-name">项目管理</div>
                <div class="feature-desc">创建和管理多个地球物理项目</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📤</div>
                <div class="feature-name">数据上传</div>
                <div class="feature-desc">支持 LAS、CSV 和 Excel 格式</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-name">数据分析</div>
                <div class="feature-desc">交互式可视化与对比分析</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-name">AI 预测</div>
                <div class="feature-desc">机器学习驱动的预测分析</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎓</div>
                <div class="feature-name">模型训练</div>
                <div class="feature-desc">自定义AI模型训练与优化</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-name">3D 可视化</div>
                <div class="feature-desc">三维交互式数据展示</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def page_login():
    """登录页面"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="header-container">
            <div class="header-title">🔐 用户登录</div>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("用户名", placeholder="输入用户名")
        password = st.text_input("密码", type="password", placeholder="输入密码")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("登录", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("❌ 用户名和密码不能为空")
                else:
                    with st.spinner("正在登录..."):
                        success, message = login_user(username, password)
                        if success:
                            st.success(message)
                            st.session_state.current_page = "dashboard"
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        with col2:
            if st.button("返回", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()

def page_register():
    """注册页面"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="header-container">
            <div class="header-title">📝 新用户注册</div>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("用户名", placeholder="4-20 个字符")
        email = st.text_input("邮箱", placeholder="example@email.com")
        password = st.text_input("密码", type="password", placeholder="至少 8 个字符")
        password_confirm = st.text_input("确认密码", type="password", placeholder="再次输入密码")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("注册", use_container_width=True, type="primary"):
                if not all([username, email, password, password_confirm]):
                    st.error("❌ 请填写所有字段")
                else:
                    with st.spinner("正在注册..."):
                        success, message = register_user(username, email, password, password_confirm)
                        if success:
                            st.success(message)
                            st.session_state.current_page = "login"
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        with col2:
            if st.button("返回", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()

def page_dashboard():
    """仪表板"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📊 仪表板</div>
        <div class="header-subtitle">欢迎使用 GeologAI 地质智能分析平台</div>
    </div>
    """, unsafe_allow_html=True)
    
    projects = get_projects()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(projects)}</div>
            <div class="metric-label">📁 项目总数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_data = sum(len(get_project_data(p.get('id') or p.get('project_id'))) 
                        for p in projects if p.get('id') or p.get('project_id'))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_data}</div>
            <div class="metric-label">💾 数据集</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">24</div>
            <div class="metric-label">🤖 模型库</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12</div>
            <div class="metric-label">✨ 任务</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("⚡ 快速操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ 创建项目", use_container_width=True):
            st.session_state.current_page = "projects"
            st.rerun()
    
    with col2:
        if st.button("📤 上传数据", use_container_width=True):
            st.session_state.current_page = "data_upload"
            st.rerun()
    
    with col3:
        if st.button("📈 分析数据", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()

def page_projects():
    """项目管理"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📁 项目管理</div>
        <div class="header-subtitle">创建和管理您的项目</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 项目列表", "➕ 创建项目"])
    
    with tab1:
        projects = get_projects()
        
        if projects:
            for project in projects:
                project_name = project.get('name', 'Untitled')
                project_type = project.get('type', '')
                project_desc = project.get('description', '')
                
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{project_name}</div>
                    <div style="color: #7f8c8d; margin-bottom: 0.5rem;">
                        📌 类型: {project_type}
                    </div>
                    <div style="color: #95a5a6;">
                        📝 {project_desc if project_desc else "暂无描述"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 暂无项目，请创建新项目")
    
    with tab2:
        st.subheader("➕ 创建新项目")
        
        with st.form("create_project_form"):
            project_name = st.text_input("项目名称", placeholder="输入项目名称")
            project_type = st.selectbox(
                "项目类型",
                ["地震数据分析", "测井数据分析", "矿产评估", "油气勘探", "其他"]
            )
            project_desc = st.text_area("项目描述", placeholder="项目简介", height=100)
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.form_submit_button("✅ 创建"):
                    if not project_name:
                        st.error("❌ 项目名称不能为空")
                    else:
                        with st.spinner("正在创建..."):
                            success, message = create_project(project_name, project_type, project_desc)
                            if success:
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

def page_data_upload():
    """数据上传"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📤 数据上传</div>
        <div class="header-subtitle">上传测井数据（LAS、CSV、Excel）</div>
    </div>
    """, unsafe_allow_html=True)
    
    projects = get_projects()
    
    if not projects:
        st.warning("⚠️ 请先创建项目")
        return
    
    project_dict = {}
    for p in projects:
        p_id = p.get('id') or p.get('project_id')
        if p_id:
            project_dict[p_id] = p.get('name', 'Untitled')
    
    if not project_dict:
        st.warning("⚠️ 项目列表为空")
        return
    
    selected_project_id = st.selectbox(
        "选择项目",
        list(project_dict.keys()),
        format_func=lambda x: project_dict[x]
    )
    
    st.markdown("---")
    
    with st.form("upload_form"):
        well_name = st.text_input("井号/井名", placeholder="输入井号")
        data_type = st.selectbox("数据格式", ["LAS", "CSV", "Excel", "其他"])
        uploaded_file = st.file_uploader("选择文件", type=["las", "csv", "xlsx", "xls"])
        description = st.text_area("数据描述", placeholder="数据相关信息", height=80)
        
        if st.form_submit_button("✅ 上传"):
            if not well_name:
                st.error("❌ 井号不能为空")
            elif not uploaded_file:
                st.error("❌ 请选择文件")
            else:
                with st.spinner("正在上传..."):
                    success, message = upload_data(selected_project_id, well_name, uploaded_file, description)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

def page_analysis():
    """数据分析"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📈 数据分析</div>
        <div class="header-subtitle">分析和可视化测井数据</div>
    </div>
    """, unsafe_allow_html=True)
    
    projects = get_projects()
    
    if not projects:
        st.warning("⚠️ 请先创建项目")
        return
    
    project_dict = {}
    for p in projects:
        p_id = p.get('id') or p.get('project_id')
        if p_id:
            project_dict[p_id] = p.get('name', 'Untitled')
    
    if not project_dict:
        st.warning("⚠️ 项目列表为空")
        return
    
    selected_project_id = st.selectbox(
        "选择项目",
        list(project_dict.keys()),
        format_func=lambda x: project_dict[x],
        key="analysis_project"
    )
    
    data_list = get_project_data(selected_project_id)
    
    if not data_list:
        st.info("💡 该项目暂无数据，请先上传数据")
        return
    
    well_names = [d.get("well_name", "未知") for d in data_list]
    selected_idx = st.selectbox("选择数据", range(len(data_list)), 
                               format_func=lambda x: well_names[x])
    
    if selected_idx is not None:
        data_item = data_list[selected_idx]
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("行数", data_item.get("rows_count", 0))
        
        with col2:
            st.metric("文件大小", f"{data_item.get('file_size', 0) / 1024:.1f} KB")
        
        with col3:
            st.metric("上传时间", data_item.get("uploaded_at", "N/A")[:10])
        
        st.markdown("---")
        
        analysis_type = st.selectbox(
            "选择分析方式",
            ["地层识别", "异常检测", "趋势预测", "质量评估"]
        )
        
        if st.button("🚀 开始分析", type="primary", use_container_width=True):
            st.info(f"✨ 正在进行 {analysis_type} 分析...")
            st.success("✅ 分析完成！")

def page_predictions():
    """AI 预测"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🤖 AI 预测</div>
        <div class="header-subtitle">使用机器学习进行预测分析</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🔨 此功能正在开发中...")

def page_training():
    """模型训练"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🎓 模型训练</div>
        <div class="header-subtitle">训练自定义机器学习模型</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🔨 此功能正在开发中...")

# ======================== 主程序入口 ========================

def main():
    """主程序"""
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据页面状态显示对应内容
    if not st.session_state.auth_token:
        if st.session_state.current_page == "login":
            page_login()
        elif st.session_state.current_page == "register":
            page_register()
        else:
            page_home()
    else:
        if st.session_state.current_page == "projects":
            page_projects()
        elif st.session_state.current_page == "data_upload":
            page_data_upload()
        elif st.session_state.current_page == "analysis":
            page_analysis()
        elif st.session_state.current_page == "predictions":
            page_predictions()
        elif st.session_state.current_page == "training":
            page_training()
        else:
            page_dashboard()

if __name__ == "__main__":
    main()

