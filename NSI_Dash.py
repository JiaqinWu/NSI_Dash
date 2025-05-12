import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium 
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Set up the Streamlit page 
st.set_page_config(layout="wide") # Use wide layout for better use of space
st.title("Neighrborhood Safety Index Dashboard")

# Load Data
df = pd.read_csv('Census_Tract_Risk_Profile.csv')
with open("geojson_data.geojson") as f:
    prince_william_tracts = json.load(f)

# Load the shapefile
#gdf_shp = gpd.read_file("Demographic_files/tl_2024_51_tract.shp")

# Sidebar for filters
st.sidebar.header("Selection to Filter Data")

### Filter by Safety Tier
all_tiers = df['Safety_Tier'].unique().tolist()
selected_tiers = st.sidebar.multiselect(
    "Select Safety Tier(s)",
    all_tiers,
    default=all_tiers 
)

### Filter by Safety Index range
min_safety_index = df['Safety_Index'].min()
max_safety_index = df['Safety_Index'].max()
safety_index_range = st.sidebar.slider(
    "Select Safety Index Range",
    min_safety_index,
    max_safety_index,
    (min_safety_index, max_safety_index) 
)

# Apply filters
filtered_df = df[df['Safety_Tier'].isin(selected_tiers)]
filtered_df = filtered_df[(filtered_df['Safety_Index'] >= safety_index_range[0]) & (filtered_df['Safety_Index'] <= safety_index_range[1])]


# Create Visualizations
# Distribution of Top Domain
if not filtered_df.empty:
    st.subheader("Distribution of Top Risk Domain")
    fig_top_domain = px.bar(
        filtered_df['Top_Domain'].value_counts().reset_index(name='count'),
        x='Top_Domain', 
        y='count',
        labels={'Top_Domain': 'Top Risk Domain', 'count': 'Number of Tracts'}
    )
    st.plotly_chart(fig_top_domain, use_container_width=True)


# Folium Map
st.subheader("Census Tract Neighborhood Safety Map")

# Ensure tract ID is string type for matching
#df["Tract_ID"] = df["Tract_ID"].astype(str)
#gdf_shp["GEOID"] = gdf_shp["GEOID"].astype(str)

# Merge shapefile with safety index data
#df = df.rename(columns={"Tract_ID": "GEOID"})
#merged_data = df[["GEOID", "Safety_Index"]].merge(gdf_shp, on="GEOID", how="left").rename(columns={"GEOID": "Tract_ID"})

m = folium.Map(location=[38.7, -77.4],
                zoom_start=10,
                tiles='CartoDB DarkMatter', 
                attr='© CartoDB') 

threshold_scale = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

choropleth = folium.Choropleth(
     geo_data=prince_william_tracts, 
     name='Safety Index',
     data=filtered_df,
     columns=['Tract_ID', 'Safety_Index'],
     key_on='feature.properties.GEOID',
     fill_color='RdYlGn',  #YlOrRd
     fill_opacity=0.7,
     line_opacity=0.2,
     threshold_scale=threshold_scale, 
 )

choropleth.add_to(m)

for key in choropleth._children:
    if key.startswith('color_map'):
        del(m._children[key])
choropleth.add_to(m)

thresholds = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

colors = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090',
    '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4']

legend_labels = [
    '0-2', '2-4', '4-6', '6-8', '8-10',
    '10-12', '12-14', '14-16', '16-18', '18+'
]

cmap = plt.get_cmap('RdYlGn')
norm = mcolors.Normalize(vmin=thresholds[0], vmax=thresholds[-1])
# Use the upper boundary of each bin for sampling colors
bin_boundaries = thresholds[1:]
html_legend_colors = [mcolors.rgb2hex(cmap(norm(boundary))) for boundary in bin_boundaries]

legend_html = """
     <div style="position: fixed;
                 bottom: 100px; right: 20px; width: 150px; z-index:9999; font-size:14px;
                 background-color:rgba(30, 30, 30, 0.8);
                 color: white;
                 border:1px solid #888;
                 border-radius: 5px;
                 padding: 10px;">
         <b>Safety Index</b> <br>
         <span style="font-size:12px;">(higher = safer)</span> <br>
         &nbsp;
""" # Added Safety Index title and subtitle here

# Add the color blocks and labels dynamically based on generated colors and labels
for i in range(len(html_legend_colors)):
    legend_html += f"""
    <div style="display: flex; align-items: center; margin-bottom: 4px;">
        <div style="background:{html_legend_colors[i]};
                    width:18px; height:18px;
                    margin-right:8px; opacity:0.9;"></div>
        <span style="flex: 1;">{legend_labels[i]}</span>
    </div>
    """

legend_html += """
     </div>
"""

# Add the custom HTML legend to the map
m.get_root().html.add_child(folium.Element(legend_html))



# Display the map
st_map = st_folium(m, width=1000, height=600) 








