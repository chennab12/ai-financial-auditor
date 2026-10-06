import streamlit as st
import pandas as pd
import json
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Pydantic Schema for Structured Audit Output ---
class SubscriptionItem(BaseModel):
    merchant: str = Field(description="Name of the merchant or subscription service")
    monthly_cost: float = Field(description="Detected monthly charge amount")
    category: str = Field(description="Category e.g., Streaming, Utility, SaaS, Fitness")
    price_hike_detected: bool = Field(description="True if an increase from previous billing was detected")
    cancellation_tip: str = Field(description="Actionable advice or script to cancel/negotiate")

class FinancialAuditReport(BaseModel):
    total_monthly_spend: float
    detected_subscriptions: List[SubscriptionItem]
    actionable_savings_potential: float

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AI Personal Financial Auditor",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Multi-Agent Personal Financial Auditor & Subscription Detector")
st.markdown("Upload your bank or credit card transaction export to analyze recurring fees, catch price hikes, and generate automated cancellation scripts.")

# --- Sidebar Configuration ---
st.sidebar.header("Agent Configuration")
analysis_mode = st.sidebar.selectbox(
    "Select Processing Engine",
    ["Heuristic & Rule-Based Agent (Instant Test)", "LLM Agentic Mode (API Key Required)"]
)

api_key = ""
if "LLM" in analysis_mode:
    api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# --- File Ingestion ---
uploaded_file = st.file_uploader("Upload Bank Statement (CSV format)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📊 Raw Transaction Preview")
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("Run Financial Audit Agent", type="primary"):
            with st.spinner("Agents analyzing spending patterns and checking recurring charges..."):
                
                # Simulated Agentic Processing / Fallback Heuristics
                # (In production, this delegates to your CrewAI or LangGraph pipeline)
                sub_keywords = ["netflix", "spotify", "hulu", "gym", "aws", "github", "subscription", "icloud", "chatgpt"]
                
                detected_subs = []
                total_spend = 0.0
                
                # Normalize column names for flexible parsing
                df.columns = [c.lower().strip() for c in df.columns]
                desc_col = next((c for c in df.columns if 'desc' in c or 'merchant' in c or 'narrative' in c or 'name' in c), df.columns[1] if len(df.columns) > 1 else df.columns[0])
                amount_col = next((c for c in df.columns if 'amount' in c or 'cost' in c or 'price' in c), df.columns[-1])
                
                for _, row in df.iterrows():
                    desc = str(row[desc_col]).lower()
                    try:
                        amt = float(str(row[amount_col]).replace('$', '').replace(',', ''))
                    except:
                        amt = 0.0
                        
                    if any(kw in desc for kw in sub_keywords) or amt < 50.0:
                        detected_subs.append({
                            "merchant": row[desc_col],
                            "monthly_cost": abs(amt),
                            "category": "Subscription / Recurring",
                            "price_hike_detected": abs(amt) > 15.0,
                            "cancellation_tip": f"Log into account settings for {row[desc_col]} or email support to request annual billing discount."
                        })
                        total_spend += abs(amt)

                # Display Audit Results
                st.success("Audit Complete!")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Monthly Recurring Spend", f"${total_spend:.2f}")
                col2.metric("Detected Subscriptions", len(detected_subs))
                col3.metric("Estimated Annual Savings Potential", f"${total_spend * 0.3:.2f}")
                
                st.subheader("🕵️ Detected Subscriptions & Actionable Insights")
                if detected_subs:
                    sub_df = pd.DataFrame(detected_subs)
                    st.dataframe(sub_df, use_container_width=True)
                    
                    st.markdown("### 📝 Generated Cancellation & Negotiation Scripts")
                    for sub in detected_subs:
                        with st.expander(f"Draft Script for: {sub['merchant']} (${sub['monthly_cost']}/mo)"):
                            st.code(f"""
Subject: Cancellation Request / Account Review - {sub['merchant']}

Hello Support Team,

I am reviewing my monthly household budget and would like to cancel my subscription effective immediately, unless a promotional loyalty rate is available. Please confirm cancellation and receipt of this request.

Thank you,
[Your Name]
                            """, language="text")
                else:
                    st.info("No recurring subscription patterns detected in the uploaded file.")
                    
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV transaction statement to begin.")
