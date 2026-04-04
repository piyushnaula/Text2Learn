import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
COLLECTION_NAME = "lessons"

_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _get_collection():
    global _chroma_client, _collection
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
    if _collection is None:
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}, 
        )
    return _collection

def embed_text(text: str) -> List[float]:
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def save_to_chroma(lesson_id,subtopic,content,topic_tag):
    collection = _get_collection()
    embedding = embed_text(subtopic)

    collection.upsert(
        ids=[lesson_id],
        embeddings=[embedding],
        documents=[subtopic],     
        metadatas=[{
            "lesson_id": lesson_id,
            "subtopic": subtopic,
            "topic_tag": topic_tag,
            "content_preview": content[:300]
        }],
    )
