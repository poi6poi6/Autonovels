from typing import Any, Dict
from .base_agent import Agent
from .llm_client import call_openai


class ReviewAgent(Agent):
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        outline = input_data.get("novel_outline", "")
        draft_text = input_data.get("draft_text", "")
        raw_legends = input_data.get("raw_legends", [])

        prompt = self.build_prompt(outline, draft_text, raw_legends)
        review = call_openai(prompt, self.config)
        return {"review_report": review}

    def build_prompt(self, outline: str, draft_text: str, raw_legends: list) -> str:
        legend_text = []
        for item in raw_legends:
            legend_text.append(
                f"地区：{item['region']}\n" + "\n".join(
                    [f"- {result['title']}: {result['snippet']}" for result in item.get('results', []) if result.get('title')]
                )
            )

        return (
            "你是小说审核者，请检查以下小说文本是否符合小说大纲、传说背景和叙事框架。\n"
            "请给出：\n"
            "1. 与大纲不一致的段落。\n"
            "2. 传说元素是否被合理使用。\n"
            "3. 是否存在情节断层、人物动机不清、主题跑偏等问题。\n"
            f"小说大纲：\n{outline}\n\n"
            f"小说文本：\n{draft_text}\n\n"
            "传说素材：\n"
            + "\n\n".join(legend_text)
            + "\n"
        )
