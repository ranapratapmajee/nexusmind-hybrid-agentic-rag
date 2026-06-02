from removed_files.tools.base import BaseTool


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Performs basic math calculations"

    def run(self, input_data):
        expression = input_data.get("expression", "")

        try:
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
