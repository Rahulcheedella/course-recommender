import json
import logging
import re
from typing import Dict, List, Any

import requests
from rapidfuzz import process, fuzz

from config import Config
from database.courses_data import COURSES_DATA

logger = logging.getLogger(__name__)


class QueryUnderstandingService:

    def __init__(self):
        self.model = Config.HUGGINGFACE_MODEL
        self.api_key = Config.HUGGINGFACE_API_KEY

        self.course_vocabulary = self._build_vocabulary()

        # Common natural-language aliases.
        self.aliases = {
            # Python
            "python programming": "Python",
            "python language": "Python",
            "python coding": "Python",
            "py": "Python",

            # Mechanical
            "mechanical engineering": "Mechanical",
            "mechanical": "Mechanical",
            "mech": "Mechanical",

            # ECE and ACSC variants
            "electronics and communication": "ECE",
            "electronics communication": "ECE",
            "electronics": "ECE",
            "communication engineering": "ECE",
            "acsc": "ECE",                            # Applied/Aeronautical/Control/Space → ECE
            "aeronautical": "ECE",
            "aerospace": "ECE",
            "space engineering": "ECE",
            "control systems": "ECE",
            "applied and computational": "ECE",
            "applied computing science": "CSE",

            # EEE
            "electrical engineering": "EEE",
            "electrical": "EEE",
            "eee": "EEE",
            "power systems": "EEE",
            "power engineering": "EEE",

            # Civil
            "civil engineering": "Civil",
            "civil": "Civil",

            # CSE / IT
            "computer science": "CSE",
            "computer science engineering": "CSE",
            "cse": "CSE",
            "information technology": "CSE",
            "it": "CSE",

            # AI / ML
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",

            "artificial intelligence": "Artificial Intelligence",
            "ai": "Artificial Intelligence",

            "deep learning": "Deep Learning",
            "dl": "Deep Learning",

            "generative ai": "Generative AI",
            "gen ai": "Generative AI",
            "llm": "Generative AI",
            "large language model": "Generative AI",

            "natural language processing": "NLP",
            "nlp": "NLP",

            "retrieval augmented generation": "RAG",
            "retrieval augmented": "RAG",
            "rag": "RAG",

            # Mechanical Tools
            "solid works": "SOLIDWORKS",
            "solidworks": "SOLIDWORKS",
            "finite element analysis": "FEA",
            "fea": "FEA",
            "ansys": "ANSYS",
            "computational fluid dynamics": "CFD",
            "cfd": "CFD",
            "fluid mechanics": "Fluid Mechanics",
            "auto cad": "AutoCAD",
            "autocad": "AutoCAD",
            "catia": "CATIA",

            # EEE Tools
            "power electronics": "Power Electronics",
            "plc": "PLC Programming",
            "scada": "SCADA",
            "matlab": "MATLAB",
            "simulink": "Simulink",
            "solar": "Solar PV",
            "etap": "ETAP",

            # ECE Tools
            "embedded systems": "Embedded Systems",
            "embedded": "Embedded Systems",
            "microcontroller": "Microcontrollers",
            "microcontrollers": "Microcontrollers",
            "arm cortex": "ARM",
            "stm32": "STM32",
            "arduino": "Arduino C++",
            "esp32": "ESP32",
            "digital signal processing": "DSP",
            "signal processing": "DSP",
            "dsp": "DSP",
            "internet of things": "IoT",
            "iot": "IoT",
            "vlsi": "VLSI",
            "verilog": "Verilog",
            "fpga": "FPGA",
            "vhdl": "Verilog",

            # Cloud / DevOps
            "aws": "AWS",
            "cloud": "Cloud",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "devops": "DevOps",

            # Robotics
            "ros": "ROS2",
            "ros2": "ROS2",
            "robotics": "ROS2",

            # Misc
            "virtual instrumentation": "MATLAB",
            "data science": "Data Science",
            "datascience": "Data Science",
        }

    # ---------------------------------------------------------
    # BUILD VOCABULARY DIRECTLY FROM COURSE DATA
    # ---------------------------------------------------------

    def _build_vocabulary(self) -> List[str]:

        values = set()

        for course in COURSES_DATA:

            values.add(course.get("title", ""))
            values.add(course.get("category", ""))
            values.add(course.get("department", ""))
            values.add(course.get("instructor", ""))

            for field in [
                "skills",
                "technologies",
                "tags"
            ]:
                for value in course.get(field, []):
                    values.add(str(value))

        return sorted(
            [
                value.strip()
                for value in values
                if value and len(value.strip()) > 1
            ],
            key=len,
            reverse=True
        )

    # ---------------------------------------------------------
    # NORMALIZE
    # ---------------------------------------------------------

    def normalize(self, value: str) -> str:

        if not value:
            return ""

        value = value.strip()

        key = value.lower()

        if key in self.aliases:
            return self.aliases[key]

        # Exact vocabulary match
        for item in self.course_vocabulary:
            if item.lower() == key:
                return item

        # Fuzzy vocabulary match
        matches = process.extract(
            value,
            self.course_vocabulary,
            scorer=fuzz.token_set_ratio,
            limit=1
        )

        if matches:

            candidate, score, _ = matches[0]

            if score >= 90:
                return candidate

        return value

    # ---------------------------------------------------------
    # LOCAL NLP ENTITY EXTRACTION
    # ---------------------------------------------------------

    def extract_local_entities(self, query: str) -> Dict[str, List[str]]:

        text = query.lower()

        entities = {
            "departments": [],
            "technologies": [],
            "skills": [],
            "topics": [],
            "categories": []
        }

        # Department detection (canonical names used in courses_data.py)
        department_aliases = {
            "cse": "CSE",
            "computer science": "CSE",
            "computer science engineering": "CSE",
            "it": "CSE",
            "information technology": "CSE",

            "ece": "ECE",
            "electronics": "ECE",
            "electronics and communication": "ECE",
            "acsc": "ECE",
            "aeronautical": "ECE",
            "aerospace": "ECE",
            "applied computing": "ECE",
            "control systems": "ECE",
            "communication": "ECE",

            "eee": "EEE",
            "electrical": "EEE",
            "electrical engineering": "EEE",
            "power engineering": "EEE",

            "mechanical": "Mechanical",
            "mechanical engineering": "Mechanical",
            "mech": "Mechanical",
            "mechatronics": "Mechatronics",

            "civil": "Civil",
            "civil engineering": "Civil",
            "construction": "Civil",

            "ai ds": "AI & DS",
            "ai ml": "AI & ML",
            "data science": "AI & DS",
            "artificial intelligence": "AI & DS"
        }

        for alias, department in department_aliases.items():

            if re.search(
                rf"\b{re.escape(alias)}\b",
                text
            ):
                if department not in entities["departments"]:
                    entities["departments"].append(department)

        # Alias/entity matching
        for alias, canonical in self.aliases.items():

            if alias in text:

                if canonical in [
                    "CSE",
                    "ECE",
                    "EEE",
                    "Mechanical",
                    "Civil"
                ]:
                    continue

                if canonical not in entities["technologies"]:
                    entities["technologies"].append(canonical)

        # Direct catalog matching
        for value in self.course_vocabulary:

            if len(value) < 3:
                continue

            if value.lower() in text:

                normalized = self.normalize(value)

                if normalized not in entities["technologies"]:
                    entities["technologies"].append(normalized)

        # Determine categories from matching courses
        for course in COURSES_DATA:

            searchable = " ".join(
                [
                    course.get("title", ""),
                    course.get("category", ""),
                    course.get("description", ""),
                    " ".join(course.get("skills", [])),
                    " ".join(course.get("technologies", [])),
                    " ".join(course.get("tags", []))
                ]
            ).lower()

            if any(
                entity.lower() in searchable
                for entity in entities["technologies"]
            ):

                category = course.get("category")

                if category and category not in entities["categories"]:
                    entities["categories"].append(category)

        return entities

    # ---------------------------------------------------------
    # LLAMA INTENT EXTRACTION
    # ---------------------------------------------------------

    def extract_llama_entities(self, query: str) -> Dict[str, Any]:

        if not self.api_key:
            return {}

        prompt = f"""
You are a course-search query analyzer.

Analyze the user's query and extract only information useful
for finding courses in a course recommendation platform.

Return ONLY valid JSON.

Required JSON format:

{{
  "intent": "course_search",
  "departments": [],
  "technologies": [],
  "skills": [],
  "topics": [],
  "categories": [],
  "difficulty": null,
  "learning_goal": null
}}

Rules:

- Do not invent entities.
- Extract multiple entities when the user mentions multiple concepts.
- Keep the user's requested technology/topic separate from their department.
- If the user says they are from Mechanical/ECE/EEE/Civil/CSE,
  identify the department.
- If the user asks for Python courses while being a Mechanical
  student, Python is the PRIMARY search intent and Mechanical
  is the user's contextual department.
- "I know Python and want AI" means Python is a known skill
  and AI is a learning goal.
- difficulty can be Beginner, Intermediate, Advanced, or null.
- learning_goal should be a short phrase or null.

Available course vocabulary:

{", ".join(self.course_vocabulary[:250])}

User query:

{query}

JSON:
"""

        try:

            response = requests.post(
                "https://api-inference.huggingface.co/models/"
                + self.model,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 300,
                        "temperature": 0.0,
                        "return_full_text": False
                    }
                },
                timeout=20
            )

            if response.status_code != 200:
                logger.warning(
                    "Llama entity extraction returned %s: %s",
                    response.status_code,
                    response.text[:300]
                )
                return {}

            data = response.json()

            if isinstance(data, list):
                generated = data[0].get(
                    "generated_text",
                    ""
                )
            elif isinstance(data, dict):
                generated = data.get(
                    "generated_text",
                    ""
                )
            else:
                generated = ""

            return self._extract_json(generated)

        except Exception as exc:

            logger.warning(
                "Llama entity extraction failed: %s",
                exc
            )

            return {}

    # ---------------------------------------------------------
    # JSON EXTRACTION
    # ---------------------------------------------------------

    def _extract_json(self, text: str) -> Dict[str, Any]:

        if not text:
            return {}

        match = re.search(
            r"\{.*\}",
            text,
            flags=re.DOTALL
        )

        if not match:
            return {}

        try:
            data = json.loads(match.group(0))

            if isinstance(data, dict):
                return data

        except json.JSONDecodeError:
            pass

        return {}

    # ---------------------------------------------------------
    # COMBINE LOCAL + LLAMA
    # ---------------------------------------------------------

    def understand(self, query: str) -> Dict[str, Any]:

        local = self.extract_local_entities(query)

        llama = self.extract_llama_entities(query)

        result = {
            "intent": "course_search",
            "departments": [],
            "technologies": [],
            "skills": [],
            "topics": [],
            "categories": [],
            "difficulty": None,
            "learning_goal": None
        }

        for field in [
            "departments",
            "technologies",
            "skills",
            "topics",
            "categories"
        ]:

            combined = []

            for value in local.get(field, []):
                normalized = self.normalize(str(value))

                if normalized not in combined:
                    combined.append(normalized)

            for value in llama.get(field, []) or []:

                normalized = self.normalize(str(value))

                if normalized not in combined:
                    combined.append(normalized)

            result[field] = combined

        difficulty = llama.get("difficulty")

        if difficulty in [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]:
            result["difficulty"] = difficulty

        result["learning_goal"] = llama.get(
            "learning_goal"
        )

        return result


query_understanding_service = QueryUnderstandingService()