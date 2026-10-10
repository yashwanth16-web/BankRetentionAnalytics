
from pathlib import Path
import pandas as pd

path = Path(__file__).parent / "European_Bank.csv"
df = pd.read_csv(path)
df.columns = df.columns.str.strip()

print("\n========== DATA QUALITY REPORT ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Missing values:", int(df.isna().sum().sum()))
print("Duplicate rows:", int(df.duplicated().sum()))
print("Duplicate CustomerIds:", int(df["CustomerId"].duplicated().sum()))

print("\n========== COLUMN VALIDATION ==========")
print("Columns:", df.columns.tolist())

for col in ["Exited", "IsActiveMember", "HasCrCard"]:
    invalid = sorted(set(df[col].dropna().unique()) - {0, 1})
    print(f"{col} invalid binary values: {invalid}")

print("\n========== CUSTOMER COUNTS ==========")
print("All dataset rows:", len(df))
print("Unique customers:", df["CustomerId"].nunique())
print("Active customers:", int((df["IsActiveMember"] == 1).sum()))
print("Inactive customers:", int((df["IsActiveMember"] == 0).sum()))
print("Exited customers:", int((df["Exited"] == 1).sum()))
print("Retained customers:", int((df["Exited"] == 0).sum()))

print("\n========== PRODUCT COUNTS ==========")
print(df["NumOfProducts"].value_counts().sort_index())

print("\n========== CHURN VALIDATION ==========")
print("Overall churn rate:", round(df["Exited"].mean() * 100, 2), "%")
print("\nChurn by product count:")
print(
    df.groupby("NumOfProducts")["Exited"]
    .agg(Customers="size", Churned="sum", Churn_Rate="mean")
    .assign(Churn_Rate=lambda x: (x["Churn_Rate"] * 100).round(2))
)

print("\n========== REPORT COMPLETE ==========")
