import streamlit as st 
import pandas as pd

st.set_page_config(page_title="Streaming Analytics", layout="wide")

# ⬇️ Единый контейнер 1200px
st.markdown("""
<style>
.block-container { max-width: 1200px; margin: auto; padding-left: 1rem; padding-right: 1rem; }
</style>
""", unsafe_allow_html=True)

# ⬇️ Стили для синей кнопки "primary"
st.markdown("""
<style>
div.stButton > button[kind="primary"] {
    background-color: #1f6feb;      /* синий GitHub-style */
    border: 1px solid #1f6feb;
    color: white;
    font-weight: 500;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #1a5fd0;      /* темнее при наведении */
    border-color: #1a5fd0;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🎵 Streaming Royalty Analyzer")

# --- Текст НАД загрузчиком ---
st.markdown(
    """
This tool helps **independent artists, labels, and managers** quickly turn royalty reports from distributors (e.g., Believe, ONErpm, DistroKid, TuneCore) into clear insights.  
Use these insights to plan your next release, target promotion where it matters, and show partners the real value of your music.

In one dashboard, you can instantly see:  
- Which tracks and releases drive your revenue  
- Where you’re strongest — by platform and country
- The real value of your streams
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

# убрали текстовую подпись
uploaded = st.file_uploader(
    label="",                      # пустая строка
    type=["csv", "xlsx"],
    label_visibility="collapsed"   # скрыть label совсем
)

if uploaded:
    try:
        current_signature = (uploaded.name, getattr(uploaded, "size", None))

        # если новый файл — сбрасываем промежуточные состояния
        if st.session_state.get("uploaded_signature") != current_signature:
            for key in ("mapped_fields", "mapping", "df_norm"):
                st.session_state.pop(key, None)

        name = uploaded.name.lower()
        if name.endswith(".csv"):
            df = robust_read_csv(uploaded)
        else:
            uploaded.seek(0)
            df = pd.read_excel(uploaded)

        st.session_state["df"] = df
        st.session_state["uploaded_file_name"] = uploaded.name
        st.session_state["uploaded_signature"] = current_signature

        # ✅ компактное подтверждение + имя файла
        st.success(f"✅ File successfully loaded")

        # показываем только первые 5 строк
        st.dataframe(df.head(5), use_container_width=True)

        # дружелюбная кнопка + выделение CTA цветом
        if st.button("Continue", type="primary"):
            st.switch_page("pages/1_📊_Overview.py")

    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.info("Try saving as UTF-8 CSV or Excel (.xlsx). If it still fails, send a message to royalty.analyzer@gmail.com.")
else:
    st.info("Upload a report to continue")

# --- Текст ПОД загрузчиком ---
st.markdown(
    """
### Having trouble?
Maybe the file doesn’t upload, the dashboard doesn’t open, or the charts stay empty.  
That’s okay — we’re adding support for more distributors all the time.  
Just send us a message at **royalty.analyzer@gmail.com**, and we’ll make it work for you.

### Try it right now
Want to see how it works? Try analyzer now with a sample report: [📥 Download](https://drive.google.com/file/d/1g0dXM4ZWUg1kvuaYUsLlzCeCxmIhd-GF/view?usp=drive_link)

---

💡 If you’re a label, manager, or artist interested in deeper catalog insights or custom analytics — reach out: **eugkoos@gmail.com**  
Or connect on [LinkedIn](https://www.linkedin.com/in/eugenekos/)
    """,
    unsafe_allow_html=True
)
