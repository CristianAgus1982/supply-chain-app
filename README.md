# 🏭 Supply Chain Planning System

> End-to-end demand forecasting system for manufacturing supply chains — XGBoost · FastAPI · React

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![XGBoost](https://img.shields.io/badge/XGBoost-3.2-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61dafb?logo=react)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Overview

This project implements a **production-grade supply chain demand forecasting system** for the manufacturing sector, inspired by enterprise platforms like RELEX Solutions.

It combines machine learning, a REST API, and an interactive dashboard into a complete end-to-end pipeline — from raw synthetic data generation to a live React dashboard that displays predictions, alerts, and SHAP explanations.

### Key capabilities

- **Demand forecasting** — predicts weekly demand for 10 industrial SKUs one week ahead
- **Automated alerts** — detects demand spikes, drops, and supplier risk before they become problems
- **Explainability** — SHAP values explain every individual prediction to supply chain managers
- **Live dashboard** — React frontend connected to the ML model via FastAPI REST API

---

## 🖥️ Dashboard Preview

```
┌──────────────────────────────────────────────────────────┐
│  Supply Chain Planning        ● API connected · 22:41    │
├──────────────┬───────────────┬──────────────┬────────────┤
│ 10 Products  │  10 Alerts    │  87 Avg Dem  │  P5 Var   │
│ Monitored    │  0H · 10M     │  Units/week  │  -88.8%   │
├──────────────────────────────────────────────────────────┤
│  Demand Forecast — Next Week                             │
│  [Bar chart: green = above avg, red = below avg]         │
├─────────────────────────┬────────────────────────────────┤
│  Active Alerts (10)     │  Why this prediction? (SHAP)   │
│  [ALL] [HIGH] [MEDIUM]  │  Product selector ▼            │
│  · P7 Demand Drop MEDIUM│  [Horizontal SHAP bar chart]   │
│  · P5 Supply Risk HIGH  │                                │
└─────────────────────────┴────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
supply-chain-app/
├── notebooks/
│   ├── 00_project_documentation.ipynb   # Full project docs
│   ├── 01_data_generation.ipynb         # Synthetic data generator
│   ├── 02_feature_engineering.ipynb     # Lags, rolling stats, encoding
│   ├── 03_xgboost_training.ipynb        # Walk-forward validation + SHAP
│   ├── 04_fastapi_backend.ipynb         # API source files + live testing
│   └── 05_react_dashboard.ipynb         # React components
├── src/api/
│   ├── main.py                          # FastAPI app + CORS + lifespan
│   ├── models.py                        # Pydantic request/response schemas
│   ├── routers/forecast.py              # /forecast endpoints
│   ├── routers/alerts.py                # /alerts endpoints
│   └── services/predictor.py            # ML inference service (singleton)
├── frontend/src/
│   ├── App.jsx                          # Root component + data fetching
│   ├── components/KPICards.jsx          # Summary metric cards
│   ├── components/ForecastChart.jsx     # Bar chart with tooltips
│   ├── components/AlertsPanel.jsx       # Filterable alerts list
│   ├── components/ShapPanel.jsx         # SHAP bar chart
│   └── api/client.js                    # FastAPI client functions
├── data/
│   ├── raw/                             # 6 CSVs from Notebook 01
│   └── processed/                       # ml_dataset.csv + feature_list.json
└── models/
    └── xgb_demand_model.pkl             # Trained XGBoost model
```

---

## 🔬 Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data | Pandas, NumPy | Synthetic data generation and feature engineering |
| ML | XGBoost, SHAP | Demand forecasting and explainability |
| Validation | Walk-forward | Time-series-correct model evaluation |
| API | FastAPI, Uvicorn | REST endpoints serving the ML model |
| Schemas | Pydantic | Request/response validation |
| Frontend | React, Vite | Interactive dashboard |
| Charts | Recharts | Forecast and SHAP visualisations |

---

## 📦 Data Pipeline

The system simulates **2 years of weekly manufacturing data** (104 weeks) across 5 variable groups:

| Group | Dataset | Key variables |
|-------|---------|--------------|
| A — Demand | `orders.csv` | ordered_qty, backlog, returns |
| B — Production | `production.csv` | capacity_hours, utilisation_pct, scrap_units |
| C — Suppliers | `suppliers.csv` | lead_time_real_d, reliability_pct, raw_material_price |
| D — External | `externals.csv` | PMI, energy_price_kwh, EUR/USD, is_holiday |
| E — Customers | `customers.csv` | framework_contract_units, has_promotion, has_launch |

Feature engineering produces **70+ features** including:
- Lag features at 1, 2, 4, 8, 13, 26, and 52 weeks
- Rolling mean, std, max, min over 4w and 12w windows
- Derived features: fill_rate, scrap_rate, supply_risk_score, demand_momentum
- Cyclical calendar encoding (week_sin, week_cos)

---

## 🤖 ML Model

### XGBoost with Walk-Forward Validation

The model is validated using **walk-forward (expanding window) validation** — the only correct approach for time series:

```
Fold 1:  Train [weeks 0-39]  → Predict week 40
Fold 2:  Train [weeks 0-40]  → Predict week 41
...
Fold N:  Train [weeks 0-T-1] → Predict week T
Final metrics = average across all folds
```

This simulates real Monday-morning deployment and produces honest performance estimates that match production reality.

### Hyperparameters

```python
XGB_PARAMS = {
    'n_estimators':     300,
    'max_depth':        5,
    'learning_rate':    0.05,
    'subsample':        0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 3,
    'reg_alpha':        0.1,
    'reg_lambda':       1.0,
}
```

### SHAP Explainability

Every prediction comes with a SHAP explanation — which features pushed the prediction up or down and by how much. This transforms XGBoost from a black box into a fully interpretable system.

---

## ⚡ API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/forecast/latest` | Predictions for all 10 products |
| `GET` | `/forecast/{product_id}` | Prediction for one product |
| `POST` | `/forecast/single` | Custom prediction (what-if analysis) |
| `POST` | `/forecast/batch` | Multiple predictions in one call |
| `GET` | `/forecast/shap/{product_id}` | SHAP explanation |
| `GET` | `/alerts` | Active alerts (optional `?severity=HIGH`) |
| `GET` | `/alerts/summary` | Alert counts by type and severity |

Interactive documentation available at `http://localhost:8000/docs` when the server is running.

---

## 🚀 Installation & Usage

### Prerequisites

- Anaconda or Miniconda
- Node.js 18+ LTS
- VS Code

### 1. Python environment

```bash
conda create -n supply-chain python=3.11 -y
conda activate supply-chain
conda install -c conda-forge jupyter jupyterlab notebook -y
pip install numpy pandas matplotlib seaborn scikit-learn xgboost lightgbm shap nbformat ipykernel
pip install fastapi "uvicorn[standard]" httpx python-multipart
python -m ipykernel install --user --name supply-chain --display-name "Supply Chain ML"
```

### 2. Run the notebooks

> ⚠️ Add this cell at the top of every notebook and run it first:
> ```python
> import os
> os.chdir(r"C:\path\to\supply-chain-app")
> ```

Run in order:
```
01_data_generation.ipynb
02_feature_engineering.ipynb
03_xgboost_training.ipynb
04_fastapi_backend.ipynb
05_react_dashboard.ipynb
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

### 4. Run the full stack

```bash
# Terminal 1 — FastAPI backend
conda activate supply-chain
cd supply-chain-app
$env:PYTHONPATH = "."          # Windows PowerShell
python -m uvicorn src.api.main:app --port 8000

# Terminal 2 — React dashboard
cd supply-chain-app/frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## 🧠 Key Design Decisions

**XGBoost over Prophet or LSTM** — handles 70+ mixed variables, trains in seconds, and supports SHAP explainability. Best tradeoff between performance, speed, and interpretability.

**Walk-forward validation** — a random split in time series produces optimistic metrics that collapse in production. Walk-forward simulates real deployment accurately.

**Multiplicative demand model** — factors are multiplied (not added) to capture compound effects: a holiday during a peak season is worse than either alone.

**Singleton model loading** — the model loads once at API startup and is shared across all requests, reducing response time from ~1s to ~1ms.

**shift(1) before rolling windows** — prevents data leakage by ensuring the model never sees the current week's demand when computing its own features.

---

## 🗺️ Next Steps

- [ ] PostgreSQL integration (replace CSV files)
- [ ] LSTM / Temporal Fusion Transformer model comparison
- [ ] Docker containerisation + cloud deployment
- [ ] Hyperparameter tuning with Optuna
- [ ] Real ERP data integration (SAP, Oracle)
- [ ] Automated weekly reporting via email/Slack
- [ ] Model drift detection and scheduled retraining

---

## 📄 License

MIT License — free to use, modify, and distribute.
