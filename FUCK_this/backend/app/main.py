from fastapi import FastAPI
from services.llm_services import Llm_services
from services.rag_service import Rag_service
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    rag = Rag_service()
    llm = Llm_services()
    result = rag.answer_question(request.question, llm)
    return result