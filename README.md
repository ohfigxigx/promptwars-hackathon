# 📚 SyllabusOS (CrunchTutor)

> **Personalized AI Learning Agent** — PS04 Challenge Entry

SyllabusOS is a full-stack AI-powered study companion that takes any syllabus and transforms it into a personalized, interactive learning experience using five specialized AI agents powered by Google Gemini 2.5 Flash.

---

## ✨ Features

### 1. Onboarding & Syllabus Manager
- Quick setup: Name, Education/Degree, and paste any raw syllabus
- **One-click sample syllabi** (Data Structures, Engineering Physics) for instant testing
- AI-powered syllabus parsing into structured Chapters & Topics
- Interactive sidebar with add/remove topics, mastered toggle, and **live study timer**
- Zero-database persistence via `localStorage`

### 2. Five Core AI Agent Tabs

| Tab | Agent | What It Does |
|-----|-------|-------------|
| 🩺 **Diagnostic** | Gap Finder | 3-question MCQ → Readiness Score + weak spots |
| 📖 **Story & Diagram** | Story Teller | Concept explained as a memorable story + Mermaid.js diagram |
| 🔢 **Variants** | Problem Generator | 3 practice variants (Easy / Medium / Exam-Trap) with solutions |
| ✅ **Answer Checker** | Mistake Finder | Text or **photo upload** (multimodal vision) → exact mistake pinpointing |
| 📓 **Revision Book** | Summary Writer | Printable high-yield revision summary (chapter or full syllabus) |

### 3. Production Quality
- Modular backend: `app.py`, `agents.py`, `prompts.py`
- Input validation, file-size limits, error handling
- ARIA labels, keyboard navigation, loading states
- Pytest test suite with mocked Gemini calls
- Production Dockerfile with Gunicorn

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/apikey)

### Setup

```bash
# Clone the repo
git clone <repo-url>
cd promptwars-hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the app
python app.py
```

Open **http://localhost:8080** in your browser.

### Run Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker

```bash
# Build
docker build -t syllabusOS .

# Run (pass your API key)
docker run -p 8080:8080 -e GEMINI_API_KEY=your-key-here syllabusOS
```

---

## ☁️ Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/syllabusOS

# Deploy
gcloud run deploy syllabusOS \
  --image gcr.io/YOUR_PROJECT/syllabusOS \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key-here \
  --port 8080 \
  --memory 512Mi \
  --timeout 120
```

---

## 📁 Project Structure

```
├── app.py                 # Flask routes & server
├── agents.py              # Gemini API agent functions
├── prompts.py             # Prompt templates for each agent
├── templates/
│   └── index.html         # Single-page frontend (Tailwind + Mermaid.js)
├── tests/
│   └── test_app.py        # Pytest suite with mocked API calls
├── requirements.txt       # Python dependencies
├── Dockerfile             # Production container
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask |
| AI | Google Gemini 2.5 Flash via `google-genai` SDK |
| Frontend | HTML5, Tailwind CSS (CDN), Mermaid.js (CDN) |
| Persistence | Browser `localStorage` (zero-DB) |
| Production | Gunicorn, Docker, Cloud Run |
| Testing | pytest with unittest.mock |

---

## 📄 License

MIT
