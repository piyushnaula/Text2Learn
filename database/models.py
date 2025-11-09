from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for tracking learners"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    courses = relationship("Course", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Course(Base):
    """Course model for storing AI-generated courses"""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(title='{self.title}')>"


class Module(Base):
    """Module model for course modules"""
    __tablename__ = 'modules'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="modules")
    subtopics = relationship("Subtopic", back_populates="module", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Module(title='{self.title}')>"


class Subtopic(Base):
    """Subtopic model for module subtopics"""
    __tablename__ = 'subtopics'
    
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    youtube_keywords = Column(Text)
    video_url = Column(String(500))
    video_title = Column(String(500))
    order_index = Column(Integer, nullable=False)
    is_generated = Column(Integer, default=0) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    module = relationship("Module", back_populates="subtopics")
    quizzes = relationship("Quiz", back_populates="subtopic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subtopic(title='{self.title}')>"


class Quiz(Base):
    """Quiz model for storing quiz questions"""
    __tablename__ = 'quizzes'
    
    id = Column(Integer, primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), nullable=False)
    question = Column(Text, nullable=False)
    option_a = Column(String(500))
    option_b = Column(String(500))
    option_c = Column(String(500))
    option_d = Column(String(500))
    correct_answer = Column(String(1))
    explanation = Column(Text)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subtopic = relationship("Subtopic", back_populates="quizzes")
    
    def __repr__(self):
        return f"<Quiz(question='{self.question[:50]}...')>"


class UserProgress(Base):
    """Track user progress and quiz scores"""
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subtopic_id = Column(Integer, ForeignKey('subtopics.id'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    score = Column(Float)
    completed = Column(Integer, default=0)  # 0 = incomplete, 1 = complete
    time_spent = Column(Integer)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, subtopic_id={self.subtopic_id})>"
