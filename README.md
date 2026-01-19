# ARTMA Modulo 6a - Gradio Agents

Small demo project for building Gradio chat UIs backed by OpenAI-compatible models and smolagents tools.

## What is inside
- `app.py`: Gradio chatbot using the OpenAI Python SDK.
- `app_http.py`: same chatbot but with raw HTTP requests.
- `agent.py`: smolagents-based chat with tool selection (web search, calculator, Excel reader, etc.).
- `tools.py`: custom tools (date/time, Excel reader, safe calculator).

## Requirements
- Python 3.10+
- An OpenAI-compatible API key

Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment variables
Create a `.env` file (or set in your shell):
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`

## Run the demos
OpenAI SDK chatbot:
```bash
python app.py
```

HTTP-only chatbot:
```bash
python app_http.py
```

Smolagents tool-calling chat:
```bash
python agent.py
```

## Notes
- `agent.py` exposes a tool selector in the UI. Tools include DuckDuckGo/Wikipedia search, webpage visiting, a calculator, and an Excel reader.
- The Excel tool expects a local `.xlsx` file path.
- The MCP browser tool requires a running MCP server, for example:
  ```bash
  npx @playwright/mcp@latest --port 8931
  ```

## License
MIT.
