# app/main.py
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
from app.routers import auth
import logging
import uuid
from app.services.retrieval import query
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cary AI Platform",
    description="Enterprise AI infrastructure for The Cary Company",
    version="1.0.0"
)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# API key auth — production would use
# Azure AD / Microsoft 365 identity
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)

def verify_api_key(
    api_key: str = Security(api_key_header)
):
    if api_key != settings.api_secret_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

class QueryRequest(BaseModel):
    question: str
    department: str = "General"
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: list
    department: str
    session_id: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Cary AI Platform",
        "version": "1.0.0"
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(
            f"Query | dept={request.department} | "
            f"session={session_id} | "
            f"q={request.question[:50]}..."
        )
        
        result = query(
            question=request.question,
            department=request.department,
            session_id=session_id
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            department=result["department"],
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Query processing failed"
        )

@app.get("/api/v1/departments")
def get_departments():
    return {
        "departments": [
            "HR",
            "Sales",
            "Operations",
            "Finance",
            "Customer Service",
            "General"
        ]
    }