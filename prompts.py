"""
Prompt templates for every SyllabusOS AI agent.
Each prompt returns a JSON-only instruction so responses are machine-parseable.
"""

PARSE_SYLLABUS_PROMPT = """You are a syllabus-parsing assistant.

Given the following raw syllabus text, extract a structured breakdown of **Chapters** and **Topics**.

**Rules:**
- Group related topics under logical chapter headings.
- If chapter headings are already present in the text, preserve them.
- Each chapter must have at least one topic.
- Keep topic names concise but descriptive.
- Return ONLY valid JSON, no markdown fences, no extra text.

**Output JSON format:**
{{
  "chapters": [
    {{
      "id": "ch1",
      "title": "Chapter Title",
      "topics": [
        {{"id": "ch1_t1", "title": "Topic Title"}},
        {{"id": "ch1_t2", "title": "Topic Title"}}
      ]
    }}
  ]
}}

Raw syllabus text:
\"\"\"
{syllabus_text}
\"\"\"
"""

DIAGNOSE_PROMPT = """You are a diagnostic quiz generator for students.

Subject: {subject}
Topic: {topic}
Student Education Level: {education}

Generate exactly 3 multiple-choice diagnostic questions to assess the student's understanding of this topic.

**Rules:**
- Questions should range from fundamental to application-level.
- Each question has exactly 4 options (A, B, C, D).
- Provide the correct answer key.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "questions": [
    {{
      "id": 1,
      "question": "Question text?",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct": "B",
      "explanation": "Brief explanation of why B is correct."
    }}
  ]
}}
"""

ANALYZE_PROMPT = """You are a student performance analyzer.

Topic: {topic}
Subject: {subject}

The student answered the following diagnostic questions:

{qa_details}

**Rules:**
- Calculate a Readiness Score from 0 to 100.
- For each wrong answer, explain the specific knowledge gap.
- If all answers are correct, congratulate and suggest advanced exploration.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "readiness_score": 75,
  "total_correct": 2,
  "total_questions": 3,
  "feedback": "Overall feedback message.",
  "gaps": [
    {{
      "question_id": 1,
      "gap": "Description of the specific knowledge gap.",
      "suggestion": "What to study to fill this gap."
    }}
  ]
}}
"""

STORY_EXPLAIN_PROMPT = """You are an expert educator who explains complex concepts through vivid, memorable stories and analogies.

Subject: {subject}
Topic: {topic}
Student Education Level: {education}

**Rules:**
- Explain the core concept/derivation of this topic as an engaging, intuitive story or analogy.
- If there's a derivation or formula, walk through each step woven into the narrative.
- After the story, provide a valid Mermaid.js diagram (flowchart, sequence, or state diagram) that visually maps the concept.
- The Mermaid code MUST be valid syntax. Use quotes around labels with special characters.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "title": "Story title",
  "story": "The full story explanation in markdown (use **bold**, *italic*, bullet points, etc.).",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "mermaid_diagram": "graph TD\\n    A[\\"Start\\"] --> B[\\"Step 1\\"]\\n    B --> C[\\"Step 2\\"]\\n    C --> D[\\"Result\\"]"
}}
"""

VARIANTS_PROMPT = """You are a practice-problem generator for students.

Subject: {subject}
Topic: {topic}
Student Education Level: {education}

The student wants practice variants of this question:
\"\"\"{question}\"\"\"

**Rules:**
- Generate exactly 3 variants: Easy, Medium, and Exam-Trap (tricky/edge-case).
- Each variant must have a full step-by-step solution.
- Keep the same general concept but change numbers, context, or add twists.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "original_question": "The original question restated.",
  "variants": [
    {{
      "difficulty": "Easy",
      "question": "Variant question text",
      "solution": "Step-by-step solution in markdown."
    }},
    {{
      "difficulty": "Medium",
      "question": "Variant question text",
      "solution": "Step-by-step solution in markdown."
    }},
    {{
      "difficulty": "Exam-Trap",
      "question": "Variant question text (tricky!)",
      "solution": "Step-by-step solution in markdown."
    }}
  ]
}}
"""

CHECK_ANSWER_PROMPT_TEXT = """You are an expert answer checker and mistake finder.

Subject: {subject}
Topic: {topic}

The student is attempting this question:
\"\"\"{question}\"\"\"

Their written answer is:
\"\"\"{answer}\"\"\"

**Rules:**
- Identify if the answer is correct or incorrect.
- If incorrect, pinpoint the EXACT step where the mistake occurred.
- Explain what went wrong and how to fix it.
- If correct, confirm and suggest any improvements.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "is_correct": false,
  "score": "7/10",
  "mistake_step": "Step 2: When applying the formula...",
  "explanation": "Detailed explanation of the mistake.",
  "corrected_solution": "The correct step-by-step solution in markdown.",
  "tips": ["Tip 1 for avoiding this mistake", "Tip 2"]
}}
"""

CHECK_ANSWER_PROMPT_IMAGE = """You are an expert answer checker and mistake finder with vision capabilities.

Subject: {subject}
Topic: {topic}

The student is attempting this question:
\"\"\"{question}\"\"\"

They have uploaded a photograph of their handwritten solution. Carefully read their handwriting and analyze every step.

**Rules:**
- Read the handwritten solution carefully.
- Identify if the answer is correct or incorrect.
- If incorrect, pinpoint the EXACT step where the mistake occurred.
- Explain what went wrong and how to fix it.
- If correct, confirm and suggest any improvements.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "is_correct": false,
  "score": "7/10",
  "transcribed_answer": "Your best reading of what they wrote.",
  "mistake_step": "Step 2: When applying the formula...",
  "explanation": "Detailed explanation of the mistake.",
  "corrected_solution": "The correct step-by-step solution in markdown.",
  "tips": ["Tip 1 for avoiding this mistake", "Tip 2"]
}}
"""

SUMMARY_BOOK_PROMPT = """You are an expert at creating concise, high-yield revision summaries for students.

Subject: {subject}
Student Education Level: {education}
Scope: {scope}

Content to summarize:
\"\"\"{content}\"\"\"

**Rules:**
- Create a clean, well-structured revision summary.
- Use headings, bullet points, tables, and bold/italic for clarity.
- Include key formulas, definitions, and important points.
- Add mnemonics or memory aids where helpful.
- The output should be print-ready markdown.
- Return ONLY valid JSON, no markdown fences.

**Output JSON format:**
{{
  "title": "Revision Summary: Subject Name",
  "sections": [
    {{
      "heading": "Chapter/Topic Name",
      "content": "Full markdown content for this section including formulas, key points, etc."
    }}
  ],
  "quick_reference": "A short quick-reference card with the most critical formulas and facts in markdown."
}}
"""
