import os
import yaml
from pathlib import Path
from agents.search_agent import WebSearchLegendAgent
from agents.outline_agent import OutlineAgent
from agents.write_agent import WritingAgent
from agents.review_agent_fixed import ReviewAgent


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    root = Path(__file__).parent
    load_env_file(root / "env")
    load_env_file(root / ".env")
    config = load_config(root / "config.yaml")

    search_agent = WebSearchLegendAgent("search_agent", config.get("search", {}))
    llm_config = config.get("llm", {})
    outline_agent = OutlineAgent("outline_agent", {**llm_config, **config.get("outline", {})})
    write_agent = WritingAgent("write_agent", {**llm_config, **config.get("write", {"chapter_count": 3})})
    review_agent = ReviewAgent("review_agent", {**llm_config, **config.get("review", {})})

    print("[1/4] 收集传说素材并生成写作任务...")
    legend_output = search_agent.run({"regions": config.get("search", {}).get("regions", [])})

    print("[2/4] 生成小说大纲...")
    outline_output = outline_agent.run(legend_output)

    print("[3/4] 生成小说稿件...")
    existing_draft = ""
    draft_file = root / "output" / "draft_text.txt"
    if draft_file.exists():
        existing_draft = draft_file.read_text(encoding="utf-8")
        print("检测到已有 draft_text.txt，已把现有内容传给写作 agent 继续写作。")

    draft_output = write_agent.run({**legend_output, **outline_output, "existing_draft": existing_draft})

    print("[4/4] 审核小说产出...")
    review_output = review_agent.run({**legend_output, **outline_output, **draft_output})

    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "legend_data.yaml").write_text(yaml.safe_dump(legend_output, allow_unicode=True), encoding="utf-8")
    (output_dir / "novel_outline.txt").write_text(outline_output["novel_outline"], encoding="utf-8")
    (output_dir / "draft_text.txt").write_text(draft_output["draft_text"], encoding="utf-8")
    (output_dir / "review_report.txt").write_text(review_output["review_report"], encoding="utf-8")

    print("工作流完成，结果已保存到 output/ 文件夹。")


if __name__ == "__main__":
    main()
