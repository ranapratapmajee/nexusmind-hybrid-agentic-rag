class ContextFormatter:
    def format(self, query: str, results: list):
        context_blocks = []

        for r in results:
            context_blocks.append(
                f"[SOURCE: {r['meta'].get('filename', 'unknown')}]\n{r['text']}"
            )

        return "\n\n".join(context_blocks)
