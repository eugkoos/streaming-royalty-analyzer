import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from typing import List, Tuple
import textwrap as _tw
import streamlit.components.v1 as components  # JS-fallback

# Try Plotly; fallback to Matplotlib if not available
try:
    import plotly.express as px
except Exception:
    px = None

import html  # HTML-escaping to prevent XSS in dynamic HTML
def _safe_str(x) -> str:
    """Convert to string and escape HTML special chars (None -> '')."""
    return html.escape("" if x is None else str(x), quote=True)

# ─────────────────────────────────────────────────────────
# UI flags
SHOW_TOP_HINT = False         # top hint (we hide it)
SHOW_SUBLINE = False          # gray line 'Filtered to …'
DEFAULT_SHOW_PCT = True       # show share of total (no checkbox)
SHOW_CHART_TITLE = False      # chart title hidden

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .block-container {
      max-width: 1200px;
      margin: auto;
      padding-left: 1rem;
      padding-right: 1rem;
      padding-top: 0.6rem !important;   /* unified top spacing */
    }
    .block-container h1 {
      margin-top: 0rem !important;
      margin-bottom: .35rem !important;
    }
    [role="progressbar"], div[data-testid="stProgress"], div[data-testid="stStatusWidget"] { display:none !important; }

    .rp-caption{ color:#6b7280; font-size:.95rem; margin:.2rem 0 .9rem; }

    .kpi-card {
      background:#f5f7fb; border:1px solid #e5e7eb; border-radius:12px;
      padding:.85rem 1rem .75rem; min-height:132px;
      display:flex; flex-direction:column; justify-content:space-between;
      box-sizing:border-box !important; min-width:0 !important;
    }
    .kpi-card .kpi-label { color:#6b7280; font-size:.9rem; font-weight:600; margin-bottom:.12rem; }
    .kpi-hint { color:#94a3b8; font-size:.82rem; line-height:1.2; margin:.02rem 0 .22rem; white-space:normal; }
    .kpi-card .kpi-value { font-size:2.6rem; font-weight:700; line-height:1.08; letter-spacing:.2px; }
    .kpi-item { font-size:1.08rem; font-weight:700; line-height:1.35rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .after-kpi-space { height: 10px !important; }

    :root{ --kpi-col-w:210px; --kpi-gap:28px; }
    .kpi-row{
      display: grid !important;
      grid-template-columns: repeat(5, var(--kpi-col-w)) !important;
      gap: var(--kpi-gap) !important;
      justify-content: center !important;
      align-items: stretch !important;
      margin:.25rem 0 .25rem !important;
    }
    .kpi-row .kpi-card{ min-width: 0 !important; box-sizing: border-box !important; }
    @media (max-width: 1200px){ :root{ --kpi-gap:26px } .kpi-row{ grid-template-columns: repeat(4, var(--kpi-col-w)) !important; } }
    @media (max-width: 1000px){ :root{ --kpi-gap:22px } .kpi-row{ grid-template-columns: repeat(3, var(--kpi-col-w)) !important; } }
    @media (max-width: 780px){  :root{ --kpi-gap:18px } .kpi-row{ grid-template-columns: repeat(2, var(--kpi-col-w)) !important; } }
    @media (max-width: 560px){  :root{ --kpi-gap:16px } .kpi-row{ grid-template-columns: 1fr !important; } }

    /* ── Title closer to toolbar ───────────────────────────────── */
    .flt-guide{
      color:#111827; font-size: clamp(1.10rem, 0.95rem + 0.6vw, 1.45rem);
      font-weight:800; line-height:1.22;
      margin:.28rem 0 .35rem;
      text-align:center;
    }
    .flt-sub{ color:#6b7280; font-size:.93rem; font-weight:500; line-height:1.32; margin:.20rem 0 0; text-align:center; }

    /* ── Compact toolbar ───────────────────────────────────────── */
    .toolbar-wrap{ margin:0 !important; }
    .toolbar-wrap [data-baseweb="select"] > div{ min-height:40px; }
    .toolbar-wrap .stButton > button{ height:40px; padding:.45rem .9rem; }
    .toolbar-wrap [data-testid="stSelectbox"],
    .toolbar-wrap .stButton{ margin-bottom:0 !important; }
    .toolbar-wrap [data-testid="column"] > div{ padding-bottom:0 !important; }

    /* ── Tight gap between toolbar and chart ───────────────────── */
    .gap-tight{ height:0 !important; margin:-18px 0 -22px 0 !important; padding:0 !important; }

    /* Additional compact spacing for chart containers */
    div[data-testid="stPlotlyChart"]{ margin-top:-30px !important; }
    div[data-testid="stPyplotChart"]{ margin-top:-30px !important; }

    .hr-line{ border:0; border-top:1px solid #e5e7eb; height:0; line-height:0; opacity:.9; }
    .hr-after-kpi{ margin: 6px 0 12px !important; }

    /* Large tabs visuals */
    .stTabs [role="tablist"], .stTabs div[data-baseweb="tab-list"] { gap: .8rem !important; }
    .stTabs [role="tab"], .stTabs button[role="tab"], .stTabs div[role="tab"]{
      padding: 1.0rem 1.2rem !important;
      font-weight: 800 !important;
      font-size: 1.18rem !important;
      border-bottom: 2px solid transparent !important;
    }
    .stTabs [role="tab"][aria-selected="true"], .stTabs button[role="tab"][aria-selected="true"]{
      color:#2563eb !important;
      border-bottom: 3px solid #2563eb !important;
    }

    /* (not used, kept for reference) */
    .choose-header{ font-size: clamp(1.10rem, 1.05rem + 0.25vw, 1.35rem) !important; font-weight:700 !important; line-height:1.25 !important; letter-spacing:.1px; text-align:center; }
    .choose-hint{ color:#9CA3AF; font-size:.92rem; font-weight:600; }
    .choose-block{ margin: .25rem 0 .60rem !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Additional CSS overrides for KPI card values and items
st.markdown("""
<style>
.kpi-card .kpi-value{
  font-size: clamp(2.0rem, 1.9rem + 0.6vw, 2.3rem) !important;
  font-weight: 600 !important;
  letter-spacing: .1px !important;
  font-variant-numeric: tabular-nums;
  white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
}
.kpi-card .kpi-item{ font-size: 1.02rem !important; font-weight: 600 !important; line-height: 1.28 !important; }
.after-kpi-space{ height: 10px !important; }
@media (max-width:1100px){ .kpi-card .kpi-value{ font-size: clamp(1.9rem, 1.8rem + 0.5vw, 2.2rem) !important; } }
@media (max-width:960px){  .kpi-card .kpi-value{ font-size: clamp(1.7rem, 1.6rem + 0.5vw, 2.0rem) !important; } }
@media (max-width:840px){  .kpi-card .kpi-value{ font-size: 1.55rem !important; } }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Guard  data & mapping
raw_df = st.session_state.get("df")
mapping = st.session_state.get("mapped_fields")
if raw_df is None or mapping is None:
    st.warning("Please upload and map your report first.")
    st.stop()

df = raw_df.copy()
df.columns = df.columns.map(lambda c: str(c).strip())
rename_map = {orig: canon for canon, orig in mapping.items() if orig in df.columns}
df = df.rename(columns=rename_map)

for col in ("revenue", "quantity"):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

required_for_page = ["platform", "country", "artist_name", "release_title", "track_title", "quantity", "revenue"]
missing_now = [c for c in required_for_page if c not in df.columns]
if missing_now:
    st.error("Some required fields are not mapped yet: " + ", ".join(missing_now))
    if st.button("⬅️ Back to Mapping"):
        st.switch_page("pages/1_📊_Overview.py")
    st.stop()

st.title("📈 Music Streaming Royalty Analyzer")

# ─────────────────────────────────────────────────────────
# Helpers
def period_label_from_reporting_month(frame: pd.DataFrame) -> str:
    if "reporting_month" not in frame.columns:
        return "—"
    ser = pd.to_datetime(frame["reporting_month"], errors="coerce").dropna()
    if ser.empty:
        return "—"
    start, end = ser.min(), ser.max()
    fmt = "%m.%Y"
    return start.strftime(fmt) if start.to_period("M") == end.to_period("M") else f"{start.strftime(fmt)}–{end.strftime(fmt)}"

def fmt_int(x: float) -> str:
    try: return f"{int(round(x)):,}".replace(",", " ")
    except Exception: return "0"

def fmt_amt(x: float) -> str:
    try:
        x = float(x)
        return f"{x:,.2f}" if abs(x) < 10 else f"{x:,.0f}"
    except Exception:
        return "0"

def wrap_label(s: str, width: int = 32) -> str:
    return _tw.fill(str(s), width=width)

PALETTE = {"Earnings":"#2563eb","Streams":"#059669","Value per 1K Streams":"#7c3aed"}


def fmt_pct(p: float) -> str:
    try:
        p = float(p)
        if p <= 0:
            return "0%"
        if p < 0.001:
            return "<0.1%"
        return f"{p:.1%}"
    except Exception:
        return "0%"
USE_GRADIENT = False
FONT = {"base":14,"y_tick":16,"bar_text":14,"title":18}

# ── Code-handling logic (disambiguation, normalization) ─────────────────────────
CODE_KEYS = {"isrc", "upc"}                 # only codes (without *_id)
MISSING_LABEL = "NaN"                       # label for empty code
DISAMBIG_MODE = "full"                      # "full" - show full code; "tail"  only tail
DISAMBIG_TAIL_LEN = 6
RPM_MIN_STREAMS = 1000

def _is_code_key(name: str) -> bool:
    return str(name).lower() in CODE_KEYS

def _normalize_code_series(s: pd.Series) -> pd.Series:
    # keep true missing values, empty strings -> <NA>
    s = pd.Series(s, dtype="string")
    s = s.str.strip().str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    s = s.replace("", pd.NA)
    return s

def aggregate_for_dim(df_src: pd.DataFrame, dim: str) -> pd.DataFrame:
    return df_src.groupby(dim, as_index=False).agg(quantity=('quantity','sum'), revenue=('revenue','sum'))

def resolve_dim_keys(analysis_type: str, frame: pd.DataFrame) -> Tuple[str, str, str]:
    if analysis_type == "Platforms": return "platform", "platform", "Top Platforms"
    if analysis_type == "Countries": return "country", "country", "Top Countries"
    if analysis_type == "Artists":   return "artist_name", "artist_name", "Top Artists"
    if analysis_type == "Releases":
        if "upc" in frame.columns and frame["upc"].notna().any():
            return "upc", "release_title", "Top Releases"
        return "release_title", "release_title", "Top Releases"
    # Tracks
    if "isrc" in frame.columns and frame["isrc"].notna().any():
        return "isrc", "track_title", "Top Tracks"
    return "track_title", "track_title", "Top Tracks"

def aggregate_with_labels(df_src: pd.DataFrame, key_col: str, label_col: str) -> pd.DataFrame:
    if key_col not in df_src.columns: key_col = label_col
    tmp = df_src.copy()
    group_key = key_col

    # code key → normalize and group with dropna=False (to keep NaN group)
    if _is_code_key(key_col):
        tmp["_key_norm"] = _normalize_code_series(tmp[key_col])
        group_key = "_key_norm"

    agg = tmp.groupby(group_key, dropna=False, as_index=False).agg(
        quantity=('quantity','sum'),
        revenue=('revenue','sum')
    )
    if group_key != key_col:
        agg = agg.rename(columns={group_key: key_col})

    # labels
    if key_col == label_col or label_col not in tmp.columns:
        agg["label"] = agg[key_col].astype("string").fillna(MISSING_LABEL)
    else:
        labels = tmp[[group_key, label_col]].copy()
        if group_key != key_col:
            labels = labels.rename(columns={group_key: key_col})
        labels = (
            labels
            .dropna(subset=[key_col, label_col])
            .drop_duplicates(subset=[key_col])
            .rename(columns={label_col: "label"})
        )
        agg = agg.merge(labels, on=key_col, how="left")
        agg["label"] = agg["label"].astype("string")
        agg.loc[agg["label"].isna(), "label"] = agg[key_col].astype("string")
        agg["label"] = agg["label"].fillna(MISSING_LABEL)

    # rpm
    agg["rpm"] = agg.apply(lambda r: (r["revenue"]/r["quantity"]*1000) if r["quantity"] > 0 else 0, axis=1)
    return agg

def top3_labels_by_revenue(frame: pd.DataFrame, key_col: str, label_col: str) -> List[str]:
    if key_col not in frame.columns: key_col = label_col
    tmp = frame.copy()
    group_key = key_col

    if _is_code_key(key_col):
        tmp["_key_norm"] = _normalize_code_series(tmp[key_col])
        group_key = "_key_norm"

    agg = tmp.groupby(group_key, dropna=False, as_index=False).agg(revenue=('revenue','sum'))
    if agg.empty: return []

    total = float(agg["revenue"].sum()) or 1.0

    if key_col == label_col or label_col not in tmp.columns:
        agg["label"] = agg[group_key].astype("string").fillna(MISSING_LABEL)
    else:
        labels = (
            tmp[[group_key, label_col]]
            .dropna(subset=[group_key, label_col])
            .drop_duplicates(subset=[group_key])
            .rename(columns={label_col: "label"})
        )
        agg = agg.merge(labels, on=group_key, how="left")
        agg["label"] = agg["label"].astype("string")
        agg.loc[agg["label"].isna(), "label"] = agg[group_key].astype("string")
        agg["label"] = agg["label"].fillna(MISSING_LABEL)

    agg = agg.sort_values("revenue", ascending=False).head(3)
    return [f'{row["label"]} ({row["revenue"]/total:.0%})' for _, row in agg.iterrows()]

def _disambiguate_labels(frame: pd.DataFrame, key_col: str, label_col: str = "label") -> pd.DataFrame:
    df2 = frame.copy()
    if key_col not in df2.columns or label_col not in df2.columns: return df2
    dup_mask = df2[label_col].astype("string").duplicated(keep=False)
    if dup_mask.any():
        raw = df2[key_col].astype("string")
        clean = raw.fillna("").str.replace(r"[^A-Za-z0-9]", "", regex=True).str.upper()
        if DISAMBIG_MODE == "full":
            code_show = clean
        else:
            code_show = clean.str[-max(1, int(DISAMBIG_TAIL_LEN)):]
        # add tail only where key is not empty
        add_mask = dup_mask & raw.notna() & (clean != "")
        df2.loc[add_mask, label_col] = df2.loc[add_mask, label_col].astype("string") + " • " + code_show[add_mask]
    return df2

# ── Chart renderers ──────────────────────────────────────
FIG_W, FIG_H = 9.0, 4.3

def make_top_barplot_mpl(data: pd.DataFrame, y_col: str, title: str, metric: str, show_pct: bool, total_value: float):
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    sns.barplot(data=data, x="metric_value", y=y_col, hue=y_col, palette="Greens_r", dodge=False, ax=ax)
    leg = ax.get_legend();  leg.remove() if leg else None
    ax.grid(False)
    for s in ["top","right","bottom","left"]: ax.spines[s].set_visible(False)
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.set_xticks([]); ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.tick_params(axis="y", labelsize=FONT["y_tick"])

    def value_fmt(v, r=None, q=None):
        base = f"{fmt_amt(v)}" if metric=="Earnings" else (f"{fmt_int(v)}" if metric=="Streams" else f"{v:,.2f} / 1K")
        return base + (f" ({v/total_value:.0%})" if show_pct and total_value>0 else "")

    for i, row in data.reset_index(drop=True).iterrows():
        mv = row["metric_value"]
        ax.text(mv + (abs(mv)*0.01 if mv else 1), i, value_fmt(mv),
                va="center", ha="left", color="black", fontsize=FONT["bar_text"])

    if SHOW_CHART_TITLE and title:
        ax.set_title(title, pad=8, fontsize=FONT["title"])
    plt.tight_layout()
    fig.subplots_adjust(right=0.92, top=0.94 if SHOW_CHART_TITLE else 0.88)
    st.pyplot(fig, use_container_width=False)

def make_top_barplot(df_src: pd.DataFrame, key_col: str, label_col: str, title: str,
                     top_n: int, metric: str, show_pct: bool, total_value: float):
    data = aggregate_with_labels(df_src, key_col, label_col)
    data = _disambiguate_labels(data, key_col, "label")

    if metric == "Earnings":
        data["metric_value"] = data["revenue"]; xfmt = ":,.0f"
    elif metric == "Streams":
        data["metric_value"] = data["quantity"]; xfmt = ":,.0f"
    else:
        data["metric_value"] = data["rpm"];      xfmt = ":,.2f"

    if metric == "Value per 1K Streams":
        data = data[data["quantity"] >= RPM_MIN_STREAMS]

    data = data.sort_values("metric_value", ascending=False).head(top_n)
    if data.empty:
        st.info(f"No items with ≥{RPM_MIN_STREAMS:,} streams for the selected filters.")
        return

    data = data.assign(
        label_wrapped=data["label"].map(lambda s: wrap_label(s, 32)),
        share=(data["metric_value"] / total_value) if (show_pct and total_value > 0) else 0.0
    )

    if px is None:
        data_for_mpl = data.rename(columns={"label_wrapped": "label"})
        make_top_barplot_mpl(data_for_mpl, "label", title if SHOW_CHART_TITLE else "", metric, DEFAULT_SHOW_PCT, total_value)
        return

    if metric == "Earnings":
        base_txt = data["metric_value"].map(fmt_amt)
    elif metric == "Streams":
        base_txt = data["metric_value"].map(fmt_int)
    else:
        base_txt = data["metric_value"].map(lambda v: f"{v:,.2f}")
    if DEFAULT_SHOW_PCT and total_value > 0:
        base_txt = base_txt + " (" + data["share"].map(fmt_pct) + ")"
    text = base_txt

    # Precompute share text for hover (supports '<0.1%')
    data['share_text'] = data['share'].map(fmt_pct) if (DEFAULT_SHOW_PCT and total_value > 0) else ''
    max_txt_len = int(max((len(str(t)) for t in text), default=10))
    right_margin = max(120, min(220, int(max_txt_len * 6.5)))
    xmax = float(data["metric_value"].max() or 0)

    fig = px.bar(data, x="metric_value", y="label_wrapped", orientation="h", text=text)
    fig.update_layout(
        title=dict(text=(title if SHOW_CHART_TITLE else ""), x=0.5, xanchor="center",
                   font=dict(size=FONT["title"], color="#111827")),
        font=dict(size=FONT["base"]),
        hoverlabel=dict(font_size=FONT["base"]),
        showlegend=False,
        margin=dict(l=8, r=right_margin, t=(4 if SHOW_CHART_TITLE else 4), b=6),
        height=max(300, 60 + 34 * len(data)),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    if xmax > 0:
        fig.update_xaxes(range=[0, xmax * 1.10])

    fig.update_layout(dragmode=False)

    custom = data[["revenue", "quantity", "label", "share", "rpm", "share_text"]].values
    if metric == "Earnings":
        hover_tmpl = ("<b>%{customdata[2]}</b><br>"
                      "Earnings: %{x" + xfmt + "}<br>"
                      "Streams: %{customdata[1]:,.0f}<br>"
                      "Value per 1K Streams: %{customdata[4]:,.2f}"
                      + ("<br>Share: %{customdata[5]}" if (DEFAULT_SHOW_PCT and total_value > 0) else "")
                      + "<extra></extra>")
    elif metric == "Streams":
        hover_tmpl = ("<b>%{customdata[2]}</b><br>"
                      "Streams: %{x" + xfmt + "}<br>"
                      "Earnings: %{customdata[0]:,.0f}<br>"
                      "Value per 1K Streams: %{customdata[4]:,.2f}"
                      + ("<br>Share: %{customdata[5]}" if (DEFAULT_SHOW_PCT and total_value > 0) else "")
                      + "<extra></extra>")
    else:
        hover_tmpl = ("<b>%{customdata[2]}</b><br>"
                      "Value per 1K Streams: %{x" + xfmt + "}<br>"
                      "Earnings: %{customdata[0]:,.0f}<br>"
                      "Streams: %{customdata[1]:,.0f}"
                      + ("<br>Share: %{customdata[5]}" if (DEFAULT_SHOW_PCT and total_value > 0) else "")
                      + "<extra></extra>")

    fig.update_traces(
        marker_color=None if USE_GRADIENT else PALETTE.get(metric, "#1f77b4"),
        marker_line_width=0,
        cliponaxis=False,
        textposition="outside",
        textfont=dict(size=FONT["bar_text"]),
        hovertemplate=hover_tmpl,
        customdata=custom
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(title=None, categoryorder="total ascending",
                     automargin=True, tickfont=dict(size=FONT["y_tick"]))

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False},
    )

def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")

def detect_currency_hint(frame: pd.DataFrame) -> str:
    if "currency" in frame.columns:
        vals = [str(x).upper() for x in frame["currency"].dropna().unique().tolist()]
        if len(vals) == 1: return f"currency: {vals[0]}"
        elif len(vals) > 1:
            preview = ", ".join(sorted(vals[:3])); suffix = "…" if len(vals) > 3 else ""
            return f"mixed currencies ({preview}{suffix})"
    return "in report currency (e.g., $ € £)"

def render_value_card(label: str, value: str, hint: str | None = None) -> str:
    # SAFE: escape user-provided text before inserting into HTML
    label_safe = _safe_str(label)
    value_safe = _safe_str(value)
    hint_safe  = _safe_str(hint) if hint else ""
    hint_html = f'<div class="kpi-hint">{hint_safe}</div>' if hint else ""
    return (
        '<div class="kpi-card">'
        f'  <div class="kpi-label">{label_safe}</div>'
        f'  {hint_html}'
        f'  <div class="kpi-value">{value_safe}</div>'
        '</div>'
    )

def render_list_card(title: str, lines: List[str]) -> str:
    # SAFE: escape every line to avoid XSS via labels
    title_safe = _safe_str(title)
    items = lines if lines else ["—"]
    items_html = "".join([f'<div class="kpi-item" title="{_safe_str(line)}">{_safe_str(line)}</div>' for line in items])
    return (
        '<div class="kpi-card">'
        f'  <div class="kpi-label">{title_safe}</div>'
        f'  {items_html}'
        '</div>'
    )

# ─────────────────────────────────────────────────────────
# SUMMARY (KPI)
period_global = period_label_from_reporting_month(df)
total_streams_global = float(df["quantity"].sum()) if not df.empty else 0.0
total_revenue_global = float(df["revenue"].sum()) if not df.empty else 0.0
_currency_hint = detect_currency_hint(df)

st.markdown(f'<div class="rp-caption">Report period: {_safe_str(period_global)}</div>', unsafe_allow_html=True)

# KPI by tracks: key only isrc or title (without track_id)
_track_key_for_kpi = "isrc" if "isrc" in df.columns and df["isrc"].notna().any() else "track_title"

top_platform_lines = top3_labels_by_revenue(df, "platform", "platform")
top_country_lines  = top3_labels_by_revenue(df, "country", "country")
top_track_lines    = top3_labels_by_revenue(df, _track_key_for_kpi, "track_title")

kpi_html = (
    '<div class="kpi-row">'
    + render_value_card("Total Earnings", fmt_amt(total_revenue_global), hint=f"Sum over the selected period — {_safe_str(_currency_hint)}")
    + render_value_card("Total Streams",  fmt_int(total_streams_global),  hint="Total number of streams (all platforms, Spotify, Apple, etc.)")
    + render_list_card("Top Platforms by Earnings", top_platform_lines)
    + render_list_card("Top Countries by Earnings", top_country_lines)
    + render_list_card("Top Tracks by Earnings",    top_track_lines)
    + '</div>'
)
st.markdown(kpi_html, unsafe_allow_html=True)
st.markdown('<div class="after-kpi-space"></div>', unsafe_allow_html=True)
st.markdown('<hr class="hr-line hr-after-kpi">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
FILTERS = {
    "platform": ("Platform", "platform", "All platforms"),
    "country":  ("Country", "country", "All countries"),
    "artist":   ("Artist", "artist_name", "All artists"),
    "release":  ("Release", "release_title", "All releases"),
    "track":    ("Track", "track_title", "All tracks"),
}
FILTER_SET = {
    "Platforms": ["artist", "country"],
    "Countries": ["platform", "artist"],
    "Artists":   ["platform", "country"],
    "Releases":  ["platform", "country"],
    "Tracks":    ["platform", "country"],
}

HELP = {
    "metric":  "Choose the metric used for ranking.",
    "topn":    "How many positions to display.",
    "platform":"Filter by platform (Spotify, Apple, etc.).",
    "country": "Listener / consumer country.",
    "artist":  "Filter by artist/performer.",
    "release": "Filter by release (album/EP/single).",
    "track":   "Filter by track/song.",
    "reset":   "Clear all filters on this tab."
}

def _k(tab: str, base: str) -> str:  # namespaced keys
    return f"{tab}__{base}"

# ─────────────────────────────────────────────────────────
def render_tab(tab_name: str):
    desired = FILTER_SET.get(tab_name, [])
    plural  = {"Platforms":"Platforms","Countries":"Countries","Artists":"Artists","Releases":"Releases","Tracks":"Tracks"}.get(tab_name,"Items")

    # defaults only for filters (NOT for metric/topn!)
    for fkey in ["platform","country","artist","release","track"]:
        st.session_state.setdefault(_k(tab_name, f"flt_{fkey}"), FILTERS[fkey][2])

    # values for header before rendering widgets
    metric_now = st.session_state.get(_k(tab_name, "metric"), "Earnings")
    topn_now   = st.session_state.get(_k(tab_name, "topn"),   "Top 10")

    def _ctx_list():
        seq = ["artist","country","platform","release","track"]
        out = []
        for fkey in seq:
            val = st.session_state.get(_k(tab_name, f"flt_{fkey}"), FILTERS[fkey][2])
            if val != FILTERS[fkey][2]:
                out.append(f'"{val}"' if fkey=="track" else val)
        return out

    ctx_vals = _ctx_list()
    ctx_suffix = (" — " + ", ".join(ctx_vals)) if ctx_vals else ""
    title_map  = f"{topn_now} {plural} by {metric_now}{ctx_suffix}"

    # SAFE: escape title before HTML injection
    title_map_safe = html.escape(title_map, quote=True)
    if SHOW_SUBLINE:
        st.markdown(f'<div class="flt-guide">{title_map_safe}</div><div class="flt-sub"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="flt-guide">{title_map_safe}</div>', unsafe_allow_html=True)

    # ── FILTERS PANEL (toolbar) ─────────────────────────
    st.markdown('<div class="toolbar-wrap">', unsafe_allow_html=True)
    c_metric, c_topn, c_f1, c_f2, c_reset = st.columns([1, 1, 1, 1, .8], gap="small")

    with c_metric:
        metric_labels = ["Earnings", "Streams", "Value per 1K Streams"]
        default_idx = metric_labels.index(metric_now) if metric_now in metric_labels else 0
        metric = st.selectbox(
            "", metric_labels,
            index=default_idx,
            key=_k(tab_name, "metric"),
            label_visibility="collapsed",
            help=HELP["metric"]
        )

    with c_topn:
        top_opts = ["Top 5", "Top 10", "Top 15", "Top 20", "Top 25"]
        default_idx = top_opts.index(topn_now) if topn_now in top_opts else 1
        top_n_option = st.selectbox(
            "", top_opts,
            index=default_idx,
            key=_k(tab_name, "topn"),
            label_visibility="collapsed",
            help=HELP["topn"]
        )
        top_n = int(top_n_option.split()[1])

    # active filters (first 2 for tab)
    active_filters = (desired + [None, None])[:2]
    df_filt_stage = df.copy()

    if active_filters[0] is not None:
        f1 = active_filters[0]
        label1, col1, def1 = FILTERS[f1]
        opts1 = [def1] + (sorted(df_filt_stage[col1].dropna().unique().tolist()) if col1 in df_filt_stage.columns else [])
        cur1_key = _k(tab_name, f"flt_{f1}")
        if st.session_state.get(cur1_key) not in opts1:
            st.session_state[cur1_key] = def1
        with c_f1:
            sel1 = st.selectbox(label1, opts1, key=cur1_key, label_visibility="collapsed", help=HELP.get(f1))
        if sel1 != def1 and col1 in df_filt_stage.columns:
            df_filt_stage = df_filt_stage[df_filt_stage[col1] == sel1]

    if active_filters[1] is not None:
        f2 = active_filters[1]
        label2, col2, def2 = FILTERS[f2]
        opts2 = [def2] + (sorted(df_filt_stage[col2].dropna().unique().tolist()) if col2 in df_filt_stage.columns else [])
        cur2_key = _k(tab_name, f"flt_{f2}")
        if st.session_state.get(cur2_key) not in opts2:
            st.session_state[cur2_key] = def2
        with c_f2:
            sel2 = st.selectbox(label2, opts2, key=cur2_key, label_visibility="collapsed", help=HELP.get(f2))
        if sel2 != def2 and col2 in df_filt_stage.columns:
            df_filt_stage = df_filt_stage[df_filt_stage[col2] == sel2]

    def _reset_current_tab():
        for fkey in ["platform","country","artist","release","track"]:
            st.session_state[_k(tab_name, f"flt_{fkey}")] = FILTERS[fkey][2]
    with c_reset:
        st.button("Reset", use_container_width=True, on_click=_reset_current_tab, key=_k(tab_name, "reset"), help=HELP["reset"])
    st.markdown('</div>', unsafe_allow_html=True)  # /toolbar-wrap

    # GAP  reduce distance to chart
    st.markdown('<div class="gap-tight"></div>', unsafe_allow_html=True)

    # ── CHART ──────────────────────────────────────────────
    df_filt = df_filt_stage
    if df_filt.empty:
        st.warning("No data to display. Try adjusting the filters.")
        return

    key_col, label_col, default_title = resolve_dim_keys(tab_name, df_filt)
    ctx_for_title = ", ".join(ctx_vals)
    chart_title = f"{default_title} by {metric}" + (f" — {ctx_for_title}" if ctx_for_title else "")

    total_streams = float(df_filt["quantity"].sum())
    total_revenue = float(df_filt["revenue"].sum())
    total_for_pct = total_revenue if metric == "Earnings" else (total_streams if metric == "Streams" else 0)

    make_top_barplot(
        df_src=df_filt, key_col=key_col, label_col=label_col, title=chart_title,
        top_n=int(top_n), metric=metric, show_pct=DEFAULT_SHOW_PCT, total_value=total_for_pct
    )

    # ── EXPORT ───────────────────────────────────────────
    agg = aggregate_with_labels(df_filt, key_col, label_col).copy()
    agg = _disambiguate_labels(agg, key_col, "label")
    agg["Value per 1K Streams"] = agg["rpm"]
    if metric == "Value per 1K Streams":
        agg = agg[agg["quantity"] >= RPM_MIN_STREAMS]
    dim_col_name = {
        "platform":"Platform",
        "country":"Country",
        "artist_name":"Artist",
        "release_title":"Release",
        "track_title":"Track",
        "isrc":"Track",         # in case label_col is isrc
        "upc":"Release"         # and for upc
    }.get(label_col, label_col.title())
    export_df = agg[["label","quantity","revenue","Value per 1K Streams"]].rename(
        columns={"label": dim_col_name, "quantity":"Streams", "revenue":"Earnings"}
    ).sort_values("Earnings" if metric=="Earnings" else ("Streams" if metric=="Streams" else "Value per 1K Streams"),
                  ascending=False)

    # SAFE: neutralize dangerous prefixes in dimension text to prevent CSV-formula execution in Excel
    export_df[dim_col_name] = export_df[dim_col_name].map(lambda s: ("'" + s) if str(s).startswith(("+","-","=","@")) else s)

    st.download_button(
        label="⬇️ Download table (CSV contains what you see in the chart)",
        data=export_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{_slug(label_col)}_summary.csv",
        mime="text/csv",
        use_container_width=True,
        key=_k(tab_name, "download"),
    )

# ─────────────────────────────────────────────────────────
tabs = st.tabs(["Platforms", "Countries", "Artists", "Releases", "Tracks"])
for name, pane in zip(["Platforms","Countries","Artists","Releases","Tracks"], tabs):
    with pane:
        render_tab(name)

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