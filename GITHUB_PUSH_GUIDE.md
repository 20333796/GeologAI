# GitHub 推送指南 & CI/CD 激活步骤

## 📋 前置条件检查清单

- [ ] 本地所有测试通过 (58/58 CRUD + Service)
- [ ] 代码覆盖率报告已生成
- [ ] `requirements.txt` 已更新
- [ ] `.github/workflows/backend-ci.yml` 已创建
- [ ] `.gitignore` 已配置
- [ ] README.md 已更新

---

## 🔧 推送到 GitHub 的步骤

### 第 1 步: 初始化 Git 仓库 (如果还未初始化)

```bash
cd d:\GeologAI
git init
git config user.name "你的名字"
git config user.email "你的邮箱"
```

### 第 2 步: 创建 .gitignore 文件

```bash
# 在项目根目录创建
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Project specific
data/raw/*
data/processed/*
*.log
EOF
```

### 第 3 步: 添加所有文件并创建初始提交

```bash
git add .

git commit -m "Phase 4 完成: 完整测试套件 + CI/CD 集成

- 实现 31 个 CRUD 单元测试 (100% 通过率)
- 实现 27 个 Service 层测试 (100% 通过率)
- 生成代码覆盖率报告 (60% 整体覆盖)
- 创建 GitHub Actions CI 工作流
- 修复所有依赖注入和导入问题
- 完善测试 fixture 系统"
```

### 第 4 步: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建仓库 "GeologAI" (或你喜欢的名称)
3. **不要** 初始化 README、.gitignore 或 license (我们已有本地版本)

### 第 5 步: 添加远程仓库并推送

```bash
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/GeologAI.git

# 推送到 main 分支
git branch -M main
git push -u origin main
```

**或使用 SSH** (推荐用于后续操作):

```bash
# 首先配置 SSH (如果还未配置)
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh

git remote set-url origin git@github.com:YOUR_USERNAME/GeologAI.git
git push -u origin main
```

---

## ✅ 验证 GitHub Actions CI

### 1. 检查 GitHub Actions 状态

1. 访问 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 查看 "backend-ci" 工作流的状态

### 2. CI 工作流应该:

- ✅ 在 Python 3.10 上运行测试
- ✅ 在 Python 3.11 上运行测试
- ✅ 生成覆盖率报告
- ✅ 上传到 Codecov (如已配置)
- ✅ 归档 HTML 覆盖率报告

### 3. 故障排查

如果 CI 失败，检查:

```bash
# 查看 GitHub Actions 日志中是否有这些错误:
1. ModuleNotFoundError: No module named 'app'
   → 确保工作流在 backend/ 目录运行

2. ImportError: cannot import name 'xyz'
   → 检查 requirements.txt 中的依赖

3. MySQL connection error
   → 这是预期的 (使用 SQLite for tests)
```

---

## 🚀 持续集成工作流图

```
┌─────────────────┐
│  git push       │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│  GitHub Actions 触发         │
│  (on: push, pull_request)    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Python 3.10/3.11 环境       │
│  安装依赖                     │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  运行 CRUD 测试               │
│  (31 个测试)                 │
└────────┬─────────────────────┘
         │
         ├─► ✅ 全部通过
         │
         ▼
┌──────────────────────────────┐
│  运行 Service 测试            │
│  (27 个测试)                 │
└────────┬─────────────────────┘
         │
         ├─► ✅ 全部通过
         │
         ▼
┌──────────────────────────────┐
│  生成覆盖率报告              │
│  (HTML + Term output)        │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  上传到 Codecov (可选)       │
│  Create artifacts            │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  ✅ 构建成功                  │
│  (已准备好合并/部署)         │
└──────────────────────────────┘
```

---

## 📊 工作流配置说明

你的 `.github/workflows/backend-ci.yml` 包含:

### 触发条件
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```
→ 在 main/develop 分支的每个推送和 PR 上运行

### 测试策略
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']
```
→ 在多个 Python 版本上测试以确保兼容性

