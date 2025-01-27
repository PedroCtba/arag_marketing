from typing import List, Dict, Any
from langchain_voyageai import VoyageAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

class VectorStoreHandler:
    def __init__(self, index_name: str):
        load_dotenv()
        
        # Initialize Pinecone
        pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        self.index_name = index_name
        self.embeddings = VoyageAIEmbeddings(voyage_api_key=os.getenv("VOYAGE_API_KEY"), model="voyage-3")
        
        # Create index if it doesn't exist
        if self.index_name not in [k["name"] for k in pinecone.list_indexes()]:
            pinecone.create_index(
                name=self.index_name,
                metric='cosine',
                dimension=1024 ,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        
        self.index = pinecone.Index(self.index_name)
        self.vectorstore = PineconeVectorStore(self.index, self.embeddings, "text")
    
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None) -> List[str]:
        """Add texts to the vector store"""
        return self.vectorstore.add_texts(texts, metadatas)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        """Search for similar documents"""
        return self.vectorstore.similarity_search(query, k=k)
    
    def delete_all(self):
        """Delete all vectors in the index"""
        self.index.delete(delete_all=True)