import os
from groq import Groq
from typing import Dict, List, Tuple
import re


class AIService:
    """Service for interacting with Groq API to generate course content"""
    
    def __init__(self, api_key: str):
        """Initialize Groq client with API key"""
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
    def _load_prompt_template(self, template_name: str) -> str:
        """Load a prompt template from the prompts directory"""
        prompt_path = os.path.join("prompts", template_name)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"Prompt template '{template_name}' not found")
    
    def _call_groq(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Make a call to Groq API with the given prompt"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def generate_course_outline(self, topic: str) -> Dict[str, List[str]]:
        """
        Generate a complete course outline with modules and subtopics
        
        Args:
            topic: The course topic
            
        Returns:
            Dictionary with module titles as keys and lists of subtopics as values
        """
        template = self._load_prompt_template("course_outline_prompt.txt")
        prompt = template.format(topic=topic)
        
        response = self._call_groq(prompt, temperature=0.7, max_tokens=3000)
        
        return self._parse_course_outline(response)
    
    def _parse_course_outline(self, outline_text: str) -> Dict[str, List[str]]:
        """Parse the AI-generated outline into a structured dictionary"""
        modules = {}
        current_module = None
        
        lines = outline_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Module"):
                if ':' in line:
                    current_module = line.split(':', 1)[1].strip()
                    modules[current_module] = []
            elif line.startswith('-') and current_module:
                subtopic = line[1:].strip() 
                if subtopic:
                    modules[current_module].append(subtopic)
        
        return modules
    
    def generate_subtopic_content(self, course_title: str, module_title: str, 
                                   subtopic_title: str, previous_subtopics: List[str] = None) -> str:
        """
        Generate detailed content for a specific subtopic
        
        Args:
            course_title: The course title
            module_title: The module title
            subtopic_title: The subtopic title
            previous_subtopics: List of previously covered subtopic titles in this module
            
        Returns:
            Detailed markdown-formatted content
        """
        template = self._load_prompt_template("subtopic_content_prompt.txt")
        
        if previous_subtopics and len(previous_subtopics) > 0:
            prev_text = "\n".join([f"- {title}" for title in previous_subtopics])
        else:
            prev_text = "None (This is the first subtopic in this module)"
        
        prompt = template.format(
            course_title=course_title,
            module_title=module_title,
            subtopic_title=subtopic_title,
            previous_subtopics=prev_text
        )
        
        content = self._call_groq(prompt, temperature=0.7, max_tokens=4000)
        return content
    
    def generate_youtube_keywords(self, course_title: str, module_title: str, 
                                   subtopic_title: str) -> str:
        """
        Generate optimized YouTube search keywords for a subtopic
        
        Args:
            course_title: The course title
            module_title: The module title
            subtopic_title: The subtopic title
            
        Returns:
            Comma-separated keywords
        """
        template = self._load_prompt_template("youtube_keywords_prompt.txt")
        prompt = template.format(
            course_title=course_title,
            module_title=module_title,
            subtopic_title=subtopic_title
        )
        
        keywords = self._call_groq(prompt, temperature=0.5, max_tokens=200)
        return keywords.strip()
    
    def generate_quiz(self, course_title: str, module_title: str, 
                      subtopic_title: str, content_summary: str = "") -> List[Dict]:
        """
        Generate quiz questions for a subtopic
        
        Args:
            course_title: The course title
            module_title: The module title
            subtopic_title: The subtopic title
            content_summary: Brief summary of the content (optional)
            
        Returns:
            List of quiz questions with options and answers
        """
        template = self._load_prompt_template("quiz_generation_prompt.txt")
        
        if not content_summary:
            content_summary = f"Content about {subtopic_title}"
        
        content_summary = content_summary.replace('{', '{{').replace('}', '}}')
        
        prompt = template.format(
            course_title=course_title,
            module_title=module_title,
            subtopic_title=subtopic_title,
            content_summary=content_summary
        )
        
        quiz_text = self._call_groq(prompt, temperature=0.6, max_tokens=3000)
        return self._parse_quiz(quiz_text)
    
    def _parse_quiz(self, quiz_text: str) -> List[Dict]:
        """Parse AI-generated quiz into structured format"""
        questions = []
        lines = quiz_text.strip().split('\n')
        
        current_question = {}
        reading_explanation = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_question and self._is_valid_quiz(current_question):
                    questions.append(current_question.copy())
                    current_question = {}
                    reading_explanation = False
                continue
            
            if re.match(r'^Question\s+\d+:?', line, re.IGNORECASE):
                if current_question and self._is_valid_quiz(current_question):
                    questions.append(current_question.copy())
                current_question = {}
                reading_explanation = False
                continue
            
            option_match = re.match(r'^([A-D])[\):]\s*(.+)$', line)
            if option_match:
                option_letter = option_match.group(1)
                option_text = option_match.group(2).strip()
                current_question[f'option_{option_letter.lower()}'] = option_text
                reading_explanation = False
            
            elif re.match(r'^Correct Answer:?\s*([A-D])', line, re.IGNORECASE):
                answer_match = re.search(r'([A-D])', line)
                if answer_match:
                    current_question['correct_answer'] = answer_match.group(1).upper()
                reading_explanation = False
            
            elif re.match(r'^Explanation:', line, re.IGNORECASE):
                explanation = line.split(':', 1)[1].strip() if ':' in line else ""
                current_question['explanation'] = explanation
                reading_explanation = True
            
            elif reading_explanation and current_question.get('explanation'):
                current_question['explanation'] += " " + line
            
            elif not current_question.get('question') and not line.startswith('**'):
                current_question['question'] = line
            elif current_question.get('question') and not any(key.startswith('option_') for key in current_question.keys()):
                current_question['question'] += " " + line
        
        if current_question and self._is_valid_quiz(current_question):
            questions.append(current_question.copy())
        
        return questions
    
    def _is_valid_quiz(self, quiz: Dict) -> bool:
        """Check if a quiz question has all required fields"""
        required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        return all(quiz.get(field) for field in required_fields)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment variables")
        exit(1)
    
    ai_service = AIService(api_key)
    
    print("Generating course outline for 'Introduction to Machine Learning'...")
    outline = ai_service.generate_course_outline("Introduction to Machine Learning")
    
    print("\nCourse Outline:")
    for module, subtopics in outline.items():
        print(f"\n{module}")
        for subtopic in subtopics:
            print(f"  - {subtopic}")
