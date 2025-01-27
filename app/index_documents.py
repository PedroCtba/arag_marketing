from rag.vector_store import VectorStoreHandler
from rag.document_processor import DocumentProcessor
from rag.loader import MarketingDataLoader
from dotenv import load_dotenv
from tqdm import tqdm
import os

def main():
    load_dotenv()
    
    # Initialize components
    data_loader = MarketingDataLoader(data_dir=r"C:\Users\PedroMiyasaki\OneDrive - DHAUZ\Área de Trabalho\Projetos\PESSOAL\arag_marketing\data\processed")
    document_processor = DocumentProcessor(
        chunk_size=500,  # Smaller chunks for better context
        chunk_overlap=50
    )
    vector_store = VectorStoreHandler(index_name=os.getenv("INDEX_NAME"))
    
    # Load all documents (no specific campaign)
    print("Loading documents...")
    documents = data_loader.load_campaign_data()
    
    if not documents:
        print("No documents found in processed directory!")
        return
        
    print(f"Found {len(documents)} documents")
    
    # Process documents
    print("Processing documents...")
    processed_docs = document_processor.process_documents(
        documents=[doc['content'] for doc in documents],
        metadatas=[doc['metadata'] for doc in documents]
    )
    
    print(f"Created {len(processed_docs)} chunks")
    
    # Add to vector store
    print("Adding to vector store...")
    for doc in tqdm(processed_docs, desc="Indexing"):
        vector_store.add_texts(
            texts=[doc.page_content],
            metadatas=[doc.metadata]
        )
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()
