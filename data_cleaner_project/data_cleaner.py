"""
Automated Data Cleaning and Visualization Tool — with Single-File HTML Report
Author: Austin Grant

Usage:
    python data_cleaner.py <input_file.csv|xlsx>

Output:
    /output/cleaned_data.csv
    /output/report_summary.html   <-- one interactive HTML with embedded charts
"""

# === 1) Imports ===
import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px


# === 2) File Input ===
def load_data(file_path: str) -> pd.DataFrame:
    print(f"Loading dataset: {file_path}")
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in (".xls", ".xlsx"):
        df = pd.read_excel(file_path)
    else:
        sys.exit("Unsupported file format. Please use .csv or .xlsx")
    print(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
    return df


# === 3) Cleaning ===
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning dataset...")
    # Standardize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Remove duplicates
    before = df.shape[0]
    df = df.drop_duplicates()
    print(f"Removed {before - df.shape[0]} duplicate rows.")

    # Fill missing values: numeric -> median, others -> "Unknown"
    missing = int(df.isna().sum().sum())
    if missing > 0:
        print(f"Found {missing} missing values. "
              f"Filling numerics with median, strings with 'Unknown'.")
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("Unknown")

    print("Cleaning complete.")
    return df


# === 4) Summary Statistics ===
def summarize_data(df: pd.DataFrame) -> pd.DataFrame:
    print("\nDataset Summary:")
    print(f"- Rows: {df.shape[0]}")
    print(f"- Columns: {df.shape[1]}")
    print(f"- Column Types:\n{df.dtypes}\n")

    # Keep compatible with older pandas: omit datetime_is_numeric arg
    summary = df.describe(include="all")
    print(summary)
    return summary


# === 5) Visualization (return figures instead of saving separate files) ===
def build_figures(df: pd.DataFrame):
    """Return a dict of Plotly figures to embed into the report."""
    figs = {"histograms": [], "heatmap": None}

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Up to 3 histograms for the first few numeric columns
    for col in num_cols[:3]:
        fig = px.histogram(df, x=col, title=f"Distribution of {col}")
        figs["histograms"].append(fig)

    # Correlation heatmap if at least 2 numeric columns
    if len(num_cols) > 1:
        corr = df[num_cols].corr()
        # px.imshow works well for correlation matrices
        heat = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap (numeric columns)"
        )
        figs["heatmap"] = heat

    return figs


# === 6) Report Generation (single HTML with embedded charts) ===
def generate_report(df: pd.DataFrame,
                    summary: pd.DataFrame,
                    figs: dict,
                    output_dir: str = "output",
                    report_name: str = "report_summary.html") -> str:
    """Create a single self-contained HTML report with embedded Plotly charts."""
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, report_name)

    # Convert tables to HTML
    head_html = df.head(10).to_html(index=False, classes="table table-sm")
    summary_html = summary.to_html(classes="table table-sm", border=0)

    # Convert figures to HTML snippets (no full html, include plotlyjs once)
    # First figure includes plotlyjs from CDN; others exclude to save size.
    fig_snippets = []
    first = True

    # Histograms
    for fig in figs.get("histograms", []):
        html = fig.to_html(full_html=False,
                           include_plotlyjs="cdn" if first else False)
        fig_snippets.append(html)
        first = False

    # Heatmap
    if figs.get("heatmap") is not None:
        html = figs["heatmap"].to_html(full_html=False,
                                       include_plotlyjs="cdn" if first else False)
        fig_snippets.append(html)
        first = False

    charts_html = "\n".join(fig_snippets) if fig_snippets else "<p>No charts generated.</p>"

    # Minimal CSS for readability
    css = """
    <style>
      body { font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: #111; }
      h1 { margin: 0 0 8px 0; }
      h2 { margin-top: 28px; }
      .meta { color:#555; margin-bottom: 16px; }
      .grid { display: grid; grid-template-columns: 1fr; gap: 20px; }
      @media (min-width: 1000px) { .grid { grid-template-columns: 1fr 1fr; } }
      table { border-collapse: collapse; width: 100%; font-size: 14px; }
      th, td { border: 1px solid #ddd; padding: 6px 8px; }
      th { background: #f6f6f6; }
      .footer { color:#666; font-size: 12px; margin-top: 24px; }
      .pill { display:inline-block; padding:4px 10px; background:#eef; border-radius:999px; margin-right:8px;}
    </style>
    """

    # Build final HTML
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Data Cleaning & Visualization Report</title>
{css}
</head>
<body>
  <h1>Data Cleaning & Visualization Report</h1>
  <div class="meta">
    <span class="pill">Rows: {df.shape[0]}</span>
    <span class="pill">Columns: {df.shape[1]}</span>
  </div>

  <h2>Preview (first 10 rows)</h2>
  {head_html}

  <h2>Summary Statistics</h2>
  {summary_html}

  <h2>Visualizations</h2>
  <div class="grid">
    {charts_html}
  </div>

  <div class="footer">
    <p>Generated automatically by Austin's Data Cleaning & Visualization Tool.</p>
  </div>
</body>
</html>
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report saved to: {report_path}")
    return report_path


# === 7) Main ===
def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python data_cleaner.py <input_file.csv|xlsx>")

    input_path = sys.argv[1]

    # 1) Load
    df = load_data(input_path)

    # 2) Clean
    df = clean_data(df)

    # 3) Summary
    summary = summarize_data(df)

    # 4) Visuals (fig objects)
    figs = build_figures(df)

    # 5) Save cleaned dataset
    os.makedirs("output", exist_ok=True)
    cleaned_path = os.path.join("output", "cleaned_data.csv")
    df.to_csv(cleaned_path, index=False)
    print(f"Cleaned data saved to: {cleaned_path}")

    # 6) Generate single HTML report with embedded charts
    generate_report(df, summary, figs, output_dir="output")


if __name__ == "__main__":
    main()
