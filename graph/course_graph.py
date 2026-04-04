from typing import Any, Dict
from graph.nodes.generate_units import generate_units_node
from graph.nodes.generate_subtopics import generate_subtopics_node
from graph.nodes.generate_content import generate_content_node
from graph.nodes.generate_quiz import generate_quiz_node

def run_generate_units(state):
    return generate_units_node(state)

def run_generate_subtopics(state):
    return generate_subtopics_node(state)

def run_generate_content(state,unit_index,subtopic_index):
    state["current_unit_index"] = unit_index
    state["current_subtopic_index"] = subtopic_index
    return generate_content_node(state)

def run_generate_quiz(state,unit_index):
    state["current_unit_index"] = unit_index
    return generate_quiz_node(state)

def build_state(
    username: str,
    course_id: str,
    topic: str,
    units: list = None,
    step: str = "pending",
    current_unit_index: int = 0,
    current_subtopic_index: int = 0,
) -> Dict[str, Any]:
    return {
        "username": username,
        "course_id": course_id,
        "topic": topic,
        "units": units or [],
        "step": step,
        "current_unit_index": current_unit_index,
        "current_subtopic_index": current_subtopic_index,
        "error": None,
    }
