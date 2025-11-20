"""
启动脚本：在导入应用前加载 backend/.env 环境变量，然后启动 uvicorn
"""
import os
from pathlib import Path

env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Ensure uvicorn is available
try:
    import uvicorn
except Exception as e:
    raise SystemExit(f"uvicorn is required but not installed: {e}")

host = os.getenv('HOST', '127.0.0.1')
port = int(os.getenv('PORT', '8000'))
reload_flag = os.getenv('DEBUG', 'False').lower() == 'true'
if __name__ == '__main__':
    uvicorn.run('app.main:app', host=host, port=port, reload=reload_flag)
