
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme

apply_theme()

# ---------------- Page configuration ----------------
st.set_page_config(
    page_title="Bank Retention Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Premium styling ----------------
st.markdown(
    """
    <style>
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }
    [data-testid="stMetric"] {
        background: #151f30;
        border: 1px solid #26354a;
        padding: 18px;
        border-radius: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load dataset ----------------
DATA_PATH = Path(__file__).parent / "European_Bank.csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()
    return data

st.sidebar.title("BANK INTELLIGENCE")
st.sidebar.caption("Customer Engagement & Retention")
st.sidebar.divider()

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info("Place European_Bank.csv in the same folder as app.py.")
    st.stop()

df = load_data(DATA_PATH)

required_columns = [
    "CustomerId", "Balance", "NumOfProducts",
    "HasCrCard", "IsActiveMember", "Exited",
]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

# ---------------- Sidebar filters ----------------
st.sidebar.subheader("Analytics Filters")

activity_options = {
    "All customers": None,
    "Active members": 1,
    "Inactive members": 0,
}
activity_label = st.sidebar.selectbox(
    "Customer activity",
    list(activity_options.keys()),
)

min_products = int(df["NumOfProducts"].min())
max_products = int(df["NumOfProducts"].max())

product_range = st.sidebar.slider(
    "Number of products",
    min_value=min_products,
    max_value=max_products,
    value=(min_products, max_products),
)


filtered = df.copy()

activity_value = activity_options[activity_label]

if activity_value is not None:
    filtered = filtered.loc[
        filtered["IsActiveMember"] == activity_value
    ]

filtered = filtered.loc[
    filtered["NumOfProducts"].between(
        product_range[0], product_range[1]
    )
]

# Verify that the filter has not removed any unexpected records.
st.sidebar.caption(
    f"Showing {len(filtered):,} of {len(df):,} customers"
)

# ---------------- Header ----------------
st.title("Customer Retention Intelligence")
st.caption(
    "PRODUCT UTILIZATION ANALYTICS  /  ENGAGEMENT  /  RETENTION"
)

total = len(filtered)
churned = int(filtered["Exited"].sum())
churn_rate = churned / total * 100 if total else 0
active_count = int((filtered["IsActiveMember"] == 1).sum())
avg_products = (
    float(filtered["NumOfProducts"].mean()) if total else 0
)

# ---------------- KPI cards ----------------
c1, c2, c3, c4 = st.columns(4)


c1.metric("Customers", f"{total:,}")
c2.metric("Churn Rate", f"{churn_rate:.2f}%")
c3.metric("Active Members", f"{active_count:,}")
c4.metric("Avg. Products", f"{avg_products:.2f}")


st.divider()

# ---------------- Charts ----------------
left, right = st.columns(2)

with left:
    st.subheader("Churn by Product Count")

    product_summary = (
        filtered.groupby("NumOfProducts", as_index=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
    )
    product_summary["Churn_Rate"] *= 100

    fig_products = px.bar(
        product_summary,
        x="NumOfProducts",
        y="Churn_Rate",
        hover_data=["Customers"],
        labels={
            "NumOfProducts": "Number of products",
            "Churn_Rate": "Churn rate (%)",
        },
        template="plotly_dark",
        color="Churn_Rate",
        color_continuous_scale=["#22d3ee", "#818cf8"],
    )
    fig_products.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=25, b=20),
    )

    st.plotly_chart(fig_products, use_container_width=True)

with right:
    st.subheader("Engagement vs Churn")

    engagement_summary = (
        filtered.groupby("IsActiveMember", as_index=False)
        .agg(
            Customers=("Exited", "size"),
            Churn_Rate=("Exited", "mean"),
        )
    )
    engagement_summary["Engagement"] = (
        engagement_summary["IsActiveMember"]
        .map({0: "Inactive", 1: "Active"})
    )
    engagement_summary["Churn_Rate"] *= 100

    fig_engagement = px.bar(
        engagement_summary,
        x="Engagement",
        y="Churn_Rate",
        text="Customers",
        labels={"Churn_Rate": "Churn rate (%)"},
        template="plotly_dark",
        color="Engagement",
        color_discrete_map={
            "Active": "#22d3ee",
            "Inactive": "#818cf8",
        },
    )
    fig_engagement.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=20, r=20, t=25, b=20),
   )

    st.plotly_chart(fig_engagement, use_container_width=True)

# ---------------- Data quality ----------------
with st.expander("Dataset validation details"):
    st.write("Dataset dimensions:", df.shape)
    st.write("Missing values:", int(df.isna().sum().sum()))
    st.write("Duplicate rows:", int(df.duplicated().sum()))
    st.write("Available columns:", list(df.columns))
    st.dataframe(filtered.head(100), use_container_width=True)

st.caption(
    "Bank Retention Intelligence | Descriptive analytics, "
    "not a causal churn prediction model."
)
