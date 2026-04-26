import os
from pathlib import Path
from typing import Any, Dict

import requests


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


def load_environment(root: Path) -> None:
    load_env_file(root / "env")
    load_env_file(root / ".env")


def get_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 GEMINI_API_KEY，请在环境变量或 env 文件中配置。")
    return api_key


def list_gemini_models(api_key: str) -> Dict[str, Any]:
    url = "https://generativelanguage.googleapis.com/v1/models"
    params = {"key": api_key}
    response = requests.get(url, params=params, timeout=30)
    if response.status_code == 404:
        url = "https://generativelanguage.googleapis.com/v1beta2/models"
        response = requests.get(url, params=params, timeout=30)

    response.raise_for_status()
    return response.json()


def main() -> None:
    root = Path(__file__).parent
    load_environment(root)
    api_key = get_api_key()

    print("正在查询 Gemini 可用模型...")
    data = list_gemini_models(api_key)
    models = data.get("models", [])
    if not models:
        print("未找到可用模型，请检查 API Key 或接口权限。")
        return

    print(f"共找到 {len(models)} 个模型：")
    for model in models:
        name = model.get("name")
        description = model.get("description", "无描述")
        availability = model.get("availability", "unknown")
        print(f"- {name}: {description} ({availability})")


if __name__ == "__main__":
    main()
