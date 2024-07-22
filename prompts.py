# prompts.py

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
