import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pymongo import MongoClient

# Load configuration
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.courses_data import COURSES_DATA, DEMO_USERS

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DB = os.getenv("NEO4J_DATABASE", "CourseRecommendationDB")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DATABASE", "course_recommendation")

def seed_neo4j():
    print(f"Connecting to Neo4j at {NEO4J_URI} [DB: {NEO4J_DB}]...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        with driver.session(database=NEO4J_DB) as session:
            # 1. Clear existing data safely if desired
            print("Cleaning existing Neo4j graph nodes and relationships...")
            session.run("MATCH (n) DETACH DELETE n")

            # 2. Seed Departments
            departments = list(set([c["department"] for c in COURSES_DATA] + [u["department"] for u in DEMO_USERS]))
            for dept in departments:
                session.run("MERGE (d:Department {name: $name})", name=dept)

            # 3. Seed Courses, Skills, Technologies, Categories and Relationships
            for course in COURSES_DATA:
                # Merge Course Node
                session.run("""
                    MERGE (c:Course {id: $id})
                    SET c.title = $title,
                        c.instructor = $instructor,
                        c.category = $category,
                        c.department = $department,
                        c.difficulty = $difficulty,
                        c.rating = $rating,
                        c.students = $students,
                        c.duration = $duration,
                        c.price = $price,
                        c.description = $description,
                        c.thumbnail = $thumbnail
                """, **course)

                # Link Course -> Department
                session.run("""
                    MATCH (c:Course {id: $id}), (d:Department {name: $dept})
                    MERGE (c)-[:BELONGS_TO]->(d)
                """, id=course["id"], dept=course["department"])

                # Merge & Link Category
                session.run("""
                    MERGE (cat:Category {name: $category})
                    WITH cat
                    MATCH (c:Course {id: $id})
                    MERGE (c)-[:BELONGS_TO]->(cat)
                """, id=course["id"], category=course["category"])

                # Merge Skills & Link TEACHES
                for skill in course.get("skills", []):
                    session.run("""
                        MERGE (s:Skill {name: $skill})
                        WITH s
                        MATCH (c:Course {id: $id})
                        MERGE (c)-[:TEACHES]->(s)
                    """, id=course["id"], skill=skill)

                # Merge Technologies & Link COVERS + PART_OF
                for tech in course.get("technologies", []):
                    session.run("""
                        MERGE (t:Technology {name: $tech})
                        WITH t
                        MATCH (c:Course {id: $id}), (cat:Category {name: $category})
                        MERGE (c)-[:COVERS]->(t)
                        MERGE (t)-[:PART_OF]->(cat)
                    """, id=course["id"], tech=tech, category=course["category"])

                # Tags -> Topic Nodes
                for tag in course.get("tags", []):
                    session.run("""
                        MERGE (t:Topic {name: $tag})
                        WITH t
                        MATCH (c:Course {id: $id})
                        MERGE (c)-[:TAGGED_WITH]->(t)
                    """, id=course["id"], tag=tag)

            # 4. Link Course -> RELATED_TO -> Course
            for course in COURSES_DATA:
                for rel_id in course.get("related_ids", []):
                    session.run("""
                        MATCH (c1:Course {id: $id1}), (c2:Course {id: $id2})
                        MERGE (c1)-[:RELATED_TO]->(c2)
                    """, id1=course["id"], id2=rel_id)

            # 5. Link Technology / Skill / Topic relationships
            # Connect skills to each other within same course
            session.run("""
                MATCH (c:Course)-[:TEACHES]->(s1:Skill), (c)-[:TEACHES]->(s2:Skill)
                WHERE s1 <> s2
                MERGE (s1)-[:RELATED_TO]->(s2)
            """)

            session.run("""
                MATCH (c:Course)-[:COVERS]->(t1:Technology), (c)-[:COVERS]->(t2:Technology)
                WHERE t1 <> t2
                MERGE (t1)-[:RELATED_TO]->(t2)
            """)

            session.run("""
                MATCH (c:Course)-[:TAGGED_WITH]->(t1:Topic), (c)-[:TAGGED_WITH]->(t2:Topic)
                WHERE t1 <> t2
                MERGE (t1)-[:RELATED_TO]->(t2)
            """)

            # 6. Seed Demo Users in Neo4j
            for user in DEMO_USERS:
                session.run("""
                    MERGE (u:User {id: $id})
                    SET u.name = $name,
                        u.email = $email,
                        u.department = $department,
                        u.experience = $experience
                """, **user)

                session.run("""
                    MATCH (u:User {id: $id}), (d:Department {name: $dept})
                    MERGE (u)-[:BELONGS_TO]->(d)
                """, id=user["id"], dept=user["department"])

                for skill in user.get("skills", []):
                    session.run("""
                        MERGE (s:Skill {name: $skill})
                        WITH s
                        MATCH (u:User {id: $id})
                        MERGE (u)-[:HAS_SKILL]->(s)
                    """, id=user["id"], skill=skill)

                for tech in user.get("interests", []):
                    session.run("""
                        MERGE (t:Technology {name: $tech})
                        WITH t
                        MATCH (u:User {id: $id})
                        MERGE (u)-[:INTERESTED_IN {score: 5.0}]->(t)
                    """, id=user["id"], tech=tech)

        driver.close()
        print("[SUCCESS] Neo4j seeding completed successfully!")
    except Exception as e:
        print(f"[WARNING] Neo4j Seeding Warning/Error: {e}")

def seed_mongodb():
    print(f"Connecting to MongoDB at {MONGODB_URI} [DB: {MONGODB_DB}]...")
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGODB_DB]

        # Reset collections
        db["courses"].delete_many({})
        db["users"].delete_many({})
        db["wishlists"].delete_many({})
        db["enrollments"].delete_many({})

        # Insert courses catalog
        db["courses"].insert_many(COURSES_DATA)
        # Insert demo users
        db["users"].insert_many(DEMO_USERS)

        print(f"[SUCCESS] MongoDB seeding completed ({len(COURSES_DATA)} courses, {len(DEMO_USERS)} users)!")
    except Exception as e:
        print(f"[WARNING] MongoDB Seeding Warning/Error: {e}")

if __name__ == "__main__":
    print("Starting full database seeding process...")
    seed_neo4j()
    seed_mongodb()
    print("Database initialization finished.")
