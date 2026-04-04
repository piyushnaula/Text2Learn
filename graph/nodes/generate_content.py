from typing import Any, Dict
from agents.content_agent import run_content_agent
from agents.tools.youtube_tool import find_youtube_video
from rag.retriever import find_cached_lesson
from rag.embedder import save_to_chroma
from db.mongo import save_lesson, update_course


def generate_content_node(state) :
    topic = state["topic"]
    course_id = state["course_id"]
    units = state["units"]
    u_idx = state["current_unit_index"]
    s_idx = state["current_subtopic_index"]
    unit = units[u_idx]
    subtopic = unit["subtopics"][s_idx]
    subtopic_title = subtopic["title"]
    unit_title = unit["title"]
    subtopic["status"] = "in_progress"
    update_course(course_id, {"units": units})
    cached_lesson, score = find_cached_lesson(subtopic_title)

    if cached_lesson is not None:
        lesson_id = cached_lesson["_id"]
        video_url = cached_lesson.get("video_url")
        video_title = cached_lesson.get("video_title")
    else:
        content, summary = run_content_agent(subtopic_title, unit_title, topic)
        video_url, video_title, video_score = find_youtube_video(subtopic_title, topic)
        lesson_id = save_lesson(
            subtopic=subtopic_title,
            topic_tag=topic,
            content=content,
            summary=summary,
            video_url=video_url,
            video_title=video_title,
        )
        save_to_chroma(
            lesson_id=lesson_id,
            subtopic=subtopic_title,
            content=content,
            topic_tag=topic,
        )
    subtopic["lesson_id"] = lesson_id
    subtopic["video_url"] = video_url if cached_lesson is None else cached_lesson.get("video_url")
    subtopic["video_title"] = video_title if cached_lesson is None else cached_lesson.get("video_title")
    subtopic["status"] = "completed"

    update_course(course_id, {"units": units, "step": "in_progress"})
    return {
        **state,
        "units": units,
        "step": "in_progress",
    }
