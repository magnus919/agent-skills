# AutoGen Tool Integration

## register_function

Bind Python functions as agent tools:

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

assistant.register_function(function_map={"search_web": search_web})
```

## MCP Tool Integration

Connect MCP servers as agent tools:

```python
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

server_params = StdioServerParams(command="npx", args=["@playwright/mcp@latest"])
async with McpWorkbench(server_params) as mcp:
    agent = AssistantAgent(
        "web_browsing_assistant",
        model_client=model_client,
        workbench=mcp,
    )
```

## Key Guidelines

- Tool functions need clear docstrings (become tool descriptions)
- Tools should handle errors gracefully and return strings
- For complex integrations, wrap external APIs with error handling
- MCP tools enable browser automation, databases, and external services
