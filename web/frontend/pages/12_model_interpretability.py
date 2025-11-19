"""
模型解释工具页面 - Phase 5e
支持 SHAP 特征解释、决策树可视化、性能分解
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="模型解释 | GeologAI",
    page_icon="🔍",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8000"
EXPLAIN_ENDPOINT = f"{API_BASE_URL}/api/explainability"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

st.title("🔍 模型解释工具")
st.markdown("---")

headers = {
    "Authorization": f"Bearer {st.session_state.auth_token}",
    "Content-Type": "application/json"
}

# ======================== 侧边栏配置 ========================
with st.sidebar:
    st.subheader("⚙️ 解释配置")
    
    # 解释方法
    explanation_method = st.selectbox(
        "解释方法",
        ["SHAP", "LIME", "特征重要性", "部分依赖", "ICE"]
    )
    
    st.markdown("---")
    
    # 模型选择
    model_id = st.selectbox(
        "选择模型",
        ["model_1", "model_2", "model_3"],
        format_func=lambda x: {"model_1": "模型 v1", "model_2": "模型 v2", "model_3": "模型 v3"}.get(x)
    )
    
    st.markdown("---")
    
    # 样本选择
    sample_type = st.radio(
        "样本类型",
        ["随机样本", "代表性样本", "异常样本", "边界样本"]
    )

# ======================== SHAP 解释 ========================
if explanation_method == "SHAP":
    st.subheader("📊 SHAP 特征解释")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**SHAP 值力图 (Force Plot)**")
        
        # 模拟 SHAP 解释
        base_value = 0.5
        feature_names = ["GR", "RT", "DEN", "NEU", "SP"]
        shap_values = np.random.randn(5) * 0.2
        feature_values = np.random.rand(5)
        
        # 创建力图
        fig = go.Figure()
        
        colors = ["red" if x < 0 else "green" for x in shap_values]
        
        fig.add_trace(go.Bar(
            y=feature_names,
            x=shap_values,
            orientation='h',
            marker=dict(color=colors),
            text=shap_values,
            textposition="outside"
        ))
        
        fig.update_layout(
            title=f"SHAP 值 (基础值: {base_value:.3f})",
            xaxis_title="SHAP 值",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**数值总结**")
        for i, name in enumerate(feature_names):
            st.metric(
                name,
                f"{shap_values[i]:+.4f}",
                f"原值: {feature_values[i]:.3f}"
            )
    
    # 水平 SHAP 总结图
    st.markdown("---")
    st.markdown("**SHAP 摘要图 (Beeswarm)**")
    
    # 多个样本的 SHAP 值
    num_samples = 100
    shap_matrix = np.random.randn(num_samples, 5) * 0.2
    
    fig = go.Figure()
    for i, name in enumerate(feature_names):
        fig.add_trace(go.Scatter(
            y=[name] * num_samples,
            x=shap_matrix[:, i],
            mode='markers',
            name=name,
            marker=dict(
                size=8,
                color=shap_matrix[:, i],
                colorscale='RdBu',
                showscale=(i == 0),
                line=dict(width=0.5)
            ),
            hovertemplate=f"<b>{name}</b><br>SHAP 值: %{{x:.4f}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="SHAP 摘要图 - 所有样本",
        xaxis_title="SHAP 值",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== LIME 解释 ========================
elif explanation_method == "LIME":
    st.subheader("🔬 LIME 局部解释")
    
    st.info("LIME (Local Interpretable Model-agnostic Explanations) 通过在预测点附近生成可解释的局部模型来解释单个预测")
    
    # 输入特征
    st.markdown("**输入特征**")
    col1, col2, col3 = st.columns(3)
    
    feature1 = col1.number_input("特征 1", value=0.5)
    feature2 = col2.number_input("特征 2", value=0.5)
    feature3 = col3.number_input("特征 3", value=0.5)
    
    if st.button("🔍 生成 LIME 解释", use_container_width=True):
        # 模拟 LIME 解释
        feature_names = ["GR", "RT", "DEN"]
        feature_values = [feature1, feature2, feature3]
        lime_weights = np.array([0.4, 0.35, 0.25])
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=feature_names,
            x=lime_weights,
            orientation='h',
            marker=dict(color='steelblue'),
            text=lime_weights,
            textposition="outside"
        ))
        
        fig.update_layout(
            title="LIME 特征权重",
            xaxis_title="权重",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 局部模型
        st.markdown("**局部线性模型系数**")
        
        lime_df = pd.DataFrame({
            "特征": feature_names,
            "系数": lime_weights,
            "实际值": feature_values,
            "贡献度": lime_weights * np.array(feature_values)
        })
        
        st.dataframe(lime_df, use_container_width=True)

# ======================== 特征重要性 ========================
elif explanation_method == "特征重要性":
    st.subheader("⭐ 特征重要性排名")
    
    col1, col2 = st.columns(2)
    
    with col1:
        importance_type = st.selectbox(
            "重要性类型",
            ["Gini", "增益", "覆盖范围", "Permutation"]
        )
    
    with col2:
        top_k = st.slider("显示前 K 个特征", 5, 50, 15, 5)
    
    # 生成特征重要性数据
    feature_names = ["GR", "RT", "DEN", "NEU", "SP", "CALI", "RES", "POR", "SAT", "PERM"][:top_k]
    importances = np.sort(np.random.exponential(1, top_k))[::-1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=importances,
        y=feature_names,
        orientation='h',
        marker=dict(
            color=importances,
            colorscale='Viridis'
        ),
        text=importances,
        textposition="outside"
    ))
    
    fig.update_layout(
        title=f"特征重要性排名 ({importance_type})",
        xaxis_title="重要性得分",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 累积贡献度
    cumulative = np.cumsum(importances) / np.sum(importances)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=range(len(feature_names)),
        y=cumulative,
        mode='lines+markers',
        fill='tozeroy',
        name='累积贡献度'
    ))
    
    # 添加 80% 线
    fig.add_hline(
        y=0.8,
        line_dash="dash",
        line_color="red",
        annotation_text="80% 贡献度"
    )
    
    fig.update_layout(
        title="特征累积贡献度",
        xaxis_title="特征排名",
        yaxis_title="累积贡献度",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 部分依赖 ========================
elif explanation_method == "部分依赖":
    st.subheader("📈 部分依赖图 (PDP)")
    
    selected_feature = st.selectbox(
        "选择特征",
        ["GR", "RT", "DEN", "NEU", "SP"]
    )
    
    # 生成 PDP 数据
    feature_range = np.linspace(0, 1, 50)
    pdp_values = 0.5 + 0.3 * np.sin(feature_range * np.pi)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=feature_range,
        y=pdp_values,
        mode='lines+markers',
        fill='tozeroy',
        name=selected_feature
    ))
    
    fig.update_layout(
        title=f"{selected_feature} 部分依赖图",
        xaxis_title=f"{selected_feature} 值",
        yaxis_title="预测输出",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== ICE 曲线 ========================
elif explanation_method == "ICE":
    st.subheader("🧊 个体条件期望 (ICE)")
    
    selected_feature = st.selectbox(
        "选择特征",
        ["GR", "RT", "DEN", "NEU", "SP"]
    )
    
    # 生成 ICE 数据
    num_samples = 30
    feature_range = np.linspace(0, 1, 50)
    
    fig = go.Figure()
    
    for i in range(num_samples):
        ice_values = 0.5 + 0.3 * np.sin(feature_range * np.pi) + np.random.randn() * 0.05
        fig.add_trace(go.Scatter(
            x=feature_range,
            y=ice_values,
            mode='lines',
            name=f'样本 {i+1}',
            showlegend=False,
            opacity=0.3
        ))
    
    # 添加平均 PDP
    pdp_avg = 0.5 + 0.3 * np.sin(feature_range * np.pi)
    fig.add_trace(go.Scatter(
        x=feature_range,
        y=pdp_avg,
        mode='lines',
        name='平均 (PDP)',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title=f"{selected_feature} ICE 曲线",
        xaxis_title=f"{selected_feature} 值",
        yaxis_title="预测输出",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ======================== 模型性能分解 ========================
st.markdown("---")
st.subheader("📊 模型性能分解")

col1, col2 = st.columns(2)

with col1:
    # 混淆矩阵
    st.markdown("**混淆矩阵**")
    
    confusion_matrix = np.array([[90, 10], [15, 85]])
    
    fig = go.Figure(data=go.Heatmap(
        z=confusion_matrix,
        x=["预测负", "预测正"],
        y=["实际负", "实际正"],
        text=confusion_matrix,
        texttemplate="%{text}",
        colorscale='Blues'
    ))
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # 性能指标
    st.markdown("**性能指标**")
    
    tp, fn, fp, tn = 85, 15, 10, 90
    
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("精度 (Accuracy)", f"{accuracy:.3f}")
        st.metric("召回率 (Recall)", f"{recall:.3f}")
    with col2:
        st.metric("精确率 (Precision)", f"{precision:.3f}")
        st.metric("F1-Score", f"{f1:.3f}")

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⚡ 实时预测", use_container_width=True):
        st.switch_page("pages/11_realtime_predictions.py")
with col2:
    if st.button("🧠 深度学习", use_container_width=True):
        st.switch_page("pages/10_deep_learning.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
