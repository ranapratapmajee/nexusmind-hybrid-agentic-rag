import re


class TextPreprocessor:
    def clean(self, text: str) -> str:
        # normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # normalize newlines
        text = re.sub(r"\n{2,}", "\n\n", text)

        return text.strip()
