# 小说 Agent 工作流

这是一个多 Agent 协同写作框架，用于自动收集各地传说、生成小说任务、产出小说内容，并以大纲与历史内容进行验证。

## 目录结构

- `agents/`
  - `base_agent.py`：Agent 基类
  - `llm_client.py`：Gemini LLM 调用工具
  - `search_agent.py`：自动收集传说并生成写作任务
  - `outline_agent.py`：构建/维护小说大纲
  - `write_agent.py`：基于大纲、传说内容和已有文本写作
  - `review_agent_fixed.py`：验证产出是否符合大纲与前文
- `run_workflow.py`：执行工作流
- `config.yaml`：配置示例
- `requirements.txt`：依赖列表
- `.gitignore`：忽略环境和输出文件

## 快速开始

1. 安装依赖：
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. 在环境变量中配置模型和搜索 API Key：
   - `GEMINI_API_KEY`
   - `SERPAPI_API_KEY`（如果启用 SerpAPI 搜索）
3. 修改 `config.yaml` 的第二段配置：
   - `search.regions`
   - `llm.model`
   - `outline.tone`
   - `outline.length`
4. 如果你希望使用自带大纲，请创建 `input/outline.txt` 并写入你的大纲。
5. 初次生成：
   ```powershell
   python run_workflow.py
   ```

## 自带大纲搜索

如果 `input/outline.txt` 存在，工作流会直接使用该大纲作为小说大纲，并基于大纲中的角色、地点、神器、神祇等元素自动生成搜索关键词，检索相关神话/传说素材。

- 可以直接把你准备好的章节大纲、人物设定、世界观描述写入 `input/outline.txt`
- 系统会根据大纲构建搜索 query，如“XXX 传说 神话”
- 搜索结果会用于生成写作任务，并结合大纲推进小说写作

## 续写已有内容

如果 `output/draft_text.txt` 已经存在，工作流会自动读取它，并把现有内容传给写作 agent：

- `write_agent.py` 会将 `draft_text.txt` 作为 `existing_draft`
- 模型会在已有文本基础上继续写，不重复已有内容
- 这样你可以逐次补全小说，而不是每次都从头生成

如果你想重新开始，请先删除 `output/draft_text.txt`，然后重新运行工作流。

## 重要文件说明

- `config.yaml`
  - `llm`：Gemini 模型配置
  - `search`：SerpAPI 搜索配置
  - `outline`：大纲风格和长度
- `output/`
  - `legend_data.yaml`
  - `novel_outline.txt`
  - `draft_text.txt`
  - `review_report.txt`

## 注意事项

- 目前默认使用 Gemini API 作为 LLM 后端。
- `env` 或 `.env` 中的 API Key 不会被推送到仓库。
- 如果输出内容过短，请检查 `GEMINI_API_KEY` 是否有效，并确保模型调用成功。

> 该工作流适合以传说素材为输入，逐步迭代生成小说内容。