from langchain_groq import ChatGroq
import os

class ThemeBasedGuardrail:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        self.temas_de_marketing = [
            "criação de conteúdo",
            "estratégia de marketing",
            "branding",
            "comunicação",
            "crm",
            "campanhas",
            "mídias sociais",
            "email marketing",
            "marketing digital",
            "estratégia de conteúdo"
        ]
        
        self.validation_prompt = """
        Analise se a seguinte consulta do usuário está relacionada a atividades de marketing/criação de conteúdo.
        Retorne apenas "true" se estiver relacionada a marketing, ou "false" se não estiver.
        
        Consulta: {query}
        
        Resposta (true/false):
        """
        
        self.default_message = {
            "query": "",
            "result": "Desculpe, sou um assistente especializado em marketing e criação de conteúdo. Não posso ajudar com perguntas fora desse contexto. Por favor, faça perguntas relacionadas a marketing, estratégias de comunicação ou criação de conteúdo.",
            "source_documents": []
        }

    def validate_query(self, query: str) -> bool:
        response = self.llm.invoke(
            self.validation_prompt.format(query=query)
        )
        return response.strip().lower() == "true"

    def check_query(self, query: str) -> dict:
        if not self.validate_query(query):
            self.default_message["query"] = query
            return self.default_message
        return {"validated": True}