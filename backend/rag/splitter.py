from langchain.text_splitter import RecursiveCharacterTextSplitter

class AgriSplitter:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "।", ".", " "]
        )

    def split(self, text: str, metadata: dict) -> list:
        docs = self.splitter.create_documents([text], metadatas=[metadata])
        return docs
