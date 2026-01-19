import os

import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def build_client(base_url: str | None) -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    base_url = (base_url or "").strip() or None
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def respond(
    message: str,
    history: list[tuple[str, str]],
    endpoint: str,
    model: str,
) -> str:
    client = build_client(endpoint)
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
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except Exception as exc:
        return f"Error from OpenAI API: {exc}"

    if not response.choices:
        return "Error from OpenAI API: empty response choices."

    content = response.choices[0].message.content
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
        title="OpenAI API Chatbot",
        description="A simple Gradio chatbot connected to the OpenAI API.",
        additional_inputs=[endpoint_input, model_input],
    )
    demo.launch()


if __name__ == "__main__":
    main()
