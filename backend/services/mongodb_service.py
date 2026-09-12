import logging
from datetime import datetime
from pymongo import MongoClient
from config import Config
from database.courses_data import COURSES_DATA

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=3000)
            self.db = self.client[Config.MONGODB_DATABASE]
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    # --- USER AUTH & PROFILE ---
    def get_user_by_email(self, email):
        if self.db is None:
            return None
        return self.db["users"].find_one({"email": email}, {"_id": 0})

    def get_user_by_id(self, user_id):
        if self.db is None:
            return None
        return self.db["users"].find_one({"id": user_id}, {"_id": 0})

    def create_user(self, user_data):
        if self.db is None:
            return user_data
        user_data["created_at"] = datetime.utcnow().isoformat()
        self.db["users"].insert_one(user_data)
        user_data.pop("_id", None)
        return user_data

    def update_user_profile(self, user_id, update_fields):
        if self.db is None:
            return False
        self.db["users"].update_one({"id": user_id}, {"$set": update_fields})
        return True

    # --- INTERACTION EVENT LOGGING ---
    def log_interaction(self, user_id, event_type, course_id=None, metadata=None):
        """Logs user interactions: search, view, click, wishlist, enrollment, completion."""
        event_doc = {
            "user_id": user_id,
            "event_type": event_type,
            "course_id": course_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        if self.db is not None:
            self.db["interactions"].insert_one(event_doc)
            event_doc.pop("_id", None)
        return event_doc

    def get_user_interactions(self, user_id, limit=50):
        if self.db is None:
            return []
        return list(self.db["interactions"].find({"user_id": user_id}, {"_id": 0}).sort("timestamp", -1).limit(limit))

    # --- WISHLIST & ENROLLMENTS ---
    def toggle_wishlist(self, user_id, course_id):
        if self.db is None:
            return False
        existing = self.db["wishlists"].find_one({"user_id": user_id, "course_id": course_id})
        if existing:
            self.db["wishlists"].delete_one({"_id": existing["_id"]})
            return False
        else:
            self.db["wishlists"].insert_one({
                "user_id": user_id,
                "course_id": course_id,
                "created_at": datetime.utcnow().isoformat()
            })
            return True

    def get_wishlist(self, user_id):
        if self.db is None:
            return []
        items = list(self.db["wishlists"].find({"user_id": user_id}))
        course_ids = [item["course_id"] for item in items]
        return self.get_courses_by_ids(course_ids)

    def enroll_course(self, user_id, course_id):
        if self.db is None:
            return True
        existing = self.db["enrollments"].find_one({"user_id": user_id, "course_id": course_id})
        if not existing:
            self.db["enrollments"].insert_one({
                "user_id": user_id,
                "course_id": course_id,
                "status": "enrolled",
                "progress": 0,
                "enrolled_at": datetime.utcnow().isoformat()
            })
        return True

    def mark_completed(self, user_id, course_id):
        if self.db is None:
            return True
        self.db["enrollments"].update_one(
            {"user_id": user_id, "course_id": course_id},
            {"$set": {"status": "completed", "progress": 100, "completed_at": datetime.utcnow().isoformat()}},
            upsert=True
        )
        return True

    def get_user_enrollments(self, user_id):
        if self.db is None:
            return []
        enrollments = list(self.db["enrollments"].find({"user_id": user_id}))
        result = []
        for e in enrollments:
            course = self.get_course_by_id(e["course_id"])
            if course:
                course["enrollment_status"] = e.get("status", "enrolled")
                course["progress"] = e.get("progress", 0)
                result.append(course)
        return result

    # --- COURSE CATALOG DATA ACCESS ---
    def get_all_courses(self):
        if self.db is not None and self.db["courses"].count_documents({}) > 0:
            courses = list(self.db["courses"].find({}, {"_id": 0}))
            return courses
        return COURSES_DATA

    def get_course_by_id(self, course_id):
        if self.db is not None:
            course = self.db["courses"].find_one({"id": course_id}, {"_id": 0})
            if course:
                return course
        for c in COURSES_DATA:
            if c["id"] == course_id:
                return c
        return None

    def get_courses_by_ids(self, course_ids):
        if not course_ids:
            return []
        if self.db is not None:
            courses = list(self.db["courses"].find({"id": {"$in": course_ids}}, {"_id": 0}))
            if courses:
                return courses
        return [c for c in COURSES_DATA if c["id"] in course_ids]

    def search_courses(self, query_str, filters=None):
        all_courses = self.get_all_courses()
        if not query_str and not filters:
            return all_courses

        results = []
        query_lower = (query_str or "").lower().strip()

        for c in all_courses:
            match = True
            if query_lower:
                # Text match title, tags, description, category, skills, technologies
                searchable_text = " ".join([
                    c.get("title", ""),
                    c.get("category", ""),
                    c.get("department", ""),
                    c.get("description", ""),
                    " ".join(c.get("skills", [])),
                    " ".join(c.get("technologies", [])),
                    " ".join(c.get("tags", []))
                ]).lower()

                if query_lower not in searchable_text:
                    match = False

            if filters:
                if filters.get("department") and c.get("department") != filters["department"]:
                    match = False
                if filters.get("category") and c.get("category") != filters["category"]:
                    match = False
                if filters.get("difficulty") and c.get("difficulty") != filters["difficulty"]:
                    match = False
                if filters.get("min_rating") and c.get("rating", 0) < float(filters["min_rating"]):
                    match = False

            if match:
                results.append(c)

        return results

mongodb_service = MongoDBService()
