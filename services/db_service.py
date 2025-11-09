import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List, Dict
from database.models import Base, User, Course, Module, Subtopic, Quiz, UserProgress
from datetime import datetime


class DatabaseService:
    """Service for managing database operations"""
    
    def __init__(self, database_url: str):
        """Initialize database connection."""
        if database_url.startswith('postgresql://') and 'psycopg' not in database_url:
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')

        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def get_or_create_user(self, username: str, email: Optional[str] = None) -> User:
        """Get existing user or create a new one"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username, email=email)
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    def create_course(self, user_id: int, title: str, description: Optional[str] = None) -> Course:
        """Create a new course"""
        session = self.get_session()
        try:
            course = Course(user_id=user_id, title=title, description=description)
            session.add(course)
            session.commit()
            session.refresh(course)
            return course
        finally:
            session.close()
    
    def get_course_by_title(self, user_id: int, title: str) -> Optional[Course]:
        """Get a course by title for a specific user"""
        session = self.get_session()
        try:
            return session.query(Course).filter_by(user_id=user_id, title=title).first()
        finally:
            session.close()
    
    def get_user_courses(self, user_id: int) -> List[Course]:
        """Get all courses for a user"""
        session = self.get_session()
        try:
            return session.query(Course).filter_by(user_id=user_id).all()
        finally:
            session.close()

    def create_module(self, course_id: int, title: str, description: Optional[str] = None, 
                     order_index: int = 0) -> Module:
        """Create a new module"""
        session = self.get_session()
        try:
            module = Module(
                course_id=course_id,
                title=title,
                description=description,
                order_index=order_index
            )
            session.add(module)
            session.commit()
            session.refresh(module)
            return module
        finally:
            session.close()
    
    def get_course_modules(self, course_id: int) -> List[Module]:
        """Get all modules for a course, ordered by order_index"""
        session = self.get_session()
        try:
            return session.query(Module).filter_by(course_id=course_id).order_by(Module.order_index).all()
        finally:
            session.close()

    def create_subtopic(self, module_id: int, title: str, order_index: int = 0) -> Subtopic:
        """Create a new subtopic"""
        session = self.get_session()
        try:
            subtopic = Subtopic(
                module_id=module_id,
                title=title,
                order_index=order_index,
                is_generated=0
            )
            session.add(subtopic)
            session.commit()
            session.refresh(subtopic)
            return subtopic
        finally:
            session.close()
    
    def get_subtopic(self, subtopic_id: int) -> Optional[Subtopic]:
        """Get a subtopic by ID"""
        session = self.get_session()
        try:
            return session.query(Subtopic).filter_by(id=subtopic_id).first()
        finally:
            session.close()
    
    def update_subtopic_content(self, subtopic_id: int, content: str, 
                                youtube_keywords: Optional[str] = None,
                                video_url: Optional[str] = None,
                                video_title: Optional[str] = None):
        """Update subtopic with generated content"""
        session = self.get_session()
        try:
            subtopic = session.query(Subtopic).filter_by(id=subtopic_id).first()
            if subtopic:
                subtopic.content = content
                subtopic.youtube_keywords = youtube_keywords
                subtopic.video_url = video_url
                subtopic.video_title = video_title
                subtopic.is_generated = 1
                subtopic.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    def get_module_subtopics(self, module_id: int) -> List[Subtopic]:
        """Get all subtopics for a module, ordered by order_index"""
        session = self.get_session()
        try:
            return session.query(Subtopic).filter_by(module_id=module_id).order_by(Subtopic.order_index).all()
        finally:
            session.close()
    
    def is_subtopic_generated(self, subtopic_id: int) -> bool:
        """Check if a subtopic has been generated"""
        session = self.get_session()
        try:
            subtopic = session.query(Subtopic).filter_by(id=subtopic_id).first()
            return subtopic.is_generated == 1 if subtopic else False
        finally:
            session.close()

    def create_quiz(self, subtopic_id: int, question: str, option_a: str, option_b: str,
                   option_c: str, option_d: str, correct_answer: str, 
                   explanation: Optional[str] = None, order_index: int = 0) -> Quiz:
        """Create a new quiz question"""
        session = self.get_session()
        try:
            quiz = Quiz(
                subtopic_id=subtopic_id,
                question=question,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                explanation=explanation,
                order_index=order_index
            )
            session.add(quiz)
            session.commit()
            session.refresh(quiz)
            return quiz
        finally:
            session.close()
    
    def get_subtopic_quizzes(self, subtopic_id: int) -> List[Quiz]:
        """Get all quizzes for a subtopic"""
        session = self.get_session()
        try:
            return session.query(Quiz).filter_by(subtopic_id=subtopic_id).order_by(Quiz.order_index).all()
        finally:
            session.close()
    
    def delete_subtopic_quizzes(self, subtopic_id: int):
        """Delete all quizzes for a subtopic"""
        session = self.get_session()
        try:
            session.query(Quiz).filter_by(subtopic_id=subtopic_id).delete()
            session.commit()
        finally:
            session.close()

    def create_full_course(self, user_id: int, course_title: str, 
                          course_outline: Dict[str, List[str]]) -> Course:
        """
        Create a complete course with modules and subtopics
        
        Args:
            user_id: User ID
            course_title: Course title
            course_outline: Dictionary with module titles as keys and subtopic lists as values
            
        Returns:
            Created Course object
        """
        session = self.get_session()
        try:
            course = Course(user_id=user_id, title=course_title)
            session.add(course)
            session.flush() 
        
            module_order = 0
            for module_title, subtopics in course_outline.items():
                module = Module(
                    course_id=course.id,
                    title=module_title,
                    order_index=module_order
                )
                session.add(module)
                session.flush()
            
                for subtopic_order, subtopic_title in enumerate(subtopics):
                    subtopic = Subtopic(
                        module_id=module.id,
                        title=subtopic_title,
                        order_index=subtopic_order,
                        is_generated=0
                    )
                    session.add(subtopic)
                
                module_order += 1
            
            session.commit()
            session.refresh(course)
            return course
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_quiz_progress(self, user_id: int, subtopic_id: int, quiz_id: int, 
                          score: float, completed: bool = True):
        """Save user's quiz progress"""
        session = self.get_session()
        try:
            progress = UserProgress(
                user_id=user_id,
                subtopic_id=subtopic_id,
                quiz_id=quiz_id,
                score=score,
                completed=1 if completed else 0
            )
            session.add(progress)
            session.commit()
        finally:
            session.close()
    
    def get_user_progress(self, user_id: int, subtopic_id: int) -> Optional[UserProgress]:
        """Get user's progress for a subtopic"""
        session = self.get_session()
        try:
            return session.query(UserProgress).filter_by(
                user_id=user_id, 
                subtopic_id=subtopic_id
            ).first()
        finally:
            session.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        exit(1)
    
    db_service = DatabaseService(database_url)

    print("Initializing database...")
    db_service.init_db()

    print("Creating test user...")
    user = db_service.get_or_create_user("test_user", "test@example.com")
    print(f"User created: {user.username}")

    print("Creating test course...")
    course_outline = {
        "Introduction to Python": [
            "What is Python?",
            "Installing Python",
            "Your First Program"
        ],
        "Variables and Data Types": [
            "Understanding Variables",
            "Basic Data Types",
            "Type Conversion"
        ]
    }
    
    course = db_service.create_full_course(user.id, "Python Basics", course_outline)
    print(f"Course created: {course.title}")

    modules = db_service.get_course_modules(course.id)
    print(f"\nModules created: {len(modules)}")
    for module in modules:
        print(f"  - {module.title}")
        subtopics = db_service.get_module_subtopics(module.id)
        for subtopic in subtopics:
            print(f"    • {subtopic.title}")
