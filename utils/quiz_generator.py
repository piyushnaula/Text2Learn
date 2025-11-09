"""
Utility functions for quiz generation and evaluation
"""
from typing import Dict, List, Optional
import random


def shuffle_quiz_options(quiz: Dict) -> Dict:
    """
    Shuffle quiz options while maintaining the correct answer
    
    Args:
        quiz: Quiz dictionary with question and options
        
    Returns:
        Quiz with shuffled options
    """
    options = {
        'A': quiz.get('option_a', ''),
        'B': quiz.get('option_b', ''),
        'C': quiz.get('option_c', ''),
        'D': quiz.get('option_d', '')
    }
    
    correct_answer = quiz.get('correct_answer', 'A')
    correct_text = options.get(correct_answer, '')
    
    option_texts = list(options.values())
    random.shuffle(option_texts)
    
    new_quiz = quiz.copy()
    new_quiz['option_a'] = option_texts[0]
    new_quiz['option_b'] = option_texts[1]
    new_quiz['option_c'] = option_texts[2]
    new_quiz['option_d'] = option_texts[3]
    
    for letter, text in zip(['A', 'B', 'C', 'D'], option_texts):
        if text == correct_text:
            new_quiz['correct_answer'] = letter
            break
    
    return new_quiz


def calculate_quiz_score(answers: Dict[int, str], quizzes: List[Dict]) -> Dict:
    """
    Calculate quiz score based on user answers
    
    Args:
        answers: Dictionary mapping question index to user answer (A, B, C, or D)
        quizzes: List of quiz dictionaries with correct answers
        
    Returns:
        Score summary dictionary
    """
    if not quizzes:
        return {
            'score': 0,
            'total': 0,
            'percentage': 0,
            'correct': 0,
            'incorrect': 0
        }
    
    correct = 0
    total = len(quizzes)
    
    for i, quiz in enumerate(quizzes):
        user_answer = answers.get(i, '').upper()
        correct_answer = quiz.get('correct_answer', '').upper()
        
        if user_answer == correct_answer:
            correct += 1
    
    percentage = (correct / total * 100) if total > 0 else 0
    
    return {
        'score': correct,
        'total': total,
        'percentage': round(percentage, 1),
        'correct': correct,
        'incorrect': total - correct
    }


def generate_quiz_feedback(score_data: Dict) -> str:
    """
    Generate encouraging feedback based on quiz score
    
    Args:
        score_data: Score data from calculate_quiz_score
        
    Returns:
        Feedback message
    """
    percentage = score_data['percentage']
    
    if percentage >= 90:
        return "Outstanding! You've mastered this topic!"
    elif percentage >= 75:
        return "Great job! You have a solid understanding of the material."
    elif percentage >= 60:
        return "Good work! You're making progress. Review the areas you missed."
    elif percentage >= 40:
        return "Keep studying! You're on the right track but need more practice."
    else:
        return "Don't give up! Review the content and try again."


def format_quiz_result(quiz: Dict, user_answer: str, show_explanation: bool = True) -> Dict:
    """
    Format quiz result for display
    
    Args:
        quiz: Quiz dictionary
        user_answer: User's selected answer
        show_explanation: Whether to include explanation
        
    Returns:
        Formatted result dictionary
    """
    correct_answer = quiz.get('correct_answer', '').upper()
    user_answer = user_answer.upper()
    is_correct = user_answer == correct_answer
    
    result = {
        'question': quiz.get('question', ''),
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct,
        'options': {
            'A': quiz.get('option_a', ''),
            'B': quiz.get('option_b', ''),
            'C': quiz.get('option_c', ''),
            'D': quiz.get('option_d', '')
        }
    }
    
    if show_explanation and quiz.get('explanation'):
        result['explanation'] = quiz.get('explanation', '')
    
    return result


def get_quiz_difficulty(quiz: Dict) -> str:
    """
    Estimate quiz difficulty based on question characteristics
    
    Args:
        quiz: Quiz dictionary
        
    Returns:
        Difficulty level: 'easy', 'medium', or 'hard'
    """
    question = quiz.get('question', '')
    
    word_count = len(question.split())
    
    complex_keywords = ['analyze', 'evaluate', 'compare', 'contrast', 'why', 'explain']
    has_complex_keyword = any(keyword in question.lower() for keyword in complex_keywords)
    
    if word_count > 20 or has_complex_keyword:
        return 'hard'
    elif word_count > 12:
        return 'medium'
    else:
        return 'easy'


def validate_quiz_structure(quiz: Dict) -> bool:
    """
    Validate that a quiz has all required fields
    
    Args:
        quiz: Quiz dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    
    for field in required_fields:
        if field not in quiz or not quiz[field]:
            return False
    
    if quiz['correct_answer'].upper() not in ['A', 'B', 'C', 'D']:
        return False
    
    return True


def create_quiz_statistics(all_results: List[Dict]) -> Dict:
    """
    Create statistics from multiple quiz attempts
    
    Args:
        all_results: List of quiz result dictionaries
        
    Returns:
        Statistics dictionary
    """
    if not all_results:
        return {
            'total_attempts': 0,
            'average_score': 0,
            'best_score': 0,
            'improvement': 0
        }
    
    scores = [result['percentage'] for result in all_results]
    
    return {
        'total_attempts': len(all_results),
        'average_score': round(sum(scores) / len(scores), 1),
        'best_score': max(scores),
        'worst_score': min(scores),
        'latest_score': scores[-1],
        'improvement': round(scores[-1] - scores[0], 1) if len(scores) > 1 else 0
    }


def generate_study_recommendations(quiz_results: List[Dict], quizzes: List[Dict]) -> List[str]:
    """
    Generate study recommendations based on quiz performance
    
    Args:
        quiz_results: List of user's quiz results
        quizzes: List of quiz questions
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    incorrect_indices = []
    for i, result in enumerate(quiz_results):
        if not result.get('is_correct', False):
            incorrect_indices.append(i)
    
    if len(incorrect_indices) == 0:
        recommendations.append("Perfect score! You can move on to the next topic.")
    elif len(incorrect_indices) <= 2:
        recommendations.append("Review the questions you missed and their explanations.")
        recommendations.append("You're ready to proceed, but a quick review wouldn't hurt!")
    else:
        recommendations.append("Review the lesson content thoroughly before retaking the quiz.")
        recommendations.append("Focus on the concepts in questions you answered incorrectly.")
        recommendations.append("Try the quiz again after reviewing.")
    
    return recommendations


if __name__ == "__main__":
    sample_quiz = {
        'question': 'What is the capital of France?',
        'option_a': 'London',
        'option_b': 'Berlin',
        'option_c': 'Paris',
        'option_d': 'Madrid',
        'correct_answer': 'C',
        'explanation': 'Paris is the capital and most populous city of France.'
    }
    
    print("Quiz valid:", validate_quiz_structure(sample_quiz))
    
    print("Difficulty:", get_quiz_difficulty(sample_quiz))
    
    quizzes = [sample_quiz] * 5
    answers = {0: 'C', 1: 'C', 2: 'A', 3: 'C', 4: 'B'}  
    score = calculate_quiz_score(answers, quizzes)
    print("\nScore:", score)
    print("Feedback:", generate_quiz_feedback(score))
