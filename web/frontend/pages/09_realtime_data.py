"""
实时数据流页面 - Phase 5d
支持流式数据展示、实时图表更新和性能监控
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="实时数据 | GeologAI",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8001"
STREAM_ENDPOINT = f"{API_BASE_URL}/api/v1/data/stream"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

# 页面标题
st.title("🔴 实时数据流")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.subheader("流配置")
    refresh_interval = st.number_input("刷新间隔 (秒)", min_value=1, max_value=60, value=3)
    max_points = st.number_input("最大点数", min_value=10, max_value=10000, value=500)
    show_raw = st.checkbox("显示原始表格", value=False)

# 选择数据源
source = st.selectbox("数据源", ["模拟传感器", "API 流式端点"], index=0)

# 初始化缓存
if "realtime_buffer" not in st.session_state:
    st.session_state.realtime_buffer = pd.DataFrame()

placeholder = st.empty()

# 主循环（基于 Streamlit 的交互式更新）
if source == "模拟传感器":
    st.info("使用本地模拟数据生成实时曲线")
    
    # 初始化示例数据
    if st.button("开始模拟实时流"):
        st.session_state.realtime_buffer = pd.DataFrame({
            "time": pd.date_range(end=pd.Timestamp.now(), periods=1),
            "value": [np.random.randn()]
        })
        
        chart = placeholder.line_chart(st.session_state.realtime_buffer.set_index("time")["value"])
        
        try:
            # 在 Streamlit 中运行实时更新
            while True:
                new_row = {"time": pd.Timestamp.now(), "value": st.session_state.realtime_buffer["value"].iloc[-1] + np.random.randn() * 0.1}
                st.session_state.realtime_buffer = pd.concat([st.session_state.realtime_buffer, pd.DataFrame([new_row])], ignore_index=True)
                
                if len(st.session_state.realtime_buffer) > max_points:
                    st.session_state.realtime_buffer = st.session_state.realtime_buffer.iloc[-max_points:]
                
                chart.add_rows(pd.DataFrame([new_row]).set_index("time"))
                time.sleep(refresh_interval)
        except Exception:
            st.warning("实时流已停止")

else:
    st.info("从后端 API 订阅实时数据（如果后端支持）")
    
    if st.button("开始订阅 API 流"):
        try:
            # 简单轮询实现（如有 WebSocket，可替换）
            chart = placeholder.line_chart()
            while True:
                resp = requests.get(STREAM_ENDPOINT, timeout=5, headers={"Authorization": f"Bearer {st.session_state.auth_token}"})
                if resp.status_code == 200:
                    data = resp.json()
                    df = pd.DataFrame(data)
                    df["time"] = pd.to_datetime(df["time"]) if "time" in df.columns else pd.to_datetime(pd.Series(pd.Timestamp.now()))
                    st.session_state.realtime_buffer = pd.concat([st.session_state.realtime_buffer, df], ignore_index=True)
                    if len(st.session_state.realtime_buffer) > max_points:
                        st.session_state.realtime_buffer = st.session_state.realtime_buffer.iloc[-max_points:]
                    chart.add_rows(st.session_state.realtime_buffer.set_index("time")[df.columns.difference(["time"]).tolist()[0]])
                else:
                    st.warning(f"流数据请求返回状态: {resp.status_code}")
                time.sleep(refresh_interval)
        except Exception as e:
            st.error(f"流订阅出错: {e}")

# 显示原始表格
if show_raw and not st.session_state.realtime_buffer.empty:
    st.subheader("原始数据")
    st.dataframe(st.session_state.realtime_buffer.tail(100), use_container_width=True)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📈 曲线分析", use_container_width=True):
        st.switch_page("pages/04_analysis.py")
with col2:
    if st.button("🎯 3D 可视化", use_container_width=True):
        st.switch_page("pages/07_3d_visualization.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
