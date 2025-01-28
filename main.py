# Import required packages
import streamlit as st
from streamlit_chat import message
from app.agent.agent import run_llm

# Page configuration
st.set_page_config(
    page_title="Assistente de conteudo",
    page_icon="🪁",
    layout="wide",
)

# Header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/midia-social.png", width=100)
with col2:
    st.header("Assistente de conteúdo")
    st.markdown("*Seu assistente de IA para geração de conteúdo*")

# Create tabs for chat and documentation
tab1, tab2 = st.tabs(["Chat", "Referências"])

with tab1:
    # Initialize session state
    if "chat_prompt_history" not in st.session_state:
        st.session_state["chat_prompt_history"] = []
    if "chat_answer_history" not in st.session_state:
        st.session_state["chat_answer_history"] = []
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "current_sources" not in st.session_state:
        st.session_state["current_sources"] = []

    # Chat interface
    st.markdown("### Peça ajuda para gerar qualquer conteúdo!")
    prompt = st.text_input(
        "Sua solicitação:",
        placeholder="e.g. Gere uma mensagem de CRM de contagem regressiva para o curso de programação em Python que começa em uma live no dia 26/01/2025 as 20h00",
        key="user_input"
    )

    # Handle user input
    if prompt:
        with st.spinner("🔎 Buscando Referências"):
            generated_response = run_llm(
                query=prompt,
                chat_history=st.session_state["chat_history"]
            )
            
            # Store both path and page content
            sources = [(doc.metadata["file_path"], doc.page_content) for doc in generated_response["source_documents"]]
            st.session_state["current_sources"] = sources
            
            formatted_response = f"{generated_response['result']}"
            
            st.session_state["chat_prompt_history"].append(prompt)
            st.session_state["chat_answer_history"].append(formatted_response)
            st.session_state["chat_history"].append(("human", prompt))
            st.session_state["chat_history"].append(("ai", generated_response["result"]))

    # Display chat history
    if st.session_state["chat_history"]:
        st.markdown("### Histórico de conversars")
        for generated_response, user_prompt in zip(
            st.session_state["chat_answer_history"],
            st.session_state["chat_prompt_history"]
        ):
            message(user_prompt, is_user=True, key=str(user_prompt))
            message(generated_response, key=str(generated_response))
            
        # Show sources for the latest response
        if st.session_state["current_sources"]:
            with st.expander("View Sources"):
                for source_path, content in st.session_state["current_sources"]:
                    st.markdown(f"**Fonte:** {source_path}")
                    st.markdown(f"{content}")

# Add content for the References tab
with tab2:
    st.markdown("### Referências utilizadas")
    st.markdown("Aqui estão os documentos e fontes que o assistente utiliza para gerar respostas:")
    
    if st.session_state["current_sources"]:
        for source_path, content in st.session_state["current_sources"]:
            with st.expander(f"📄 {source_path}"):
                st.markdown(content)
    else:
        st.info("Faça uma pergunta no chat para ver as referências utilizadas.")
