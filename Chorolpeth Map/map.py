import pandas as pd
import plotly.express as px


# Load and inspect the dataset
file_path = "Data_Breach_Chronology_sample.csv"

# Read the dataset (pipe-delimited)
df = pd.read_csv(file_path, delimiter='|', engine='python')


# Use the 'source' column as the reporting state
df = df.dropna(subset=['source'])

# Make sure state abbreviations are in upper case
df['source'] = df['source'].str.upper()


# Count breaches by state
breach_counts = df['source'].value_counts().reset_index()
breach_counts.columns = ['state', 'breach_count']


# Create the choropleth map
fig = px.choropleth(
    breach_counts,
    locations='state',               
    locationmode='USA-states',       
    color='breach_count',            
    color_continuous_scale='Reds',  
    scope='usa',                     
    title='Heat Map of Data Breaches by State',
    labels={'breach_count': 'Number of Breaches'}
)

# Style the map background and borders
fig.update_geos(
    bgcolor='black',
    lakecolor='lightblue',
    landcolor='lightgrey',
    showcountries=True,
    showcoastlines=True,
    showland=True
)
fig.update_traces(marker_line_color='black', marker_line_width=0.5)

# Show the interactive map
fig.show()
# Save the map as an HTML file
fig.write_html("index.html")

#https://wjarosz0001.github.io/CIT-4105-DE1/Chorolpeth%20Map
