import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium 
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from folium.plugins import MeasureControl
import streamlit.components.v1 as components

# Set up the Streamlit page 
#st.image("static/logo2.png", width=200)
st.set_page_config(layout="wide") # Use wide layout for better use of space
#st.image("static/logo1.png", use_column_width=True)
st.title("Census Tract Neighborhood Safety Index Map")

# Load Data
df = pd.read_csv('Census_Tract_Risk_Profile.csv')
with open("geojson_data.geojson") as f:
    prince_william_tracts = json.load(f)

# Load the shapefile
#gdf_shp = gpd.read_file("Demographic_files/tl_2024_51_tract.shp")

# Sidebar for filters
st.sidebar.header("Selection to Filter Safety Index Range")

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
filtered_df = df[(df['Safety_Index'] >= safety_index_range[0]) & (df['Safety_Index'] <= safety_index_range[1])]
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.write(" ")
st.sidebar.image("static/logo1.png", use_column_width=True)

# Folium Map
#st.subheader("Census Tract Neighborhood Safety Map")

# Ensure tract ID is string type for matching
#df["Tract_ID"] = df["Tract_ID"].astype(str) # This line might be redundant if you rename later
#gdf_shp["GEOID"] = gdf_shp["GEOID"].astype(str) # This is commented out

# Merge shapefile with safety index data
#df = df.rename(columns={"Tract_ID": "GEOID"}) # This is commented out
#merged_data = df[["GEOID", "Safety_Index"]].merge(gdf_shp, on="GEOID", how="left").rename(columns={"GEOID": "Tract_ID"}) # This is commented out

census_tracts = gpd.read_file("Demographic_files/tl_2024_51_tract.shp")
# Create GEOID column in filtered_df if needed
# It seems 'Tract_ID' exists in filtered_df and corresponds to 'GEOID' in census_tracts.
# Let's ensure consistency.
if 'GEOID' not in filtered_df.columns:
    # Assuming Tract_ID from the CSV is the GEOID
    filtered_df["GEOID"] = filtered_df["Tract_ID"].astype(str)

# Ensure GEOID is string type in both datasets
census_tracts["GEOID"] = census_tracts["GEOID"].astype(str)
filtered_df["GEOID"] = filtered_df["GEOID"].astype(str)

