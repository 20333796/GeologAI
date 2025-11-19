#!/usr/bin/env python3
"""
Create GitHub repository using GitHub API
"""

import subprocess
import sys

def main():
    username = "20333796"
    email = "20333796@qq.com"
    password = "z110112113"
    repo_name = "GeologAI"
    
    print("=" * 60)
    print("GitHub Repository Setup")
    print("=" * 60)
    
    # Step 1: Configure Git with user info
    print("\n[1] 配置 Git 用户信息...")
    subprocess.run(["git", "config", "--global", "user.name", username], 
                   cwd="d:\\GeologAI")
    subprocess.run(["git", "config", "--global", "user.email", email], 
                   cwd="d:\\GeologAI")
    print("✓ Git 用户信息配置完成")
    
    # Step 2: Show remote
    print("\n[2] 当前远程配置:")
    result = subprocess.run(["git", "remote", "-v"], 
                           cwd="d:\\GeologAI", 
                           capture_output=True, 
                           text=True)
    print(result.stdout)
    
    # Step 3: Try to push (will prompt for credentials)
    print("\n[3] 尝试推送到 GitHub...")
    print("⚠️ 注意：Git 会弹出凭证输入窗口")
    print("   用户名: 20333796")
    print("   密码: z110112113 或 PAT token")
    print()
    
    result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                           cwd="d:\\GeologAI")
    
    if result.returncode == 0:
        print("\n✅ 推送成功！")
        print(f"仓库地址: https://github.com/{username}/{repo_name}")
    else:
        print("\n❌ 推送失败")
        print("\n🔧 如果失败，请按以下步骤操作:")
        print("1. 访问 https://github.com/new")
        print("2. 创建新仓库 'GeologAI'")
        print("3. 不要初始化任何文件")
        print("4. 创建后，在本地运行:")
        print("   git push -u origin main")
        sys.exit(1)

if __name__ == "__main__":
    main()
