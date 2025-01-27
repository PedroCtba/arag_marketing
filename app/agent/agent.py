# Import required packages
import os
import streamlit as st

# Importar pacotes do langchain
from langchain.chains.retrieval import create_retrieval_chain
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_pinecone import PineconeVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Importar AI da Groq (Fonte de LLM)
from langchain_groq import ChatGroq

# Definir função para rodar llm RAG
def run_llm(query, chat_history=[], set_stream_lit_secrets=False):
    if set_stream_lit_secrets:
        # Set environment variables from Streamlit secrets
        os.environ["INDEX_NAME"] = st.secrets["INDEX_NAME"]
        os.environ["VOYAGE_API_KEY"] = st.secrets["VOYAGE_API_KEY"]
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]

    # Setar modelo de embedding
    emmbeding = VoyageAIEmbeddings(model="voyage-3")

    # Setar o objeto de busca de similaridade no Pinecone
    docseacrh = PineconeVectorStore(index_name=os.environ["INDEX_NAME"], embedding=emmbeding)

    # Setar modelo e temperatura
    chat = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    # Fazer prompt de retrieval QA
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    # Combinar prompt com chat
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

    # Fazer prompt de repharase (para casos onde tem histórico de conversa a pergunta precisa ser re-fraseada)
    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=docseacrh.as_retriever(), prompt=rephrase_prompt,
    )

    # Criar chain de busca -> prompt + chat (Rag Model)
    qa = create_retrieval_chain(
        history_aware_retriever, combine_docs_chain=stuff_documents_chain,
    )

    # Invocar a chain com a query do usuário
    result = qa.invoke(input={"input": query, "chat_history": chat_history})

    # Ajustar o dicionário do result, e retornar (front end purposes)
    print(result["context"])
    return {
        "query": result["input"],
        "result": result["answer"],
        "source_documents": result["context"]
    }

# Executar como script
if __name__ == "__main__":
    # Chamar função	com query
    res = run_llm(query="Crie uma descrição para um grupo de vendas no whatsapp baseado nas descrições que temos, o contexto atual é um grupo de vendas de carro")

    # Mostrar resposta
    print(res["source_documents"])
