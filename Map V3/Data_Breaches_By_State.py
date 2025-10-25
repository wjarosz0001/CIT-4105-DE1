import pandas as pd
import plotly.express as px


INPUT_XLSX = "Map V3/DataBreach Organized.xlsx"

#load
df = pd.read_excel(INPUT_XLSX)

# Treat missing as UNKN, strip spaces, uppercase
states_raw = (
    df["breach_location_state"]
    .fillna("UNKN")
    .astype(str)
    .str.strip()
    .str.upper()
)


def normalize_state(val: str) -> str:
    # keep UNKN untouched
    if val == "UNKN":
        return "UNKN"
    else:
        return val

states_norm = states_raw.map(normalize_state)

#count
counts = states_norm.value_counts(dropna=False).reset_index()
counts.columns = ["state", "count"]

# Pull out UNKN
unknown_count = int(counts.loc[counts["state"] == "UNKN", "count"].sum()) if "UNKN" in counts["state"].values else 0

# Keep only valid USPS state codes for the map (and DC)
valid_codes = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA",
    "ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
    "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
}
plot_df = counts[counts["state"].isin(valid_codes)].copy()

#Plotting
fig = px.choropleth(
    plot_df,
    locations="state",
    locationmode="USA-states",
    color="count",
    color_continuous_scale="Viridis",
    scope="usa",
    title="Data Breaches by State Including Unknowns",
)

fig.update_layout(
    title={
        'text': "Data Breaches by State Including Unknowns",
        'x': 0.5,                # center horizontally
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=24, color='Black', family='Arial')
    },
    margin=dict(t=100)           # adds space above the map for the title
)

# Shows Unknown count
fig.add_annotation(
    text=f"Unknown {unknown_count}",
    xref="paper", yref="paper",
    x=0.98, y=0.5,                
    showarrow=False,
    font=dict(size=14, color="white"),
    bgcolor="rgba(0,0,0,0.65)",
    bordercolor="white",
    borderwidth=1,
    borderpad=6,
)

fig.add_shape(
    type="circle",
    xref="paper", yref="paper",
    x0=0.90, y0=0.47, x1=1.0, y1=0.53,   
    line=dict(width=0),
    fillcolor="rgba(0,0,0,0.35)"
)


fig.show()
fig.write_html("Map V3/breach_map.html")