"""
深度学习模型页面 - Phase 5e
支持神经网络配置、模型编译、实时训练监控
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="深度学习 | GeologAI",
    page_icon="🧠",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8000"
DL_ENDPOINT = f"{API_BASE_URL}/api/deeplearning"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

st.title("🧠 深度学习模型")
st.markdown("---")

headers = {
    "Authorization": f"Bearer {st.session_state.auth_token}",
    "Content-Type": "application/json"
}

# ======================== 侧边栏配置 ========================
with st.sidebar:
    st.subheader("⚙️ 模型配置")
    
    # 模型架构选择
    model_type = st.selectbox(
        "模型架构",
        ["CNN", "RNN/LSTM", "全连接神经网络", "混合模型"]
    )
    
    st.markdown("---")
    
    # 模型参数
    st.subheader("🔧 网络参数")
    
    num_layers = st.slider("隐藏层数", 1, 10, 3)
    neurons_per_layer = st.number_input("每层神经元数", 32, 512, 128, 32)
    dropout_rate = st.slider("Dropout 比例", 0.0, 0.5, 0.2, 0.05)
    activation = st.selectbox("激活函数", ["ReLU", "Tanh", "Sigmoid", "ELU"])
    
    st.markdown("---")
    
    # 训练参数
    st.subheader("📊 训练参数")
    
    epochs = st.number_input("训练轮数", 10, 1000, 100, 10)
    batch_size = st.selectbox("批次大小", [16, 32, 64, 128, 256])
    learning_rate = st.number_input("学习率", 0.0001, 0.1, 0.001, 0.0001, format="%.5f")
    optimizer = st.selectbox("优化器", ["Adam", "SGD", "RMSprop", "Adagrad"])

# ======================== 主内容区 ========================
st.subheader("🧬 神经网络构建器")

# 展示模型架构
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**模型架构预览**")
    
    architecture_text = f"""
    ```
    输入层 (Input)
         ↓
    """
    
    for i in range(num_layers):
        architecture_text += f"    隐藏层 {i+1} ({neurons_per_layer} neurons, {activation}, Dropout={dropout_rate})\n         ↓\n"
    
    architecture_text += "    输出层 (Output)\n    ```"
    
    st.markdown(architecture_text)

with col2:
    st.metric("模型类型", model_type)
    st.metric("总层数", num_layers + 2)
    st.metric("总参数数", (neurons_per_layer ** 2) * num_layers)

# 模型编译配置
st.markdown("---")
st.subheader("⚙️ 模型编译")

col1, col2, col3 = st.columns(3)

with col1:
    loss_function = st.selectbox("损失函数", ["MSE", "MAE", "交叉熵", "Huber"])

with col2:
    metrics = st.multiselect(
        "评估指标",
        ["Accuracy", "Precision", "Recall", "F1-Score"],
        default=["Accuracy"]
    )

with col3:
    early_stopping = st.checkbox("启用早停", value=True)
    if early_stopping:
        patience = st.number_input("耐心值", 3, 50, 10)

# ======================== 模型训练 ========================
st.markdown("---")
st.subheader("🚀 模型训练")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 开始训练", use_container_width=True):
        with st.spinner("正在训练神经网络..."):
            try:
                training_config = {
                    "model_type": model_type,
                    "num_layers": num_layers,
                    "neurons_per_layer": neurons_per_layer,
                    "dropout_rate": dropout_rate,
                    "activation": activation,
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "learning_rate": learning_rate,
                    "optimizer": optimizer,
                    "loss_function": loss_function,
                    "metrics": metrics,
                    "early_stopping": early_stopping
                }
                
                response = requests.post(
                    f"{DL_ENDPOINT}/train",
                    json=training_config,
                    headers=headers,
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.dl_result = result
                    st.success("✅ 训练完成！")
                else:
                    st.error(f"❌ 训练失败: {response.json().get('detail', '未知错误')}")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")

with col2:
    if st.button("📊 导出模型", use_container_width=True):
        st.info("模型导出功能开发中...")

with col3:
    if st.button("🔄 重置", use_container_width=True):
        st.session_state.pop("dl_result", None)
        st.rerun()

# ======================== 训练结果展示 ========================
if "dl_result" in st.session_state:
    result = st.session_state.dl_result
    
    st.markdown("---")
    st.subheader("📈 训练结果")
    
    # 性能指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("最终精度", f"{result.get('final_accuracy', 0):.3f}")
    with col2:
        st.metric("最低损失", f"{result.get('min_loss', 0):.4f}")
    with col3:
        st.metric("训练时间", f"{result.get('training_time', 0):.1f}s")
    with col4:
        st.metric("模型大小", f"{result.get('model_size', 0) / 1024 / 1024:.2f} MB")
    
    # 训练曲线
    col1, col2 = st.columns(2)
    
    with col1:
        # 损失曲线
        training_loss = result.get("training_loss", [])
        validation_loss = result.get("validation_loss", [])
        
        if training_loss:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=training_loss, name="训练损失", mode='lines'))
            if validation_loss:
                fig.add_trace(go.Scatter(y=validation_loss, name="验证损失", mode='lines'))
            
            fig.update_layout(
                title="损失函数曲线",
                xaxis_title="轮次",
                yaxis_title="损失值",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 精度曲线
        training_acc = result.get("training_accuracy", [])
        validation_acc = result.get("validation_accuracy", [])
        
        if training_acc:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=training_acc, name="训练精度", mode='lines'))
            if validation_acc:
                fig.add_trace(go.Scatter(y=validation_acc, name="验证精度", mode='lines'))
            
            fig.update_layout(
                title="精度曲线",
                xaxis_title="轮次",
                yaxis_title="精度",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🤖 AI 预测", use_container_width=True):
        st.switch_page("pages/05_predictions.py")
with col2:
    if st.button("🎯 模型解释", use_container_width=True):
        st.switch_page("pages/12_model_interpretability.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
