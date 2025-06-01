import json
import random
from typing import Dict, List, Union
from vocab_data import HSK_VOCAB

class ChineseQuizGenerator:
    def __init__(self):
        self.hsk_vocab = HSK_VOCAB

    def generate_quiz(self, level: str, n_questions: int, mode: str) -> Dict:
        """Generate a quiz based on the given parameters"""
        if level not in self.hsk_vocab:
            raise ValueError(f"Invalid HSK level: {level}")

        words = self.hsk_vocab[level]
        selected_words = random.sample(words, n_questions)

        questions = []
        for i, word in enumerate(selected_words, 1):
            if mode == "JP→CN":
                prompt = word["jp"]
                answer = f"{word['cn']} ({word['pinyin']})"
            elif mode == "CN→JP":
                prompt = f"{word['cn']} ({word['pinyin']})"
                answer = word["jp"]
            else:
                raise ValueError(f"Invalid mode: {mode}")

            questions.append({
                "id": i,
                "prompt": prompt,
                "answer": answer
            })

        return {"questions": questions}

    def score_quiz(self, user_answers: List[Dict], questions: List[Dict]) -> Dict:
        """Score the user's answers and provide feedback"""
        correct_count = 0
        details = []
        
        for user_answer in user_answers:
            question = next(q for q in questions if q["id"] == user_answer["id"])
            is_correct = user_answer["user_answer"].strip().lower() == question["answer"].strip().lower()
            
            if not is_correct:
                details.append({
                    "id": user_answer["id"],
                    "correct": False,
                    "expected": question["answer"]
                })
            else:
                correct_count += 1
                details.append({"id": user_answer["id"], "correct": True})

        total = len(questions)
        percentage = (correct_count / total) * 100

        feedback = f"よく頑張りました！今日は{percentage:.1f}%でした。"
        if percentage < 70:
            feedback += "もう少し練習が必要かもしれませんね。"
        elif percentage < 90:
            feedback += "良いスコアですね！次も頑張りましょう！"
        else:
            feedback += "素晴らしい！完璧なスコアです！"

        return {
            "summary": {
                "score": correct_count,
                "total": total,
                "percentage": round(percentage, 1)
            },
            "details": details,
            "feedback": feedback
        }

# Example usage:
if __name__ == "__main__":
    generator = ChineseQuizGenerator()
    
    # Generate a quiz
    quiz = generator.generate_quiz(level="HSK3", n_questions=3, mode="CN→JP")
    print("Generated Quiz:")
    print(json.dumps(quiz, ensure_ascii=False, indent=2))
    
    # Example scoring
    user_answers = [
        {"id": 1, "user_answer": "今日"},
        {"id": 2, "user_answer": "助ける"},
        {"id": 3, "user_answer": "思う"}
    ]
    
    score = generator.score_quiz(user_answers, quiz["questions"])
    print("\nScoring Result:")
    print(json.dumps(score, ensure_ascii=False, indent=2))
