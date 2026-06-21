# app/ingestion/pdf_loader.py

from pathlib import Path
import pypdf
from config.settings import get_settings

class PDFLoader:
    def __init__(self):
        self.settings = get_settings()

    def extract_text(self, file_path: Path) -> str:
        """
        Reads a binary PDF file from disk and extracts clean, raw text content.
        Safely filters out empty pages or broken formatting structural lines.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Target PDF document not found at: {file_path}")

        extracted_text_segments = []
        
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text_segments.append(page_text)
                    
        return "\n\n".join(extracted_text_segments)