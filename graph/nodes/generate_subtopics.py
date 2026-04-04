import json
from pathlib import Path
from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.llm import llm_outline
from db.mongo import update_course

_PROMPT_TEXT = (Path(__file__).parents[2] / "prompts" / "subtopics_prompt.txt").read_text()
_prompt = PromptTemplate.from_template(_PROMPT_TEXT)
_chain = _prompt | llm_outline | StrOutputParser()

def _parse_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        return json.loads(raw[start:end])

def generate_subtopics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state["topic"]
    course_id = state["course_id"]
    units = state["units"]

    for unit in units:
        raw = _chain.invoke({
            "topic": topic,
            "unit_number": unit["unit_number"],
            "unit_title": unit["title"],
            "unit_description": unit["description"],
        })

        subtopics_data = _parse_json(raw)

        unit["subtopics"] = [
            {
                "title": s["title"],
                "status": "locked",
                "lesson_id": None,
                "video_url": None,
                "video_title": None,
            }
            for s in subtopics_data
        ]
        
    update_course(course_id, {"units": units, "step": "subtopics_generated"})

    return {
        **state,
        "units": units,
        "step": "subtopics_generated",
    }
