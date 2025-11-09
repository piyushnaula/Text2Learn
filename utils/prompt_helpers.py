"""
Helper functions for working with AI prompts and responses
"""
import re
from typing import Dict, List, Optional

def clean_text(text: str) -> str:
    """
    Clean and normalize text output from AI
    
    Args:
        text: Raw text from AI
        
    Returns:
        Cleaned text
    """
    text = re.sub(r'\s+', ' ', text)
    
    text = text.strip()
    
    return text


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown text
    
    Args:
        text: Markdown text containing code blocks
        
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    code_blocks = []
    
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        language = match[0] if match[0] else 'text'
        code = match[1].strip()
        code_blocks.append({
            'language': language,
            'code': code
        })
    
    return code_blocks


def format_quiz_for_display(quiz_data: List[Dict]) -> str:
    """
    Format quiz data for display in Streamlit
    
    Args:
        quiz_data: List of quiz question dictionaries
        
    Returns:
        Formatted string for display
    """
    formatted = ""
    
    for i, question in enumerate(quiz_data, 1):
        formatted += f"\n**Question {i}:** {question.get('question', '')}\n\n"
        formatted += f"A) {question.get('option_a', '')}\n"
        formatted += f"B) {question.get('option_b', '')}\n"
        formatted += f"C) {question.get('option_c', '')}\n"
        formatted += f"D) {question.get('option_d', '')}\n\n"
        formatted += f"**Correct Answer:** {question.get('correct_answer', '')}\n"
        
        if question.get('explanation'):
            formatted += f"**Explanation:** {question.get('explanation', '')}\n"
        
        formatted += "\n---\n"
    
    return formatted


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix


def validate_course_outline(outline: Dict[str, List[str]]) -> bool:
    """
    Validate that a course outline has the correct structure
    
    Args:
        outline: Course outline dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(outline, dict):
        return False
    
    if len(outline) < 3 or len(outline) > 10:
        return False
    
    for module_title, subtopics in outline.items():
        if not isinstance(module_title, str) or not module_title:
            return False
        
        if not isinstance(subtopics, list) or len(subtopics) < 2:
            return False
        
        for subtopic in subtopics:
            if not isinstance(subtopic, str) or not subtopic:
                return False
    
    return True


def create_progress_summary(completed: int, total: int) -> Dict[str, any]:
    """
    Create a progress summary
    
    Args:
        completed: Number of completed items
        total: Total number of items
        
    Returns:
        Dictionary with progress information
    """
    percentage = (completed / total * 100) if total > 0 else 0
    
    return {
        'completed': completed,
        'total': total,
        'remaining': total - completed,
        'percentage': round(percentage, 1),
        'progress_bar': f"{'█' * int(percentage / 10)}{'░' * (10 - int(percentage / 10))}"
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    filename = filename.replace(' ', '_')
    
    max_length = 100
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time for text
    
    Args:
        text: Text to analyze
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    
    return max(1, round(minutes))


def extract_key_topics(text: str, num_topics: int = 5) -> List[str]:
    """
    Extract key topics from text (simple implementation)
    
    Args:
        text: Text to analyze
        num_topics: Number of topics to extract
        
    Returns:
        List of key topics
    """
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                   'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been',
                   'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                   'could', 'should', 'may', 'might', 'must', 'can', 'this', 
                   'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 
                   'we', 'they', 'what', 'which', 'who', 'when', 'where', 
                   'why', 'how'}
    
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    word_freq = {}
    for word in words:
        if word not in common_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:num_topics]]


if __name__ == "__main__":
    messy_text = "  This   is   a   test   with   extra    spaces  "
    print("Cleaned text:", clean_text(messy_text))
    
    long_text = "This is a very long text that needs to be truncated for display purposes"
    print("Truncated:", truncate_text(long_text, 30))
    
    progress = create_progress_summary(7, 10)
    print("\nProgress Summary:")
    print(f"  Completed: {progress['completed']}/{progress['total']}")
    print(f"  Percentage: {progress['percentage']}%")
    print(f"  Progress: {progress['progress_bar']}")
    
    sample_text = "Python is a high-level, interpreted programming language. " * 50
    reading_time = estimate_reading_time(sample_text)
    print(f"\nEstimated reading time: {reading_time} minutes")
