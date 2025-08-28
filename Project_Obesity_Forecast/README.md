# U.S. Adult Obesity Prevalence Forecast (2011–2030)

## Overview
This project forecasts U.S. adult obesity prevalence using Prophet, validated with 2021–2023 data, and visualized with an interactive Plotly choropleth map. Toggle between **Observed (2011–2023)** and **Predicted (2024–2030)** modes to explore trends.

## Features
- Population-weighted national averages per year.
- MAE validation per state (e.g., 0.14%–3.05%).
- Interactive map with hover details.

## Tech Stack
- **Languages/Tools**: Python, SQL
- **Libraries**: Prophet, Plotly, Pandas, NumPy
- **Future Skills**: Scikit-learn, TensorFlow (via IBM ML Cert)

## Limitations & Future Work
The 2030 forecast (37.27%) underpredicts the CDC’s 2023 rate (40.3%), likely due to post-2020 structural changes (e.g., pandemic effects) not captured in the 2011–2020 training data. Prophet suits smooth trends but may lag on sudden shifts. Future enhancements include:
- Continuous retraining.
- Testing LSTM, XGBoost with features, or Bayesian hierarchical forecasting.
- Improving MAE outliers in smaller states (e.g., SD 3.05%) with partial pooling.

## Getting Started
1. **Install Dependencies**:
   - Ensure Python 3.7+ is installed.
   - Run: `pip install -r requirements.txt` to install required libraries (Prophet, Plotly, Pandas, NumPy, cmdstanpy).
   - Note: `cmdstanpy` may require a C++ compiler (e.g., gcc) and internet for initial setup. If issues arise, try `pip install pystan` instead.
2. **Prepare the Database**:
   - Download the CDC BRFSS dataset from [Nutrition, Physical Activity, and Obesity - Behavioral Risk Factor Surveillance System | Data | Centers for Disease Control and Prevention](https://data.cdc.gov/Nutrition-Physical-Activity-and-Obesity/Nutrition-Physical-Activity-and-Obesity-Behavioral/hn4x-zwk7/about_data).
   - Export the data to a SQLite database:
     - Use DB Browser for SQLite (download from [DB Browser for SQLite](https://sqlitebrowser.org/)).
     - Create a new database file named `health_cdc.sqlite`.
     - Import the CSV data into a table named `cdc_health`.
     - Ensure columns include: `LocationDesc`, `LocationAbbr`, `Topic`, `Data_Value`, `YearEnd`, `StratificationCategory1`, `Stratification1`.
3. Run `obesity_prevalence.py` to generate the map and validation figure.

## Files
- `obesity_prevalence.py`: Main script generating the forecast and visualizations.
- `obesity_prevalence_map.html`: Interactive choropleth map output.
- `prophet_validation_2021_2023.html`: Validation visualization for selected states.

## License
[MIT License](LICENSE) *(Add a LICENSE file with MIT terms if open-source.)*
