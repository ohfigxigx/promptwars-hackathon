"""
SyllabusOS (CrunchTutor) — Flask application.
Production-ready backend with input validation, file-size checks, and error handling.
"""

import json
import logging
import os
import traceback

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

import agents

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB per image


# ── Helpers ──────────────────────────────────────────────────────────────────


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _require_fields(data: dict, fields: list[str]):
    """Raise ValueError if any required field is missing or blank."""
    missing = [f for f in fields if not data.get(f, "").strip()]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


# ── Routes ───────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/parse-syllabus", methods=["POST"])
def parse_syllabus():
    try:
        data = request.get_json(force=True)
        _require_fields(data, ["syllabus_text"])
        syllabus_text = data["syllabus_text"].strip()
        if len(syllabus_text) > 50_000:
            return _error("Syllabus text too long (max 50 000 characters).")
        result = agents.parse_syllabus(syllabus_text)
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("parse_syllabus error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to parse syllabus. Please try again.", 500)


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    try:
        data = request.get_json(force=True)
        _require_fields(data, ["topic", "subject"])
        result = agents.generate_diagnostic(
            topic=data["topic"].strip(),
            subject=data["subject"].strip(),
            education=data.get("education", "").strip() or "Undergraduate",
        )
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("diagnose error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to generate diagnostic. Please try again.", 500)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        _require_fields(data, ["topic", "subject", "qa_details"])
        result = agents.analyze_answers(
            topic=data["topic"].strip(),
            subject=data["subject"].strip(),
            qa_details=data["qa_details"].strip(),
        )
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("analyze error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to analyze answers. Please try again.", 500)


@app.route("/api/explain-story", methods=["POST"])
def explain_story():
    try:
        data = request.get_json(force=True)
        _require_fields(data, ["topic", "subject"])
        result = agents.explain_story(
            topic=data["topic"].strip(),
            subject=data["subject"].strip(),
            education=data.get("education", "").strip() or "Undergraduate",
        )
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("explain_story error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to generate explanation. Please try again.", 500)


@app.route("/api/variants", methods=["POST"])
def variants():
    try:
        data = request.get_json(force=True)
        _require_fields(data, ["question", "topic", "subject"])
        result = agents.generate_variants(
            question=data["question"].strip(),
            topic=data["topic"].strip(),
            subject=data["subject"].strip(),
            education=data.get("education", "").strip() or "Undergraduate",
        )
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("variants error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to generate variants. Please try again.", 500)


@app.route("/api/check-answer", methods=["POST"])
def check_answer():
    try:
        question = request.form.get("question", "").strip()
        topic = request.form.get("topic", "").strip()
        subject = request.form.get("subject", "").strip()

        if not question or not topic or not subject:
            return _error("Missing required fields: question, topic, subject.")

        # Check if an image file was uploaded
        image_file = request.files.get("image")

        if image_file and image_file.filename:
            # Validate image type
            if image_file.content_type not in ALLOWED_IMAGE_TYPES:
                return _error(
                    f"Unsupported image type: {image_file.content_type}. "
                    f"Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
                )
            image_bytes = image_file.read()
            if len(image_bytes) > MAX_IMAGE_BYTES:
                return _error("Image too large (max 5 MB).")
            if len(image_bytes) == 0:
                return _error("Uploaded image is empty.")

            result = agents.check_answer_image(
                question=question,
                topic=topic,
                subject=subject,
                image_bytes=image_bytes,
                mime_type=image_file.content_type,
            )
        else:
            answer = request.form.get("answer", "").strip()
            if not answer:
                return _error("Provide either a typed answer or upload an image.")
            result = agents.check_answer_text(
                question=question,
                answer=answer,
                topic=topic,
                subject=subject,
            )
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("check_answer error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to check answer. Please try again.", 500)


@app.route("/api/summary-book", methods=["POST"])
def summary_book():
    try:
        data = request.get_json(force=True)
        _require_fields(data, ["subject", "content"])
        result = agents.generate_summary(
            subject=data["subject"].strip(),
            education=data.get("education", "").strip() or "Undergraduate",
            scope=data.get("scope", "chapter").strip(),
            content=data["content"].strip(),
        )
        return jsonify(result)
    except ValueError as e:
        return _error(str(e))
    except Exception as e:
        logger.error("summary_book error: %s\n%s", e, traceback.format_exc())
        return _error("Failed to generate summary. Please try again.", 500)


# ── Entry point (development) ───────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
