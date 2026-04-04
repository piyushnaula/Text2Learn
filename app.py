import json
from typing import Any, Dict, List, Optional
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Text2Learn",
    layout="wide",
    initial_sidebar_state="expanded",
)

from db.mongo import get_or_create_user,create_course,get_course,get_user_courses,get_lesson
from graph.course_graph import build_state,run_generate_units,run_generate_subtopics,run_generate_content,run_generate_quiz
from services.quiz_service import get_unit_quiz,submit_quiz,get_previous_result,compute_progress,all_subtopics_done

st.markdown("""
<style>
/* Main background */
.main { background-color: #0f1117; }

/* Status badges */
.badge-locked    { color: #6b7280; font-size: 0.85rem; }
.badge-progress  { color: #f59e0b; font-size: 0.85rem; }
.badge-done      { color: #10b981; font-size: 0.85rem; }

/* Unit card */
.unit-card {
    background: #1e2130;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #3b82f6;
}

/* Subtopic row */
.subtopic-row {
    padding: 0.4rem 0.2rem;
    border-bottom: 1px solid #2d3148;
}

/* Quiz result */
.correct-answer   { background: #064e3b; border-radius: 6px; padding: 0.4rem 0.8rem; margin: 0.2rem 0; }
.incorrect-answer { background: #7f1d1d; border-radius: 6px; padding: 0.4rem 0.8rem; margin: 0.2rem 0; }
</style>
""", unsafe_allow_html=True)

def ss() -> dict:
    return st.session_state


