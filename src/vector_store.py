"""
Vector Store Module
Pinecone integration for scalable document embeddings
"""
import os
import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import hashlib
import time

from src.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL, CHROMA_PERSIST_DIR


class VectorStore:
    """Pinecone-based vector store for document embeddings"""
    
    def __init__(self):
        """Initialize Pinecone client and embedding model"""
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.use_pinecone = False
        
        if PINECONE_API_KEY and PINECONE_INDEX_NAME:
            try:
                self.pc = Pinecone(api_key=PINECONE_API_KEY)
                self.index_name = PINECONE_INDEX_NAME
                self.index = self.pc.Index(self.index_name)
                self.use_pinecone = True
                print("✅ Connected to Pinecone")
            except Exception as e:
                print(f"⚠️ Pinecone connection failed: {e}. Falling back to ChromaDB.")
        else:
            print("⚠️ Pinecone keys missing. Using ChromaDB fallback.")

        # Fallback to ChromaDB if Pinecone is not available
        if not self.use_pinecone:
            import chromadb
            from chromadb.config import Settings
            self.client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False)
            )

    def _get_collection_name(self, user_id: str) -> str:
        """Generate collection name for user (ChromaDB specific)"""
        hash_id = hashlib.md5(user_id.encode()).hexdigest()[:16]
        return f"user_{hash_id}"
    
    def add_documents(self, chunks: List[dict], user_id: str) -> int:
        """Add document chunks to vector store"""
        # Generate embeddings
        documents = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(documents).tolist()
        
        if self.use_pinecone:
            vectors = []
            for i, chunk in enumerate(chunks):
                vector_id = f"{user_id}_{chunk['metadata']['source']}_{chunk['metadata']['chunk_id']}"
                # Add user_id to metadata for filtering
                metadata = chunk["metadata"].copy()
                metadata["user_id"] = user_id
                metadata["content"] = chunk["content"]
                
                vectors.append({
                    "id": vector_id,
                    "values": embeddings[i],
                    "metadata": metadata
                })
            
            # Upsert to Pinecone in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                self.index.upsert(vectors=vectors[i:i+batch_size])
                
        else:
            # ChromaDB Fallback implementation
            collection = self.client.get_or_create_collection(self._get_collection_name(user_id))
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [f"{user_id}_{chunk['metadata']['source']}_{chunk['metadata']['chunk_id']}" for chunk in chunks]
            collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
            
        return len(chunks)
    
    def search(self, query: str, user_id: str, n_results: int = 20) -> List[dict]:
        """Search for relevant documents (retrieves more results for re-ranking)"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        if self.use_pinecone:
            try:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=n_results,
                    filter={"user_id": user_id},
                    include_metadata=True
                )
                
                documents = []
                for match in results.matches:
                    metadata = match.metadata
                    documents.append({
                        "content": metadata.get("content", ""),
                        "metadata": {k:v for k,v in metadata.items() if k != "content" and k != "user_id"},
                        "score": match.score
                    })
                return documents
            except Exception as e:
                print(f"Pinecone search error: {e}")
                return []
        
        else:
            # ChromaDB Fallback
            collection = self.client.get_or_create_collection(self._get_collection_name(user_id))
            if collection.count() == 0:
                return []
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, collection.count())
            )
            
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": 1.0 # Chroma doesn't give score in same range, simplifying
                    })
            return documents

    def get_document_list(self, user_id: str) -> List[str]:
        """Get unique document sources"""
        if self.use_pinecone:
            # Pinecone doesn't support getting unique metadata values efficiently
            # We'll use a dummy query to fetch recent docs and extract sources
            # For production, you'd store this metadata in a separate DB (like Supabase)
            # For now, we'll try to fetch a good number of vectors
            try:
                results = self.index.query(
                    vector=[0.0] * 384, # Dummy vector
                    top_k=1000,
                    filter={"user_id": user_id},
                    include_metadata=True
                )
                sources = set()
                for match in results.matches:
                    if "source" in match.metadata:
                        sources.add(match.metadata["source"])
                return list(sources)
            except:
                return []
        else:
            collection = self.client.get_or_create_collection(self._get_collection_name(user_id))
            if collection.count() == 0: return []
            data = collection.get(include=["metadatas"])
            return list(set(m["source"] for m in data["metadatas"]))

    def delete_document(self, user_id: str, document_name: str) -> bool:
        """Delete a document"""
        if self.use_pinecone:
            # Pinecone delete by filter
            try:
                self.index.delete(
                    filter={
                        "user_id": user_id,
                        "source": document_name
                    }
                )
                return True
            except:
                return False
        else:
            # ChromaDB delete
            collection = self.client.get_or_create_collection(self._get_collection_name(user_id))
            collection.delete(where={"source": document_name})
            return True

    def clear_user_data(self, user_id: str) -> bool:
        """Clear all data for user"""
        if self.use_pinecone:
            try:
                self.index.delete(filter={"user_id": user_id})
                return True
            except:
                return False
        else:
            try:
                self.client.delete_collection(self._get_collection_name(user_id))
                return True
            except:
                return False

    def get_document_count(self, user_id: str) -> int:
        """Get total chunks"""
        if self.use_pinecone:
            # Approximate count via stats (metadata filtering stats are not direct API)
            # This is hard in Pinecone without separate tracking. 
            # We will return 0 or do a simple query
            return 0 
        else:
            collection = self.client.get_or_create_collection(self._get_collection_name(user_id))
            return collection.count()


# Singleton instance
_vector_store: Optional[VectorStore] = None


@st.cache_resource
def get_vector_store() -> VectorStore:
    """Get or create vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
