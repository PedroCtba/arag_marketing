# Import required packages
import os
import streamlit as st

# Importar pacotes do langchain
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Importar AI da Groq (Fonte de LLM)
from langchain_groq import ChatGroq

# Import prompts
from .prompts import retrieval_marketing_agent_initial_prompt, retrieval_marketing_agent_rephrase_prompt

# Import guard rails
from .guard.retrieval_based_guardrail import RetrievalBasedGuardrail

# Definir função para rodar llm RAG
def run_llm(query, chat_history=[], set_stream_lit_secrets=False):
    if set_stream_lit_secrets:
        # Set environment variables from Streamlit secrets
        os.environ["INDEX_NAME"] = st.secrets["INDEX_NAME"]
        os.environ["VOYAGE_API_KEY"] = st.secrets["VOYAGE_API_KEY"]
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    
    # Initialize the retriever
    embedding = VoyageAIEmbeddings(model="voyage-3")
    docsearch = PineconeVectorStore(index_name=os.environ["INDEX_NAME"], embedding=embedding)

    # Set the LLM model
    chat = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    # Combine prompt with chat
    stuff_documents_chain = create_stuff_documents_chain(chat, PromptTemplate.from_template(retrieval_marketing_agent_initial_prompt))

    # Use history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=docsearch.as_retriever(), prompt=PromptTemplate.from_template(retrieval_marketing_agent_rephrase_prompt)
    )

    # Create the RAG pipeline
    qa = create_retrieval_chain(
        history_aware_retriever, combine_docs_chain=stuff_documents_chain,
    )

    # Invoke the chain with user's query and chat history
    result = qa.invoke(input={"input": query, "chat_history": chat_history})

    # Return structured response
    return {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"]
    }

# Executar como script
if __name__ == "__main__":
    # Chamar função	com query
    res = run_llm(query="Gere uma mensagem de CRM de contagem regressiva para o curso de programação em Python que começa em uma live no dia 26/01/2025 as 20h00")

    # Mostrar resposta
    print(res)
