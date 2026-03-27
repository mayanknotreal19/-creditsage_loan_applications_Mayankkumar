# AI Agent CSV Explorer

A production-ready Streamlit application that allows users to upload a CSV dataset and interact with it using simple natural language-like queries.

## Features
- CSV File Upload
- Data Preview
- Basic AI Agent logic for searching and filtering
- Missing value handling

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Example Usage
- Upload a CSV (e.g., sales data).
- Type "Show me summary" to see statistical data.
- Type "Filter for [Value]" to search for specific rows.
- Ask general questions like "Help" to see available commands.