def init_session():
    defaults = {
        "logged_in": False,
        "username": "",
        "course_id": None,
        "course_state": None,  
        "view": "home",         
        "active_unit_idx": None,
        "active_subtopic_idx": None,
        "active_quiz_unit_idx": None,
        "quiz_answers": {},      
        "quiz_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

def status_icon(status: str) -> str:
    return {"locked": "🔒", "in_progress": "⏳", "completed": "✅"}.get(status, "🔒")

def reload_course():
    course = get_course(ss()["course_id"])
    if course:
        state = ss()["course_state"]
        state["units"] = course["units"]
        state["step"] = course["step"]
        ss()["course_state"] = state

def render_sidebar():
    with st.sidebar:
        st.markdown("## Text2Learn")

        if not ss()["logged_in"]:
            st.info("Log in to start learning.")
            return

        st.markdown(f"**{ss()['username']}**")
        st.divider()

        if ss()["course_state"] and ss()["course_state"].get("units"):
            units = ss()["course_state"]["units"]
            progress = compute_progress(units)
            st.markdown("**Course Progress**")
            st.progress(progress / 100)
            st.caption(f"{progress}% complete")
            st.divider()

        st.markdown("**My Courses**")
        courses = get_user_courses(ss()["username"])
        if not courses:
            st.caption("No courses yet.")
        else:
            for c in courses:
                label = f"{c['topic']}"
                step_label = {
                    "pending": "Not started",
                    "units_generated": "Units ready",
                    "subtopics_generated": "Ready to learn",
                    "in_progress": "In progress",
                    "done": "Completed",
                }.get(c.get("step", "pending"), "")
                if st.button(f"{label}", key=f"course_btn_{c['_id']}"):
                    ss()["course_id"] = c["_id"]
                    ss()["course_state"] = build_state(
                        username=ss()["username"],
                        course_id=c["_id"],
                        topic=c["topic"],
                        units=c.get("units", []),
                        step=c.get("step", "pending"),
                    )
                    ss()["view"] = "course"
                    st.rerun()
                st.caption(f"  {step_label}")

        st.divider()
        if st.button("New Course"):
            ss()["course_id"] = None
            ss()["course_state"] = None
            ss()["view"] = "home"
            st.rerun()

        if st.button("Logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("#Text2Learn")
        st.markdown("### AI-Powered Course Generation Platform")
        st.markdown("---")
        st.markdown("#### Get started")
        username = st.text_input("Enter your username", placeholder="e.g. your_name")
        if st.button("Login / Sign Up", type="primary", use_container_width=True):
            if username.strip():
                get_or_create_user(username.strip())
                ss()["username"] = username.strip()
                ss()["logged_in"] = True
                ss()["view"] = "home"
                st.rerun()
            else:
                st.error("Please enter a username.")

def render_home():
    st.markdown("## Start a New Course")
    st.markdown("Type any topic and Text2Learn will build a full course for you — step by step.")
    st.markdown("---")

    topic = st.text_input(
        "What do you want to learn?",
        placeholder="e.g. Machine Learning, Digital Marketing, Python for Beginners...",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        generate_clicked = st.button("Generate Course", type="primary")

    if generate_clicked:
        if not topic.strip():
            st.error("Please enter a topic.")
            return

        with st.spinner("Creating your course outline..."):
            course_id = create_course(ss()["username"], topic.strip())

            state = build_state(
                username=ss()["username"],
                course_id=course_id,
                topic=topic.strip(),
            )

            state = run_generate_units(state)

        ss()["course_id"] = course_id
        ss()["course_state"] = state
        ss()["view"] = "course"
        st.rerun()

def render_course():
    state = ss()["course_state"]
    if not state:
        ss()["view"] = "home"
        st.rerun()
        return

    topic = state["topic"]
    step = state["step"]
    units = state.get("units", [])

    st.markdown(f"## {topic}")
    st.markdown("---")

    if step == "units_generated":
        st.markdown("### Course Outline Ready")
        st.markdown("Here are the 5 units for your course. Review them and confirm to continue.")
        st.markdown("")

        for unit in units:
            with st.container():
                st.markdown(
                    f"<div class='unit-card'>"
                    f"<strong>Unit {unit['unit_number']}: {unit['title']}</strong><br>"
                    f"<span style='color:#9ca3af'>{unit['description']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Confirm & Generate Subtopics", type="primary"):
                with st.spinner("Generating subtopics for all units..."):
                    new_state = run_generate_subtopics(state)
                ss()["course_state"] = new_state
                st.rerun()
        with col2:
            if st.button("Regenerate Outline"):
                with st.spinner("Regenerating..."):
                    new_state = run_generate_units(state)
                ss()["course_state"] = new_state
                st.rerun()

    elif step == "subtopics_generated":
        st.markdown("### Subtopics Ready")
        st.markdown("Review the full course structure below, then confirm to start learning.")
        st.markdown("")

        for unit in units:
            with st.expander(f"Unit {unit['unit_number']}: {unit['title']}", expanded=False):
                st.markdown(f"*{unit['description']}*")
                st.markdown("**Subtopics:**")
                for sub in unit.get("subtopics", []):
                    st.markdown(f"- {sub['title']}")

        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Start Learning!", type="primary"):
                from db.mongo import update_course
                update_course(ss()["course_id"], {"step": "in_progress"})
                state["step"] = "in_progress"
                ss()["course_state"] = state
                st.rerun()

    elif step in ("in_progress", "done"):
        _render_learning_view(state, units, topic)

    else:
        st.info("Course is being prepared...")


def _render_learning_view(state: dict, units: list, topic: str):
    progress = compute_progress(units)
    st.markdown(f"**Overall Progress: {progress}%**")
    st.progress(progress / 100)
    st.markdown("---")

    for u_idx, unit in enumerate(units):
        subtopics = unit.get("subtopics", [])
        completed_count = sum(1 for s in subtopics if s.get("status") == "completed")
        unit_label = f"Unit {unit['unit_number']}: {unit['title']}  ({completed_count}/{len(subtopics)} done)"

        with st.expander(unit_label, expanded=(u_idx == 0)):
            st.markdown(f"*{unit['description']}*")
            st.markdown("")

            for s_idx, sub in enumerate(subtopics):
                icon = status_icon(sub.get("status", "locked"))
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"{icon} {sub['title']}")
                with col2:
                    btn_label = "Open" if sub.get("status") == "completed" else "Learn"
                    if st.button(btn_label, key=f"sub_{u_idx}_{s_idx}"):
                        if sub.get("status") != "completed":
                            with st.spinner(f"Generating lesson: {sub['title']}..."):
                                new_state = run_generate_content(state, u_idx, s_idx)
                            ss()["course_state"] = new_state
                            reload_course()

                        ss()["active_unit_idx"] = u_idx
                        ss()["active_subtopic_idx"] = s_idx
                        ss()["view"] = "subtopic"
                        st.rerun()

            st.markdown("---")
            quiz_done = unit.get("quiz_done", False)
            all_done = all_subtopics_done(unit)

            if all_done and not quiz_done:
                st.markdown("#### Unit Complete!")
                st.markdown("All subtopics are done. Ready to test your knowledge?")
                if st.button(f"Generate Unit Quiz", key=f"gen_quiz_{u_idx}"):
                    with st.spinner("Generating quiz..."):
                        new_state = run_generate_quiz(state, u_idx)
                    ss()["course_state"] = new_state
                    reload_course()
                    ss()["active_quiz_unit_idx"] = u_idx
                    ss()["view"] = "quiz"
                    st.rerun()

            elif quiz_done:
                quiz_score = unit.get("quiz_score")
                score_text = f"Score: {quiz_score}" if quiz_score is not None else ""
                st.success(f"Quiz completed! {score_text}")
                if st.button(f"Review Quiz", key=f"review_quiz_{u_idx}"):
                    ss()["active_quiz_unit_idx"] = u_idx
                    ss()["view"] = "quiz"
                    st.rerun()

def render_subtopic():
    state = ss()["course_state"]
    u_idx = ss()["active_unit_idx"]
    s_idx = ss()["active_subtopic_idx"]

    if state is None or u_idx is None or s_idx is None:
        ss()["view"] = "course"
        st.rerun()
        return

    reload_course()
    state = ss()["course_state"]
    units = state["units"]
    unit = units[u_idx]
    sub = unit["subtopics"][s_idx]
    topic = state["topic"]

    if st.button("Back to Course"):
        ss()["view"] = "course"
        st.rerun()

    st.markdown(f"## {sub['title']}")
    st.markdown(f"*Unit {unit['unit_number']}: {unit['title']} — {topic}*")
    st.markdown("---")

    lesson_id = sub.get("lesson_id")
    lesson = get_lesson(lesson_id) if lesson_id else None

    if lesson is None:
        st.warning("Lesson content not generated yet.")
        if st.button("Generate Lesson Now"):
            with st.spinner("Generating lesson..."):
                new_state = run_generate_content(state, u_idx, s_idx)
            ss()["course_state"] = new_state
            reload_course()
            st.rerun()
        return

    tab_content, tab_video, tab_nav = st.tabs(["Lesson", "Video Tutorial", "Navigate"])

    with tab_content:
        st.markdown(lesson["content"])

    with tab_video:
        video_url = lesson.get("video_url") or sub.get("video_url")
        video_title = lesson.get("video_title") or sub.get("video_title")

        if video_url:
            st.markdown(f"#### 🎥 {video_title or 'Tutorial Video'}")
            st.video(video_url)
            st.caption(f"[Open on YouTube]({video_url})")
        else:
            st.info("No highly relevant tutorial video was found for this subtopic.")
            st.caption(
                "Text2Learn only shows videos with a relevance score above the threshold "
                "to make sure you get quality content."
            )

    with tab_nav:
        st.markdown("#### Navigate Subtopics")
        subtopics = unit["subtopics"]
        for i, s in enumerate(subtopics):
            icon = status_icon(s.get("status", "locked"))
            is_current = i == s_idx
            label = f"**{icon} {s['title']}**" if is_current else f"{icon} {s['title']}"
            if st.button(label, key=f"nav_sub_{i}", disabled=is_current):
                if s.get("status") != "completed":
                    with st.spinner(f"Generating lesson..."):
                        new_state = run_generate_content(state, u_idx, i)
                    ss()["course_state"] = new_state
                ss()["active_subtopic_idx"] = i
                st.rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if s_idx > 0:
                if st.button("⬅️ Previous Subtopic"):
                    ss()["active_subtopic_idx"] = s_idx - 1
                    st.rerun()
        with col2:
            if s_idx < len(subtopics) - 1:
                if st.button("Next Subtopic ➡️"):
                    next_sub = subtopics[s_idx + 1]
                    if next_sub.get("status") != "completed":
                        with st.spinner("Generating next lesson..."):
                            new_state = run_generate_content(state, u_idx, s_idx + 1)
                        ss()["course_state"] = new_state
                    ss()["active_subtopic_idx"] = s_idx + 1
                    st.rerun()
            else:
                if all_subtopics_done(unit) and not unit.get("quiz_done"):
                    if st.button("Take Unit Quiz"):
                        with st.spinner("Generating quiz..."):
                            new_state = run_generate_quiz(state, u_idx)
                        ss()["course_state"] = new_state
                        ss()["active_quiz_unit_idx"] = u_idx
                        ss()["view"] = "quiz"
                        st.rerun()

def render_quiz():
    state = ss()["course_state"]
    u_idx = ss()["active_quiz_unit_idx"]

    if state is None or u_idx is None:
        ss()["view"] = "course"
        st.rerun()
        return

    reload_course()
    state = ss()["course_state"]
    units = state["units"]
    unit = units[u_idx]
    topic = state["topic"]
    course_id = ss()["course_id"]
    username = ss()["username"]

    if st.button("← Back to Course"):
        ss()["view"] = "course"
        st.rerun()

    st.markdown(f"## Quiz — Unit {unit['unit_number']}: {unit['title']}")
    st.markdown(f"*{topic}*")
    st.markdown("---")
    quiz_doc = get_unit_quiz(course_id, unit["unit_number"])
    if not quiz_doc:
        st.error("Quiz not found. Please go back and generate the quiz.")
        return

    questions = quiz_doc.get("questions", [])
    if not questions:
        st.error("Quiz has no questions.")
        return

    prev_result = get_previous_result(username, topic, unit["unit_number"])

    if prev_result:
        _render_quiz_result_view(prev_result, questions)
        return

    st.markdown(f"**{len(questions)} questions** — Choose the best answer for each.")
    st.markdown("")

    quiz_answers = {}
    all_answered = True

    for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        options = q.get("options", [])
        option_labels = [f"{opt['label']}. {opt['text']}" for opt in options]
        option_keys = [opt["label"] for opt in options]

        chosen = st.radio(
            f"Question {i+1}",
            options=option_labels,
            key=f"quiz_q_{i}",
            label_visibility="collapsed",
        )

        if chosen:
            chosen_label = chosen.split(".")[0].strip()
            quiz_answers[i] = chosen_label
        else:
            all_answered = False

        st.markdown("")

    st.markdown("---")
    if st.button("Submit Quiz", type="primary", disabled=not all_answered):
        result = submit_quiz(
            username=username,
            course_topic=topic,
            course_id=course_id,
            unit_number=unit["unit_number"],
            unit_index=u_idx,
            questions=questions,
            user_answers=quiz_answers,
            units=units,
        )
        ss()["quiz_result"] = result
        reload_course()
        st.rerun()

    if not all_answered:
        st.caption("Answer all questions to submit.")


def _render_quiz_result_view(result: dict, questions: list):
    score = result["score"]
    total = result["total"]
    percentage = result.get("percentage", round((score / total) * 100, 1) if total else 0)
    if percentage >= 80:
        st.success(f"Great job! You scored **{score}/{total}** ({percentage}%)")
    elif percentage >= 50:
        st.warning(f"Not bad! You scored **{score}/{total}** ({percentage}%). Review the explanations below.")
    else:
        st.error(f"You scored **{score}/{total}** ({percentage}%). Review the lesson and try again.")

    st.markdown("---")
    st.markdown("### Review Answers")

    for i, q_data in enumerate(questions):
        chosen = result.get("answers", {}).get(str(i)) or result.get("answers", {}).get(i, "")
        correct = q_data.get("correct_label", "")
        is_correct = chosen == correct

        bg_color = "#064e3b" if is_correct else "#7f1d1d"
        icon = "✅" if is_correct else "❌"

        st.markdown(
            f"<div style='background:{bg_color};border-radius:8px;padding:0.8rem 1rem;margin:0.5rem 0'>"
            f"<strong>{icon} Q{i+1}. {q_data['question']}</strong><br>"
            f"Your answer: <strong>{chosen}</strong> &nbsp;|&nbsp; Correct: <strong>{correct}</strong><br>"
            f"<em>{q_data.get('explanation','')}</em>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("← Back to Course"):
        ss()["view"] = "course"
        st.rerun()

def main():
    render_sidebar()

    if not ss()["logged_in"]:
        render_login()
        return

    view = ss()["view"]

    if view == "home":
        render_home()
    elif view == "course":
        render_course()
    elif view == "subtopic":
        render_subtopic()
    elif view == "quiz":
        render_quiz()
    else:
        render_home()


if __name__ == "__main__":
    main()
