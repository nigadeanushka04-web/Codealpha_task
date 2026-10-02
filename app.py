
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Unemployment Analysis", page_icon="📊", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "Unemployment in India.csv"

RATE = "Estimated Unemployment Rate (%)"
EMP = "Estimated Employed"
LFPR = "Estimated Labour Participation Rate (%)"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Region"] = df["Region"].astype(str).str.strip()
    df["Area"] = df["Area"].astype(str).str.strip()
    df["Frequency"] = df["Frequency"].astype(str).str.strip()
    for c in [RATE, EMP, LFPR]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Date", RATE]).drop_duplicates().sort_values("Date")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["COVID_Period"] = np.where(
        (df["Date"] >= "2019-05-01") & (df["Date"] <= "2020-02-29"),
        "Pre-COVID",
        np.where((df["Date"] >= "2020-03-01") & (df["Date"] <= "2020-06-30"),
                 "COVID shock", "Post-shock")
    )
    return df

df = load_data()

st.title("📊 Unemployment Analysis with Python")
st.caption("Exploration of unemployment trends, regional differences, seasonality, and the COVID-19 shock.")

with st.sidebar:
    st.header("Filters")
    regions = st.multiselect("Region", sorted(df["Region"].unique()), default=[])
    areas = st.multiselect("Area", sorted(df["Area"].unique()), default=[])
    min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

filtered = df.copy()
if regions:
    filtered = filtered[filtered["Region"].isin(regions)]
if areas:
    filtered = filtered[filtered["Area"].isin(areas)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = filtered[(filtered["Date"].dt.date >= date_range[0]) & (filtered["Date"].dt.date <= date_range[1])]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average unemployment", f"{filtered[RATE].mean():.2f}%")
c2.metric("Median unemployment", f"{filtered[RATE].median():.2f}%")
c3.metric("Highest observed", f"{filtered[RATE].max():.2f}%")
c4.metric("Records", f"{len(filtered):,}")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trend", "🦠 COVID-19", "🗺️ Regions", "📅 Seasonality"])

with tab1:
    st.subheader("National / filtered unemployment trend")
    trend = filtered.groupby("Date", as_index=False)[RATE].mean().set_index("Date")
    st.line_chart(trend)
    st.subheader("Employment and labour participation")
    cols = [c for c in [EMP, LFPR] if c in filtered.columns]
    if cols:
        st.line_chart(filtered.groupby("Date")[cols].mean())

with tab2:
    st.subheader("COVID-19 period comparison")
    covid = filtered.groupby("COVID_Period", as_index=False).agg(
        Avg_Unemployment=(RATE, "mean"),
        Avg_Employed=(EMP, "mean"),
        Avg_LFPR=(LFPR, "mean"),
        Records=(RATE, "size")
    )
    st.dataframe(covid, use_container_width=True)
    st.bar_chart(covid.set_index("COVID_Period")["Avg_Unemployment"])
    st.info("The COVID shock window is defined here as March–June 2020. This is an analytical grouping for the project, not a causal estimate.")

with tab3:
    st.subheader("Regional comparison")
    region = filtered.groupby("Region", as_index=False).agg(
        Avg_Unemployment=(RATE, "mean"),
        Avg_Employed=(EMP, "mean"),
        Avg_LFPR=(LFPR, "mean")
    ).sort_values("Avg_Unemployment", ascending=False)
    st.dataframe(region, use_container_width=True)
    st.bar_chart(region.set_index("Region")["Avg_Unemployment"].head(15))

with tab4:
    st.subheader("Calendar-month pattern")
    order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seasonal = filtered.groupby("Month_Name", as_index=False)[RATE].mean()
    seasonal["Month_Name"] = pd.Categorical(seasonal["Month_Name"], categories=order, ordered=True)
    seasonal = seasonal.sort_values("Month_Name").set_index("Month_Name")
    st.line_chart(seasonal)
    st.caption("Monthly averages describe recurring calendar patterns in this dataset; they should not automatically be interpreted as causal seasonality.")

st.subheader("Dataset preview")
st.dataframe(filtered.head(20), use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data", csv, "filtered_unemployment.csv", "text/csv")
