import streamlit as st
import pandas as pd

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTcso-sK4gPLoFOWaN4Pk4-tNIIE9x9GLZTnzx913Hu32qP16Yc6UgJLEJZlMxDhzZ1Ew0DZ47udzeQ/pub?gid=272834926&single=true&output=csv"

st.set_page_config(page_title="CCTV Live Tracking", layout="wide")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Parse timestamp + numeric columns
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    for col in ["No. of Staff Present", "No. of Customer Present", "No. of Stock Boxes on Floor"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

st.title("CCTV Live Tracking — Dashboard")

# ---- Filters
c1, c2, c3 = st.columns(3)

stores = sorted(df["Select Store"].dropna().unique()) if "Select Store" in df.columns else []
users = sorted(df["User"].dropna().unique()) if "User" in df.columns else []

with c1:
    store_sel = st.multiselect("Store", stores, default=list(stores)[:1] if len(stores) else [])
with c2:
    user_sel = st.multiselect("User", users, default=[])
with c3:
    days = st.selectbox("Last N days", [1, 3, 7, 14, 30, 90], index=2)

f = df.copy()

if store_sel and "Select Store" in f.columns:
    f = f[f["Select Store"].isin(store_sel)]

if user_sel and "User" in f.columns:
    f = f[f["User"].isin(user_sel)]

if "Timestamp" in f.columns and f["Timestamp"].notna().any():
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    f = f[f["Timestamp"] >= cutoff]

# ---- KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Checks", len(f))

if "No. of Customer Present" in f.columns:
    k2.metric("Avg Customers", round(f["No. of Customer Present"].mean(), 1))
if "No. of Staff Present" in f.columns:
    k3.metric("Avg Staff", round(f["No. of Staff Present"].mean(), 1))
if "No. of Stock Boxes on Floor" in f.columns:
    k4.metric("Avg Stock Boxes", round(f["No. of Stock Boxes on Floor"].mean(), 1))

st.divider()

# ---- Staff Doing breakdown
if "Staff Doing" in f.columns:
    st.subheader("Staff Doing — Breakdown")
    doing = (
        f["Staff Doing"]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )
    doing_counts = doing.value_counts().reset_index()
    doing_counts.columns = ["Activity", "Count"]
    st.dataframe(doing_counts, use_container_width=True)

st.divider()

# ---- Store-wise averages
if "Select Store" in f.columns:
    st.subheader("Store-wise Summary (Averages)")
    cols = [c for c in ["No. of Staff Present", "No. of Customer Present", "No. of Stock Boxes on Floor"] if c in f.columns]
    if cols:
        summary = f.groupby("Select Store")[cols].mean().round(2).reset_index()
        st.dataframe(summary, use_container_width=True)

st.divider()

# ---- Latest entries table
st.subheader("Latest Entries")
show_cols = [c for c in ["Timestamp","User","Select Store","No. of Staff Present","No. of Customer Present",
                         "No. of Stock Boxes on Floor","Staff Doing","Comment","File Photo"] if c in f.columns]

if "Timestamp" in f.columns:
    f = f.sort_values("Timestamp", ascending=False)

st.dataframe(f[show_cols], use_container_width=True)