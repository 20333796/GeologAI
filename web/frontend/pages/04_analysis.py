"""
曲线分析页面 - Phase 5d
支持测井曲线的交互式可视化和分析
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# 页面配置
st.set_page_config(
    page_title="曲线分析 | GeologAI",
    page_icon="📈",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8000"
DATA_ENDPOINT = f"{API_BASE_URL}/api/data"
ANALYSIS_ENDPOINT = f"{API_BASE_URL}/api/analysis"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

# 页面标题
st.title("📈 测井曲线分析")
st.markdown("---")

# 获取认证头
headers = {
    "Authorization": f"Bearer {st.session_state.auth_token}",
    "Content-Type": "application/json"
}

# ======================== 加载数据 ========================
@st.cache_data(ttl=30)
def get_projects():
    """获取项目列表"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/projects",
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

projects_dict = get_projects()

if not projects_dict:
    st.warning("⚠️ 请先创建项目和上传数据")
    st.stop()

# ======================== 侧边栏配置 ========================
with st.sidebar:
    st.subheader("⚙️ 分析配置")
    
    # 选择项目
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
    
    # 选择数据
    data_names = {i: d.get("well_name") for i, d in enumerate(data_list)}
    selected_data_idx = st.selectbox(
        "选择井号",
        list(data_names.keys()),
        format_func=lambda x: data_names[x]
    )
    
    selected_data = data_list[selected_data_idx]
    data_id = selected_data.get("id")
    
    st.markdown("---")
    
    # 分析选项
    analysis_type = st.radio(
        "分析类型",
        ["曲线展示", "相关性分析", "统计分析", "对比分析"]
    )
    
    st.markdown("---")
    
    # 显示数据信息
    st.subheader("📊 数据信息")
    st.metric("井号", selected_data.get("well_name"))
    st.metric("行数", selected_data.get("rows_count", 0))
    st.metric("文件", selected_data.get("filename"))

# ======================== 主内容区 ========================
# 加载数据
data_content = get_data_content(data_id)

if not data_content:
    st.error("❌ 无法加载数据")
    st.stop()

# 尝试将数据转换为 DataFrame
try:
    if isinstance(data_content.get("data"), list):
        df = pd.DataFrame(data_content["data"])
    else:
        st.error("❌ 数据格式错误")
        st.stop()
except Exception as e:
    st.error(f"❌ 数据处理错误: {str(e)}")
    st.stop()

