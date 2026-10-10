
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme

apply_theme()

st.set_page_config(
    page_title="Executive Retention Overview",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "European_Bank.csv"
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

st.title("Executive Retention Overview")
st.caption(
    "CUSTOMER ENGAGEMENT  /  PRODUCT UTILIZATION  /  RETENTION STRATEGY"
)

# Executive KPIs
total = len(df)
churned = int(df["Exited"].sum())
retained = total - churned
churn_rate = df["Exited"].mean() * 100
active_churn = df.loc[df["IsActiveMember"] == 1, "Exited"].mean() * 100
inactive_churn = df.loc[df["IsActiveMember"] == 0, "Exited"].mean() * 100


c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    st.metric("Total Customers", f"{len(df):,}")

with c2:
    retention_rate = (1 - df["Exited"].mean()) * 100 if not df.empty else 0
    st.metric("Retention Rate", f"{retention_rate:.2f}%")

with c3:
    churn_rate = df["Exited"].mean() * 100 if not df.empty else 0
    st.metric("Churn Rate", f"{churn_rate:.2f}%")

with c4:
    exited_customers = int(df["Exited"].sum())
    st.metric("Exited Customers", f"{exited_customers:,}")


st.divider()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Engagement Impact")

    engagement = (
        df.groupby("IsActiveMember", as_index=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
    )
    engagement["Churn_Rate"] *= 100
    engagement["Segment"] = engagement["IsActiveMember"].map(
        {0: "Inactive", 1: "Active"}
    )

    fig = px.bar(
        engagement,
        x="Segment",
        y="Churn_Rate",
        text="Churn_Rate",
        hover_data=["Customers"],
        labels={"Churn_Rate": "Observed churn (%)"},
        template="plotly_dark",
        color="Segment",
        color_discrete_map={
            "Active": "#22d3ee",
            "Inactive": "#fb7185",
        },
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Product Depth Impact")

    products = (
        df.groupby("NumOfProducts", as_index=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
    )
    products["Churn_Rate"] *= 100

    fig = px.bar(
        products,
        x="NumOfProducts",
        y="Churn_Rate",
        text="Churn_Rate",
        hover_data=["Customers"],
        labels={
            "NumOfProducts": "Number of products",
            "Churn_Rate": "Observed churn (%)",
        },
        template="plotly_dark",
        color="Churn_Rate",
        color_continuous_scale=["#22d3ee", "#818cf8"],
    )
    fig.update_layout(
        height=380,
        autosize=True,
        margin=dict(l=15, r=15, t=25, b=55),
        xaxis=dict(
            title="Number of Products",
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


st.divider()
st.header("Executive Findings")

engagement_gap = inactive_churn - active_churn

st.markdown(
    f"""
    **1. Engagement is associated with retention.**  
    Inactive customers have an observed churn rate of **{inactive_churn:.2f}%**,
    compared with **{active_churn:.2f}%** among active customers.
    This is a difference of **{engagement_gap:.2f} percentage points**.

    **2. Product count has a non-linear relationship with churn.**  
    Customers with two products show lower observed churn than customers
    with one product. However, the three-product and four-product groups
    are much smaller and have substantially higher observed churn.

    **3. Financial value alone should not define customer priority.**  
    Combine engagement indicators with balance, product usage, and
    observed customer behavior to identify segments for further review.
    """
)

st.subheader("Recommended Retention Actions")

st.markdown(
    """
    - **Re-engagement:** Test targeted outreach for inactive customers.
    - **Product review:** Investigate why customers with three or four
      products have high observed churn before changing product bundles.
    - **Premium customer care:** Review inactive, high-balance customers
      for relevant service or relationship-building opportunities.
    - **Measurement:** Track campaign response, subsequent activity,
      and churn over time to evaluate whether interventions work.
    """
)

st.caption(
    "Findings are descriptive associations from the supplied dataset. "
    "They do not establish causation or predict future churn."
)
