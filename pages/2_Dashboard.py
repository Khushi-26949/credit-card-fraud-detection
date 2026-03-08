import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from fpdf import FPDF
from datetime import datetime

# ---------------------------------------------------
# Base Directory — works on any computer
# ---------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "cleaned_fraud_data2.xls")
HISTORY_PATH = os.path.join(BASE_DIR, "user_history.json")

# --- PAGE TITLE ---
st.markdown("<h2 style='color:#4CAF50;'>📊 Advanced Fraud Detection Dashboard</h2>", unsafe_allow_html=True)
st.write("Explore fraud patterns, high-risk transactions, amount trends, hours analysis, and more.")

# --- LOGIN CHECK ---
if "user" not in st.session_state or not st.session_state.user:
    st.warning("⚠ Please login first to access Dashboard.")
    st.stop()

# --------------------------------------------------------------------
# 👤 USER PERSONAL HISTORY
# --------------------------------------------------------------------
st.markdown("### 👤 My Transaction History")

user_email = st.session_state.user["email"]
user_name = st.session_state.user["name"]

if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, "r") as f:
        history = json.load(f)

    user_data = history.get(user_email, [])

    if not user_data:
        st.info("ℹ No transactions yet — go to Fraud Detection page!")
    else:
        df_user = pd.DataFrame(user_data)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Checks", len(df_user))
        col2.metric("🚨 Fraud", df_user[df_user["prediction"] == 1].shape[0])
        col3.metric("✅ Safe", df_user[df_user["prediction"] == 0].shape[0])

        st.dataframe(df_user)

        st.markdown("### 📄 Download Your Report")

        def generate_pdf(user_name, user_email, user_data):
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Helvetica", "B", 20)
            pdf.set_fill_color(33, 37, 41)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 15, "Credit Card Fraud Detection Report", fill=True, ln=True, align="C")

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 11)
            pdf.ln(5)
            pdf.cell(0, 8, f"Name   : {user_name}", ln=True)
            pdf.cell(0, 8, f"Email  : {user_email}", ln=True)
            pdf.cell(0, 8, f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(5)

            total = len(user_data)
            fraud = sum(1 for r in user_data if r["prediction"] == 1)
            safe = total - fraud

            pdf.set_font("Helvetica", "B", 13)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, "Summary", fill=True, ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, f"Total Transactions : {total}", ln=True)
            pdf.cell(0, 8, f"Fraud Detected     : {fraud}", ln=True)
            pdf.cell(0, 8, f"Safe Transactions  : {safe}", ln=True)
            pdf.ln(5)

            pdf.set_font("Helvetica", "B", 13)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(0, 10, "Transaction Details", fill=True, ln=True)
            pdf.ln(2)

            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(50, 50, 50)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(45, 8, "Timestamp", border=1, fill=True)
            pdf.cell(25, 8, "Amount", border=1, fill=True)
            pdf.cell(15, 8, "Hour", border=1, fill=True)
            pdf.cell(25, 8, "Risk Score", border=1, fill=True)
            pdf.cell(30, 8, "Result", border=1, fill=True, ln=True)

            pdf.set_font("Helvetica", "", 9)
            for record in user_data:
                pdf.set_text_color(0, 0, 0)
                result = "FRAUD" if record["prediction"] == 1 else "SAFE"
                if record["prediction"] == 1:
                    pdf.set_fill_color(255, 220, 220)
                else:
                    pdf.set_fill_color(220, 255, 220)

                pdf.cell(45, 7, str(record.get("timestamp", "N/A")), border=1, fill=True)
                pdf.cell(25, 7, f"Rs {record['amount']:.2f}", border=1, fill=True)
                pdf.cell(15, 7, str(record["hour"]), border=1, fill=True)
                pdf.cell(25, 7, f"{record['risk_score']}%", border=1, fill=True)
                pdf.cell(30, 7, result, border=1, fill=True, ln=True)

            return pdf.output()

        if st.button("📥 Generate & Download PDF Report"):
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf(user_name, user_email, user_data)

            st.download_button(
                label="⬇️ Click Here to Download PDF",
                data=bytes(pdf_bytes),
                file_name=f"fraud_report_{user_name}.pdf",
                mime="application/pdf"
            )
            st.success("✅ PDF Ready — Click above to download!")

