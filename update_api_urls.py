#!/usr/bin/env python
"""Batch update API_BASE_URL in all frontend pages"""
from pathlib import Path

frontend_pages = Path("d:/GeologAI/web/frontend/pages")
exclude_files = {"01_login.py"}  # Already updated

for py_file in frontend_pages.glob("*.py"):
    if py_file.name in exclude_files:
        continue
    
    content = py_file.read_text(encoding='utf-8')
    
    if "127.0.0.1:8000" in content:
        new_content = content.replace("127.0.0.1:8000", "127.0.0.1:8001")
        py_file.write_text(new_content, encoding='utf-8')
        print(f"✅ {py_file.name}")
    else:
        print(f"⏭️  {py_file.name} (no change needed)")

print("\n✅ All files updated!")
