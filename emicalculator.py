import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------
# EMI Calculator Function
# ----------------------------------------------------
def emi_calculator(principal, annual_rate, tenure_years):
    monthly_rate = annual_rate / (12 * 100)
    tenure_months = tenure_years * 12

    emi = principal * monthly_rate * pow(1 + monthly_rate, tenure_months) / \
          (pow(1 + monthly_rate, tenure_months) - 1)

    balance = principal
    data = []

    total_principal_paid = 0
    total_interest_paid = 0
    total_months_paid = 0

    for year in range(1, tenure_years + 1):
        interest_year = 0
        principal_year = 0
        months_paid = 0

        for _ in range(12):
            if balance <= 0:
                break

            interest_component = balance * monthly_rate
            principal_component = emi - interest_component

            interest_year += interest_component
            principal_year += principal_component

            balance -= principal_component
            months_paid += 1

        total_principal_paid += principal_year
        total_interest_paid += interest_year
        total_months_paid += months_paid

        data.append([
            year,
            round(emi * 12, 2),
            round(principal_year, 2),
            round(interest_year, 2),
            round(max(balance, 0), 2),
            months_paid,
            round(total_principal_paid, 2),
            round(total_interest_paid, 2),
            total_months_paid
        ])

    df = pd.DataFrame(data, columns=[
        "Year", "EMI Paid (Yearly)", "Principal Paid", "Interest Paid",
        "Balance Remaining", "Months Paid",
        "Total Principal Paid Till Now", "Total Interest Paid Till Now",
        "Total Months Paid Till Now"
    ])

    return emi, df


# ----------------------------------------------------
# Streamlit UI
# ----------------------------------------------------
st.set_page_config(layout="wide")

# Updated Title
st.title("EMI Calculator for Personal Finance")

loan = st.number_input("Enter Loan Amount (₹)", min_value=1000, value=500000)
rate = st.number_input("Enter Annual Interest Rate (%)", min_value=1.0, value=8.5)
tenure = st.number_input("Enter Tenure (Years)", min_value=1, value=5)

emi, table = emi_calculator(loan, rate, tenure)

st.subheader(f"💰 Monthly EMI: ₹{round(emi, 2)}")

left, right = st.columns([1.4, 1])

# ---------------- LEFT SECTION ----------------
with left:
    st.write("### 📅 Yearly EMI Breakdown")
    st.dataframe(table, height=350)

    selected_year = st.selectbox(
        "Select Year to View Loan Status",
        options=table["Year"].tolist(),
        key="year_select"
    )

# Get selected year data
row = table[table["Year"] == selected_year].iloc[0]

# ---------------- RIGHT SECTION ----------------
with right:

    st.write(f"### 📊 Loan Pie Chart — Year {selected_year}")

    # TOTAL paid till selected year
    total_paid = row["Total Principal Paid Till Now"] + row["Total Interest Paid Till Now"]

    # Pending principal = original loan - total principal paid
    pending_principal = loan - row["Total Principal Paid Till Now"]

    # Pie chart (Paid vs Pending out of full loan)
    fig, ax = plt.subplots()
    ax.pie(
        [total_paid, pending_principal],
        labels=["Total Amount Paid", "Pending Amount"],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig)

    # Segregation Section
    st.write(f"### 🧾 Summary (Till Year {selected_year})")

    st.write(f"**Total EMI Months Completed:** {row['Total Months Paid Till Now']} months")

    st.write("### ✔ Amount Settled (Paid So Far)")
    st.write(f"- **Principal Paid:** ₹{row['Total Principal Paid Till Now']}")
    st.write(f"- **Interest Paid:** ₹{row['Total Interest Paid Till Now']}")
    st.write(f"- **Total Paid:** ₹{total_paid}")

    st.write("### ⏳ Pending Amount (Remaining Loan)")
    st.write(f"- **Pending Principal:** ₹{pending_principal}")
    st.write("- **Pending Interest:** Not applicable (future interest not charged)")
    st.write(f"- **Total Pending:** ₹{pending_principal}")

# Download CSV
csv = table.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Download EMI Table (CSV)",
    data=csv,
    file_name="emi_breakdown.csv",
    mime="text/csv"
)
