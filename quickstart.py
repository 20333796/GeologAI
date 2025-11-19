#!/usr/bin/env python3
"""
GeologAI 快速启动工具
支持测试、开发、部署等多种模式
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

class GeologAILauncher:
    def __init__(self):
        self.backend_dir = Path(__file__).parent / "backend"
        self.workspace_dir = Path(__file__).parent
        
    def run_tests(self, target="all", verbose=False):
        """运行测试套件"""
        os.chdir(self.backend_dir)
        
        if target == "all":
            cmd = "pytest tests/ -v" if verbose else "pytest tests/ -q"
        elif target == "crud":
            cmd = "pytest tests/test_crud.py -v" if verbose else "pytest tests/test_crud.py -q"
        elif target == "service":
            cmd = "pytest tests/test_services.py -v" if verbose else "pytest tests/test_services.py -q"
        elif target == "api":
            cmd = "pytest tests/test_api.py -v" if verbose else "pytest tests/test_api.py -q"
        else:
            print(f"❌ 未知的测试目标: {target}")
            return False
            
        print(f"\n📋 运行 {target} 测试...\n")
        return subprocess.run(cmd, shell=True).returncode == 0
    
    def coverage_report(self):
        """生成覆盖率报告"""
        os.chdir(self.backend_dir)
        
        print("\n📊 生成覆盖率报告...\n")
        result = subprocess.run(
            "pytest tests/test_crud.py tests/test_services.py "
            "--cov=app --cov-report=html --cov-report=term-missing -q",
            shell=True
        )
        
        if result.returncode == 0:
            report_path = self.backend_dir / "htmlcov" / "index.html"
            print(f"\n✅ 覆盖率报告已生成!")
            print(f"📁 位置: {report_path}")
            print(f"💡 用浏览器打开此文件查看详细报告\n")
        
        return result.returncode == 0
    
    def start_dev_server(self, port=8000):
        """启动开发服务器"""
        os.chdir(self.backend_dir)
        
        print(f"""
╔════════════════════════════════════════════════╗
║     GeologAI 开发服务器启动中...               ║
║     地址: http://localhost:{port}                  ║
║     API 文档: http://localhost:{port}/docs        ║
║     ReDoc: http://localhost:{port}/redoc         ║
╚════════════════════════════════════════════════╝
        """)
        
        cmd = f"uvicorn app.main:app --reload --port {port} --host 0.0.0.0"
        return subprocess.run(cmd, shell=True).returncode == 0
    
    def start_docker_compose(self):
        """启动 Docker Compose 完整栈"""
        os.chdir(self.workspace_dir)
        
        print("""
╔════════════════════════════════════════════════╗
║     启动 Docker Compose 栈...                  ║
║     服务: Backend, MySQL, Redis (如配置)       ║
╚════════════════════════════════════════════════╝
        """)
        
        return subprocess.run("docker-compose up -d", shell=True).returncode == 0
    
    def stop_docker_compose(self):
        """停止 Docker Compose"""
        os.chdir(self.workspace_dir)
        print("\n⏹️  停止 Docker Compose 栈...\n")
        return subprocess.run("docker-compose down", shell=True).returncode == 0
    
    def show_status(self):
        """显示系统状态"""
        os.chdir(self.backend_dir)
        
        print("""
╔════════════════════════════════════════════════╗
║          GeologAI 系统状态检查                 ║
╚════════════════════════════════════════════════╝
        """)
        
        # 检查依赖
        print("\n📦 检查依赖...")
        subprocess.run("pip list | findstr fastapi sqlalchemy pydantic", shell=True)
        
        # 显示测试统计
        print("\n📊 测试统计:")
        os.chdir(self.backend_dir)
        subprocess.run("pytest tests/ --collect-only -q", shell=True)
    
    def quick_check(self):
        """快速健康检查"""
        os.chdir(self.backend_dir)
        
        print("""
╔════════════════════════════════════════════════╗
║          快速健康检查 (5 秒)                  ║
╚════════════════════════════════════════════════╝
        """)
        
        # 运行关键测试
        cmd = "pytest tests/test_crud.py tests/test_services.py -q --tb=no"
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode == 0:
            print("\n✅ 所有关键测试通过!")
        else:
            print("\n⚠️  部分测试失败，请运行 'python quickstart.py test --verbose' 查看详情")
        
        return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(
        description="GeologAI 快速启动工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python quickstart.py test              # 运行所有测试
  python quickstart.py test crud -v      # 运行 CRUD 测试 (详细)
  python quickstart.py coverage          # 生成覆盖率报告
  python quickstart.py dev               # 启动开发服务器
  python quickstart.py docker up         # 启动 Docker 栈
  python quickstart.py status            # 显示系统状态
        """)
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="运行测试")
    test_parser.add_argument("target", nargs="?", default="all", 
                            choices=["all", "crud", "service", "api"],
                            help="测试目标")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    # coverage 命令
    subparsers.add_parser("coverage", help="生成覆盖率报告")
    
    # dev 命令
    dev_parser = subparsers.add_parser("dev", help="启动开发服务器")
    dev_parser.add_argument("-p", "--port", type=int, default=8000, help="服务器端口")
    
    # docker 命令
    docker_parser = subparsers.add_parser("docker", help="Docker 操作")
    docker_parser.add_argument("action", choices=["up", "down"], help="操作")
    
    # status 命令
    subparsers.add_parser("status", help="显示系统状态")
    
    # check 命令
    subparsers.add_parser("check", help="快速健康检查")
    
    args = parser.parse_args()
    
    launcher = GeologAILauncher()
    
    if args.command == "test":
        success = launcher.run_tests(args.target, args.verbose)
    elif args.command == "coverage":
        success = launcher.coverage_report()
    elif args.command == "dev":
        success = launcher.start_dev_server(args.port)
    elif args.command == "docker":
        if args.action == "up":
            success = launcher.start_docker_compose()
        else:
            success = launcher.stop_docker_compose()
    elif args.command == "status":
        launcher.show_status()
        success = True
    elif args.command == "check":
        success = launcher.quick_check()
    else:
        parser.print_help()
        success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
