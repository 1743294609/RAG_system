import os
import json
import markdown
from pdfplumber import open as open_pdf
from docx import Document
import pandas as pd

class DocumentLoader:
    @staticmethod
    def load_file(file_path):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return DocumentLoader._load_pdf(file_path)
        elif ext == '.md':
            return DocumentLoader._load_markdown(file_path)
        elif ext == '.json':
            return DocumentLoader._load_json(file_path)
        elif ext == '.txt':
            return DocumentLoader._load_text(file_path)
        elif ext == '.docx':
            return DocumentLoader._load_docx(file_path)
        elif ext == '.xlsx':
            return DocumentLoader._load_xlsx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _load_pdf(file_path):
        content = ""
        with open_pdf(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        return content.strip()
    
    @staticmethod
    def _load_markdown(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        html_content = markdown.markdown(content)
        return html_content
    
    @staticmethod
    def _load_json(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _load_text(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _load_docx(file_path):
        doc = Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])
        return content
    
    @staticmethod
    def _load_xlsx(file_path):
        df = pd.read_excel(file_path)
        return df.to_string()

    @staticmethod
    def get_supported_extensions():
        return ['.pdf', '.md', '.json', '.txt', '.docx', '.xlsx']