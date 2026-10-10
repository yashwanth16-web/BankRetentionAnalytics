
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme

apply_theme()

st.set_page_config(
    page_title="Engagement Analytics",
    page_icon="👥",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "European_Bank.csv"
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

st.title("Engagement & Product Utilization")
st.caption("Customer behavior • Product depth • Retention")

# Engagement segmentation
df["Engagement_Segment"] = df.apply(
    lambda row: (
        "Inactive • High Balance"
        if row["IsActiveMember"] == 0 and row["Balance"] >= df["Balance"].quantile(0.75)
        else "Inactive • Other"
        if row["IsActiveMember"] == 0
        else "Active • Single Product"
        if row["NumOfProducts"] == 1
        else "Active • Multiple Products"
    ),
    axis=1,
)

st.sidebar.header("Segment Filters")

segments = st.sidebar.multiselect(
    "Engagement segment",
    options=sorted(df["Engagement_Segment"].unique()),
    default=sorted(df["Engagement_Segment"].unique()),
)

min_balance = int(df["Balance"].min())
max_balance = int(df["Balance"].max())

balance_range = st.sidebar.slider(
    "Account balance range",
    min_value=min_balance,
    max_value=max_balance,
    value=(min_balance, max_balance),
)

view = df[
    df["Engagement_Segment"].isin(segments)
    & df["Balance"].between(*balance_range)
].copy()

customers = len(view)
churn_rate = view["Exited"].mean() * 100 if customers else 0
active_rate = (
    view["IsActiveMember"].mean() * 100 if customers else 0
)


c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.metric("Customers in View", f"{len(view):,}")

with c2:
    churn_rate = view["Exited"].mean() * 100 if not view.empty else 0
    st.metric("Observed Churn Rate", f"{churn_rate:.2f}%")

with c3:
    active_rate = (
        view["IsActiveMember"].mean() * 100 if not view.empty else 0
    )
    st.metric("Active Customer Rate", f"{active_rate:.2f}%")



left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Customer Segment Distribution")

    counts = (
        view["Engagement_Segment"]
        .value_counts()
        .rename_axis("Segment")
        .reset_index(name="Customers")
    )

    fig = px.bar(
        counts,
        x="Segment",
        y="Customers",
        color="Segment",
        template="plotly_dark",
        color_discrete_sequence=[
            "#6366f1", "#f97316", "#10b981", "#a855f7"
        ],
    )

    fig.update_layout(
        autosize=True,
        showlegend=False,
        height=380,
        margin=dict(l=10, r=10, t=20, b=65),
        xaxis=dict(title=None, tickangle=-20, automargin=True),
        yaxis=dict(title="Customers", automargin=True),
    )

    st.plotly_chart(
        fig, use_container_width=True, key="segment_distribution"
    )

with right:
    st.subheader("Churn Rate by Segment")

    rates = (
        view.groupby("Engagement_Segment", as_index=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
    )
    rates["Churn_Rate"] *= 100

    fig = px.bar(
        rates,
        x="Engagement_Segment",
        y="Churn_Rate",
        hover_data=["Customers"],
        text="Churn_Rate",
        template="plotly_dark",
        color="Engagement_Segment",
        color_discrete_sequence=[
            "#6366f1", "#f97316", "#10b981", "#a855f7"
        ],
    )

    fig.update_traces(
        texttemplate="%{y:.2f}%",
        textposition="outside",
    )

    fig.update_layout(
        autosize=True,
        showlegend=False,
        height=380,
        margin=dict(l=10, r=10, t=20, b=65),
        xaxis=dict(title=None, tickangle=-20, automargin=True),
        yaxis=dict(title="Churn Rate (%)", automargin=True),
    )

    st.plotly_chart(
        fig, use_container_width=True, key="segment_churn"
    )


with right:
    st.subheader("Churn Rate by Segment")
    rates = (
        view.groupby("Engagement_Segment", as_index=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
    )
    rates["Churn_Rate"] *= 100

    fig = px.bar(
        rates,
        x="Engagement_Segment",
        y="Churn_Rate",
        hover_data=["Customers"],
        labels={"Churn_Rate": "Churn Rate (%)"},
        color="Churn_Rate",
        color_continuous_scale=["#22d3ee", "#818cf8"],
        template="plotly_dark",
    )
    fig.update_layout(
        autosize=True,
        showlegend=False,
        margin=dict(l=15, r=15, t=25, b=80),
        xaxis=dict(
            title="Customer Segment",
            tickangle=-20,
            automargin=True,
        ),
        yaxis=dict(
            title="Churn Rate (%)",
            automargin=True,
        ),
        coloraxis_showscale=False,
    )
fig.update_traces(
    texttemplate="%{y:.2f}%",
    textposition="outside",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("High-Balance Inactive Customers")

risk = view[
    (view["IsActiveMember"] == 0)
    & (view["Balance"] >= df["Balance"].quantile(0.75))
].copy()

st.caption(
    "High balance is defined here as the top quartile of the full dataset. "
    "This is a screening rule, not a prediction of future churn."
)

display_cols = [
    "CustomerId",
    "Geography",
    "Age",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "Exited",
]

st.write(f"Customers matching the screening rule: {len(risk):,}")
st.dataframe(
    risk[display_cols].sort_values("Balance", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.header("Product Depth & Retention")

product_analysis = (
    df.groupby("NumOfProducts", as_index=False)
    .agg(
        Customer_Count=("Exited", "size"),
        Churned_Customers=("Exited", "sum"),
        Churn_Rate=("Exited", "mean"),
    )
)

product_analysis["Churn_Rate"] = (
    product_analysis["Churn_Rate"] * 100
).round(2)

product_analysis["Retention_Rate"] = (
    100 - product_analysis["Churn_Rate"]
).round(2)

st.caption(
    "This analysis uses the complete dataset, independent of the sidebar filters."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Count by Product Count")
    fig_count = px.bar(
        product_analysis,
        x="NumOfProducts",
        y="Customer_Count",
        text="Customer_Count",
        labels={
            "NumOfProducts": "Number of Products",
            "Customer_Count": "Customers",
        },
        template="plotly_dark",
        color="Customer_Count",
        color_continuous_scale=["#22d3ee", "#818cf8"],
    )
    st.plotly_chart(fig_count, use_container_width=True)

with col2:
    st.subheader("Churn Rate by Product Count")
    fig_rate = px.bar(
        product_analysis,
        x="NumOfProducts",
        y="Churn_Rate",
        text="Churn_Rate",
        hover_data=["Customer_Count", "Churned_Customers"],
        labels={
            "NumOfProducts": "Number of Products",
            "Churn_Rate": "Churn Rate (%)",
        },
        template="plotly_dark",
        color="Churn_Rate",
        color_continuous_scale=["#22d3ee", "#818cf8"],
    )
    st.plotly_chart(fig_rate, use_container_width=True)

st.subheader("Product Depth Summary")
st.dataframe(
    product_analysis,
    use_container_width=True,
    hide_index=True,
)
