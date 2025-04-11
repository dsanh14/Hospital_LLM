from typing import List, Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class AmbiguityDetector:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_NAME", "gemini-2.0-flashlite"),
            temperature=float(os.getenv("TEMPERATURE", "0.1")),
            convert_system_message_to_human=True
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
            
            If you detect ambiguity, respond with "Clarification needed:" followed by numbered questions.
            If the query is clear, respond with "No clarification needed."
            """),
            ("human", "{query}")
        ])
        
        self.chain = self.prompt_template | self.llm
    
    def detect_ambiguity(self, query: str) -> Optional[List[str]]:
        """Detect ambiguity in a query and return clarification questions if needed"""
        response = self.chain.invoke({"query": query})
        
        # Parse the response to extract clarification questions
        try:
            if "Clarification needed:" in response.content:
                questions = []
                for line in response.content.split("\n")[1:]:
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