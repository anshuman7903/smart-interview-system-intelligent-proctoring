from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME
from datetime import datetime

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections (like tables in SQL)
candidates_col = db["candidates"]
sessions_col   = db["sessions"]
questions_col  = db["questions"]
reports_col    = db["reports"]


def create_session(candidate_name, domain, difficulty):
    """Create a new interview session and return its ID."""
    session = {
        "candidate_name": candidate_name,
        "domain": domain,
        "difficulty": difficulty,
        "status": "active",
        "created_at": datetime.utcnow(),
        "answers": [],
        "violations": [],
        "score": None
    }
    result = sessions_col.insert_one(session)
    return str(result.inserted_id)  # returns session ID


def save_answer(session_id, question, answer, score, feedback=None):
    """Save a candidate's answer to the session."""
    from bson import ObjectId
    sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"answers": {
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback,
            "timestamp": datetime.utcnow()
        }}}
    )


def log_violation(session_id, violation_type):
    """Log a proctoring violation (e.g. face not detected)."""
    from bson import ObjectId
    sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"violations": {
            "type": violation_type,
            "timestamp": datetime.utcnow()
        }}}
    )


def get_session(session_id):
    """Fetch a session by ID."""
    from bson import ObjectId
    return sessions_col.find_one({"_id": ObjectId(session_id)})


def get_all_sessions():
    """Get all sessions for the recruiter dashboard."""
    return list(sessions_col.find().sort("created_at", -1))