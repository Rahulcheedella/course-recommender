import logging
from services.neo4j_service import neo4j_service
from services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

# Configurable interaction weights as requested
EVENT_WEIGHTS = {
    "search": 1.0,
    "course_view": 2.0,
    "course_click": 2.5,
    "wishlist": 4.0,
    "enrollment": 6.0,
    "completion": 8.0,
    "chatbot_query": 1.5
}

class InterestEngine:
    def process_event(self, user_id, event_type, course_id=None, metadata=None):
        """Processes user interaction and updates interest weights in Neo4j and MongoDB."""
        weight = EVENT_WEIGHTS.get(event_type, 1.0)
        metadata = metadata or {}
        extracted_topics = []

        # Case 1: Search event
        if event_type in ["search", "chatbot_query"] and metadata.get("query"):
            query_str = metadata["query"]
            extracted_topics.append(query_str.title())

        # Case 2: Course interaction
        if course_id:
            course = mongodb_service.get_course_by_id(course_id)
            if course:
                extracted_topics.extend(course.get("technologies", []))
                extracted_topics.extend(course.get("skills", []))
                # Also include category as a topic
                extracted_topics.append(course.get("category"))

        # Update interest scores in Neo4j
        for topic in set(extracted_topics):
            if topic:
                neo4j_service.update_interest_score(user_id, topic, weight=weight)

        # Log event in MongoDB
        mongodb_service.log_interaction(user_id, event_type, course_id=course_id, metadata=metadata)

    def get_user_interest_percentages(self, user_id):
        """Generates normalized interest scores (%) for dashboard visualization."""
        context = neo4j_service.get_user_graph_context(user_id)
        interests = context.get("interests", [])

        if not interests:
            # Fallback based on user department skills if cold-start
            user = mongodb_service.get_user_by_id(user_id)
            if user:
                skills = user.get("skills", []) + user.get("interests", [])
                return [{"topic": topic, "score": 75} for topic in skills[:5]]
            return [
                {"topic": "Full Stack", "score": 80},
                {"topic": "Python", "score": 70},
                {"topic": "AI & ML", "score": 60}
            ]

        # Calculate max score for scaling to 100%
        valid_interests = [i for i in interests if i and i.get("tech") and i.get("score") is not None]
        if not valid_interests:
            return []

        max_score = max([i["score"] for i in valid_interests] + [10.0])
        results = []
        for item in sorted(valid_interests, key=lambda x: x["score"], reverse=True)[:6]:
            percentage = min(100, int((item["score"] / max_score) * 100))
            results.append({"topic": item["tech"], "score": max(20, percentage)})

        return results

interest_engine = InterestEngine()
