import logging
import math
from datetime import datetime, timezone
from services.neo4j_service import neo4j_service
from services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

# Map unknown/uncommon departments to the closest known one with courses
DEPT_NORMALIZE = {
    "ACSC": "ECE",
    "Aeronautical": "ECE",
    "Aerospace": "ECE",
    "IT": "CSE",
    "Information Technology": "CSE",
    "AI & DS": "AI & DS",
    "AI & ML": "AI & ML",
    "Other": "CSE",
}

class RecommendationEngine:
    def get_user_recommendations(self, user_id):
        """Generates structured multi-section personalized recommendations."""
        user = mongodb_service.get_user_by_id(user_id)
        if not user:
            return self._get_generic_recommendations()

        raw_dept = user.get("department", "CSE")
        # Normalize unknown departments
        user_dept = DEPT_NORMALIZE.get(raw_dept, raw_dept)
        user_skills = set(user.get("skills", []))
        user_interests = set(user.get("interests", []))
        user_experience = user.get("experience", "Beginner")

        # Fetch Graph Context & Interaction Events
        graph_context = neo4j_service.get_user_graph_context(user_id)
        viewed_ids = set(graph_context.get("viewed_courses", []))
        saved_ids = set(graph_context.get("saved_courses", []))
        enrolled_ids = set(graph_context.get("enrolled_courses", []))

        # Traversed graph candidate paths
        graph_candidates = neo4j_service.get_traversed_recommendations(user_id)
        graph_reason_map = {item["course_id"]: item["reason"] for item in graph_candidates if "course_id" in item}

        all_courses = mongodb_service.get_all_courses()
        recent_search_scores = self._get_recent_search_scores(user_id, all_courses)

        # Check if this department has any courses in the catalog
        dept_course_count = sum(1 for c in all_courses if c.get("department") == user_dept)
        logger.info(f"[Recs] User dept: {raw_dept} → normalized: {user_dept} | dept_courses: {dept_course_count}")

        scored_courses = []

        for course in all_courses:
            cid = course["id"]
            score = 0.0
            reasons = []

            # 1. Department match (primary dept, then interest-based for cross-dept)
            if course.get("department") == user_dept:
                score += 20.0
                reasons.append(f"Top choice for {user_dept} department")
            elif dept_course_count == 0:
                # No courses for this dept — use interests to rank instead
                course_techs = set(course.get("technologies", []) + course.get("skills", []))
                interest_overlap = user_interests.intersection(course_techs)
                if interest_overlap:
                    score += 18.0
                    reasons.append(f"Matches your interest in {', '.join(list(interest_overlap)[:2])}")

            # 2. Skill & Interest overlap
            course_skills = set(course.get("skills", []) + course.get("technologies", []))
            skill_overlap = user_skills.intersection(course_skills)
            if skill_overlap:
                score += len(skill_overlap) * 8.0
                reasons.append(f"Matches your skills: {', '.join(list(skill_overlap)[:2])}")

            interest_overlap = user_interests.intersection(course_skills)
            if interest_overlap:
                score += len(interest_overlap) * 10.0
                reasons.append(f"Matches your interests: {', '.join(list(interest_overlap)[:2])}")

            # 3. Knowledge Graph traversal score
            if cid in graph_reason_map:
                score += 30.0
                g_reason = graph_reason_map[cid]
                if "Cross-department" in g_reason:
                    score += 15.0
                    reasons.insert(0, g_reason)
                else:
                    reasons.append(g_reason)

            # 4. Recent search activity, expanded through the existing graph
            recent_search_score = recent_search_scores.get(cid, 0.0)
            if recent_search_score:
                score += recent_search_score
                reasons.append("Based on your recent search activity")

            # 5. Difficulty alignment
            if course.get("difficulty") == user_experience:
                score += 10.0

            # 6. Rating & Popularity
            score += float(course.get("rating", 4.5)) * 3.0
            score += min(15.0, (course.get("students", 0) / 10000.0))

            # 7. Penalty for already enrolled
            if cid in enrolled_ids:
                score -= 50.0

            explanation = reasons[0] if reasons else f"Highly rated in {course.get('category')}"

            scored_courses.append({
                "course": course,
                "score": score,
                "recommendation_reason": explanation
            })

        scored_courses.sort(key=lambda x: x["score"], reverse=True)

        # ── Section 1: Recommended For You ──────────────────────────────
        recommended_for_you = []
        for item in scored_courses[:6]:
            c = dict(item["course"])
            c["recommendation_reason"] = item["recommendation_reason"]
            recommended_for_you.append(c)

        # ── Section 2: Popular in Your Department ───────────────────────
        dept_courses = [c for c in all_courses if c.get("department") == user_dept]
        # If dept has no courses, fall back to interest-based popular picks
        if not dept_courses:
            dept_courses = sorted(
                all_courses,
                key=lambda c: (
                    bool(user_interests.intersection(set(c.get("technologies", []) + c.get("skills", [])))),
                    c.get("students", 0)
                ),
                reverse=True
            )
        else:
            dept_courses = sorted(dept_courses, key=lambda x: x.get("students", 0), reverse=True)

        popular_in_dept = []
        for c in dept_courses[:6]:
            cd = dict(c)
            cd["recommendation_reason"] = f"Popular choice among {raw_dept} students"
            popular_in_dept.append(cd)

        # ── Section 3: Because You Viewed / Saved ────────────────────────
        because_you_viewed = []
        if viewed_ids or saved_ids:
            interacted_ids = viewed_ids.union(saved_ids)
            for item in scored_courses:
                c = item["course"]
                if c["id"] not in interacted_ids and c["id"] not in enrolled_ids:
                    cd = dict(c)
                    cd["recommendation_reason"] = f"Based on your recent interest in {c.get('category')}"
                    because_you_viewed.append(cd)
                    if len(because_you_viewed) >= 6:
                        break
        if not because_you_viewed:
            because_you_viewed = [dict(item["course"]) for item in scored_courses[6:12]]

        # ── Section 4: Based on Your Recent History ──────────────────────
        based_on_history = self._get_history_based_recommendations(user_id, all_courses, enrolled_ids)

        # ── Section 5: Trending ──────────────────────────────────────────
        trending_courses = sorted(
            all_courses,
            key=lambda x: (x.get("rating", 0), x.get("students", 0)),
            reverse=True
        )[:6]
        for c in trending_courses:
            c = dict(c)
            c["recommendation_reason"] = "🔥 Trending across all tech learning domains"

        # ── Section 6: Continue Learning ─────────────────────────────────
        continue_learning = mongodb_service.get_user_enrollments(user_id)

        return {
            "recommended_for_you": recommended_for_you,
            "popular_in_department": popular_in_dept,
            "because_you_viewed": because_you_viewed,
            "based_on_history": based_on_history,
            "trending_courses": trending_courses,
            "continue_learning": continue_learning
        }

    def _get_recent_search_scores(self, user_id, all_courses):
        """Return decayed course boosts for recent searches and graph matches."""
        try:
            interactions = mongodb_service.get_user_interactions(user_id, limit=20)
        except Exception:
            return {}

        now = datetime.now(timezone.utc)
        search_scores = {}

        for position, event in enumerate(interactions):
            if event.get("event_type") != "search":
                continue

            query = (event.get("metadata") or {}).get("query", "").strip()
            if not query:
                continue

            timestamp = event.get("timestamp")
            try:
                event_time = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
                if event_time.tzinfo is None:
                    event_time = event_time.replace(tzinfo=timezone.utc)
                age_days = max(0.0, (now - event_time).total_seconds() / 86400.0)
            except (TypeError, ValueError):
                # Preserve ordering when an older event has no usable timestamp.
                age_days = float(position)

            recency = math.exp(-age_days / 7.0)
            try:
                graph_result = neo4j_service.extract_entities_and_search_graph(query)
            except Exception:
                graph_result = {}

            graph_scores = graph_result.get("course_scores", {})
            entities = graph_result.get("entities", [])
            query_terms = {
                term.lower()
                for term in query.split()
                if len(term) > 2
            }
            query_terms.update(
                str(entity).lower()
                for entity in entities
                if entity
            )

            for course in all_courses:
                course_id = course["id"]
                course_text = " ".join([
                    course.get("title", ""),
                    course.get("department", ""),
                    course.get("category", ""),
                    " ".join(course.get("technologies", [])),
                    " ".join(course.get("skills", [])),
                    " ".join(course.get("tags", []))
                ]).lower()
                lexical_matches = sum(1 for term in query_terms if term in course_text)
                graph_match = float(graph_scores.get(course_id, 0.0))

                if lexical_matches or graph_match:
                    lexical_boost = min(20.0, lexical_matches * 5.0)
                    graph_boost = min(30.0, graph_match * 0.3)
                    search_scores[course_id] = search_scores.get(course_id, 0.0) + (
                        lexical_boost + graph_boost
                    ) * recency

        return search_scores

    def _get_history_based_recommendations(self, user_id, all_courses, enrolled_ids):
        """
        Reads user's recent interaction history from MongoDB and
        returns courses related to recently searched/clicked topics.
        """
        try:
            interactions = mongodb_service.get_user_interactions(user_id, limit=20)
        except Exception:
            interactions = []

        if not interactions:
            return []

        # Extract topic terms from recent searches and views
        search_terms = set()
        clicked_course_ids = set()

        for event in interactions:
            etype = event.get("event_type", "")
            meta = event.get("metadata", {})
            if etype in ("search", "chatbot_query") and meta.get("query"):
                # Extract key words from search query
                words = meta["query"].lower().split()
                for w in words:
                    if len(w) > 3:  # skip short stop words
                        search_terms.add(w)
            elif etype in ("course_view", "course_click") and event.get("course_id"):
                clicked_course_ids.add(event["course_id"])

        if not search_terms and not clicked_course_ids:
            return []

        history_courses = []
        seen_ids = set()

        # Find courses matching recent search terms
        for course in all_courses:
            cid = course["id"]
            if cid in enrolled_ids or cid in seen_ids:
                continue

            course_text = " ".join([
                course.get("title", ""),
                course.get("category", ""),
                " ".join(course.get("technologies", [])),
                " ".join(course.get("skills", [])),
                " ".join(course.get("tags", []))
            ]).lower()

            match_count = sum(1 for term in search_terms if term in course_text)

            if match_count > 0 or cid in clicked_course_ids:
                cd = dict(course)
                if cid in clicked_course_ids:
                    cd["recommendation_reason"] = "You recently viewed this course"
                else:
                    cd["recommendation_reason"] = f"Based on your recent search activity"
                cd["_history_score"] = match_count + (5 if cid in clicked_course_ids else 0)
                history_courses.append(cd)
                seen_ids.add(cid)

        history_courses.sort(key=lambda x: x.get("_history_score", 0), reverse=True)
        return history_courses[:6]

    def get_query_recommendations(
        self,
        user_id,
        query,
        limit=8
    ):
        """
        Generates recommendations specifically for the user's
        current natural-language search.

        Explicit query intent has priority over department.
        Department is retained as secondary personalization.
        """

        user = (
            mongodb_service.get_user_by_id(user_id)
            if user_id
            else None
        )

        graph_result = (
            neo4j_service.extract_entities_and_search_graph(query)
        )

        matched_ids = graph_result.get(
            "matched_course_ids",
            []
        )

        graph_scores = graph_result.get(
            "course_scores",
            {}
        )

        technologies = graph_result.get(
            "technologies",
            []
        )

        skills = graph_result.get(
            "skills",
            []
        )

        topics = graph_result.get(
            "topics",
            []
        )

        departments = graph_result.get(
            "departments",
            []
        )

        all_courses = mongodb_service.get_all_courses()

        user_department = (
            user.get("department")
            if user
            else None
        )

        user_skills = set(
            user.get("skills", [])
            if user
            else []
        )

        query_terms = set(
            [
                x.lower()
                for x in (
                    technologies
                    + skills
                    + topics
                    + departments
                )
            ]
        )

        scored = []

        for course in all_courses:

            course_id = course["id"]

            score = float(
                graph_scores.get(course_id, 0)
            )

            reasons = []

            course_department = course.get(
                "department"
            )

            course_text = " ".join(
                [
                    course.get("title", ""),
                    course.get("category", ""),
                    course.get("description", ""),
                    " ".join(course.get("skills", [])),
                    " ".join(course.get("technologies", [])),
                    " ".join(course.get("tags", []))
                ]
            ).lower()

            # -------------------------------------------------
            # PRIMARY QUERY MATCH
            # -------------------------------------------------

            direct_matches = 0

            for term in query_terms:

                if term and term.lower() in course_text:

                    direct_matches += 1

            if direct_matches:

                score += direct_matches * 45

                reasons.append(
                    "Matches your current search"
                )

            # -------------------------------------------------
            # EXPLICIT DEPARTMENT CONTEXT
            # -------------------------------------------------

            if (
                user_department
                and course_department == user_department
            ):

                score += 12

                reasons.append(
                    f"Relevant to your {user_department} background"
                )

            # -------------------------------------------------
            # QUERY DEPARTMENT
            # -------------------------------------------------

            if (
                course_department
                and course_department in departments
            ):

                score += 15

                reasons.append(
                    f"Related to {course_department} engineering"
                )

            # -------------------------------------------------
            # USER SKILLS
            # -------------------------------------------------

            course_skills = set(
                course.get("skills", [])
            )

            skill_overlap = user_skills.intersection(
                course_skills
            )

            if skill_overlap:

                score += len(skill_overlap) * 10

                reasons.append(
                    "Builds on your existing skills"
                )

            # -------------------------------------------------
            # RATING
            # -------------------------------------------------

            score += (
                float(course.get("rating", 0))
                * 2
            )

            # -------------------------------------------------
            # POPULARITY
            # -------------------------------------------------

            score += min(
                10,
                float(course.get("students", 0))
                / 10000
            )

            scored.append(
                {
                    "course": course,
                    "score": score,
                    "reason": (
                        reasons[0]
                        if reasons
                        else "Related to your learning interests"
                    )
                }
            )

        # -----------------------------------------------------
        # SORT
        # -----------------------------------------------------

        scored.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # -----------------------------------------------------
        # FALLBACK
        # -----------------------------------------------------

        if not matched_ids:

            # Use MongoDB text search only as fallback.
            fallback = mongodb_service.search_courses(
                query
            )

            fallback_ids = {
                c["id"]
                for c in fallback
            }

            for item in scored:

                if item["course"]["id"] in fallback_ids:

                    item["score"] += 80

        # -----------------------------------------------------
        # RETURN
        # -----------------------------------------------------

        results = []

        for item in scored:

            course = dict(item["course"])

            course["recommendation_reason"] = (
                item["reason"]
            )

            course["_recommendation_score"] = round(
                item["score"],
                2
            )

            results.append(course)

            if len(results) >= limit:
                break

        return {
            "query": query,
            "entities": graph_result.get(
                "entities",
                []
            ),
            "technologies": technologies,
            "skills": skills,
            "topics": topics,
            "departments": departments,
            "matched_courses": results
        }

    def _get_generic_recommendations(self):
        courses = mongodb_service.get_all_courses()
        top_courses = sorted(courses, key=lambda x: x.get("rating", 0), reverse=True)[:6]
        for c in top_courses:
            c["recommendation_reason"] = "Top rated platform course"
        return {
            "recommended_for_you": top_courses,
            "popular_in_department": top_courses,
            "because_you_viewed": top_courses,
            "based_on_history": [],
            "trending_courses": top_courses,
            "continue_learning": []
        }

recommendation_engine = RecommendationEngine()
