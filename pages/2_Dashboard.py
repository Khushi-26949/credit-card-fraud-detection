import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

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

if os.path.exists("user_history.json"):
    with open("user_history.json", "r") as f:
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
else:
    st.info("ℹ No transaction history found.")

st.markdown("---")

# --- LOAD DATASET ---
@st.cache_data
def load_data():
    return pd.read_csv(r"C:\Users\khush\OneDrive\Desktop\cleaned_fraud_data2.xls")

df = load_data()
st.success("✅ Dataset Loaded Successfully!")

# --------------------------------------------------------------------
# 🔍 FILTER BAR (Top Controls)
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

fig1 = px.pie(
    class_counts,
    names="Class",
    values="Count",
    title="Fraud vs Normal Distribution",
    color="Class",
    hole=0.4
)
st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------------------------
# 2️⃣ AMOUNT DISTRIBUTION CHART
# --------------------------------------------------------------------
st.markdown("### 💰 Amount Distribution (Normal vs Fraud)")

fig2 = px.box(
    filtered_df,
    x="Class",
    y="Amount",
    color="Class",
    title="Amount Comparison: Normal vs Fraud"
)
st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------------------------
# 3️⃣ HOURLY ANALYSIS
# --------------------------------------------------------------------
if "Hour" in df.columns:
    st.markdown("### ⏰ Transactions by Hour (Normal vs Fraud)")

    hourly = filtered_df.groupby("Hour")["Class"].value_counts().unstack(fill_value=0)

    fig3 = px.line(
        hourly,
        x=hourly.index,
        y=[0, 1],
        labels={"value": "Count", "Hour": "Hour of Day"},
        title="Hourly Transaction Trend"
    )
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

# Footer
st.markdown("<hr><center>Made with ❤️ | Advanced ML Dashboard</center>", unsafe_allow_html=True)
