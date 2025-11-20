#!/usr/bin/env python
"""Fix API endpoints in frontend pages"""
from pathlib import Path
import re

frontend_pages = Path("d:/GeologAI/web/frontend/pages")

# Mapping of incorrect endpoints to correct ones
endpoint_fixes = {
    "/api/projects": "/api/v1/projects",
    "/api/data/upload": "/api/v1/data/upload",
    "/api/data": "/api/v1/data",
    "/api/analysis": "/api/v1/analysis",
    "/api/predictions": "/api/v1/predictions",
    "/api/models": "/api/v1/models",
    "/api/explainability": "/api/v1/explainability",
    "/api/deeplearning": "/api/v1/deeplearning",
}

for py_file in frontend_pages.glob("*.py"):
    content = py_file.read_text(encoding='utf-8')
    original_content = content
    
    for old_endpoint, new_endpoint in endpoint_fixes.items():
        content = content.replace(old_endpoint, new_endpoint)
    
    if content != original_content:
        py_file.write_text(content, encoding='utf-8')
        print(f"✅ {py_file.name}")

print("\n✅ All endpoints fixed!")
