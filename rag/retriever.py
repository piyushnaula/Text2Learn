import os
from typing import Optional, Tuple
from dotenv import load_dotenv
from rag.embedder import embed_text, _get_collection
from db.mongo import get_lesson
load_dotenv()

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))


def find_cached_lesson(subtopic):
    collection = _get_collection()
    if collection.count() == 0:
        return None, 0.0

    query_embedding = embed_text(subtopic)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        include=["distances", "metadatas"],
    )

    if not results["ids"] or not results["ids"][0]:
        return None, 0.0

    distance = results["distances"][0][0]
    similarity = 1.0 - distance 

    if similarity >= SIMILARITY_THRESHOLD:
        metadata = results["metadatas"][0][0]
        lesson_id = metadata.get("lesson_id")
        if lesson_id:
            lesson_doc = get_lesson(lesson_id)
            return lesson_doc, similarity

    return None, similarity
