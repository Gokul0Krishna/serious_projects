import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tree_sitter_languages import get_language, get_parser 
from tree_sitter import Language, Parser

class RAGService:
    def __init__(self):
        self.db_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.db_client.get_or_create_collection(
            name="codebase",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.parser = get_parser('python')


if __name__ == '__main__':
    obj = RAGService()