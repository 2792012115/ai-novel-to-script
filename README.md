# 📜 AI 小说转剧本工具

将 3 章以上小说 → 结构化 YAML 剧本

[![Python Tests](https://github.com/2792012115/ai-novel-to-script/actions/workflows/test.yml/badge.svg)](https://github.com/2792012115/ai-novel-to-script/actions)

## 核心功能
- 🎭 角色自动提取（含别名映射、关系网络）
- 🏗️ 智能场景切分（按地点/时间变化）
- 💬 对白与节拍生成（5种 beat 类型）
- 📄 YAML 剧本输出

## 快速开始
```bash
pip install -r backend/requirements.txt
cp .env.example .env  # 填入 OPENAI_API_KEY
python run.py
```
浏览器打开 http://localhost:8000

## YAML Schema 文档
👉 [完整 Schema 定义与设计原因](docs/yaml_schema.md)

## Demo 视频
👉 [B站观看演示](https://www.bilibili.com/video/待替换)

MIT License · XEngineer 2026
