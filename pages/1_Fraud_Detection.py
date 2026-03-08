import streamlit as st
import joblib
import numpy as np
import pandas as pd
import json
import os
import time
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------
# Base Directory — works on any computer
# ---------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "fraud_model (1).pkl")
DATA_PATH = os.path.join(BASE_DIR, "cleaned_fraud_data2.xls")

# ---------------------------------------------------
# Load User Transaction History
# ---------------------------------------------------
HISTORY_PATH = os.path.join(BASE_DIR, "user_history.json")

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return {}
    with open(HISTORY_PATH, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)

history_db = load_history()

# ---------------------------------------------------
# Title Section
# ---------------------------------------------------
st.markdown("## 💳 Credit Card Fraud Detection")
st.write("Check fraud automatically using dummy dataset OR enter custom values.")

# ---------------------------------------------------
# Load Model
# ---------------------------------------------------
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

# ---------------------------------------------------
# Load dummy dataset
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

data = load_data()

# ---------------------------------------------------
# Show logged-in user
# ---------------------------------------------------
if "user" in st.session_state and st.session_state.user:
    user = st.session_state.user
    st.info(f"Logged in as: **{user['name']}** ({user['email']})")
    user_email = user["email"]
else:
    st.warning("⚠ Please login first from Home Page.")
    st.stop()

# ---------------------------------------------------
# AUTO-FILL BUTTON
# ---------------------------------------------------
st.markdown("### 🔄 Auto-Fill Transaction (Using Dummy Dataset)")

if st.button("Auto-Fill Random Transaction"):
    row = data.sample(1).iloc[0]

    st.session_state.amount = float(row["Amount"])
    st.session_state.hour = int(row["Hour"])
    st.session_state.device = "Yes" if row["device_change"] == 1 else "No"
    st.session_state.location = "Yes" if row["location_diff"] == 1 else "No"

    st.success("Random transaction loaded!")

# ---------------------------------------------------
# TRANSACTION INPUT FIELDS
# ---------------------------------------------------
st.markdown("### 📝 Transaction Details")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input(
            "Transaction Amount (₹)",
            min_value=0.0,
            step=1.0,
            value=st.session_state.get("amount", 0.0)
        )

        device = st.selectbox(
            "Device Changed?",
            ["No", "Yes"],
            index=1 if st.session_state.get("device") == "Yes" else 0
        )

    with col2:
        hour = st.slider(
            "Transaction Hour (0–23)",
            0, 23,
            value=st.session_state.get("hour", 0)
        )

        location = st.selectbox(
            "Location Different?",
            ["No", "Yes"],
            index=1 if st.session_state.get("location") == "Yes" else 0
        )

# ---------------------------------------------------
# Feature Flags
# ---------------------------------------------------
night_flag = 1 if (hour >= 23 or hour <= 6) else 0
device_flag = 1 if device == "Yes" else 0
loc_flag = 1 if location == "Yes" else 0
high_amt = 1 if amount > 10000 else 0

# ---------------------------------------------------
# XAI Reasoning Function
# ---------------------------------------------------
def explain_transaction(amount, hour, night_flag, device_flag, loc_flag, high_amt):
    reasons = []

    if high_amt:
        reasons.append("💰 **High transaction amount detected**")

    if night_flag:
        reasons.append("🌙 **Transaction happened late at night**")

    if device_flag:
        reasons.append("📱 **Device changed recently**")

    if loc_flag:
        reasons.append("📍 **Location mismatch detected**")

    risk_score = (night_flag*20 + device_flag*20 + loc_flag*30 + high_amt*30)

    if risk_score == 0:
        reasons.append("✔ **No suspicious behavior detected**")

    return reasons, risk_score

# ---------------------------------------------------
# PREDICTION
# ---------------------------------------------------
st.markdown("### 🔍 Predict Fraud")

if st.button("Predict Fraud Now"):
    with st.spinner("🔍 Analyzing transaction..."):
        time.sleep(1.5)
        input_data = np.array([[amount, hour, night_flag, device_flag, loc_flag, high_amt]])
        prediction = model.predict(input_data)[0]

    reasons, risk_score = explain_transaction(amount, hour, night_flag, device_flag, loc_flag, high_amt)

    st.subheader("🧾 Transaction Summary")
    st.write({
        "Amount": amount,
        "Hour": hour,
        "Night Transaction": night_flag,
        "Device Changed": device_flag,
        "Location Different": loc_flag,
        "High Amount": high_amt
    })

    st.subheader("🤖 Suspicious Transaction Reasoning (XAI)")
    for r in reasons:
        st.write("- " + r)

    st.markdown(f"### 🔥 Risk Score: **{risk_score}%**")

    if risk_score > 50:
        bar_color = "red"
        risk_label = "High Risk 🚨"
    elif risk_score > 20:
        bar_color = "orange"
        risk_label = "Medium Risk ⚠️"
    else:
        bar_color = "green"
        risk_label = "Low Risk ✅"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": f"Risk Level — {risk_label}"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": bar_color},
            "steps": [
                {"range": [0, 30], "color": "#d4edda"},
                {"range": [30, 60], "color": "#fff3cd"},
                {"range": [60, 100], "color": "#f8d7da"},
            ],
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

    if prediction == 1:
        st.error("⚠ Fraud Detected — This transaction looks suspicious.")
    else:
        st.success("✔ Safe Transaction — No fraud detected.")

    new_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "amount": amount,
        "hour": hour,
        "night_flag": night_flag,
        "device_flag": device_flag,
        "loc_flag": loc_flag,
        "high_amt": high_amt,
        "prediction": int(prediction),
        "risk_score": risk_score,
        "reasons": reasons
    }

    if user_email not in history_db:
        history_db[user_email] = []

    history_db[user_email].append(new_record)
    save_history(history_db)

    st.success("📁 Transaction saved to your history!")
