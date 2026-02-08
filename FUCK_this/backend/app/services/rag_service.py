import chromadb
from chromadb.config import Settings
from typing import List, Dict
from chromadb.utils import embedding_functions
import ast

class RAGService:
    def __init__(self):
        self.db_client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.db_client.get_or_create_collection(
            name="codebase",
            embedding_function = self.embedding, 
            metadata={"hnsw:space": "cosine"}
        )
        

    def _chuncking(self,filepath:str,code:str):
        chunks = []
        try:
            tree = ast.parse(code)
        except:
            return chunks
        
        lines = code.split('\n')

        for i in ast.walk(tree):
            if isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = i.lineno-1
                end = getattr(i, "end_lineno", i.lineno) - 1
                code_text = "\n".join(lines[start:end + 1]) 

                chunks.append({
                    "id": f"{filepath}:{start}",
                    "text": code_text,
                    "metadata": {
                        "file": filepath,
                        "start_line": start,
                        "end_line": end,
                        "type": type(i).__name__,
                        "name": i.name
                    }
                })

        return chunks

    def index_file(self,filepath:str,code:str):
        chunks = self._chuncking(filepath,code)

        if not chunks:
            return

        text = [i['text'] for i in chunks]

        self.collection.add(
            documents=text,
            metadatas=[i['metadata'] for i in chunks],
            ids=[i['id'] for i in chunks]
        )

    def _search(self, query: str, top_k: int = 5):

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        chunks = []

        if not results["documents"]:
            return chunks

        for i in range(len(results["documents"][0])):
            chunks.append({
                "code": results["documents"][0][i],
                "file": results["metadatas"][0][i]["file"],
                "line": results["metadatas"][0][i]["start_line"],
                "relevance": 1 - results["distances"][0][i]
            })

        return chunks
        
    def answer_question(self, question: str, llm_service):
        relevant_chunks = self._search(question, top_k=3)
        if not relevant_chunks:
            return {
                "answer": "I couldn't find relevant code for that question.",
                "references": []
            }
        
        context = ""
        
        for i, chunk in enumerate(relevant_chunks):
            context += f"\n[{i+1}] File: {chunk['file']} (line {chunk['line']})\n"
            context += chunk['code']
            context += "\n---\n"

if __name__ == '__main__':
    obj = RAGService()