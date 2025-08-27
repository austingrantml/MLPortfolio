# U.S. Adult Obesity Prevalence Forecast (2011–2030)

## Overview
This project forecasts U.S. adult obesity prevalence using Prophet, validated with 2021–2023 data, and visualized with an interactive Plotly choropleth map. Toggle between **Observed (2011–2023)** and **Predicted (2024–2030)** modes to explore trends.

## Features
- Population-weighted national averages per year.
- MAE validation per state (e.g., 0.14%–3.05%).
- Interactive map with hover details.

## Tech Stack
- **Languages/Tools**: Python, SQL
- **Libraries**: Prophet, Plotly, Pandas
- **Future Skills**: Scikit-learn, TensorFlow (via IBM ML Cert)

## Limitations & Future Work
The 2030 forecast (37.27%) underpredicts the CDC’s 2023 rate (40.3%), likely due to post-2020 structural changes (e.g., pandemic effects) not captured in the 2011–2020 training data. Prophet suits smooth trends but may lag on sudden shifts. Future enhancements include:
- Continuous retraining.
- Testing LSTM, XGBoost with features, or Bayesian hierarchical forecasting.
- Improving MAE outliers in smaller states (e.g., SD 3.05%) with partial pooling.

## Getting Started
1. Ensure a SQLite DB (`health_cdc.sqlite`) with CDC BRFSS data is available.
2. Install dependencies: `pip install prophet plotly pandas`.
3. Run `obesity_prevalence_map.py` to generate the map and validation figure.

## Files
- `obesity_prevalence_map.py`: Main script.
- `obesity_prevalence_map.html`: Interactive map output.
- `prophet_validation_2021_2023.html`: Validation visualization.
