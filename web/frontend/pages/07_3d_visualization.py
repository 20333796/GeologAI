"""
3D 可视化页面 - Phase 5d
支持 3D 曲线展示、钻孔轨迹、地层结构可视化
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="3D 可视化 | GeologAI",
    page_icon="🎯",
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
st.title("🎯 3D 可视化")
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
    st.subheader("⚙️ 3D 可视化配置")
    
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
    
    # 选择单个或多个数据
    data_names = {i: d.get("well_name") for i, d in enumerate(data_list)}
    selected_data_indices = st.multiselect(
        "选择井号",
        list(data_names.keys()),
        format_func=lambda x: data_names[x],
        default=[0] if data_names else []
    )
    
    if not selected_data_indices:
        st.warning("⚠️ 请至少选择一个井")
        st.stop()
    
    st.markdown("---")
    
    # 可视化类型
    viz_type = st.radio(
        "可视化类型",
        ["3D 散点图", "3D 曲线", "3D 钻孔轨迹", "多井对比"]
    )
    
    st.markdown("---")
    
    # 显示数据信息
    st.subheader("📊 数据概览")
    for idx in selected_data_indices[:3]:  # 最多显示 3 个
        data_item = data_list[idx]
        st.metric(
            data_item.get("well_name"),
            f"{data_item.get('rows_count', 0)} 行"
        )

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

# ======================== 3D 散点图 ========================
if viz_type == "3D 散点图":
    st.subheader("🎯 3D 散点图")
    
    df = dfs[0]
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_columns) < 3:
        st.warning("⚠️ 需要至少 3 个数值列来创建 3D 散点图")
        st.stop()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x_col = st.selectbox("X 轴", numeric_columns, index=0)
    with col2:
        y_col = st.selectbox("Y 轴", numeric_columns, index=1 if len(numeric_columns) > 1 else 0)
    with col3:
        z_col = st.selectbox("Z 轴", numeric_columns, index=2 if len(numeric_columns) > 2 else 0)
    
    # 创建 3D 散点图
    fig = go.Figure(data=[go.Scatter3d(
        x=df[x_col],
        y=df[y_col],
        z=df[z_col],
        mode='markers',
        marker=dict(
            size=4,
            color=df[z_col],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=z_col)
        ),
        text=df.index,
        hovertemplate=f'<b>{x_col}</b>: %{{x:.2f}}<br><b>{y_col}</b>: %{{y:.2f}}<br><b>{z_col}</b>: %{{z:.2f}}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"{well_names[0]} - 3D 散点图",
        scene=dict(
            xaxis_title=x_col,
            yaxis_title=y_col,
            zaxis_title=z_col
        ),
        height=700,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示统计信息
    st.markdown("---")
    st.subheader("📊 数据统计")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{x_col} 范围", f"{df[x_col].min():.2f} - {df[x_col].max():.2f}")
    with col2:
        st.metric(f"{y_col} 范围", f"{df[y_col].min():.2f} - {df[y_col].max():.2f}")
    with col3:
        st.metric(f"{z_col} 范围", f"{df[z_col].min():.2f} - {df[z_col].max():.2f}")

# ======================== 3D 曲线 ========================
elif viz_type == "3D 曲线":
    st.subheader("📈 3D 曲线")
    
    df = dfs[0]
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_columns) < 2:
        st.warning("⚠️ 需要至少 2 个数值列")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        curve1 = st.selectbox("曲线 1", numeric_columns, index=0)
    with col2:
        curve2 = st.selectbox("曲线 2", numeric_columns, index=1 if len(numeric_columns) > 1 else 0)
    
    # 创建深度作为 Z 轴
    depth = np.arange(len(df))
    
    fig = go.Figure()
    
    # 添加第一条曲线
    fig.add_trace(go.Scatter3d(
        x=df[curve1],
        y=[0] * len(df),
        z=depth,
        mode='lines',
        name=curve1,
        line=dict(color='blue', width=5),
        hovertemplate=f'<b>{curve1}</b>: %{{x:.2f}}<br><b>深度</b>: %{{z}}<extra></extra>'
    ))
    
    # 添加第二条曲线
    fig.add_trace(go.Scatter3d(
        x=df[curve2],
        y=[1] * len(df),
        z=depth,
        mode='lines',
        name=curve2,
        line=dict(color='red', width=5),
        hovertemplate=f'<b>{curve2}</b>: %{{x:.2f}}<br><b>深度</b>: %{{z}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{well_names[0]} - 3D 曲线对比",
        scene=dict(
            xaxis_title="数值",
            yaxis_title="曲线",
            zaxis_title="深度",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=700,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 3D 钻孔轨迹 ========================
elif viz_type == "3D 钻孔轨迹":
    st.subheader("🕳️ 3D 钻孔轨迹")
    
    st.info("💡 3D 钻孔轨迹模拟")
    
    # 生成模拟的钻孔轨迹
    num_wells = len(selected_data_indices)
    
    fig = go.Figure()
    
    for idx, well_idx in enumerate(selected_data_indices[:5]):  # 最多 5 个井
        df = dfs[idx] if idx < len(dfs) else None
        if df is None or len(df) < 10:
            continue
        
        well_name = well_names[idx]
        
        # 生成三维坐标
        depth = np.arange(len(df))
        
        # 模拟钻孔轨迹（略微偏斜）
        angle = idx * 30  # 不同的井角度
        x = 100 * np.sin(np.radians(angle)) + np.random.randn(len(df)) * 5
        y = 100 * np.cos(np.radians(angle)) + np.random.randn(len(df)) * 5
        z = depth
        
        # 添加钻孔轨迹
        fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines+markers',
            name=well_name,
            line=dict(width=8),
            marker=dict(size=3),
            hovertemplate=f'<b>{well_name}</b><br>深度: %{{z}}<extra></extra>'
        ))
        
        # 添加井口标记
        fig.add_trace(go.Scatter3d(
            x=[x[0]],
            y=[y[0]],
            z=[z[0]],
            mode='markers+text',
            name=f"{well_name} (井口)",
            marker=dict(size=12, color='red'),
            text=[well_name],
            textposition="top center",
            hovertemplate=f'<b>{well_name} 井口</b><extra></extra>'
        ))
    
    fig.update_layout(
        title="3D 钻孔轨迹图",
        scene=dict(
            xaxis_title="东西方向 (m)",
            yaxis_title="南北方向 (m)",
            zaxis_title="深度 (m)",
            zaxis=dict(autorange="reversed"),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=700,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 多井对比 ========================
elif viz_type == "多井对比":
    st.subheader("🔄 多井 3D 对比")
    
    if len(dfs) < 2:
        st.warning("⚠️ 需要至少 2 个井数据进行对比")
        st.stop()
    
    # 选择对比曲线
    all_cols = set()
    for df in dfs:
        all_cols.update(df.select_dtypes(include=[np.number]).columns)
    
    all_cols = list(all_cols)
    
    if len(all_cols) < 1:
        st.warning("⚠️ 没有数值列可用于对比")
        st.stop()
    
    selected_curve = st.selectbox("选择对比曲线", all_cols)
    
    # 创建多井对比图
    fig = go.Figure()
    
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    for idx, df in enumerate(dfs[:5]):  # 最多 5 个井
        if selected_curve not in df.columns:
            continue
        
        well_name = well_names[idx]
        depth = np.arange(len(df))
        
        fig.add_trace(go.Scatter3d(
            x=df[selected_curve],
            y=[idx] * len(df),
            z=depth,
            mode='lines',
            name=well_name,
            line=dict(color=colors[idx % len(colors)], width=5),
            hovertemplate=f'<b>{well_name}</b><br>{selected_curve}: %{{x:.2f}}<br>深度: %{{z}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"多井 {selected_curve} 对比",
        scene=dict(
            xaxis_title=f"{selected_curve}",
            yaxis_title="井号",
            zaxis_title="深度 (m)",
            zaxis=dict(autorange="reversed"),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=700,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📈 曲线分析", use_container_width=True):
        st.switch_page("pages/04_analysis.py")
with col2:
    if st.button("🪨 地层剖面", use_container_width=True):
        st.switch_page("pages/08_stratum_profile.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
