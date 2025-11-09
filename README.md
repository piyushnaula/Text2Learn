# Text 2 Learn

**Created by: Piyush Naula**

An AI-powered course generator that transforms any topic into a structured learning experience complete with lessons, curated videos, and adaptive quizzes.

---

## Overview

Text 2 Learn unites Groq large language models, a Streamlit interface, and PostgreSQL/SQLite storage to deliver end-to-end course authoring. Provide a topic and the platform produces a multi-module syllabus, detailed lessons on demand, recommended videos, and contextual quizzes—then caches everything for instant reuse.

---

## Key Features

- Automated course outlines with 5–6 modules and coherent subtopics
- On-demand lesson authoring (≈1,000 words) with reading time estimates
- AI-generated quizzes that include feedback and progress tracking
- YouTube tutorial discovery with relevance ranking
- Persistent caching to reduce API cost and latency
- Responsive Streamlit interface inspired by ChatGPT aesthetics

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| UI | Streamlit |
| AI | Groq API (Llama 3.x, Mixtral) |
| Database | PostgreSQL or SQLite |
| ORM | SQLAlchemy |
| Video Search | YouTube Data API v3 |
| Configuration | python-dotenv |

---

## Prerequisites

1. Python 3.8 or newer
2. Groq API key from [console.groq.com](https://console.groq.com/)
3. YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)
4. PostgreSQL server (optional when using SQLite)

---

## Quick Start

```bash
git clone https://github.com/piyushnaula/Text2Learn.git
cd ai_course_generator
python -m venv venv
venv\Scripts\activate   
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GROQ_API_KEY=your_groq_api_key
YOUTUBE_API_KEY=your_youtube_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/ai_course_generator
DEBUG=True
```

### Database choices

- **SQLite (fastest setup):** `DATABASE_URL=sqlite:///ai_courses.db`
- **PostgreSQL:** Create the `ai_course_generator` database locally or via a cloud provider and keep the connection string in `.env`.

---

## Run the Application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. To change the port, run `streamlit run app.py --server.port 8502`.

---

## Using Text 2 Learn

1. Start the app and log in with any username (it creates the profile if absent).
2. Enter a topic such as “Digital Marketing Fundamentals” and generate a course (≈15 seconds).
3. Expand modules to view subtopics, then open a subtopic to trigger lesson generation.
4. Explore the **Content**, **Video Tutorial**, and **Quiz** tabs for each subtopic.
5. Track completion via status icons and the progress bar; cached data loads instantly on revisits.

Tips for best results:

- Choose focused topics (“Intro to Python Programming”) instead of vague or ultra-niche prompts.
- Complete quizzes to reinforce learning and review explanations.
- Pair lessons with recommended videos for a blended learning experience.

---

## Architecture Snapshot

- **Streamlit Frontend:** Session handling, layout, interactive widgets.
- **Services Layer:** `ai_service.py`, `youtube_service.py`, and `db_service.py` encapsulate AI calls, video search, and persistence.
- **Database Layer:** SQLAlchemy models map to users, courses, modules, subtopics, quizzes, and progress tables.
- **Prompt Templates:** Stored in `prompts/` for outlines, lesson content, search keywords, and quizzes.

```
Frontend (Streamlit)
      │
Application Services
 (AI | YouTube | DB)
      │
Data Storage (PostgreSQL / SQLite)
```

---

## AI Workflow

1. Generate course outlines with few-shot and chain-of-thought prompting.
2. Cache outlines in the database for reuse.
3. Produce lesson content on demand with adaptive depth based on topic.
4. Derive YouTube keywords, fetch candidates, and select the top tutorial.
5. Build quizzes with explanations and store results for progress tracking.

Tunable parameters in `services/ai_service.py`:

- `self.model` controls the Groq model (default `llama-3.3-70b-versatile`).
- Temperature defaults: outline 0.7, content 0.7, keywords 0.5, quizzes 0.6.

---

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `FATAL: password authentication failed` | Verify PostgreSQL credentials or switch to SQLite. |
| `ModuleNotFoundError: No module named 'streamlit'` | Activate the virtual environment and reinstall requirements. |
| Groq authentication errors | Confirm the API key in `.env` and available quota. |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` or free the port. |
| YouTube videos missing | Ensure API key validity and quota; some videos block embedding. |
| Slow first load | Expected during first-generation; cached content loads instantly afterward. |

---

## Performance Snapshot

- Course outline: 10–15 seconds
- First lesson generation: 20–30 seconds
- Cached lesson reload: < 1 second
- Quiz generation: 8–12 seconds
- Typical memory usage: 200–400 MB
- Storage per course: ≈50 KB

---

## Future Enhancements

- User authentication with secure credentials
- Progress dashboard and analytics
- Text-to-speech lessons
- PDF export for offline study
- Gamified achievements
- AI-powered topic recommendations
- Collaborative learning spaces
- Multi-language course generation
- Mobile companion app

---

## Example Topics

- Technical: “Machine Learning Basics”, “Web Development with React”
- Business: “Personal Finance Management”, “Entrepreneurship 101”
- Creative: “Photography Essentials”, “Content Writing Mastery”
- Academic: “Introduction to Psychology”, “World History Overview”

---

## Support & Contact

- Create GitHub issues for bugs or feature requests.
- Email Piyush Naula for collaboration and inquiries.
