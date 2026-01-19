import os

import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()


def build_endpoint(base_url: str | None) -> str:
    base_url = (base_url or "").strip() or "https://api.openai.com/v1"
    return base_url.rstrip("/")


def respond(
    message: str,
    history: list[tuple[str, str]],
    endpoint: str,
    model: str,
) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Missing OPENAI_API_KEY environment variable."

    base_url = build_endpoint(endpoint)
    messages = []
    for pair in history:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        user_msg, assistant_msg = pair
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})

    model = (model or "").strip() or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": messages},
            timeout=600,
        )
    except requests.RequestException as exc:
        return f"Error from OpenAI API: {exc}"

    if response.status_code >= 400:
        return f"Error from OpenAI API: {response.status_code} {response.text}"

    try:
        data = response.json()
    except ValueError:
        return "Error from OpenAI API: invalid JSON response."

    if not isinstance(data, dict):
        print(data)
        return "Error from OpenAI API: unexpected JSON response."

    choices = data.get("choices", [])
    if not choices:
        return "Error from OpenAI API: empty response choices."

    content = choices[0].get("message", {}).get("content", "")
    return content or ""


def main() -> None:
    endpoint_input = gr.Textbox(
        label="Endpoint (base URL)",
        placeholder="https://api.openai.com/v1",
        value=os.environ.get("OPENAI_BASE_URL", ""),
    )
    model_input = gr.Textbox(
        label="Model",
        placeholder="gpt-4o-mini",
        value=os.environ.get("OPENAI_MODEL", ""),
    )
    demo = gr.ChatInterface(
        fn=respond,
        title="OpenAI API Chatbot (HTTP)",
        description="A simple Gradio chatbot using HTTP requests (no SDK).",
        additional_inputs=[endpoint_input, model_input],
    )
    demo.launch()


if __name__ == "__main__":
    main()
