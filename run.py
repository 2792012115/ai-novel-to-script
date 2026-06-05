import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
import uvicorn
from config import config
print(f"http://{config.host}:{config.port}  model={config.openai_model}")
uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
