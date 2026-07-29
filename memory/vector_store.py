import os
import shutil
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from config.settings import settings
from config.logging_config import system_logger

# Fallback Fake Embeddings class for offline/testing development
class LocalFakeEmbeddings(Embeddings):
    def __init__(self, size: int = 1536):
        self.size = size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Deterministic dummy vector generation based on character sum
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.size
        char_sum = sum(ord(c) for c in text)
        for i in range(self.size):
            vector[i] = ((char_sum + i) % 100) / 100.0
        return vector

class VectorMemoryManager:
    def __init__(self):
        self.index_base_dir = "logs/vector_stores"
        os.makedirs(self.index_base_dir, exist_ok=True)
        
        # Configure embedding provider based on environment validation
        if not settings.OPENAI_API_KEY or "mock" in settings.OPENAI_API_KEY or "your_openai" in settings.OPENAI_API_KEY:
            system_logger.info("Using LocalFakeEmbeddings for testing/offline run.")
            self.embeddings = LocalFakeEmbeddings()
        else:
            system_logger.info("Initializing OpenAIEmbeddings.")
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    def _get_index_path(self, patient_id: int) -> str:
        return os.path.join(self.index_base_dir, f"patient_{patient_id}")

    def store_document(self, patient_id: int, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Indexes a clinical text block in the patient's vector store index."""
        if not text.strip():
            return

        index_path = self._get_index_path(patient_id)
        meta = metadata or {}
        meta["patient_id"] = patient_id
        
        try:
            if os.path.exists(index_path):
                # Load existing and append
                db = FAISS.load_local(index_path, self.embeddings, allow_dangerous_deserialization=True)
                db.add_texts([text], metadatas=[meta])
                db.save_local(index_path)
            else:
                # Create new index
                db = FAISS.from_texts([text], self.embeddings, metadatas=[meta])
                db.save_local(index_path)
            system_logger.info(f"Vector memory stored for patient {patient_id}.")
        except Exception as e:
            system_logger.error(f"Failed to save to vector store: {e}")

    def search_documents(self, patient_id: int, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Retrieve most semantically relevant documents for the given query."""
        index_path = self._get_index_path(patient_id)
        if not os.path.exists(index_path):
            return []

        try:
            db = FAISS.load_local(index_path, self.embeddings, allow_dangerous_deserialization=True)
            docs = db.similarity_search(query, k=limit)
            return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]
        except Exception as e:
            system_logger.error(f"Failed to search vector store: {e}")
            return []

    def clear(self, patient_id: int) -> None:
        """Deletes the patient vector store directories."""
        index_path = self._get_index_path(patient_id)
        if os.path.exists(index_path):
            try:
                shutil.rmtree(index_path)
                system_logger.info(f"Cleared vector memory directory for patient {patient_id}.")
            except Exception as e:
                system_logger.error(f"Failed to delete index directory: {e}")
