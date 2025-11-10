import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# ----------------- Load Data -----------------
file = "Data Breach Time for breach type Hack.xlsx"
df = pd.read_excel(file)

# Map organization type codes to full names
org_map = {
    "BSF": "Financial Services Business",
    "BSO": "Other Business",
    "BSR": "Retail Business",
    "EDU": "Education",
    "MED": "Medical",
    "NGO": "Non-Governmental Organization",
    "UNKN": "Unknown"
}
df["organization_type"] = df["organization_type"].map(org_map).fillna(df["organization_type"])

# Ensure Days column is numeric and remove non-numeric
df["Days"] = pd.to_numeric(df["Days"], errors="coerce")
df_clean = df.dropna(subset=["Days"])

# ----------------- Print Averages -----------------
avg_by_org = df_clean.groupby("organization_type")["Days"].mean().reset_index()
avg_by_org.columns = ["organization_type", "average_days"]
overall_avg = df_clean["Days"].mean()

print("Average breach duration in days by organization type:\n")
print(avg_by_org.to_string(index=False))
print("\nOverall average breach duration in days:")
print(round(overall_avg, 2))

# ----------------- Scatter Plot -----------------
df_clean = df_clean.sort_values(by="organization_type")
org_types = df_clean["organization_type"].unique()
x_positions = {org: i for i, org in enumerate(org_types)}

plt.figure(figsize=(10,5))
for org in org_types:
    y = df_clean[df_clean["organization_type"] == org]["Days"]
    x = [x_positions[org]] * len(y)
    plt.scatter(x, y)

plt.xticks(range(len(org_types)), org_types, rotation=45, ha="right")
plt.xlabel("Organization Type")
plt.ylabel("Breach Duration (Days)")
plt.title("Scatter Plot of Breach Durations by Organization Type")
plt.tight_layout()

buf = BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
img_scatter = base64.b64encode(buf.read()).decode("utf-8")
buf.close()

# ----------------- HTML Export -----------------
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Breach Duration Analysis</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h1 {{ margin-bottom: 4px; }}
h2 {{ margin-top: 24px; }}
img {{ max-width: 100%; height: auto; border: 1px solid #777; padding: 8px; }}
.container {{ max-width: 1100px; margin: auto; }}
table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 6px; }}
</style>
</head>
<body>
<div class="container">
<h1>Breach Duration Analysis</h1>

<h2>Average Breach Duration by Organization Type</h2>
{avg_by_org.to_html(index=False)}

<h2>Overall Average Breach Duration (Days)</h2>
<p>{round(overall_avg, 2)}</p>

<h2>Scatter Plot: All Breach Durations</h2>
<img src="data:image/png;base64,{img_scatter}">
</div>
</body>
</html>
"""

with open("breach_duration_report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\nHTML report created: breach_duration_report.html")
