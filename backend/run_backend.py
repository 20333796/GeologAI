#!/usr/bin/env python
"""Direct server startup script for port 8001"""
import os
import sys
from pathlib import Path

# Setup path
backend_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_dir))

# Load .env
env_file = backend_dir / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Override port for this session
os.environ['PORT'] = '8001'

if __name__ == '__main__':
    import uvicorn
    print("🚀 Starting GeologAI Backend on http://127.0.0.1:8001")
    uvicorn.run(
        'app.main:app',
        host='127.0.0.1',
        port=8001,
        reload=False,
        log_level='info'
    )
