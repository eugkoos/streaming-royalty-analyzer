import streamlit as st
import pandas as pd
import re

# Unified container 1200px with top padding
st.markdown("""
<style>
.block-container {
  max-width: 1200px;
  margin: auto;
  padding-left: 1rem;
  padding-right: 1rem;
  padding-top: 0.6rem !important;   /* same top spacing as Dashboard */
}
.block-container h1 {
  margin-top: 0rem !important;
  margin-bottom: .35rem !important;
}
</style>
""", unsafe_allow_html=True)

# Primary button styles (also works for form_submit_button)
st.markdown("""
<style>
/* Regular st.button with type="primary" */
div.stButton > button[kind="primary"]{
  background-color:#1f6feb !important;
  border:1px solid #1f6feb !important;
  color:#fff !important;
  font-weight:500;
}
/* Buttons inside forms (form_submit_button) */
form button[data-testid="baseButton-primary"],
form button[kind="primary"]{
  background-color:#1f6feb !important;
  border:1px solid #1f6feb !important;
  color:#fff !important;
  font-weight:500;
}
/* Hover state */
div.stButton > button[kind="primary"]:hover,
form button[data-testid="baseButton-primary"]:hover,
form button[kind="primary"]:hover{
  background-color:#1a5fd0 !important;
  border-color:#1a5fd0 !important;
  color:#fff !important;
}
</style>
""", unsafe_allow_html=True)

# --- Title and intro text ---
st.title("Check your columns")
st.markdown(
    """
Different distributors structure reports in different ways.  
This step makes sure the app understands your data correctly.  

We’ve already guessed most columns (Artist, Track, Platform, Revenue, etc.).  
Please review the matches below and confirm — so your dashboard shows the right insights. 
    """
)

# Take df from session
df = st.session_state.get("df")
if not isinstance(df, pd.DataFrame):
    df = st.session_state.get("df_raw")
if not isinstance(df, pd.DataFrame):
    st.error("No data found. Please upload a file first.")
    st.stop()

# Preview (5 rows)
st.dataframe(df.head(5), use_container_width=True)
# st.divider()  # removed extra line

# Canonical required fields
REQUIRED_FIELDS = {
    # Report info
    "reporting_month": "Month of the statement/report (e.g., 2023-01)",
    "country":         "Country / Territory",
    "platform":        "Streaming/download platform",
    # Content info
    "artist_name":     "Artist name",
    "release_title":   "Release/album title",
    "track_title":     "Track title",
    "isrc":            "ISRC (track id)",
    "upc":             "UPC/EAN (release)",
    # Performance
    "quantity":        "Streams/units/downloads",
    "revenue":         "Revenue/royalty amount",
}

# Aliases for auto-detect (original + correction for country)
EXACT_NAMES = {
    "reporting_month": [
        "reporting_month","transaction month","statement month","report month",
        "sales month","accounted date","month","year_month","yyyymm",
    ],
    "platform": ["platform","store","service","partner","retailer"],
    "country":  [
        "country","territory","region","market",
        "country region","country/region"
    ],
    "artist_name": ["artist_name","artists","artist"],
    "release_title": ["release_title","album/channel","album","release","product","release name"],
    "upc": ["upc","ean","barcode","catalog","catalog number","parent id"],
    "track_title": ["track_title","title","song","track name","track"],
    "isrc": ["isrc","id"],
    "quantity": ["quantity","units","streams","downloads","qty","plays","play count","streams count"],
    "revenue": ["revenue","net_revenue","gross_revenue","net","gross","amount","royalty","earnings","total usd","payout","gross amount","net amount"],
}

def _norm(s: str) -> str:
    """
    Unicode normalization: lowercasing and removing non-alphanumeric,
    including underscores. Ensures 'Net Revenue' and 'net_revenue' match.
    """
    return re.sub(r"[\W_]+", "", str(s).lower(), flags=re.UNICODE)

def auto_map_exact(columns):
    """Auto-mapping based on exact normalized names."""
    cols = list(columns)
    col_norm = {c: _norm(c) for c in cols}
    auto = {}
    for canon, exact_list in EXACT_NAMES.items():
        targets = [_norm(x) for x in exact_list]
        match = next((c for c in cols if col_norm[c] in targets), None)
        if match is not None:
            auto[canon] = match
    return auto

# Russian aliases
# Original headers found in file:
# 'Месяц продаж','Магазин','Лейбл','Cтрана','Исполнитель','UPC','Альбом','ISRC','Трек',
# 'Тип контента','Тип транзакции','Количество',
# 'Доход Лицензиата, ... руб.','Ставка вознаграждения Лицензиара, %','Вознаграждение Лицензиара, руб.'
RUSSIAN_ALIASES = {
    "reporting_month": [
        "Месяц продаж",
    ],
    "platform": [
        "Магазин",
    ],
    "country": [
        "Cтрана",   # Latin 'C'
        "Страна",   # Cyrillic 'С'
    ],
    "artist_name": [
        "Исполнитель",
    ],
    "release_title": [
        "Альбом",
    ],
    "track_title": [
        "Трек",
    ],
    "isrc": [
        "ISRC",
    ],
    "upc": [
        "UPC",
    ],
    "quantity": [
        "Количество",
    ],
    "revenue": [
        "Вознаграждение Лицензиара, руб.",
        # The report also contains «Доход Лицензиата, ... руб.» — not mapped intentionally to avoid confusion.
    ],
}

