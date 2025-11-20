"""
GeologAI 官网首页 - 完全独立模块，无侧边栏
"""

import streamlit as st


# 页面配置 - 不配置侧边栏
st.set_page_config(
    page_title="GeologAI - 地质智能分析平台",
    page_icon="🌍",
    layout="wide"
)

# 更彻底隐藏Streamlit所有侧边栏和导航UI
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
    </style>
""", unsafe_allow_html=True)

st.markdown("---")


# ============= 极简导航栏 + 登录注册入口 =============
nav_col1, nav_col2, nav_col3 = st.columns([6, 6, 2])
with nav_col1:
    st.markdown("<div style='font-size: 28px; font-weight: bold; color: #222; padding-top: 6px;'>🌍 GeologAI</div>", unsafe_allow_html=True)
with nav_col2:
    st.markdown("<div style='font-size: 16px; color: #666; padding-top: 12px;'>地质智能分析平台</div>", unsafe_allow_html=True)
with nav_col3:
    login_btn = st.button("登录 / 注册", key="nav_login", use_container_width=True)
    if login_btn:
        st.switch_page("pages/01_auth.py")
st.markdown("---")

# ============= Hero 英雄区 =============
st.markdown("""
<div style='text-align: center; padding: 60px 0px;'>
    <h1 style='font-size: 48px; font-weight: bold; margin-bottom: 20px;'>
        🌍 智能地质分析平台
    </h1>
    <p style='font-size: 24px; color: #666; margin-bottom: 40px;'>
        AI 赋能的地质数据智能分析和预测系统
    </p>
    <p style='font-size: 16px; color: #888; line-height: 1.8;'>
        结合深度学习、地球物理学和地质学知识<br/>
        为地质勘探、矿产评估、油气勘探提供精准的智能解决方案
    </p>
</div>
""", unsafe_allow_html=True)

# 行动按钮
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])


# 行动按钮（仅展示，不跳转登录/注册）
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
with btn_col1:
    st.button("📚 了解更多", use_container_width=True, key="hero_learn")
with btn_col2:
    st.button("💬 联系我们", use_container_width=True, key="hero_contact")
with btn_col3:
    st.button("🌐 访问官网", use_container_width=True, key="hero_web")

st.markdown("---")

# ============= 核心优势 =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 50px;'>
        为什么选择 GeologAI？
    </h2>
</div>
""", unsafe_allow_html=True)

feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)

features = [
    {
        "icon": "🤖",
        "title": "AI 驱动",
        "desc": "深度学习模型自动分析地质数据，准确率高达 95%"
    },
    {
        "icon": "⚡",
        "title": "实时处理",
        "desc": "秒级响应速度，支持大规模数据实时分析处理"
    },
    {
        "icon": "🔒",
        "title": "安全可靠",
        "desc": "企业级数据加密，ISO27001 认证保护"
    },
    {
        "icon": "📈",
        "title": "可视化",
        "desc": "3D 交互式地图，直观展示分析结果"
    }
]

