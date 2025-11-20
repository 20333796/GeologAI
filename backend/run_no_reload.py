"""
Start backend with .env and without uvicorn autoreload (Windows-friendly background run)
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
            # Do not overwrite existing environment variables (allow CLI override)
            if k.strip() not in os.environ:
                os.environ[k.strip()] = v.strip()

try:
    import uvicorn
except Exception as e:
    raise SystemExit(f"uvicorn is required but not installed: {e}")

host = os.getenv('HOST', '127.0.0.1')
port = int(os.getenv('PORT', '8000'))

if __name__ == '__main__':
    uvicorn.run('app.main:app', host=host, port=port, reload=False)
