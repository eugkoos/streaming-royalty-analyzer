# 🎶 Music Streaming Royalty Analyzer

A **Streamlit app** for musicians, managers, and labels.  
Upload royalty/streaming reports (CSV/XLSX) and instantly get insights: which releases drive your earnings, on which platforms, and in which countries.  

---

## ✨ Features
- **Upload & Auto-mapping** — upload your distributor report, and the app automatically detects key fields (Artist, Track, Platform, Country, Streams) — you only need to review and confirm.  
- **Tabbed Interactive Dashboard** — explore your data through dedicated tabs (Platforms, Countries, Artists, Releases, Tracks). Each tab shows KPIs, top lists, and charts.  
- **Key Metrics** — Total Earnings, Total Streams, Payout per 1K Streams, Top Platforms, Countries, and Tracks.  
- **Top-N & % of total** — focus on Top 5/10/15… and see share of total earnings/streams.  
- **Export** — download the filtered table as CSV (earnings, streams, payout per 1K streams).  
- **🔍 Context-aware filters** — each tab supports deep filtering, for example:  
  - Platforms → filter by Artist, Country  
  - Countries → filter by Platform, Artist  
  - Artists → filter by Platform, Country  
  - Releases → filter by Platform, Country  
  - Tracks → filter by Platform, Country  
  KPI, charts, and tables always recalc for the chosen slice.  

💡 **Examples**:  
- Platforms + Country=US → Top platforms by earnings in the US  
- Tracks + Platform=Spotify → Which tracks deliver most earnings on Spotify  
- Artists + Country=BR → Which artists are growing in Brazil  
---

## 💡 Why this app matters
Musicians and managers receive raw CSV/Excel royalty reports with tens of thousands of rows. They are hard to read and even harder to analyze.  

**Streaming Royalty Analyzer** turns these messy files into actionable dashboards in seconds:  

- 📊 **Clarity** — charts, KPI cards, and Top lists instead of endless tables.  
- 🎵 **Industry language** — *“How much did my tracks earn?”, “Which platforms and countries matter?”, “Payout per 1000 streams”*.  
- ⚡ **Time savings** — answers in seconds instead of hours in Excel.  
- 🧩 **Simplicity** — works in the browser, no technical skills required.  

---

## 🚀 Try it yourself  
👉 **Run the app on Streamlit Cloud** – [see it live in your browser](https://streaming-royalty-analyzer.streamlit.app/)  
📑 **Download Sample Report (CSV)** – [use it to test the app if you don’t have your own data](https://drive.google.com/file/d/1g0dXM4ZWUg1kvuaYUsLlzCeCxmIhd-GF/view)  

---

## 🛠 Tech stack
Python · Streamlit · Pandas · openpyxl · Plotly · Matplotlib · Seaborn

---

## 🎯 Background
I spent 5+ years in the music industry:  
— label and artist manager (100+ releases)  
— concert promoter (40+ concerts)  
— digital marketing campaigns  

Now I’m building my career as a **BI & Data Analyst**.  
This project is my bridge between music and analytics: it shows how raw distributor data can be transformed into insights that drive decisions.  

---

## ⚙️ How to run locally
```bash
# 1) Clone repository
git clone https://github.com/<your-username>/streaming-royalty-analyzer.git
cd streaming-royalty-analyzer

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run
streamlit run app.py
```

---

## 📂 Project structure
```
app.py
pages/
  1_📊_Overview.py
  2_📈_Dashboard.py
.streamlit/
  config.toml
LICENSE
SampleData/
  sample_distributor_report.csv
requirements.txt
README.md
LICENSE
PRIVACY.md
TERMS.md
.gitignore
```

---

### 📜 License
MIT License © 2025 Eugene Kostiuchenko  

---

## Disclaimer & Privacy

- This app is an **independent analytics tool** and does not store or share uploaded data.  
- It is **not affiliated with, sponsored by, or endorsed by any music distributor** (e.g., Believe, DistroKid, TuneCore, ONErpm).  
- Users must upload only royalty/streaming reports they are authorized to use.  
- Uploaded files are processed **only in memory** during your session and are not stored or shared.  
- Hosting is provided by [Streamlit Community Cloud](https://streamlit.io/cloud). Streamlit may collect aggregated or anonymized usage data as described in their [Trust & Security](https://streamlit.io/trust-and-security) documentation.  

See [PRIVACY.md](https://github.com/eugkoos/streaming-royalty-analyzer/blob/main/PRIVACY.md) and [TERMS.md](https://github.com/eugkoos/streaming-royalty-analyzer/blob/main/TERMS.md) for details.  

---

## 🎯 Why this project matters for BI & Analytics roles

This project is not only useful for musicians — it also demonstrates **core BI & Analytics competencies**:

- **End-to-end pipeline** — from raw messy reports (CSV/XLSX) → data cleaning & mapping → KPIs → interactive dashboards.  
- **Core BI skills** — data wrangling, schema mapping, calculation of marketing/business metrics (Earnings, Streams, RPM).  
- **Visualization** — interactive dashboards with KPIs, Top-N breakdowns, filters, and CSV export.  
- **Data security** — in-memory only, no file storage, with explicit Privacy & Terms (XSS protection, CSV injection prevention).  
- **Business context** — shows how raw operational data can be transformed into insights that drive smarter decisions.  

---

## 📬 Contacts
- **Email:** eugkoos@gmail.com  
- **LinkedIn:** [linkedin.com/in/eugenekos](https://www.linkedin.com/in/eugenekos/)  
- **GitHub:** [github.com/eugkoos](https://github.com/eugkoos)  
