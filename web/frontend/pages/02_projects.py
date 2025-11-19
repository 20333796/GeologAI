"""
项目管理页面 - Phase 5c
用户项目管理和创建
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="项目管理 | GeologAI",
    page_icon="📁",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8000"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/api/projects"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

# 页面标题
st.title("📁 项目管理")
st.markdown("---")

# 获取认证头
headers = {
    "Authorization": f"Bearer {st.session_state.auth_token}",
    "Content-Type": "application/json"
}

# ======================== 获取项目列表 ========================
@st.cache_data(ttl=30)
def get_projects():
    """从后端获取项目列表"""
    try:
        response = requests.get(
            PROJECTS_ENDPOINT,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ 获取项目失败: {response.json().get('detail', '未知错误')}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到服务器")
        return []
    except Exception as e:
        st.error(f"❌ 错误: {str(e)}")
        return []

# ======================== 创建项目表单 ========================
st.subheader("➕ 创建新项目")

with st.form("create_project_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input(
            "项目名称",
            placeholder="输入项目名称",
            max_chars=100
        )
    
    with col2:
        project_location = st.text_input(
            "位置/地区",
            placeholder="输入项目位置",
            max_chars=100
        )
    
    project_description = st.text_area(
        "项目描述",
        placeholder="输入项目描述",
        height=100,
        max_chars=500
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        well_count = st.number_input("井数", min_value=0, value=1)
    with col2:
        depth_from = st.number_input("起始深度 (m)", min_value=0.0, value=0.0)
    with col3:
        depth_to = st.number_input("结束深度 (m)", min_value=0.0, value=1000.0)
    
    submit_create = st.form_submit_button("✅ 创建项目", use_container_width=True)

if submit_create:
    if not project_name:
        st.error("❌ 项目名称不能为空")
    else:
        with st.spinner("正在创建项目..."):
            try:
                payload = {
                    "name": project_name,
                    "location": project_location,
                    "description": project_description,
                    "well_count": well_count,
                    "depth_from": depth_from,
                    "depth_to": depth_to
                }
                
                response = requests.post(
                    PROJECTS_ENDPOINT,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    st.success("✅ 项目创建成功！")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ 创建失败: {response.json().get('detail', '未知错误')}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到服务器")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")

st.markdown("---")

# ======================== 项目列表 ========================
st.subheader("📋 我的项目")

projects = get_projects()

if not projects:
    st.info("💡 暂无项目，请创建第一个项目！")
else:
    # 以表格形式显示项目
    if isinstance(projects, list) and len(projects) > 0:
        # 转换为 DataFrame
        project_data = []
        for project in projects:
            project_data.append({
                "项目名称": project.get("name", "N/A"),
                "位置": project.get("location", "N/A"),
                "井数": project.get("well_count", 0),
                "创建时间": project.get("created_at", "N/A")[:10],
                "ID": project.get("id", "N/A")
            })
        
        df = pd.DataFrame(project_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("📊 项目详情")
        
        # 项目选择
        selected_project = st.selectbox(
            "选择项目查看详情",
            [p.get("name") for p in projects],
            key="project_select"
        )
        
        # 显示选中项目的详情
        for project in projects:
            if project.get("name") == selected_project:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("项目名称", project.get("name", "N/A"))
                
                with col2:
                    st.metric("位置", project.get("location", "N/A"))
                
                with col3:
                    st.metric("井数", project.get("well_count", 0))
                
                st.markdown("**项目描述:**")
                st.info(project.get("description", "无描述"))
                
                # 项目操作
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📁 查看数据", use_container_width=True):
                        st.session_state.selected_project_id = project.get("id")
                        st.switch_page("pages/03_data_upload.py")
                
                with col2:
                    if st.button("✏️ 编辑", use_container_width=True):
                        st.info("编辑功能开发中...")
                
                with col3:
                    if st.button("🗑️ 删除", use_container_width=True):
                        with st.spinner("正在删除项目..."):
                            try:
                                project_id = project.get("id")
                                response = requests.delete(
                                    f"{PROJECTS_ENDPOINT}/{project_id}",
                                    headers=headers,
                                    timeout=10
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ 项目已删除")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
                            except Exception as e:
                                st.error(f"❌ 错误: {str(e)}")
                
                break
    else:
        st.warning("⚠️ 获取项目列表失败")

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 返回首页", use_container_width=True):
        st.switch_page("web/frontend/app.py")
with col2:
    st.caption("💡 提示: 创建项目后可以上传测井数据")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
