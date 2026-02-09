from pydantic import BaseModel, Field
from typing import List, Optional

class CodeReviewRequest(BaseModel):
    code: str = Field(..., description="Code to review")
    language: str = Field(..., description="Programming language")
    file_path: Optional[str] = Field(None, description="File path for context")

class Issue(BaseModel):
    type: str
    severity: str
    line: int
    description: str
    suggestion: str
    tool: Optional[str] = None

class CodeReviewResponse(BaseModel):
    issues: List[Issue]
    total_issues: int
    score: float


class DocumentationRequest(BaseModel):
    code: str
    doc_type: str = "docstring"
    style: str = "google"


class DocumentationResponse(BaseModel):
    documentation: str
    doc_type: str


class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None


class Reference(BaseModel):
    file: str
    line: int
    code: str
    relevance: float


class QuestionResponse(BaseModel):
    answer: str
    references: List[Reference]


class IndexRequest(BaseModel):
    project_path: str
    file_extensions: List[str] = [".py", ".js", ".ts"]


class IndexResponse(BaseModel):
    files_indexed: int
    chunks_created: int
    status: str


class HealthResponse(BaseModel):
    status: str
    version: str
    ollama_available: bool    