# U.S. Adult Obesity Prevalence Forecast (2011–2030)

## Overview
This project forecasts U.S. adult obesity prevalence using Prophet, validated with 2021–2023 data, and visualized with an interactive Plotly choropleth map. Toggle between **Observed (2011–2023)** and **Predicted (2024–2030)** modes to explore trends. The data is sourced from the CDC’s Nutrition, Physical Activity, and Obesity - Behavioral Risk Factor Surveillance System, used for DNPAO’s Data, Trends, and Maps database.

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

2. **Dataset**  
   This project uses the CDC’s **Nutrition, Physical Activity, and Obesity - Behavioral Risk Factor Surveillance System (BRFSS)** dataset.  

   👉 Download it directly from the CDC portal here:  
   [CDC DNPAO BRFSS Dataset (CSV)](https://chronicdata.cdc.gov/Nutrition-Physical-Activity-and-Obesity/Nutrition-Physical-Activity-and-Obesity-Behavioral/nf89-v3kw)

   ### Preparing the Data
   1. Click the link above and download the dataset as **CSV**.  
   2. Save the file in this project folder and rename it to:  
      ```
      cdc_health.csv
      ```
   3. Use DB Browser for SQLite (or Python) to load this dataset into a table named `cdc_health`.  
   4. Once the dataset is prepared, run `obesity_prevalence.py` to generate the visualizations.

## Files
- `obesity_prevalence.py`: Main script generating the forecast and visualizations.
- `obesity_prevalence_map.html`: Interactive choropleth map output.
- `prophet_validation_2021_2023.html`: Validation visualization for selected states.

## License
[MIT License](LICENSE) *(Add a LICENSE file with MIT terms if open-source.)*
