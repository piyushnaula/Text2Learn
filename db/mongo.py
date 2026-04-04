import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv('DB_NAME')

_client: Optional[MongoClient] = None
def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client

def get_db():
    return get_client()[DB_NAME]

def users_col() -> Collection:
    return get_db()["users"]

def courses_col() -> Collection:
    return get_db()["courses"]

def lessons_col() -> Collection:
    return get_db()["lessons"]

def quizzes_col() -> Collection:
    return get_db()["quizzes"]

def quiz_results_col() -> Collection:
    return get_db()["quiz_results"]

def get_or_create_user(username):
    col = users_col()
    user = col.find_one({"username": username})
    if user is None:
        doc = {
            "username": username,
            "created_at": datetime.utcnow(),
            "courses": [],
        }
        result = col.insert_one(doc)
        doc["_id"] = result.inserted_id
        user = doc
    return user

def add_course_to_user(username, course_id):
    users_col().update_one(
        {"username": username},
        {"$addToSet": {"courses": course_id}}
    )

def create_course(username, topic):
    doc = {
        "username": username,
        "topic": topic,
        "units": [],
        "step": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = courses_col().insert_one(doc)
    course_id = str(result.inserted_id)
    add_course_to_user(username, course_id)
    return course_id

def get_course(course_id):
    doc = courses_col().find_one({"_id": ObjectId(course_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def update_course(course_id, updates):
    updates["updated_at"] = datetime.utcnow()
    courses_col().update_one(
        {"_id": ObjectId(course_id)},
        {"$set": updates}
    )

def get_user_courses(username) :
    docs = list(
        courses_col()
        .find({"username": username})
        .sort("created_at", -1)
    )
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

def save_lesson(subtopic,topic_tag,content,summary,video_url= None,video_title= None):
    doc = {
        "subtopic": subtopic,
        "topic_tag": topic_tag,
        "content": content,
        "summary": summary,
        "video_url": video_url,
        "video_title": video_title,
        "created_at": datetime.utcnow(),
    }
    result = lessons_col().insert_one(doc)
    return str(result.inserted_id)

def get_lesson(lesson_id):
    doc = lessons_col().find_one({"_id": ObjectId(lesson_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def save_quiz(course_id, unit_number, quiz_data):
    doc = {
        "course_id": course_id,
        "unit_number": unit_number,
        **quiz_data,
        "created_at": datetime.utcnow(),
    }
    result = quizzes_col().insert_one(doc)
    return str(result.inserted_id)

def get_quiz(course_id, unit_number):
    doc = quizzes_col().find_one({"course_id": course_id, "unit_number": unit_number})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def save_quiz_result(
    username,
    course_topic,
    unit_number,
    score,
    total,
    answers):
    doc = {
        "username": username,
        "course_topic": course_topic,
        "unit_number": unit_number,
        "score": score,
        "total": total,
        "answers": answers,
        "submitted_at": datetime.utcnow(),
    }
    quiz_results_col().insert_one(doc)

def get_quiz_result(username, course_topic, unit_number):
    doc = quiz_results_col().find_one({
        "username": username,
        "course_topic": course_topic,
        "unit_number": unit_number,
    })
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc
