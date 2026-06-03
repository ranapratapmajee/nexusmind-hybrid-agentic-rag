import ast
import operator as op
from typing import Any, Dict


# =========================================================
# 🧠 SAFE CALCULATOR ENGINE
# =========================================================
class SafeCalculator:
    _operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.Mod: op.mod,
        ast.USub: op.neg,
    }

    def evaluate(self, expression: str) -> Dict[str, Any]:
        try:
            node = ast.parse(expression, mode="eval").body
            result = self._eval(node)

            return {
                "expression": expression,
                "result": result,
                "success": True,
            }

        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False,
            }

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            return self._operators[type(node.op)](
                self._eval(node.left),
                self._eval(node.right),
            )

        if isinstance(node, ast.UnaryOp):
            return self._operators[type(node.op)](self._eval(node.operand))

        raise TypeError("Unsupported expression")


# =========================================================
# 🧠 TOOL REGISTRY (EVENT-BUS READY)
# =========================================================
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self._register_defaults()

    def register(self, name: str, func):
        self.tools[name] = func

    # ---------------------------------------------------------
    # DEFAULT TOOLS
    # ---------------------------------------------------------
    def _register_defaults(self):
        calc = SafeCalculator()
        self.register("calculator", calc.evaluate)
        self.register("web_search", self._web_search_stub)

    # ---------------------------------------------------------
    # TOOL EXECUTION (STANDARDIZED OUTPUT)
    # ---------------------------------------------------------
    def execute(self, tool_name: str, query: str) -> Dict[str, Any]:

        if tool_name not in self.tools:
            return {
                "tool": tool_name,
                "error": "Tool not found",
                "available_tools": list(self.tools.keys()),
                "success": False,
            }

        tool = self.tools[tool_name]

        try:
            if tool_name == "calculator":
                expression = self._extract_expression(query)
                result = tool(expression)
            else:
                result = tool(query)

            return {
                "tool": tool_name,
                "input": query,
                "output": result,
                "success": True,
            }

        except Exception as e:
            return {
                "tool": tool_name,
                "input": query,
                "error": str(e),
                "success": False,
            }

    # ---------------------------------------------------------
    # EXPRESSION EXTRACTION (SAFE + CLEAN)
    # ---------------------------------------------------------
    def _extract_expression(self, query: str) -> str:
        q = query.lower().strip()

        prefixes = ["calculate", "solve", "what is", "="]

        for prefix in prefixes:
            if q.startswith(prefix):
                return query[len(prefix) :].strip()

        return query.strip()

    # ---------------------------------------------------------
    # STUB TOOL (FUTURE WEB SEARCH INTEGRATION)
    # ---------------------------------------------------------
    def _web_search_stub(self, query: str) -> Dict[str, Any]:
        return {
            "tool": "web_search",
            "query": query,
            "results": [],
            "status": "not_implemented",
            "success": True,
        }
