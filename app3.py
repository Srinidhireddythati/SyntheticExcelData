import os
import pandas as pd
import streamlit as st
import openai
from prompts import ANALYZER_SYSTEM_PROMPT, GENERATOR_SYSTEM_PROMPT  # Import your prompts

# Function to read the Excel file
def read_excel(file):
    data = pd.read_excel(file)
    return data

# Create the Analyzer Agent
def analyzer_agent(sample_data, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": ANALYZER_SYSTEM_PROMPT  # Use the prompt from prompts.py
            },
            {
                "role": "user",
                "content": f"Analyze the following data:\n{sample_data}"
            }
        ],
        max_tokens=400,
        temperature=0.1
    )
    return response.choices[0].message['content']

# Create the Generator Agent
def generator_agent(analysis_result, sample_data, openai_api_key, input_data):
    openai.api_key = openai_api_key
    num_rows_to_generate = len(input_data)+1 # Generate the same number of rows as the input data size
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": GENERATOR_SYSTEM_PROMPT  # Use the prompt from prompts.py
            },
            {
                "role": "user",
                "content": f"Generate {num_rows_to_generate} rows of data based on the following analysis:\n{analysis_result}\nSample data:\n{sample_data}"
            }
        ],
        max_tokens=400,
        temperature=1.0
    )
    return response.choices[0].message['content']

# Streamlit app
def main():
    st.title("Excel Data Analyzer and Generator")

    # Input for API key
    openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

    # File uploader for Excel files
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

    if uploaded_file and openai_api_key:
        # Read the sample data from the uploaded Excel file
        sample_data = read_excel(uploaded_file)
        sample_data_str = sample_data.to_csv(index=False)

        st.write("Launching team of Agents...")

        # Analyze the sample data using the Analyzer Agent
        analysis_result = analyzer_agent(sample_data_str, openai_api_key)
        st.subheader("Analyzer Agent Output:")
        st.write(analysis_result)

        st.write("Generating new data...")

        # Generate the same number of rows as the input data size
        generated_data = generator_agent(analysis_result, sample_data_str, openai_api_key, sample_data)

        # Convert generated data to a DataFrame
        generated_data_list = [row.split(',') for row in generated_data.strip().split('\n')]
        
        # Ensure the first row is treated as the header and matches the input DataFrame's columns
        generated_df = pd.DataFrame(generated_data_list[1:], columns=sample_data.columns)

        # Display generated data
        st.subheader("Generated Data:")
        st.dataframe(generated_df)

        # Save generated data to an Excel file
        output_file = "gpt-4o.xlsx"
        generated_df.to_excel(output_file, index=False)

        # Create a download button for the generated Excel file
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Excel File",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()