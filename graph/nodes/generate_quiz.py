import json
from typing import Any, Dict

from services.llm import llm_quiz
from db.mongo import get_lesson, save_quiz, update_course
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path

_PROMPT_TEXT = (Path(__file__).parents[2] / "prompts" / "quiz_prompt.txt").read_text()
_prompt = PromptTemplate.from_template(_PROMPT_TEXT)
_chain = _prompt | llm_quiz | StrOutputParser()


def _parse_quiz_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])


def generate_quiz_node(state):
    topic = state["topic"]
    course_id = state["course_id"]
    units = state["units"]
    u_idx = state["current_unit_index"]
    unit = units[u_idx]

    summaries = []
    for subtopic in unit["subtopics"]:
        lesson_id = subtopic.get("lesson_id")
        if lesson_id:
            lesson = get_lesson(lesson_id)
            if lesson:
                summaries.append(
                    f"Subtopic: {subtopic['title']}\nSummary: {lesson.get('summary', '')}"
                )

    if not summaries:
        return {**state, "step": "in_progress"}

    summaries_text = "\n\n".join(summaries)
    num_questions = min(10, max(5, len(summaries))) 

    raw = _chain.invoke({
        "topic": topic,
        "unit_number": unit["unit_number"],
        "unit_title": unit["title"],
        "summaries": summaries_text,
        "num_questions": num_questions,
    })

    quiz_data = _parse_quiz_json(raw)

    save_quiz(course_id, unit["unit_number"], quiz_data)
    unit["quiz_done"] = True
    update_course(course_id, {"units": units})

    return {
        **state,
        "units": units,
        "step": "in_progress",
    }