for idx, feature in enumerate(features):
    cols = [feature_col1, feature_col2, feature_col3, feature_col4]
    with cols[idx]:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(72, 219, 251, 0.1), rgba(72, 219, 251, 0.05));
            border: 2px solid rgba(72, 219, 251, 0.2);
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <div style='font-size: 48px; margin-bottom: 15px;'>{feature["icon"]}</div>
            <div style='font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333;'>
                {feature["title"]}
            </div>
            <div style='font-size: 14px; color: #666; line-height: 1.6;'>
                {feature["desc"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============= 核心功能模块 =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 50px;'>
        核心功能模块
    </h2>
</div>
""", unsafe_allow_html=True)

module_col1, module_col2, module_col3 = st.columns(3)

modules = [
    {
        "icon": "📁",
        "title": "项目管理",
        "items": ["创建项目", "任务追踪", "团队协作", "版本控制"]
    },
    {
        "icon": "💾",
        "title": "数据管理",
        "items": ["数据上传", "格式转换", "数据清洗", "数据预处理"]
    },
    {
        "icon": "🔍",
        "title": "智能分析",
        "items": ["AI 模型", "深度学习", "实时预测", "结果导出"]
    }
]

module_cols = [module_col1, module_col2, module_col3]

for idx, module in enumerate(modules):
    with module_cols[idx]:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
            border: 2px solid rgba(76, 175, 80, 0.2);
            border-radius: 12px;
            padding: 30px 20px;
        '>
            <div style='font-size: 40px; margin-bottom: 15px;'>{module["icon"]}</div>
            <div style='font-size: 20px; font-weight: bold; margin-bottom: 15px; color: #333;'>
                {module["title"]}
            </div>
            <div style='font-size: 14px; color: #666;'>
        """, unsafe_allow_html=True)
        
        for item in module["items"]:
            st.markdown(f"✅ {item}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("---")

# ============= 性能统计 =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 50px;'>
        平台数据
    </h2>
</div>
""", unsafe_allow_html=True)

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

stats = [
    {"number": "10,000+", "label": "活跃用户"},
    {"number": "1,000,000+", "label": "处理数据点"},
    {"number": "95%", "label": "预测准确率"},
    {"number": "24/7", "label": "技术支持"}
]

stat_cols = [stat_col1, stat_col2, stat_col3, stat_col4]

for idx, stat in enumerate(stats):
    with stat_cols[idx]:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 152, 0, 0.05));
            border: 2px solid rgba(255, 152, 0, 0.2);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
        '>
            <div style='font-size: 32px; font-weight: bold; color: #FF9800; margin-bottom: 10px;'>
                {stat["number"]}
            </div>
            <div style='font-size: 14px; color: #666;'>
                {stat["label"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============= 客户案例 =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 50px;'>
        客户案例
    </h2>
</div>
""", unsafe_allow_html=True)

case_col1, case_col2, case_col3 = st.columns(3)

cases = [
    {
        "title": "油田勘探优化",
        "company": "中石油集团",
        "result": "提升预测准确率 40%",
        "desc": "通过 AI 模型优化钻井位置选择，节省成本 2000 万元"
    },
    {
        "title": "矿产资源评估",
        "company": "紫金矿业",
        "result": "评估时间缩短 60%",
        "desc": "自动分析地质数据，加快矿产评估效率"
    },
    {
        "title": "地震风险预测",
        "company": "中国地震局",
        "result": "预警准确度 92%",
        "desc": "基于多源数据的深度学习预测地震风险"
    }
]

case_cols = [case_col1, case_col2, case_col3]

for idx, case in enumerate(cases):
    with case_cols[idx]:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(156, 39, 176, 0.1), rgba(156, 39, 176, 0.05));
            border: 2px solid rgba(156, 39, 176, 0.2);
            border-radius: 12px;
            padding: 25px;
        '>
            <div style='font-size: 18px; font-weight: bold; margin-bottom: 8px; color: #333;'>
                {case["title"]}
            </div>
            <div style='font-size: 13px; color: #888; margin-bottom: 12px;'>
                <strong>客户：</strong> {case["company"]}
            </div>
            <div style='
                background: #F3E5F5;
                border-left: 4px solid #9C27B0;
                padding: 12px;
                margin-bottom: 12px;
                border-radius: 4px;
            '>
                <div style='font-size: 14px; font-weight: bold; color: #9C27B0;'>
                    ✨ {case["result"]}
                </div>
            </div>
            <div style='font-size: 13px; color: #666; line-height: 1.6;'>
                {case["desc"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============= 技术栈 =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 30px;'>
        技术支撑
    </h2>
</div>
""", unsafe_allow_html=True)

tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)

techs = [
    {"name": "PyTorch", "desc": "深度学习框架"},
    {"name": "TensorFlow", "desc": "机器学习库"},
    {"name": "PostgreSQL", "desc": "数据库系统"},
    {"name": "Kubernetes", "desc": "容器编排"}
]

tech_cols = [tech_col1, tech_col2, tech_col3, tech_col4]

for idx, tech in enumerate(techs):
    with tech_cols[idx]:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.1), rgba(33, 150, 243, 0.05));
            border: 2px solid rgba(33, 150, 243, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        '>
            <div style='font-size: 16px; font-weight: bold; color: #333; margin-bottom: 5px;'>
                {tech["name"]}
            </div>
            <div style='font-size: 12px; color: #888;'>
                {tech["desc"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============= 定价方案 =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 50px;'>
        灵活的定价方案
    </h2>
</div>
""", unsafe_allow_html=True)

price_col1, price_col2, price_col3 = st.columns(3)

pricing = [
    {
        "name": "基础版",
        "price": "¥299/月",
        "features": [
            "5 个项目",
            "100 GB 存储",
            "基础分析工具",
            "邮件支持"
        ],
        "highlight": False
    },
    {
        "name": "专业版",
        "price": "¥999/月",
        "features": [
            "无限项目",
            "1 TB 存储",
            "完整分析工具",
            "优先支持",
            "自定义报告"
        ],
        "highlight": True
    },
    {
        "name": "企业版",
        "price": "定制",
        "features": [
            "专属服务器",
            "无限存储",
            "专业团队",
            "24/7 电话支持",
            "定制开发"
        ],
        "highlight": False
    }
]

price_cols = [price_col1, price_col2, price_col3]

for idx, plan in enumerate(pricing):
    with price_cols[idx]:
        bg_color = "rgba(76, 175, 80, 0.1)" if plan["highlight"] else "rgba(200, 200, 200, 0.05)"
        border_color = "rgba(76, 175, 80, 0.4)" if plan["highlight"] else "rgba(200, 200, 200, 0.2)"
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {bg_color}, rgba(255, 255, 255, 0.05));
            border: 3px solid {border_color};
            border-radius: 12px;
            padding: 30px;
        '>
            <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333;'>
                {plan["name"]}
            </div>
            <div style='font-size: 28px; font-weight: bold; color: #4CAF50; margin-bottom: 20px;'>
                {plan["price"]}
            </div>
        """, unsafe_allow_html=True)
        
        for feature in plan["features"]:
            st.markdown(f"✅ {feature}")
        
        st.markdown("", unsafe_allow_html=True)
        st.button(f"选择 {plan['name']}", use_container_width=True, key=f"price_{idx}")
        
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============= FAQ =============
st.markdown("""
<div style='text-align: center; padding: 40px 0px;'>
    <h2 style='font-size: 36px; font-weight: bold; margin-bottom: 50px;'>
        常见问题
    </h2>
