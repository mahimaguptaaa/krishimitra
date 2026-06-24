import fitz  # PyMuPDF

def load_document(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
