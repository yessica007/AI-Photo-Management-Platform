from fastapi import FastAPI
from pydantic import BaseModel

from app.upload import router as upload_router
from app.embeddings import text_embedding
from app.search import search

app = FastAPI(
    title="AI Photo Management Platform",
    description="PanScience Technical Assignment",
    version="1.0"
)

# Include upload routes
app.include_router(upload_router)


@app.get("/")
def home():
    return {
        "message": "AI Photo Management API is running!"
    }


class SearchRequest(BaseModel):
    query: str


@app.post("/search")
def semantic_search(request: SearchRequest):

    embedding = text_embedding(request.query)

    results = search(embedding)

    return {
        "query": request.query,
        "results": results
    }