from typing import Any, Dict
from .base_agent import Agent
from .llm_client import call_llm


class OutlineAgent(Agent):
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        legend_tasks = input_data.get("legend_tasks", [])
        content_summary = input_data.get("raw_legends", [])
        tone = self.config.get("tone", "玄幻奇幻")
        length = self.config.get("length", "中篇小说大纲")

        prompt = self.build_prompt(legend_tasks, content_summary, tone, length)
        outline = call_llm(prompt, self.config)
        return {"novel_outline": outline}

    def build_prompt(self, legend_tasks: list, contents: list, tone: str, length: str) -> str:
        tasks_text = []
        for task in legend_tasks:
            tasks_text.append(f"地区：{task['region']}\n任务说明：{task['task_prompt']}\n")

        summary_text = []
        for item in contents:
            lines = [f"{result['title']}: {result['snippet']}" for result in item.get("results", []) if result.get("title")]
            summary_text.append("地区：" + item["region"] + "\n" + "\n".join(lines))

        return (
            f"你是一个小说大纲专家。请基于下面的传说任务与传说要点，生成一个{length}。\n"
            f"小说风格：{tone}。\n"
            "不要写任何自我介绍、说明性前言或多余的语句。\n"
            "不要只给出章节标题。\n"
            "请直接输出完整的大纲正文，包含每章的核心情节、主要角色、冲突节点、场景和情感走向。\n"
            f"要求包含：主要角色、反派设定、关键地点、主线冲突、三幕结构、世界观背景。\n\n"
            "传说任务：\n"
            + "\n".join(tasks_text)
            + "\n"
            "传说要点：\n"
            + "\n".join(summary_text)
            + "\n"
            "请输出一个清晰的章节大纲，并附带每章的核心冲突和情节推进。"
        )
