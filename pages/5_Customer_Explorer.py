
from pathlib import Path

import pandas as pd
import streamlit as st


# Load shared project theme
CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "style.css"

if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Customer Explorer",
    page_icon="🔎",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "European_Bank.csv"
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

st.title("Customer Explorer")
st.caption(
    "Search, filter, and inspect customer engagement, "
    "product utilization, and retention outcomes."
)

# Search and filters
st.sidebar.header("Customer Search")

search_id = st.sidebar.text_input(
    "Customer ID",
    placeholder="Enter a customer ID",
)

geographies = ["All"] + sorted(df["Geography"].dropna().unique().tolist())
geography = st.sidebar.selectbox("Geography", geographies)

activity = st.sidebar.selectbox(
    "Engagement status",
    ["All", "Active", "Inactive"],
)

churn_status = st.sidebar.selectbox(
    "Customer outcome",
    ["All", "Retained", "Exited"],
)

min_age = int(df["Age"].min())
max_age = int(df["Age"].max())

age_range = st.sidebar.slider(
    "Customer age",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age),
)

product_values = sorted(df["NumOfProducts"].dropna().unique().tolist())
product_selection = st.sidebar.multiselect(
    "Number of products",
    options=product_values,
    default=product_values,
)

view = df.copy()

if search_id.strip():
    if not search_id.strip().isdigit():
        st.warning("Enter a numeric Customer ID.")
        st.stop()

    view = view[
        view["CustomerId"].astype(str).str.contains(
            search_id.strip(), regex=False
        )
    ]

if geography != "All":
    view = view[view["Geography"] == geography]

if activity == "Active":
    view = view[view["IsActiveMember"] == 1]
elif activity == "Inactive":
    view = view[view["IsActiveMember"] == 0]

if churn_status == "Retained":
    view = view[view["Exited"] == 0]
elif churn_status == "Exited":
    view = view[view["Exited"] == 1]

view = view[view["Age"].between(*age_range)]
view = view[view["NumOfProducts"].isin(product_selection)]

# Summary
total = len(view)
churned = int(view["Exited"].sum()) if total else 0
churn_rate = view["Exited"].mean() * 100 if total else 0

c1, c2, c3 = st.columns(3)
c1.metric("Matching Customers", f"{total:,}")
c2.metric("Exited Customers", f"{churned:,}")
c3.metric("Observed Churn Rate", f"{churn_rate:.2f}%")

st.divider()

st.subheader("Customer Records")

display_columns = [
    "CustomerId",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited",
]

st.dataframe(
    view[display_columns].sort_values("CustomerId"),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Export filtered customers",
    data=view[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="filtered_customers.csv",
    mime="text/csv",
)

st.caption(
    "Customer-level records are shown for analytical exploration. "
    "Observed exit status is historical, not a forecast of future churn."
)
