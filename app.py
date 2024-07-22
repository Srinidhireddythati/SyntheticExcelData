import pandas as pd
import openai
import streamlit as st
import os

ANALYZER_SYSTEM_PROMPT = """You are an AI agent that analyzes the CSV provided by the user.
Focus on analyzing the data structure, format, and column meanings. Provide a clear description of each column's purpose and how the data is organized."""

GENERATOR_SYSTEM_PROMPT = """You are an AI agent that generates new CSV rows based on analysis results and sample data.
Ensure the new rows follow the exact formatting of the original data. Output only the generated rows, without any additional text."""

ANALYZER_USER_PROMPT = """Analyze the structure and patterns of this sample dataset:

{sample_data}

Provide a concise summary:
1. Describe the formatting of the dataset, including the structure of the CSV.
2. Explain what the dataset represents and clarify the purpose of each column.
3. Based on identified patterns, describe how new data should look, maintaining the dataset's structure and column meanings.
"""

GENERATOR_USER_PROMPT = """Generate {num_rows} new CSV rows based on the analysis and sample data:

Analysis:
{analysis_result}

Sample Data:
{sample_data}

Ensure the generated rows match the formatting of the original data. Output only the generated rows, without any additional text.
"""

# Function to read the Excel file
def read_excel(file_path):
    data = pd.read_excel(file_path)
    return data

# Function to change the date in an Excel file to a specific date
def change_date_in_excel(data: pd.DataFrame, target_date: str = "29/02/2018"):
    data['Date'] = target_date
    return data

# Function to save generated data to an existing Excel file
def save_to_excel(input_data: pd.DataFrame, output_file: str):
    input_data.to_excel(output_file, index=False)

# Function to generate sales data using OpenAI API with GPT-4
def generate_openai_sales_data(num_rows: int, sample_data: pd.DataFrame):
    sample_data_str = sample_data.to_csv(index=False)

    analyzer_prompt = ANALYZER_USER_PROMPT.format(sample_data=sample_data_str)
    analysis_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
            {"role": "user", "content": analyzer_prompt}
        ]
    )

    analysis_result = analysis_response.choices[0].message['content'].strip()

    generator_prompt = GENERATOR_USER_PROMPT.format(num_rows=num_rows, analysis_result=analysis_result, sample_data=sample_data_str)
    generation_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": generator_prompt}
        ]
    )

    generated_text = generation_response.choices[0].message['content'].strip()

    # Parsing the response directly as a Python list of lists
    try:
        new_data = eval(generated_text)
        if not isinstance(new_data, list) or not all(isinstance(row, list) for row in new_data):
            raise ValueError("Generated data is not in the expected format")
    except (SyntaxError, ValueError) as e:
        st.error(f"Failed to parse the generated data from OpenAI response: {e}")
        new_data = []

    return new_data

# Function to replace data in specific columns and return the modified DataFrame
def replace_data(input_data: pd.DataFrame, generated_data, target_columns=[3, 4, 5, 6, 7]):
    if len(generated_data) != len(input_data):
        st.error("The number of generated rows does not match the number of original rows.")
        return input_data

    # Replace data in specified columns
    for i in range(len(input_data)):  # Loop through original data rows
        for col_index, col_offset in zip(target_columns, range(len(target_columns))):
            input_data.iloc[i, col_index] = generated_data[i][col_offset]  # Assuming generated data is in the correct format

    return input_data

# Function to remove the second row and return the modified DataFrame
def remove_second_row(data: pd.DataFrame):
    data = data.drop(1).reset_index(drop=True)
    return data

# Streamlit app
def main():
    st.title("Excel Data Processor")

    openai_api_key = st.text_input("Enter your OpenAI API key", type="password")
    openai.api_key = openai_api_key

    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    if uploaded_file is not None:
        file_path = f"uploaded_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        num_rows_to_generate = st.number_input("Number of rows to generate", min_value=1, max_value=100, value=3)

        if st.button("Process Excel"):
            # Create output directory if it doesn't exist
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            # Read the input file
            input_data = read_excel(file_path)

            # Generate new data using OpenAI
            generated_data = generate_openai_sales_data(num_rows_to_generate, input_data)

            # Print the generated data on the webpage
            if generated_data:
                st.write("Generated Data:")
                st.write(pd.DataFrame(generated_data, columns=input_data.columns))

            # Replace the data in specified columns
            modified_data = replace_data(input_data, generated_data)

            # Change the date in the replaced data
            modified_data_with_dates = change_date_in_excel(modified_data)

            # Remove the second row
            final_data = remove_second_row(modified_data_with_dates)

            # Save the final output
            final_output_path = os.path.join(output_dir, "final_output.xlsx")
            save_to_excel(final_data, final_output_path)

            st.success("Excel processing completed. Download the processed files below:")

            st.download_button(
                label="Download Final Output Excel",
                data=open(final_output_path, "rb").read(),
                file_name="final_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
