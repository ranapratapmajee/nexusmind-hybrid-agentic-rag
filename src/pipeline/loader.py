import glob
import os
from abc import ABC, abstractmethod

import fitz


class BaseLoader(ABC):
    @abstractmethod
    def load(self) -> list[dict]:
        pass


class LocalFileLoader(BaseLoader):
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir

    def load(self):
        documents = []
        pattern = os.path.join(self.data_dir, "*.*")

        print(f"📁 Scanning {self.data_dir}...")

        for path in glob.glob(pattern):
            filename = os.path.basename(path)

            try:
                if path.endswith((".txt", ".md")):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                elif path.endswith(".pdf"):
                    content = self._read_pdf(path)

                else:
                    continue

                documents.append(
                    {
                        "source": "local",
                        "filename": filename,
                        "content": content.strip(),
                    }
                )

            except Exception as e:
                print(f"❌ Failed {filename}: {e}")

        return documents

    def _read_pdf(self, path):
        text = ""
        with fitz.open(path) as pdf:
            for page in pdf:
                text += page.get_text("text") + "\n\n"
        return text
