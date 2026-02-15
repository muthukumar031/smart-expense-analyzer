import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os


# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Expense Analyzer", layout="centered")

USERS_FILE = "users.csv"
EXPENSE_FILE = "expenses.csv"

# ---------------- FILE INITIALIZATION ----------------
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(EXPENSE_FILE):
    pd.DataFrame(columns=["username", "date", "category", "amount", "payment"]).to_csv(EXPENSE_FILE, index=False)

users_df = pd.read_csv(USERS_FILE)
expense_df = pd.read_csv(EXPENSE_FILE)

# ---------------- AUTHENTICATION ----------------
st.title("💰 Smart Expense Analyzer")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# -------- Register --------
if choice == "Register":
    st.subheader("📝 Create Account")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if u in users_df["username"].values:
            st.warning("User already exists")
        else:
            users_df.loc[len(users_df)] = [u, p]
            users_df.to_csv(USERS_FILE, index=False)
            st.success("Registered successfully")

# -------- Login --------
elif choice == "Login":
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if ((users_df["username"] == u) & (users_df["password"] == p)).any():
            st.session_state["user"] = u
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- MAIN APPLICATION ----------------
if "user" in st.session_state:
    user = st.session_state["user"]
    st.sidebar.success(f"Logged in as {user}")

    # -------- Add Expense --------
    st.header("➕ Add Expense")
    with st.form("expense_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"])
        amount = st.number_input("Amount", min_value=1)
        payment = st.selectbox("Payment Mode", ["Cash", "UPI", "Card"])
        submit = st.form_submit_button("Add Expense")

    if submit:
        expense_df.loc[len(expense_df)] = [user, date, category, amount, payment]
        expense_df.to_csv(EXPENSE_FILE, index=False)
        st.success("Expense added successfully")

    # -------- Analysis --------
    st.header("📊 Expense Analysis")
    user_df = expense_df[expense_df["username"] == user]

    if not user_df.empty:
        user_df["date"] = pd.to_datetime(user_df["date"])
        user_df["month"] = user_df["date"].dt.to_period("M")
        user_df["week"] = user_df["date"].dt.to_period("W")

        # Weekly Analysis
        st.subheader("📅 Weekly Expense")
        weekly = user_df.groupby("week")["amount"].sum()
        fig1, ax1 = plt.subplots()
        ax1.plot(weekly.index.astype(str), weekly.values, marker="o")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        # Monthly Analysis
        st.subheader("📆 Monthly Expense")
        monthly = user_df.groupby("month")["amount"].sum()
        fig2, ax2 = plt.subplots()
        ax2.bar(monthly.index.astype(str), monthly.values)
        st.pyplot(fig2)

        # -------- Prediction --------
        st.subheader("🔮 Next Month Prediction")

        valid_months = []
        for m in user_df["month"].unique():
            days = user_df[user_df["month"] == m]["date"].dt.day.nunique()
            if days >= 25:
                valid_months.append(m)

        if len(valid_months) >= 2:
            valid_df = user_df[user_df["month"].isin(valid_months)]
            final_monthly = valid_df.groupby("month")["amount"].sum()

            X = np.arange(len(final_monthly)).reshape(-1, 1)
            y = final_monthly.values

            model = LinearRegression()
            model.fit(X, y)

            prediction = model.predict([[len(final_monthly)]])
            st.success(f"Estimated Next Month Expense: ₹ {int(prediction[0])}")
        else:
            st.warning("Prediction requires at least 2 months with 25+ days data")

    else:
        st.info("No expense data available")

    # -------- Logout --------
    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.rerun()


