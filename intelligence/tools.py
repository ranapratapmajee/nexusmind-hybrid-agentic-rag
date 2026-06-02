import ast
import operator as op
from typing import Any, Callable, Dict


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

    def evaluate(self, expression: str) -> float:
        try:
            node = ast.parse(expression, mode="eval").body
            return self._eval(node)
        except Exception as e:
            return {"error": f"Invalid expression: {str(e)}"}

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
# 🧠 TOOL REGISTRY
# =========================================================
class ToolRegistry:
    """
    Central tool execution layer
    Router decides tool → Orchestrator executes
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_defaults()

    def register(self, name: str, func: Callable):
        self.tools[name] = func

    def _register_defaults(self):
        calc = SafeCalculator()
        self.register("calculator", calc.evaluate)
        self.register("web_search", self._web_search_stub)

    # =========================================================
    # EXECUTION
    # =========================================================
    def execute(self, tool_name: str, query: str) -> Any:

        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys()),
            }

        tool = self.tools[tool_name]

        try:
            # -------------------------
            # TOOL-SPECIFIC HANDLING
            # -------------------------
            if tool_name == "calculator":
                expression = self._extract_expression(query)
                return tool(expression)

            return tool(query)

        except Exception as e:
            return {"error": str(e), "tool": tool_name}

    # =========================================================
    # SAFE EXPRESSION EXTRACTION
    # =========================================================
    def _extract_expression(self, query: str) -> str:
        """
        Converts:
        'calculate 2+2'
        → '2+2'
        """

        q = query.lower()

        for prefix in ["calculate", "solve", "what is"]:
            if q.startswith(prefix):
                return query[len(prefix) :].strip()

        return query.strip()

    # =========================================================
    # FALLBACK DETECTION (ONLY IF ROUTER FAILS)
    # =========================================================
    def detect(self, query: str) -> str:
        q = query.lower()

        if any(k in q for k in ["+", "-", "*", "/", "calculate", "solve"]):
            return "calculator"

        if any(k in q for k in ["search", "google", "web"]):
            return "web_search"

        return "calculator"

    # =========================================================
    # WEB STUB
    # =========================================================
    def _web_search_stub(self, query: str):
        return {
            "tool": "web_search",
            "status": "not_implemented",
            "query": query,
            "result": "Web search layer will be implemented in next phase",
        }
