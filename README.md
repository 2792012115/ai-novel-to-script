# 📜 AI 小说转剧本工具

> **AI 辅助剧本创作工具：将 3 章以上小说文本自动转换为结构化 YAML 剧本**
>
> 粘贴小说 → AI 四阶段流水线 → 可编辑的 YAML 剧本初稿

[![Python Tests](https://github.com/2792012115/ai-novel-to-script/actions/workflows/test.yml/badge.svg)](https://github.com/2792012115/ai-novel-to-script/actions/workflows/test.yml)

---

## 📋 项目简介

本工具帮助小说作者快速将作品改编为剧本格式，降低从"小说"到"剧本"的转换门槛。

### 核心功能

| 功能 | 描述 |
|------|------|
| 🎭 **角色自动提取** | 识别所有角色、别名映射、关系网络 |
| 🏗️ **智能场景切分** | 按地点/时间变化自动切分场次 |
| 💬 **对白与节拍生成** | 提取原文对白，标注语气、动作提示 |
| 📄 **YAML 剧本输出** | 符合影视行业惯例的结构化剧本格式 |
| 📐 **完整 Schema 文档** | YAML Schema 定义 + 设计原因说明 |

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────┐
│              前端 (HTML/CSS/JS)               │
│        输入小说文本 → 展示 YAML/JSON          │
└──────────────────┬───────────────────────────┘
                   │ POST /api/convert
┌──────────────────▼───────────────────────────┐
│             FastAPI 后端 (Python)             │
│                                               │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │ 预处理引擎    │  │    AI 四阶段流水线    │  │
│  │ ·章节识别    │  │ ① 角色提取          │  │
│  │ ·元信息提取  │  │ ② 场景切分          │  │
│  │ ·文本清洗    │  │ ③ 对白/节拍生成     │  │
│  └──────────────┘  │ ④ YAML 组装输出     │  │
│                    └──────────┬───────────┘  │
│  ┌───────────────────────────▼────────────┐  │
│  │         YAML 剧本生成器                │  │
│  │    · Schema 合规输出                   │  │
│  │    · JSON/YAML 双格式                  │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  DeepSeek / LLM   │
         │  (四阶段 Prompt)  │
         └───────────────────┘
```

---

## 🚀 快速开始

```bash
# 1. 克隆
git clone <repo-url> && cd ai-novel-to-script

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 4. 启动
python run.py
```

浏览器打开 **http://localhost:8000**，粘贴 3 章以上小说文本即可。

---

## 📐 YAML Schema 设计文档

👉 [完整 Schema 定义与设计原因](docs/yaml_schema.md)

Schema 设计亮点：
- **YAML 而非 JSON**：剧本是人机协作产物，YAML 可读性远优于 JSON
- **beats 数组而非平铺**：允许按节拍类型批量操作（"所有对白加语气标注"）
- **角色表 + 别名映射**：解决小说中同一角色多称呼问题
- **五类节拍**：action / dialogue / voiceover / transition / montage

---

## 🔮 未来扩展

- [ ] 支持分镜脚本（景别、机位、运镜）
- [ ] 多线程叙事（并行时间线）
- [ ] 导出 Final Draft / Fountain 格式
- [ ] AI 辅助修改（"把第三场改成夜景"）
- [ ] 多人协作编辑

---

## 📁 项目结构

```
ai-novel-to-script/
├── backend/
│   ├── main.py                # FastAPI 入口
│   ├── config.py              # 配置
│   ├── models.py              # 数据模型
│   ├── novel_preprocessor.py  # 文本预处理
│   ├── ai_analyzer.py         # AI 四阶段流水线
│   └── script_generator.py    # YAML 生成器
├── frontend/index.html        # Web 前端
├── docs/yaml_schema.md        # Schema 设计文档
├── tests/test_all.py          # 测试
└── run.py                     # 启动脚本
```

---

## 🎥 Demo 视频

👉 [B站观看演示](https://www.bilibili.com/video/待替换)

---

MIT License · XEngineer 2026
