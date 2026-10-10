
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme

apply_theme()

st.set_page_config(
    page_title="Customer Risk Intelligence",
    page_icon="🎯",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "European_Bank.csv"
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

st.title("High-Value Disengaged Customers")
st.caption(
    "Identify inactive customers with substantial balances "
    "or salaries for targeted retention outreach."
)

st.sidebar.header("Risk Screening Controls")

balance_threshold = st.sidebar.number_input(
    "Minimum account balance",
    min_value=0.0,
    max_value=float(df["Balance"].max()),
    value=float(df["Balance"].quantile(0.75)),
    step=5000.0,
)

salary_threshold = st.sidebar.number_input(
    "Minimum estimated annual salary",
    min_value=0.0,
    max_value=float(df["EstimatedSalary"].max()),
    value=float(df["EstimatedSalary"].quantile(0.75)),
    step=5000.0,
)

include_active = st.sidebar.checkbox(
    "Include active customers",
    value=False,
)

# Screen for high financial value
high_value = (
    (df["Balance"] >= balance_threshold)
    | (df["EstimatedSalary"] >= salary_threshold)
)

if include_active:
    risk = df[high_value].copy()
else:
    risk = df[
        high_value & (df["IsActiveMember"] == 0)
    ].copy()

risk["Risk_Segment"] = risk.apply(
    lambda row: (
        "Balance + Salary"
        if row["Balance"] >= balance_threshold
        and row["EstimatedSalary"] >= salary_threshold
        else "High Balance"
        if row["Balance"] >= balance_threshold
        else "High Salary"
    ),
    axis=1,
)

total = len(risk)
observed_churn = (
    risk["Exited"].mean() * 100 if total else 0
)
avg_balance = (
    risk["Balance"].mean() if total else 0
)


c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.metric("Customers Flagged", f"{total:,}")

with c2:
    st.metric("Observed Churn Rate", f"{observed_churn:.2f}%")

with c3:
    st.metric("Average Balance", f"{avg_balance:,.2f}")


st.info(
    "This is a screening tool based on current activity and financial "
    "thresholds, not a predictive model. Salary is estimated annual "
    "salary, not verified income. Flagged customers are not guaranteed "
    "to churn."
)

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Risk Segment Distribution")
    segment_counts = (
        risk["Risk_Segment"]
        .value_counts()
        .rename_axis("Segment")
        .reset_index(name="Customers")
    )

    fig = px.bar(
        segment_counts,
        x="Segment",
        y="Customers",
        color="Segment",
        template="plotly_dark",
    )
    fig.update_layout(
        height=380,
        autosize=True,
        showlegend=False,
        margin=dict(l=15, r=15, t=20, b=65),
        xaxis=dict(title=None, tickangle=-15, automargin=True),
        yaxis=dict(title="Customers", automargin=True),
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Balance vs Estimated Salary")
    if not risk.empty:
        fig = px.scatter(
            risk,
            x="EstimatedSalary",
            y="Balance",
            color="Exited",
            size="NumOfProducts",
            hover_data=[
                "CustomerId",
                "Geography",
                "Age",
                "IsActiveMember",
            ],
            labels={
                "EstimatedSalary": "Estimated Annual Salary",
                "Balance": "Account Balance",
                "Exited": "Exited (1 = Yes)",
            },
            template="plotly_dark",
            color_discrete_map={
                0: "#22d3ee",
                1: "#fb7185",
            },
        )
        fig.update_layout(
            height=380,
            autosize=True,
            margin=dict(l=15, r=15, t=20, b=45),
            xaxis=dict(automargin=True),
            yaxis=dict(automargin=True),
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No customers match the selected thresholds.")

st.subheader("Flagged Customer List")

columns = [
    "CustomerId",
    "Geography",
    "Age",
    "Balance",
    "EstimatedSalary",
    "NumOfProducts",
    "IsActiveMember",
    "Exited",
    "Risk_Segment",
]

st.dataframe(
    risk[columns].sort_values("Balance", ascending=False),
    use_container_width=True,
    hide_index=True,
)

csv_data = risk[columns].to_csv(index=False).encode("utf-8")

st.download_button(
    "Download flagged customers (CSV)",
    data=csv_data,
    file_name="flagged_customers.csv",
    mime="text/csv",
)
