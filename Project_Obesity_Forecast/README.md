# U.S. Adult Obesity Prevalence Forecast (2011–2030)

## Overview
This project forecasts U.S. adult obesity prevalence using Prophet, validated with 2021–2023 data, and visualized with an interactive Plotly choropleth map. Toggle between **Observed (2011–2023)** and **Predicted (2024–2030)** modes to explore trends. The data is sourced from the CDC’s Nutrition, Physical Activity, and Obesity - Behavioral Risk Factor Surveillance System (BRFSS), used for DNPAO’s Data, Trends, and Maps database.

## Features
- Population-weighted national averages per year.
- MAE validation per state (e.g., 0.14%–3.05%).
- Interactive map with hover details.
- Comparison to external forecasts such as Harvard’s Happy Faces survey and CDC projections.

## Tech Stack
- **Languages/Tools**: Python, SQL
- **Libraries**: Prophet, Plotly, Pandas, NumPy
- **Future Skills**: Scikit-learn, TensorFlow (via IBM ML Cert)

## Key Insights & Limitations
- Healthy People 2030 goal (U.S. Department of Health and Human Services): **36.0%** (aim to reduce adult obesity prevalence through healthy eating and physical activity, developed via a collaborative process with government agencies and experts, supported by efforts from RFK Jr. and the administration to improve national health)
- Prophet population-weighted 2030 forecast: **37.27%** (potentially the closest to reality if these efforts succeed)
- Current adult obesity prevalence (CDC, August 2021–August 2023): **40%** (severe obesity: 9.4%; slight decrease from previous years, breaking a trend of increasing rates, though above the 36.0% goal, with recent figures around 40–42%)
- Harvard T.H. Chan School of Public Health 2030 forecast (NJEM, 2019): **~48%** (national average)
- American Journal of Preventive Medicine 2030 forecast (AJPM, 2012): **~44%**
Prophet’s 2030 forecast (37.27%) is more conservative, possibly due to its pre-2020 training data missing post-pandemic shifts, and aligns closely with the Healthy People 2030 goal if current health initiatives succeed. The variance among forecasts (37%–48%) reflects differences in data periods and modeling methods. Future work could explore LSTM, XGBoost, or Bayesian hierarchical models to better capture rapid changes.

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
