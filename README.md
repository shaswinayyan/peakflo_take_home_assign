# Peakflo AR Collections Analysis: Moving from "Chasing" to "Optimizing"

> **Project Update (May 2024):** This repository contains the full analysis, data story, and strategic recommendations for optimizing the Accounts Receivable (AR) process.
> **Live Data Story:** [View the New York Times-Style Report](https://shaswinayyan.github.io/peakflo_take_home_assign/)

---

## 📖 Project Overview
The CFO of a B2B SaaS client is facing unpredictable cash flow. The current collections process is manual, reactive, and "gut-feeling" based.
**The Goal:** Transform AR from a chaotic chase into a precision-engineered predictive engine.

This repository documents my **48-hour sprint** to:
1.  **Audit** the raw invoice data for quality and anomalies.
2.  **Segment** customers based on *behavior* (Speed & Consistency), not just volume.
3.  **Prototype** a solution using both Heuristics (Rule-based) and Machine Learning (Random Forest).
4.  **Deliver** a compelling narrative that bridges the gap between Data and Strategy.

---

## 📂 Repository Structure
This repo is organized for transparency and reproducibility:

```text
├── docs/                   # FINAL Web Application (GitHub Pages source)
│   ├── index.html          # Interactive "Data Story" app (NYT Style)
│   └── web_data.js         # Data payload for the visualization engine
├── notebooks/              # Jupyter Analysis
│   └── Peakflo_Analysis.ipynb  # The Core Analysis (Process -> Validation -> Recommendations)
├── reports/                # Strategic Documents & Artifacts
│   ├── Executive_Summary_Enhanced.md  # The "Bottom Line" for the CFO
│   ├── The_Peakflo_Chronicles.md      # The Narrative Arc ("Tale of Two Customers")
│   ├── ML_Experiment_Report.md        # Why we chose Heuristics over ML (for now)
│   └── Assumptions_and_Verification.md# Detailed Data Audit logs
├── scripts/                # Reproducibility Scripts
│   ├── create_notebook.py  # Generates the analysis notebook
│   ├── analysis_script.py  # ETL Pipeline
│   └── ml_experiment.py    # Random Forest Shadow Mode Prototype
└── data/                   # Processed Datasets (CSVs)
```

---

## ⚙️ methodology: The "Trust-First" Framework
My analysis follows a strict "Trust-First" pipeline. I did not simply feed data into a model.

### Phase 1: The Audit (Data Integrity)
Before analyzing, I verified the raw inputs.
*   **The Findings:** 25% of invoices had an `Amount Due` > `Total Amount`, indicating misapplied penalties.
*   **The Action:** I explicitly excluded these anomalies from the Revenue Forecast to prevent overstating recoverable cash.

### Phase 2: Segmentation (Behavioral Clustering)
I moved past "High vs Low" volume. I mapped every customer on a **Speed vs Consistency** matrix.
*   **Prompt Payer:** Pays early. (Strain on AR team: 0%)
*   **Slow but Steady ("Chaotic Charlie"):** Consistently pays ~15 days late. (Strategy: **Automated Nudge**, not calls).
*   **The Ghosts:** 112 accounts that have *never* paid. (Strategy: **Immediate Credit Lock**).

### Phase 3: The Model Decision (Heuristics > ML)
I trained a **Random Forest Regressor** (Accuracy: 87%, MAE: 29 Days) to predict payment dates.
**Strategic Choice:** I rejected shipping the ML model for Day 1.
*   **Reason:** Financial operations require transparency. A rule like *"3 Days Late = Nudge"* is auditable. A Black Box model is not.
*   **Plan:** The ML model runs in "Shadow Mode" to gather validation data for Q3 rollout.

---

## 🚀 Future Prospects & Roadmap
Due to the strict 48-hour delivery timeline, I prioritized **Analytic Rigor** and **Narrative Strategy** over full-stack engineering.
If I had 2 more days, I would implement:

1.  **Interactive Streamlit/Dash App**: Move the logic from the Notebook/HTML into a live Streamlit dashboard where the AR team can upload *new* CSVs and get instant segmentation.
2.  **What-If Scenarios**: A slider-based UI to simulate "What if we reduce DSO by 5 days?" and see the cash flow impact in real-time.
3.  **Production ML Pipeline**: Dockerize the Random Forest model and deploy it as an API endpoint (FastAPI) to score invoices in real-time as they are generated.
4.  **Email Integration**: Connect the "Smart Nudge" logic directly to SendGrid/SMTP to automate the emails for the "Slow but Steady" segment.

---

## 💡 How to Run This Project

### 1. The Interactive Story (No Code Required)
Visit the **[Live Data Story](https://shaswinayyan.github.io/peakflo_take_home_assign/)**.
*   *Experience the "Scrollytelling" narrative.*
*   *Interact with the Charts (Chart.js).*

### 2. The Code (Reproduce the Analysis)
Clone the repo and run the notebook:
```bash
git clone https://github.com/shaswinayyan/peakflo_take_home_assign.git
cd peakflo_take_home_assign
pip install pandas numpy plotly seaborn scikit-learn
jupyter notebook notebooks/Peakflo_Analysis.ipynb
```

---

**Author:** [Your Name]
**Role:** Analytics Engineer
**Status:** Ready for CFO Review.
