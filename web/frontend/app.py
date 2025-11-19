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

# 侧边栏
st.sidebar.title("🌍 测井AI平台")
page = st.sidebar.radio(
    "导航",
    ["数据上传", "曲线分析", "AI预测", "模型训练"]
)

API_URL = "http://localhost:8000"

# 页面1：数据上传
if page == "数据上传":
    st.title("📁 测井数据上传")
    
    st.info("📌 上传功能开发中，目前支持以下操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("支持的文件格式")
        st.markdown("""
        - **LAS 格式**: LAS 2.0, LAS 3.0
        - **CSV 格式**: 标准逗号分隔
        - **Excel 格式**: .xlsx, .xls
        """)
    
    with col2:
        st.subheader("常见测井曲线")
        st.markdown("""
        - **GR**: 自然伽马 (API)
        - **RT**: 真实电阻率 (Ω·m)
        - **DEN**: 密度 (g/cm³)
        - **NEU**: 中子孔隙度 (%)
        - **SP**: 自然电位 (mV)
        - **CALI**: 套管井径 (inch)
        """)
    
    st.divider()
    
    st.subheader("示例数据")
    if st.button("加载示例数据集"):
        import numpy as np
        
        # 创建示例数据
        depth = np.arange(1000, 2000, 1)
        sample_data = pd.DataFrame({
            "DEPTH": depth,
            "GR": 50 + 30 * np.sin(depth / 100) + np.random.randn(len(depth)) * 5,
            "RT": 10 + 5 * np.cos(depth / 80) + np.random.randn(len(depth)) * 2,
            "DEN": 2.2 + 0.3 * np.sin(depth / 150) + np.random.randn(len(depth)) * 0.1
        })
        
        st.success("✅ 示例数据已加载")
        st.dataframe(sample_data.head(10), use_container_width=True)
        st.download_button(
            label="📥 下载示例数据 (CSV)",
            data=sample_data.to_csv(index=False),
            file_name="well_log_sample.csv",
            mime="text/csv"
        )

# 页面2：曲线分析
elif page == "曲线分析":
    st.title("📊 测井曲线分析")
    
    st.info("📌 展示测井曲线的分析和可视化")
    
    # 示例数据可视化
    if st.button("加载示例数据"):
        # 生成示例数据
        import numpy as np
        depth = np.arange(1000, 2000, 0.5)
        gr = 50 + 30 * np.sin(depth / 50) + np.random.randn(len(depth)) * 5
        rt = 10 + 5 * np.cos(depth / 30) + np.random.randn(len(depth)) * 2
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=depth,
            x=gr,
            mode='lines',
            name='自然伽马(GR)',
            line=dict(color='green', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            y=depth,
            x=rt,
            mode='lines',
            name='真实电阻率(RT)',
            line=dict(color='blue', width=1)
        ))
        
        fig.update_layout(
            title="测井曲线展示",
            yaxis=dict(title="深度 (m)", autorange="reversed"),
            xaxis=dict(title="数值"),
            height=800,
            hovermode='y unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("统计信息")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("GR 平均值", f"{gr.mean():.2f}")
        with col2:
            st.metric("RT 平均值", f"{rt.mean():.2f}")
        with col3:
            st.metric("采样点数", len(depth))

# 页面3：AI预测
elif page == "AI预测":
    st.title("🤖 AI曲线预测")
    
    # 检查API连接
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=2)
        if health_response.status_code == 200:
            health_data = health_response.json()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("API状态", "✅ 在线")
            with col2:
                st.metric("模型状态", "✅ 就绪" if health_data.get("model_loaded") else "⚠️ 演示模式")
            with col3:
                st.metric("版本", health_data.get("version", "N/A"))
    except Exception as e:
        st.error(f"❌ API连接失败: {str(e)}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        depth_from = st.number_input("起始深度 (m)", value=1000.0, min_value=0.0)
    with col2:
        depth_to = st.number_input("结束深度 (m)", value=1500.0, min_value=0.0)
    
    # 获取可用曲线
    available_curves = ["GR", "RT", "DEN", "NEU", "SP", "CALI"]
    try:
        curves_response = requests.get(f"{API_URL}/curves", timeout=2)
        if curves_response.status_code == 200:
            available_curves = curves_response.json().get("curves", available_curves)
    except:
        pass  # 使用默认值
    
    curves = st.multiselect(
        "选择要预测的曲线",
        available_curves,
        default=["GR", "RT"]
    )
    
    if st.button("开始预测", type="primary"):
        # 验证输入
        if depth_from >= depth_to:
            st.error("❌ 起始深度必须小于结束深度")
        elif not curves:
            st.error("❌ 请至少选择一条曲线")
        else:
            with st.spinner("AI模型推理中..."):
                payload = {
                    "depth_from": depth_from,
                    "depth_to": depth_to,
                    "curves": curves
                }
                
                try:
                    response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ 预测完成！置信度: {result['confidence']:.2%}")
                        
                        # 显示结果
                        predictions_df = pd.DataFrame(result['predictions'])
                        st.dataframe(predictions_df, use_container_width=True)
                        
                        # 绘制曲线
                        if not predictions_df.empty:
                            fig = go.Figure()
                            for curve in curves:
                                curve_data = predictions_df[predictions_df['curve'] == curve]
                                if not curve_data.empty:
                                    fig.add_trace(go.Scatter(
                                        x=curve_data['value'],
                                        y=curve_data['depth'],
                                        mode='lines',
                                        name=curve
                                    ))
                            
                            fig.update_layout(
                                title="预测结果曲线",
                                xaxis_title="数值",
                                yaxis_title="深度 (m)",
                                yaxis=dict(autorange="reversed"),
                                height=600
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"❌ 预测失败: {response.json().get('detail', '未知错误')}")
                except requests.exceptions.Timeout:
                    st.error("❌ 请求超时，请检查API服务")
                except Exception as e:
                    st.error(f"❌ 预测失败: {str(e)}")

# 页面4：模型训练
elif page == "模型训练":
    st.title("🎓 模型训练")
    
    st.info("模型训练功能开发中...")
    
    with st.form("training_form"):
        epochs = st.slider("训练轮数", 1, 100, 10)
        batch_size = st.selectbox("批次大小", [16, 32, 64, 128])
        learning_rate = st.number_input("学习率", value=0.001, format="%.6f")
        
        submitted = st.form_submit_button("开始训练")
        if submitted:
            st.warning("训练功能即将推出！")