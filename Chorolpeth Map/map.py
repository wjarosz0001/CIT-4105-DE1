import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Load and inspect the dataset

file_path = "Chorolpeth Map/Data_Breach_Chronology_sample.csv"
df = pd.read_csv(file_path, delimiter='|', engine='python')


# Clean / normalize

# Use the 'source' column as the reporting state (keep only rows that have a state)
df = df.dropna(subset=['source']).copy()
df['source'] = df['source'].astype(str).str.upper().str.strip()

# Detect a column that indicates the reporting agency (e.g., HHS)
possible_agency_cols = ['reported_by', 'reporting_agency', 'agency', 'source_agency']
agency_col = next((c for c in possible_agency_cols if c in df.columns), None)

if agency_col is not None:
    df[agency_col] = df[agency_col].astype(str).str.upper().str.strip()
    hhs_count = int((df[agency_col] == 'HHS').sum())
else:
    # Fallback: if no explicit agency column, count rows where source literally says HHS
    hhs_count = int((df['source'] == 'HHS').sum())

# Count breaches by state (choropleth)

breach_counts = (
    df.loc[df['source'].str.len() == 2]  # keep 2-letter state codes
      .groupby('source', as_index=False)
      .size()
      .rename(columns={'source':'state', 'size':'breach_count'})
)


# Build a figure with two panels: map (left) + HHS bubble (right)

fig = make_subplots(
    rows=1, cols=2,
    specs=[[{'type': 'choropleth'}, {'type': 'xy'}]],
    column_widths=[0.82, 0.18],
    horizontal_spacing=0.05,
    subplot_titles=(
        "Heat Map of Data Breaches by State",
        "Reported by HHS"
    )
)

# Choropleth
choropleth = px.choropleth(
    breach_counts,
    locations='state',
    locationmode='USA-states',
    color='breach_count',
    color_continuous_scale='Reds',
    scope='usa',
    labels={'breach_count': 'Number of Breaches'}
).data[0]

# Make state borders visible/dark
choropleth.marker.line.color = 'black'
choropleth.marker.line.width = 0.5

fig.add_trace(choropleth, row=1, col=1)

# Style the map geos
fig.update_geos(
    bgcolor='black',
    lakecolor='lightblue',
    landcolor='lightgrey',
    showcountries=True,
    showcoastlines=True,
    showland=True,
    projection_type='albers usa'
)


# Right-side "circle" (bubble) for HHS

# Compute a visually nice bubble size
max_state = int(breach_counts['breach_count'].max()) if not breach_counts.empty else 1
# Use sqrt scaling so size grows more gently
size = 40 if hhs_count == 0 else 20 + 40 * (np.sqrt(hhs_count) / np.sqrt(max(1, max_state)))

fig.add_trace(
    go.Scatter(
        x=[0], y=[0],
        mode='markers+text',
        text=[f"HHS Reports:\n{hhs_count:,}"],
        textposition='bottom center',
        marker=dict(
            symbol='circle',
            size=size,
            line=dict(color='white', width=2),
            opacity=0.9
        ),
        hovertemplate="HHS Reports: %{text}<extra></extra>"
    ),
    row=1, col=2
)

# Hide axes for the right panel and style background
fig.update_xaxes(visible=False, row=1, col=2)
fig.update_yaxes(visible=False, row=1, col=2)


# Overall styling

fig.update_layout(
    title=dict(text="Heat Map of Data Breaches by State", x=0.5),
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    coloraxis_colorbar=dict(title="Breaches")
)

# Render & save
fig.show()
fig.write_html("Chorolpeth Map/index.html")

#https://wjarosz0001.github.io/CIT-4105-DE1/Chorolpeth%20Map
