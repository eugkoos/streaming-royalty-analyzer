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

# ─────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* Keep a narrow page container (do not stretch the whole dashboard) */
    .block-container { max-width: 1200px; margin: auto; padding-left: 1rem; padding-right: 1rem; }

    /* Hide service elements under the title */
    h1 + div, section.main h1 + div, .block-container h1 + div, h1 + div:empty {
      display:none !important; height:0 !important; margin:0 !important; padding:0 !important; border:0 !important; background:transparent !important;
    }
    .block-container h1 { margin-bottom: .35rem !important; }
    [role="progressbar"], div[data-testid="stProgress"], div[data-testid="stStatusWidget"] { display:none !important; }

    /* Period caption */
    .rp-caption{ color:#6b7280; font-size:.95rem; margin:.2rem 0 .9rem; }

    /* KPI cards */
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
    .after-kpi-space { height: 10px !important; }  /* меньше промежуток над линией */

    /* KPI layout (5 per row) + breakpoints */
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

    /* Guide above filters: bold line + compact grey subline (no tooltip) */
    .flt-guide{
      color:#111827; font-size:1.02rem; font-weight:700;
      line-height:1.25; margin:.26rem 0 .06rem;
    }
    .flt-sub{
      color:#6b7280; font-size:.93rem; font-weight:500;
      line-height:1.32; margin:.02rem 0 0;
    }

    /* Pull the filters row closer to the guide */
    .filters-wrap{ margin-top:-14px !important; }

    /* Slightly tighter selectboxes */
    .filters-wrap [data-baseweb="select"] > div{ min-height:44px; }
    .filters-wrap [data-testid="stSelectbox"]{ margin-bottom:.10rem !important; }
    .filters-wrap .stButton > button{ margin-top:.05rem; }

    /* Divider styles */
    .hr-line{ border:0; border-top:1px solid #e5e7eb; height:0; line-height:0; opacity:.9; }
    .hr-after-kpi{ margin: 6px 0 12px !important; } /* меньше сверху, немного снизу */
    </style>
    """,
    unsafe_allow_html=True
)

# KPI typography tweaks
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
.after-kpi-space{ height: 10px !important; }  /* синхронизировано */
@media (max-width:1100px){ .kpi-card .kpi-value{ font-size: clamp(1.9rem, 1.8rem + 0.5vw, 2.2rem) !important; } }
@media (max-width:960px){  .kpi-card .kpi-value{ font-size: clamp(1.7rem, 1.6rem + 0.5vw, 2.0rem) !important; } }
@media (max-width:840px){  .kpi-card .kpi-value{ font-size: 1.55rem !important; } }
</style>
""", unsafe_allow_html=True)

# JS-fallback: hide block under H1
components.html("""
<script>
  try {
    const h1 = window.parent.document.querySelector('h1');
    if (h1 && h1.nextElementSibling) {
      const el = h1.nextElementSibling;
      el.style.display = 'none'; el.style.height = '0'; el.style.margin = '0';
      el.style.padding = '0'; el.style.border = '0'; el.style.background = 'transparent';
    }
  } catch(e) {}
</script>
""", height=0, width=0)

# CTA styles
st.markdown("""
<style>
.choose-header{ font-size: clamp(1.10rem, 1.05rem + 0.25vw, 1.35rem) !important; font-weight:700 !important; line-height:1.25 !important; letter-spacing:.1px; }
.choose-block{ margin: .25rem 0 .60rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Guard — data & mapping
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

st.title("📈 Streaming Royalty Analyzer")

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
    return f"{int(round(x)):,}".replace(",", " ")

def fmt_amt(x: float) -> str:
    return f"{x:,.0f}" if abs(x) >= 1000 else f"{x:,.2f}"

def fmt_short(v: float) -> str:
    a = abs(float(v))
    if a >= 1_000_000_000: return f"{v/1_000_000_000:.1f}B"
    if a >= 1_000_000:     return f"{v/1_000_000:.1f}M"
    if a >= 1_000:         return f"{v/1_000:.1f}K"
    return f"{v:.0f}"

def wrap_label(s: str, width: int = 32) -> str:
    return _tw.fill(str(s), width=width)

PALETTE = {"Earnings":"#2563eb","Streams":"#059669","Value per 1K Streams":"#7c3aed"}
USE_GRADIENT = False
FONT = {"base":14,"y_tick":16,"bar_text":14,"title":18}

# >>> NEW: порог для RPM (минимум стримов, чтобы показать пункт)
RPM_MIN_STREAMS = 1000

def aggregate_for_dim(df_src: pd.DataFrame, dim: str) -> pd.DataFrame:
    return df_src.groupby(dim, as_index=False).agg(quantity=('quantity','sum'), revenue=('revenue','sum'))

# >>> агрегируем по UPC/ISRC (лейблы — названия)
def resolve_dim_keys(analysis_type: str, frame: pd.DataFrame) -> Tuple[str, str, str]:
    if analysis_type == "Platforms": return "platform", "platform", "Top Platforms"
    if analysis_type == "Countries": return "country", "country", "Top Countries"
    if analysis_type == "Artists":
        key = "artist_id" if "artist_id" in frame.columns else "artist_name"
        return key, "artist_name", "Top Artists"
    if analysis_type == "Releases":
        if "upc" in frame.columns and frame["upc"].notna().any():
            return "upc", "release_title", "Top Releases"
        key = "release_id" if "release_id" in frame.columns else "release_title"
        return key, "release_title", "Top Releases"
    # Tracks
    if "isrc" in frame.columns and frame["isrc"].notna().any():
        return "isrc", "track_title", "Top Tracks"
    key = "track_id" if "track_id" in frame.columns else "track_title"
    return key, "track_title", "Top Tracks"

def aggregate_with_labels(df_src: pd.DataFrame, key_col: str, label_col: str) -> pd.DataFrame:
    if key_col not in df_src.columns: key_col = label_col
    agg = df_src.groupby(key_col, as_index=False).agg(quantity=('quantity','sum'), revenue=('revenue','sum'))
    if key_col == label_col or label_col not in df_src.columns:
        agg["label"] = agg[key_col].astype(str)
    else:
        labels = (df_src[[key_col, label_col]].dropna().drop_duplicates(subset=[key_col]).rename(columns={label_col:"label"}))
        agg = agg.merge(labels, on=key_col, how="left")
    agg["rpm"] = agg.apply(lambda r: (r["revenue"]/r["quantity"]*1000) if r["quantity"] > 0 else 0, axis=1)
    return agg

def top3_labels_by_revenue(frame: pd.DataFrame, key_col: str, label_col: str) -> List[str]:
    if key_col not in frame.columns: key_col = label_col
    agg = frame.groupby(key_col, as_index=False).agg(revenue=('revenue','sum'))
    if agg.empty: return []
    total = float(agg["revenue"].sum()) or 1.0
    if key_col == label_col or label_col not in frame.columns:
        agg["label"] = agg[key_col].astype(str)
    else:
        labels = (frame[[key_col, label_col]].dropna().drop_duplicates(subset=[key_col]).rename(columns={label_col:"label"}))
        agg = agg.merge(labels, on=key_col, how="left")
    agg = agg.sort_values("revenue", ascending=False).head(3)
    return [f'{row["label"]} ({row["revenue"]/total:.0%})' for _, row in agg.iterrows()]

# ── Chart renderers ──────────────────────────────────────
FIG_W, FIG_H = 9.0, 4.3  # for Matplotlib fallback

def make_top_barplot_mpl(data: pd.DataFrame, y_col: str, title: str, metric: str, show_pct: bool, total_value: float):
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    sns.barplot(data=data, x="metric_value", y=y_col, hue=y_col, palette="Greens_r", dodge=False, ax=ax)
    leg = ax.get_legend();  leg.remove() if leg else None
    ax.grid(False)
    for s in ["top","right","bottom","left"]: ax.spines[s].set_visible(False)
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.set_xticks([]); ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.tick_params(axis="y", labelsize=FONT["y_tick"])

    def value_fmt(v, r, q):
        base = f"{fmt_amt(v)}" if metric=="Earnings" else (f"{fmt_int(v)} streams" if metric=="Streams" else f"{fmt_amt(v)} / 1K")
        return base + (f" ({v/total_value:.0%})" if show_pct and total_value>0 else "")

    for i, row in data.reset_index(drop=True).iterrows():
        mv = row["metric_value"]
        ax.text(mv + (abs(mv)*0.01 if mv else 1), i, value_fmt(mv, row["revenue"], row["quantity"]),
                va="center", ha="left", color="black", fontsize=FONT["bar_text"])

    ax.set_title(title, pad=10, fontsize=FONT["title"])
    plt.tight_layout()
    fig.subplots_adjust(right=0.92)
    st.pyplot(fig, use_container_width=False)

def make_top_barplot(df_src: pd.DataFrame, key_col: str, label_col: str, title: str,
                     top_n: int, metric: str, show_pct: bool, total_value: float):
    """Primary renderer: Plotly if available, otherwise MPL."""
    data = aggregate_with_labels(df_src, key_col, label_col)

    if metric == "Earnings":
        data["metric_value"] = data["revenue"]; xfmt = ":,.0f"
    elif metric == "Streams":
        data["metric_value"] = data["quantity"]; xfmt = ":,.0f"
    else:
        data["metric_value"] = data["rpm"];      xfmt = ":,.2f"

    # >>> NEW: скрываем low-volume пункты только для RPM
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
        make_top_barplot_mpl(data_for_mpl, "label", title, metric, show_pct, total_value)
        return

    if metric == "Earnings":
        base_txt = data["metric_value"].map(fmt_amt)
    elif metric == "Streams":
        base_txt = data["metric_value"].map(fmt_int)
    else:
        base_txt = data["metric_value"].map(lambda v: f"{v:,.2f}")
    if show_pct and total_value > 0:
        base_txt = base_txt + " (" + data["share"].map(lambda p: f"{p:.0%}") + ")"
    text = base_txt

    max_txt_len = int(max((len(str(t)) for t in text), default=10))
    right_margin = max(120, min(220, int(max_txt_len * 6.5)))
    xmax = float(data["metric_value"].max() or 0)

    fig = px.bar(data, x="metric_value", y="label_wrapped", orientation="h", text=text)
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=FONT["title"], color="#111827")),
        font=dict(size=FONT["base"]),
        hoverlabel=dict(font_size=FONT["base"]),
        showlegend=False,
        margin=dict(l=8, r=right_margin, t=44, b=10),
        height=max(300, 64 + 36 * len(data)),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    if xmax > 0:
        fig.update_xaxes(range=[0, xmax * 1.10])

    fig.update_layout(dragmode=False)

    custom = data[["revenue", "quantity", "label", "share", "rpm"]].values
    if metric == "Earnings":
        hover_tmpl = ("<b>%{customdata[2]}</b><br>"
                      "Earnings: %{x" + xfmt + "}<br>"
                      "Streams: %{customdata[1]:,.0f}<br>"
                      "Value per 1K Streams: %{customdata[4]:,.2f}"
                      + ("<br>Share: %{customdata[3]:.0%}" if (show_pct and total_value > 0) else "")
                      + "<extra></extra>")
    elif metric == "Streams":
        hover_tmpl = ("<b>%{customdata[2]}</b><br>"
                      "Streams: %{x" + xfmt + "}<br>"
                      "Earnings: %{customdata[0]:,.0f}<br>"
                      "Value per 1K Streams: %{customdata[4]:,.2f}"
                      + ("<br>Share: %{customdata[3]:.0%}" if (show_pct and total_value > 0) else "")
                      + "<extra></extra>")
    else:
        hover_tmpl = ("<b>%{customdata[2]}</b><br>"
                      "Value per 1K Streams: %{x" + xfmt + "}<br>"
                      "Earnings: %{customdata[0]:,.0f}<br>"
                      "Streams: %{customdata[1]:,.0f}"
                      + ("<br>Share: %{customdata[3]:.0%}" if (show_pct and total_value > 0) else "")
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
    hint_html = f'<div class="kpi-hint">{hint}</div>' if hint else ""
    return (
        '<div class="kpi-card">'
        f'  <div class="kpi-label">{label}</div>'
        f'  {hint_html}'
        f'  <div class="kpi-value">{value}</div>'
        '</div>'
    )

def render_list_card(title: str, lines: List[str]) -> str:
    items = lines if lines else ["—"]
    items_html = "".join([f'<div class="kpi-item" title="{line}">{line}</div>' for line in items])
    return (
        '<div class="kpi-card">'
        f'  <div class="kpi-label">{title}</div>'
        f'  {items_html}'
        '</div>'
    )

# ─────────────────────────────────────────────────────────
# SUMMARY (KPI)
period_global = period_label_from_reporting_month(df)
total_streams_global = float(df["quantity"].sum()) if not df.empty else 0.0
total_revenue_global = float(df["revenue"].sum()) if not df.empty else 0.0
_currency_hint = detect_currency_hint(df)

st.markdown(f'<div class="rp-caption">Report period: {period_global}</div>', unsafe_allow_html=True)

# prefer ISRC internally for tracks in KPI
_track_key_for_kpi = "isrc" if "isrc" in df.columns and df["isrc"].notna().any() else ("track_id" if "track_id" in df.columns else "track_title")

top_platform_lines = top3_labels_by_revenue(df, "platform", "platform")
top_country_lines  = top3_labels_by_revenue(df, "country", "country")
top_track_lines    = top3_labels_by_revenue(df, _track_key_for_kpi, "track_title")

kpi_html = (
    '<div class="kpi-row">'
    + render_value_card("Total Earnings", fmt_amt(total_revenue_global), hint=f"Sum over the selected period — {_currency_hint}")
    + render_value_card("Total Streams",  fmt_int(total_streams_global),  hint="Total number of streams (all platforms, Spotify, Apple, etc.)")
    + render_list_card("Top Platforms by Earnings", top_platform_lines)
    + render_list_card("Top Countries by Earnings", top_country_lines)
    + render_list_card("Top Tracks by Earnings",    top_track_lines)
    + '</div>'
)
st.markdown(kpi_html, unsafe_allow_html=True)
st.markdown('<div class="after-kpi-space"></div>', unsafe_allow_html=True)
st.markdown('<hr class="hr-line hr-after-kpi">', unsafe_allow_html=True)  # компактная линия

# ─────────────────────────────────────────────────────────
# ANALYSIS — dimension & metric selectors (top)
st.markdown(
    '<div class="choose-block"><span class="choose-header"><b>Explore your catalog by platform, artist, release, track, or country — then pick a metric to see the story.</b></span></div>',
    unsafe_allow_html=True
)
col_dim, col_metric, col_topn, col_pct = st.columns([2, 2, 1.5, 1], gap="small")
with col_dim:
    analysis_type = st.selectbox("", ["Platforms", "Countries", "Artists", "Releases", "Tracks"], index=0, label_visibility="collapsed")
with col_metric:
    metric_labels = ["Earnings", "Streams", "Value per 1K Streams"]
    metric = st.selectbox("", metric_labels, index=0, label_visibility="collapsed")
with col_topn:
    top_n_option = st.selectbox("", ["Top 5", "Top 10", "Top 15", "Top 20", "Top 25"], index=1, label_visibility="collapsed")
    top_n = int(top_n_option.split()[1])
with col_pct:
    show_pct = st.checkbox("% of total", value=True, key="chk_pct", disabled=(metric == "Value per 1K Streams"))

# ─────────────────────────────────────────────────────────
# Dynamic guide (friendly): always after selectors
# >>> Spacing tuning for "You're viewing…" line and filters
st.markdown("""
<style>
  /* Отступы у строки “You're viewing …” */
  .flt-guide{ margin: .70rem 0 .25rem !important; }  /* top | sides | bottom */

  /* Чуть больше воздуха под серой подстрокой */
  .flt-sub{ margin-top: .25rem !important; }

  /* Фильтры не так сильно “подтягиваем” вверх (было -14px) */
  .filters-wrap{ margin-top: -6px !important; }
</style>
""", unsafe_allow_html=True)
# <<< End spacing tweak

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

human = {"platform":"platform", "country":"country", "artist":"artist", "release":"release", "track":"track"}
def join_human(keys):
    keys = [human[k] for k in keys if k in human]
    if not keys: return ""
    return keys[0] if len(keys) == 1 else (", ".join(keys[:-1]) + " and " + keys[-1])

desired = FILTER_SET.get(analysis_type, [])
plural = {"Platforms":"Platforms","Countries":"Countries","Artists":"Artists","Releases":"Releases","Tracks":"Tracks"}.get(analysis_type,"Items")

# Title: always "Top N … by …"
title_map = f"You're viewing {top_n_option} {plural} by {metric}"

# Subline: friendly guidance or applied summary
platform_sel = st.session_state.get("flt_platform", "All platforms")
country_sel  = st.session_state.get("flt_country", "All countries")
applied_bits = []
if platform_sel != "All platforms": applied_bits.append(f"Platform: {platform_sel}")
if country_sel  != "All countries": applied_bits.append(f"Country: {country_sel}")

if applied_bits:
    sub_map = "Filtered to " + " • ".join(applied_bits) + " — adjust filters below to compare markets or artists."
else:
    sub_map = f"Filter below by {join_human(desired)} to see how performance changes in different markets and discover new growth opportunities."

st.markdown(
    f'<div class="flt-guide">{title_map}.</div><div class="flt-sub">{sub_map}</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────
# Defaults for filters
defaults = {"flt_platform":"All platforms","flt_country":"All countries","flt_artist":"All artists","flt_release":"All releases","flt_track":"All tracks"}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

def _reset_filters():
    for k, v in defaults.items():
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────
# Filters: always show two slots from FILTER_SET (even if single unique)
active_filters = (desired + [None, None])[:2]

st.markdown('<div class="filters-wrap">', unsafe_allow_html=True)
cols = st.columns([2, 2, 1], gap="small")

df_filt_stage = df.copy()

for i, fkey in enumerate(active_filters):
    with cols[i]:
        if fkey is None:
            st.write("")
        else:
            label, col_name, default = FILTERS[fkey]
            opts = [default] + (sorted(df_filt_stage[col_name].dropna().unique().tolist()) if col_name in df_filt_stage.columns else [])
            current_val = st.session_state.get(f"flt_{fkey}", default)
            if current_val not in opts:
                current_val = default
            sel = st.selectbox(label, opts, key=f"flt_{fkey}", label_visibility="collapsed")
            if sel != default and col_name in df_filt_stage.columns:
                df_filt_stage = df_filt_stage[df_filt_stage[col_name] == sel]

with cols[2]:
    st.button("Reset", use_container_width=True, on_click=_reset_filters)

st.markdown('</div>', unsafe_allow_html=True)

# Filters summary (optional)
def filters_summary(ss) -> str:
    parts = []
    if ss["flt_platform"] != "All platforms": parts.append(f'Platform: {ss["flt_platform"]}')
    if ss["flt_country"]  != "All countries": parts.append(f'Country: {ss["flt_country"]}')
    if ss["flt_artist"]   != "All artists":   parts.append(f'Artist: {ss["flt_artist"]}')
    if ss["flt_release"]  != "All releases":  parts.append(f'Release: {ss["flt_release"]}')
    if ss["flt_track"]    != "All tracks":    parts.append(f'Track: “{ss["flt_track"]}”')
    return " · ".join(parts)

applied = filters_summary(st.session_state)
if applied: st.caption(f"**Filters applied:** {applied}")

# Final filtered dataframe
df_filt = df_filt_stage

# ─────────────────────────────────────────────────────────
# Chart
chart_placeholder = st.container()
with chart_placeholder:
    if df_filt.empty:
        st.warning("No data to display. Try adjusting the filters.")
    else:
        key_col, label_col, default_title = resolve_dim_keys(analysis_type, df_filt)

        ctx = []
        if st.session_state.get("flt_platform") != "All platforms": ctx.append(st.session_state["flt_platform"])
        if st.session_state.get("flt_country")  != "All countries": ctx.append(st.session_state["flt_country"])
        if st.session_state.get("flt_artist")   != "All artists":   ctx.append(st.session_state["flt_artist"])
        if st.session_state.get("flt_release")  != "All releases":  ctx.append(st.session_state["flt_release"])
        if st.session_state.get("flt_track")    != "All tracks":    ctx.append(f'"{st.session_state["flt_track"]}"')
        chart_ctx = " · ".join(ctx)

        total_streams = float(df_filt["quantity"].sum())
        total_revenue = float(df_filt["revenue"].sum())
        total_for_pct = total_revenue if metric == "Earnings" else (total_streams if metric == "Streams" else 0)
        chart_title = f"{default_title} by {metric}" + (f" — {chart_ctx}" if chart_ctx else "")

        make_top_barplot(
            df_src=df_filt, key_col=key_col, label_col=label_col, title=chart_title,
            top_n=top_n, metric=metric, show_pct=show_pct, total_value=total_for_pct
        )

# Export table
if not df_filt.empty:
    key_col, label_col, _ = resolve_dim_keys(analysis_type, df_filt)
    agg = aggregate_with_labels(df_filt, key_col, label_col).copy()
    agg["Value per 1K Streams"] = agg["rpm"]

    # >>> NEW: тот же порог для выгрузки, когда выбран RPM
    if metric == "Value per 1K Streams":
        agg = agg[agg["quantity"] >= RPM_MIN_STREAMS]

    dim_col_name = {
        "platform":"Platform",
        "country":"Country",
        "artist_name":"Artist",
        "release_title":"Release",
        "track_title":"Track"
    }.get(label_col, label_col.title())

    export_df = agg[["label","quantity","revenue","Value per 1K Streams"]].rename(
        columns={"label": dim_col_name, "quantity":"Streams", "revenue":"Earnings"}
    )
    sort_key = "Earnings" if metric == "Earnings" else ("Streams" if metric == "Streams" else "Value per 1K Streams")
    export_df = export_df.sort_values(sort_key, ascending=False)

    st.download_button(
        label="⬇️ Download table (CSV contains what you see in the chart)",
        data=export_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{_slug(label_col)}_summary.csv",
        mime="text/csv",
        use_container_width=True
    )
