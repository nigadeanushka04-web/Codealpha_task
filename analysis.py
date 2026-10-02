
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "Unemployment in India.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

RATE = "Estimated Unemployment Rate (%)"
EMP = "Estimated Employed"
LFPR = "Estimated Labour Participation Rate (%)"

def load_clean_data():
    df = pd.read_csv(DATA)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Region"] = df["Region"].astype(str).str.strip()
    df["Area"] = df["Area"].astype(str).str.strip()
    df["Frequency"] = df["Frequency"].astype(str).str.strip()
    for c in [RATE, EMP, LFPR]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Date", RATE]).drop_duplicates()
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Period"] = np.where(
        (df["Date"] >= "2019-05-01") & (df["Date"] <= "2020-02-29"),
        "Pre-COVID",
        np.where(
            (df["Date"] >= "2020-03-01") & (df["Date"] <= "2020-06-30"),
            "COVID shock",
            "Post-shock"
        )
    )
    return df

def main():
    df = load_clean_data()

    monthly = (df.groupby("Date", as_index=False)
                 .agg(Unemployment_Rate=(RATE, "mean"),
                      Estimated_Employed=(EMP, "mean"),
                      Labour_Participation=(LFPR, "mean")))
    monthly.to_csv(OUT / "monthly_national_summary.csv", index=False)

    state = (df.groupby("Region", as_index=False)
               .agg(Avg_Unemployment_Rate=(RATE, "mean"),
                    Avg_Employed=(EMP, "mean"),
                    Avg_LFPR=(LFPR, "mean"))
               .sort_values("Avg_Unemployment_Rate", ascending=False))
    state.to_csv(OUT / "state_summary.csv", index=False)

    area = (df.groupby("Area", as_index=False)
              .agg(Avg_Unemployment_Rate=(RATE, "mean"),
                   Avg_Employed=(EMP, "mean"),
                   Avg_LFPR=(LFPR, "mean")))
    area.to_csv(OUT / "area_summary.csv", index=False)

    seasonal = (df.groupby("Month_Name", as_index=False)
                  .agg(Avg_Unemployment_Rate=(RATE, "mean")))
    order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seasonal["Month_Name"] = pd.Categorical(seasonal["Month_Name"], categories=order, ordered=True)
    seasonal = seasonal.sort_values("Month_Name")
    seasonal.to_csv(OUT / "monthly_seasonal_summary.csv", index=False)

    period = (df.groupby("Period", as_index=False)
                .agg(Avg_Unemployment_Rate=(RATE, "mean"),
                     Avg_Employed=(EMP, "mean"),
                     Avg_LFPR=(LFPR, "mean"),
                     Records=(RATE, "size")))
    period.to_csv(OUT / "covid_period_summary.csv", index=False)

    # National trend
    plt.figure(figsize=(11,5))
    plt.plot(monthly["Date"], monthly["Unemployment_Rate"], marker="o")
    plt.title("Average Unemployment Rate Over Time")
    plt.xlabel("Date")
    plt.ylabel("Unemployment Rate (%)")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "national_unemployment_trend.png", dpi=160)
    plt.close()

    # State comparison
    top = state.head(10).sort_values("Avg_Unemployment_Rate")
    plt.figure(figsize=(9,5))
    plt.barh(top["Region"], top["Avg_Unemployment_Rate"])
    plt.title("Top 10 Regions by Average Unemployment Rate")
    plt.xlabel("Average Unemployment Rate (%)")
    plt.tight_layout()
    plt.savefig(OUT / "top_regions.png", dpi=160)
    plt.close()

    # Seasonal
    plt.figure(figsize=(10,5))
    plt.plot(seasonal["Month_Name"].astype(str), seasonal["Avg_Unemployment_Rate"], marker="o")
    plt.title("Average Unemployment Rate by Calendar Month")
    plt.xlabel("Month")
    plt.ylabel("Average Unemployment Rate (%)")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "seasonal_trend.png", dpi=160)
    plt.close()

    # COVID comparison
    covid = period.set_index("Period")
    pre = covid.loc["Pre-COVID", "Avg_Unemployment_Rate"] if "Pre-COVID" in covid.index else np.nan
    shock = covid.loc["COVID shock", "Avg_Unemployment_Rate"] if "COVID shock" in covid.index else np.nan
    change = shock - pre if pd.notna(pre) and pd.notna(shock) else np.nan

    with open(OUT / "key_findings.txt", "w", encoding="utf-8") as f:
        f.write("KEY FINDINGS\n")
        f.write("============\n")
        f.write(f"Rows after cleaning: {len(df):,}\n")
        f.write(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}\n")
        f.write(f"Overall average unemployment rate: {df[RATE].mean():.2f}%\n")
        f.write(f"Overall median unemployment rate: {df[RATE].median():.2f}%\n")
        f.write(f"Highest observed unemployment rate: {df[RATE].max():.2f}%\n")
        if pd.notna(pre) and pd.notna(shock):
            f.write(f"Pre-COVID average: {pre:.2f}%\n")
            f.write(f"COVID-shock average: {shock:.2f}%\n")
            f.write(f"COVID-shock minus pre-COVID: {change:+.2f} percentage points\n")
        f.write(f"Highest-average region: {state.iloc[0]['Region']} ({state.iloc[0]['Avg_Unemployment_Rate']:.2f}%)\n")
        f.write(f"Lowest-average region: {state.iloc[-1]['Region']} ({state.iloc[-1]['Avg_Unemployment_Rate']:.2f}%)\n")

    print("Analysis complete. Files saved in outputs/")

if __name__ == "__main__":
    main()
