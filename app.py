import streamlit as st
from openai import OpenAI

# Streamlit Subheading
st.subheader("Convert Between SQL and Pandas Code", divider='rainbow')

# Input for OpenAI API Key
api_key = st.text_input("Enter your OpenAI API key", type="password")

# Function to convert SQL to Pandas
def sql_to_pandas(query, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are an expert in SQL and Pandas. For the given SQL query, provide the equivalent pandas statements."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

# Function to convert Pandas to SQL
def pandas_to_sql(query, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are an expert in SQL and Pandas. For the given pandas code, provide the equivalent SQL query."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

# User input to select conversion direction
conversion_type = st.radio(
    "Select the type of conversion you want to perform:",
    ('SQL to Pandas', 'Pandas to SQL')
)

# Input through Streamlit: SQL or Pandas code
input_text = st.text_area("Enter your code here")

# Streamlit button to generate response
if st.button("Convert Code"):
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
    elif not input_text:
        st.warning("Please enter the code to convert.")
    else:
        with st.spinner("Generating the equivalent code..."):
            if conversion_type == 'SQL to Pandas':
                response = sql_to_pandas(input_text, api_key)
            else:
                response = pandas_to_sql(input_text, api_key)
        st.write(response)
