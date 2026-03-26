# 🇮🇳 Indian Startup Funding Dashboard

An interactive **Streamlit-based analytics dashboard** designed to explore and analyze the Indian startup funding ecosystem.

This project transforms raw, inconsistent funding data into **clean, structured, and actionable insights** using data cleaning, feature engineering, and interactive visualizations.

---

## 🌐 Live Demo

🔗 https://indianstartupfunddashboard-cuagchwcqwec4b2xz9wtoo.streamlit.app/

---

## 🚀 Key Features

### 📊 1. Overview Dashboard

A comprehensive snapshot of the startup ecosystem:

* **Key Metrics (KPIs)**

  * Total Funding
  * Maximum Funding
  * Average Funding
  * Total Startups Funded

* **Funding Trends**

  * Month-over-Month (MoM) funding trend
  * Time-series visualization

* **Sector Analysis**

  * Top sectors by funding
  * Cleaned and standardized categories

* **Geographic Insights**

  * City-wise funding distribution
  * **Interactive India Map Visualization** (funding hotspots)

* **Top Investors**

  * Ranked based on total investment

---

### 🏢 2. Startup Analysis

Explore detailed insights for individual startups:

* Funding history over time
* Year-wise funding trends
* Structured and cleaned startup data

---

### 💰 3. Investor Analysis

Understand investor behavior and patterns:

* Recent investments
* Top startups funded
* Sector-wise investment distribution
* Investment trends over time

---

## 🧠 Data Engineering Highlights

This project goes beyond visualization and focuses heavily on **real-world data cleaning challenges**:

### ✅ City Normalization

* Resolved inconsistent entries like:

  * `Bangalore / SFO` → Bangalore
  * `New York, Bengaluru` → Bangalore
* Removed non-Indian locations

---

### ✅ Sector Standardization

* Unified categories:

  * `fintech`, `finance`, `financial services` → **FinTech**
* Reduced noise by grouping smaller categories into **"Other"**

---

### ✅ Startup Name Cleaning

* Fixed inconsistencies:

  * `Byju///`, `BYJU’S`, `byjus` → **Byju’s**
  * `Ola Cabs`, `OLA` → **Ola**

---

### ✅ Investor Entity Resolution (Advanced)

* Consolidated variations:

  * `Sequoia Capital India` → **Sequoia**
  * `Lightspeed India`, `Lightspeed Ventures` → **Lightspeed**
  * `Aarin Capital Partners`, `Aarin Capital Others` → **Aarin Capital**

* Removed noise:

  * `Undisclosed HNIs`, invalid entries

* Handled multi-investor fields using:

  * **String parsing + explosion + deduplication**

---

## 📊 Dataset

The dataset includes:

* Startup Name
* Founders
* Industry / Sector
* City / Location
* Investors
* Funding Rounds & Stage
* Investment Date
* Funding Amount

---

## 🛠️ Tech Stack

* **Python 3**
* **Streamlit** – Interactive dashboard framework
* **Pandas & NumPy** – Data cleaning and transformation
* **Plotly** – Interactive visualizations
* **Matplotlib (initial version)**

---

## ⚙️ Key Functionalities

* Dynamic filtering (Year, City, Sector)
* Interactive charts and graphs
* Map-based visualization
* Clean dropdowns (no duplicates)
* Error handling for empty selections
* Optimized performance using caching

---

## 📈 Project Impact

* Improved data reliability through cleaning & normalization
* Reduced noise and duplication in key entities
* Enabled better decision-making through structured insights
* Built a **production-level analytics dashboard**

---

## 🧑‍💻 Author

**Aditya Kumar**

---

## ⭐ Conclusion

This project demonstrates:

* End-to-end **data analysis pipeline**
* Real-world **data cleaning & preprocessing**
* Interactive **dashboard development**
* Strong focus on **user experience and data accuracy**

---

## 🚀 Future Improvements

* Advanced filtering (funding stage, investor type)
* Real-time API integration
* Predictive analytics (future funding trends)
* Enhanced UI/UX design

---
