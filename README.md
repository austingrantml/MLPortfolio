# Austin’s Machine Learning Portfolio
![Python](https://img.shields.io/badge/Python-3.11-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![ML](https://img.shields.io/badge/Machine%20Learning-Portfolio-orange) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A curated portfolio of machine learning experiments, models, and practical applications demonstrating applied data science and predictive analytics skills.

---

## 👋 About Me
Hi! I’m **Austin**, an aspiring Machine Learning Engineer passionate about solving real-world problems using Python, data analysis, and machine learning.  

This repository showcases projects that highlight:
- **Model development**: training, tuning, and evaluating ML models  
- **Data engineering**: cleaning, preprocessing, and transforming datasets  
- **Visualization**: clear, interactive, and insightful plots  

**Skills & Tools:** Python, SQL, Pandas, NumPy, Matplotlib, Plotly, Prophet, TensorFlow, PyTorch, Git/GitHub

---

## 🏗 Projects

### 1. **U.S. Adult Obesity Prevalence Forecast (2011–2030)** ![Prophet](https://img.shields.io/badge/Prophet-TimeSeries-blue) ![SQL](https://img.shields.io/badge/SQL-Database-lightgrey)
**Description:** Forecasted U.S. adult obesity prevalence using **Prophet**, validated with 2021–2023 CDC data. Includes an interactive Plotly choropleth map and comparison with Harvard and AJPM studies.

**Technologies:** Python, SQL, Prophet, Plotly, Pandas, NumPy  

**Key Achievements:**  
- **37.27% population-weighted forecast** for 2030 (Healthy People 2030 target: 36.0%)  
- MAE of **0.14%–3.05%** across states  
- Benchmarked against external studies for actionable insights  

**Code / Notebook:** [View Project](https://github.com/austingrantml/MLPortfolio/tree/main/Project_Obesity_Forecast)

---

### 2. **Automated Data Cleaning & Visualization Tool (2025)** 🧹📊  
![Python](https://img.shields.io/badge/Python-3.11-blue) ![Plotly](https://img.shields.io/badge/Plotly-InteractiveCharts-orange) ![Pandas](https://img.shields.io/badge/Pandas-DataFrame-lightgrey)

**Description:**  
A fully automated tool that reads any CSV or Excel dataset, cleans messy data, performs summary statistics, and generates an **interactive HTML report** with embedded charts. Designed for clients or teams who need quick, professional data insights without manual processing.

**Technologies:** Python, Pandas, NumPy, Plotly, HTML  

**Key Features:**  
- Handles **missing values**, **duplicates**, and **inconsistent formatting**  
- Automatically produces **histograms**, **correlation heatmaps**, and **summary tables**  
- Outputs a **cleaned dataset** (`cleaned_data.csv`) and a **single interactive report** (`report_summary.html`)  
- Built for small businesses, researchers, and data professionals needing instant clarity  

**Code / Notebook:** [View Project](https://github.com/austingrantml/MLPortfolio/tree/main/data_cleaner_project)

---

## ⚡ How to Run Projects
```bash
# Clone the repository
git clone https://github.com/austingrantml/MLPortfolio.git

# Navigate to project folder
cd MLPortfolio/Project_Obesity_Forecast
# or
cd MLPortfolio/data_cleaner_project

# Install dependencies
pip install -r requirements.txt

# Run the project
python obesity_prevalence.py
# or
python data_cleaner.py <your_dataset.csv>
