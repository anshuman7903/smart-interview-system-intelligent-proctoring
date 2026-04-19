import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.question_engine import generate_questions

print("Testing question generation...")
questions = generate_questions("Technical (Python)", "Easy", 4)

print(f"\nTotal questions generated: {len(questions)}")
for i, q in enumerate(questions, 1):
    print(f"\n--- Question {i} ---")
    print(q)