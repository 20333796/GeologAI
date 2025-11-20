"""
后台首页 - 仪表板
macOS风格设计，提供10个功能模块快速导航
供已认证用户访问
"""

import streamlit as st
import requests
from datetime import datetime
import time

# 页面配置
st.set_page_config(
    page_title="仪表板 - GeologAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏顶部菜单
st.markdown("""
    <style>
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    header { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { padding: 0px !important; }
    .stAppViewContainer { padding: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# ============= 认证检查 =============
if not st.session_state.get("auth_token"):
    st.switch_page("pages/00_home.py")

# ============= 会话状态初始化 =============
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# 后端API配置
BACKEND_URL = "http://localhost:8001"
API_VERSION = "v1"
AUTH_TOKEN = st.session_state.get("auth_token", "")
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


# ============= 侧边栏：自定义内容 =============
user_name = st.session_state.user_info["username"] if st.session_state.get("user_info") and st.session_state.user_info.get("username") else "用户"
user_email = st.session_state.user_info["email"] if st.session_state.get("user_info") and st.session_state.user_info.get("email") else ""
with st.sidebar:
    st.markdown("### 👤 个人中心")
    st.markdown(f"**用户名**：{user_name}")
    if user_email:
        st.markdown(f"**邮箱**：{user_email}")
    st.markdown("---")
    if st.button("🔓 退出登录", use_container_width=True, type="secondary"):
        st.session_state.auth_token = None
        st.session_state.user_info = None
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("💬 智能问答（即将上线）")

# ============= 主内容区域 =============

# ============= 欢迎信息 =============
now = datetime.now()
hour = now.hour
if hour < 12:
    greeting = "早上好"
elif hour < 18:
    greeting = "下午好"
else:
    greeting = "晚上好"

user_display_name = st.session_state.user_info.get("real_name", st.session_state.user_info.get("username", "用户")) if st.session_state.user_info else "用户"
st.markdown(f"# {greeting}，{user_display_name}! 👋")
st.markdown(f"欢迎来到 GeologAI 数据分析平台 | {now.strftime('%Y年%m月%d日 %H:%M')}")

st.markdown("---")

# ============= 获取项目列表 =============
@st.cache_data(ttl=30)
def get_projects_count():
    """获取项目总数"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/{API_VERSION}/projects",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            return len(response.json())
        return 0
    except:
        return 0

# ============= 快速统计信息 =============
st.markdown("## 📊 概览")

col1, col2, col3, col4 = st.columns(4)

projects_count = get_projects_count()

with col1:
    st.metric("🔬 项目总数", str(projects_count), "+0 本周")

with col2:
    st.metric("📁 数据集", "48", "+5 本周")

with col3:
    st.metric("📈 分析结果", "87", "+12 本周")

with col4:
    st.metric("🤖 模型库", "24", "最新版本")

st.markdown("---")

# ============= 功能模块导航 (Launchpad风格) =============
st.markdown("## 🚀 功能中心")

# 初始化session_state标志
if "show_create_project_modal" not in st.session_state:
    st.session_state.show_create_project_modal = False

# 定义10个功能模块
modules = [
    {
        "icon": "📁",
        "title": "项目管理",
        "desc": "创建和管理分析项目",
        "page": "pages/03_data_upload.py",
        "color": "#FF6B6B"
    },
    {
        "icon": "💾",
        "title": "数据管理",
        "desc": "上传和处理地质数据",
        "page": "pages/04_analysis.py",
        "color": "#4ECDC4"
    },
    {
        "icon": "🔍",
        "title": "数据分析",
        "desc": "AI驱动的深度分析",
        "page": "pages/05_predictions.py",
        "color": "#45B7D1"
    },
    {
        "icon": "🗺️",
        "title": "地理可视化",
        "desc": "交互式地图展示",
        "page": "pages/06_model_training.py",
        "color": "#96CEB4"
    },
    {
        "icon": "🤖",
        "title": "AI模型库",
        "desc": "预训练模型和工具",
        "page": "pages/07_3d_visualization.py",
        "color": "#FFEAA7"
    },
    {
        "icon": "📈",
        "title": "性能评估",
        "desc": "模型效果评估工具",
        "page": "pages/08_stratum_profile.py",
        "color": "#DDA15E"
    },
    {
        "icon": "📊",
        "title": "报告生成",
        "desc": "生成专业分析报告",
        "page": "pages/09_realtime_data.py",
        "color": "#BC6C25"
    },
    {
        "icon": "⚙️",
        "title": "系统设置",
        "desc": "账户和系统配置",
        "page": "pages/10_deep_learning.py",
        "color": "#6C757D"
    },
    {
        "icon": "📚",
        "title": "帮助中心",
        "desc": "文档和常见问题",
        "page": "pages/11_realtime_predictions.py",
        "color": "#007BFF"
    },
    {
        "icon": "🔗",
        "title": "集成工具",
        "desc": "第三方服务集成",
        "page": "pages/12_model_interpretability.py",
        "color": "#6F42C1"
    }
]

# 创建网格布局 - 5列 x 2行
cols = st.columns(5)


# ============= 功能按钮：点击直接跳转 =============
for idx, module in enumerate(modules):
    col_idx = idx % 5
    with cols[col_idx]:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {module['color']}15, {module['color']}05);
            border: 2px solid {module['color']}30;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        '>
            <div style='font-size: 40px; margin-bottom: 10px;'>{module['icon']}</div>
            <div style='font-weight: bold; font-size: 16px; color: #333; margin-bottom: 5px;'>{module['title']}</div>
            <div style='font-size: 12px; color: #666;'>{module['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 项目管理模块 - 打开创建项目弹窗
        if idx == 0:  # 项目管理是第一个
            if st.button(f"进入", key=f"module_{idx}", use_container_width=True):
                st.session_state.show_create_project_modal = True
                st.rerun()
        else:
            if st.button(f"进入", key=f"module_{idx}", use_container_width=True):
                st.switch_page(module["page"])

st.markdown("---")

# ============= 创建项目弹窗 =============
if st.session_state.show_create_project_modal:
    st.markdown("## ➕ 创建新项目")
    
    with st.form("create_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "项目名称",
                placeholder="输入项目名称",
                max_chars=100
            )
        
        with col2:
            project_type = st.selectbox(
                "项目类型",
                ["地震数据分析", "测井数据分析", "矿产评估", "油气勘探", "其他"]
            )
        
        project_desc = st.text_area(
            "项目描述",
            placeholder="简要描述项目目标和内容",
            height=100,
            max_chars=500
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submit_btn = st.form_submit_button("✅ 创建", use_container_width=True, type="primary")
        
        with col2:
            cancel_btn = st.form_submit_button("❌ 取消", use_container_width=True)
        
        if cancel_btn:
            st.session_state.show_create_project_modal = False
            st.rerun()
        
        if submit_btn:
            if not project_name:
                st.error("❌ 项目名称不能为空")
            else:
                with st.spinner("正在创建项目..."):
                    try:
                        payload = {
                            "name": project_name,
                            "type": project_type,
                            "description": project_desc
                        }
                        
                        response = requests.post(
                            f"{BACKEND_URL}/api/{API_VERSION}/projects",
                            json=payload,
                            headers=HEADERS,
                            timeout=10
                        )
                        
                        if response.status_code in [200, 201]:
                            st.success("✅ 项目创建成功！")
                            st.session_state.show_create_project_modal = False
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            error_msg = response.json().get("detail", "创建失败")
                            st.error(f"❌ 创建失败: {error_msg}")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ 无法连接到服务器")
                    except Exception as e:
                        st.error(f"❌ 错误: {str(e)}")
    
    st.markdown("---")

# ============= 最近活动 =============
st.markdown("## 📝 最近活动")

activity_data = [
    {"time": "2024-01-20 14:30", "action": "项目「油田勘探」已完成分析", "type": "success"},
    {"time": "2024-01-20 12:15", "action": "上传数据集「地震数据2024Q1」", "type": "info"},
    {"time": "2024-01-19 16:45", "action": "运行AI模型「地层识别v3.2」", "type": "success"},
    {"time": "2024-01-19 10:20", "action": "导出分析报告「矿产预测报告」", "type": "info"},
]

for activity in activity_data:
    if activity["type"] == "success":
        icon = "✅"
    else:
        icon = "ℹ️"
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(icon)
    with col2:
        st.markdown(f"**{activity['action']}**")
    with col3:
        st.markdown(f"*{activity['time']}*", help="活动时间")

st.markdown("---")

# ============= 快速链接 =============
st.markdown("## 🔗 快速链接")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📘 API 文档", use_container_width=True):
        st.info("API 文档: http://localhost:8001/docs")

with col2:
    if st.button("💬 用户社区", use_container_width=True):
        st.info("用户社区: https://community.geologai.com")

with col3:
    if st.button("🆘 技术支持", use_container_width=True):
        st.info("支持邮箱: support@geologai.com")

with col4:
    if st.button("📋 反馈意见", use_container_width=True):
        st.info("请发送反馈至: feedback@geologai.com")

st.markdown("---")

# ============= 系统信息 =============
st.markdown("## ℹ️ 系统信息")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **平台版本**
    - GeologAI v2.0
    - Backend v2.0
    - Frontend v2.0
    """)

with col2:
    st.markdown("""
    **系统状态**
    - 🟢 后端服务: 正常
    - 🟢 数据库: 正常
    - 🟢 AI引擎: 就绪
    """)

with col3:
    st.markdown("""
    **最后同步**
    - 用户数据: 刚刚
    - 模型库: 本周更新
    - 配置: 最新
    """)

st.markdown("---")

# ============= 页脚 =============
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 用户协议", use_container_width=True):
        st.info("用户协议内容...")

with col2:
    if st.button("🔒 隐私政策", use_container_width=True):
        st.info("隐私政策内容...")

with col3:
    if st.button("❓ 常见问题", use_container_width=True):
        st.info("常见问题内容...")

st.markdown("")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2024 GeologAI | 版本 v2.0 | 保留所有权利</div>", unsafe_allow_html=True)