# Dictionary for variable name mapping (to make them more readable)
variable_name_map = {
    # Socioeconomic
    "LOWINCPCT": "Low Income Population",
    "UNEMPPCT": "Unemployment Rate",
    "LINGISOPCT": "Limited English Proficiency",
    "LESSHSPCT": "Less than High School Education",
    "E_POV150_P": "Population Below 150% Poverty Level",
    "With_PublicAssIncome_P": "Public Assistance Income",
    "With_SSI_P": "Supplemental Security Income",
    "E_UNINSUR_P": "Uninsured Population",
    "With_Medicaid_P": "Medicaid Coverage",

    # Housing
    "PRE1960PCT": "Housing Built Before 1960",
    "E_HBURD_P": "Housing Cost Burden",
    "House_Vacant_P": "Vacant Housing",
    "E_MUNIT_P": "Multi-Unit Housing",
    "E_MOBILE_P": "Mobile Homes",
    "E_CROWD_P": "Crowded Housing",
    "Owner_occupied_P": "Owner-Occupied Housing",
    "Mean_Proportion_HHIncome": "Housing Cost as % of Income",

    # Transportation
    "PTRAF": "Traffic Volume",
    "E_NOVEH_P": "No Vehicle Access",
    "Mean_Transportation_time(min)": "Average Commute Time",
    "Work_Drivealone_P": "Drive Alone to Work",
    "Work_Carpooled_P": "Carpool to Work",
    "Work_PublicTransportation_P": "Public Transit to Work",
    "Work_Walk_P": "Walk to Work",
    "Work_Fromhome_P": "Work from Home",

    # TransportationSafety
    "Percent_Severe/Fatal": "Severe/Fatal Crashes",
    "Avg_Person_Injured/Kill": "Person Injuries/Fatalities",
    "Avg_Pedestrian_Injured/Kill": "Pedestrian Injuries/Fatalities",
    "Percent_Alcohol_Related": "Alcohol-Related Crashes",
    "Percent_Distracted_Related": "Distracted Driving Crashes",
    "Percent_Drowsy_Related": "Drowsy Driving Crashes",
    "Percent_Drug_Related": "Drug-Related Crashes",
    "Percent_Speed_Related": "Speed-Related Crashes",
    "Percent_Hitrun_Related": "Hit and Run Crashes",
    "Percent_Schoolzone_Related": "School Zone Crashes",
    "Percent_Lgtruck_Related": "Large Truck Crashes",
    "Percent_Young_Related": "Young Driver Crashes",
    "Percent_Senior_Related": "Senior Driver Crashes",
    "Percent_Bike_Related": "Bicycle Crashes",
    "Percent_Night_Related": "Nighttime Crashes",
    "Percent_Workzone_Related": "Work Zone Crashes",

    # Environmental
    "PM25": "Fine Particulate Matter",
    "OZONE": "Ozone Level",
    "DSLPM": "Diesel Particulate Matter",
    "NO2": "Nitrogen Dioxide",
    "RSEI_AIR": "Air Toxics",
    "PTSDF": "Treatment, Storage, Disposal Facilities",
    "UST": "Underground Storage Tanks",
    "PWDIS": "Water Discharge Sites",
    "PNPL": "National Priority List Sites",
    "PRMP": "Risk Management Plan Facilities",

    # PublicHealth
    "LIFEEXPPCT": "Life Expectancy",
    "EMS_Calls": "EMS Calls",
    "Structure_Fires": "Structure Fires",
    "Medical_Calls": "Medical Emergency Calls",
    "Violence_Calls": "Violence-Related Calls",
    "Opioid_Calls": "Opioid-Related Calls",
    "Calls_Per_HVU_Caller": "Calls per High-Volume User",
    "High_Volume_Utilizer_Percent": "High-Volume 911 Users",
    "Stroke_Calls": "Stroke Emergencies",
    "Cardiac_Calls": "Cardiac Emergencies",
    "Diabetic_Calls": "Diabetic Emergencies",
    "CPR_Calls": "CPR Incidents",
    "Respiratory_Calls": "Respiratory Emergencies",
    "High_Blood_Pressure_Calls": "Blood Pressure Emergencies",
    "Attempted_Suicide": "Suicide Attempts",
    "Domestic": "Domestic Violence",
    "Homeless": "Homelessness Calls",
    "Shootings": "Shooting Incidents",
    "Stabbings": "Stabbing Incidents",
    "Assaults": "Assault Incidents"
}


# Function to get a readable variable name
def get_readable_name(var_name):
    return variable_name_map.get(var_name, var_name.replace('_', ' '))

# Filter census tracts to just Prince William County if needed (COUNTYFP = 153 for Prince William)
if 'COUNTYFP' in census_tracts.columns:
    # Check if there are any PWC tracts in the data
    pwc_tracts = census_tracts[census_tracts['COUNTYFP'] == '153']
    if len(pwc_tracts) > 0:
        print(f"Filtering census tracts to {len(pwc_tracts)} Prince William County tracts")
        census_tracts = pwc_tracts
    else:
        print("Warning: No Prince William County tracts found in the shapefile with COUNTYFP '153'. Check shapefile data.")


# Merge data
print("Merging data with boundaries...")
merged_data = filtered_df.merge(
    census_tracts,
    on="GEOID",
    how="left"
)

