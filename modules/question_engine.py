import google.generativeai as genai
from config.settings import GEMINI_API_KEY
import json
import re

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_questions(domain, difficulty, num_questions=5):
    """Generate mix of MCQ and text questions."""

    mcq_count  = num_questions // 2
    text_count = num_questions - mcq_count

    questions = []

    # ── Generate MCQ questions ────────────────────────────────
    mcq_prompt = f"""
Generate {mcq_count} multiple choice questions for domain: {domain}
Difficulty: {difficulty}

Return ONLY a valid JSON array like this:
[
  {{
    "question": "What does Python's GIL stand for?",
    "options": ["Global Interpreter Lock", "General Input Loop", "Global Input Library", "General Interpreter Lock"],
    "answer": "Global Interpreter Lock",
    "type": "mcq"
  }}
]

Return ONLY the JSON array. No extra text, no markdown, no backticks.
"""

    try:
        mcq_response = model.generate_content(mcq_prompt)
        raw = mcq_response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        mcq_list = json.loads(raw)
        for q in mcq_list:
            q["type"] = "mcq"
        questions.extend(mcq_list)
    except Exception as e:
        print(f"MCQ generation error: {e}")

    # ── Generate text questions ───────────────────────────────
    text_prompt = f"""
Generate {text_count} descriptive interview questions for domain: {domain}
Difficulty: {difficulty}

Return ONLY a numbered list:
1. Question one here
2. Question two here

No extra text.
"""

    try:
        text_response = model.generate_content(text_prompt)
        raw = text_response.text.strip()
        for line in raw.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                question = line.split(".", 1)[-1].strip()
                questions.append({
                    "question": question,
                    "type"    : "text"
                })
    except Exception as e:
        print(f"Text question generation error: {e}")

    return questions


def evaluate_answer(question, answer, domain):
    """Use Gemini to score a text answer out of 10."""
    prompt = f"""
You are an expert interviewer for {domain}.

Question: {question}
Candidate's Answer: {answer}

Score this answer out of 10 and give brief feedback.
Return ONLY valid JSON like this:
{{"score": 7, "feedback": "Good answer but missing X detail."}}

Return ONLY the JSON. No extra text.
"""
    try:
        response = model.generate_content(prompt)
        raw      = response.text.strip()
        raw      = re.sub(r"```json|```", "", raw).strip()
        result   = json.loads(raw)
        return {"score": result.get("score", 5), "feedback": result.get("feedback", "No feedback")}
    except Exception as e:
        print(f"Evaluation error: {e}")
        return {"score": 5, "feedback": "Could not evaluate answer"}