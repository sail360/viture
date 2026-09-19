# src/tool_providers/tool_router.py
"""
Basic tool router for Project. Add tool logic here and import in project.py.
"""

from .calculator import calculator_tool
from .echo import echo_tool
from .tell_time import tell_time_tool

# Tool registry and OpenAI-style tool spec for LLM tool-calling
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "A simple calculator that evaluates arithmetic expressions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The arithmetic expression to evaluate."}
                },
                "required": ["expression"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "echo",
            "description": "Echoes back the provided text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to echo back."}
                },
                "required": ["text"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tell_time",
            "description": "Tells the current date and time.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

tool_registry = {
    "calculator": calculator_tool,
    "echo": echo_tool,
    "tell_time": lambda: tell_time_tool(),
}

def tool_router(user_input: str) -> str | None:
    """
    Checks user input for tool commands and executes them.
    Returns tool result string or None if no tool matched.
    """
    # Calculator tool
    if user_input.lower().startswith('calc:'):
        expr = user_input[len('calc:'):].strip()
        return calculator_tool(expr)
    # Echo tool
    if user_input.lower().startswith('echo:'):
        text = user_input[len('echo:'):].strip()
        return echo_tool(text)
    # Tell time tool - direct text trigger
    if user_input.lower().startswith('time') or 'what time' in user_input.lower():
        return tell_time_tool()
    # Example: if user_input starts with 'search:', perform a search
    if user_input.lower().startswith('search:'):
        query = user_input[len('search:'):].strip()
        # Placeholder: simulate a tool result
        tool_result = f"[TOOL] Search result for '{query}': ..."
        return tool_result
    # Add more tool checks here as needed
    return None
