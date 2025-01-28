from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Process documents and split them into chunks
        """
        if metadatas is None:
            metadatas = [{} for _ in documents]
            
        docs = [
            Document(page_content=text, metadata=metadata)
            for text, metadata in zip(documents, metadatas)
        ]
        
        return self.text_splitter.split_documents(docs) 
