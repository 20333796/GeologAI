#!/usr/bin/env python
"""
手动初始化数据库并强制创建 demo_user 账户
"""
from backend.app.db.init_db import init_database, create_sample_data

if __name__ == "__main__":
    print("初始化数据库...")
    init_database()
    print("写入演示账户...")
    create_sample_data()
    print("完成！")
