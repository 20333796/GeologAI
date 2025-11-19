import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="地球物理测井AI平台",
    page_icon="🌍",
    layout="wide"
)

# ======================== 页面配置 ========================
# 初始化 session state
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ======================== 侧边栏 ========================
st.sidebar.title("🌍 测井AI平台")

# 用户信息部分
if st.session_state.auth_token:
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ 已登录: {st.session_state.user_info.get('username', 'User')}")
    
    if st.sidebar.button("🚪 退出登录", use_container_width=True):
        st.session_state.auth_token = None
        st.session_state.user_info = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # 导航菜单
    page = st.sidebar.radio(
        "导航菜单",
        [
            "📊 首页",
            "📁 项目管理",
            "📤 数据上传",
            "📈 曲线分析",
            "🎯 3D 可视化",
            "🔴 实时数据",
            "🤖 AI预测",
            "🎓 模型训练",
        ]
    )
else:
    st.sidebar.warning("⚠️ 请先登录才能继续使用应用")
    if st.sidebar.button("🔐 前往登录页面", use_container_width=True):
        st.switch_page("pages/01_login.py")
    st.stop()

API_URL = "http://localhost:8000"

# ======================== 页面内容 ========================

# 首页
if page == "📊 首页":
    st.title("🌍 欢迎来到 GeologAI")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 用户", st.session_state.user_info.get("username", "Unknown"))
    with col2:
        st.metric("📊 数据集", "准备中")
    with col3:
        st.metric("🤖 模型", "离线")
    
    st.markdown("---")
    st.subheader("快速开始")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📁 项目管理", use_container_width=True):
            st.switch_page("pages/02_projects.py")
        st.caption("创建和管理项目")
    with col2:
        if st.button("📤 数据上传", use_container_width=True):
            st.switch_page("pages/03_data_upload.py")
        st.caption("上传测井数据")
    with col3:
        if st.button("📈 曲线分析", use_container_width=True):
            st.switch_page("pages/04_analysis.py")
        st.caption("分析和可视化")
    
    st.markdown("---")
    st.subheader("平台功能")
    
    features = {
        "📁 项目管理": "创建和管理多个地球物理项目",
        "📤 数据上传": "支持 LAS、CSV 和 Excel 格式的测井数据",
        "📈 曲线分析": "交互式测井曲线可视化和对比分析",
        "🎯 3D 可视化": "三维交互式曲线与钻孔轨迹",
        "🔴 实时数据": "实时流式数据与性能监控",
        "🤖 AI预测": "使用机器学习模型预测缺失的曲线",
        "🎓 模型训练": "使用你的数据训练自定义 AI 模型"
    }
    
    for feature, description in features.items():
        st.markdown(f"- **{feature}**: {description}")
    
    st.markdown("---")
    st.caption("💡 提示: 使用左侧菜单导航到不同的功能页面")

# 项目管理页面
elif page == "📁 项目管理":
    st.switch_page("pages/02_projects.py")

# 数据上传页面
elif page == "📤 数据上传":
    st.switch_page("pages/03_data_upload.py")

# 曲线分析页面
elif page == "📈 曲线分析":
    st.switch_page("pages/04_analysis.py")

# 3D 可视化页面
elif page == "🎯 3D 可视化":
    st.switch_page("pages/07_3d_visualization.py")

# 实时数据页面
elif page == "🔴 实时数据":
    st.switch_page("pages/09_realtime_data.py")

# AI预测页面
elif page == "🤖 AI预测":
    st.switch_page("pages/05_predictions.py")

# 模型训练页面
elif page == "🎓 模型训练":
    st.switch_page("pages/06_model_training.py")