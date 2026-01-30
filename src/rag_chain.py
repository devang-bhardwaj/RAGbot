"""
RAG Chain Module
Integrates Groq LLM with retrieval for Q&A
Supports streaming responses
"""
from langchain_groq import ChatGroq
import streamlit as st
from langchain_core.prompts import PromptTemplate
from typing import List, Optional, Generator
import time

from src.config import GROQ_API_KEY, GROQ_MODEL
from src.vector_store import get_vector_store


# Query Rewrite Template
REWRITE_QUERY_TEMPLATE = """Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just rewrite it if needed and otherwise return it as is.

Chat History:
{chat_history}

Latest Question: {question}

Standalone Question:"""

# RAG Prompt Template - Enhanced for better responses and history
RAG_PROMPT_TEMPLATE = """You are RAGbot, an intelligent AI assistant that answers questions based on uploaded documents.

CHAT HISTORY:
{chat_history}

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based ONLY on the context provided above
2. If the context doesn't contain relevant information, say "I don't have enough information in the uploaded documents to answer this question."
3. Be concise yet comprehensive in your response
4. Always respond in English, regardless of the document language
5. Format your response with proper paragraphs for readability
6. Do not fabricate or assume information not present in the context
7. If multiple documents provide relevant information, synthesize them coherently
8. Use the Chat History to provide better context for your answer if needed

YOUR ANSWER:"""


from flashrank import Ranker, RerankRequest

# ... imports ...

class RAGChain:
    """RAG Chain combining retrieval with Groq LLM"""
    
    def __init__(self):
        """Initialize RAG chain with Groq LLM"""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found. Please set it in your .env file")
        
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.3,
            max_tokens=2048,
            streaming=True
        )
        
        # Initialize Re-ranker (Model is small ~40MB, downloads on first run)
        try:
            self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="./.cache")
        except Exception as e:
            print(f"Warning: FlashRank initialization failed: {e}")
            self.ranker = None
        
        self.prompt = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template=RAG_PROMPT_TEMPLATE
        )
        
        self.rewrite_prompt = PromptTemplate(
            input_variables=["chat_history", "question"],
            template=REWRITE_QUERY_TEMPLATE
        )
        
        self.vector_store = get_vector_store()
    
    def _rerank_documents(self, query: str, documents: List[dict], top_k: int = 5) -> List[dict]:
        """Re-rank documents using FlashRank"""
        if not self.ranker or not documents:
            return documents[:top_k]
        
        # Format for FlashRank
        passages = [
            {"id": str(i), "text": doc["content"], "meta": doc["metadata"]} 
            for i, doc in enumerate(documents)
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        
        # Sort and return top_k
        reranked_docs = []
        for res in results[:top_k]:
            # Map back to our format
            reranked_docs.append({
                "content": res["text"],
                "metadata": res["meta"],
                "score": res["score"]
            })
            
        return reranked_docs

    def _format_context(self, documents: List[dict]) -> str:
        """Format retrieved documents into context string"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc["metadata"].get("source", "Unknown")
            content = doc["content"]
            context_parts.append(f"[Document {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)

    def _format_history(self, messages: List[dict]) -> str:
        # ... (same as before) ...
        """Format chat history into string"""
        if not messages:
            return "No previous conversation."
        
        formatted = []
        for msg in messages[-5:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)

    def rewrite_query(self, question: str, history: List[dict]) -> str:
        # ... (same as before) ...
        """Rewrite question to be standalone based on history"""
        if not history:
            return question
            
        formatted_history = self._format_history(history)
        
        prompt = self.rewrite_prompt.format(
            chat_history=formatted_history,
            question=question
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception:
            return question

    def get_response_stream(self, question: str, user_id: str, history: List[dict] = None) -> Generator:
        """
        Get streaming RAG response with re-ranking
        """
        history = history or []
        
        # Rewrite query
        search_query = question
        if history:
            search_query = self.rewrite_query(question, history)
        
        # 1. Retrieval (Fetch more docs for re-ranking, e.g., 20)
        initial_documents = self.vector_store.search(
            query=search_query,
            user_id=user_id,
            n_results=15 
        )
        
        # 2. Re-ranking (Filter down to top 5 most relevant)
        if initial_documents:
            documents = self._rerank_documents(search_query, initial_documents, top_k=5)
        else:
            documents = []
        
        # Check if user has any documents
        if not documents and not initial_documents: # Only return empty if truly no docs found
             yield {
                "type": "complete",
                "response": "You haven't uploaded any documents yet. Please upload a document first, then ask questions about it.",
                "sources": [],
                "has_documents": False
            }
             return

        # Format context and history
        context = self._format_context(documents)
        chat_history_str = self._format_history(history)
        
        # Create prompt
        formatted_prompt = self.prompt.format(
            context=context,
            question=question, 
            chat_history=chat_history_str
        )
        
        # Extract unique sources
        sources = list(set(doc["metadata"].get("source", "Unknown") for doc in documents))
        
        # Stream LLM response
        full_response = ""
        try:
            for chunk in self.llm.stream(formatted_prompt):
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    yield {
                        "type": "chunk",
                        "content": chunk.content
                    }
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }
            return
        
        # Final response with metadata
        yield {
            "type": "complete",
            "response": full_response,
            "sources": sources,
            "has_documents": True,
            "rewritten_query": search_query if search_query != question else None
        }


# Singleton instance
_rag_chain: Optional[RAGChain] = None


@st.cache_resource
def get_rag_chain() -> RAGChain:
    """Get or create RAG chain instance"""
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain
