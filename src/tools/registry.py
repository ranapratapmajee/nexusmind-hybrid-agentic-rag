from typing import Dict, Optional

from src.tools.base import BaseTool


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    # ----------------------------
    # Register Tool
    # ----------------------------
    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    # ----------------------------
    # Get Tool
    # ----------------------------
    def get(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    # ----------------------------
    # List Tools (for debug / UI)
    # ----------------------------
    def list_tools(self):
        return {name: tool.description for name, tool in self.tools.items()}

    # ----------------------------
    # Auto Detect Tool from Query
    # ----------------------------
    def detect(self, query: str) -> Optional[str]:
        q = query.lower()

        # 🔢 calculator tool
        if any(op in q for op in ["+", "-", "*", "/", "%"]):
            return "calculator"

        # 🧠 future extensions
        if "price" in q or "buy" in q:
            return "commerce_search"

        if "search" in q:
            return "web_search"

        return None

    # ----------------------------
    # Execute Tool Safely
    # ----------------------------
    def execute(self, tool_name: str, query: str):
        tool = self.get(tool_name)

        if not tool:
            return f"[ToolRegistry] No tool found: {tool_name}"

        try:
            return tool.run(query)
        except Exception as e:
            return f"[Tool Error] {str(e)}"
