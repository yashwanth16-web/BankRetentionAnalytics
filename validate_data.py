
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).parent / "European_Bank.csv"

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

print("\n========== DATASET OVERVIEW ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Column names:", df.columns.tolist())

print("\n========== DATA QUALITY ==========")
print("Missing values:", int(df.isna().sum().sum()))
print("Duplicate rows:", int(df.duplicated().sum()))
print("Duplicate customer IDs:", int(df["CustomerId"].duplicated().sum()))

print("\n========== BINARY FIELD VALIDATION ==========")
for col in ["Exited", "IsActiveMember", "HasCrCard"]:
    print(f"\n{col} values:")
    print(df[col].value_counts(dropna=False).sort_index())

    unexpected = set(df[col].dropna().unique()) - {0, 1}
    print("Unexpected values:", unexpected)

print("\n========== PRODUCT COUNT ==========")
print(df["NumOfProducts"].value_counts().sort_index())

print("\n========== CHURN RATE ==========")
print("Overall churn (%):", round(df["Exited"].mean() * 100, 2))

print("\nChurn by activity (%):")
print(
    (df.groupby("IsActiveMember")["Exited"].mean() * 100)
    .round(2)
)

print("\nChurn by product count (%):")
print(
    (df.groupby("NumOfProducts")["Exited"].mean() * 100)
    .round(2)
)

print("\n========== VALIDATION FINISHED ==========")
