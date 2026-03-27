import streamlit as st
import pandas as pd
import string
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Multi-Tool Agent", layout="wide")

# --- DATA SETTINGS ---
def load_data(uploaded_file):
    """Safely loads CSV and handles missing values."""
    try:
        df = pd.read_csv(uploaded_file)
        return df.fillna("N/A")
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# --- AGENT TOOLS (Modular Logic) ---

def tool_1_show_dataset(df):
    """Tool 1: Displays the full dataset (first 100 rows)."""
    return "dataframe", df.head(100), "Here is the dataset (showing top 100 rows):"

def tool_2_show_columns(df):
    """Tool 2: Displays the column names of the dataset."""
    cols = ", ".join(df.columns.tolist())
    return "text", f"The columns in this dataset are: **{cols}**", "Dataset Columns"

def tool_3_filter_data(df, clean_query):
    """Tool 3: Filters data based on column name matches."""
    col_mapping = {col.lower().replace("_", " "): col for col in df.columns}
    matched_cols = [actual_name for norm_name, actual_name in col_mapping.items() if norm_name in clean_query]
    
    if matched_cols:
        return "dataframe", df[matched_cols].head(50), f"Showing data for columns: {', '.join(matched_cols)}"
    return None

def tool_4_eligibility_checker(query):
    """Tool 4: Checks loan eligibility based on income."""
    # Find numbers in query
    numbers = re.findall(r'\d+', query)
    if numbers:
        income = int(numbers[0])
        status = "✅ Eligible" if income > 3000 else "❌ Not Eligible"
        return "text", f"With an income of **${income}**, your status is: **{status}** (Criteria: > $3000)", "Loan Eligibility Result"
    return "text", "Please provide an income amount (e.g., 'Check eligibility for 5000').", "Calculation Error"

def tool_5_emi_calculator(query):
    """Tool 5: Basic EMI Calculator."""
    # Look for numbers: Principal, Rate, Tenure
    numbers = re.findall(r'\d+', query)
    if len(numbers) >= 3:
        p = float(numbers[0])  # Principal
        r = float(numbers[1]) / (12 * 100)  # Monthly interest rate
        n = float(numbers[2])  # Tenure in months
        
        if r > 0:
            emi = p * r * ((1 + r)**n) / ((1 + r)**n - 1)
        else:
            emi = p / n # Zero interest case
            
        return "text", f"For a loan of **${p}** at **{numbers[1]}%** for **{n}** months, the EMI is: **${emi:.2f}**", "EMI Calculation"
    return "text", "Please provide: Loan amount, Interest rate, and Tenure (e.g., 'EMI 10000 5 12').", "Calculation Error"

def tool_fallback():
    """Fallback response if no tool matches."""
    return "text", "I couldn't match your request to a tool. Try 'show dataset', 'emi calculator', or 'check eligibility'.", "Agent Error"

# --- CORE AGENT LOGIC ---

def run_multi_tool_agent(user_query, df):
    """
    Agent Orchestrator: Routes queries to specific tools using if/else logic.
    """
    clean_query = user_query.lower().translate(str.maketrans('', '', string.punctuation))

    # Trigger Tool 4: Eligibility
    if "eligible" in clean_query or "eligibility" in clean_query:
        return tool_4_eligibility_checker(clean_query)

    # Trigger Tool 5: EMI
    if "emi" in clean_query or "calculate" in clean_query or "calculator" in clean_query:
        # Avoid matching 'calculate' if it's meant for filtering? 
        # Usually EMI/Calculator implies tool 5.
        if "emi" in clean_query or "loan" in clean_query:
            return tool_5_emi_calculator(clean_query)

    # Trigger Tool 1: Show Dataset
    if any(p in clean_query for p in ["dataset", "show data", "display data", "view"]):
        return tool_1_show_dataset(df)

    # Trigger Tool 2: Show Columns
    if any(p in clean_query for p in ["column", "header", "field"]):
        return tool_2_show_columns(df)

    # Trigger Tool 3: Filter (Last priority dataset tool)
    filter_res = tool_3_filter_data(df, clean_query)
    if filter_res:
        return filter_res

    return tool_fallback()

# --- STREAMLIT UI ---

st.title("🤖 Multi-Tool AI Multi-Agent System")
st.markdown("I can explore data, check loan eligibility, and calculate EMI.")

uploaded_file = st.file_uploader("Upload Dataset (CSV)", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        # Prompt for agent
        query = st.text_input("Talk to the Agent:", placeholder="e.g. 'Show columns', 'EMI 50000 10 24', 'Is 4000 eligible?'")

        if query:
            # Execute Agent
            res_type, res_content, res_title = run_multi_tool_agent(query, df)
            
            st.divider()
            st.subheader(f"🛠️ {res_title}")
            
            if res_type == "dataframe":
                st.dataframe(res_content, use_container_width=True)
            else:
                st.info(res_content)
        else:
            st.dataframe(df.head(5), use_container_width=True)
            st.info("Try asking: 'What are the columns?' or 'Calculate EMI 10000 5 12'")
else:
    st.info("👋 Welcome! Please upload a CSV file to begin interacting with the tools.")

# Footer Details
st.sidebar.title("Tool Instructions")
st.sidebar.markdown("""
- **Dataset Tools:** 'Show dataset', 'Show columns'
- **Filter Tools:** Mention column names (e.g. 'loan status')
- **Eligibility:** 'Check eligibility 5000'
- **EMI:** 'EMI [Amount] [Rate] [Tenure]'
""")
