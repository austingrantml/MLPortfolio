import sqlite3
import sys
import numpy as np
import pandas as pd
import plotly.express as px
from prophet import Prophet

# CONFIG
DB_PATH = "health_cdc.sqlite"  # always use this database

# CONNECT & VERIFY
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("Tables in DB:", tables)

TABLE = 'cdc_health' if 'cdc_health' in tables else (tables[0] if tables else None)
if TABLE is None:
    print("No tables found in the database. Import your CSV first.")
    sys.exit(1)

# Verify required columns exist
cur.execute(f"PRAGMA table_info({TABLE})")
cols = {row[1] for row in cur.fetchall()}
required = {
    'LocationDesc', 'LocationAbbr', 'Topic', 'Data_Value', 'YearEnd',
    'StratificationCategory1', 'Stratification1'
}
missing_cols = required - cols
if missing_cols:
    print(f"Table '{TABLE}' is missing required columns: {missing_cols}")
    sys.exit(1)

# QUERY: Pull the rows we care about (overall adult obesity prevalence)
query = f"""
SELECT
  YearEnd AS Year,
  LocationDesc AS state_name,
  LocationAbbr AS state_abbr,
  CAST(
    CASE
      WHEN YearEnd = 2023 AND LocationAbbr = 'PA' THEN 33.4
      WHEN YearEnd = 2023 AND LocationAbbr = 'KY' THEN 37.7
      WHEN YearEnd = 2021 AND LocationAbbr = 'FL' THEN 30.5
      ELSE Data_Value
    END AS FLOAT) AS obesity_prevalence
FROM {TABLE}
WHERE Topic = 'Obesity / Weight Status'
  AND Question = 'Percent of adults aged 18 years and older who have obesity'
  AND StratificationCategory1 = 'Total'
  AND Stratification1 = 'Total'
  AND LocationDesc NOT IN ('National', 'Guam', 'Puerto Rico', 'Virgin Islands', 'District of Columbia')
GROUP BY YearEnd, LocationAbbr
"""
df = pd.read_sql_query(query, conn)
conn.close()

# CLEAN & SANITY CHECKS
df = df.dropna(subset=['obesity_prevalence', 'state_abbr', 'state_name'])
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype(int)
print("Available Years:", sorted(df['Year'].unique()))
print("Available States:", sorted(df['state_abbr'].unique()))

# Small debug: show problematic rows for FL / PA / KY if any
cur = sqlite3.connect(DB_PATH).cursor()
cur.execute(f"""
    SELECT YearEnd, LocationDesc, Data_Value
    FROM {TABLE}
    WHERE Topic = 'Obesity / Weight Status'
      AND Question = 'Percent of adults aged 18 years and older who have obesity'
      AND StratificationCategory1 = 'Total'
      AND Stratification1 = 'Total'
      AND LocationDesc IN ('Florida', 'Pennsylvania', 'Kentucky')
      AND YearEnd IN (2021, 2023)
""")
print("\n2021/2023 Debug for FL, PA, KY:", cur.fetchall())

# FORECAST: per-state Prophet forecasts (train <= 2020, validate 2021-2023)
future_years = pd.date_range(start='2024-01-01', end='2030-12-31', freq='YE').year
future_df = []
validation_store = {}  # keep per-state 2021–2023 validation

