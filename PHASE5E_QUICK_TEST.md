# 🎉 Phase 5E 快速测试指南

## ✅ 架构完成情况

### 三个独立页面已完成
1. **`00_home.py`** - 官网首页 [隐藏侧边栏]
2. **`01_auth.py`** - 登录/注册页 [隐藏侧边栏]
3. **`02_dashboard.py`** - 后台仪表板 [显示侧边栏]

### 核心特性
✅ 文件名全英文
✅ 页面内容全中文
✅ 官网和认证页无侧边栏
✅ 仪表板有完整侧边栏菜单
✅ 三个页面完全独立
✅ JWT认证集成
✅ 表单验证完整

---

## 🚀 快速启动

### 方式1：分别启动（推荐，便于调试）

**终端1 - 启动后端**
```powershell
cd D:\GeologAI\backend
conda run -n geologai uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**终端2 - 启动前端**
```powershell
cd D:\GeologAI
conda run -n geologai streamlit run web/frontend/app.py --server.port 8501
```

### 方式2：批处理脚本

双击运行：
- `D:\GeologAI\start_backend_test.bat` (后端)
- `D:\GeologAI\start_frontend_test.bat` (前端)

---

## 🧪 测试场景

### 场景1：未认证用户访问
```
1. 打开 http://localhost:8501
2. 🔍 应该看到：官网首页
3. ✓ 应该看到：
   - 公司信息和功能介绍
   - 最新资讯板块
   - 「注册/登录」按钮
   - NO侧边栏
```

### 场景2：点击注册/登录
```
1. 点击右上角「注册/登录」按钮
2. 🔍 应该看到：认证页面
3. ✓ 应该看到：
   - 登录和注册两个标签页
   - 演示账户快速登录
   - NO侧边栏
```

### 场景3：使用演示账户登录
```
1. 保持在「登录」标签页
2. 点击「使用演示账户登录」
3. 🔍 应该看到：仪表板
4. ✓ 应该看到：
   - 个性化欢迎信息
   - 4个统计卡片
   - 10个功能模块卡片
   - LEFT侧边栏 ✨（主要差异点）
   - 侧边栏菜单项：项目管理、数据管理等
```

### 场景4：仪表板导航
```
1. 在仪表板上
2. 查看左侧菜单
3. ✓ 应该有以下菜单项：
   - 首页
   - 项目管理
   - 数据管理
   - 数据分析
   - 地理可视化
   - AI模型库
   - 性能评估
   - 报告生成
   - 系统设置
   - 帮助中心
   - 集成工具
   - 登出
```

### 场景5：登出
```
1. 在仪表板上
2. 点击左侧菜单最下方的「登出」
   或顶部右侧的「登出」按钮
3. 🔍 应该返回：官网首页
4. ✓ 确认：
   - 回到官网首页
   - NO侧边栏
   - 认证令牌已清除
```

### 场景6：注册新账户
```
1. 进入认证页面
2. 切换到「注册」标签页
3. 填写表单：
   - 用户名：testuser2024
   - 邮箱：test2024@example.com
   - 姓名：测试用户
   - 密码：TestPass123
   - 确认密码：TestPass123
4. 勾选「我已阅读并同意...」
5. 点击「创建账户」
6. ✓ 应该看到：
   - 成功消息
   - 自动切换回登录标签页
   - 可以用新账户登录
```

---

## 🔑 演示账户

```
用户名：demo_user
密码：DemoUser123
```

---

## 📋 验证清单

使用此清单来验证整个系统：

### 页面结构 ✓
- [ ] 官网首页 (`00_home.py`) 存在
- [ ] 认证页面 (`01_auth.py`) 存在
- [ ] 仪表板 (`02_dashboard.py`) 存在
- [ ] 所有文件名都是英文

### 侧边栏显示 ✓
- [ ] 官网首页：NO侧边栏
- [ ] 认证页面：NO侧边栏
- [ ] 仪表板：HAS侧边栏

### 功能流程 ✓
- [ ] 未认证用户看到官网
- [ ] 已认证用户看到仪表板
- [ ] 登录成功后自动重定向
- [ ] 登出成功后回到官网

### 认证功能 ✓
- [ ] 演示账户可以登录
- [ ] 密码验证正常
- [ ] 邮箱格式验证正常
- [ ] 新注册账户可以创建

### UI/UX ✓
- [ ] 中文界面正确显示
- [ ] 10个功能模块卡片显示
- [ ] 统计卡片显示正确
- [ ] 最近活动列表显示
- [ ] 所有按钮可点击

---

## 🐛 常见问题

**Q: 无法连接到后端？**
```
A: 确保后端在 http://localhost:8001 运行
   检查：netstat -ano | findstr :8001
```

**Q: 页面之间无法跳转？**
```
A: 清除浏览器缓存和Streamlit缓存
   Streamlit缓存位置：~/.streamlit/
   或重启Streamlit进程
```

**Q: 侧边栏没有显示/隐藏？**
```
A: 检查 st.set_page_config() 中的 initial_sidebar_state
   hidden  → 官网和认证页
   expanded → 仪表板
```

**Q: 登录后还是看到官网？**
```
A: 检查 st.session_state.auth_token 是否正确设置
   检查网络连接到后端
   检查浏览器是否有 cookie/session 问题
```

---

## 📊 API端点检查

**检查后端API是否正常**

```bash
# 检查后端是否运行
curl http://localhost:8001/docs

# 尝试登录演示账户
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"DemoUser123"}'
```

---

## 🎯 下一步

1. ✅ **架构完成** - 三个独立页面已完成
2. ⏳ **集成功能模块** - 将10个模块链接到实际功能
3. ⏳ **优化UI/UX** - 根据反馈调整界面
4. ⏳ **完整测试** - 各种场景和用例测试

---

**准备好测试了吗？🚀**

快速开始命令：
```bash
# 终端1
cd D:\GeologAI\backend && conda run -n geologai uvicorn app.main:app --host 0.0.0.0 --port 8001

# 终端2
cd D:\GeologAI && conda run -n geologai streamlit run web/frontend/app.py --server.port 8501
```

然后访问：http://localhost:8501
