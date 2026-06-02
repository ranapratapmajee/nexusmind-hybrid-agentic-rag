import ast
import operator as op


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
    def __init__(self):
        self.tools = {}
        self._register_defaults()

    def register(self, name: str, func):
        self.tools[name] = func

    def _register_defaults(self):
        calc = SafeCalculator()
        self.register("calculator", calc.evaluate)
        self.register("web_search", self._web_search_stub)

    def execute(self, tool_name: str, query: str):
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys()),
            }

        tool = self.tools[tool_name]

        if tool_name == "calculator":
            expression = self._extract_expression(query)
            return tool(expression)

        return tool(query)

    def _extract_expression(self, query: str):
        q = query.lower()
        for prefix in ["calculate", "solve", "what is"]:
            if q.startswith(prefix):
                return query[len(prefix) :].strip()
        return query.strip()

    def _web_search_stub(self, query: str):
        return {"tool": "web_search", "status": "not_implemented", "query": query}