# Convert to GeoDataFrame
# Check if geometry column exists before converting
if 'geometry' in merged_data.columns:
    merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry')

    # Check for missing merges
    missing = merged_data.loc[merged_data.geometry.isna()].shape[0]
    print(f"\nUnmatched tracts (missing geometry): {missing}")

    # If there are missing geometries, they can't be mapped
    if missing > 0:
        print("Warning: Some census tracts couldn't be matched to shapefile geometries and will not be mapped.")
        merged_data = merged_data.dropna(subset=['geometry'])

    # Create a dictionary to prepare our tract data for JavaScript
    # This part will only run if merged_data is not empty after dropping NaNs
    if not merged_data.empty:
        tract_data = {}
        for idx, row in merged_data.iterrows():
            # Use GEOID from the merged_data which should align with the shapefile
            tract_id = row['GEOID']

            # Domain rankings
            domain_ranks = {}
            domains = ['Socioeconomic', 'Housing', 'Transportation', 'TransportationSafety', 'Environmental', 'PublicHealth']
            for domain in domains:
                rank_col = f"{domain}_Rank"
                if rank_col in row and pd.notna(row[rank_col]):
                    try:
                        domain_ranks[domain] = int(row[rank_col])
                    except ValueError:
                        # Handle cases where rank might not be a valid integer
                        domain_ranks[domain] = None
                        print(f"Warning: Could not convert rank for tract {tract_id}, domain {domain} to integer: {row[rank_col]}")


            # Top variables by domain
            domain_variables = {}
            for domain in domains:
                domain_vars = []
                for i in range(1, 4):
                    var_col = f"{domain}_Var{i}"
                    if var_col in row and pd.notna(row[var_col]) and row[var_col]:
                        domain_vars.append(get_readable_name(row[var_col]))
                if domain_vars:
                    domain_variables[domain] = domain_vars

            # Add to tract data dictionary
            tract_data[tract_id] = {
                'safety_index': float(row['Safety_Index']) if pd.notna(row['Safety_Index']) else None,
                'safety_tier': row['Safety_Tier'] if 'Safety_Tier' in row and pd.notna(row['Safety_Tier']) else 'N/A',
                'top_domain': row['Top_Domain'] if 'Top_Domain' in row and pd.notna(row['Top_Domain']) else 'N/A',
                'domain_ranks': domain_ranks,
                'domain_variables': domain_variables
            }

        # Add safety_index to the GeoJSON properties
        merged_data['safety_index'] = merged_data['Safety_Index']

        # Create map file with modern design

        # Prepare GeoJSON
        geo_data = merged_data.to_json()
        tract_data_json = json.dumps(tract_data).replace("'", "\\'")

        # HTML file name
        output_file = "Modern_Safety_Index_Map.html"

        # Calculate bounds and center coordinates before writing the file
        bounds = merged_data.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        with open(output_file, "w") as f:
            f.write("""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Neighborhood Safety Index Map</title>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
                <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
                <style>
                    /* ... (your CSS styles) ... */
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        font-family: 'Roboto', sans-serif;
                    }

                    body {
                        display: flex;
                        height: 100vh;
                        overflow: hidden;
                        background-color: #1f2937;
                        color: #f3f4f6;
                    }

                    #map {
                        flex: 3;
                        height: 100%;
                        z-index: 1;
                    }

                    #panel {
                        flex: 1;
                        min-width: 320px;
                        max-width: 400px;
                        padding: 20px;
                        background-color: #1f2937;
                        box-shadow: -3px 0 10px rgba(0,0,0,0.2);
                        overflow-y: auto;
                        display: flex;
                        flex-direction: column;
                        z-index: 2;
                        border-left: 1px solid #374151;
                    }

                    #panel.hidden {
                        display: none;
                    }

                    h1 {
                        margin-top: 0;
                        margin-bottom: 15px;
                        font-size: 22px;
                        font-weight: 500;
                        text-align: center;
                        color: #f3f4f6;
                    }

                    h2 {
                        margin-top: 0;
                        font-size: 18px;
                        font-weight: 500;
                        color: #f3f4f6;
                    }

                    h3 {
                        margin-top: 20px;
                        margin-bottom: 10px;
                        font-size: 16px;
                        font-weight: 500;
                        color: #f3f4f6;
                    }

                    hr {
                        border: 0;
                        height: 1px;
                        background: #374151;
                        margin: 15px 0;
                    }

                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 15px;
                        background-color: #283548;
                        border-radius: 8px;
                        overflow: hidden;
                    }

                    td {
                        padding: 10px;
                        border-bottom: 1px solid #374151;
                    }

                    tr:last-child td {
                        border-bottom: none;
                    }

                    ul {
                        margin-top: 8px;
                        margin-bottom: 15px;
                        padding-left: 25px;
                    }

                    li {
                        margin-bottom: 6px;
                        color: #e5e7eb;
                    }

                    .info {
                        padding: 8px 10px;
                        font: 14px/16px 'Roboto', sans-serif;
                        background: #283548;
                        color: #f3f4f6;
                        box-shadow: 0 0 15px rgba(0,0,0,0.2);
                        border-radius: 8px;
                        border: 1px solid #374151;
                    }

                    .info h4 {
                        margin: 0 0 8px;
                        color: #9ca3af;
                        font-weight: 500;
                    }

                    .legend {
                        line-height: 20px;
                        color: #e5e7eb;
                    }

                    .legend i {
                        width: 18px;
                        height: 18px;
                        float: left;
                        margin-right: 8px;
                        opacity: 0.85;
                    }

                    .place-label {
                        background-color: transparent;
                        border: none;
                        white-space: nowrap;
                    }

                    .subtitle {
                        text-align: center;
                        font-size: 14px;
                        margin-bottom: 20px;
                        color: #9ca3af;
                        font-weight: 300;
                    }

                    .panel-header {
                        text-align: center;
                        margin-bottom: 25px;
                    }

                    .panel-content {
                        flex: 1;
                    }

                    .info-box {
                        background-color: #283548;
                        border: 1px solid #374151;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }

                    .info-box p {
                        margin-bottom: 8px;
                        color: #e5e7eb;
                    }

                    .info-box p:last-child {
                        margin-bottom: 0;
                    }

                    .info-box strong {
                        color: #f3f4f6;
                        font-weight: 500;
                    }

                    .intro-text {
                        font-size: 14px;
                        line-height: 1.6;
                        color: #9ca3af;
                        margin-bottom: 25px;
                        font-weight: 300;
                    }

                    .domain-section {
                        background-color: #283548;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 12px;
                    }

                    .domain-section strong {
                        color: #f3f4f6;
                        font-weight: 500;
                    }


                    .welcome-message {
                        padding: 30px;
                        text-align: center;
                        font-size: 16px;
                        color: #9ca3af;
                        height: 100%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 300;
                    }

                    .close-button {
                        position: absolute;
                        top: 15px;
                        right: 15px;
                        border: none;
                        background: none;
                        font-size: 20px;
                        font-weight: 300;
                        color: #9ca3af;
                        cursor: pointer;
                        transition: color 0.2s;
                    }

                    .close-button:hover {
                        color: #f3f4f6;
                    }

                    .domain-pill {
                        display: inline-block;
                        background-color: #374151;
                        color: #f3f4f6;
                        padding: 3px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 500;
                        margin-right: 5px;
                        margin-bottom: 5px;
                    }

                    .safety-value {
                        display: flex;
                        align-items: center;
                        margin: 15px 0;
                    }

                    .safety-value-number {
                        font-size: 24px;
                        font-weight: 700;
                        margin-right: 10px;
                        color: #f3f4f6;
                    }

                    .safety-value-label {
                        font-size: 14px;
                        color: #9ca3af;
                    }

                    .safety-tier {
                        display: inline-block;
                        padding: 3px 10px;
                        border-radius: 12px;
                        font-size: 14px;
                        font-weight: 500;
                        margin-top: 5px;
                        margin-bottom: 10px;
                    }

                    .tier-high {
                        background-color: rgba(220, 38, 38, 0.2);
                        color: #ef4444;
                    }

                    .tier-moderate {
                        background-color: rgba(245, 158, 11, 0.2);
                        color: #f59e0b;
                    }

                    .tier-low {
                        background-color: rgba(16, 185, 129, 0.2);
                        color: #10b981;
                    }

                    .tier-very-low {
                        background-color: rgba(5, 150, 105, 0.2);
                        color: #059669;
                    }

                    .rank-number {
                        display: inline-block;
                        width: 24px;
                        height: 24px;
                        border-radius: 50%;
                        background-color: #374151;
                        color: #f3f4f6;
                        text-align: center;
                        line-height: 24px;
                        margin-right: 8px;
                        font-weight: 500;
                    }

                    /* Style the leaflet components for dark theme */
                    .leaflet-container {{
                        background-color: #111827;
                    }}

                    .leaflet-control-zoom a {{
                        background-color: #283548;
                        color: #f3f4f6;
                        border-color: #374151;
                    }}

                    .leaflet-control-zoom a:hover {{
                        background-color: #374151;
                    }}

                    .leaflet-control-attribution {{
                        background-color: rgba(40, 53, 72, 0.8) !important;
                        color: #9ca3af !important;
                    }}

                    .leaflet-control-attribution a {{
                        color: #60a5fa !important;
                    }}
                </style>
            </head>
            <body>
                <div id="map"></div>
                <div id="panel" class="hidden">
                    <button class="close-button" onclick="document.getElementById('panel').classList.add('hidden')">X</button>
                    <div class="panel-header">
                        <h1>Neighborhood Safety Index</h1>
                        <div class="subtitle">Census Tract Details</div>
                    </div>
                    <div class="panel-content" id="panel-content">
                        <div class="welcome-message">
                            Click on a census tract to view detailed risk information
                        </div>
                    </div>
                </div>

                <script>""")

            # Write JavaScript center coordinates
            f.write(f"""
                // Initialize map with dark theme
                var map = L.map('map', {{
                    center: [{center_lat}, {center_lon}],
                    zoom: 10,
                    zoomControl: false  // We'll add it manually in a better position
                }});

                // Add dark-themed tile layer
                L.tileLayer('https://cartodb-basemaps-{{s}}.global.ssl.fastly.net/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    subdomains: 'abcd',
                    maxZoom: 19
                }}).addTo(map);

                // Add zoom control in the top right
                L.control.zoom({{
                    position: 'topright'
                }}).addTo(map);

                // Define color function - same colors as before
                function getColor(d) {{
                    return d > 18 ? '#006837' :
                           d > 16 ? '#1a9850' :
                           d > 14 ? '#66bd63' :
                           d > 12 ? '#a6d96a' :
                           d > 10 ? '#d9ef8b' :
                           d > 8  ? '#fee08b' :
                           d > 6  ? '#fdae61' :
                           d > 4  ? '#f46d43' :
                           d > 2  ? '#d73027' :
                                    '#a50026';
                }}

                // Style function with cleaner edges
                function style(feature) {{
                    return {{
                        fillColor: getColor(feature.properties.safety_index),
                        weight: 1.5,
                        opacity: 1,
                        color: '#1f2937',  // Dark border that blends with background
                        fillOpacity: 0.85
                    }};
                }}

                // Highlight function with more prominent highlighting
                function highlightFeature(e) {{
                    var layer = e.target;

                    layer.setStyle({{
                        weight: 3,
                        color: '#f3f4f6',  // Light border for contrast
                        dashArray: '',
                        fillOpacity: 0.9
                    }});

                    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {{
                        layer.bringToFront();
                    }}

                    info.update(layer.feature.properties);
                }}

                // Reset highlight
                function resetHighlight(e) {{
                    geojson.resetStyle(e.target);
                    info.update();
                }}

                // Get appropriate class for safety tier
                function getTierClass(tier) {{
                    if (tier.includes('High')) return 'tier-high';
                    if (tier.includes('Moderate')) return 'tier-moderate';
                    if (tier.includes('Low') && !tier.includes('Very')) return 'tier-low';
                    if (tier.includes('Very Low')) return 'tier-very-low';
                    return '';
                }}

                // Click handler to populate side panel with modern styling
                function clickFeature(e) {{
                    var properties = e.target.feature.properties;
                    // Ensure we use the GEOID from properties as the lookup key
                    var tractId = properties.GEOID; // Use GEOID from properties
                    var tractData = tractDataLookup[tractId];

                    // Show the panel
                    document.getElementById('panel').classList.remove('hidden');

                    // Update panel content
                    var panelContent = document.getElementById('panel-content');

                    // Build HTML content with modern styling
                    var html = `
                        <div class="info-box">
                            <h2>Census Tract: ${{tractId}}</h2>

                            <div class="safety-value">
                                <div class="safety-value-number">${{tractData && tractData.safety_index !== undefined && tractData.safety_index !== null ? tractData.safety_index.toFixed(1) : 'N/A'}}</div>
                                <div class="safety-value-label">Safety Index<br/>(1-20 scale, higher = safer)</div>
                            </div>

                            <div class="safety-tier ${{tractData ? getTierClass(tractData.safety_tier) : ''}}">${{tractData ? tractData.safety_tier : 'N/A'}}</div>

                            <p><strong>Highest Risk Domain:</strong> ${{tractData ? tractData.top_domain : 'N/A'}}</p>
                        </div>

                        <h3>Domain Risk Ranking</h3>
                        <table>`;

                    // Add domain rankings in two columns
                    var domains = tractData ? Object.keys(tractData.domain_ranks) : [];
                    for (var i = 0; i < domains.length; i += 2) {{
                        html += '<tr>';

                        // First column
                        var domain1 = domains[i];
                        html += `<td><span class="rank-number">${{tractData.domain_ranks[domain1] !== null ? tractData.domain_ranks[domain1] : 'N/A'}}</span> ${{domain1}}</td>`;

                        // Second column (if exists)
                        if (i + 1 < domains.length) {{
                            var domain2 = domains[i+1];
                            html += `<td><span class="rank-number">${{tractData.domain_ranks[domain2] !== null ? tractData.domain_ranks[domain2] : 'N/A'}}</span> ${{domain2}}</td>`;
                        }} else {{
                            html += '<td></td>';
                        }}

                        html += '</tr>';
                    }}

                    html += `</table>
                            <h3>Top Contributing Variables</h3>`;

                    // Add variables by domain
                    var domainVars = tractData ? Object.keys(tractData.domain_variables) : [];
                    for (var j = 0; j < domainVars.length; j++) {{
                        var domain = domainVars[j];
                        var variables = tractData.domain_variables[domain];

                        html += `
                            <div class="domain-section">
                                <strong>${{domain}}:</strong>
                                <ul>`;

                        for (var k = 0; k < variables.length; k++) {{
                            html += `<li>${{variables[k]}}</li>`;
                        }}

                        html += `</ul>
                            </div>`;
                    }}

                    // If no data found for the tract
                    if (!tractData) {{
                         html = `<div class="welcome-message">No detailed data available for this tract.</div>`;
                    }}


                    panelContent.innerHTML = html;

                    // Zoom to feature only if geometry exists
                    if (e.target.getBounds) {{
                         map.fitBounds(e.target.getBounds());
                    }} else {{
                         console.warn("Clicked feature has no valid bounds for zooming.");
                    }}

                }}

                // Set up the interaction
                function onEachFeature(feature, layer) {{
                    layer.on({{
                        mouseover: highlightFeature,
                        mouseout: resetHighlight,
                        click: clickFeature
                    }});
                }}

                // Create tract data lookup - Ensure this is available globally in the script
                var tractDataLookup = {tract_data_json};


                // Load GeoJSON data
                // Check if geoData exists and has features before adding layer
                var geoData = {geo_data};
                if (geoData && geoData.features && geoData.features.length > 0) {{
                     // Add GeoJSON layer
                    var geojson = L.geoJSON(geoData, {{
                        style: style,
                        onEachFeature: onEachFeature
                    }}).addTo(map);
                }} else {{
                    console.warn("No GeoJSON data or features available to load the map layer.");
                    // Display a message on the map or console if no data is loaded
                }}


                // Add modern info control
                var info = L.control({{position: 'topright'}});

                info.onAdd = function (map) {{
                    this._div = L.DomUtil.create('div', 'info');
                    this.update();
                    return this._div;
                }};

                info.update = function (props) {{
                    this._div.innerHTML = '<h4>Neighborhood Safety Index</h4>' +  (props ?
                        '<b>Census Tract: ' + (props.GEOID ? props.GEOID : 'N/A') + '</b><br />' + // Use GEOID from properties
                        'Safety Index: ' + (props.safety_index !== undefined && props.safety_index !== null ? props.safety_index.toFixed(1) : 'N/A') + '/20'
                        : 'Hover over a census tract');
                }};


                info.addTo(map);

                // Add modern legend
                var legend = L.control({{position: 'bottomright'}});

                legend.onAdd = function (map) {{
                    var div = L.DomUtil.create('div', 'info legend'),
                        grades = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
                        labels = [],
                        from, to;

                    div.innerHTML = '<h4>Safety Index</h4><div style="text-align:center;margin-bottom:8px;font-size:12px;">(higher = safer)</div>';

                    for (var i = 0; i < grades.length; i++) {{
                        from = grades[i];
                        to = grades[i + 1];

                        labels.push(
                            '<i style="background:' + getColor(from + 1) + '"></i> ' +
                            from + (to ? '&ndash;' + to : '+'));
                    }}

                    div.innerHTML += labels.join('<br>');
                    return div;
                }};

                legend.addTo(map);

                // Add place labels with modern styling
                var placeLabels = [
                    {{name: "Woodbridge", location: [38.698, -77.295]}},
                    {{name: "Dale City", location: [38.637, -77.313]}},
                    {{name: "Lake Ridge", location: [38.683, -77.301]}},
                    {{name: "Manassas", location: [38.751, -77.475]}},
                    {{name: "Dumfries", location: [38.567, -77.329]}},
                    {{name: "Gainesville", location: [38.796, -77.614]}},
                    {{name: "Occoquan", location: [38.684, -77.160]}},
                    {{name: "Haymarket", location: [38.812, -77.636]}}
                ];

                // Add the place labels to the map with modern styling
                placeLabels.forEach(function(place) {{
                    // Create a modern styled label with shadow effects and better visibility
                    var icon = L.divIcon({{
                        className: 'place-label',
                        html: '<div style="font-family: Roboto, Arial, sans-serif; font-size: 14px; font-weight: 600; color: #f3f4f6; text-shadow: 0px 0px 3px rgba(0,0,0,0.7); background-color: rgba(40, 53, 72, 0.85); border-radius: 4px; padding: 4px 8px; border: 1px solid #4b5563; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">' + place.name + '</div>',
                        iconSize: [100, 30],
                        iconAnchor: [50, 15]
                    }});

                    // Add marker with the custom icon
                    L.marker(place.location, {{
                        icon: icon,
                        interactive: false, // Don't capture clicks on the label
                        keyboard: false
                    }}).addTo(map);
                }});
            </script>
            </body>
            </html>""")

        # Display the map
        # Ensure the HTML file exists before trying to display it
        import os
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                html_content = f.read()
            components.html(html_content, width=1000, height=600)
        else:
            st.error(f"Map HTML file not created: {output_file}")

    else:
        st.warning("No data available to generate the map after applying filters and merging.")

else:
    st.error("Geometry column not found in merged data. Cannot create GeoDataFrame for mapping. Check the shapefile loading and merging steps.")








