"""
数据上传页面 - Phase 5c
支持 LAS、CSV、Excel 格式的测井数据上传
"""

import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="数据上传 | GeologAI",
    page_icon="📤",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8001"
DATA_ENDPOINT = f"{API_BASE_URL}/api/v1/data"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/api/v1/projects"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

# 页面标题
st.title("📤 测井数据上传")
st.markdown("---")

# 获取认证头
headers = {
    "Authorization": f"Bearer {st.session_state.auth_token}",
    "Content-Type": "application/json"
}

# ======================== 获取项目列表 ========================
def get_projects(use_cache=True):
    """从后端获取项目列表"""
    try:
        response = requests.get(
            PROJECTS_ENDPOINT,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            projects = response.json()
            return {p.get("id"): p.get("name") for p in projects}
        return {}
    except:
        return {}

# 初始化session_state标志
if "refresh_projects" not in st.session_state:
    st.session_state.refresh_projects = False

# 获取项目列表
projects_dict = get_projects()

if not projects_dict:
    st.warning("⚠️ 请先创建项目")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ 创建项目", use_container_width=True, type="primary"):
            st.session_state.refresh_projects = True
            st.switch_page("pages/02_dashboard.py")
    with col2:
        if st.button("🔄 刷新项目列表", use_container_width=True):
            st.rerun()
    st.stop()

# ======================== 数据上传表单 ========================
st.subheader("📤 上传测井数据")

with st.form("upload_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        project_id = st.selectbox(
            "选择项目",
            list(projects_dict.keys()),
            format_func=lambda x: projects_dict[x]
        )
    
    with col2:
        well_name = st.text_input(
            "井号/井名",
            placeholder="输入井号",
            max_chars=50
        )
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择数据文件",
        type=["las", "csv", "xlsx", "xls"],
        help="支持 LAS、CSV 和 Excel 格式"
    )
    
    # 数据描述
    data_description = st.text_area(
        "数据描述（可选）",
        placeholder="输入数据相关信息",
        height=80,
        max_chars=500
    )
    
    submit_upload = st.form_submit_button("✅ 上传数据", use_container_width=True)

if submit_upload:
    if not well_name:
        st.error("❌ 井号不能为空")
    elif not uploaded_file:
        st.error("❌ 请选择文件")
    else:
        with st.spinner("正在上传数据..."):
            try:
                # 准备文件上传
                files = {
                    'file': (uploaded_file.name, uploaded_file.getbuffer(), uploaded_file.type)
                }
                
                data = {
                    'project_id': str(project_id),
                    'well_name': well_name,
                    'description': data_description
                }
                
                # 上传到后端
                response = requests.post(
                    f"{DATA_ENDPOINT}/upload",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {st.session_state.auth_token}"},
                    timeout=30
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    st.success("✅ 数据上传成功！")
                    st.info(f"上传的文件: {uploaded_file.name}\n数据行数: {result.get('rows_count', 'N/A')}")
                else:
                    error_msg = response.json().get("detail", "未知错误")
                    st.error(f"❌ 上传失败: {error_msg}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到服务器")
            except requests.exceptions.Timeout:
                st.error("❌ 上传超时，请重试")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")

st.markdown("---")

# ======================== 已上传数据列表 ========================
st.subheader("📋 已上传的数据")

@st.cache_data(ttl=30)
def get_data_list(project_id):
    """获取项目下的数据列表"""
    try:
        response = requests.get(
            f"{DATA_ENDPOINT}?project_id={project_id}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# 选择项目查看数据
selected_project_for_view = st.selectbox(
    "查看数据",
    list(projects_dict.keys()),
    format_func=lambda x: projects_dict[x],
    key="view_project"
)

data_list = get_data_list(selected_project_for_view)

if data_list:
    # 显示数据表格
    data_display = []
    for data in data_list:
        data_display.append({
            "井号": data.get("well_name", "N/A"),
            "文件名": data.get("filename", "N/A"),
            "大小": f"{data.get('file_size', 0) / 1024:.1f} KB",
            "上传时间": data.get("uploaded_at", "N/A")[:10],
            "行数": data.get("rows_count", 0)
        })
    
    df = pd.DataFrame(data_display)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📊 数据预览")
    
    # 选择数据预览
    data_names = [d.get("well_name") for d in data_list]
    selected_data = st.selectbox(
        "选择数据预览",
        range(len(data_list)),
        format_func=lambda x: f"{data_list[x].get('well_name')} ({data_list[x].get('filename')})"
    )
    
    if selected_data is not None:
        selected_data_item = data_list[selected_data]
        
        # 显示数据信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("井号", selected_data_item.get("well_name", "N/A"))
        with col2:
            st.metric("行数", selected_data_item.get("rows_count", 0))
        with col3:
            st.metric("文件大小", f"{selected_data_item.get('file_size', 0) / 1024:.1f} KB")
        with col4:
            st.metric("上传时间", selected_data_item.get("uploaded_at", "N/A")[:10])
        
        # 预览数据（如果有）
        if selected_data_item.get("preview"):
            st.markdown("**数据预览：**")
            preview_data = pd.DataFrame(selected_data_item.get("preview", []))
            st.dataframe(preview_data, use_container_width=True)
        
        # 数据操作
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 下载", use_container_width=True):
                st.info("下载功能开发中...")
        
        with col2:
            if st.button("📈 分析", use_container_width=True):
                st.switch_page("pages/04_analysis.py")
        
        with col3:
            if st.button("🗑️ 删除", use_container_width=True):
                with st.spinner("正在删除数据..."):
                    try:
                        response = requests.delete(
                            f"{DATA_ENDPOINT}/{selected_data_item.get('id')}",
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ 数据已删除")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ 删除失败")
                    except Exception as e:
                        st.error(f"❌ 错误: {str(e)}")
else:
    st.info("💡 暂无数据，请先上传测井数据")

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📁 项目管理", use_container_width=True):
        st.switch_page("pages/02_dashboard.py")
with col2:
    st.caption("💡 支持格式: LAS, CSV, XLSX, XLS")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
