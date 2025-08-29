# U.S. Adult Obesity Prevalence Forecast (2011–2030)

## Overview
This project forecasts U.S. adult obesity prevalence using **Prophet**, validated with 2021–2023 data, and visualized through an **interactive Plotly choropleth map**. Users can toggle between **Observed (2011–2023)** and **Predicted (2024–2030)** modes to explore trends.  
Data source: CDC’s Behavioral Risk Factor Surveillance System (BRFSS), used in DNPAO’s *Data, Trends, and Maps* database.

## Motivation
Adult obesity is one of the most pressing U.S. public health challenges. Forecasting prevalence helps policymakers, researchers, and healthcare organizations measure progress toward national health goals like **Healthy People 2030**.

---

## Features
- 📈 **Population-weighted national averages** per year.  
- ✅ **Validation per state** using 2021–2023 data (MAE 0.14%–3.05%).  
- 🌍 **Interactive choropleth map** with hover details + mode toggle.  
- 🔗 **Comparisons** to external forecasts (Harvard, CDC, AJPM).  

---

## Tech Stack
- **Languages/Tools**: Python, SQL  
- **Libraries**: Prophet, Plotly, Pandas, NumPy  
- **Future Skills**: Scikit-learn, TensorFlow (via IBM ML Cert)  

---

## Key Insights
- **Healthy People 2030 goal**: 36.0% adult obesity prevalence.  
- **Current prevalence (CDC 2021–2023)**: ~40% (severe obesity: 9.4%).  
- **Prophet forecast (2030, weighted)**: 37.27% — closer to the HP2030 target.  
- **External forecasts**:  
  - Harvard T.H. Chan / NEJM (2019): ~48%  
  - AJPM (2012): ~44%  

📌 Prophet’s conservative 37% forecast may reflect pre-2020 training data (less pandemic impact). The 37%–48% forecast range shows how modeling assumptions strongly influence long-term projections.

---

## Future Work
- Explore alternative models: **LSTM, XGBoost, Bayesian hierarchical**.  

## Getting Started
1. **Install Dependencies**:
   - Ensure Python 3.7+ is installed.
   - Run: `pip install -r requirements.txt` to install required libraries (Prophet, Plotly, Pandas, NumPy, cmdstanpy).
   - Note: `cmdstanpy` may require a C++ compiler (e.g., gcc) and internet for initial setup. If issues arise, try `pip install pystan` instead.
2. **Dataset**
   The dataset has been pre-cleaned and included in this repository as `cdc_health.csv`. It contains only the necessary rows and columns required for this project, so you **do not need to download anything from the CDC portal**.
   ### Preparing the Data
   1. Ensure `cdc_health.csv` is in the project folder.
   2. Use DB Browser for SQLite (or Python) to load this dataset into a table named `cdc_health`.
   3. Once the dataset is prepared, run `obesity_prevalence.py` to generate the visualizations.

## Files
- `obesity_prevalence.py`: Main script generating the forecast and visualizations.
- `obesity_prevalence_map.html`: Interactive choropleth map output.
- `prophet_validation_2021_2023.html`: Validation visualization for selected states.
- `cdc_health.csv`: Pre-cleaned dataset required for the script.

## License
[MIT License](LICENSE) *(Add a LICENSE file with MIT terms if open-source.)*
