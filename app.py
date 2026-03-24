import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import html
import json

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTcso-sK4gPLoFOWaN4Pk4-tNIIE9x9GLZTnzx913Hu32qP16Yc6UgJLEJZlMxDhzZ1Ew0DZ47udzeQ/pub?gid=272834926&single=true&output=csv"

st.set_page_config(page_title="CCTV Live Tracking", layout="wide")

# -------------------- THEME --------------------
BG = "#ffffff"
TEXT = "#0b1f3b"
BORDER = "#d0d7e2"
TABLE_BG = "#020817"
TABLE_BG_2 = "#111827"
TABLE_LINE = "#2b3445"
WHITE = "#ffffff"
ACCENT = "#dd5656"

st.markdown(
    f"""
    <style>
      :root {{
        --gg-bg: #ffffff;
        --gg-text: #0b1f3b;
        --gg-border: #cbd5e1;
        --gg-soft: #f8fafc;
        --gg-table: #020817;
        --gg-table-2: #111827;
        --gg-line: #2b3445;
        --gg-white: #ffffff;
      }}

      .stApp {{
        background: var(--gg-bg);
        color: var(--gg-text);
      }}

      body {{
        color: var(--gg-text);
      }}

      h1, h2, h3, h4, h5, h6,
      p,
      label,
      .stMarkdown,
      .stText,
      .stCaption {{
        color: var(--gg-text) !important;
      }}

      .stButton > button {{
        border: 1px solid var(--gg-text);
        color: var(--gg-text);
        background: #ffffff;
        border-radius: 10px;
        font-weight: 600;
      }}

      .stButton > button:hover {{
        background: var(--gg-soft);
        color: var(--gg-text);
        border: 1px solid var(--gg-text);
      }}

      /* -------- SELECT / MULTISELECT FIELD -------- */
      div[data-baseweb="select"] {{
        color: var(--gg-text) !important;
      }}

      div[data-baseweb="select"] > div {{
        background: #ffffff !important;
        border: 1px solid var(--gg-border) !important;
        color: var(--gg-text) !important;
      }}

      div[data-baseweb="select"] input {{
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
        opacity: 1 !important;
      }}

      div[data-baseweb="select"] span {{
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
        opacity: 1 !important;
      }}

      div[data-baseweb="tag"] {{
        background: #eaf2ff !important;
        color: var(--gg-text) !important;
      }}

      div[data-baseweb="tag"] span {{
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
      }}

      div[data-baseweb="select"] input::placeholder {{
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
      }}

      /* -------- DROPDOWN POPUP FIX -------- */
      div[role="listbox"] {{
          background: #ffffff !important;
          border: 1px solid #cbd5e1 !important;
          box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12) !important;
      }}

      div[role="option"] {{
          background: #ffffff !important;
          color: #0b1f3b !important;
          opacity: 1 !important;
      }}

      div[role="option"] *,
      div[role="option"] span,
      div[role="option"] div,
      div[role="option"] p,
      div[role="option"] li {{
          color: #0b1f3b !important;
          -webkit-text-fill-color: #0b1f3b !important;
          fill: #0b1f3b !important;
          opacity: 1 !important;
      }}

      div[role="option"]:hover {{
          background: #eef4fb !important;
      }}

      div[role="option"]:hover *,
      div[role="option"]:hover span,
      div[role="option"]:hover div {{
          color: #0b1f3b !important;
          -webkit-text-fill-color: #0b1f3b !important;
      }}

      div[role="option"][aria-selected="true"] {{
          background: #e8f0fe !important;
      }}

      div[role="option"][aria-selected="true"] *,
      div[role="option"][aria-selected="true"] span,
      div[role="option"][aria-selected="true"] div {{
          color: #0b1f3b !important;
          -webkit-text-fill-color: #0b1f3b !important;
      }}

      div[data-baseweb="menu"] {{
          background: #ffffff !important;
      }}

      div[data-baseweb="menu"] *,
      div[data-baseweb="menu"] span,
      div[data-baseweb="menu"] div,
      div[data-baseweb="menu"] li {{
          color: #0b1f3b !important;
          -webkit-text-fill-color: #0b1f3b !important;
          opacity: 1 !important;
      }}

      ul[role="listbox"] {{
          background: #ffffff !important;
      }}

      ul[role="listbox"] * {{
          color: #0b1f3b !important;
          -webkit-text-fill-color: #0b1f3b !important;
      }}
            /* Extra fallback for portal-rendered dropdowns */
      body div[role="listbox"],
      body ul[role="listbox"] {{
          background: #ffffff !important;
      }}

      body div[role="option"],
      body li[role="option"] {{
          background: #ffffff !important;
          color: #0b1f3b !important;
      }}

      body div[role="option"] *,
      body li[role="option"] *,
      body div[role="option"] span,
      body li[role="option"] span,
      body div[role="option"] div,
      body li[role="option"] div {{
          color: #0b1f3b !important;
          -webkit-text-fill-color: #0b1f3b !important;
          opacity: 1 !important;
      }}
      
      /* -------- DATE INPUT -------- */
      div[data-testid="stDateInput"] > div {{
        background: #ffffff !important;
        border: 1px solid var(--gg-border) !important;
        border-radius: 10px !important;
      }}

      div[data-testid="stDateInput"] input {{
        background: #ffffff !important;
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
        opacity: 1 !important;
      }}

      div[data-testid="stDateInput"] svg {{
        fill: var(--gg-text) !important;
      }}

      /* -------- CALENDAR POPUP -------- */
      [data-baseweb="popover"] {{
        background: #ffffff !important;
        color: var(--gg-text) !important;
      }}

      [data-baseweb="popover"] * {{
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
        opacity: 1 !important;
      }}

      [data-baseweb="calendar"] {{
        background: #ffffff !important;
      }}

      [data-baseweb="calendar"] * {{
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
      }}

      [data-baseweb="calendar"] button {{
        background: #ffffff !important;
        color: var(--gg-text) !important;
      }}

      [data-baseweb="calendar"] button:hover {{
        background: #eef4fb !important;
        color: var(--gg-text) !important;
      }}

      [data-baseweb="calendar"] [aria-selected="true"] {{
        background: #dd5656 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
      }}

      input, textarea {{
        color: var(--gg-text) !important;
        -webkit-text-fill-color: var(--gg-text) !important;
        opacity: 1 !important;
      }}

      .stSlider label, .stSlider span {{
        color: var(--gg-text) !important;
        font-weight: 600 !important;
      }}

      [data-testid="stMetricLabel"] {{
        color: var(--gg-text) !important;
      }}

      [data-testid="stMetricValue"] {{
        color: var(--gg-text) !important;
      }}

      details {{
        border: 1px solid var(--gg-line);
        border-radius: 10px;
        overflow: hidden;
        background: var(--gg-table-2);
      }}

      details summary {{
        background: var(--gg-table-2) !important;
        color: var(--gg-white) !important;
        font-weight: 700 !important;
        padding: 12px 16px !important;
      }}

      .streamlit-expanderHeader {{
        color: var(--gg-white) !important;
        font-weight: 700 !important;
      }}

      .gg-footer {{
        margin-top: 28px;
        padding-top: 18px;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #475569 !important;
        font-size: 14px;
        font-weight: 600;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- DATA --------------------
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)

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

# -------------------- HELPERS --------------------
def fmt_value(v):
    if pd.isna(v):
        return ""
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return str(round(v, 2))
    return str(v).strip()


def fmt_timestamp(v):
    if pd.isna(v) or v == "":
        return ""
    try:
        return pd.to_datetime(v).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(v)


def first_existing(columns_to_check, all_columns):
    for c in columns_to_check:
        if c in all_columns:
            return c
    return None


# -------------------- TITLE --------------------
st.title("Goodgudi CCTV Live Tracking — Dashboard")

# -------------------- FILTERS --------------------

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.0, 1.0])

stores = sorted(df["Select Store"].dropna().astype(str).unique()) if "Select Store" in df.columns else []
users = sorted(df["User"].dropna().astype(str).unique()) if "User" in df.columns else []

with c1:
    store_sel = st.multiselect("Store", stores, default=[])

with c2:
    user_sel = st.multiselect("User", users, default=[])

min_date = df["Timestamp"].min().date() if "Timestamp" in df.columns and df["Timestamp"].notna().any() else None
max_date = df["Timestamp"].max().date() if "Timestamp" in df.columns and df["Timestamp"].notna().any() else None

with c3:
    start_date = st.date_input("Start date", value=min_date if min_date else None)

with c4:
    end_date = st.date_input("End date", value=max_date if max_date else None)
f = df.copy()

if store_sel and "Select Store" in f.columns:
    f = f[f["Select Store"].astype(str).isin(store_sel)]

if user_sel and "User" in f.columns:
    f = f[f["User"].astype(str).isin(user_sel)]

if "Timestamp" in f.columns and f["Timestamp"].notna().any() and start_date and end_date:
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    f = f[(f["Timestamp"] >= start_ts) & (f["Timestamp"] <= end_ts)]

# -------------------- KPIs --------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Checks", int(len(f)))

if "No. of Customer Present" in f.columns:
    k2.metric("Avg Customers", round(f["No. of Customer Present"].mean(), 1) if len(f) else 0)
if "No. of Staff Present" in f.columns:
    k3.metric("Avg Staff", round(f["No. of Staff Present"].mean(), 1) if len(f) else 0)
if "No. of Stock Boxes on Floor" in f.columns:
    k4.metric("Avg Stock Boxes", round(f["No. of Stock Boxes on Floor"].mean(), 1) if len(f) else 0)

st.divider()

# -------------------- LATEST N --------------------
if "Timestamp" in f.columns:
    f = f.sort_values("Timestamp", ascending=False)

top_n = st.slider("Show latest N entries", min_value=5, max_value=100, value=10, step=5)

latest = f.head(top_n).copy()

# dynamic column detection
ratio_col = first_existing(
    ["Staff on Floor Ratio", "% Staff on Floor %", "Staff on Floor %"],
    latest.columns
)
total_logged_col = first_existing(
    ["Total Staff Logged In"],
    latest.columns
)

# order for table
preferred_order = [
    "Timestamp",
    "User",
    "Select Store",
    "No. of Staff Present",
    "No. of Customer Present",
    ratio_col,
    "No. of Stock Boxes on Floor",
    "Staff Doing",
    "Comment",
    "File Photo",
    total_logged_col,
]

show_cols = [c for c in preferred_order if c and c in latest.columns]

# any extra columns not in preferred list can still be included at end if needed
extra_cols = [c for c in latest.columns if c not in show_cols]
# keep extra cols excluded for display to avoid disturbing current table too much

def build_whatsapp_text(row):
    parts = []

    ts_val = fmt_timestamp(row.get("Timestamp", ""))
    store_val = fmt_value(row.get("Select Store", ""))
    staff_val = fmt_value(row.get("No. of Staff Present", ""))
    customer_val = fmt_value(row.get("No. of Customer Present", ""))
    boxes_val = fmt_value(row.get("No. of Stock Boxes on Floor", ""))
    doing_val = fmt_value(row.get("Staff Doing", ""))
    comment_val = fmt_value(row.get("Comment", ""))
    user_val = fmt_value(row.get("User", ""))
    total_logged_val = fmt_value(row.get("Total Staff Logged In", ""))
    ratio_val = fmt_value(row.get(ratio_col, "")) if ratio_col else ""

    # -------------------- BASIC HELPERS --------------------
    def to_number(val):
        try:
            if val == "" or val is None:
                return None
            return float(val)
        except Exception:
            return None

    # -------------------- ACTIVITY EMOJI MAP --------------------
    # Keep only if you want emojis inside activity names later.
    activity_emoji_map = {
        "Attending to Customers": "🛍️",
        "Browsing Mobile": "📱",
        "Doing VM": "🪄",
        "Doing Stock Count": "📦",
        "Near Counter": "🧾",
        "Not In Store": "🚶",
    }

    # -------------------- CUSTOMER EMOJI LOGIC --------------------
    customer_emoji = ""
    customer_num = to_number(customer_val)

    if customer_num == 1:
        customer_emoji = "🧍 "
    elif customer_num == 2:
        customer_emoji = "👥 "
    elif customer_num is not None and customer_num > 2:
        customer_emoji = "🧑‍🤝‍🧑 "

    # -------------------- STAFF NOT ON FLOOR --------------------
    staff_not_on_floor = ""
    try:
        total_logged_num = to_number(total_logged_val)
        staff_num = to_number(staff_val)

        if total_logged_num is not None and staff_num is not None:
            diff = int(total_logged_num - staff_num)
            if diff >= 0:
                staff_not_on_floor = str(diff)
    except Exception:
        staff_not_on_floor = ""

    # -------------------- OUTPUT FORMAT --------------------
    if ts_val:
        parts.append(f"{ts_val}")

    if store_val:
        parts.append(f"{store_val}")

    if staff_val:
        parts.append(f"Staff on Floor: {staff_val}")

    if customer_val != "":
        # emoji only when customers > 0
        parts.append(f"{customer_emoji}Customers: {customer_val}".strip())

    # show box emoji only when boxes > 0
    boxes_num = to_number(boxes_val)
    if boxes_val != "":
        if boxes_num is not None and boxes_num > 0:
            parts.append(f"📦 Boxes: {boxes_val}")
        else:
            parts.append(f"Boxes: {boxes_val}")

    # Activities without emojis
    if doing_val:
        activities = [x.strip() for x in doing_val.split(",") if x.strip()]
        if activities:
            parts.append("Activities: " + ", ".join(activities))

    if comment_val:
        parts.append(f"Comment: {comment_val}")

    if user_val:
        parts.append(f"By: {user_val}")

    if total_logged_val:
        parts.append(f" Logged In: {total_logged_val}")

    if ratio_val:
        parts.append(f"Staff Ratio: {ratio_val}")

    if staff_not_on_floor != "":
        try:
            n = int(staff_not_on_floor)

            if n <= 0:
                icon = "🟢"
            elif n <= 2:
                icon = "🟡"
            else:
                icon = "🔴"

            parts.append(f"{icon} Staff outside the Store: {n}")
        except Exception:
            parts.append(f"🚶 Staff outside the Store: {staff_not_on_floor}")

    return " | ".join(parts)

def render_latest_table_with_copy(df_table, visible_cols):
    if df_table.empty:
        st.info("No entries found for the selected filters.")
        return

    table_headers = visible_cols + ["Copy"]

    html_rows = []
    for i, (_, row) in enumerate(df_table.iterrows()):
        row_cells = []

        for col in visible_cols:
            val = row.get(col, "")
            display_val = fmt_timestamp(val) if col == "Timestamp" else fmt_value(val)
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
                    border:1px solid {TEXT};
                    color:{TEXT};
                    background:white;
                    padding:6px 14px;
                    border-radius:10px;
                    cursor:pointer;
                    font-family:inherit;
                    font-size:13px;
                    font-weight:700;
                "
            >
                Copy
            </button>
            <div id="copied-msg-{i}" style="font-size:11px; color:white; margin-top:4px;"></div>
        </td>
        """
        row_cells.append(copy_btn)
        html_rows.append("<tr>" + "".join(row_cells) + "</tr>")

    header_html = "".join([f"<th>{html.escape(str(h))}</th>" for h in table_headers])

    # sticky header inside scrollable wrapper
    table_html = f"""
    <div style="width:100%; overflow:auto; max-height:520px; border:1px solid {TABLE_LINE}; border-radius:10px;">
      <table style="
          width:max-content;
          min-width:100%;
          border-collapse:collapse;
          font-family:Arial, sans-serif;
          font-size:14px;
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
      thead th {{
        position: sticky;
        top: 0;
        z-index: 10;
        background: {TABLE_BG_2};
        color: {WHITE};
        text-align: left;
        padding: 12px 10px;
        border: 1px solid {TABLE_LINE};
        white-space: nowrap;
        font-weight: 700;
      }}

      tbody td {{
        padding: 10px 10px;
        border: 1px solid {TABLE_LINE};
        background: {TABLE_BG};
        color: {WHITE};
        vertical-align: top;
        white-space: nowrap;
      }}

      tbody tr:hover td {{
        background: #0f172a;
      }}
    </style>
    """

    components.html(table_html, height=560, scrolling=False)


# -------------------- SHOW TABLE VIEW --------------------
with st.expander("Show Table View", expanded=True):
    render_latest_table_with_copy(latest[show_cols], show_cols)

st.divider()

# -------------------- BREAKDOWN BELOW TABLE --------------------
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

# -------------------- STORE SUMMARY BELOW TABLE --------------------
if "Select Store" in f.columns:
    st.subheader("Store-wise Summary (Averages)")
    cols = [c for c in ["No. of Staff Present", "No. of Customer Present", "No. of Stock Boxes on Floor"] if c in f.columns]
    if cols:
        summary = f.groupby("Select Store")[cols].mean().round(2).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)

# -------------------- FOOTER --------------------
st.markdown(
    """
    <div class="gg-footer">
      Dashboard Developed By Rohit Chougule @Goodgudi Retail Pvt. Ltd. Bangalore
    </div>
    """,
    unsafe_allow_html=True,
)