else:
    st.info("ℹ No transaction history found.")

st.markdown("---")

# --- LOAD DATASET ---
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()
st.success("✅ Dataset Loaded Successfully!")

# --------------------------------------------------------------------
# 🔍 FILTER BAR
# --------------------------------------------------------------------
st.markdown("### 🔎 Filters")

colf1, colf2, colf3 = st.columns(3)

fraud_filter = colf1.selectbox("Filter by Class", ["All", "Normal", "Fraud"])
hour_filter = colf2.slider("Filter by Hour Range", 0, 23, (0, 23))
amount_filter = colf3.slider("Amount Range", 0, int(df["Amount"].max()), (0, int(df["Amount"].max())))

filtered_df = df.copy()

if fraud_filter != "All":
    filtered_df = filtered_df[filtered_df["Class"] == (1 if fraud_filter == "Fraud" else 0)]

filtered_df = filtered_df[
    (filtered_df["Hour"] >= hour_filter[0]) &
    (filtered_df["Hour"] <= hour_filter[1]) &
    (filtered_df["Amount"] >= amount_filter[0]) &
    (filtered_df["Amount"] <= amount_filter[1])
]

# --------------------------------------------------------------------
# 📌 METRICS CARDS
# --------------------------------------------------------------------
st.markdown("### 📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transactions", len(filtered_df))
col2.metric("Normal", filtered_df[filtered_df["Class"] == 0].shape[0])
col3.metric("Fraud", filtered_df[filtered_df["Class"] == 1].shape[0])

fraud_percent = round((filtered_df[filtered_df["Class"] == 1].shape[0] / len(filtered_df)) * 100, 2) if len(filtered_df) > 0 else 0
col4.metric("Fraud %", f"{fraud_percent}%")

st.markdown("---")

# --------------------------------------------------------------------
# 1️⃣ FRAUD vs NORMAL DISTRIBUTION
# --------------------------------------------------------------------
st.markdown("### 🔍 Fraud vs Normal Distribution")

class_counts = filtered_df["Class"].value_counts().reset_index()
class_counts.columns = ["Class", "Count"]

fig1 = px.pie(class_counts, names="Class", values="Count",
              title="Fraud vs Normal Distribution", color="Class", hole=0.4)
st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------------------------
# 2️⃣ AMOUNT DISTRIBUTION CHART
# --------------------------------------------------------------------
st.markdown("### 💰 Amount Distribution (Normal vs Fraud)")

fig2 = px.box(filtered_df, x="Class", y="Amount", color="Class",
              title="Amount Comparison: Normal vs Fraud")
st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------------------------
# 3️⃣ HOURLY ANALYSIS
# --------------------------------------------------------------------
if "Hour" in df.columns:
    st.markdown("### ⏰ Transactions by Hour (Normal vs Fraud)")
    hourly = filtered_df.groupby("Hour")["Class"].value_counts().unstack(fill_value=0)
    fig3 = px.line(hourly, x=hourly.index, y=[0, 1],
                   labels={"value": "Count", "Hour": "Hour of Day"},
                   title="Hourly Transaction Trend")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠ 'Hour' column not found in dataset.")

st.markdown("---")

# --------------------------------------------------------------------
# 4️⃣ HIGH RISK TRANSACTIONS TABLE
# --------------------------------------------------------------------
st.markdown("### 🚨 Top 10 High Amount & High Risk Transactions")
high_risk_df = filtered_df.sort_values(by="Amount", ascending=False).head(10)
st.dataframe(high_risk_df)

# --------------------------------------------------------------------
# 5️⃣ DATASET PREVIEW
# --------------------------------------------------------------------
with st.expander("📄 Full Dataset Preview (Filtered)"):
    st.dataframe(filtered_df)
st.markdown("<hr><center>Made with ❤️ | Advanced ML Dashboard</center>", unsafe_allow_html=True)
