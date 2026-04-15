import json
import google.generativeai as genai
from config.settings import GEMINI_API_KEY

# Connect to Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_questions(domain, difficulty, num_questions=5):
    """Ask Gemini to generate interview questions."""

    prompt = f"""
    Generate {num_questions} interview questions for the domain: {domain}
    Difficulty level: {difficulty}
    
    Return ONLY a numbered list like this:
    1. Question one here
    2. Question two here
    
    No extra text, no explanations.
    """

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Convert numbered text into a Python list
        lines = raw.split("\n")
        questions = []
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit():
                question = line.split(".", 1)[-1].strip()
                questions.append(question)

        return questions

    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def evaluate_answer(question, answer, domain):
    """Ask Gemini to evaluate the answer and return a score and feedback."""
    prompt = f"""
    You are an expert technical interviewer in the '{domain}' domain.
    Evaluate the candidate's answer to the following question.
    
    Question: {question}
    Candidate's Answer: {answer}
    
    Instructions:
    1. Score the answer out of 10 based on accuracy, completeness, and clarity.
    2. Provide a short, constructive feedback (1-2 sentences).
    3. Return ONLY a valid JSON object in this exact format:
    {{
        "score": <number>,
        "feedback": "<string>"
    }}
    Do not add any markdown formatting or explanations outside the JSON.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up any markdown block wrappers if Gemini still includes them
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return result

    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return {"score": 0, "feedback": "AI evaluation failed."}