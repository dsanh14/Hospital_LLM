from typing import List, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class AmbiguityDetector:
    def __init__(self):
        # Configure Gemini with direct API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(model_name)
        
        # Store example questions that should be considered clear
        self.example_questions = {
            "What's the current ICU occupancy rate?",
            "Show me the census trends for the last month",
            "Which units are at capacity?"
        }
        
        self.system_prompt = """You are an expert at detecting ambiguity in questions about hospital operations.
Your task is to identify any ambiguous terms or missing context in the query that would prevent
giving a precise answer about hospital data.

Common sources of ambiguity in hospital queries include:
- Unspecified time periods beyond standard ranges (e.g., "a while ago", "some time")
- Unclear unit references (e.g., "the ICU" when there are multiple ICUs)
- Vague metrics without context (e.g., "busy", "crowded")
- Missing context about patient types or conditions

Note: Standard time periods like "current", "today", "last month", "last week" are considered clear.

If you detect ambiguity, respond with "Clarification needed:" followed by numbered questions.
If the query is clear or uses standard time periods, respond with "No clarification needed." """
    
    def detect_ambiguity(self, query: str) -> Optional[List[str]]:
        """Detect ambiguity in a query and return clarification questions if needed"""
        # If the query is an example question, consider it clear
        if query.strip() in self.example_questions:
            return None
            
        # If the query is similar to example questions but with minor variations, consider it clear
        if self._is_similar_to_example(query):
            return None
        
        full_prompt = f"{self.system_prompt}\n\nQuestion: {query}\nResponse:"
        response = self.model.generate_content(full_prompt)
        
        # Parse the response to extract clarification questions
        try:
            if "Clarification needed:" in response.text:
                questions = []
                for line in response.text.split("\n")[1:]:
                    if line.strip() and line[0].isdigit():
                        questions.append(line.split(". ", 1)[1])
                return questions if questions else None
            return None
        except Exception as e:
            print(f"Error parsing ambiguity detection response: {e}")
            return None
    
    def _is_similar_to_example(self, query: str) -> bool:
        """Check if a query is similar to example questions"""
        query = query.lower().strip()
        
        # Common time period patterns that should be considered clear
        clear_time_periods = [
            "current", "today", "last month", "last week",
            "this month", "this week", "yesterday"
        ]
        
        # Check if query contains clear time periods
        if any(period in query for period in clear_time_periods):
            return True
            
        return False
    
    def _is_ambiguous_term(self, term: str) -> bool:
        """Check if a term is potentially ambiguous"""
        ambiguous_terms = {
            "recent", "next", "that",
            "busy", "crowded", "full", "empty", "high", "low",
            "some", "few", "many", "several"
        }
        return term.lower() in ambiguous_terms 