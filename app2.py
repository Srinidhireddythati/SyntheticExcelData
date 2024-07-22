import pandas as pd
import openai
import streamlit as st
from typing import List
import random
import os

# Function to read the Excel file
def read_excel(file_path):
    data = pd.read_excel(file_path)
    return data

# Function to change the date in an Excel file to a specific date
def change_date_in_excel(input_file_path: str, output_file_path: str, target_date: str = "29/02/2018"):
    data = pd.read_excel(input_file_path)
    data['Date'] = target_date
    data.to_excel(output_file_path, index=False)
    st.write(f"Dates in {input_file_path} have been changed to {target_date} and saved to {output_file_path}")

# Function to save generated data to an existing Excel file
def save_to_excel(input_data: pd.DataFrame, output_file: str):
    input_data.to_excel(output_file, index=False)

# Function to generate random sales data for replacement
def generate_random_sales_data(num_rows: int):
    new_data = []
    for _ in range(num_rows):
        sales = round(random.uniform(80000, 120000), 2)
        marketing_spend = round(random.uniform(1000, 30000), 2)
        electronics_sales = round(random.uniform(10000, 30000), 2)
        home_sales = round(random.uniform(10000, 20000), 2)
        clothes_sales = round(random.uniform(25000, 40000), 2)
        new_data.append([sales, marketing_spend, electronics_sales, home_sales, clothes_sales])
    return new_data

# Function to replace data in specific columns and save the modified Excel file
def replace_and_save_data(input_file_path, output_file_path, num_rows_to_generate=3, target_columns=[3, 4, 5, 6, 7]):
    sample_data = read_excel(input_file_path)
    
    # Generate new content
    generated_data = generate_random_sales_data(len(sample_data))
    
    # Replace data in specified columns
    for i in range(len(sample_data)):  # Loop through original data rows
        for col_index, col_offset in zip(target_columns, range(len(target_columns))):
            sample_data.iloc[i, col_index] = generated_data[i][col_offset]  # Assuming generated data is in the correct format
    
    # Save modified data
    save_to_excel(sample_data, output_file_path)
    st.write(f"Data in {input_file_path} has been replaced in columns {target_columns} and saved to {output_file_path}")

# Function to remove the second row and save the modified data
def remove_second_row_and_save(input_file_path: str, output_file_path: str):
    data = pd.read_excel(input_file_path)
    data = data.drop(1).reset_index(drop=True)
    data.to_excel(output_file_path, index=False)
    st.write(f"Data from {input_file_path} with the second row removed has been saved to {output_file_path}")

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
            
            # Replace the data in specified columns
            replace_and_save_data(file_path, os.path.join(output_dir, "replaced_data.xlsx"), num_rows_to_generate)

            # Change the date in the replaced data file
            change_date_in_excel(os.path.join(output_dir, "replaced_data.xlsx"), os.path.join(output_dir, "modified_dates.xlsx"), target_date="29/02/2018")

            # Remove the second row and save the modified data
            remove_second_row_and_save(os.path.join(output_dir, "modified_dates.xlsx"), os.path.join(output_dir, "final_output.xlsx"))

            st.success("Excel processing completed. Download the processed files below:")

            st.download_button(
                label="Download Replaced Data Excel",
                data=open(os.path.join(output_dir, "replaced_data.xlsx"), "rb").read(),
                file_name="replaced_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.download_button(
                label="Download Modified Dates Excel",
                data=open(os.path.join(output_dir, "modified_dates.xlsx"), "rb").read(),
                file_name="modified_dates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.download_button(
                label="Download Final Output Excel",
                data=open(os.path.join(output_dir, "final_output.xlsx"), "rb").read(),
                file_name="final_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
