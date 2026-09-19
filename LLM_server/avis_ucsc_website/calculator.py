"""
A simple calculator tool.
Usage: 'calc: <expression>'
"""
def calculator_tool(expression: str) -> str:
    try:
        # Only allow safe characters
        allowed = set('0123456789+-*/(). ') 
        if not set(expression).issubset(allowed):
            return "[TOOL] Calculator: Invalid characters in expression."
        result = eval(expression, {"__builtins__": {}})
        return f"[TOOL] Calculator result: {result}"
    except Exception as e:
        return f"[TOOL] Calculator error: {e}"
