from modules.question_engine import generate_questions

questions = generate_questions("Technical (Python)", "Medium", 3)

for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")