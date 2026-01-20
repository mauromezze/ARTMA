# Using OpenAI/Anthropic (requires 'smolagents[litellm]')
from smolagents import LiteLLMModel
from smolagents import (
    ToolCallingAgent,
    CodeAgent,
    DuckDuckGoSearchTool,
    ApiWebSearchTool,
    GoogleSearchTool,
    SpeechToTextTool,
    VisitWebpageTool,
    WebSearchTool,
    WikipediaSearchTool,
    MCPClient
)
from tools import CurrentDateTimeTool, ReadExcelTool, CalculatorTool
from dotenv import load_dotenv
import os
import gradio as gr

load_dotenv()

model = LiteLLMModel(
    model_id="openai/"+os.environ.get("OPENAI_MODEL"),
    api_base=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY")
    )

try:
    MCPBrowser = MCPClient(
        {
            "url": "http://localhost:8931/mcp",
            "transport": "streamable-http",
        }
    )
    MCP_BROWSER_TOOLS = MCPBrowser.get_tools()
except Exception as exc:
    MCPBrowser = None
    MCP_BROWSER_TOOLS = []
    print(f"Warning: MCPBrowser unavailable ({exc})")

TOOL_REGISTRY = {
    "DuckDuckGoSearchTool": DuckDuckGoSearchTool,
    "WikipediaSearchTool": WikipediaSearchTool,
    "VisitWebpageTool": VisitWebpageTool,
    "ApiWebSearchTool": ApiWebSearchTool,
    "GoogleSearchTool": GoogleSearchTool,
    "SpeechToTextTool": SpeechToTextTool,
    "WebSearchTool": WebSearchTool,
    "CurrentDateTimeTool": CurrentDateTimeTool,
    #"SqliteSelectTool": SqliteSelectTool,
    "ReadExcelTool": ReadExcelTool,
    "CalculatorTool": CalculatorTool,
}

if MCP_BROWSER_TOOLS:
    TOOL_REGISTRY["MCPBrowser"] = MCP_BROWSER_TOOLS  # npx @playwright/mcp@latest --port 8931

def _format_agent_response(result):
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        for key in ("text", "final_answer", "output", "answer", "content"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return str(result)
    return str(result)


def chat_with_agent(message, history, agent_type, enabled_tools, max_steps, planning_interval):
    tools = []
    for name in enabled_tools:
        entry = TOOL_REGISTRY[name]
        if callable(entry):
            tools.append(entry())
        elif isinstance(entry, list):
            tools.extend(entry)
        else:
            tools.append(entry)
    max_steps = int(max_steps) if str(max_steps).strip() else None
    planning_interval = int(planning_interval) if str(planning_interval).strip() else None
    if agent_type == "CodeAgent":
        agent = CodeAgent(
            tools=tools,
            model=model,
            max_steps=max_steps,
            planning_interval=planning_interval,
        )
    else:
        agent = ToolCallingAgent(
            tools=tools,
            model=model,
            max_steps=max_steps,
            planning_interval=planning_interval,
        )
    return _format_agent_response(agent.run(message))


ui = gr.ChatInterface(
    fn=chat_with_agent,
    title="Agent Chat",
    description="Chat with the smolagents agent.",
    additional_inputs=[
        gr.Radio(
            choices=["ToolCallingAgent", "CodeAgent"],
            value="ToolCallingAgent",
            label="Agent type",
        ),
        gr.CheckboxGroup(
            choices=list(TOOL_REGISTRY.keys()),
            #value=["DuckDuckGoSearchTool"],
            label="Enabled tools",
        )
        ,
        gr.Textbox(
            value="20",
            label="Max steps",
            placeholder="e.g. 10",
        ),
        gr.Textbox(
            value="",
            label="Planning interval",
            placeholder="e.g. 2",
        ),
    ],
)


if __name__ == "__main__":
    ui.launch()
