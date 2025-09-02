# 🎶 Streaming Royalty Analyzer

A **Streamlit app** for musicians, managers, and labels.  
Upload royalty/streaming reports (CSV/XLSX) and instantly get insights: which releases drive your earnings, on which platforms, and in which countries.  

*Inspired by real-world royalty report structures from music distributors.*   

---

## ✨ Features
- **Upload & Auto-mapping** — upload your distributor report, and the app automatically detects key fields (Artist, Track, Platform, Country, Streams — you only need to review and confirm.  
- **Interactive Dashboard** — visualize performance by tracks, releases, platforms, and countries.  
- **Key Metrics** — Total Earnings, Total Streams, Payout per 1K Streams, Top Platforms, Countries, and Tracks.  
- **Top-N & % of total** — focus on Top 5/10/15… and see share of total earnings/streams.  
- **Export** — download the filtered table as CSV (earnings, streams, payout per 1K streams).  
- **🔍 Deep filters (context-aware)** — for each analysis view, context filters help you dive deeper:  
  - Platforms → filter by Artist, Country  
  - Countries → Platform, Artist  
  - Artists → Platform, Country  
  - Releases → Platform, Country  
  - Tracks → Platform, Country  
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

## 🚀 Live demo
👉 [Try the app on Streamlit Cloud](https://streaming-royalty-analyzer.streamlit.app/)  
📂 [Download sample report (CSV)](https://drive.google.com/file/d/1g0dXM4ZWUg1kvuaYUsLlzCeCxmIhd-GF/view)  

---

## 🛠 Tech stack
- **App:** Streamlit  
- **Data:** Pandas, openpyxl (Excel support)  
- **Visualization:** Plotly, Matplotlib, Seaborn  

---

## 🎯 Background
I spent 5+ years in the music industry:  
— label manager (100+ releases)  
— concert promoter (40+ concerts)  
— marketing campaigns  

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
requirements.txt
README.md
LICENSE
```

---

## 📜 License
MIT License © 2025 Eugene Kostiuchenko  

---

## 📬 Contacts
- **Email:** eugkoos@gmail.com  
- **LinkedIn:** [linkedin.com/in/eugenekos](https://www.linkedin.com/in/eugenekos/)  
- **GitHub:** [github.com/eugkoos](https://github.com/eugkoos)  

---

⚡ *For artists and managers — upload your report and instantly see which tracks, platforms, and markets drive your earnings.  
For HR and recruiters — this project demonstrates a full BI pipeline: data ingestion → auto-mapping → dashboard with deep filters → export.*  
