from typing import Dict, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

from data_layer.data_manager import DataManager
from clarification.ambiguity_detector import AmbiguityDetector

load_dotenv()

class QueryProcessor:
    def __init__(self, data_manager: DataManager, ambiguity_detector: AmbiguityDetector):
        self.data_manager = data_manager
        self.ambiguity_detector = ambiguity_detector
        
        # Configure Gemini with direct API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(model_name)
        
        # Load the schema for context
        self.schema = self.data_manager.get_schema()
        
        # Create the prompt template
        self.system_prompt = """You are a helpful assistant that answers questions about hospital operations data.
You have access to the following data tables and their schemas:

{schema}

When answering questions:
1. Be precise and factual
2. Include relevant numbers and statistics
3. Explain your reasoning
4. If the query is ambiguous, ask for clarification
5. Format your response in a clear, structured way

Based on the data available in the tables, provide a clear and concise answer."""
    
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
        
        # Get relevant data based on the query
        data = self._extract_relevant_data(query)
        
        # Format the schema and data for the prompt
        schema_str = self._format_schema_for_prompt()
        data_str = self._format_data_for_prompt(data) if data is not None else "No relevant data found."
        
        # Create the full prompt
        full_prompt = f"{self.system_prompt.format(schema=schema_str)}\n\nAvailable Data:\n{data_str}\n\nQuestion: {query}\nAnswer:"
        
        # Process the query
        response = self.model.generate_content(full_prompt)
        
        return {
            "answer": response.text,
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
    
    def _format_data_for_prompt(self, data: pd.DataFrame) -> str:
        """Format DataFrame for inclusion in the prompt"""
        if data is None or data.empty:
            return "No data available."
        return f"Data Preview:\n{data.head().to_string()}"
    
    def _extract_relevant_data(self, query: str) -> pd.DataFrame:
        """Extract relevant data based on the query"""
        query = query.lower()
        
        # Handle census trends query
        if "census" in query and "trend" in query and "last month" in query:
            sql = """
            SELECT date, unit_id, patient_count, admissions, discharges
            FROM census
            WHERE date >= date('now', '-30 days')
            ORDER BY date DESC, unit_id
            """
            return self.data_manager.execute_query(sql)
        
        # Handle ICU occupancy query
        if "icu" in query and ("occupancy" in query or "capacity" in query):
            sql = """
            SELECT unit_name,
                   total_beds,
                   occupied_beds,
                   ROUND(CAST(occupied_beds AS FLOAT) / total_beds * 100, 1) as occupancy_rate
            FROM icu_stats
            WHERE timestamp >= datetime('now', '-1 day')
            ORDER BY timestamp DESC
            LIMIT 3
            """
            return self.data_manager.execute_query(sql)
        
        # Handle units at capacity query
        if "capacity" in query or "full" in query:
            sql = """
            SELECT unit_name,
                   total_beds,
                   occupied_beds,
                   ROUND(CAST(occupied_beds AS FLOAT) / total_beds * 100, 1) as occupancy_rate
            FROM icu_stats
            WHERE timestamp >= datetime('now', '-1 day')
                AND (CAST(occupied_beds AS FLOAT) / total_beds) >= 0.9
            ORDER BY occupancy_rate DESC
            """
            return self.data_manager.execute_query(sql)
        
        return None 