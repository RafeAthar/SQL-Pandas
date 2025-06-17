"""
SQL-Pandas Converter App
A Streamlit application for converting between SQL and Pandas code using OpenAI's API.
"""

import streamlit as st
import openai
from openai import OpenAI
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "gpt-3.5-turbo-0125"
MAX_TOKENS = 1000
TEMPERATURE = 0.1

class SQLPandasConverter:
    """Handles conversion between SQL and Pandas code using OpenAI API."""
    
    def __init__(self, api_key: str):
        """Initialize the converter with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
    
    def _make_api_call(self, system_prompt: str, user_query: str) -> Optional[str]:
        """Make API call to OpenAI with error handling."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            return response.choices[0].message.content
        except openai.APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            st.error(f"OpenAI API returned an error: {e}")
            return None
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI Connection Error: {e}")
            st.error(f"Failed to connect to OpenAI API: {e}")
            return None
        except openai.RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}")
            st.error(f"OpenAI API request exceeded rate limit: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error(f"An unexpected error occurred: {e}")
            return None
    
    def sql_to_pandas(self, sql_query: str) -> Optional[str]:
        """Convert SQL query to equivalent Pandas code."""
        system_prompt = """You are an expert in SQL and Pandas. 
        For the given SQL query, provide the equivalent pandas statements.
        Include necessary imports and assume the data is in a DataFrame called 'df'.
        Provide clean, readable code with comments explaining complex operations."""
        
        return self._make_api_call(system_prompt, sql_query)
    
    def pandas_to_sql(self, pandas_code: str) -> Optional[str]:
        """Convert Pandas code to equivalent SQL query."""
        system_prompt = """You are an expert in SQL and Pandas.
        For the given pandas code, provide the equivalent SQL query.
        Assume the DataFrame operations are performed on a table with the same name.
        Provide clean, readable SQL with proper formatting."""
        
        return self._make_api_call(system_prompt, pandas_code)

def validate_inputs(api_key: str, input_text: str) -> Tuple[bool, str]:
    """Validate user inputs and return validation status and message."""
    if not api_key.strip():
        return False, "Please enter your OpenAI API key."
    
    if not input_text.strip():
        return False, "Please enter the code to convert."
    
    if len(input_text) > 5000:
        return False, "Input text is too long. Please limit to 5000 characters."
    
    return True, ""

def display_result(result: str, conversion_type: str):
    """Display the conversion result with proper formatting."""
    if result:
        st.success("Conversion completed successfully!")
        
        # Determine the language for syntax highlighting
        language = "python" if conversion_type == "SQL to Pandas" else "sql"
        
        st.code(result, language=language)
        
        # Add copy button functionality
        st.button("📋 Copy to Clipboard", 
                 help="Click to copy the result to clipboard",
                 key="copy_button")
    else:
        st.error("Failed to generate conversion. Please check your API key and try again.")

def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="SQL-Pandas Converter",
        page_icon="🔄",
        layout="wide"
    )
    
    # Header
    st.title("🔄 SQL-Pandas Converter")
    st.markdown("Convert between SQL queries and Pandas operations using AI")
    st.divider()
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to use the conversion service"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "This app uses OpenAI's GPT model to convert between SQL and Pandas code. "
            "Make sure you have a valid OpenAI API key."
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Input")
        
        # Conversion type selection
        conversion_type = st.radio(
            "Select conversion type:",
            options=["SQL to Pandas", "Pandas to SQL"],
            help="Choose the type of conversion you want to perform"
        )
        
        # Input text area
        placeholder_text = (
            "SELECT * FROM users WHERE age > 25"
            if conversion_type == "SQL to Pandas"
            else "df[df['age'] > 25]"
        )
        
        input_text = st.text_area(
            "Enter your code:",
            height=300,
            placeholder=placeholder_text,
            help=f"Enter your {'SQL query' if conversion_type == 'SQL to Pandas' else 'Pandas code'} here"
        )
        
        # Character count
        st.caption(f"Characters: {len(input_text)}/5000")
    
    with col2:
        st.header("Output")
        
        # Convert button
        if st.button("🚀 Convert Code", type="primary"):
            # Validate inputs
            is_valid, error_message = validate_inputs(api_key, input_text)
            
            if not is_valid:
                st.warning(error_message)
            else:
                # Perform conversion
                with st.spinner("Converting code... This may take a few seconds."):
                    try:
                        converter = SQLPandasConverter(api_key)
                        
                        if conversion_type == "SQL to Pandas":
                            result = converter.sql_to_pandas(input_text)
                        else:
                            result = converter.pandas_to_sql(input_text)
                        
                        # Display result
                        display_result(result, conversion_type)
                        
                    except Exception as e:
                        st.error(f"An error occurred during conversion: {e}")
                        logger.error(f"Conversion error: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Tip:** For best results, provide clear and well-formatted code. "
        "The converter works best with standard SQL queries and common Pandas operations."
    )

if __name__ == "__main__":
    main()
