import os
import requests
from typing import Any, Dict, List
from .base_agent import Agent


class WebSearchLegendAgent(Agent):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.provider = config.get("provider", "serpapi")
        self.api_key_env = config.get("api_key_env", "SERPAPI_API_KEY")
        self.max_results = int(config.get("max_results", 3))

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        regions = input_data.get("regions", [])
        raw_legends = []

        for region in regions:
            query = f"{region} 传说 民间故事" 
            search_results = self.search_web(query)
            raw_legends.append({
                "region": region,
                "query": query,
                "results": search_results,
            })

        tasks = self.generate_tasks(raw_legends)
        return {"raw_legends": raw_legends, "legend_tasks": tasks}

    def search_web(self, query: str) -> List[Dict[str, Any]]:
        if self.provider.lower() == "serpapi":
            return self.search_serpapi(query)
        raise RuntimeError(f"不支持的搜索提供商: {self.provider}")

    def search_serpapi(self, query: str) -> List[Dict[str, Any]]:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"缺少 SerpAPI API Key，请设置环境变量 {self.api_key_env}。")

        url = "https://serpapi.com/search.json"
        params = {
            "q": query,
            "engine": "google",
            "api_key": api_key,
            "num": self.max_results,
            "hl": "zh-CN",
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        organic = data.get("organic_results", [])
        return [
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link"),
            }
            for item in organic[: self.max_results]
        ]

    def generate_tasks(self, raw_legends: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        tasks = []
        for item in raw_legends:
            region = item["region"]
            detail = "\n".join(
                [f"- {result['title']}: {result['snippet']}" for result in item["results"] if result.get("title")]
            )
            prompt = (
                f"请根据以下{region}地区的传说摘要，生成3条适合小说写作的任务：\n"
                f"{detail}\n"
                f"每条任务都要包含：主题、主角冲突、魔幻元素、历史/本土氛围。"
            )
            tasks.append({"region": region, "task_prompt": prompt})
        return tasks
