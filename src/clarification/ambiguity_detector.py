from typing import List, Optional
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class AmbiguityDetector:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at detecting ambiguity in questions about hospital operations.
            Your task is to identify any ambiguous terms or missing context in the query that would prevent
            giving a precise answer about hospital data.
            
            Common sources of ambiguity in hospital queries include:
            - Unspecified time periods (e.g., "current", "recent")
            - Unclear unit references (e.g., "the ICU" when there are multiple ICUs)
            - Vague metrics (e.g., "busy", "crowded")
            - Missing context about patient types or conditions
            
            If you detect ambiguity, provide specific clarification questions that would help resolve it.
            If the query is clear, return an empty list.
            """),
            ("human", "{query}")
        ])
    
    def detect_ambiguity(self, query: str) -> Optional[List[str]]:
        """Detect ambiguity in a query and return clarification questions if needed"""
        response = self.llm.predict(
            self.prompt_template.format_messages(query=query)[0].content
        )
        
        # Parse the response to extract clarification questions
        # The LLM should return either an empty list or a list of questions
        try:
            # The response should be in a format like:
            # "Clarification needed:\n1. Which ICU unit are you referring to?\n2. What time period are you interested in?"
            if "Clarification needed:" in response:
                questions = []
                for line in response.split("\n")[1:]:
                    if line.strip() and line[0].isdigit():
                        questions.append(line.split(". ", 1)[1])
                return questions if questions else None
            return None
        except Exception as e:
            print(f"Error parsing ambiguity detection response: {e}")
            return None
    
    def _is_ambiguous_term(self, term: str) -> bool:
        """Check if a term is potentially ambiguous"""
        ambiguous_terms = {
            "current", "recent", "last", "next", "this", "that",
            "busy", "crowded", "full", "empty", "high", "low",
            "the", "our", "your", "their"
        }
        return term.lower() in ambiguous_terms 