# ======================== 曲线展示 ========================
if analysis_type == "曲线展示":
    st.subheader("📊 测井曲线展示")
    
    # 选择要展示的曲线
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_columns) == 0:
        st.warning("⚠️ 暂无数值型数据")
        st.stop()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_curves = st.multiselect(
            "选择曲线",
            numeric_columns,
            default=numeric_columns[:3] if len(numeric_columns) >= 3 else numeric_columns
        )
    
    with col2:
        chart_type = st.radio("图表类型", ["线图", "柱状图"])
    
    if selected_curves:
        # 创建图表
        if chart_type == "线图":
            fig = go.Figure()
            
            for curve in selected_curves:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[curve],
                    mode='lines',
                    name=curve,
                    hovertemplate=f"<b>{curve}</b><br>索引: %{{x}}<br>值: %{{y:.2f}}<extra></extra>"
                ))
            
            fig.update_layout(
                title=f"{selected_data.get('well_name')} - 测井曲线",
                xaxis_title="深度/时间",
                yaxis_title="数值",
                hovermode="x unified",
                height=600
            )
        else:
            # 柱状图 - 使用前20行演示
            display_df = df[selected_curves].head(20)
            fig = go.Figure(data=[
                go.Bar(name=col, x=display_df.index, y=display_df[col])
                for col in selected_curves
            ])
            
            fig.update_layout(
                title=f"{selected_data.get('well_name')} - 柱状图展示（前20行）",
                xaxis_title="索引",
                yaxis_title="数值",
                barmode='group',
                height=600
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 数据表格
    st.subheader("📋 数据表格")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        rows_to_show = st.slider("显示行数", 5, min(100, len(df)), 20)
    
    with col2:
        if st.checkbox("显示统计信息"):
            st.dataframe(df.describe(), use_container_width=True)
    
    st.dataframe(df.head(rows_to_show), use_container_width=True)

# ======================== 相关性分析 ========================
elif analysis_type == "相关性分析":
    st.subheader("📊 曲线相关性分析")
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_columns) < 2:
        st.warning("⚠️ 数值型列少于2个，无法进行相关性分析")
        st.stop()
    
    # 计算相关系数
    correlation_matrix = df[numeric_columns].corr()
    
    # 绘制热力图
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlation_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="相关系数")
    ))
    
    fig.update_layout(
        title=f"{selected_data.get('well_name')} - 曲线相关性热力图",
        height=600,
        width=700
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示相关系数详情
    st.subheader("📈 相关系数详情")
    
    # 找出相关性最强的曲线对
    correlation_pairs = []
    for i in range(len(numeric_columns)):
        for j in range(i + 1, len(numeric_columns)):
            corr_value = correlation_matrix.iloc[i, j]
            correlation_pairs.append({
                "曲线1": numeric_columns[i],
                "曲线2": numeric_columns[j],
                "相关系数": f"{corr_value:.3f}"
            })
    
    correlation_pairs.sort(key=lambda x: abs(float(x["相关系数"])), reverse=True)
    st.dataframe(
        pd.DataFrame(correlation_pairs[:10]),
        use_container_width=True,
        hide_index=True
    )

# ======================== 统计分析 ========================
elif analysis_type == "统计分析":
    st.subheader("📊 数据统计分析")
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_columns) == 0:
        st.warning("⚠️ 暂无数值型数据")
        st.stop()
    
    # 选择要分析的曲线
    selected_curve = st.selectbox("选择曲线", numeric_columns)
    
    # 显示统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均值", f"{df[selected_curve].mean():.2f}")
    with col2:
        st.metric("中位数", f"{df[selected_curve].median():.2f}")
    with col3:
        st.metric("标准差", f"{df[selected_curve].std():.2f}")
    with col4:
        st.metric("数据范围", f"{df[selected_curve].min():.2f} - {df[selected_curve].max():.2f}")
    
    st.markdown("---")
    
    # 分布直方图
    fig = go.Figure(data=[
        go.Histogram(
            x=df[selected_curve],
            nbinsx=50,
            name=selected_curve,
            hovertemplate="<b>%{x:.2f}</b><br>频数: %{y}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title=f"{selected_curve} - 分布直方图",
        xaxis_title="数值",
        yaxis_title="频数",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 箱线图
    fig = go.Figure(data=[
        go.Box(
            y=df[selected_curve],
            name=selected_curve,
            boxmean='sd'
        )
    ])
    
    fig.update_layout(
        title=f"{selected_curve} - 箱线图",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 对比分析 ========================
elif analysis_type == "对比分析":
    st.subheader("📊 多数据对比分析")
    
    data_list_all = get_data_list(project_id)
    
    if len(data_list_all) < 2:
        st.warning("⚠️ 需要至少2条数据进行对比")
        st.stop()
    
    # 选择对比数据
    data_indices = st.multiselect(
        "选择对比的数据",
        list(range(len(data_list_all))),
        format_func=lambda x: data_list_all[x].get("well_name"),
        max_selections=3
    )
    
    if len(data_indices) < 2:
        st.warning("⚠️ 请至少选择2条数据进行对比")
        st.stop()
    
    # 选择对比曲线
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    selected_curve = st.selectbox("选择对比曲线", numeric_columns)
    
    # 加载对比数据
    fig = go.Figure()
    
    for idx in data_indices:
        data_item = data_list_all[idx]
        data_id_temp = data_item.get("id")
        data_content_temp = get_data_content(data_id_temp)
        
        if data_content_temp and isinstance(data_content_temp.get("data"), list):
            try:
                df_temp = pd.DataFrame(data_content_temp["data"])
                if selected_curve in df_temp.columns:
                    fig.add_trace(go.Scatter(
                        x=df_temp.index,
                        y=df_temp[selected_curve],
                        mode='lines',
                        name=data_item.get("well_name"),
                        hovertemplate=f"<b>{data_item.get('well_name')}</b><br>值: %{{y:.2f}}<extra></extra>"
                    ))
            except:
                pass
    
    fig.update_layout(
        title=f"{selected_curve} - 多井对比",
        xaxis_title="深度/时间",
        yaxis_title="数值",
        hovermode="x unified",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📤 上传数据", use_container_width=True):
        st.switch_page("pages/03_data_upload.py")
with col2:
    if st.button("🤖 AI 预测", use_container_width=True):
        st.switch_page("pages/05_predictions.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
