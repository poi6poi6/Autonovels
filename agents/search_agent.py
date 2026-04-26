import os
import re
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
        outline = input_data.get("outline", "").strip()
        regions = input_data.get("regions", [])
        raw_legends = []

        if outline:
            queries = self.build_queries_from_outline(outline)
        else:
            queries = [f"{region} 传说 民间故事" for region in regions]

        for query in queries:
            search_results = self.search_web(query)
            raw_legends.append({
                "region": query,
                "query": query,
                "results": search_results,
            })

        tasks = self.generate_tasks(raw_legends)
        return {"raw_legends": raw_legends, "legend_tasks": tasks}

    def build_queries_from_outline(self, outline: str) -> List[str]:
        terms: List[str] = []
        patterns = [
            r"角色[:：]\s*([^，。；\n]+)",
            r"主要角色[:：]\s*([^，。；\n]+)",
            r"反派[:：]\s*([^，。；\n]+)",
            r"地点[:：]\s*([^，。；\n]+)",
            r"场景[:：]\s*([^，。；\n]+)",
            r"神器[:：]\s*([^，。；\n]+)",
            r"神祇[:：]\s*([^，。；\n]+)",
            r"魔法[:：]\s*([^，。；\n]+)",
            r"势力[:：]\s*([^，。；\n]+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, outline)
            for match in matches:
                term = match.strip()
                if term and term not in terms:
                    terms.append(term)
                    if len(terms) >= self.max_results:
                        break
            if len(terms) >= self.max_results:
                break

        if not terms:
            lines = [line.strip() for line in outline.splitlines() if line.strip()]
            for line in lines:
                if any(keyword in line for keyword in ["传说", "神话", "神", "魔", "神器", "古代", "王朝", "英雄"]):
                    term = line.split("：")[-1].strip() if "：" in line else line
                    if term and term not in terms:
                        terms.append(term)
                        if len(terms) >= self.max_results:
                            break

        if not terms:
            first_lines = [line.strip() for line in outline.splitlines() if line.strip()]
            terms = first_lines[: self.max_results]

        queries = [f"{term} 传说 神话" for term in terms[: self.max_results]]
        return queries

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
            region = item.get("region", item.get("query", "大纲"))
            detail = "\n".join(
                [f"- {result['title']}: {result['snippet']}" for result in item["results"] if result.get("title")]
            )
            prompt = (
                f"请根据以下{region}的传说摘要，生成3条适合小说写作的任务：\n"
                f"{detail}\n"
                f"每条任务都要包含：主题、主角冲突、魔幻元素、历史/本土氛围。"
            )
            tasks.append({"region": region, "task_prompt": prompt})
        return tasks
