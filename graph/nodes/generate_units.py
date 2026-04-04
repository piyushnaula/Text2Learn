import json
from pathlib import Path
from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.llm import llm_outline
from db.mongo import update_course

_PROMPT_TEXT = (Path(__file__).parents[2] / "prompts" / "units_prompt.txt").read_text()
_prompt = PromptTemplate.from_template(_PROMPT_TEXT)
_chain = _prompt | llm_outline | StrOutputParser()


def generate_units_node(state):
    topic = state["topic"]
    course_id = state["course_id"]

    raw = _chain.invoke({"topic": topic})
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    try:
        units_data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        units_data = json.loads(raw[start:end])

    units = []
    for u in units_data:
        units.append({
            "unit_number": u["unit_number"],
            "title": u["title"],
            "description": u["description"],
            "subtopics": [],
            "quiz_done": False,
            "quiz_score": None,
        })

    update_course(course_id, {"units": units, "step": "units_generated"})

    return {
        **state,
        "units": units,
        "step": "units_generated",
    }
