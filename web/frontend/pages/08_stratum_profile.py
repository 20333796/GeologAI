"""
地层剖面页面 - Phase 5d
支持多井地层剖面展示、地层对比、深度标注
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="地层剖面 | GeologAI",
    page_icon="🪨",
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
st.title("🪨 地层剖面")
st.markdown("---")

# 获取认证头
headers = {
    "Authorization": f"Bearer {st.session_state.auth_token}",
    "Content-Type": "application/json"
}

# ======================== 辅助函数 ========================
@st.cache_data(ttl=30)
def get_projects():
    """获取项目列表"""
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

@st.cache_data(ttl=60)
def get_data_content(data_id):
    """获取数据详细内容"""
    try:
        response = requests.get(
            f"{DATA_ENDPOINT}/{data_id}",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ======================== 侧边栏配置 ========================
with st.sidebar:
    st.subheader("⚙️ 剖面配置")
    
    # 选择项目
    projects_dict = get_projects()
    if not projects_dict:
        st.warning("⚠️ 请先创建项目")
        st.stop()
    
    project_id = st.selectbox(
        "选择项目",
        list(projects_dict.keys()),
        format_func=lambda x: projects_dict[x]
    )
    
    # 获取数据列表
    data_list = get_data_list(project_id)
    if not data_list:
        st.warning("💡 该项目暂无数据")
        st.stop()
    
    # 选择多个井
    data_names = {i: d.get("well_name") for i, d in enumerate(data_list)}
    selected_data_indices = st.multiselect(
        "选择井号（按展示顺序）",
        list(data_names.keys()),
        format_func=lambda x: data_names[x],
        default=list(data_names.keys())[:min(3, len(data_names))]
    )
    
    if not selected_data_indices:
        st.warning("⚠️ 请至少选择一个井")
        st.stop()
    
    st.markdown("---")
    
    # 剖面配置
    st.subheader("📐 剖面配置")
    
    profile_type = st.radio(
        "剖面类型",
        ["岩性剖面", "物性剖面", "综合剖面"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        min_depth = st.number_input("最小深度 (m)", value=0.0)
    with col2:
        max_depth = st.number_input("最大深度 (m)", value=1000.0)
    
    st.markdown("---")
    
    # 地层设置
    st.subheader("🪨 地层设置")
    
    show_stratum_boundaries = st.checkbox("显示地层边界", value=True)
    show_stratum_names = st.checkbox("显示地层名称", value=True)
    show_grid = st.checkbox("显示网格", value=True)

# ======================== 加载数据 ========================
dfs = []
well_names = []
for idx in selected_data_indices:
    data_id = data_list[idx].get("id")
    data_content = get_data_content(data_id)
    
    if data_content and isinstance(data_content.get("data"), list):
        try:
            df = pd.DataFrame(data_content["data"])
            dfs.append(df)
            well_names.append(data_list[idx].get("well_name"))
        except:
            pass

if not dfs:
    st.error("❌ 无法加载任何数据")
    st.stop()

# ======================== 岩性剖面 ========================
if profile_type == "岩性剖面":
    st.subheader("🪨 岩性剖面展示")
    
    # 创建岩性编码字典
    stratum_colors = {
        "砂岩": "#FDB462",
        "泥岩": "#BEBADA",
        "灰岩": "#80B1D3",
        "页岩": "#8DD3C7",
        "砾岩": "#B3DE69"
    }
    
    # 生成地层数据
    fig = make_subplots(
        rows=1,
        cols=len(dfs),
        subplot_titles=[f"{name}" for name in well_names],
        specs=[[{"type": "bar"}] * len(dfs)]
    )
    
    stratum_types = ["砂岩", "泥岩", "灰岩", "页岩", "砾岩"]
    
    for col_idx, df in enumerate(dfs, 1):
        # 模拟地层数据
        depths = np.linspace(min_depth, max_depth, 10)
        stratum_sequence = np.random.choice(stratum_types, size=len(depths)-1)
        stratum_heights = np.diff(depths)
        
        # 添加地层柱状图
        for height_idx, (depth, stratum) in enumerate(zip(depths[:-1], stratum_sequence)):
            color = stratum_colors.get(stratum, "#CCCCCC")
            
            fig.add_trace(
                go.Bar(
                    y=[stratum_heights[height_idx]],
                    x=[col_idx],
                    orientation='v',
                    name=stratum,
                    marker=dict(color=color),
                    legendgroup=stratum,
                    showlegend=(col_idx == 1),
                    hovertemplate=f"<b>{stratum}</b><br>深度: {depth:.0f}m<br>厚度: {stratum_heights[height_idx]:.0f}m<extra></extra>",
                    text=stratum,
                    textposition="inside"
                ),
                row=1,
                col=col_idx
            )
    
    fig.update_layout(
        title="地层岩性剖面",
        height=600,
        barmode='stack',
        showlegend=True,
        hovermode='closest'
    )
    
    fig.update_yaxes(title_text="深度 (m)", row=1, col=1)
    fig.update_xaxes(showticklabels=False)
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 物性剖面 ========================
elif profile_type == "物性剖面":
    st.subheader("📊 物性剖面展示")
    
    # 获取数值列
    numeric_cols = set()
    for df in dfs:
        numeric_cols.update(df.select_dtypes(include=[np.number]).columns)
    
    numeric_cols = list(numeric_cols)
    
    if not numeric_cols:
        st.warning("⚠️ 没有数值列可用")
        st.stop()
    
    selected_property = st.selectbox("选择物性参数", numeric_cols)
    
    # 创建物性剖面
    fig = make_subplots(
        rows=1,
        cols=len(dfs),
        subplot_titles=[f"{name}" for name in well_names],
        specs=[[{"secondary_y": False}] * len(dfs)]
    )
    
    for col_idx, df in enumerate(dfs, 1):
        if selected_property not in df.columns:
            continue
        
        depth_idx = np.arange(len(df))
        values = df[selected_property]
        
        # 添加曲线
        fig.add_trace(
            go.Scatter(
                x=values,
                y=depth_idx,
                mode='lines',
                name=well_names[col_idx-1],
                line=dict(width=2),
                fill='tozerox',
                hovertemplate=f"{selected_property}: %{{x:.2f}}<br>深度: %{{y}}<extra></extra>"
            ),
            row=1,
            col=col_idx
        )
    
    fig.update_layout(
        title=f"{selected_property} 物性剖面",
        height=600,
        showlegend=False,
        hovermode='y unified'
    )
    
    fig.update_yaxes(title_text="深度", row=1, col=1, autorange="reversed")
    fig.update_xaxes(title_text=selected_property)
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 综合剖面 ========================
elif profile_type == "综合剖面":
    st.subheader("🔗 综合剖面展示")
    
    # 获取数值列
    numeric_cols = []
    for df in dfs:
        numeric_cols.extend(df.select_dtypes(include=[np.number]).columns)
    
    numeric_cols = list(set(numeric_cols))[:5]  # 最多 5 个参数
    
    if len(numeric_cols) < 2:
        st.warning("⚠️ 需要至少 2 个数值参数")
        st.stop()
    
    selected_props = st.multiselect(
        "选择显示的物性参数（最多3个）",
        numeric_cols,
        default=numeric_cols[:min(3, len(numeric_cols))],
        max_selections=3
    )
    
    if not selected_props:
        st.warning("⚠️ 请至少选择一个参数")
        st.stop()
    
    # 创建综合剖面
    num_props = len(selected_props)
    fig = make_subplots(
        rows=1,
        cols=len(dfs) * num_props,
        subplot_titles=[
            f"{well_names[well_idx]} - {prop}"
            for well_idx in range(len(dfs))
            for prop in selected_props
        ],
        specs=[[{"type": "scatter"}] * (len(dfs) * num_props)]
    )
    
    for well_idx, df in enumerate(dfs):
        for prop_idx, prop in enumerate(selected_props):
            col_idx = well_idx * num_props + prop_idx + 1
            
            if prop not in df.columns:
                continue
            
            depth = np.arange(len(df))
            values = df[prop]
            
            fig.add_trace(
                go.Scatter(
                    x=values,
                    y=depth,
                    mode='lines+markers',
                    name=prop,
                    line=dict(width=2),
                    hovertemplate=f"{prop}: %{{x:.2f}}<br>深度: %{{y}}<extra></extra>"
                ),
                row=1,
                col=col_idx
            )
    
    fig.update_layout(
        title="综合地层剖面",
        height=600,
        showlegend=False
    )
    
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 地层统计信息 ========================
st.markdown("---")
st.subheader("📈 地层统计")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("井数", len(dfs))
    
with col2:
    st.metric("深度范围", f"{min_depth:.0f} - {max_depth:.0f} m")
    
with col3:
    total_samples = sum(len(df) for df in dfs)
    st.metric("总样本数", total_samples)

# ======================== 地层数据表 ========================
st.subheader("📋 地层数据详情")

selected_well_for_table = st.selectbox(
    "选择井查看详细数据",
    range(len(dfs)),
    format_func=lambda x: well_names[x]
)

display_df = dfs[selected_well_for_table].head(20)
st.dataframe(display_df, use_container_width=True)

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎯 3D 可视化", use_container_width=True):
        st.switch_page("pages/07_3d_visualization.py")
with col2:
    if st.button("📊 数据分析", use_container_width=True):
        st.switch_page("pages/04_analysis.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
