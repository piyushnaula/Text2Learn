import streamlit as st
import os
import sys
import importlib
from dotenv import load_dotenv

if 'services' in sys.modules:
    importlib.reload(sys.modules['services'])

from services import AIService, YouTubeService, DatabaseService

load_dotenv()

st.set_page_config(
    page_title="Text 2 Learn",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)


if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_course' not in st.session_state:
    st.session_state.current_course = None
if 'selected_subtopic' not in st.session_state:
    st.session_state.selected_subtopic = None
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'show_quiz_results' not in st.session_state:
    st.session_state.show_quiz_results = False

@st.cache_resource
def initialize_services():
    """Initialize all services with API keys"""
    groq_key = os.getenv("GROQ_API_KEY")
    youtube_key = os.getenv("YOUTUBE_API_KEY")
    db_url = os.getenv("DATABASE_URL")

    if not groq_key:
        st.error("GROQ_API_KEY not found in environment variables")
        st.stop()

    if not youtube_key:
        st.warning("YOUTUBE_API_KEY not found. Video fetching will be disabled.")

    if not db_url:
        st.error("DATABASE_URL not found in environment variables")
        st.stop()

    ai_service = AIService(groq_key)
    youtube_service = YouTubeService(youtube_key) if youtube_key else None
    db_service = DatabaseService(db_url)

    db_service.init_db()

    return ai_service, youtube_service, db_service


def estimate_reading_time(content: str) -> int:
    """Estimate reading time in minutes based on word count"""
    if not content:
        return 0
    words = len(content.split())
    minutes = max(1, round(words / 200))
    return minutes


def create_progress_summary(completed: int, total: int) -> dict:
    """Create a progress summary dictionary"""
    percentage = int((completed / total * 100)) if total > 0 else 0
    return {
        'completed': completed,
        'total': total,
        'percentage': percentage
    }


def calculate_quiz_score(user_answers: dict, quiz_dicts: list) -> dict:
    """Calculate quiz score based on user answers"""
    correct = 0
    total = len(quiz_dicts)
    
    for i, quiz in enumerate(quiz_dicts):
        user_answer = user_answers.get(i, '')
        if user_answer == quiz.get('correct_answer', ''):
            correct += 1
    
    percentage = int((correct / total * 100)) if total > 0 else 0
    
    return {
        'score': correct,
        'total': total,
        'percentage': percentage
    }


def generate_quiz_feedback(score_data: dict) -> str:
    """Generate feedback message based on quiz score"""
    percentage = score_data['percentage']
    
    if percentage >= 90:
        return "Excellent! You have mastered this topic!"
    elif percentage >= 70:
        return "Good job! You have a solid understanding."
    elif percentage >= 50:
        return "Not bad, but consider reviewing the material."
    else:
        return "Keep learning! Review the content and try again."