### 覆盖率上报
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```
→ 将覆盖率报告发送到 Codecov (可视化趋势)

---

## 🔐 配置 Codecov (可选但推荐)

### 1. 在 Codecov 注册

访问 https://codecov.io 并用 GitHub 账户登录

### 2. 启用仓库

- 访问 https://app.codecov.io
- 搜索你的 GeologAI 仓库
- 点击 "Setup repo" 激活

### 3. 无需额外配置

大多数情况下，Codecov 会自动检测你的 GitHub Actions 工作流

### 4. 查看覆盖率徽章

在 README.md 中添加:

```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/GeologAI/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/GeologAI)
```

---

## 📝 更新 README.md

在推送前，更新项目的 README.md 包含:

```markdown
# GeologAI - 地质数据管理与 AI 预测系统

[![codecov](https://codecov.io/gh/YOUR_USERNAME/GeologAI/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/GeologAI)
[![CI/CD](https://github.com/YOUR_USERNAME/GeologAI/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/GeologAI/actions)

## 📊 项目状态

- ✅ Phase 1-3: 后端框架 (完成)
- ✅ Phase 4: 测试 & CI (完成)
- 🔄 Phase 5: 前端 & 部署 (进行中)

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/GeologAI.git
cd GeologAI

# 运行测试
cd backend
pytest tests/ -v

# 启动开发服务器
python -m uvicorn app.main:app --reload
```

## 📚 文档

- [完整项目总结](PHASE4_COMPLETION_SUMMARY.md)
- [快速启动指南](QUICK_START_CARD.md)
- [系统设计文档](SYSTEM_DESIGN.md)
- [API 参考](API_QUICK_REFERENCE.md)

## 📊 测试覆盖率

- **CRUD 测试**: 31/31 ✅
- **Service 测试**: 27/27 ✅
- **代码覆盖率**: 60%

## 🛠️ 技术栈

- FastAPI + Uvicorn
- SQLAlchemy 2.0
- Pydantic v2
- MySQL / SQLite
- pytest

---

**由 GitHub Copilot 生成**
```

---

## 🔄 后续工作流

### 日常开发流程

```bash
# 1. 创建特性分支
git checkout -b feature/new-feature

# 2. 做出更改并测试
pytest tests/ -v

# 3. 提交更改
git add .
git commit -m "Add new feature: [description]"

# 4. 推送到远程
git push origin feature/new-feature

# 5. 在 GitHub 上创建 Pull Request (PR)
# → GitHub Actions 自动运行测试

# 6. 如果 CI 通过，合并 PR 到 main
```

### 监控 CI 状态

```bash
# 查看最新工作流运行
gh run list --limit 10

# 查看特定工作流的详细信息
gh run view [run-id]

# 查看工作流日志
gh run view [run-id] --log
```

---

## 🎯 部署到生产的前置条件

推送到生产前确保:

- [ ] 所有测试通过 ✅
- [ ] GitHub Actions CI 成功 ✅
- [ ] 代码覆盖率 > 60% ✅
- [ ] 没有 lint 错误
- [ ] 文档已更新
- [ ] 依赖已安全审查

---

## 📌 重要提示

1. **第一次推送需要一些时间**: GitHub 需要初始化 Actions
2. **工作流日志保存 90 天**: 之后自动删除
3. **制品保留**: HTML 覆盖率报告保留 3 个月
4. **并发限制**: 免费账户每月 2000 分钟 GitHub Actions (通常足够)

---

## ✅ 推送检查清单

在运行 `git push` 前检查:

```bash
# 1. 确认本地测试都通过
cd backend
pytest tests/ -q
# 预期: 58 passed

# 2. 检查 Git 状态
git status

# 3. 查看待提交的更改
git diff --staged

# 4. 确认远程配置正确
git remote -v

# 5. 确认在正确的分支
git branch

# 6. 拉取最新更改 (如果有其他贡献者)
git pull origin main

# 7. 最后推送
git push -u origin main
```

---

**最后检查**: 所有 58 个核心测试 ✅ 通过
**推送时间**: 预计 2-3 分钟
**CI 运行时间**: 预计 3-5 分钟

---

## 🆘 常见问题

**Q: 推送后没有看到 GitHub Actions 运行?**
A: 等待 30 秒，然后刷新 GitHub 页面的 Actions 标签

**Q: CI 失败了怎么办?**
A: 检查工作流日志查看具体错误，本地重现问题后修复，重新提交

**Q: 如何跳过 CI 运行?**
A: 在提交消息中添加 `[skip ci]` (不推荐)
```bash
git commit -m "doc: Update README [skip ci]"
```

---

**准备好推送了吗? 🚀**

