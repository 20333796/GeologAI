"""
模型训练页面 - Phase 5e
支持自定义模型训练和性能评估
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json

# 页面配置
st.set_page_config(
    page_title="模型训练 | GeologAI",
    page_icon="🎓",
    layout="wide"
)

# API 配置
API_BASE_URL = "http://127.0.0.1:8000"
TRAINING_ENDPOINT = f"{API_BASE_URL}/api/training"
DATA_ENDPOINT = f"{API_BASE_URL}/api/data"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/api/projects"

# 验证认证
if not st.session_state.get("auth_token"):
    st.error("❌ 请先登录")
    st.stop()

# 页面标题
st.title("🎓 模型训练")
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
    st.subheader("⚙️ 训练配置")
    
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
    
    # 可以选择多个数据进行联合训练
    data_names = {i: d.get("well_name") for i, d in enumerate(data_list)}
    selected_data_indices = st.multiselect(
        "选择训练数据",
        list(data_names.keys()),
        format_func=lambda x: data_names[x],
        default=[0]
    )
    
    if not selected_data_indices:
        st.warning("⚠️ 请至少选择一个数据集")
        st.stop()
    
    st.markdown("---")
    
    # 显示数据信息
    st.subheader("📊 数据概览")
    for idx in selected_data_indices:
        data_item = data_list[idx]
        st.metric(
            data_item.get("well_name"),
            f"{data_item.get('rows_count', 0)} 行"
        )

# ======================== 主内容区 ========================
# 加载数据
dfs = []
for idx in selected_data_indices:
    data_id = data_list[idx].get("id")
    data_content = get_data_content(data_id)
    
    if data_content and isinstance(data_content.get("data"), list):
        try:
            df = pd.DataFrame(data_content["data"])
            dfs.append(df)
        except:
            st.error(f"❌ 无法加载数据")
            st.stop()

if not dfs:
    st.error("❌ 无法加载任何数据")
    st.stop()

# 合并数据（如果有多个）
if len(dfs) > 1:
    combined_df = pd.concat(dfs, ignore_index=True)
else:
    combined_df = dfs[0]

numeric_columns = combined_df.select_dtypes(include=[np.number]).columns.tolist()

# ======================== 训练配置 ========================
st.subheader("🔧 训练参数配置")

tabs = st.tabs(["基本配置", "高级参数", "模型对比"])

# ======================== TAB 1: 基本配置 ========================
with tabs[0]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**数据配置**")
        
        if numeric_columns:
            target_column = st.selectbox(
                "目标变量",
                numeric_columns,
                help="要预测的目标列"
            )
        else:
            st.error("❌ 暂无数值型列")
            st.stop()
        
        # 移除目标列后的特征
        feature_columns = [col for col in numeric_columns if col != target_column]
        selected_features = st.multiselect(
            "特征变量",
            feature_columns,
            default=feature_columns[:min(10, len(feature_columns))],
            help="用于训练的输入特征"
        )
        
        train_test_split = st.slider(
            "训练集比例",
            0.5,
            0.95,
            0.8,
            0.05,
            help="训练数据占总数据的比例"
        )
    
    with col2:
        st.markdown("**模型配置**")
        
        model_type = st.selectbox(
            "模型类型",
            ["回归模型", "分类模型"],
            help="选择任务类型"
        )
        
        algorithm = st.selectbox(
            "算法",
            ["随机森林", "神经网络", "支持向量机", "线性回归", "梯度提升"],
            help="选择具体算法"
        )
        
        random_state = st.number_input(
            "随机种子",
            min_value=0,
            max_value=9999,
            value=42,
            step=1,
            help="用于重现结果"
        )

# ======================== TAB 2: 高级参数 ========================
with tabs[1]:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**交叉验证**")
        enable_cv = st.checkbox("启用交叉验证", value=True)
        if enable_cv:
            cv_folds = st.slider("CV 折数", 2, 10, 5)
        else:
            cv_folds = None
    
    with col2:
        st.markdown("**特征工程**")
        normalize_features = st.checkbox("特征标准化", value=True)
        remove_outliers = st.checkbox("移除异常值", value=False)
        feature_selection = st.checkbox("特征选择", value=False)
    
    with col3:
        st.markdown("**数据处理**")
        handle_missing = st.selectbox(
            "缺失值处理",
            ["删除", "均值填充", "中位数填充", "向前填充"]
        )
        random_forest_params = {}
        if algorithm == "随机森林":
            n_estimators = st.slider("树数量", 10, 500, 100, 10)
            max_depth = st.slider("最大深度", 5, 50, None)
            random_forest_params = {
                "n_estimators": n_estimators,
                "max_depth": max_depth
            }

# ======================== TAB 3: 模型对比 ========================
with tabs[2]:
    st.markdown("**模型对比设置**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        compare_models = st.checkbox("启用模型对比", value=False)
    
    with col2:
        if compare_models:
            comparison_algorithms = st.multiselect(
                "选择对比算法",
                ["随机森林", "神经网络", "支持向量机", "线性回归", "梯度提升"],
                default=["随机森林", "神经网络"]
            )
        else:
            comparison_algorithms = []

# ======================== 执行训练 ========================
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    start_training = st.button("🚀 开始训练", use_container_width=True)

with col2:
    reset_button = st.button("🔄 重置", use_container_width=True)

with col3:
    help_button = st.button("❓ 帮助", use_container_width=True)

if help_button:
    st.info("""
    **模型训练说明：**
    
    **基本配置：**
    - 选择目标变量和特征变量
    - 设置训练/测试数据分割比例
    - 选择模型类型和算法
    
    **高级参数：**
    - 交叉验证：使用K折验证提高模型稳健性
    - 特征工程：标准化、异常值处理、特征选择
    - 数据处理：缺失值处理方法
    
    **模型对比：**
    - 同时训练多个模型进行对比
    - 自动生成对比报告
    """)

if reset_button:
    st.session_state.pop("training_result", None)
    st.rerun()

if start_training:
    if not selected_features:
        st.error("❌ 请至少选择一个特征")
    else:
        with st.spinner("🔄 正在训练模型..."):
            try:
                # 准备训练请求
                training_request = {
                    "target_column": target_column,
                    "feature_columns": selected_features,
                    "train_test_split": train_test_split,
                    "algorithm": algorithm,
                    "model_type": model_type,
                    "random_state": random_state,
                    "cross_validation": enable_cv,
                    "cv_folds": cv_folds if enable_cv else None,
                    "normalize_features": normalize_features,
                    "remove_outliers": remove_outliers,
                    "feature_selection": feature_selection,
                    "handle_missing": handle_missing,
                    "algorithm_params": random_forest_params,
                    "compare_models": compare_models,
                    "comparison_algorithms": comparison_algorithms
                }
                
                # 发送训练请求
                response = requests.post(
                    TRAINING_ENDPOINT,
                    json=training_request,
                    headers=headers,
                    timeout=300  # 允许较长的训练时间
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    st.session_state.training_result = result
                    st.success("✅ 模型训练完成！")
                else:
                    error_msg = response.json().get("detail", "未知错误")
                    st.error(f"❌ 训练失败: {error_msg}")
            
            except requests.exceptions.Timeout:
                st.error("❌ 训练超时，请尝试减少数据量或简化模型")
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到服务器")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")

# ======================== 显示训练结果 ========================
if "training_result" in st.session_state and st.session_state.training_result:
    result = st.session_state.training_result
    
    st.markdown("---")
    st.subheader("📈 训练结果")
    
    # 显示性能指标
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = result.get("metrics", {})
    
    with col1:
        st.metric("精度", f"{metrics.get('accuracy', 0):.3f}")
    
    with col2:
        st.metric("R² 分数", f"{metrics.get('r2_score', 0):.3f}")
    
    with col3:
        st.metric("MAE", f"{metrics.get('mae', 0):.3f}")
    
    with col4:
        st.metric("RMSE", f"{metrics.get('rmse', 0):.3f}")
    
    st.markdown("---")
    
    # 显示训练/测试性能对比
    col1, col2 = st.columns(2)
    
    with col1:
        # 训练曲线
        training_history = result.get("training_history", {})
        if training_history:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=list(range(len(training_history.get("train_loss", [])))),
                y=training_history.get("train_loss", []),
                mode='lines',
                name="训练损失"
            ))
            
            if "val_loss" in training_history:
                fig.add_trace(go.Scatter(
                    x=list(range(len(training_history.get("val_loss", [])))),
                    y=training_history.get("val_loss", []),
                    mode='lines',
                    name="验证损失"
                ))
            
            fig.update_layout(
                title="训练曲线",
                xaxis_title="轮次",
                yaxis_title="损失值",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 性能指标对比
        train_metrics = result.get("train_metrics", {})
        test_metrics = result.get("test_metrics", {})
        
        if train_metrics and test_metrics:
            fig = go.Figure()
            
            metrics_names = ["精度", "R²", "MAE"]
            train_vals = [
                train_metrics.get("accuracy", 0),
                train_metrics.get("r2_score", 0),
                train_metrics.get("mae", 0)
            ]
            test_vals = [
                test_metrics.get("accuracy", 0),
                test_metrics.get("r2_score", 0),
                test_metrics.get("mae", 0)
            ]
            
            fig.add_trace(go.Bar(name="训练集", x=metrics_names, y=train_vals))
            fig.add_trace(go.Bar(name="测试集", x=metrics_names, y=test_vals))
            
            fig.update_layout(
                title="训练/测试性能对比",
                height=400,
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 特征重要性
    st.markdown("---")
    st.subheader("🎯 特征重要性")
    
    feature_importance = result.get("feature_importance", {})
    
    if feature_importance:
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
    
    # 模型对比（如果启用）
    if result.get("model_comparison"):
        st.markdown("---")
        st.subheader("📊 模型对比")
        
        comparison_results = result.get("model_comparison", {})
        
        # 创建对比表
        comparison_data = []
        for model_name, metrics in comparison_results.items():
            comparison_data.append({
                "模型": model_name,
                "精度": f"{metrics.get('accuracy', 0):.3f}",
                "R²": f"{metrics.get('r2_score', 0):.3f}",
                "MAE": f"{metrics.get('mae', 0):.3f}",
                "RMSE": f"{metrics.get('rmse', 0):.3f}"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # 对比图表
        model_names = [m["模型"] for m in comparison_data]
        accuracies = [float(m["精度"]) for m in comparison_data]
        
        fig = go.Figure(data=[
            go.Bar(x=model_names, y=accuracies, marker_color='lightblue')
        ])
        
        fig.update_layout(
            title="模型精度对比",
            yaxis_title="精度",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 保存模型
    st.markdown("---")
    st.subheader("💾 模型保存")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        model_name = st.text_input(
            "模型名称",
            value=f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    with col2:
        model_desc = st.text_area(
            "模型描述",
            placeholder="输入模型相关描述",
            height=50
        )
    
    with col3:
        if st.button("💾 保存模型", use_container_width=True):
            with st.spinner("正在保存模型..."):
                try:
                    save_request = {
                        "model_name": model_name,
                        "description": model_desc,
                        "algorithm": algorithm,
                        "metrics": metrics
                    }
                    
                    response = requests.post(
                        f"{TRAINING_ENDPOINT}/save",
                        json=save_request,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200 or response.status_code == 201:
                        st.success(f"✅ 模型已保存为: {model_name}")
                    else:
                        st.error("❌ 模型保存失败")
                except Exception as e:
                    st.error(f"❌ 错误: {str(e)}")
    
    # 下载报告
    st.markdown("---")
    
    report_data = {
        "训练时间": datetime.now().isoformat(),
        "算法": algorithm,
        "目标变量": target_column,
        "特征数": len(selected_features),
        "训练集比例": train_test_split,
        "性能指标": metrics,
        "特征重要性": feature_importance
    }
    
    report_json = json.dumps(report_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 下载训练报告",
        data=report_json,
        file_name=f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🤖 AI 预测", use_container_width=True):
        st.switch_page("pages/05_predictions.py")
with col2:
    st.caption("💡 模型训练需要较长时间，请耐心等待")
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
