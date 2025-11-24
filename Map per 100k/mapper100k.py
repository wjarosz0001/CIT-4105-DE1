import pandas as pd
import plotly.express as px

INPUT_XLSX = "Map per 100k/DataBreach Organized.xlsx"

# Load data
df = pd.read_excel(INPUT_XLSX)

# Clean and normalize state column
states_raw = (
    df["breach_location_state"]
    .fillna("UNKN")
    .astype(str)
    .str.strip()
    .str.upper()
)

def normalize_state(val: str) -> str:
    if val == "UNKN":
        return "UNKN"
    return val

states_norm = states_raw.map(normalize_state)

# Count breaches per state
counts = states_norm.value_counts(dropna=False).reset_index()
counts.columns = ["state", "count"]

# Unknown
unknown_count = int(
    counts.loc[counts["state"] == "UNKN", "count"].sum()
) if "UNKN" in counts["state"].values else 0

# Valid state codes
valid_codes = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA",
    "ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
    "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
}

all_states_df = pd.DataFrame({"state": sorted(valid_codes)})

plot_df = all_states_df.merge(
    counts[counts["state"].isin(valid_codes)],
    on="state",
    how="left"
).fillna({"count": 0})

plot_df["count"] = plot_df["count"].astype(int)

pop_df = pd.read_csv("Map per 100k/state_populations.csv") #Adjusted version of this https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html 
pop_df["state"] = pop_df["state"].str.upper().str.strip()

# Merge population
plot_df = plot_df.merge(pop_df, on="state", how="left")

# Calculate breaches per 100,000
plot_df["breaches_per_100k"] = (
    plot_df["count"] / plot_df["population"] * 100000
)

plot_df["breaches_per_100k"] = plot_df["breaches_per_100k"].fillna(0)

max_per_100k = plot_df["breaches_per_100k"].max()
if max_per_100k <= 0:
    max_per_100k = 1

#mapper100k
fig = px.choropleth(
    plot_df,
    locations="state",
    locationmode="USA-states",
    color="breaches_per_100k",
    color_continuous_scale="Viridis",
    range_color=(0, max_per_100k),
    scope="usa",
    title="Data Breaches per 100,000 People by State",
    labels={"breaches_per_100k": "Breaches per 100,000"}
)

fig.update_coloraxes(
    colorbar=dict(
        tickmode="linear",
        dtick=0.5
    )
)

fig.update_layout(
    title={
        'text': "Data Breaches per 100,000 People by State",
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=24, color='Black', family='Arial')
    },
    margin=dict(t=100)
)

# Annotation for unknowns (optional)
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

fig.write_html("Map per 100k/index_per_100k.html")
fig.show()
