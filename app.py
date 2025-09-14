import streamlit as st
import pandas as pd

st.set_page_config(page_title="Streaming Analytics", layout="wide")

# ⬇️ Unified container 1200px
st.markdown("""
<style>
.block-container { max-width: 1200px; margin: auto; padding-left: 1rem; padding-right: 1rem; }
</style>
""", unsafe_allow_html=True)

# ⬇️ Styles for the blue "primary" button
st.markdown("""
<style>
div.stButton > button[kind="primary"] {
    background-color: #1f6feb;      /* GitHub-style blue */
    border: 1px solid #1f6feb;
    color: white;
    font-weight: 500;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #1a5fd0;      /* darker on hover */
    border-color: #1a5fd0;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🎵 Streaming Royalty Analyzer")

# --- Intro text ---
st.markdown(
    """
This tool helps **independent artists, labels, and managers** quickly turn raw royalty reports from distributors into clear insights.  

Upload your royalty or streaming reports (CSV/XLSX) and instantly discover:  
- Which tracks and releases drive your earnings  
- On which platforms and in which countries you are strongest  
- The real value of your streams  

Use these insights to plan your next release, focus promotion where it matters most, and demonstrate the true value of your music to partners.  
    """,
    unsafe_allow_html=True
)

# --- Session init ---
if "df" not in st.session_state:
    st.session_state["df"] = None
if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None
if "uploaded_signature" not in st.session_state:
    st.session_state["uploaded_signature"] = None  # (name, size)

# --- Robust CSV reader ---
def robust_read_csv(file):
    """CSV reader with auto-separator and encoding fallback"""
    try:
        file.seek(0)
        return pd.read_csv(file, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
    except Exception:
        pass

    encodings = ["utf-8-sig", "utf-8", "cp1251", "latin-1"]
    seps = [",", ";", "\t", "|"]
    for enc in encodings:
        for sep in seps:
            try:
                file.seek(0)
                return pd.read_csv(file, sep=sep, engine="python", encoding=enc, on_bad_lines="skip")
            except Exception:
                continue

    raise ValueError("Could not parse CSV: try another delimiter/encoding.")

# --- Upload UI ---
st.header("Upload report file")

uploaded = st.file_uploader(
    label="",                    
    type=["csv", "xlsx"],
    label_visibility="collapsed"   
)

MAX_SIZE = 200 * 1024 * 1024  # 200 MB limit
ALLOWED_EXT = (".csv", ".xlsx")

if uploaded:
    try:
        # --- Size check ---
        if getattr(uploaded, "size", None) and uploaded.size > MAX_SIZE:
            st.error("❌ File too large. Maximum allowed size is 200 MB.")
            st.stop()

        # --- Extension check ---
        name = (uploaded.name or "").lower()
        if not name.endswith(ALLOWED_EXT):
            st.error("❌ Unsupported file type. Please upload a .csv or .xlsx file.")
            st.stop()

        current_signature = (uploaded.name, getattr(uploaded, "size", None))

        # Reset session state if a new file is uploaded
        if st.session_state.get("uploaded_signature") != current_signature:
            for key in ("mapped_fields", "mapping", "df_norm"):
                st.session_state.pop(key, None)

        # Try to read the file
        if name.endswith(".csv"):
            df = robust_read_csv(uploaded)
        else:
            uploaded.seek(0)
            df = pd.read_excel(uploaded)

        st.session_state["df"] = df
        st.session_state["uploaded_file_name"] = uploaded.name
        st.session_state["uploaded_signature"] = current_signature

        st.success("✅ File successfully loaded")

        # Show preview
        st.dataframe(df.head(5), use_container_width=True)

        if st.button("Continue", type="primary"):
            st.switch_page("pages/1_📊_Overview.py")

    except Exception:
        st.error("❌ Failed to read file. Please upload a valid UTF-8 CSV or .xlsx.")
else:
    st.info("Upload a report to continue")

# --- Short privacy note under uploader ---
st.caption(
    "🔒 Uploaded files are processed in memory only during your session, "
    "never stored on disk, not shared with third parties, and automatically discarded when the session ends. [Read full Privacy Policy](https://github.com/eugkoos/streaming-royalty-analyzer/blob/main/PRIVACY.md)"
)
# --- Outro text ---
st.markdown(
    """
### Having trouble?
Maybe the file doesn’t upload, the dashboard doesn’t open, or the charts stay empty.  
That’s okay — we’re continuously improving the tool.  
Just send us a message at **royalty.analyzer@gmail.com**, and we’ll make it work for you.

### Try it right now
Want to see how it works? Try analyzer now with a sample report: [📥 Download](https://drive.google.com/file/d/1g0dXM4ZWUg1kvuaYUsLlzCeCxmIhd-GF/view?usp=drive_link)

---

💡 If you’re a label, manager, or artist interested in deeper catalog insights or custom analytics — reach out: **eugkoos@gmail.com**  
Or connect on [LinkedIn](https://www.linkedin.com/in/eugenekos/)
    """,
    unsafe_allow_html=True
)

# --- Footer with Privacy & Terms (only on homepage) ---
st.markdown("---")
st.markdown(
    """
    <div style="font-size:0.9rem; color:#6b7280;">
      © 2025 • <a href="https://github.com/yourname/yourrepo/blob/main/PRIVACY.md" target="_blank">Privacy</a> •
      <a href="https://github.com/yourname/yourrepo/blob/main/TERMS.md" target="_blank">Terms</a>
    </div>
    """,
    unsafe_allow_html=True,
)