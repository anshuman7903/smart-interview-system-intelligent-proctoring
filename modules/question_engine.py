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