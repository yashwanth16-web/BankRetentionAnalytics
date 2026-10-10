
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme

apply_theme()

st.set_page_config(
    page_title="Retention Strength",
    page_icon="📈",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "European_Bank.csv"
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

st.title("Retention Strength Intelligence")
st.caption(
    "Understand relationship depth through engagement, "
    "product utilization, and credit-card ownership."
)

st.sidebar.header("Scoring Configuration")

engagement_weight = st.sidebar.slider(
    "Engagement weight (%)", 0, 100, 50
)
product_weight = st.sidebar.slider(
    "Product depth weight (%)", 0, 100, 35
)
card_weight = st.sidebar.slider(
    "Credit-card weight (%)", 0, 100, 15
)

weight_total = engagement_weight + product_weight + card_weight

if weight_total == 0:
    st.warning("Increase at least one scoring weight.")
    st.stop()

# Normalize the weights so their sum is 100%.
w_engagement = engagement_weight / weight_total
w_product = product_weight / weight_total
w_card = card_weight / weight_total

# Transparent, rule-based component scores.
df["Engagement_Score"] = df["IsActiveMember"] * 100

df["Product_Score"] = (
    df["NumOfProducts"].clip(lower=0, upper=2) / 2 * 100
)

df["Card_Score"] = df["HasCrCard"] * 100

df["Relationship_Strength"] = (
    df["Engagement_Score"] * w_engagement
    + df["Product_Score"] * w_product
    + df["Card_Score"] * w_card
).round(1)

df["Strength_Tier"] = pd.cut(
    df["Relationship_Strength"],
    bins=[-0.01, 39.99, 69.99, 100],
    labels=["Developing", "Moderate", "Strong"],
)

st.info(
    "The index is an illustrative, configurable score from 0 to 100. "
    "Product depth is capped at two products for scoring purposes. "
    "The thresholds and weights are analytical assumptions, not "
    "validated predictors of future retention."
)

# Filters
st.sidebar.subheader("Customer Filters")

tiers = st.sidebar.multiselect(
    "Relationship strength",
    options=["Developing", "Moderate", "Strong"],
    default=["Developing", "Moderate", "Strong"],
)

activity_filter = st.sidebar.selectbox(
    "Engagement",
    ["All", "Active", "Inactive"],
)

view = df[df["Strength_Tier"].astype(str).isin(tiers)].copy()

if activity_filter == "Active":
    view = view[view["IsActiveMember"] == 1]
elif activity_filter == "Inactive":
    view = view[view["IsActiveMember"] == 0]

total = len(view)
avg_score = (
    view["Relationship_Strength"].mean() if total else 0
)
observed_churn = view["Exited"].mean() * 100 if total else 0


c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.metric("Customers Analyzed", f"{total:,}")

with c2:
    st.metric("Average Strength Score", f"{avg_score:.1f}/100")

with c3:
    st.metric("Observed Churn Rate", f"{observed_churn:.2f}%")


left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Relationship Strength Distribution")

    fig = px.histogram(
        view,
        x="Relationship_Strength",
        nbins=20,
        color="Strength_Tier",
        template="plotly_dark",
        labels={"Relationship_Strength": "Strength Score"},
        color_discrete_map={
            "Developing": "#fb7185",
            "Moderate": "#fbbf24",
            "Strong": "#22d3ee",
        },
    )
    fig.update_layout(
        autosize=True,
        height=380,
        margin=dict(l=15, r=15, t=20, b=55),
        xaxis=dict(
            title="Relationship Strength Score",
            tickangle=0,
            automargin=True,
        ),
        yaxis=dict(
            title="Customers",
            automargin=True,
        ),
        bargap=0.12,
    )

    st.plotly_chart(fig, use_container_width=True)


with right:
    st.subheader("Churn by Strength Tier")

    tier_summary = (
        view.groupby("Strength_Tier", observed=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
        .reset_index()
    )
    tier_summary["Churn_Rate"] *= 100

    fig = px.bar(
        tier_summary,
        x="Strength_Tier",
        y="Churn_Rate",
        text="Churn_Rate",
        hover_data=["Customers"],
        template="plotly_dark",
        labels={
            "Strength_Tier": "Relationship Tier",
            "Churn_Rate": "Observed Churn (%)",
        },
        color="Strength_Tier",
        color_discrete_map={
            "Developing": "#fb7185",
            "Moderate": "#fbbf24",
            "Strong": "#22d3ee",
        },
    )

    fig.update_layout(
        height=380,
        autosize=True,
        margin=dict(l=15, r=15, t=25, b=55),
        xaxis=dict(
            title="Relationship Tier",
            tickangle=0,
            automargin=True,
        ),
        yaxis=dict(
            title="Observed Churn (%)",
            automargin=True,
        ),
        showlegend=False,
    )

    fig.update_traces(
        texttemplate="%{y:.2f}%",
        textposition="outside",
    )

    st.plotly_chart(fig, use_container_width=True)


st.subheader("Relationship Strength Summary")
st.dataframe(
    tier_summary,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Customer-Level Scores")

display_columns = [
    "CustomerId",
    "IsActiveMember",
    "NumOfProducts",
    "HasCrCard",
    "Engagement_Score",
    "Product_Score",
    "Card_Score",
    "Relationship_Strength",
    "Strength_Tier",
    "Exited",
]

st.dataframe(
    view[display_columns].sort_values(
        "Relationship_Strength", ascending=True
    ),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download retention strength scores",
    data=view[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="retention_strength_scores.csv",
    mime="text/csv",
)
