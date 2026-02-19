import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Step 1 — Load and prepare
# -------------------------

# Load data
df = pd.read_csv("input/PaidSearch.csv")

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Create log revenue
df["log_revenue"] = np.log(df["revenue"])


# -------------------------
# Step 2 — Pivot tables
# -------------------------

# Treatment group: search turned OFF after May 22
treated = df[df["search_stays_on"] == 0]

treated_pivot = treated.pivot_table(
    index="dma",
    columns="treatment_period",
    values="log_revenue",
    aggfunc="mean"
)

# Rename columns
treated_pivot = treated_pivot.rename(columns={
    0: "log_revenue_pre",
    1: "log_revenue_post"
})

# Compute difference
treated_pivot["log_revenue_diff"] = (
    treated_pivot["log_revenue_post"] - treated_pivot["log_revenue_pre"]
)

# Save
treated_pivot.to_csv("temp/treated_pivot.csv")


# Control group: search stays ON
untreated = df[df["search_stays_on"] == 1]

untreated_pivot = untreated.pivot_table(
    index="dma",
    columns="treatment_period",
    values="log_revenue",
    aggfunc="mean"
)

# Rename columns
untreated_pivot = untreated_pivot.rename(columns={
    0: "log_revenue_pre",
    1: "log_revenue_post"
})

# Compute difference
untreated_pivot["log_revenue_diff"] = (
    untreated_pivot["log_revenue_post"] - untreated_pivot["log_revenue_pre"]
)

# Save
untreated_pivot.to_csv("temp/untreated_pivot.csv")

# -------------------------
# Step 3 — Summary stats
# -------------------------

num_treated = df[df["search_stays_on"] == 0]["dma"].nunique()
num_untreated = df[df["search_stays_on"] == 1]["dma"].nunique()

start_date = df["date"].min().date()
end_date = df["date"].max().date()

print(f"Treated DMAs: {num_treated}")
print(f"Untreated DMAs: {num_untreated}")
print(f"Date range: {start_date} to {end_date}")

# -------------------------
# Step 4 — Figure 5.2
# -------------------------

# Compute average revenue by date and group
avg_revenue = (
    df.groupby(["date", "search_stays_on"])["revenue"]
      .mean()
      .reset_index()
)

# Separate groups
control = avg_revenue[avg_revenue["search_stays_on"] == 1]
treatment = avg_revenue[avg_revenue["search_stays_on"] == 0]

# Plot
plt.figure(figsize=(10, 6))

plt.plot(control["date"], control["revenue"],
         label="Control (search stays on)")

plt.plot(treatment["date"], treatment["revenue"],
         label="Treatment (search goes off)")

# Vertical treatment line
plt.axvline(pd.to_datetime("2012-05-22"),
            linestyle="--")

plt.xlabel("Date")
plt.ylabel("Revenue")
plt.title("Average Revenue by Group Over Time")
plt.legend()

plt.tight_layout()
plt.savefig("output/figures/figure_5_2.png")
plt.close()

# -------------------------
# Step 5 — Figure 5.3
# -------------------------

# Compute average log revenue by date and group
avg_log = (
    df.groupby(["date", "search_stays_on"])["log_revenue"]
      .mean()
      .reset_index()
)

# Pivot so each group becomes a column
pivot_log = avg_log.pivot(
    index="date",
    columns="search_stays_on",
    values="log_revenue"
)

# Compute difference: control (1) - treatment (0)
pivot_log["log_diff"] = pivot_log[1] - pivot_log[0]

# Plot
plt.figure(figsize=(10, 6))

plt.plot(pivot_log.index, pivot_log["log_diff"])

# Treatment date line
plt.axvline(pd.to_datetime("2012-05-22"),
            linestyle="--")

plt.xlabel("Date")
plt.ylabel("log(rev_control) - log(rev_treat)")
plt.title("Log Revenue Difference Over Time")

plt.tight_layout()
plt.savefig("output/figures/figure_5_3.png")
plt.close()
