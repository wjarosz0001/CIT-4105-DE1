import pandas as pd

INPUT_CSV = "Unique_Cell_Strings for column K.csv"

def categorize_item(item):
    medical_keywords = ["health", "insurance", "patient", "hiv", "mychart",
                        "prescription", "member", "sub", "eye", "hospital",
                        "group", "medical", "diagnose", "medicare", "medication",
                        "treatment", "diagnosis", "clinic", "phsyician"]
    
    financial_keywords = ["account", "1099", "bank", "balance",
                        "cvv", "credit", "loan", "tax", "financ", "routing",
                        "expiration", "security code", "credit", "debit",
                         "claim", "payment", "payoff", "payroll", "discover", "billing"]
    
    digital_keywords = ["email", "e-mail", "access code", "username", "online", "password",
                        "website"]
    
    school_keywords = ["academic", "employ", "business", "iep", "compensation", "customer",
                       "degree", "education", "military", "income", "student", "wage",
                       "resume", "salary", "hr"]
    
    personal_keywords = ["address", "license", "biometric", "birth", "death",
                          "name", "passport", "personal", "phone", "social", "state",
                            "contact", "family", "fingerprint", "gov", "vehicale",
                            "signature", "sex", "postal", "gender", "race", "country", "city",
                            "citizenship", "demographic"]

    item_lower = str(item).lower()
    if any(keyword in item_lower for keyword in medical_keywords):
        return "Medical Information"
    elif any(keyword in item_lower for keyword in financial_keywords):
        return "Financial Information"
    elif any(keyword in item_lower for keyword in digital_keywords):
        return "Digital Identifiers"
    elif any(keyword in item_lower for keyword in school_keywords):
        return "School and Career Information"
    elif any(keyword in item_lower for keyword in personal_keywords):
        return "Personal Information"
    else:
        return "Other"

# Load CSV
df = pd.read_csv(INPUT_CSV)
TARGET_COLUMN = df.columns[0]

df["Category"] = df[TARGET_COLUMN].apply(categorize_item)

# ---- CHART ----
import matplotlib.pyplot as plt
from io import BytesIO
import base64

counts = df["Category"].value_counts()

plt.figure(figsize=(10,5))
ax = counts.plot(kind="bar")

plt.title("Breached Data types by Category")
plt.xlabel("Category")
plt.ylabel("Count")
plt.ylim(0, max(counts) + 20)
plt.tight_layout()

# Add labels above bars
for i, v in enumerate(counts):
    plt.text(i, v + 0.5, str(v), ha='center', fontweight='bold')

# Save plot to memory buffer for HTML embedding
buf = BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode('utf-8')
buf.close()

# ---- HTML REPORT ----
html = f"""
<html>
<head>
<title>Most Commonly Breached Data types by Category</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h1 {{ font-size: 22px; }}
img {{ max-width: 800px; border:1px solid #aaa; padding:10px; }}
table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 5px; }}
</style>
</head>
<body>
<h1>Most Commonly Breached Data types by Category</h1>
<p><b>Total Records:</b> {len(df)}</p>

<h2>Bar Chart</h2>
<img src="data:image/png;base64,{img_base64}" />

<h2>Category Counts</h2>
{counts.to_frame().to_html()}

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)