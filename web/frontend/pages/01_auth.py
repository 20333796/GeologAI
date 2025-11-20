"""
注册登录页面 - 独立的认证界面
"""

import streamlit as st
import requests
import re
import time

# 页面配置 - 不配置侧边栏
st.set_page_config(
    page_title="注册/登录 - GeologAI",
    page_icon="🔐",
    layout="centered"
)

# 完全隐藏Streamlit所有UI元素
st.markdown("""
    <style>
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    header { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { padding: 0px !important; }
    .stAppViewContainer { padding: 0px !important; }
    .block-container { max-width: 500px !important; }
    </style>
""", unsafe_allow_html=True)

# 后端API配置
BACKEND_URL = "http://localhost:8001"
API_VERSION = "v1"

# 会话状态初始化
if "auth_message" not in st.session_state:
    st.session_state.auth_message = None
if "auth_message_type" not in st.session_state:
    st.session_state.auth_message_type = None

# ============= 帮助函数 =============

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8个字符"
    if not any(c.isupper() for c in password):
        return False, "密码必须包含至少一个大写字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含至少一个数字"
    return True, "密码符合要求"

def register_user(username, email, password, password_confirm, real_name):
    """调用后端注册API"""
    try:
        if not username or not email or not password or not real_name:
            return False, "请填写所有必填项"
        
        if len(username) < 3 or len(username) > 50:
            return False, "用户名长度应在3-50个字符之间"
        
        if not validate_email(email):
            return False, "邮箱格式不正确"
        
        if password != password_confirm:
            return False, "两次输入的密码不一致"
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            return False, msg
        
        response = requests.post(
            f"{BACKEND_URL}/api/{API_VERSION}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "real_name": real_name
            },
            timeout=10
        )
        
        if response.status_code == 201:
            return True, "注册成功！请登录"
        elif response.status_code == 400:
            detail = response.json().get("detail", "注册失败")
            return False, detail
        else:
            return False, f"注册失败: {response.status_code}"
    
    except requests.ConnectionError:
        return False, "无法连接到服务器，请检查后端是否运行"
    except Exception as e:
        return False, f"注册错误: {str(e)}"

def login_user(username, password):
    """调用后端登录API"""
    try:
        if not username or not password:
            return False, None, None, "请输入用户名和密码"
        
        response = requests.post(
            f"{BACKEND_URL}/api/{API_VERSION}/auth/login",
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data.get("access_token"), data.get("user"), "登录成功"
        elif response.status_code == 401:
            return False, None, None, "用户名或密码错误"
        elif response.status_code == 403:
            return False, None, None, "账户已被禁用"
        else:
            return False, None, None, f"登录失败: {response.status_code}"
    
    except requests.ConnectionError:
        return False, None, None, "无法连接到服务器，请检查后端是否运行"
    except Exception as e:
        return False, None, None, f"登录错误: {str(e)}"

# ============= 页面布局 =============

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🔐 认证中心")
with col2:
    if st.button("← 返回", use_container_width=True):
        st.switch_page("pages/00_home.py")

st.markdown("---")

# 选项卡：登录和注册
tab1, tab2 = st.tabs(["🔓 登录", "📝 注册"])

# ============= 登录标签页 =============
with tab1:
    st.markdown("## 登录您的账户")
    
    # 显示之前的消息
    if st.session_state.auth_message:
        if st.session_state.auth_message_type == "success":
            st.success(st.session_state.auth_message)
        elif st.session_state.auth_message_type == "error":
            st.error(st.session_state.auth_message)
        st.session_state.auth_message = None
        st.session_state.auth_message_type = None
    
    with st.form("login_form", clear_on_submit=True):
        login_username = st.text_input(
            "用户名或邮箱",
            placeholder="输入您的用户名或邮箱地址",
            key="login_username"
        )
        login_password = st.text_input(
            "密码",
            type="password",
            placeholder="输入您的密码",
            key="login_password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("")
        with col2:
            st.markdown("[忘记密码?](https://example.com)")
        
        st.markdown("")
        
        submit_login = st.form_submit_button("🔓 登录", use_container_width=True, type="primary")
    
    if submit_login:
        with st.spinner("正在登录..."):
            success, token, user, message = login_user(login_username, login_password)
            
            if success:
                st.success(message)
                st.session_state.auth_token = token
                st.session_state.user_info = user
                st.session_state.current_page = "dashboard"
                time.sleep(1)
                st.switch_page("pages/02_dashboard.py")
            else:
                st.error(message)
    
    # 快速登录演示账户
    st.markdown("---")
    st.markdown("### 💡 快速体验")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("使用演示账户登录", use_container_width=True):
            with st.spinner("正在登录..."):
                success, token, user, message = login_user("demo_user", "DemoUser123")
                if success:
                    st.success(message)
                    st.session_state.auth_token = token
                    st.session_state.user_info = user
                    time.sleep(1)
                    st.switch_page("pages/02_dashboard.py")
                else:
                    st.error(message)
    
    with col2:
        st.info("demo_user / DemoUser123")

# ============= 注册标签页 =============
with tab2:
    st.markdown("## 创建新账户")
    
    with st.form("register_form", clear_on_submit=True):
        register_username = st.text_input(
            "用户名",
            placeholder="3-50个字符，字母和数字组合",
            key="register_username"
        )
        register_email = st.text_input(
            "邮箱地址",
            placeholder="example@email.com",
            key="register_email"
        )
        register_real_name = st.text_input(
            "真实姓名",
            placeholder="您的真实姓名",
            key="register_real_name"
        )
        register_password = st.text_input(
            "密码",
            type="password",
            placeholder="至少8个字符，需包含大写字母和数字",
            key="register_password"
        )
        register_password_confirm = st.text_input(
            "确认密码",
            type="password",
            placeholder="再次输入密码",
            key="register_password_confirm"
        )
        
        # 显示密码要求
        st.markdown("""
        **密码要求：**
        - ✓ 至少8个字符
        - ✓ 至少一个大写字母（A-Z）
        - ✓ 至少一个数字（0-9）
        """)
        
        # 同意条款复选框
        agree_terms = st.checkbox(
            "我已阅读并同意《用户协议》和《隐私政策》",
            key="agree_terms"
        )
        
        st.markdown("")
        
        submit_register = st.form_submit_button("📝 创建账户", use_container_width=True, type="primary")
    
    if submit_register:
        if not agree_terms:
            st.error("请阅读并同意《用户协议》和《隐私政策》")
        else:
            with st.spinner("正在创建账户..."):
                success, message = register_user(
                    register_username,
                    register_email,
                    register_password,
                    register_password_confirm,
                    register_real_name
                )
                
                if success:
                    st.success(message)
                    st.session_state.auth_message = "注册成功！现在请登录"
                    st.session_state.auth_message_type = "success"
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(message)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #888; font-size: 12px;'>© 2024 GeologAI | 安全登录</div>", unsafe_allow_html=True)
