# AI Knowledge Graph Course Recommendation & Learning Assistant

A personalized technical course discovery and recommendation platform powered by **Neo4j Knowledge Graph**, **MongoDB Activity Logging**, **Flask REST APIs**, **Hugging Face Llama NLU**, and a modern **React UI**.

---

## 🌟 Architecture & System Design

```
                      ┌────────────────────────────────────────┐
                      │              React UI                  │
                      │  (Explore, Dash, Chatbot, Graph Viz)  │
                      └───────────────────┬────────────────────┘
                                          │ Axios HTTP
                                          ▼
                      ┌────────────────────────────────────────┐
                      │            Flask REST API              │
                      │   (Auth, Courses, Recs, Chat, Graph)   │
                      └────────┬──────────┬───────────┬────────┘
                               │          │           │
            ┌──────────────────┘          │           └──────────────────┐
            ▼                             ▼                              ▼
┌───────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│     MongoDB           │   │     Neo4j Graph           │   │ HuggingFace / Llama API   │
│ - User Profiles       │   │ - Graph Traversal         │   │ - Grounded NLU            │
│ - Activity Logs       │   │ - Skill/Tech Relations    │   │ - Explanations            │
│ - Wishlists/Enrolls   │   │ - Dynamic Interest Scores │   │ - No Course Hallucination │
└───────────────────────┘   └───────────────────────────┘   └───────────────────────────┘
```

---

## 📂 Project Structure

```
Knowledge Graph/
├── backend/
│   ├── app.py                      # Flask Application entry point
│   ├── config.py                   # Environment config loader
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Backend environment template
│   ├── models/
│   │   ├── user_model.py
│   │   └── course_model.py
│   ├── services/
│   │   ├── neo4j_service.py        # Neo4j Cypher queries & sub-graph builder
│   │   ├── mongodb_service.py      # MongoDB CRUD & catalog search
│   │   ├── recommendation_engine.py# Hybrid recommendation scoring & explanations
│   │   ├── interest_engine.py      # Dynamic interaction weighting & interest graph
│   │   └── llama_service.py        # Hugging Face Llama 1B integration with database grounding
│   └── routes/
│       ├── auth_routes.py          # /api/auth (Login, Register)
│       ├── course_routes.py        # /api/courses (Catalog, Search)
│       ├── recommendation_routes.py# /api/recommendations (Personalized, Department, Trending)
│       ├── interaction_routes.py   # /api/interactions (Clicks, Views, Wishlist, Enroll)
│       ├── chat_routes.py          # /api/chat (AI Learning Assistant)
│       ├── user_routes.py          # /api/user (Profile, History, Learning Paths)
│       └── graph_routes.py         # /api/knowledge-graph (Visual Graph Data)
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css               # Vanilla CSS Design System (Glassmorphic LMS theme)
│       ├── services/
│       │   └── api.js              # Axios REST Client
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── CourseCard.jsx      # Card with rating, price & graph explanation banner
│       │   ├── RecommendationSection.jsx
│       │   ├── SearchBar.jsx
│       │   ├── Filters.jsx
│       │   ├── Chatbot.jsx          # Floating AI Assistant popover
│       │   └── KnowledgeGraphVisualizer.jsx # Interactive SVG graph canvas
│       └── pages/
│           ├── Home.jsx             # Dashboard with Interest Graph metrics
│           ├── Explore.jsx          # Multi-filter search catalog
│           ├── CourseDetails.jsx    # Full metadata, skills taught & related nodes
│           ├── Login.jsx
│           ├── Register.jsx
│           ├── Profile.jsx
│           ├── Wishlist.jsx
│           ├── MyLearning.jsx
│           ├── KnowledgeGraphPage.jsx
│           └── LearningPathPage.jsx # Career roadmaps (AI, Full Stack, ECE, Mech, Civil)
│
├── database/
│   ├── neo4j/
│   │   ├── schema.cypher          # Constraints & indexes
│   │   └── seed.cypher
│   ├── courses_data.py             # 50+ rich technical courses across 12+ engineering domains
│   └── seed_all.py                 # Automated Python seeder for Neo4j & MongoDB
│
└── README.md
```

---

## 💻 Setup & Installation Instructions

### 1. Database Setup
#### Neo4j:
- Ensure Neo4j is running locally (default: `neo4j://127.0.0.1:7687`).
- Database name: `CourseRecommendationDB`
- Username: `neo4j`

#### MongoDB:
- Ensure MongoDB server is running locally (default: `mongodb://localhost:27017/`).
- Database name: `course_recommendation`

### 2. Backend Setup (Flask)
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### Environment File Configuration
Create a `.env` file in `backend/`:
```env
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=CourseRecommendationDB

MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=course_recommendation

HUGGINGFACE_API_KEY=your_hf_api_key_optional
HUGGINGFACE_MODEL=meta-llama/Llama-3.2-1B-Instruct
FLASK_PORT=5000
```

#### Database Seeding
Populate Neo4j graph nodes and MongoDB catalog:
```bash
python ../database/seed_all.py
```

#### Run Flask Server
```bash
python app.py
```
The Flask API will run on `http://localhost:5000`.

---

### 3. Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## 🧪 Demo Test Credentials

You can use the built-in quick-autofill buttons on the login page:

| Department | Email | Password | Interests |
| :--- | :--- | :--- | :--- |
| **CSE** | `alex.cse@example.com` | `password123` | React, Node.js, AI |
| **ECE** | `priya.ece@example.com` | `password123` | Embedded Systems, Microcontrollers, VLSI |
| **Mechanical** | `david.mech@example.com` | `password123` | ANSYS, FEA, SOLIDWORKS |
| **EEE** | `rohan.eee@example.com` | `password123` | MATLAB, Power Electronics, Solar PV |
| **Civil** | `emily.civil@example.com` | `password123` | Revit, STAAD Pro, BIM |

---

## 🧠 Recommendation Algorithm & Knowledge Graph Logic

The system uses a **Hybrid Knowledge Graph Recommendation Algorithm**:

$$\text{Score} = w_{\text{dept}} \cdot S_{\text{dept}} + w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{tech}} \cdot S_{\text{tech}} + w_{\text{interest}} \cdot S_{\text{interest}} + w_{\text{graph\_path}} \cdot S_{\text{graph\_path}} + w_{\text{rating}} \cdot S_{\text{rating}}$$

### Dynamic Interaction Weighting Strategy:
- **Search Query**: +1.0 interest score weight
- **Course View**: +2.0 interest score weight
- **Course Click**: +2.5 interest score weight
- **Wishlist Save**: +4.0 interest score weight
- **Enrollment**: +6.0 interest score weight
- **Completion**: +8.0 interest score weight

### Explainable Recommendations:
For every recommended course, Cypher graph paths are traversed and rendered on course cards:
> *"Recommended because you recently searched for React and viewed JavaScript courses connected in the Knowledge Graph"*

---

## 🤖 Conversational AI Assistant (Llama 1B)
- Floating assistant at bottom-right corner.
- **Grounding**: Retrieves actual catalog courses and graph context before calling Meta Llama 1B Instruct.
- **Zero Hallucination**: AI generates conversational guidance while attaching real interactive database course cards below responses.
