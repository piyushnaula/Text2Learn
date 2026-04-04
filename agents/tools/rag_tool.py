from langchain.tools import tool
from rag.retriever import find_cached_lesson


@tool
def rag_retrieval(subtopic: str) -> str:
    lesson, score = find_cached_lesson(subtopic)
    if lesson is not None:
        return (
            f"CACHE HIT (similarity={score:.2f})\n\n"
            f"Subtopic: {lesson['subtopic']}\n\n"
            f"{lesson['content']}"
        )
    else:
        return f"NO CACHE FOUND for '{subtopic}' (best similarity={score:.2f}). Please search the web."
