import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from document_loader import DocumentLoader
from vector_store import VectorStore
from llm_integrator import LLMIntegrator

load_dotenv()

app = FastAPI(title="RAG Knowledge Base API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
llm_integrator = LLMIntegrator()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: list = []

@app.post("/api/upload", tags=["documents"])
async def upload_file(file: UploadFile = File(...)):
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        supported_exts = DocumentLoader.get_supported_extensions()
        
        if file_ext not in supported_exts:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Supported types: {supported_exts}")
        
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        content = DocumentLoader.load_file(file_path)
        vector_store.add_document(file.filename, file_ext[1:], content)
        
        os.remove(file_path)
        
        return {"message": "File uploaded and processed successfully", "filename": file.filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse, tags=["query"])
async def query_knowledge_base(request: QueryRequest):
    try:
        results = vector_store.search_similar(request.query, request.top_k)
        
        if not results:
            return {"answer": "根据提供的文档，我无法回答这个问题", "sources": []}
        
        answer = llm_integrator.generate_response(request.query, results)
        
        sources = [
            {"id": r["id"], "filename": r["filename"], "similarity": round(r["similarity"], 4)}
            for r in results
        ]
        
        return {"answer": answer, "sources": sources}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", tags=["documents"])
async def list_documents():
    try:
        docs = vector_store.get_all_documents()
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{doc_id}", tags=["documents"])
async def delete_document(doc_id: int):
    try:
        success = vector_store.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host=host, port=port)