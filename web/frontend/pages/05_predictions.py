"""
AI 预测页面 - Phase 5e
支持机器学习预测和模型结果解释
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="AI 预测 | GeologAI",
    page_icon="🤖",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8001"
PREDICTIONS_ENDPOINT = f"{API_BASE_URL}/api/v1/predictions"
DATA_ENDPOINT = f"{API_BASE_URL}/api/v1/data"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/api/v1/projects"
MODELS_ENDPOINT = f"{API_BASE_URL}/api/v1/models"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

# 页面标题
st.title("🤖 AI 预测分析")
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
def get_models():
    """获取可用的预测模型"""
    try:
        response = requests.get(
            MODELS_ENDPOINT,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        # 返回默认模型列表
        return [
            {"id": "model_1", "name": "随机森林模型", "type": "regression", "accuracy": 0.87},
            {"id": "model_2", "name": "神经网络模型", "type": "classification", "accuracy": 0.92},
            {"id": "model_3", "name": "支持向量机", "type": "regression", "accuracy": 0.85}
        ]
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
    st.subheader("⚙️ 预测配置")
    
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
    
    # 选择模型
    models = get_models()
    model_names = {m.get("id"): m.get("name") for m in models}
    
    selected_model_id = st.selectbox(
        "选择预测模型",
        list(model_names.keys()),
        format_func=lambda x: model_names[x]
    )
    
    st.markdown("---")
    
    # 显示数据信息
    st.subheader("📊 数据信息")
    st.metric("井号", selected_data.get("well_name"))
    st.metric("行数", selected_data.get("rows_count", 0))

# ======================== 主内容区 ========================
# 加载数据
data_content = get_data_content(data_id)

if not data_content:
    st.error("❌ 无法加载数据")
    st.stop()

# 转换为 DataFrame
try:
    if isinstance(data_content.get("data"), list):
        df = pd.DataFrame(data_content["data"])
    else:
        st.error("❌ 数据格式错误")
        st.stop()
except Exception as e:
    st.error(f"❌ 数据处理错误: {str(e)}")
    st.stop()

numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

# ======================== 预测配置 ========================
st.subheader("🔧 预测参数配置")

col1, col2, col3 = st.columns(3)

with col1:
    if numeric_columns:
        target_column = st.selectbox(
            "选择目标变量（预测目标）",
            numeric_columns
        )
    else:
        st.error("❌ 暂无数值型列")
        st.stop()

with col2:
    # 移除目标列后的特征
    feature_columns = [col for col in numeric_columns if col != target_column]
    selected_features = st.multiselect(
        "选择特征变量",
        feature_columns,
        default=feature_columns[:min(5, len(feature_columns))]
    )

with col3:
    train_test_split = st.slider(
        "训练集比例",
        0.5,
        0.95,
        0.8,
        0.05
    )

# 预测参数
st.markdown("---")
st.subheader("📊 模型参数")

col1, col2, col3 = st.columns(3)

with col1:
    cross_validation = st.checkbox("启用交叉验证", value=True)

with col2:
    random_state = st.number_input(
        "随机种子",
        min_value=0,
        max_value=9999,
        value=42,
        step=1
    )

with col3:
    if cross_validation:
        cv_folds = st.number_input(
            "交叉验证折数",
            min_value=2,
            max_value=10,
            value=5
        )

# ======================== 执行预测 ========================
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    execute_prediction = st.button("🚀 执行预测", use_container_width=True)

with col2:
    reset_button = st.button("🔄 重置", use_container_width=True)

with col3:
    help_button = st.button("❓ 帮助", use_container_width=True)

if help_button:
    st.info("""
    **AI 预测说明：**
    
    1. **选择目标变量** - 要预测的数值列
    2. **选择特征变量** - 用于预测的输入列
    3. **调整参数** - 选择模型参数和训练配置
    4. **执行预测** - 运行预测模型
    
    **参数说明：**
    - **训练集比例** - 用于训练的数据占比（剩余用于测试）
    - **交叉验证** - 启用时使用K折验证提高模型稳健性
    - **随机种子** - 用于重现结果的随机数种子
    """)

if reset_button:
    st.session_state.pop("prediction_result", None)
    st.rerun()

if execute_prediction:
    if not selected_features:
        st.error("❌ 请至少选择一个特征变量")
    else:
        with st.spinner("🔄 正在执行预测..."):
            try:
                # 准备预测请求
                prediction_request = {
                    "data_id": str(data_id),
                    "model_id": selected_model_id,
                    "target_column": target_column,
                    "feature_columns": selected_features,
                    "train_test_split": train_test_split,
                    "cross_validation": cross_validation,
                    "cv_folds": cv_folds if cross_validation else None,
                    "random_state": random_state
                }
                
                # 发送预测请求
                response = requests.post(
                    PREDICTIONS_ENDPOINT,
                    json=prediction_request,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    st.session_state.prediction_result = result
                    st.success("✅ 预测完成！")
                else:
                    error_msg = response.json().get("detail", "未知错误")
                    st.error(f"❌ 预测失败: {error_msg}")
            
            except requests.exceptions.Timeout:
                st.error("❌ 预测超时，请尝试减少数据量或简化模型")
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到服务器")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")

# ======================== 显示预测结果 ========================
if "prediction_result" in st.session_state and st.session_state.prediction_result:
    result = st.session_state.prediction_result
    
    st.markdown("---")
    st.subheader("📈 预测结果")
    
    # 显示模型性能指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "模型精度",
            f"{result.get('accuracy', 0):.3f}",
            delta=f"{(result.get('accuracy', 0) - 0.5) * 100:.1f}%"
        )
    
    with col2:
        st.metric("R² 分数", f"{result.get('r2_score', 0):.3f}")
    
    with col3:
        st.metric("MAE", f"{result.get('mae', 0):.3f}")
    
    with col4:
        st.metric("RMSE", f"{result.get('rmse', 0):.3f}")
    
    st.markdown("---")
    
    # 显示预测值 vs 实际值
    col1, col2 = st.columns(2)
    
    with col1:
        # 预测值 vs 实际值散点图
        predictions = result.get("predictions", [])
        actual_values = result.get("actual_values", [])
        
        if predictions and actual_values:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=actual_values,
                y=predictions,
                mode='markers',
                marker=dict(size=8, opacity=0.6),
                name="预测结果"
            ))
            
            # 添加完美预测线
            min_val = min(min(actual_values), min(predictions))
            max_val = max(max(actual_values), max(predictions))
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name="完美预测",
                line=dict(dash='dash', color='red')
            ))
            
            fig.update_layout(
                title="预测值 vs 实际值",
                xaxis_title="实际值",
                yaxis_title="预测值",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 残差分布
        if predictions and actual_values:
            residuals = np.array(actual_values) - np.array(predictions)
            
            fig = go.Figure(data=[
                go.Histogram(
                    x=residuals,
                    nbinsx=30,
                    name="残差",
                    hovertemplate="<b>%{x:.2f}</b><br>频数: %{y}<extra></extra>"
                )
            ])
            
            fig.update_layout(
                title="残差分布",
                xaxis_title="残差值",
                yaxis_title="频数",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 特征重要性
    st.markdown("---")
    st.subheader("🎯 特征重要性")
    
    feature_importance = result.get("feature_importance", {})
    
    if feature_importance:
        # 排序特征重要性
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        fig = go.Figure(data=[
            go.Bar(
                x=[f[1] for f in sorted_features],
                y=[f[0] for f in sorted_features],
                orientation='h',
                marker=dict(color=[f[1] for f in sorted_features], colorscale='Viridis')
            )
        ])
        
        fig.update_layout(
            title="特征重要性排名",
            xaxis_title="重要性得分",
            height=300,
            margin=dict(l=150)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 预测结果表格
    st.markdown("---")
    st.subheader("📋 预测详情")
    
    if predictions and actual_values:
        results_df = pd.DataFrame({
            "样本索引": range(len(predictions)),
            "实际值": actual_values,
            "预测值": predictions,
            "误差": np.array(actual_values) - np.array(predictions),
            "相对误差%": (abs(np.array(actual_values) - np.array(predictions)) / 
                        (abs(np.array(actual_values)) + 1e-10) * 100).round(2)
        })
        
        st.dataframe(
            results_df.head(50),
            use_container_width=True,
            hide_index=False
        )
        
        # 下载结果
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 下载预测结果",
            data=csv,
            file_name=f"prediction_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📈 分析曲线", use_container_width=True):
        st.switch_page("pages/04_analysis.py")
with col2:
    if st.button("🎓 模型训练", use_container_width=True):
        st.switch_page("pages/06_model_training.py")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
