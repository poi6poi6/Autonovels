# 小说 Agent 工作流

这是一个多 Agent 协同写作框架，用于自动收集各地传说、生成小说任务、产出小说内容，并以大纲与历史内容进行验证。

## 目录结构

- `agents/`
  - `base_agent.py`：Agent 基类
  - `llm_client.py`：LLM 调用工具
  - `search_agent.py`：自动收集传说并生成写作任务
  - `outline_agent.py`：构建/维护小说大纲
  - `write_agent.py`：基于大纲和传说内容写作
  - `review_agent.py`：验证产出是否符合大纲与前文
- `run_workflow.py`：执行工作流
- `config.yaml`：配置示例
- `requirements.txt`：依赖列表

## 快速开始

1. 安装依赖：
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. 在环境变量中配置模型和搜索 API Key：
   - `GEMINI_API_KEY`
   - `SERPAPI_API_KEY`（如果启用 SerpAPI 搜索）
3. 修改 `config.yaml` 中的地区词条和写作风格。
4. 运行：
   ```powershell
   python run_workflow.py
   ```

## 说明

- `WebSearchLegendAgent`：负责自动收集传说、提取关键内容并生成写作任务。
- `OutlineAgent`：根据传说素材和小说目标，生成或更新小说大纲。
- `WritingAgent`：将大纲与传说内容结合，产出小说章节或片段。
- `ReviewAgent`：验证产出是否符合大纲，检查前后文一致性。

> 该工作流可根据实际模型和搜索服务扩展为更完整的自动写作流水线。