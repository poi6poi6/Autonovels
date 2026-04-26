import os
import requests
from typing import Any, Dict


def get_api_key(config: Dict[str, Any]) -> str:
    provider = config.get("provider", "gemini").lower()
    default_env = "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"
    api_key_env = config.get("api_key_env", default_env)
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(f"缺少 API Key，请设置环境变量 {api_key_env}。")
    return api_key


def extract_text_from_gemini_candidate(candidate: Dict[str, Any]) -> str:
    if not isinstance(candidate, dict):
        return ""
    content = candidate.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts", [])
    text_parts = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        if "text" in part and isinstance(part["text"], str):
            text_parts.append(part["text"])
    return "".join(text_parts).strip()


def call_gemini(prompt: str, config: Dict[str, Any]) -> str:
    api_key = get_api_key(config)
    model = config.get("model", "gemini-2.5-flash")
    if not model.startswith("models/"):
        model = f"models/{model}"
    temperature = float(config.get("temperature", 0.7))
    max_tokens = int(config.get("max_tokens", 1200))
    timeout = float(config.get("request_timeout", 120))
    max_retries = int(config.get("retry_attempts", 2))
    backoff = float(config.get("retry_backoff", 5.0))

    url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {
        "model": model,
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        print(f"[LLM] Gemini 请求第 {attempt}/{max_retries} 次，等待 API 响应... (timeout={timeout}s)")
        try:
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini API 返回为空候选，无法读取生成结果。")

            text = extract_text_from_gemini_candidate(candidates[0])
            if not text:
                raise RuntimeError("Gemini API 返回的候选内容无法解析为文本。")

            print("[LLM] Gemini 响应完成，继续下一步。")
            return text
        except requests.Timeout as exc:
            last_error = exc
            print(f"[LLM] Gemini 请求超时，第 {attempt} 次失败：{exc}")
        except requests.RequestException as exc:
            last_error = exc
            status = getattr(exc.response, 'status_code', None)
            body = getattr(exc.response, 'text', None)
            print(f"[LLM] Gemini 请求异常，第 {attempt} 次失败：{status} {body}")
            if status and status < 500:
                break
        except Exception as exc:
            last_error = exc
            print(f"[LLM] Gemini 处理失败，第 {attempt} 次失败：{exc}")
            break

        if attempt < max_retries:
            print(f"[LLM] 等待 {backoff} 秒后重试...")
            import time
            time.sleep(backoff)

    raise RuntimeError(
        "Gemini API 请求失败，请确认模型名称、API Key 是否正确，或网络是否稳定。"
        f" URL: {url} 错误: {last_error}"
    )


def call_llm(prompt: str, config: Dict[str, Any]) -> str:
    provider = config.get("provider", "gemini").lower()
    if provider == "gemini":
        return call_gemini(prompt, config)
    raise RuntimeError(f"不支持的 LLM provider: {provider}")
