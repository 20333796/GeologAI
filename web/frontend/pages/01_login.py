"""
登录页面 - Phase 5b
集成后端认证 API
"""

import streamlit as st
import requests
import json
from datetime import datetime

# 配置
API_BASE_URL = "http://127.0.0.1:8000"
AUTH_ENDPOINT = f"{API_BASE_URL}/api/auth"

# 页面配置
st.set_page_config(
    page_title="登录 | GeologAI",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 美化
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "login_tab" not in st.session_state:
    st.session_state.login_tab = "login"

# 标题
st.title("🔐 GeologAI 认证")
st.markdown("---")

# 检查是否已登录
if st.session_state.auth_token:
    st.markdown("""
    <div class="success-box">
        <strong>✅ 已登录</strong><br>
        用户名: {}<br>
        邮箱: {}
    </div>
    """.format(st.session_state.user_info.get("username"), st.session_state.user_info.get("email")), 
    unsafe_allow_html=True)
    
    if st.button("退出登录", key="logout_btn"):
        st.session_state.auth_token = None
        st.session_state.user_info = None
        st.rerun()
    
    st.markdown("---")
    st.info("✨ 登录成功！现在可以浏览应用的其他功能。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 查看项目"):
            st.switch_page("pages/02_projects.py")
    with col2:
        if st.button("📁 上传数据"):
            st.switch_page("pages/03_data_upload.py")
else:
    # 登录/注册选项卡
    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])
    
    # ======================== 登录标签页 ========================
    with tab1:
        st.subheader("用户登录")
        
        with st.form("login_form"):
            username = st.text_input(
                "用户名",
                placeholder="输入用户名或邮箱",
                key="login_username"
            )
            password = st.text_input(
                "密码",
                type="password",
                placeholder="输入密码",
                key="login_password"
            )
            submit_login = st.form_submit_button("🔓 登录", use_container_width=True)
        
        if submit_login:
            if not username or not password:
                st.error("❌ 用户名和密码不能为空")
            else:
                with st.spinner("正在验证凭证..."):
                    try:
                        # 调用后端登录 API
                        response = requests.post(
                            f"{AUTH_ENDPOINT}/login",
                            json={
                                "username": username,
                                "password": password
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            # 保存令牌和用户信息
                            st.session_state.auth_token = data.get("access_token")
                            st.session_state.user_info = {
                                "username": data.get("username"),
                                "email": data.get("email"),
                                "user_id": data.get("user_id")
                            }
                            st.success("✅ 登录成功！")
                            st.rerun()
                        else:
                            error_msg = response.json().get("detail", "登录失败")
                            st.error(f"❌ {error_msg}")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ 无法连接到服务器。请确保后端正在运行（http://127.0.0.1:8000）")
                    except requests.exceptions.Timeout:
                        st.error("❌ 请求超时，请重试")
                    except Exception as e:
                        st.error(f"❌ 发生错误: {str(e)}")
        
        # 演示用户提示
        st.markdown("""
        <div class="info-box">
        <strong>💡 演示账户（首次注册时可用）</strong><br>
        用户名: demo<br>
        密码: demo123
        </div>
        """, unsafe_allow_html=True)
    
    # ======================== 注册标签页 ========================
    with tab2:
        st.subheader("创建新账户")
        
        with st.form("register_form"):
            reg_username = st.text_input(
                "用户名",
                placeholder="选择用户名（字母、数字、下划线）",
                key="reg_username"
            )
            reg_email = st.text_input(
                "邮箱地址",
                placeholder="输入有效的邮箱地址",
                key="reg_email"
            )
            reg_password = st.text_input(
                "密码",
                type="password",
                placeholder="至少 6 个字符",
                key="reg_password"
            )
            reg_password_confirm = st.text_input(
                "确认密码",
                type="password",
                placeholder="再次输入密码",
                key="reg_password_confirm"
            )
            submit_register = st.form_submit_button("📝 注册", use_container_width=True)
        
        if submit_register:
            # 验证表单
            if not all([reg_username, reg_email, reg_password, reg_password_confirm]):
                st.error("❌ 所有字段都是必填的")
            elif reg_password != reg_password_confirm:
                st.error("❌ 两次输入的密码不一致")
            elif len(reg_password) < 6:
                st.error("❌ 密码至少需要 6 个字符")
            elif "@" not in reg_email:
                st.error("❌ 请输入有效的邮箱地址")
            else:
                with st.spinner("正在创建账户..."):
                    try:
                        # 调用后端注册 API
                        response = requests.post(
                            f"{AUTH_ENDPOINT}/register",
                            json={
                                "username": reg_username,
                                "email": reg_email,
                                "password": reg_password
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success("✅ 账户创建成功！")
                            st.info("请使用新账户凭证登录。")
                            st.session_state.login_tab = "login"
                            st.rerun()
                        elif response.status_code == 400:
                            error_msg = response.json().get("detail", "注册失败")
                            st.error(f"❌ {error_msg}")
                        else:
                            st.error(f"❌ 注册失败 (HTTP {response.status_code})")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ 无法连接到服务器。请确保后端正在运行")
                    except requests.exceptions.Timeout:
                        st.error("❌ 请求超时，请重试")
                    except Exception as e:
                        st.error(f"❌ 发生错误: {str(e)}")

# ======================== 页脚 ========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏠 [主页](../)")
with col2:
    st.caption("📖 [文档](https://github.com/20333796/GeologAI)")
with col3:
    st.caption("⚙️ [设置](#)")

# 调试信息（可选）
if st.session_state.get("show_debug"):
    st.markdown("---")
    st.subheader("🐛 调试信息")
    st.json({
        "token": st.session_state.auth_token[:20] + "..." if st.session_state.auth_token else None,
        "user": st.session_state.user_info,
        "timestamp": datetime.now().isoformat()
    })
