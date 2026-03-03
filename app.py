import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTcso-sK4gPLoFOWaN4Pk4-tNIIE9x9GLZTnzx913Hu32qP16Yc6UgJLEJZlMxDhzZ1Ew0DZ47udzeQ/pub?gid=272834926&single=true&output=csv"

st.set_page_config(page_title="CCTV Live Tracking", layout="wide")

# ---------- UI (Navy on White) ----------
NAVY = "#0b1f3b"
st.markdown(
    f"""
    <style>
      .stApp {{
        background: white;
        color: {NAVY};
      }}
      h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: {NAVY} !important;
      }}
      /* Make sidebar white too */
      section[data-testid="stSidebar"] {{
        background: white;
      }}
      /* Buttons */
      .stButton>button {{
        border: 1px solid {NAVY};
        color: {NAVY};
        background: white;
        border-radius: 10px;
      }}
      .stButton>button:hover {{
        opacity: 0.9;
      }}
      /* Dataframe header color */
      div[data-testid="stDataFrame"] * {{
        color: {NAVY} !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Parse timestamp
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)

    # Numeric columns cleanup
    for col in ["No. of Staff Present", "No. of Customer Present", "No. of Stock Boxes on Floor"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

st.title("CCTV Live Tracking — Dashboard")

# ---------- Filters ----------
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.6])

stores = sorted(df["Select Store"].dropna().unique()) if "Select Store" in df.columns else []
users = sorted(df["User"].dropna().unique()) if "User" in df.columns else []

with c1:
    store_sel = st.multiselect("Store", stores, default=list(stores)[:1] if len(stores) else [])
with c2:
    user_sel = st.multiselect("User", users, default=[])

# Date range filter
min_date = None
max_date = None
if "Timestamp" in df.columns and df["Timestamp"].notna().any():
    min_date = df["Timestamp"].min().date()
    max_date = df["Timestamp"].max().date()

with c3:
    start_date = st.date_input("Start date", value=min_date if min_date else None)
with c4:
    end_date = st.date_input("End date", value=max_date if max_date else None)

f = df.copy()

if store_sel and "Select Store" in f.columns:
    f = f[f["Select Store"].isin(store_sel)]

if user_sel and "User" in f.columns:
    f = f[f["User"].isin(user_sel)]

if "Timestamp" in f.columns and f["Timestamp"].notna().any() and start_date and end_date:
    # include full end date
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    f = f[(f["Timestamp"] >= start_ts) & (f["Timestamp"] <= end_ts)]

# ---------- KPIs ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Checks", int(len(f)))

if "No. of Customer Present" in f.columns:
    k2.metric("Avg Customers", round(f["No. of Customer Present"].mean(), 1) if len(f) else 0)
if "No. of Staff Present" in f.columns:
    k3.metric("Avg Staff", round(f["No. of Staff Present"].mean(), 1) if len(f) else 0)
if "No. of Stock Boxes on Floor" in f.columns:
    k4.metric("Avg Stock Boxes", round(f["No. of Stock Boxes on Floor"].mean(), 1) if len(f) else 0)

st.divider()

# ---------- Staff Doing breakdown ----------
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
    st.dataframe(doing_counts, use_container_width=True, hide_index=True)

st.divider()

# ---------- Store-wise summary ----------
if "Select Store" in f.columns:
    st.subheader("Store-wise Summary (Averages)")
    cols = [c for c in ["No. of Staff Present", "No. of Customer Present", "No. of Stock Boxes on Floor"] if c in f.columns]
    if cols:
        summary = f.groupby("Select Store")[cols].mean().round(2).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)

st.divider()

# ---------- Helper: Copy button (clipboard) ----------
def copy_button(text_to_copy: str, button_label: str = "Copy"):
    safe_text = (
        text_to_copy
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("\n", " ")
        .replace("\r", " ")
    )

    html = f"""
    <div style="display:flex; gap:10px; align-items:center;">
      <button
        style="
          border:1px solid {NAVY};
          color:{NAVY};
          background:white;
          padding:6px 12px;
          border-radius:10px;
          cursor:pointer;
          font-family:inherit;
        "
        onclick="navigator.clipboard.writeText(`{safe_text}`).then(()=>{{ 
          const el = document.getElementById('copied-msg');
          if (el) {{ el.innerText = 'Copied ✅'; setTimeout(()=>el.innerText='', 1200); }}
        }});"
      >
        {button_label}
      </button>
      <span id="copied-msg" style="font-size:12px; color:{NAVY};"></span>
    </div>
    """
    components.html(html, height=45)

# ---------- Latest Entries with Copy per row ----------
st.subheader("Latest Entries (with Copy for WhatsApp)")

# Sort latest first
if "Timestamp" in f.columns:
    f = f.sort_values("Timestamp", ascending=False)

show_cols = [c for c in [
    "Timestamp","User","Select Store","No. of Staff Present","No. of Customer Present",
    "No. of Stock Boxes on Floor","Staff Doing","Comment","File Photo"
] if c in f.columns]

# Show top N
top_n = st.slider("Show latest N entries", min_value=5, max_value=100, value=20, step=5)
latest = f.head(top_n).copy()

# Render each row as a card + copy button
for idx, row in latest.iterrows():
    ts = row.get("Timestamp", "")
    store = row.get("Select Store", "")
    staff_no = row.get("No. of Staff Present", "")
    doing = row.get("Staff Doing", "")
    comment = row.get("Comment", "")

    # Format timestamp nicely
    if pd.notna(ts) and ts != "":
        try:
            ts_str = pd.to_datetime(ts).strftime("%d/%m/%Y %H:%M")
        except Exception:
            ts_str = str(ts)
    else:
        ts_str = ""

    whatsapp_text = f"On {ts_str} in {store} | Staff: {staff_no} | Doing: {doing} | Comment: {comment}"

    with st.container(border=True):
        cA, cB = st.columns([4, 1.2])

        with cA:
            # show key info
            st.write(f"**{ts_str}**  •  **Store:** {store}  •  **Staff:** {staff_no}")
            if "No. of Customer Present" in row:
                st.write(f"**Customers:** {row.get('No. of Customer Present', '')}  •  **Boxes:** {row.get('No. of Stock Boxes on Floor', '')}")
            if doing:
                st.write(f"**Staff Doing:** {doing}")
            if comment:
                st.write(f"**Comment:** {comment}")

        with cB:
            copy_button(whatsapp_text, "Copy")

# Also keep a raw table below (optional)
with st.expander("Show table view"):
    st.dataframe(latest[show_cols], use_container_width=True, hide_index=True)
