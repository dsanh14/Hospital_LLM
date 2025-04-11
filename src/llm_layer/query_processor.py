from typing import Dict, Any
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

from data_layer.data_manager import DataManager
from clarification.ambiguity_detector import AmbiguityDetector

load_dotenv()

class QueryProcessor:
    def __init__(self, data_manager: DataManager, ambiguity_detector: AmbiguityDetector):
        self.data_manager = data_manager
        self.ambiguity_detector = ambiguity_detector
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Load the schema for context
        self.schema = self.data_manager.get_schema()
        
        # Create the prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions about hospital operations data.
            You have access to the following data tables and their schemas:
            
            {schema}
            
            When answering questions:
            1. Be precise and factual
            2. Include relevant numbers and statistics
            3. Explain your reasoning
            4. If the query is ambiguous, ask for clarification
            5. Format your response in a clear, structured way
            """),
            ("human", "{query}")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query and return the result"""
        # Check for ambiguity
        clarification_needed = self.ambiguity_detector.detect_ambiguity(query)
        if clarification_needed:
            return {
                "answer": "I need some clarification to answer your question accurately.",
                "clarification_questions": clarification_needed,
                "explanation": "The query contains ambiguous terms that need to be clarified."
            }
        
        # Format the schema for the prompt
        schema_str = self._format_schema_for_prompt()
        
        # Process the query
        response = self.chain.run(
            query=query,
            schema=schema_str
        )
        
        # Extract relevant data
        data = self._extract_relevant_data(query)
        
        return {
            "answer": response,
            "data": data,
            "explanation": "The answer is based on the current hospital operations data."
        }
    
    def _format_schema_for_prompt(self) -> str:
        """Format the schema into a string for the prompt"""
        schema_str = ""
        for table_name, table_info in self.schema["tables"].items():
            schema_str += f"\nTable: {table_name}\n"
            schema_str += f"Description: {table_info['description']}\n"
            schema_str += "Columns:\n"
            for col_name, col_info in table_info["columns"].items():
                schema_str += f"  - {col_name} ({col_info['type']}): {col_info['description']}\n"
        return schema_str
    
    def _extract_relevant_data(self, query: str) -> Any:
        """Extract relevant data based on the query"""
        # This is a placeholder - actual implementation would:
        # 1. Parse the query to determine which tables and columns are needed
        # 2. Execute appropriate data queries
        # 3. Return the relevant data
        return None 