</div>
""", unsafe_allow_html=True)

with st.expander("🔹 GeologAI 支持哪些数据格式？"):
    st.markdown("""
    我们支持多种地质数据格式，包括：
    - **地震数据**: SEG-Y, miniSEED
    - **测井数据**: LAS, ASCII
    - **地图数据**: GeoTIFF, ShapeFile
    - **表格数据**: CSV, Excel, NetCDF
    """)

with st.expander("🔹 数据安全性如何保证？"):
    st.markdown("""
    我们采取多层安全措施：
    - 🔐 军级 AES-256 加密传输和存储
    - ✅ ISO 27001 信息安全管理体系认证
    - 🛡️ 定期安全审计和渗透测试
    - 📋 完全符合 GDPR 和 CCPA 合规
    """)

with st.expander("🔹 如何快速开始使用？"):
    st.markdown("""
    只需 3 步：
    1. 点击"立即开始"注册账户
    2. 上传地质数据文件
    3. 运行 AI 分析，查看结果
    
    通常 5 分钟内即可完成首次分析。
    """)

with st.expander("🔹 提供哪些技术支持？"):
    st.markdown("""
    我们提供多种支持方式：
    - 📧 邮件支持（24 小时内回复）
    - 💬 在线客服（工作时间）
    - 📚 详细文档库
    - 🎓 免费培训课程
    - ☎️ 企业版电话支持（24/7）
    """)

st.markdown("---")

# ============= Call to Action =============
st.markdown("""
<div style='
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(76, 175, 80, 0.05));
    border: 2px solid rgba(76, 175, 80, 0.3);
    border-radius: 12px;
    padding: 50px 30px;
    text-align: center;
    margin: 40px 0px;
'>
    <h2 style='font-size: 32px; font-weight: bold; margin-bottom: 20px; color: #333;'>
        准备好了吗？
    </h2>
    <p style='font-size: 18px; color: #666; margin-bottom: 30px;'>
        立即加入数千名地质专业人士，体验 AI 驱动的智能分析
    </p>
</div>
""", unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 1, 1])

with cta_col1:
    if st.button("🚀 免费试用 14 天", use_container_width=True, type="primary", key="cta_try"):
        st.session_state.current_page = "auth"
        st.switch_page("pages/01_auth.py")

with cta_col2:
    if st.button("📧 申请演示", use_container_width=True, key="cta_demo"):
        st.info("请发送邮件至: demo@geologai.com")

with cta_col3:
    if st.button("💬 咨询销售", use_container_width=True, key="cta_sales"):
        st.info("📞 400-800-8888")

st.markdown("---")

# ============= 底部导航 =============
footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)

with footer_col1:
    st.markdown("""
    **产品**
    - 功能特性
    - 定价方案
    - 安全性
    """)

with footer_col2:
    st.markdown("""
    **公司**
    - 关于我们
    - 博客
    - 招聘
    """)

with footer_col3:
    st.markdown("""
    **资源**
    - 文档
    - API 参考
    - 示例代码
    """)

with footer_col4:
    st.markdown("""
    **联系**
    - 📧 support@geologai.com
    - 📞 +86-10-1234-5678
    - 🌐 www.geologai.com
    """)

st.markdown("---")

st.markdown("""
<div style='text-align: center; color: #999; font-size: 12px; padding: 30px 0px;'>
    © 2024 GeologAI. All rights reserved. | 
    <a href='#'>隐私政策</a> | 
    <a href='#'>用户协议</a> | 
    <a href='#'>联系我们</a>
</div>
""", unsafe_allow_html=True)
