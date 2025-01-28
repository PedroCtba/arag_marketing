class RetrievalBasedGuardrail:
    def __init__(self, retriever, min_relevant_docs=1, no_docs_message=None, similarity_threshold=None):
        """
        Initialize the guardrail with a retriever, minimum relevant documents, and a custom message.

        Args:
            retriever: The retriever object (e.g., PineconeVectorStore retriever).
            min_relevant_docs (int): Minimum number of relevant documents required to proceed.
            no_docs_message (str): Custom message to return when no relevant documents are found.
            similarity_threshold (float): Optional similarity threshold for filtering documents.
        """
        self.retriever = retriever
        self.min_relevant_docs = min_relevant_docs
        self.no_docs_message = no_docs_message or (
            "Não encontrei materiais relevantes para essa solicitação. "
            "Por favor, reformule essa solicitação oferecendo mais contexto, tema, etc. "
            "Ou faça uma solicitação diferente."
        )
        self.similarity_threshold = similarity_threshold

    def check_relevance(self, query, chat_history=None):
        """
        Check if the query retrieves enough relevant documents.

        Args:
            query (str): The user's query.
            chat_history (list): The previous messages in the conversation.

        Returns:
            dict: A dictionary with two keys:
                - "relevant": True if enough relevant documents are found, False otherwise.
                - "documents": List of relevant documents (if any).
                - "message": The no-docs message (if no relevant documents are found).
        """
        # Combine chat history into a contextualized query if available
        if chat_history:
            contextual_query = "\n".join([msg['user'] for msg in chat_history[-3:]]) + "\n" + query
        else:
            contextual_query = query

        # Retrieve documents with similarity scores
        relevant_docs = self.retriever.similarity_search_with_score(contextual_query, k=5)

        # Print document scores for tuning
        print("\n--- Retrieved Document Scores ---")
        for doc, score in relevant_docs:
            print(f"Score: {score:.4f} | Content: {doc.page_content[:50]}...")  # Truncate content for readability
            
        # Retrieve documents with optional similarity threshold
        if self.similarity_threshold:
            relevant_docs = self.retriever.similarity_search_with_score(
                contextual_query, k=self.min_relevant_docs, filter={"score": {"$gte": self.similarity_threshold}}
            )
        else:
            relevant_docs = self.retriever.similarity_search(contextual_query, k=self.min_relevant_docs)
        
        # Allow follow-up queries that rely on previous conversation even if no relevant docs are found
        if len(relevant_docs) >= self.min_relevant_docs or (chat_history and len(chat_history) > 0):
            return {
                "relevant": True,
                "documents": relevant_docs,
                "message": None
            }
        else:
            return {
                "relevant": False,
                "documents": [],
                "message": self.no_docs_message
            }
