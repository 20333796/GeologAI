import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

st.set_page_config(
    page_title="GeologAI - AI驱动的测井分析平台",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================== API配置 ========================
API_BASE_URL = "http://127.0.0.1:8001"
AUTH_ENDPOINT = f"{API_BASE_URL}/api/v1/auth"

# ======================== 页面样式 ========================
st.markdown("""
<style>
    /* 全局样式 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    
    /* 隐藏默认元素 */
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stToolbar"] { visibility: hidden; }
    
    /* 主容器背景 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* 顶部导航栏 */
    .navbar {
        position: sticky;
        top: 0;
        background: white;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 999;
    }
    
    .navbar-logo {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .navbar-tagline {
        font-size: 12px;
        color: #999;
        margin-left: 0.5rem;
    }
    
    .auth-buttons-group {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .btn-outline {
        background: white;
        color: #667eea;
        border: 2px solid #667eea;
        padding: 10px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-outline:hover {
        background: #667eea;
        color: white;
    }
    
    .btn-solid {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-solid:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .user-badge {
        background: #f0f0f0;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* 英雄区域 */
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
    
    .hero-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .btn-large {
        padding: 14px 32px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-white {
        background: white;
        color: #667eea;
    }
    
    .btn-white:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    /* 功能网格 */
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
        cursor: pointer;
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
    
    /* 模态框 */
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2000;
        backdrop-filter: blur(4px);
    }
    
    .modal {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        max-width: 480px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: slideUp 0.3s ease;
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .modal-close {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #999;
    }
    
    .modal-title {
        font-size: 28px;
        font-weight: 800;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .modal-subtitle {
        font-size: 14px;
        color: #999;
        margin-bottom: 2rem;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .form-input {
        width: 100%;
        padding: 12px 16px;
        border: 2px solid #f0f0f0;
        border-radius: 8px;
        font-size: 14px;
        font-family: inherit;
        transition: border-color 0.3s;
        box-sizing: border-box;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .form-error {
        color: #e74c3c;
        font-size: 12px;
        margin-top: 0.5rem;
    }
    
    .form-button {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .form-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    .tab-switcher {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .tab-button {
        background: none;
        border: none;
        padding: 12px 0;
        margin-bottom: -2px;
        font-size: 14px;
        font-weight: 600;
        color: #999;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: all 0.3s;
    }
    
    .tab-button.active {
        color: #667eea;
        border-bottom-color: #667eea;
    }
    
    /* Dashboard */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .welcome-text {
        font-size: 28px;
        font-weight: 800;
        color: #2c3e50;
    }
    
    .dashboard-modules {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
    }
    
    .module-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .module-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.12);
    }
    
    .module-icon {
        font-size: 44px;
        margin-bottom: 0.5rem;
    }
    
    .module-name {
        font-size: 16px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.25rem;
    }
    
    .module-desc {
        font-size: 12px;
        color: #999;
    }
</style>
""", unsafe_allow_html=True)

# ======================== 初始化Session State ========================
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "show_auth_modal" not in st.session_state:
    st.session_state.show_auth_modal = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# 检查URL参数
params = st.query_params
if params.get("auth") == "login":
    st.session_state.show_auth_modal = True
    st.session_state.auth_mode = "login"
    st.query_params.clear()
elif params.get("auth") == "register":
    st.session_state.show_auth_modal = True
    st.session_state.auth_mode = "register"
    st.query_params.clear()

# ======================== 工具函数 ========================

def login_user(username: str, password: str):
    """登录用户"""
    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data.get("access_token")
            st.session_state.user_info = data.get("user", {})
            st.session_state.show_auth_modal = False
            st.success("✅ 登录成功！")
            st.rerun()
        else:
            st.error(f"❌ 登录失败: {response.text}")
    except Exception as e:
        st.error(f"❌ 连接错误: {str(e)}")

def register_user(username: str, email: str, password: str, confirm_password: str):
    """注册用户"""
    if password != confirm_password:
        st.error("❌ 两次输入的密码不匹配")
        return
    
    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/register",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 201:
            st.success("✅ 注册成功！正在自动登录...")
            login_user(username, password)
        else:
            error_data = response.json()
            error_msg = error_data.get("detail", "未知错误")
            st.error(f"❌ 注册失败: {error_msg}")
    except Exception as e:
        st.error(f"❌ 连接错误: {str(e)}")

def logout_user():
    """退出登录"""
    st.session_state.auth_token = None
    st.session_state.user_info = None
    st.rerun()

# ======================== 顶部导航栏 ========================

col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])