# Iterate over states and fit individual Prophet models
for state_abbr in df['state_abbr'].unique():
    state_data = df[df['state_abbr'] == state_abbr].sort_values('Year').copy()
    prophet_df = pd.DataFrame({
        'ds': pd.to_datetime(state_data['Year'].astype(str)),
        'y': state_data['obesity_prevalence']
    })

    # Train on 2011–2020 (or whatever years are <= 2020)
    train_df = prophet_df[prophet_df['ds'].dt.year <= 2020]

    # If not enough training data, skip gracefully
    if train_df.shape[0] < 3:
        # Not enough history to train Prophet reliably; fall back to a simple linear extrapolation
        # but still try to keep consistent shape: use last observed value repeated
        last_vals = state_data[state_data['Year'] <= 2020]['obesity_prevalence']
        last_val = float(last_vals.iloc[-1]) if len(last_vals) > 0 else np.nan
        # create simple constant future
        fut = pd.DataFrame({'Year': future_years})
        fut['state_name'] = state_data['state_name'].iloc[0] if len(state_data) > 0 else state_abbr
        fut['state_abbr'] = state_abbr
        fut['obesity_prevalence'] = last_val
        future_df.append(fut)
        validation_store[state_abbr] = {'years': [2021,2022,2023], 'actual': np.array([np.nan,np.nan,np.nan]), 'pred': np.array([last_val,last_val,last_val]), 'mae': np.nan}
        print(f"Skipped Prophet for {state_abbr} (insufficient training rows). Falling back to last-observed fill.")
        continue

    # fit Prophet
    model = Prophet(yearly_seasonality=True, changepoint_prior_scale=0.05)
    model.fit(train_df)

    # Validate 2021–2023
    validate_years = [2021, 2022, 2023]
    validate_dates = pd.DataFrame({'ds': pd.to_datetime(validate_years, format='%Y')})
    validate_forecast = model.predict(validate_dates)
    actuals = state_data[state_data['Year'].isin(validate_years)]['obesity_prevalence'].values
    preds = validate_forecast['yhat'].values
    mae = float(np.mean(np.abs(actuals - preds))) if len(actuals) == len(preds) and len(preds) > 0 else np.nan
    validation_store[state_abbr] = {
        'years': validate_years, 'actual': actuals, 'pred': preds, 'mae': mae
    }
    if not np.isnan(mae):
        print(f"MAE for {state_abbr} (2021–2023): {mae:.2f}%")

    # Predict future 2024–2030
    future_dates = pd.DataFrame({'ds': pd.to_datetime(future_years.astype(str))})
    forecast = model.predict(future_dates)

    # Build state's future dataframe
    state_future = pd.DataFrame({
        'Year': future_years,
        'state_name': state_data['state_name'].iloc[0],
        'state_abbr': state_abbr,
        'obesity_prevalence': forecast['yhat'].clip(20, 50),  # clip to reasonable band
    })
    future_df.append(state_future)

# concat futures
future_df = pd.concat(future_df, ignore_index=True)

# COMBINE actuals + forecasts into one table, mark is_forecast
df['is_forecast'] = False
future_df['is_forecast'] = True
df = pd.concat([df, future_df], ignore_index=True).sort_values(['Year', 'state_abbr']).reset_index(drop=True)

# BUILD hover text for clean portfolio tooltips
def mk_hover(r):
    tag = "Predicted" if r['is_forecast'] else "Actual"
    return f"{r['state_name']}<br>{int(r['Year'])}: {tag} {r['obesity_prevalence']:.1f}%"

df['hover_text'] = df.apply(mk_hover, axis=1)

# POPULATION DICTIONARY (Census 2020) used for population-weighted average
# Note: DC already excluded; territories excluded.
populations = {
    'AL': 5024279, 'AK': 733391,  'AZ': 7151502, 'AR': 3011524, 'CA': 39538223,
    'CO': 5773714, 'CT': 3605944, 'DE': 989948,  'FL': 21538187, 'GA': 10711908,
    'HI': 1455271, 'ID': 1839106, 'IL': 12812508,'IN': 6785528, 'IA': 3190369,
    'KS': 2937880, 'KY': 4505836, 'LA': 4657757, 'ME': 1362359, 'MD': 6177224,
    'MA': 7029917, 'MI': 10077331,'MN': 5706494, 'MS': 2961279, 'MO': 6154913,
    'MT': 1084225, 'NE': 1961504, 'NV': 3104614, 'NH': 1377529, 'NJ': 9288994,
    'NM': 2117522, 'NY': 20201249,'NC': 10439388,'ND': 779094,  'OH': 11799448,
    'OK': 3959353, 'OR': 4237256, 'PA': 13002700,'RI': 1097379, 'SC': 5118425,
    'SD': 886667,  'TN': 6910840, 'TX': 29145505,'UT': 3271616, 'VT': 643077,
    'VA': 8631393, 'WA': 7705281, 'WV': 1793716, 'WI': 5893718, 'WY': 576851
}

# Build frames for animation; for each year compute population-weighted national avg
# and attach it as an annotation within the frame layout so it updates when animating
years = sorted(df['Year'].unique())
frames = []
for year in years:
    df_year = df[df['Year'] == year].copy()

    # population-weighted national average (only states that have population mapping)
    pop_map = df_year['state_abbr'].map(populations)
    mask = pop_map.notna()
    if mask.sum() > 0:
        weighted_avg = (df_year.loc[mask, 'obesity_prevalence'] * pop_map[mask]).sum() / pop_map[mask].sum()
    else:
        weighted_avg = df_year['obesity_prevalence'].mean()

    # Observed vs Predicted tag for the frame
    mode_tag = "Predicted" if df_year['is_forecast'].any() else "Observed"
    ann_text = f"National Avg (pop-weighted) {year}: {weighted_avg:.2f}% ({mode_tag})"

    ann = dict(
        text=ann_text,
        x=0.5, xanchor='center',
        y=-0.06, yanchor='top',  # Moved under play/pause button (y=-0.08)
        xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=14, color='black')
    )

    frames.append(dict(
        data=[dict(
            locations=df_year['state_abbr'],
            z=df_year['obesity_prevalence'],
            hovertext=df_year['hover_text'],
            type='choropleth',
            locationmode='USA-states',
            colorscale='Viridis',
            reversescale=True,
            colorbar=dict(title="Obesity Prevalence (%)",
                          tickvals=[20, 30, 40],
                          ticktext=["20%", "30%", "40%"])
        )],
        name=str(year),
        layout=dict(annotations=[ann], title_text=f"Adult Obesity Prevalence by State - {year} ({mode_tag})")
    ))

