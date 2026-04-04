from typing import Dict, List, Optional, Any
from db.mongo import get_quiz,save_quiz_result,get_quiz_result,update_course

def get_unit_quiz(course_id: str, unit_number: int) -> Optional[Dict[str, Any]]:
    return get_quiz(course_id, unit_number)

def submit_quiz(username,course_topic,course_id,unit_number,unit_index,questions,user_answers, units):
    score = 0
    per_question = []
    for i, question in enumerate(questions):
        correct_label = question["correct_label"]
        chosen_label = user_answers.get(i, "")
        is_correct = chosen_label == correct_label
        if is_correct:
            score += 1
        per_question.append({
            "question": question["question"],
            "options": question["options"],
            "chosen_label": chosen_label,
            "correct_label": correct_label,
            "explanation": question["explanation"],
            "is_correct": is_correct,
        })
    total = len(questions)
    percentage = round((score / total) * 100, 1) if total > 0 else 0.0

    save_quiz_result(username=username,course_topic=course_topic,unit_number=unit_number,score=score,total=total,answers=user_answers)

    units[unit_index]["quiz_score"] = score
    update_course(course_id, {"units": units})

    return {"score": score,"total": total,"percentage": percentage,"per_question": per_question}

def get_previous_result(username,course_topic,unit_number):
    return get_quiz_result(username, course_topic, unit_number)

def compute_progress(units):
    total_points = 0
    earned_points = 0

    for unit in units:
        subtopics = unit.get("subtopics", [])
        total_points += len(subtopics) + 1

        for sub in subtopics:
            if sub.get("status") == "completed":
                earned_points += 1

        if unit.get("quiz_done"):
            earned_points += 1

    if total_points == 0:
        return 0.0

    return round((earned_points / total_points) * 100, 1)


def all_subtopics_done(unit):
    subtopics = unit.get("subtopics", [])
    if not subtopics:
        return False
    return all(s.get("status") == "completed" for s in subtopics)