# Merge: extend EXACT_NAMES with Russian aliases (no duplicates)
for canon, aliases in RUSSIAN_ALIASES.items():
    if canon in EXACT_NAMES:
        merged = list(dict.fromkeys(list(EXACT_NAMES[canon]) + aliases))
        EXACT_NAMES[canon] = merged
    else:
        EXACT_NAMES[canon] = list(dict.fromkeys(aliases))

# Auto-detect + check existing mapping from session
auto_map = auto_map_exact(df.columns)
existing = st.session_state.get("mapped_fields") or st.session_state.get("mapping") or {}
initial = {**auto_map, **existing}

# Form for mapping
with st.form("mapping_form", clear_on_submit=False):
    st.subheader("Confirm your columns")
    st.caption("Most fields are already filled in — just review and adjust if needed")

    order = [
        "reporting_month", "country", "platform",      # row 1 (Report)
        "artist_name", "release_title", "track_title", # row 2 (Content)
        "isrc", "upc", "quantity", "revenue"          # row 3 (Performance)
    ]

    nice_label = {
        "reporting_month": "Reporting Month",
        "country":         "Country",
        "platform":        "Platform",
        "artist_name":     "Artist",
        "release_title":   "Release",
        "track_title":     "Track",
        "isrc":            "ISRC",
        "upc":             "UPC",
        "quantity":        "Quantity (streams/units)",
        "revenue":         "Revenue",
    }

    help_text = {
        "reporting_month": "e.g. Reporting/Transaction Month",
        "country":         "Country / Territory / Region",
        "platform":        "Store / Service / Partner",
        "artist_name":     "Performer / Artist name",
        "release_title":   "Album / Release title",
        "track_title":     "Song / Track title",
        "isrc":            "Track identifier (ISRC)",
        "upc":             "Release identifier (UPC/EAN)",
        "quantity":        "Streams / Units",
        "revenue":         "Net/Gross amount",
    }

    all_cols = list(df.columns)
    base_options = ["-- Select column --"] + all_cols

    selections, chosen, missing, dup = {}, set(), [], False

    # Row 1 — Report
    r1 = st.columns(3)
    for i, key in enumerate(order[:3]):
        default = initial.get(key)
        idx = base_options.index(default) if default in all_cols else 0
        with r1[i]:
            pick = st.selectbox(nice_label[key], base_options, index=idx, help=help_text[key], key=f"sel_{key}")
        if pick == "-- Select column --":
            missing.append(key)
        else:
            if pick in chosen: dup = True
            selections[key] = pick
            chosen.add(pick)

    # Row 2 — Content
    r2 = st.columns(3)
    for i, key in enumerate(order[3:6]):
        default = initial.get(key)
        idx = base_options.index(default) if default in all_cols else 0
        with r2[i]:
            pick = st.selectbox(nice_label[key], base_options, index=idx, help=help_text[key], key=f"sel_{key}")
        if pick == "-- Select column --":
            missing.append(key)
        else:
            if pick in chosen: dup = True
            selections[key] = pick
            chosen.add(pick)

    # Row 3 — Performance
    r3 = st.columns(4)
    for i, key in enumerate(order[6:]):
        default = initial.get(key)
        idx = base_options.index(default) if default in all_cols else 0
        with r3[i]:
            pick = st.selectbox(nice_label[key], base_options, index=idx, help=help_text[key], key=f"sel_{key}")
        if pick == "-- Select column --":
            missing.append(key)
        else:
            if pick in chosen: dup = True
            selections[key] = pick
            chosen.add(pick)

    # Validation messages
    if missing:
        st.warning("Missing fields: " + ", ".join(nice_label[k] for k in missing))
    if dup:
        st.error("Please make sure each field has a unique column. Please fix duplicates.")

    # Navigation
    c1, c2 = st.columns([1, 1])
    back_btn    = c1.form_submit_button("⬅️ Back to Upload File", use_container_width=True)
    confirm_btn = c2.form_submit_button("Go to dashboard", type="primary", use_container_width=True)

# Button handling
if back_btn:
    st.switch_page("app.py")

if confirm_btn:
    missing_now = [k for k in REQUIRED_FIELDS if k not in selections]
    dup_now = len(selections.values()) != len(set(selections.values()))
    if missing_now or dup_now:
        if missing_now:
            st.warning("Missing fields: " + ", ".join(nice_label[k] for k in missing_now))
        if dup_now:
            st.error("Some columns are assigned to multiple fields. Please fix duplicates.")
    else:
        st.session_state["mapped_fields"] = selections
        st.session_state["mapping"] = selections
        st.success("Mapping confirmed!")
        st.switch_page("pages/2_📈_Dashboard.py")

# --- Footer with Privacy & Terms (only on homepage) ---
st.markdown("---")
st.markdown(
    """
    <div style="font-size:0.9rem; color:#6b7280;">
      © 2025 • <a href="https://github.com/eugkoos/streaming-royalty-analyzer/blob/main/PRIVACY.md" target="_blank">Privacy</a> •
      <a href="https://github.com/eugkoos/streaming-royalty-analyzer/blob/main/TERMS.md" target="_blank">Terms</a>
    </div>
    """,
    unsafe_allow_html=True,
)