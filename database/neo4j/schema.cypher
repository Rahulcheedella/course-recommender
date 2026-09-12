// Neo4j Graph Database Schema Constraints & Indexes for Course Recommendation System

CREATE CONSTRAINT FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT FOR (c:Course) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT FOR (d:Department) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT FOR (t:Technology) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT FOR (cat:Category) REQUIRE cat.name IS UNIQUE;

CREATE INDEX FOR (c:Course) ON (c.department);
CREATE INDEX FOR (c:Course) ON (c.difficulty);
CREATE INDEX FOR (c:Course) ON (c.category);
