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
def analyzer_agent(sample_data, openai_api_key, model):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model=model,
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
def generator_agent(analysis_result, sample_data, openai_api_key, model, num_rows_to_generate):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model=model,
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

    # Dropdown for model selection
    model = st.selectbox(
        "Select the OpenAI model:",
        options=["gpt-4o", "gpt-4o-mini"],
        index=0
    )

    # File uploader for Excel files
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

    if uploaded_file and openai_api_key:
        # Read the sample data from the uploaded Excel file
        sample_data = read_excel(uploaded_file)
        sample_data_str = sample_data.to_csv(index=False)

        # Calculate the number of rows in the input data
        num_input_rows = len(sample_data)

        # Number of rows to generate
        num_rows_to_generate = num_input_rows + 1

        st.write("Launching team of Agents...")

        # Analyze the sample data using the Analyzer Agent
        analysis_result = analyzer_agent(sample_data_str, openai_api_key, model)
        st.subheader("Analyzer Agent Output:")
        st.write(analysis_result)

        st.write("Generating new data...")

        # Generate new rows of data
        generated_data = generator_agent(analysis_result, sample_data_str, openai_api_key, model, num_rows_to_generate)

        # Convert generated data to a DataFrame
        generated_data_list = [row.split(',') for row in generated_data.strip().split('\n')]

        # Debug: Print the raw generated data and sample data columns
        st.write("Generated Data (Raw):")
        st.write(generated_data_list)
        st.write("Sample Data Columns:")
        st.write(sample_data.columns)

        # Ensure the first row is treated as the header and matches the input DataFrame's columns
        generated_df = pd.DataFrame(generated_data_list[1:], columns=sample_data.columns)

        # Display generated data
        st.subheader("Generated Data:")
        st.dataframe(generated_df)

        # Save generated data to an Excel file
        output_file = "generated_data.xlsx"
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
