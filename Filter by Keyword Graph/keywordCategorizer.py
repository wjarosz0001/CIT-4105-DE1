import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

INPUT_CSV = "Filter by Keyword Graph/Unique_Cell_Strings for column K.csv"

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


X = df[TARGET_COLUMN].astype(str)
y = df["Category"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

vectorizer = TfidfVectorizer(stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

clf = LogisticRegression(max_iter=2000)
clf.fit(X_train_vec, y_train)

y_pred = clf.predict(X_test_vec)

accuracy = accuracy_score(y_test, y_pred)
report_text = classification_report(y_test, y_pred)

sample_results = pd.DataFrame({
    "Text": X_test.iloc[:10].values,
    "Actual Category": y_test.iloc[:10].values,
    "Predicted Category": y_pred[:10]
})

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

for i, v in enumerate(counts):
    plt.text(i, v + 0.5, str(v), ha='center', fontweight='bold')

buf = BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode('utf-8')
buf.close()

table_df = counts.reset_index()
table_df.columns = ["Category", "Count"]

# Convert classification report newlines to <br> for HTML
report_html = report_text.replace("\n", "<br>")

html = f"""
<html>
<head>
<title>Most Commonly Breached Data types by Category</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h1 {{ font-size: 22px; }}
img {{ max-width: 800px; border:1px solid #aaa; padding:10px; }}
table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 5px; }}
th {{ text-align: left; }}
pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 4px; }}
</style>
</head>
<body>
<h1>Most Commonly Breached Data types by Category</h1>
<p><b>Total Records:</b> {len(df)}</p>

<h2>Bar Chart</h2>
<img src="data:image/png;base64,{img_base64}" />

<h2>Category Counts</h2>
{table_df.to_html(index=False)}

<h2>Classification</h2>
<p>
For this question, we treat the dataset as a classification problem: 
given the text in each record, we predict which category it belongs to 
(Medical Information, Financial Information, Personal Information, etc.).
</p>

<p><b>Classification Accuracy:</b> {accuracy:.3f}</p>

<h3>Sample Predictions (Actual vs Predicted)</h3>
{sample_results.to_html(index=False)}

<h3>Classification Report</h3>
<pre>{report_text}</pre>

</body>
</html>
"""

with open("Filter by Keyword Graph/index.html", "w", encoding="utf-8") as f:
    f.write(html)