with col_nav1:
    st.markdown('<div class="navbar-logo">🌍 GeologAI</div>', unsafe_allow_html=True)

with col_nav3:
    if st.session_state.auth_token:
        col_user, col_logout = st.columns(2)
        with col_user:
            username = st.session_state.user_info.get("username", "User")
            st.markdown(f'<div class="user-badge">👤 {username}</div>', unsafe_allow_html=True)
        with col_logout:
            if st.button("🚪 退出", use_container_width=True):
                logout_user()
    else:
        col_login, col_register = st.columns(2)
        with col_login:
            if st.button("🔐 登录", use_container_width=True):
                st.session_state.show_auth_modal = True
                st.session_state.auth_mode = "login"
        with col_register:
            if st.button("📝 注册", use_container_width=True):
                st.session_state.show_auth_modal = True
                st.session_state.auth_mode = "register"

st.markdown("---")

# ======================== 认证模态框 ========================

if st.session_state.show_auth_modal:
    col_modal_spacer1, col_modal, col_modal_spacer2 = st.columns([1, 2, 1])
    
    with col_modal:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        ">
        """, unsafe_allow_html=True)
        
        # 关闭按钮
        col_close_btn = st.columns([10, 1])[1]
        with col_close_btn:
            if st.button("✕", key="close_modal"):
                st.session_state.show_auth_modal = False
                st.rerun()
        
        # Tab 切换
        col_tab1, col_tab2 = st.columns(2)
        with col_tab1:
            if st.button(
                "🔐 登录",
                key="tab_login",
                use_container_width=True,
                type="primary" if st.session_state.auth_mode == "login" else "secondary"
            ):
                st.session_state.auth_mode = "login"
                st.rerun()
        
        with col_tab2:
            if st.button(
                "📝 注册",
                key="tab_register",
                use_container_width=True,
                type="primary" if st.session_state.auth_mode == "register" else "secondary"
            ):
                st.session_state.auth_mode = "register"
                st.rerun()
        
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # 登录表单
        if st.session_state.auth_mode == "login":
            st.markdown("### 登录您的账户")
            
            login_username = st.text_input(
                "用户名",
                placeholder="输入用户名",
                key="login_username"
            )
            login_password = st.text_input(
                "密码",
                type="password",
                placeholder="输入密码",
                key="login_password"
            )
            
            col_submit1, col_submit2 = st.columns(2)
            with col_submit1:
                if st.button("🔓 登录", use_container_width=True, type="primary", key="login_btn"):
                    if login_username and login_password:
                        login_user(login_username, login_password)
                    else:
                        st.error("❌ 请输入用户名和密码")
            
            with col_submit2:
                if st.button("✕ 取消", use_container_width=True, key="cancel_login"):
                    st.session_state.show_auth_modal = False
                    st.rerun()
        
        # 注册表单
        else:
            st.markdown("### 创建新账户")
            
            reg_username = st.text_input(
                "用户名",
                placeholder="4-20个字符",
                key="reg_username"
            )
            reg_email = st.text_input(
                "邮箱",
                placeholder="example@email.com",
                key="reg_email"
            )
            reg_password = st.text_input(
                "密码",
                type="password",
                placeholder="至少8个字符",
                key="reg_password"
            )
            reg_confirm = st.text_input(
                "确认密码",
                type="password",
                placeholder="再次输入密码",
                key="reg_confirm"
            )
            
            col_submit1, col_submit2 = st.columns(2)
            with col_submit1:
                if st.button("✓ 注册", use_container_width=True, type="primary", key="register_btn"):
                    if all([reg_username, reg_email, reg_password, reg_confirm]):
                        register_user(reg_username, reg_email, reg_password, reg_confirm)
                    else:
                        st.error("❌ 请填写所有字段")
            
            with col_submit2:
                if st.button("✕ 取消", use_container_width=True, key="cancel_register"):
                    st.session_state.show_auth_modal = False
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ======================== 未登录状态 - 首页 ========================

if not st.session_state.auth_token:
    # 英雄区域
    st.markdown("""
    <div class="hero">
        <h1 class="hero-title">🌍 地球物理AI分析平台</h1>
        <p class="hero-subtitle">
            利用先进的机器学习和深度学习技术，
            自动化分析测井数据，提高地球物理解释效率
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能介绍
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
                <div class="feature-desc">支持LAS、CSV和Excel格式</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-name">曲线分析</div>
                <div class="feature-desc">交互式可视化与对比分析</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-name">3D可视化</div>
                <div class="feature-desc">三维交互式钻孔轨迹</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔴</div>
                <div class="feature-name">实时数据</div>
                <div class="feature-desc">流式数据与监控</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-name">AI预测</div>
                <div class="feature-desc">机器学习自动预测</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎓</div>
                <div class="feature-name">模型训练</div>
                <div class="feature-desc">自定义AI模型训练</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-name">深度学习</div>
                <div class="feature-desc">神经网络配置与监控</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-name">实时预测</div>
                <div class="feature-desc">流式推理与批量评估</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-name">模型解释</div>
                <div class="feature-desc">SHAP与特征分析</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: white; padding: 2rem;">
        <p style="font-size: 16px;">
            💡 <b>准备好开始了吗？</b> 点击上方 <b>🔐 登录</b> 或 <b>📝 注册</b> 按钮进入平台
        </p>
    </div>
    """, unsafe_allow_html=True)

# ======================== 已登录状态 - 仪表盘 ========================

else:
    # Dashboard 头部
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <div class="welcome-text">👋 欢迎，{}</div>
            <div style="font-size: 14px; color: #999; margin-top: 0.25rem;">
                准备好分析数据了吗？
            </div>
        </div>
    </div>
    """.format(st.session_state.user_info.get("username", "用户")), unsafe_allow_html=True)
    
    # 快速操作
    st.markdown("### ⚡ 快速操作")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 新建项目", use_container_width=True):
            st.switch_page("pages/02_projects.py")
    
    with col2:
        if st.button("📤 上传数据", use_container_width=True):
            st.switch_page("pages/03_data_upload.py")
    
    with col3:
        if st.button("📈 分析数据", use_container_width=True):
            st.switch_page("pages/04_analysis.py")
    
    st.markdown("---")
    
    # 功能模块网格
    st.markdown("### 🚀 功能模块")
    
    modules = [
        ("📁 项目管理", "pages/02_projects.py", "创建和管理项目"),
        ("📤 数据上传", "pages/03_data_upload.py", "上传测井数据"),
        ("📈 曲线分析", "pages/04_analysis.py", "分析和可视化"),
        ("🤖 AI预测", "pages/05_predictions.py", "机器学习预测"),
        ("🎓 模型训练", "pages/06_model_training.py", "训练自定义模型"),
        ("🎯 3D可视化", "pages/07_3d_visualization.py", "三维交互"),
        ("🔴 实时数据", "pages/09_realtime_data.py", "流式数据监控"),
        ("🧠 深度学习", "pages/10_deep_learning.py", "神经网络"),
        ("⚡ 实时预测", "pages/11_realtime_predictions.py", "流式推理"),
        ("🔍 模型解释", "pages/12_model_interpretability.py", "特征解释"),
    ]
    
    cols = st.columns(5)
    for idx, (name, page, desc) in enumerate(modules):
        with cols[idx % 5]:
            if st.button(name, use_container_width=True, help=desc):
                st.switch_page(page)
    
    st.markdown("---")
    st.markdown("""
    <div style="
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: #999;
        font-size: 14px;
    ">
        💡 提示：使用上方功能按钮快速导航到不同的模块
    </div>
    """, unsafe_allow_html=True)

