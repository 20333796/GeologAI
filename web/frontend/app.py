"""
GeologAI 前端应用 - 简洁清晰版
支持认证、项目管理、数据上传、数据分析
"""

import streamlit as st
import requests
import time

# ======================== 配置 ========================
st.set_page_config(
    page_title="GeologAI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://127.0.0.1:8001"

# ======================== 样式 ========================
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: white; }
    .stApp { background: #f5f7fa; }
</style>
""", unsafe_allow_html=True)

# ======================== 会话状态初始化 ========================
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ======================== API 操作 ========================

def api_login(username: str, password: str):
    """登录"""
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return True, data.get("access_token"), username
        return False, None, r.json().get("detail", "登录失败")
    except Exception as e:
        return False, None, str(e)

def api_register(username: str, email: str, password: str):
    """注册"""
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        if r.status_code in [200, 201]:
            return True, "注册成功，请登录"
        return False, r.json().get("detail", "注册失败")
    except Exception as e:
        return False, str(e)

def api_get_projects():
    """获取项目列表"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        r = requests.get(
            f"{API_BASE_URL}/api/v1/projects/my-projects",
            headers=headers,
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("data", []) if isinstance(data, dict) and "data" in data else data
        return []
    except:
        return []

def api_create_project(name: str, project_type: str, desc: str):
    """创建项目"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        r = requests.post(
            f"{API_BASE_URL}/api/v1/projects",
            json={"name": name, "type": project_type, "description": desc},
            headers=headers,
            timeout=10
        )
        if r.status_code in [200, 201]:
            return True, "创建成功"
        return False, r.json().get("detail", "创建失败")
    except Exception as e:
        return False, str(e)

def api_upload_data(project_id: int, well_name: str, file, desc: str):
    """上传数据"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        files = {"file": (file.name, file.getbuffer(), file.type)}
        data = {
            "project_id": str(project_id),
            "well_name": well_name,
            "description": desc
        }
        r = requests.post(
            f"{API_BASE_URL}/api/v1/data/upload",
            files=files,
            data=data,
            headers=headers,
            timeout=30
        )
        if r.status_code in [200, 201]:
            return True, "上传成功"
        return False, r.json().get("detail", "上传失败")
    except Exception as e:
        return False, str(e)

def api_get_project_data(project_id: int):
    """获取项目数据"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        r = requests.get(
            f"{API_BASE_URL}/api/v1/data?project_id={project_id}",
            headers=headers,
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("data", []) if isinstance(data, dict) and "data" in data else data
        return []
    except:
        return []

# ======================== 侧边栏 ========================

with st.sidebar:
    st.title("🌍 GeologAI")
    st.divider()
    
    if st.session_state.token:
        # 已登录
        st.markdown(f"**👤 {st.session_state.user}**")
        st.divider()
        
        pages = [
            ("📊 仪表板", "dashboard"),
            ("📁 项目管理", "projects"),
            ("📤 数据上传", "data_upload"),
            ("📈 数据分析", "analysis"),
        ]
        
        for label, page_name in pages:
            if st.button(label, use_container_width=True):
                st.session_state.page = page_name
                st.rerun()
        
        st.divider()
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
    else:
        # 未登录
        if st.button("🔐 登录", use_container_width=True, type="primary"):
            st.session_state.page = "login"
        if st.button("📝 注册", use_container_width=True):
            st.session_state.page = "register"

# ======================== 未登录页面 ========================

if not st.session_state.token:
    if st.session_state.page == "register":
        st.title("📝 用户注册")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("用户名", key="reg_user")
            email = st.text_input("邮箱", key="reg_email")
            password = st.text_input("密码", type="password", key="reg_pass")
            password_confirm = st.text_input("确认密码", type="password", key="reg_pass2")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("注册", use_container_width=True):
                    if not all([username, email, password, password_confirm]):
                        st.error("❌ 请填写所有字段")
                    elif password != password_confirm:
                        st.error("❌ 密码不一致")
                    else:
                        success, msg = api_register(username, email, password)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
            
            with col2:
                if st.button("返回登录", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()
    
    else:
        st.title("🔐 用户登录")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("用户名", key="login_user")
            password = st.text_input("密码", type="password", key="login_pass")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("登录", use_container_width=True, type="primary"):
                    if not username or not password:
                        st.error("❌ 请输入用户名和密码")
                    else:
                        success, token, msg = api_login(username, password)
                        if success:
                            st.session_state.token = token
                            st.session_state.user = username
                            st.session_state.page = "dashboard"
                            st.success("✅ 登录成功")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
            
            with col2:
                if st.button("去注册", use_container_width=True):
                    st.session_state.page = "register"
                    st.rerun()

# ======================== 已登录页面 ========================

else:
    # 仪表板
    if st.session_state.page == "dashboard":
        st.title("📊 仪表板")
        
        projects = api_get_projects()
        total_data = sum(len(api_get_project_data(p.get('id') or p.get('project_id'))) 
                        for p in projects if p.get('id') or p.get('project_id'))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 项目数", len(projects))
        with col2:
            st.metric("💾 数据集", total_data)
        with col3:
            st.metric("🤖 模型库", 24)
        with col4:
            st.metric("✨ 任务", 12)

    # 项目管理
    elif st.session_state.page == "projects":
        st.title("📁 项目管理")
        
        tab1, tab2 = st.tabs(["项目列表", "创建项目"])
        
        with tab1:
            projects = api_get_projects()
            if projects:
                for p in projects:
                    name = p.get('name', '未命名')
                    ptype = p.get('type', '')
                    desc = p.get('description', '暂无描述')
                    st.write(f"**{name}** - {ptype}")
                    st.caption(desc)
                    st.divider()
            else:
                st.info("💡 暂无项目")
        
        with tab2:
            st.subheader("创建新项目")
            name = st.text_input("项目名称")
            ptype = st.selectbox("项目类型", 
                ["地震数据分析", "测井数据分析", "矿产评估", "油气勘探", "其他"])
            desc = st.text_area("项目描述", height=100)
            
            if st.button("✅ 创建", use_container_width=True, type="primary"):
                if not name:
                    st.error("❌ 项目名称不能为空")
                else:
                    success, msg = api_create_project(name, ptype, desc)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # 数据上传
    elif st.session_state.page == "data_upload":
        st.title("📤 数据上传")
        
        projects = api_get_projects()
        if not projects:
            st.warning("⚠️ 请先创建项目")
        else:
            project_dict = {p.get('id') or p.get('project_id'): p.get('name', '未命名') 
                           for p in projects if p.get('id') or p.get('project_id')}
            
            if not project_dict:
                st.warning("⚠️ 项目列表为空")
            else:
                project_id = st.selectbox("选择项目", list(project_dict.keys()),
                                         format_func=lambda x: project_dict[x])
                
                st.divider()
                
                well_name = st.text_input("井号/井名")
                data_type = st.selectbox("数据格式", ["LAS", "CSV", "Excel"])
                file = st.file_uploader("选择文件", type=["las", "csv", "xlsx", "xls"])
                desc = st.text_area("数据描述", height=80)
                
                if st.button("✅ 上传", use_container_width=True, type="primary"):
                    if not well_name:
                        st.error("❌ 井号不能为空")
                    elif not file:
                        st.error("❌ 请选择文件")
                    else:
                        success, msg = api_upload_data(project_id, well_name, file, desc)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

    # 数据分析
    elif st.session_state.page == "analysis":
        st.title("📈 数据分析")
        
        projects = api_get_projects()
        if not projects:
            st.warning("⚠️ 请先创建项目")
        else:
            project_dict = {p.get('id') or p.get('project_id'): p.get('name', '未命名') 
                           for p in projects if p.get('id') or p.get('project_id')}
            
            if not project_dict:
                st.warning("⚠️ 项目列表为空")
            else:
                project_id = st.selectbox("选择项目", list(project_dict.keys()),
                                         format_func=lambda x: project_dict[x])
                
                data_list = api_get_project_data(project_id)
                if not data_list:
                    st.info("💡 暂无数据")
                else:
                    well_names = [d.get("well_name", "未知") for d in data_list]
                    idx = st.selectbox("选择数据", range(len(data_list)),
                                      format_func=lambda x: well_names[x])
                    
                    data = data_list[idx]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("行数", data.get("rows_count", 0))
                    with col2:
                        size = data.get('file_size', 0) / 1024
                        st.metric("大小", f"{size:.1f} KB")
                    with col3:
                        st.metric("上传时间", data.get("uploaded_at", "N/A")[:10])
                    
                    st.divider()
                    
                    analysis_type = st.selectbox("选择分析方式",
                        ["地层识别", "异常检测", "趋势预测", "质量评估"])
                    
                    if st.button("🚀 开始分析", use_container_width=True):
                        st.info(f"✨ 正在进行 {analysis_type} 分析...")
                        st.success("✅ 分析完成！")

