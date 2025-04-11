import streamlit as st
import os
from dotenv import load_dotenv
from llm_layer.query_processor import QueryProcessor
from data_layer.data_manager import DataManager
from clarification.ambiguity_detector import AmbiguityDetector
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

def main():
    st.set_page_config(
        page_title="Hospital Operations Query System",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Hospital Operations Query System")
    st.markdown("""
    Ask questions about hospital operations data in natural language.
    Examples:
    - "What's the current ICU occupancy rate?"
    - "Show me the census trends for the last month"
    - "Which units are at capacity?"
    """)
    
    # Initialize components
    data_manager = DataManager()
    ambiguity_detector = AmbiguityDetector()
    query_processor = QueryProcessor(data_manager, ambiguity_detector)
    
    # User input
    user_query = st.text_input("Enter your question:", placeholder="e.g., What's the current ICU occupancy rate?")
    
    if user_query:
        try:
            # Process query
            with st.spinner("Processing your query..."):
                result = query_processor.process_query(user_query)
                
                # Display results
                st.subheader("Answer")
                st.write(result['answer'])
                
                if result.get('explanation'):
                    with st.expander("See explanation"):
                        st.write(result['explanation'])
                
                if result.get('data'):
                    st.subheader("Supporting Data")
                    st.dataframe(result['data'])
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Error processing query: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 