def main():
    """Main application function"""

    ai_service, youtube_service, db_service = initialize_services()

    st.title("AI Course Generator")
    st.caption("Generate personalized courses on any topic using AI")

    with st.sidebar:
        st.header("User Profile")

        username = st.text_input("Username", value="default_user")

        if st.button("Login / Register"):
            user = db_service.get_or_create_user(username)
            st.session_state.user_id = user.id
            st.success(f"Logged in as {username}")

        if st.session_state.user_id:
            st.divider()

            st.header("My Courses")
            courses = db_service.get_user_courses(st.session_state.user_id)

            if courses:
                for course in courses:
                    if st.button(f"{course.title}", key=f"course_{course.id}"):
                        st.session_state.current_course = course
                        st.session_state.selected_subtopic = None
                        st.rerun()
            else:
                st.info("No courses yet. Create your first course below!")

    if not st.session_state.user_id:
        st.info("Please login or register using the sidebar to get started.")
        return

    if not st.session_state.current_course:
        st.subheader("Generate a Course")
        st.write("Enter any topic and AI will create a comprehensive course with lessons, videos, and quizzes.")

        col1, col2 = st.columns([3, 1])

        with col1:
            topic = st.text_input(
                "What do you want to learn today?",
                placeholder="e.g., Introduction to Machine Learning, Digital Marketing, Web Development",
                label_visibility="visible"
            )

        with col2:
            st.write("")
            st.write("")
            generate_btn = st.button("Generate Course", use_container_width=True, type="primary")

        if generate_btn and topic:
            with st.spinner("AI is creating your personalized course..."):
                try:
                    outline = ai_service.generate_course_outline(topic)

                    if not outline or len(outline) < 3:
                        st.error("Failed to generate a valid course outline. Please try again.")
                        return

                    course = db_service.create_full_course(
                        st.session_state.user_id,
                        topic,
                        outline
                    )

                    st.session_state.current_course = course
                    st.success(f"Course '{topic}' created successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error generating course: {str(e)}")

        st.divider()
        st.subheader("Popular Topics")

        example_topics = [
            ("Python Programming", "Introduction to Python Programming"),
            ("Digital Marketing", "Digital Marketing Fundamentals"),
            ("Data Science", "Data Science for Beginners"),
            ("React Development", "Web Development with React"),
            ("Personal Finance", "Personal Finance Management"),
            ("AI & ChatGPT", "Introduction to ChatGPT and AI")
        ]

        cols = st.columns(3)
        for i, (display_name, full_topic) in enumerate(example_topics):
            with cols[i % 3]:
                if st.button(display_name, key=f"example_{i}", use_container_width=True):
                    topic = full_topic
                    with st.spinner("AI is creating your personalized course..."):
                        try:
                            outline = ai_service.generate_course_outline(full_topic)
                            if outline and len(outline) >= 3:
                                course = db_service.create_full_course(
                                    st.session_state.user_id,
                                    full_topic,
                                    outline
                                )
                                st.session_state.current_course = course
                                st.success(f"Course '{full_topic}' created successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    else:
        display_course(ai_service, youtube_service, db_service)

def display_course(ai_service, youtube_service, db_service):
    """Display the current course with modules and subtopics"""

    course = st.session_state.current_course

    if st.button("← New Course", key="back_to_home"):
        st.session_state.current_course = None
        st.session_state.selected_subtopic = None
        st.rerun()

    st.title(course.title)

    modules = db_service.get_course_modules(course.id)

    if not st.session_state.selected_subtopic:
        st.subheader("Course Outline")

        for module in modules:
            with st.expander(f"**Module {module.order_index + 1}: {module.title}**", expanded=True):
                subtopics = db_service.get_module_subtopics(module.id)

                for subtopic in subtopics:
                    status = "✅" if subtopic.is_generated else "⭕"

                    if st.button(
                        f"{status} {subtopic.title}",
                        key=f"subtopic_{subtopic.id}",
                        use_container_width=True
                    ):
                        st.session_state.selected_subtopic = subtopic
                        st.session_state.quiz_answers = {}
                        st.session_state.show_quiz_results = False
                        st.rerun()

        total_subtopics = sum(len(db_service.get_module_subtopics(m.id)) for m in modules)
        generated_subtopics = sum(
            sum(1 for s in db_service.get_module_subtopics(m.id) if s.is_generated)
            for m in modules
        )

        progress = create_progress_summary(generated_subtopics, total_subtopics)

        st.divider()
        st.subheader("Learning Progress")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Completed", f"{progress['completed']}", help="Subtopics you've completed")
        with col2:
            st.metric("Remaining", f"{progress['total'] - progress['completed']}", help="Subtopics left to complete")
        with col3:
            st.metric("Progress", f"{progress['percentage']}%", help="Overall course completion")

        st.progress(progress['percentage'] / 100)

    else:
        display_subtopic(ai_service, youtube_service, db_service)

def display_subtopic(ai_service, youtube_service, db_service):
    """Display detailed subtopic content"""

    subtopic = st.session_state.selected_subtopic

    if st.button("← Back to Course Outline"):
        st.session_state.selected_subtopic = None
        st.session_state.quiz_answers = {}
        st.session_state.show_quiz_results = False
        st.rerun()

    st.header(subtopic.title)

    if not subtopic.is_generated:
        with st.spinner("AI is generating detailed content..."):
            try:
                course = st.session_state.current_course

                modules = db_service.get_course_modules(course.id)
                current_module = None
                all_module_subtopics = []
                for m in modules:
                    subtopics = db_service.get_module_subtopics(m.id)
                    if any(s.id == subtopic.id for s in subtopics):
                        current_module = m
                        all_module_subtopics = subtopics
                        break

                previous_subtopic_titles = []
                for s in all_module_subtopics:
                    if s.id == subtopic.id:
                        break
                    if s.is_generated:
                        previous_subtopic_titles.append(s.title)

                content = ai_service.generate_subtopic_content(
                    course.title,
                    current_module.title if current_module else "Module",
                    subtopic.title,
                    previous_subtopics=previous_subtopic_titles
                )

                keywords = ai_service.generate_youtube_keywords(
                    course.title,
                    current_module.title if current_module else "Module",
                    subtopic.title
                )

                video_url = None
                video_title = None
                if youtube_service:
                    video_data = youtube_service.search_best_video(keywords)
                    if video_data:
                        video_url = video_data['url']
                        video_title = video_data['title']

                db_service.update_subtopic_content(
                    subtopic.id,
                    content,
                    keywords,
                    video_url,
                    video_title
                )

                try:
                    with st.spinner("Generating quiz questions..."):
                        quiz_data = ai_service.generate_quiz(
                            course.title,
                            current_module.title if current_module else "Module",
                            subtopic.title,
                            content[:500] if content else ""  
                        )

                    quiz_saved_count = 0
                    if quiz_data:
                        for i, quiz in enumerate(quiz_data):
                            if (quiz.get('question') and
                                quiz.get('option_a') and
                                quiz.get('option_b') and
                                quiz.get('option_c') and
                                quiz.get('option_d') and
                                quiz.get('correct_answer')):

                                db_service.create_quiz(
                                    subtopic.id,
                                    quiz.get('question', ''),
                                    quiz.get('option_a', ''),
                                    quiz.get('option_b', ''),
                                    quiz.get('option_c', ''),
                                    quiz.get('option_d', ''),
                                    quiz.get('correct_answer', 'A'),
                                    quiz.get('explanation', ''),
                                    i
                                )
                                quiz_saved_count += 1

                    if quiz_saved_count > 0:
                        st.success(f"Generated {quiz_saved_count} quiz questions!")
                    else:
                        st.info("ℹNo quiz questions were generated for this topic. Content and video are still available for learning!")

                except Exception as quiz_error:
                    st.warning(f"Could not generate quiz: {str(quiz_error)}. Content and video are still available!")

                subtopic = db_service.get_subtopic(subtopic.id)
                st.session_state.selected_subtopic = subtopic
                st.rerun()

            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
                return

    st.divider()

    reading_time = estimate_reading_time(subtopic.content or "")
    st.caption(f"Estimated reading time: {reading_time} min")

    tab1, tab2, tab3 = st.tabs(["Content", "Video Tutorial", "Quiz"])

    with tab1:
        st.markdown(subtopic.content or "No content available")

    with tab2:
        if subtopic.video_url:
            st.subheader("Recommended Tutorial")
            st.write(f"**{subtopic.video_title}**")

            video_id = subtopic.video_url.split('watch?v=')[-1].split('&')[0]
            st.video(f"https://www.youtube.com/watch?v={video_id}")

            st.caption(f"Search keywords: {subtopic.youtube_keywords}")
        else:
            st.info("No video tutorial available for this topic")

    with tab3:
        display_quiz(db_service, subtopic.id)

def display_quiz(db_service, subtopic_id):
    """Display quiz for the subtopic"""

    quizzes = db_service.get_subtopic_quizzes(subtopic_id)

    if not quizzes:
        st.info("No quiz available for this topic")
        return

    st.subheader(f"Quiz ({len(quizzes)} questions)")

    if not st.session_state.show_quiz_results:
        for i, quiz in enumerate(quizzes):
            st.markdown(f"**Question {i+1}:** {quiz.question}")

            answer = st.radio(
                "Select your answer:",
                options=['A', 'B', 'C', 'D'],
                format_func=lambda x: f"{x}) {getattr(quiz, f'option_{x.lower()}')}",
                key=f"quiz_{quiz.id}",
                index=None
            )

            if answer:
                st.session_state.quiz_answers[i] = answer

            st.divider()

        if st.button("Submit Quiz", use_container_width=True):
            if len(st.session_state.quiz_answers) < len(quizzes):
                st.warning("Please answer all questions before submitting")
            else:
                st.session_state.show_quiz_results = True
                st.rerun()

    else:
        quiz_dicts = [
            {
                'question': q.question,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation
            }
            for q in quizzes
        ]

        score_data = calculate_quiz_score(st.session_state.quiz_answers, quiz_dicts)
        feedback = generate_quiz_feedback(score_data)

        st.success(f"**Score: {score_data['score']} / {score_data['total']} ({score_data['percentage']}%)**")
        st.info(feedback)

        st.subheader("Detailed Results")

        for i, quiz in enumerate(quizzes):
            user_answer = st.session_state.quiz_answers.get(i, '')
            is_correct = user_answer == quiz.correct_answer

            if is_correct:
                st.success(f"Question {i+1}: Correct!")
            else:
                st.error(f"Question {i+1}: Incorrect")
                st.write(f"**Your answer:** {user_answer}")
                st.write(f"**Correct answer:** {quiz.correct_answer}")

            if quiz.explanation:
                with st.expander("See explanation"):
                    st.write(quiz.explanation)

        if st.button("Retake Quiz", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.show_quiz_results = False
            st.rerun()

if __name__ == "__main__":
    main()
