from typing import Any, Dict
from .base_agent import Agent
from .llm_client import call_llm


class WritingAgent(Agent):
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        outline = input_data.get("novel_outline", "")
        raw_legends = input_data.get("raw_legends", [])
        chapter_count = self.config.get("chapter_count", 3)

        prompt = self.build_prompt(outline, raw_legends, chapter_count)
        draft = call_llm(prompt, self.config)
        return {"draft_text": draft}

    def build_prompt(self, outline: str, raw_legends: list, chapter_count: int) -> str:
        legend_text = []
        for item in raw_legends:
            legend_text.append(
                f"地区：{item['region']}\n" + "\n".join(
                    [f"- {result['title']}: {result['snippet']}" for result in item.get('results', []) if result.get('title')]
                )
            )

        return (
            "你是小说写作者。请根据下面的小说大纲以及收集到的传说素材，写出前几章的小说片段。\n"
            "不要写任何自我介绍、创作说明或‘写作者已就位’之类的前言。\n"
            "不要只给出章节标题。\n"
            "请直接给出每一章的完整故事内容，包含人物、对话、场景、情节推进和情感刻画。\n"
            "要求：\n"
            "1. 保持与大纲一致，且每章都要交代世界观和人物关系。\n"
            "2. 融合传说中的关键元素与地域风情。\n"
            f"大纲：\n{outline}\n\n"
            "传说素材：\n"
            + "\n\n".join(legend_text)
            + "\n\n"
            f"请写出前 {chapter_count} 章，每章不少于 350 字，直接输出正文，不要只写标题。"
        )
