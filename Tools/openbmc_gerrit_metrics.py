# Create a helper that turns the CSVs/PNGs produced by `openbmc_gerrit_metrics.py`
# into a single self-contained HTML dashboard with embedded images (base64) and
# simple tables.
#
# Usage (after you run the metrics script):
#   python make_mini_lfx_dashboard.py --indir openbmc_metrics_out --out mini_lfx_dashboard.html
#
# The HTML is fully self-contained; you can open it locally or share it.

from textwrap import dedent

path = "/mnt/data/make_mini_lfx_dashboard.py"
code = r'''#!/usr/bin/env python3
import argparse
import base64
import csv
import html
import os
from datetime import datetime

def b64img(path):
    if not os.path.exists(path):
        return ""
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def read_csv(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def table_html(rows, title=None, max_rows=None):
    if not rows:
        return "<p><em>No data</em></p>"
    if max_rows is not None:
        rows = rows[:max_rows]
    cols = list(rows[0].keys())
    thead = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    trs = []
    for r in rows:
        tds = "".join(f"<td>{html.escape(str(r.get(c,'')))}</td>" for c in cols)
        trs.append(f"<tr>{tds}</tr>")
    tbl = f"<table class='tbl'><thead><tr>{thead}</tr></thead><tbody>{''.join(trs)}</tbody></table>"
    if title:
        return f"<h3>{html.escape(title)}</h3>{tbl}"
    return tbl

def main():
    ap = argparse.ArgumentParser(description="Build a self-contained mini LFX-style HTML dashboard from metrics CSVs/PNGs.")
    ap.add_argument("--indir", default="openbmc_metrics_out", help="Directory containing CSVs and PNGs from the metrics script")
    ap.add_argument("--out", default="mini_lfx_dashboard.html", help="Output HTML file")
    ap.add_argument("--title", default="OpenBMC ODM Metrics — Mini LFX Dashboard", help="Page title")
    args = ap.parse_args()

    indir = args.indir
    raw_csv = os.path.join(indir, "changes_raw.csv")
    monthly_csv = os.path.join(indir, "monthly_counts.csv")
    summary_csv = os.path.join(indir, "summary.csv")

    chart_monthly = os.path.join(indir, "chart_monthly_changes.png")
    chart_ttm = os.path.join(indir, "chart_ttm_boxplot.png")
    chart_ps = os.path.join(indir, "chart_avg_patchsets.png")

    rows_raw = read_csv(raw_csv)
    rows_monthly = read_csv(monthly_csv)
    rows_summary = read_csv(summary_csv)

    img_monthly = b64img(chart_monthly)
    img_ttm = b64img(chart_ttm)
    img_ps = b64img(chart_ps)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(args.title)}</title>
<style>
  :root {{
    --bg:#0b0d12; --card:#151922; --text:#e8eef7; --muted:#9db0c9; --accent:#6fb4ff;
    --ok:#5ad398; --warn:#ffb454; --bad:#ff6b6b; --table:#1b2230;
  }}
  body {{ background:var(--bg); color:var(--text); font: 14px/1.6 Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin:0; }}
  header {{ padding:24px; border-bottom:1px solid #202636; position: sticky; top:0; background:linear-gradient(0deg, rgba(11,13,18,0.85), rgba(11,13,18,0.95)); backdrop-filter: blur(6px); }}
  h1 {{ margin:0 0 6px; font-size:22px; }}
  .muted {{ color:var(--muted); }}
  main {{ padding:24px; display:grid; grid-template-columns: repeat(auto-fit, minmax(320px,1fr)); gap:16px; }}
  section.card {{ background:var(--card); border:1px solid #202636; border-radius:16px; padding:16px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }}
  section.card h2 {{ margin:0 0 8px; font-size:18px; }}
  section.card h3 {{ margin:12px 0 8px; font-size:16px; color:var(--accent); }}
  .imgwrap {{ width:100%; overflow:auto; border-radius:12px; background: #0f1320; border:1px solid #1f2840; }}
  .imgwrap img {{ display:block; width:100%; height:auto; }}
  .tbl {{ width:100%; border-collapse: collapse; background:var(--table); border-radius:12px; overflow:hidden; }}
  .tbl thead th {{ text-align:left; padding:8px 10px; background:#22304a; color:#d0e2ff; border-bottom:1px solid #2b3b58; position:sticky; top:0; }}
  .tbl td {{ padding:8px 10px; border-bottom:1px solid #253248; }}
  .kpis {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:10px; }}
  .kpi {{ background:linear-gradient(180deg,#182136, #121826); border:1px solid #1e2a41; border-radius:12px; padding:12px; }}
  .kpi .label {{ font-size:12px; color:var(--muted); }}
  .kpi .value {{ font-size:20px; margin-top:4px; }}
  footer {{ padding:16px 24px; color:var(--muted); border-top:1px solid #202636; }}
  a, a:visited {{ color:var(--accent); }}
</style>
</head>
<body>
  <header>
    <h1>{html.escape(args.title)}</h1>
    <div class="muted">Generated at {generated_at} — Source: Gerrit REST (via metrics script output)</div>
  </header>
  <main>
    <section class="card">
      <h2>Summary</h2>
      <div class="kpis">
        <div class="kpi"><div class="label">Organizations</div><div class="value">{len({r.get('org') for r in rows_summary}) if rows_summary else 0}</div></div>
        <div class="kpi"><div class="label">Changes (total)</div><div class="value">{sum(int(r.get('changes',0) or 0) for r in rows_summary) if rows_summary else 0}</div></div>
        <div class="kpi"><div class="label">Months Covered</div><div class="value">{len(rows_monthly) if rows_monthly else 0}</div></div>
      </div>
      {table_html(rows_summary, "By Organization (changes / median TTM / avg patch sets)")}
    </section>

    <section class="card">
      <h2>Monthly Merged Changes</h2>
      {"<div class='imgwrap'><img alt='Monthly merged changes' src='" + img_monthly + "'></div>" if img_monthly else "<p><em>No chart available. Run the metrics script first.</em></p>"}
      {table_html(rows_monthly, "Monthly Counts (first 24 rows)", max_rows=24)}
    </section>

    <section class="card">
      <h2>Time to Merge (Days)</h2>
      {"<div class='imgwrap'><img alt='TTM boxplot' src='" + img_ttm + "'></div>" if img_ttm else "<p><em>No chart available. Run the metrics script first.</em></p>"}
    </section>

    <section class="card">
      <h2>Average Patch Sets</h2>
      {"<div class='imgwrap'><img alt='Avg patch sets' src='" + img_ps + "'></div>" if img_ps else "<p><em>No chart available. Run the metrics script first.</em></p>"}
    </section>

    <section class="card">
      <h2>Raw Changes (preview)</h2>
      {table_html(rows_raw[:50], "First 50 rows of changes_raw.csv") if rows_raw else "<p><em>No raw CSV found.</em></p>"}
      <p class="muted">Tip: open the CSVs in a spreadsheet for deeper filtering.</p>
    </section>
  </main>
  <footer>
    Mini LFX Dashboard — built from local CSV/PNG artifacts generated by your metrics fetcher. Customize this page or re-run with fresh data anytime.
  </footer>
</body>
</html>
"""
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"Wrote {args.out}")
    if not rows_summary and not rows_monthly and not rows_raw:
        print("Note: No input CSVs found. Run your metrics script first (openbmc_gerrit_metrics.py).")

if __name__ == "__main__":
    main()
'''
with open(path, "w") as f:
    f.write(code)

path