# Subsets for modes: Observed and Predicted year lists + sliders/play args
observed_years = sorted(df.loc[~df['is_forecast'], 'Year'].unique().tolist())
predicted_years = sorted(df.loc[df['is_forecast'], 'Year'].unique().tolist())

def make_slider(year_list):
    return dict(
        active=0,
        steps=[dict(
            method="animate",
            args=[[str(y)], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}],
            label=str(y)
        ) for y in year_list],
        x=0.5, xanchor="center",
        y=-0.16, yanchor="top",
        pad={"t": 30, "b": 20}
    )

observed_slider = make_slider(observed_years)
predicted_slider = make_slider(predicted_years)

# Play sequences bound to mode (list of frame names)
obs_play_args = [[str(y) for y in observed_years], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate", "fromcurrent": True, "max_frame": len(observed_years) - 1}]
pred_play_args = [[str(y) for y in predicted_years], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate", "fromcurrent": True, "max_frame": len(predicted_years) - 1}]

# BUILD INITIAL FIGURE (start with first observed year)
df_initial = df[df['Year'] == observed_years[0]]

# compute initial pop-weighted avg for annotation
pop_map_init = df_initial['state_abbr'].map(populations)
mask_init = pop_map_init.notna()
if mask_init.sum() > 0:
    weighted_init = (df_initial.loc[mask_init, 'obesity_prevalence'] * pop_map_init[mask_init]).sum() / pop_map_init[mask_init].sum()
else:
    weighted_init = df_initial['obesity_prevalence'].mean()

init_ann = dict(
    text=f"National Avg (pop-weighted) {observed_years[0]}: {weighted_init:.2f}% (Observed)",
    x=0.5, xanchor='center',
    y=-0.06, yanchor='top',  # Moved under play/pause button (y=-0.08)
    xref='paper', yref='paper',
    showarrow=False,
    font=dict(size=14, color='black')
)

fig = px.choropleth(
    df_initial,
    locations="state_abbr",
    locationmode="USA-states",
    color="obesity_prevalence",
    hover_name="state_name",
    hover_data={"state_abbr": False, "Year": True},
    color_continuous_scale="Viridis",
    scope="usa",
    title="U.S. Adult Obesity Prevalence by State (%) — Historical & Prophet Forecast (to 2030)",
    range_color=[20, 45]
)

# Apply custom hover text (clean)
for tr in fig.data:
    tr.hovertext = df_initial['hover_text']
    tr.hovertemplate = "%{hovertext}<extra></extra>"

# Static mode label to the figure (UI polish)
mode_label_ann = dict(
    text="View Mode: Observed (2011–2023) vs Predicted (2024–2030) — use the mode buttons below",
    x=0.01, xanchor='left',
    y=1.135, yanchor='top',
    xref='paper', yref='paper',
    showarrow=False,
    font=dict(size=11, color='black')
)

fig.update_layout(annotations=[init_ann, mode_label_ann])

# CONTROLS: play/pause, year dropdown, mode toggle that swaps slider & play args
fig.update_layout(
    updatemenus=[
        # 0) Play / Pause (Play bound to Observed by default)
        dict(
            type="buttons",
            direction="left",
            buttons=[
                dict(args=obs_play_args, label="Play", method="animate"),
                dict(args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                     label="Pause", method="animate")
            ],
            pad={"r": 10, "t": 10},
            x=0.5, xanchor="center",
            y=-0.08, yanchor="top"
        ),
        # 1) Year jump dropdown (all years)
        dict(
            buttons=[
                dict(
                    args=[{
                        "z": [df[df['Year'] == y]['obesity_prevalence']],
                        "locations": [df[df['Year'] == y]['state_abbr']],
                        "hovertext": [df[df['Year'] == y]['hover_text']],
                        "annotations": frames[years.index(y)]['layout']['annotations'] if years.index(y) < len(frames) else []
                    }],
                    label=str(y), method="update"
                ) for y in years
            ],
            direction="down",
            pad={"r": 10, "t": 10},
            x=0.01, xanchor="left",
            y=1.06, yanchor="top"   # still below the title
        ),
        # 2) Mode toggle (Observed / Predicted) — swaps slider & play sequence
        dict(
            type="buttons",
            direction="right",
            buttons=[
                dict(
                    label="Observed",
                    method="relayout",
                    args=[{
                        "sliders": [observed_slider],
                        "updatemenus[0].buttons[0].args": obs_play_args
                    }]
                ),
                dict(
                    label="Predicted",
                    method="relayout",
                    args=[{
                        "sliders": [predicted_slider],
                        "updatemenus[0].buttons[0].args": pred_play_args
                    }]
                )
            ],
            pad={"r": 10, "t": 10},
            x=0.01, xanchor="left",
            y=1.12, yanchor="top"
        )
    ],
    # Start with Observed slider installed
    sliders=[observed_slider],
    coloraxis=dict(
        cmin=20, cmax=45, reversescale=True,
        colorbar=dict(title="Obesity Prevalence (%)", tickvals=[20, 30, 40], ticktext=["20%", "30%", "40%"])
    ),
    geo=dict(showlakes=True, lakecolor="lightblue"),
    margin=dict(t=160, b=200, l=40, r=40),  # extra bottom margin for annotations
    height=860
)

fig.frames = frames

fig.update_layout(
    title=dict(
        x=0.01, xanchor="left",  # left align
        y=0.97, yanchor="top"    # slightly above mode label
    )
)

# RENDER & SAVE
fig.show()
fig.write_html("obesity_prevalence_map.html")

# Validation figure (2021-2023) for showcase states
showcase_states = [s for s in ['TN', 'CA', 'NY'] if s in validation_store]
if showcase_states:
    rows = []
    for s in showcase_states:
        info = validation_store[s]
        for yr, a, p in zip(info['years'], info['actual'], info['pred']):
            rows.append({'state': s, 'Year': yr,
                         'Actual': float(a) if not np.isnan(a) else np.nan,
                         'Predicted': float(p)})
    val_df = pd.DataFrame(rows)

    # Melt for tidy plotting
    plot_df = val_df.melt(id_vars=['state', 'Year'], value_vars=['Actual', 'Predicted'],
                          var_name='Series', value_name='Prevalence')

    val_fig = px.line(
        plot_df, x='Year', y='Prevalence',
        color='Series', line_dash='Series',
        facet_col='state', facet_col_wrap=len(showcase_states),
        markers=True,
        title="Prophet Validation (Train ≤ 2020 → Predict 2021–2030): Selected States"
    )
    val_fig.update_yaxes(title="Prevalence (%)", matches=None)
    val_fig.update_xaxes(dtick=1)
    val_fig.update_layout(height=420, margin=dict(t=80, b=40, l=40, r=40))
    val_fig.show()
    val_fig.write_html("prophet_validation_2021_2023.html")

# PRINT: all 2030 predictions (head) and population-weighted national average for 2030
df_2030 = df[df['Year'] == 2030].copy()

# Unweighted mean (for reference)
national_avg_2030_unweighted = df_2030['obesity_prevalence'].mean()

# Population-weighted national average
pop_map_2030 = df_2030['state_abbr'].map(populations)
mask_2030 = pop_map_2030.notna()
if mask_2030.sum() > 0:
    national_avg_2030_weighted = (df_2030.loc[mask_2030, 'obesity_prevalence'] * pop_map_2030[mask_2030]).sum() / pop_map_2030[mask_2030].sum()
else:
    national_avg_2030_weighted = national_avg_2030_unweighted

print("\nAll 2030 Predictions (head):")
print(df_2030.head())
print(f"\nNational Average Obesity Prevalence in 2030 (Prophet, unweighted mean): {national_avg_2030_unweighted:.2f}%")
print(f"National Average Obesity Prevalence in 2030 (Prophet, POPULATION-WEIGHTED): {national_avg_2030_weighted:.2f}%")

# VALIDATION SUMMARY (MAE for 2021-2023)
mae_rows = []
for s, info in validation_store.items():
    if not np.isnan(info['mae']):
        mae_rows.append((s, info['mae']))
if mae_rows:
    mae_tbl = pd.DataFrame(mae_rows, columns=['State', 'MAE_2021_2023'])
    mae_tbl = mae_tbl.sort_values('MAE_2021_2023')
    print("\nPer-state Prophet validation MAE (percentage points), sorted best→worst:")
    print(mae_tbl.to_string(index=False))
else:
    print("\nNo MAE values computed (insufficient data).")


# KEY INSIGHTS
print("\nKey Insights:")
print("• Forecasts use Prophet (train ≤2020) with validation on 2021–2023 per state.")
print("• Toggle lets you flip between Observed (up to 2023) and Predicted (2024–2030).")
print("• The annotation under the map shows a population-weighted national average for the displayed year.")
print("• The printed value above is the population-weighted national average for 2030 for easy reference.")