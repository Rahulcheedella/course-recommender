import logging
import re
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
        """
        Smart multi-keyword, field-weighted search over the course catalog.

        Scoring weights (per matching token):
          - title match:        150 pts  (exact phrase), 80 pts  (per word, whole-word)
          - technology match:   100 pts  (per word, whole-word)
          - skill match:         80 pts  (per word, whole-word)
          - tag match:           60 pts  (per word, whole-word)
          - category match:      50 pts  (per word, whole-word)
          - description match:   30 pts  (per word, whole-word)
          - department match:    20 pts  (low — secondary personalization only)

        Token matching is WHOLE-WORD only to prevent false positives
        (e.g. "rag" should NOT match "storage").

        Department is NEVER the primary filter when a real query exists.
        """
        all_courses = self.get_all_courses()

        # No query and no filters → return everything
        if not query_str and not filters:
            return all_courses

        query_lower = (query_str or "").lower().strip()

        # Tokenize: keep words >= 2 chars, drop filler words
        _STOPWORDS = {
            "for", "and", "the", "with", "to", "in", "of", "a", "an",
            "is", "on", "at", "by", "as", "or", "i", "me", "my", "am",
            "want", "need", "show", "find", "best", "good", "top",
            "course", "courses", "learn", "learning", "study", "how"
        }
        tokens = [
            w for w in re.sub(r"[^a-z0-9 ]", " ", query_lower).split()
            if len(w) >= 2 and w not in _STOPWORDS
        ]

        # Pre-compile whole-word patterns for each token (faster than re.search per-course)
        token_patterns = [re.compile(r"\b" + re.escape(tok) + r"\b") for tok in tokens]

        results = []

        for c in all_courses:
            # ------- Apply explicit sidebar filters first -------
            if filters:
                if filters.get("department") and c.get("department") != filters["department"]:
                    continue
                if filters.get("category") and c.get("category") != filters["category"]:
                    continue
                if filters.get("difficulty") and c.get("difficulty") != filters["difficulty"]:
                    continue
                if filters.get("min_rating") and c.get("rating", 0) < float(filters["min_rating"]):
                    continue

            # ------- Score the course against the query -------
            if query_lower:
                score = 0

                title_lower   = c.get("title", "").lower()
                techs_lower   = " ".join(c.get("technologies", [])).lower()
                skills_lower  = " ".join(c.get("skills", [])).lower()
                tags_lower    = " ".join(c.get("tags", [])).lower()
                cat_lower     = c.get("category", "").lower()
                desc_lower    = c.get("description", "").lower()
                dept_lower    = c.get("department", "").lower()

                # Exact full-phrase bonus.
                # For short queries (≤4 chars, e.g. "RAG", "NLP") use whole-word
                # matching to avoid "rag" hitting "storage", "nlp" hitting "help", etc.
                # For longer phrases (e.g. "machine learning") substring is fine.
                if len(query_lower) <= 4:
                    _qpat = re.compile(r"\b" + re.escape(query_lower) + r"\b")
                    if _qpat.search(title_lower):
                        score += 150
                    if _qpat.search(techs_lower):
                        score += 100
                    if _qpat.search(skills_lower):
                        score += 80
                else:
                    if query_lower in title_lower:
                        score += 150
                    if query_lower in techs_lower:
                        score += 100
                    if query_lower in skills_lower:
                        score += 80

                # Per-token scoring — WHOLE-WORD only to avoid false positives
                for pat in token_patterns:
                    if pat.search(title_lower):
                        score += 80
                    if pat.search(techs_lower):
                        score += 100
                    if pat.search(skills_lower):
                        score += 80
                    if pat.search(tags_lower):
                        score += 60
                    if pat.search(cat_lower):
                        score += 50
                    if pat.search(desc_lower):
                        score += 30
                    if pat.search(dept_lower):
                        score += 20   # lowest weight — secondary personalization only

                # Must have at least one relevant hit to be included
                if score == 0:
                    continue

                c = dict(c)
                c["_search_score"] = score
            else:
                c = dict(c)
                c["_search_score"] = 0

            results.append(c)

        # Sort by relevance score desc, then rating as tiebreaker
        results.sort(
            key=lambda x: (x.get("_search_score", 0), x.get("rating", 0)),
            reverse=True
        )
        return results

mongodb_service = MongoDBService()
