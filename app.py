import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import html
import json

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
    numeric_cols = [
        "No. of Staff Present",
        "No. of Customer Present",
        "No. of Stock Boxes on Floor",
        "Total Staff Logged In",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

st.title("CCTV Live Tracking — Dashboard")

# Placeholder so "Show Table View" can appear immediately after title
table_placeholder = st.empty()

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

# ---------- Latest entries setup ----------
if "Timestamp" in f.columns:
    f = f.sort_values("Timestamp", ascending=False)

top_n = st.slider("Show latest N entries", min_value=5, max_value=100, value=20, step=5)
latest = f.head(top_n).copy()

# Detect ratio column safely (supports both possible header names)
ratio_col = None
for candidate in ["Staff on Floor Ratio", "% Staff on Floor %"]:
    if candidate in latest.columns:
        ratio_col = candidate
        break

# Detect total logged-in column safely
total_logged_col = "Total Staff Logged In" if "Total Staff Logged In" in latest.columns else None

show_cols = [
    c for c in [
        "Timestamp",
        "User",
        "Select Store",
        "No. of Staff Present",
        "No. of Customer Present",
        "No. of Stock Boxes on Floor",
        "Staff Doing",
        "Comment",
        "File Photo",
        total_logged_col,
        ratio_col,
    ] if c and c in latest.columns
]

def fmt_value(v):
    if pd.isna(v):
        return ""
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return str(round(v, 2))
    return str(v)

def fmt_timestamp(v):
    if pd.isna(v) or v == "":
        return ""
    try:
        return pd.to_datetime(v).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(v)

def build_whatsapp_text(row):
    ts_str = fmt_timestamp(row.get("Timestamp", ""))
    store = fmt_value(row.get("Select Store", ""))
    staff_no = fmt_value(row.get("No. of Staff Present", ""))
    customers = fmt_value(row.get("No. of Customer Present", ""))
    boxes = fmt_value(row.get("No. of Stock Boxes on Floor", ""))
    doing = fmt_value(row.get("Staff Doing", ""))
    comment = fmt_value(row.get("Comment", ""))
    total_logged = fmt_value(row.get(total_logged_col, "")) if total_logged_col else ""
    ratio_val = fmt_value(row.get(ratio_col, "")) if ratio_col else ""

    parts = []
    if ts_str:
        parts.append(f"On {ts_str}")
    if store:
        parts.append(f"in {store}")
    if staff_no:
        parts.append(f"Staff: {staff_no}")
    if customers:
        parts.append(f"Customers: {customers}")
    if boxes:
        parts.append(f"Boxes: {boxes}")
    if total_logged:
        parts.append(f"Total Logged In: {total_logged}")
    if ratio_val:
        parts.append(f"Staff on Floor Ratio: {ratio_val}")
    if doing:
        parts.append(f"Doing: {doing}")
    if comment:
        parts.append(f"Comment: {comment}")

    return " | ".join(parts)

def render_latest_table_with_copy(df_table, visible_cols, ratio_col_name=None):
    if df_table.empty:
        st.info("No entries found for the selected filters.")
        return

    table_headers = visible_cols + ["Copy"]

    html_rows = []
    for i, (_, row) in enumerate(df_table.iterrows()):
        row_cells = []

        for col in visible_cols:
            val = row.get(col, "")
            if col == "Timestamp":
                display_val = fmt_timestamp(val)
            else:
                display_val = fmt_value(val)
            row_cells.append(f"<td>{html.escape(display_val)}</td>")

        copy_text = build_whatsapp_text(row)
        js_copy_text = json.dumps(copy_text)

        copy_btn = f"""
        <td style="text-align:center; white-space:nowrap;">
            <button
                onclick='navigator.clipboard.writeText({js_copy_text}).then(() => {{
                    const msg = document.getElementById("copied-msg-{i}");
                    if (msg) {{
                        msg.innerText = "Copied ✅";
                        setTimeout(() => msg.innerText = "", 1200);
                    }}
                }});'
                style="
                    border:1px solid {NAVY};
                    color:{NAVY};
                    background:white;
                    padding:6px 12px;
                    border-radius:8px;
                    cursor:pointer;
                    font-family:inherit;
                    font-size:13px;
                "
            >
                Copy
            </button>
            <div id="copied-msg-{i}" style="font-size:11px; color:{NAVY}; margin-top:4px;"></div>
        </td>
        """
        row_cells.append(copy_btn)
        html_rows.append("<tr>" + "".join(row_cells) + "</tr>")

    header_html = "".join([f"<th>{html.escape(str(h))}</th>" for h in table_headers])

    table_html = f"""
    <div style="overflow-x:auto; width:100%;">
      <table style="
          width:100%;
          border-collapse:collapse;
          font-family:Arial, sans-serif;
          font-size:14px;
          color:{NAVY};
      ">
        <thead>
          <tr>
            {header_html}
          </tr>
        </thead>
        <tbody>
          {''.join(html_rows)}
        </tbody>
      </table>
    </div>

    <style>
      table thead tr th {{
        position: sticky;
        top: 0;
        background: #111827;
        color: white;
        text-align: left;
        padding: 10px 8px;
        border: 1px solid #2b3445;
        white-space: nowrap;
      }}
      table tbody tr td {{
        padding: 10px 8px;
        border: 1px solid #2b3445;
        background: #020817;
        color: white;
        vertical-align: top;
        white-space: nowrap;
      }}
      table tbody tr:hover td {{
        background: #0f172a;
      }}
    </style>
    """

    components.html(table_html, height=min(650, 110 + (len(df_table) * 46)), scrolling=True)

# ---------- Show Table View FIRST after title ----------
with table_placeholder.container():
    with st.expander("Show Table View", expanded=True):
        render_latest_table_with_copy(latest[show_cols], show_cols, ratio_col)

st.subheader("Latest Entries (with Copy for WhatsApp)")
st.caption("Copy button is now available inside the same table view row.")
