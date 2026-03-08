# 🛡️ Credit Card Fraud Detection System

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?style=for-the-badge&logo=streamlit)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange?style=for-the-badge&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> A full-stack fraud detection web application that analyzes financial transactions in real time using Machine Learning, with explainable AI reasoning, interactive dashboards, and secure user management.

---

## 📸 Preview

| Login & Auth | Fraud Detection | Dashboard |
|---|---|---|
| Secure login with attempt limiting | ML prediction + Risk Gauge | Plotly charts + PDF export |

---

## ✨ Key Features

| Category | Feature |
|---|---|
| 🔐 **Authentication** | Register, Login, SHA-256 password hashing, session management |
| 🚫 **Security** | Login attempt limiting (3 tries), page-level access control |
| ✅ **Validation** | Email format, 10-digit phone, password strength checks |
| 💳 **Fraud Detection** | Real-time ML prediction with auto-fill from dataset |
| 🤖 **Explainable AI** | XAI reasoning — explains *why* a transaction is flagged |
| 🔥 **Risk Score** | Visual gauge chart (Green → Yellow → Red, 0–100%) |
| ⏱️ **Timestamps** | Every transaction saved with date & time |
| 📊 **Dashboard** | Personal history, Plotly charts (Pie, Box, Line), Top-10 table |
| 📄 **PDF Reports** | Download full transaction history as formatted PDF |
| 🔑 **Admin Panel** | Password-protected panel to manage users & data |

---

## 🗂️ Project Structure

```
credit-card-fraud-detection/
├── app.py                        # Main app — Login, Register, Navigation
├── pages/
│   ├── 1_Fraud_Detection.py      # Fraud prediction + XAI + Risk Gauge
│   ├── 2_Dashboard.py            # Analytics dashboard + PDF export
│   └── Admin.py                  # Admin panel (password protected)
├── fraud_model.pkl               # Trained ML classification model
├── cleaned_fraud_dataset.xls     # Dataset for auto-fill & analysis
├── users.json                    # Registered user store
├── user_history.json             # Per-user transaction history
└── README.md
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.12** | Core language |
| **Streamlit** | Multi-page web app framework |
| **Scikit-learn + Joblib** | ML model training & deployment |
| **Pandas + NumPy** | Data processing |
| **Plotly** | Interactive charts & gauge visualization |
| **FPDF2** | PDF report generation |
| **Hashlib (SHA-256)** | Secure password hashing |
| **JSON** | Lightweight data storage |

---

## 🚀 Getting Started

**1. Install dependencies**
```bash
pip install streamlit pandas numpy plotly scikit-learn joblib fpdf2
```

**2. Ensure these files exist in your project folder**
```
app.py
fraud_model.pkl
cleaned_fraud_dataset.xls
users.json           ← should contain {}
user_history.json    ← should contain {}
pages/
  ├── 1_Fraud_Detection.py
  ├── 2_Dashboard.py
  └── Admin.py
```

**3. Run the app**
```bash
streamlit run app.py
```

**4. Open in browser**
```
http://localhost:8501
```

---

## 📖 Usage Guide

1. **Register** — Create account with name, valid email, 10-digit phone & password
2. **Login** — Enter credentials and press `Enter` or click Login
3. **Fraud Detection** — Enter transaction details manually or use Auto-Fill
4. **View Result** — See prediction, XAI reasoning, risk score gauge & timestamp
5. **Dashboard** — Explore personal history, analytics charts & download PDF report
6. **Admin Panel** — Enter admin password to manage users and data

---

## 🔒 Security Overview

| Feature | Implementation |
|---|---|
| Password Storage | SHA-256 hashed — never stored as plain text |
| Login Protection | Locked after 3 failed attempts |
| Admin Access | Password hash verification |
| Input Validation | Email regex, 10-digit phone, 6-char password minimum |
| Session Control | `st.session_state` — persists across all pages |
| Page Guard | Every page verifies login before rendering |

---

## 🤖 ML Model

**Input Features**

| Feature | Description |
|---|---|
| `amount` | Transaction amount (₹) |
| `hour` | Hour of transaction (0–23) |
| `night_flag` | 1 if transaction between 11PM–6AM |
| `device_flag` | 1 if new/unrecognized device |
| `location_flag` | 1 if location mismatch |
| `high_amount_flag` | 1 if amount > ₹10,000 |

**Output:** `1` → Fraudulent 🚨 &nbsp;&nbsp;|&nbsp;&nbsp; `0` → Safe ✅

**Risk Score Logic**

```
Night Transaction    → +20%
Device Changed       → +20%
Location Mismatch    → +30%
High Amount          → +30%
─────────────────────────────
Max Risk Score       = 100%
```

---

## 🔄 System Workflow

```
User Registers ──► Validation ──► SHA-256 Hash ──► users.json
     │
     ▼
   Login ──► Session Saved ──► Access Granted
     │
     ├──► Fraud Detection ──► ML Model ──► XAI + Gauge ──► user_history.json
     │
     ├──► Dashboard ──► History + Charts ──► PDF Download
     │
     └──► Admin Panel ──► Manage Users & Data
```

---

## 👥 Team

| Member | Contribution |
|---|---|
| **Khushi** | Web app development, authentication, dashboard, PDF reports, admin panel, XAI integration |
| **Soni** | Dataset sourcing, data cleaning & preprocessing, feature engineering, ML model training (Jupyter Notebook) |

---

## 📜 License

This project is built for educational and hackathon purposes only.
