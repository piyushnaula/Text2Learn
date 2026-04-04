from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Subtopic(BaseModel):
    title: str
    status: str = "locked"          
    lesson_id: Optional[str] = None 
    video_url: Optional[str] = None
    video_title: Optional[str] = None

class Unit(BaseModel):
    unit_number: int
    title: str
    description: str
    subtopics: List[Subtopic] = []
    quiz_done: bool = False
    quiz_score: Optional[int] = None  

class Course(BaseModel):
    topic: str
    units: List[Unit] = []
    step: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfile(BaseModel):
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    courses: List[str] = []         

class Lesson(BaseModel):
    subtopic: str
    topic_tag: str                  
    content: str                    
    summary: str                    
    video_url: Optional[str] = None
    video_title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizOption(BaseModel):
    label: str                      
    text: str

class QuizQuestion(BaseModel):
    question: str
    options: List[QuizOption]
    correct_label: str              
    explanation: str

class Quiz(BaseModel):
    unit_number: int
    unit_title: str
    questions: List[QuizQuestion]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizResult(BaseModel):
    username: str
    course_topic: str
    unit_number: int
    score: int
    total: int
    answers: Dict[int, str] = {}    # question_index -> chosen_label
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class CourseState(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    course_id: Optional[str] = None
    topic: Optional[str] = None
    units: Optional[List[Dict[str, Any]]] = None
    current_unit_index: Optional[int] = None
    current_subtopic_index: Optional[int] = None
    step: Optional[str] = None
    error: Optional[str] = None
