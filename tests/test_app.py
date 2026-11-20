"""
Tests for SyllabusOS Flask application.
All Gemini API calls are mocked to run without an API key.
"""

import json
import io
import pytest
from unittest.mock import patch, MagicMock

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


# ── Health check ─────────────────────────────────────────────────────────────


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"SyllabusOS" in resp.data


# ── Parse Syllabus ───────────────────────────────────────────────────────────


MOCK_PARSED = {
    "chapters": [
        {
            "id": "ch1",
            "title": "Arrays",
            "topics": [
                {"id": "ch1_t1", "title": "Introduction to Arrays"},
                {"id": "ch1_t2", "title": "Array Operations"},
            ],
        }
    ]
}


@patch("agents.parse_syllabus", return_value=MOCK_PARSED)
def test_parse_syllabus_success(mock_agent, client):
    resp = client.post(
        "/api/parse-syllabus",
        json={"syllabus_text": "Unit 1: Arrays - Introduction, Operations"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "chapters" in data
    assert len(data["chapters"]) == 1
    mock_agent.assert_called_once()


def test_parse_syllabus_missing_field(client):
    resp = client.post("/api/parse-syllabus", json={"syllabus_text": ""})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


# ── Diagnose ─────────────────────────────────────────────────────────────────


MOCK_DIAGNOSTIC = {
    "questions": [
        {
            "id": 1,
            "question": "What is an array?",
            "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
            "correct": "A",
            "explanation": "An array is a data structure.",
        }
    ]
}


@patch("agents.generate_diagnostic", return_value=MOCK_DIAGNOSTIC)
def test_diagnose_success(mock_agent, client):
    resp = client.post(
        "/api/diagnose",
        json={"topic": "Arrays", "subject": "Data Structures"},
    )
    assert resp.status_code == 200
    assert "questions" in resp.get_json()


def test_diagnose_missing_fields(client):
    resp = client.post("/api/diagnose", json={"topic": ""})
    assert resp.status_code == 400


# ── Analyze ──────────────────────────────────────────────────────────────────


MOCK_ANALYSIS = {
    "readiness_score": 67,
    "total_correct": 2,
    "total_questions": 3,
    "feedback": "Good effort!",
    "gaps": [],
}


@patch("agents.analyze_answers", return_value=MOCK_ANALYSIS)
def test_analyze_success(mock_agent, client):
    resp = client.post(
        "/api/analyze",
        json={
            "topic": "Arrays",
            "subject": "Data Structures",
            "qa_details": "Q1: A (correct), Q2: B (wrong), Q3: C (correct)",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "readiness_score" in data


# ── Explain Story ────────────────────────────────────────────────────────────


MOCK_STORY = {
    "title": "The Array Kingdom",
    "story": "Once upon a time...",
    "key_takeaways": ["Arrays are contiguous"],
    "mermaid_diagram": "graph TD\n    A-->B",
}


@patch("agents.explain_story", return_value=MOCK_STORY)
def test_explain_story_success(mock_agent, client):
    resp = client.post(
        "/api/explain-story",
        json={"topic": "Arrays", "subject": "Data Structures"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "story" in data
    assert "mermaid_diagram" in data


# ── Variants ─────────────────────────────────────────────────────────────────


MOCK_VARIANTS = {
    "original_question": "Find the max element.",
    "variants": [
        {"difficulty": "Easy", "question": "Q1", "solution": "S1"},
        {"difficulty": "Medium", "question": "Q2", "solution": "S2"},
        {"difficulty": "Exam-Trap", "question": "Q3", "solution": "S3"},
    ],
}


@patch("agents.generate_variants", return_value=MOCK_VARIANTS)
def test_variants_success(mock_agent, client):
    resp = client.post(
        "/api/variants",
        json={
            "question": "Find the max element in an array.",
            "topic": "Arrays",
            "subject": "Data Structures",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["variants"]) == 3


# ── Check Answer (text) ─────────────────────────────────────────────────────


MOCK_CHECK = {
    "is_correct": False,
    "score": "5/10",
    "mistake_step": "Step 2",
    "explanation": "You forgot to handle the edge case.",
    "corrected_solution": "Correct solution here.",
    "tips": ["Always check boundaries"],
}


@patch("agents.check_answer_text", return_value=MOCK_CHECK)
def test_check_answer_text(mock_agent, client):
    resp = client.post(
        "/api/check-answer",
        data={
            "question": "Find max element",
            "answer": "Loop through and compare",
            "topic": "Arrays",
            "subject": "Data Structures",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "is_correct" in data


@patch("agents.check_answer_image", return_value=MOCK_CHECK)
def test_check_answer_image(mock_agent, client):
    # Create a fake image file
    fake_image = (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100), "solution.png")
    resp = client.post(
        "/api/check-answer",
        data={
            "question": "Find max element",
            "topic": "Arrays",
            "subject": "Data Structures",
            "image": fake_image,
        },
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200


def test_check_answer_missing_fields(client):
    resp = client.post(
        "/api/check-answer",
        data={"question": "", "topic": "", "subject": ""},
    )
    assert resp.status_code == 400


# ── Summary Book ─────────────────────────────────────────────────────────────


MOCK_SUMMARY = {
    "title": "Revision Summary: Data Structures",
    "sections": [{"heading": "Arrays", "content": "Key points..."}],
    "quick_reference": "Array: O(1) access, O(n) search",
}


@patch("agents.generate_summary", return_value=MOCK_SUMMARY)
def test_summary_book_success(mock_agent, client):
    resp = client.post(
        "/api/summary-book",
        json={
            "subject": "Data Structures",
            "content": "Chapter 1: Arrays - introduction, operations, searching",
            "scope": "chapter",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sections" in data
