import re
from typing import List, Dict
import PyPDF2

class PDFProcessor:

    def extract_text(self, pdf_path: str) -> str:
        """Extract raw text from a PDF file."""
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def clean_text(self, text: str) -> str:
        """Normalize and clean PDF text for processing."""
        text = re.sub(r"\s+", " ", text)               # collapse whitespace
        text = re.sub(r"–", "-", text)                 # normalize dashes
        text = re.sub(r"[^\S\r\n]+", " ", text)        # remove weird spaces
        text = text.strip()
        return text

    def detect_sections(self, text: str) -> List[Dict]:
        """Very basic header detection based on capitalization and spacing."""
        lines = text.split("\n")
        sections = []
        current_title = "Introduction"
        current_text = ""

        for line in lines:
            # simple heuristic for section headers
            if line.strip().isupper() and len(line.split(" ")) < 10:
                # save previous section
                if current_text:
                    sections.append({"title": current_title, "text": current_text})
                current_title = line.strip().title()
                current_text = ""
            else:
                current_text += line + " "

        if current_text:
            sections.append({"title": current_title, "text": current_text})

        return sections

    def chunk_text(self, text: str, max_tokens: int = 1200) -> List[str]:
        """Chunk text into LLM-sized segments."""
        words = text.split(" ")
        chunks = []
        current = []

        for w in words:
            current.append(w)
            # rough token approximation: 1 token ~ 0.75 words
            if len(current) > max_tokens * 0.75:
                chunks.append(" ".join(current))
                current = []

        if current:
            chunks.append(" ".join(current))

        return chunks

    def process_pdf(self, pdf_path: str):
        """Full pipeline — extract, clean, detect sections, chunk text."""
        raw = self.extract_text(pdf_path)
        cleaned = self.clean_text(raw)
        sections = self.detect_sections(cleaned)
        chunks = self.chunk_text(cleaned)

        return {
            "full_text": cleaned,
            "sections": sections,
            "chunks": chunks
        }
