"""AI 小说转剧本工具 - 启动脚本"""
import os, sys

project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(project_root, "backend"))
sys.path.insert(0, os.path.join(project_root, "backend"))

try:
    from dotenv import load_dotenv
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ 已加载环境变量: {env_path}")
    else:
        print("⚠️ 未找到 .env，请复制 .env.example → .env 填入 API Key")
except ImportError:
    pass

openai_key = os.getenv("OPENAI_API_KEY", "")
if not openai_key:
    print("❌ OPENAI_API_KEY 未设置！")
    sys.exit(1)

import uvicorn
from config import config

print(f"""
╔══════════════════════════════════════╗
║   📜 AI 小说转剧本工具 v1.0        ║
║   模型: {config.openai_model:<28}║
║   地址: http://{config.host}:{config.port}             ║
╚══════════════════════════════════════╝
""")

uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
