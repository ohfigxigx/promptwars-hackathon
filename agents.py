"""
AI Agent functions — each calls Gemini 2.5 Flash via the official google-genai SDK.
"""

import json
import os
import re
import logging

from google import genai
from google.genai import types
from dotenv import load_dotenv

from prompts import (
    PARSE_SYLLABUS_PROMPT,
    DIAGNOSE_PROMPT,
    ANALYZE_PROMPT,
    STORY_EXPLAIN_PROMPT,
    VARIANTS_PROMPT,
    CHECK_ANSWER_PROMPT_TEXT,
    CHECK_ANSWER_PROMPT_IMAGE,
    SUMMARY_BOOK_PROMPT,
)

load_dotenv()
logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _get_client() -> genai.Client:
    """Return a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in environment.")
    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> dict:
    """Extract JSON from model output, stripping markdown fences if present."""
    text = text.strip()
    # Remove ```json ... ``` wrappers
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    return json.loads(text)


def _call_gemini(prompt: str) -> dict:
    """Send a text prompt to Gemini and parse the JSON response."""
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
        ),
    )
    return _extract_json(response.text)


def _call_gemini_multimodal(prompt: str, image_bytes: bytes, mime_type: str) -> dict:
    """Send text + image to Gemini and parse the JSON response."""
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_text(prompt),
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=8192,
        ),
    )
    return _extract_json(response.text)


# ── Agent Functions ──────────────────────────────────────────────────────────


def parse_syllabus(syllabus_text: str) -> dict:
    """Parse raw syllabus text into structured chapters and topics."""
    prompt = PARSE_SYLLABUS_PROMPT.format(syllabus_text=syllabus_text)
    return _call_gemini(prompt)


def generate_diagnostic(topic: str, subject: str, education: str) -> dict:
    """Generate 3 diagnostic MCQ questions for a topic."""
    prompt = DIAGNOSE_PROMPT.format(
        topic=topic, subject=subject, education=education
    )
    return _call_gemini(prompt)


def analyze_answers(
    topic: str, subject: str, qa_details: str
) -> dict:
    """Analyze student answers and return readiness score + gaps."""
    prompt = ANALYZE_PROMPT.format(
        topic=topic, subject=subject, qa_details=qa_details
    )
    return _call_gemini(prompt)


def explain_story(topic: str, subject: str, education: str) -> dict:
    """Explain a topic via story/analogy with a Mermaid diagram."""
    prompt = STORY_EXPLAIN_PROMPT.format(
        topic=topic, subject=subject, education=education
    )
    return _call_gemini(prompt)


def generate_variants(
    question: str, topic: str, subject: str, education: str
) -> dict:
    """Generate 3 difficulty-graded variants of a question."""
    prompt = VARIANTS_PROMPT.format(
        question=question, topic=topic, subject=subject, education=education
    )
    return _call_gemini(prompt)


def check_answer_text(
    question: str, answer: str, topic: str, subject: str
) -> dict:
    """Check a typed answer for mistakes."""
    prompt = CHECK_ANSWER_PROMPT_TEXT.format(
        question=question, answer=answer, topic=topic, subject=subject
    )
    return _call_gemini(prompt)


def check_answer_image(
    question: str, topic: str, subject: str,
    image_bytes: bytes, mime_type: str
) -> dict:
    """Check a handwritten answer (photo) for mistakes using vision."""
    prompt = CHECK_ANSWER_PROMPT_IMAGE.format(
        question=question, topic=topic, subject=subject
    )
    return _call_gemini_multimodal(prompt, image_bytes, mime_type)


def generate_summary(
    subject: str, education: str, scope: str, content: str
) -> dict:
    """Generate a revision summary book."""
    prompt = SUMMARY_BOOK_PROMPT.format(
        subject=subject, education=education, scope=scope, content=content
    )
    return _call_gemini(prompt)
