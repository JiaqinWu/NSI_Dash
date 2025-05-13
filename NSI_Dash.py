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
import os

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

# Folium Map
st.subheader("Census Tract Neighborhood Safety Map")

st.info("Starting geographic visualization process...")

# Ensure variable_name_map is defined BEFORE this section
# Dictionary for variable name mapping (to make them more readable)
# If you haven't defined this earlier in your script, add it here:
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
    "Assaults": "Assault Incidents",

    # Demographics
    "PEOPCOLORPCT": "Percentage of People with Color",
    "LOWINCPCT": "Percentage of People with Low Income",
    "UNEMPPCT": "Percentage of Unemployed People",
    "DISABILITYPCT": "Percentage of People with Disability",
    "UNDER5PCT": "Percentage of People Under 5",
    "OVER64PCT": "Percentage of People Over 64"
}

# Make sure format_percentage is defined BEFORE this section
# Function to format percentages
def format_percentage(val):
    if pd.isna(val):
        return "N/A"
    try:
        numeric_val = float(val)
        # Check if the value is extremely small (close to zero but not NaN)
        # Sometimes float conversion results in very small numbers instead of 0
        if abs(numeric_val) < 1e-9: # Use a small tolerance
             return "0.00%"
        return f"{round(numeric_val * 100, 2)}%"
    except (ValueError, TypeError):
        return "N/A" # Handle cases where conversion to float fails

# Make sure get_readable_name is defined BEFORE this section
# Function to get a readable variable name
def get_readable_name(var_name):
    return variable_name_map.get(var_name, var_name.replace('_', ' '))


# Load the shapefile
try:
    st.info("Loading shapefile: Demographic_files/tl_2024_51_tract.shp")
    census_tracts = gpd.read_file("Demographic_files/tl_2024_51_tract.shp")
    st.info(f"Shapefile loaded successfully. Number of tracts: {len(census_tracts)}")
except Exception as e:
    st.error(f"Error loading shapefile: {e}")
    st.stop() # Stop execution if shapefile can't be loaded


# Ensure Tract_ID and GEOID are string type for matching
st.info(f"Number of rows in filtered_df before GEOID check: {len(filtered_df)}")
if 'Tract_ID' in filtered_df.columns:
     filtered_df["GEOID"] = filtered_df["Tract_ID"].astype(str)
     st.info("Ensured 'GEOID' column exists and is string type in filtered data.")
else:
     st.error("Column 'Tract_ID' not found in the filtered data. Cannot proceed with merging.")
     st.stop() # Stop execution if Tract_ID is missing


if 'GEOID' in census_tracts.columns:
    census_tracts["GEOID"] = census_tracts["GEOID"].astype(str)
    st.info("Ensured 'GEOID' column is string type in census tracts.")
else:
     st.error("Column 'GEOID' not found in census tracts shapefile. Cannot proceed with merging.")
     st.stop() # Stop execution if GEOID is missing in shapefile


# Filter census tracts to just Prince William County if needed (COUNTYFP = 153 for Prince William)
if 'COUNTYFP' in census_tracts.columns:
    # Check if there are any PWC tracts in the data
    pwc_tracts = census_tracts[census_tracts['COUNTYFP'] == '153']
    if len(pwc_tracts) > 0:
        st.info(f"Filtering census tracts to {len(pwc_tracts)} Prince William County tracts (COUNTYFP = '153').")
        census_tracts = pwc_tracts
    else:
        st.warning("No Prince William County tracts found in the shapefile with COUNTYFP '153'. Check shapefile data.")
else:
    st.warning("COUNTYFP column not found in shapefile. Skipping Prince William County filter.")


# Merge data
st.info(f"Attempting to merge filtered data ({len(filtered_df)} rows) with census tracts ({len(census_tracts)} rows) on 'GEOID'...")
merged_data = filtered_df.merge(
    census_tracts,
    on="GEOID",
    how="left"
)
st.info(f"Merge completed. Rows in merged_data: {len(merged_data)}")


# Convert to GeoDataFrame
# Check if geometry column exists before converting
if 'geometry' in merged_data.columns:
    st.info("Geometry column found. Converting merged data to GeoDataFrame.")
    merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry')

    # Check for missing merges (rows from filtered_df that didn't find a matching geometry)
    missing_geometries_count = merged_data.geometry.isna().sum() # Use sum() to count True values
    st.info(f"Checking for missing geometries after merge. Unmatched tracts: {missing_geometries_count}")


    # If there are missing geometries, they can't be mapped
    if missing_geometries_count > 0:
        st.warning(f"{missing_geometries_count} census tracts couldn't be matched to shapefile geometries and will be dropped for mapping.")
        # Keep only rows with valid geometry
        merged_data = merged_data.dropna(subset=['geometry']).reset_index(drop=True) # Reset index after dropping
        st.info(f"Rows remaining with valid geometry after dropping missing ones: {len(merged_data)}")

    # Check if there's data left to map after dropping missing geometries
    if not merged_data.empty:
        st.info(f"Merged data contains {len(merged_data)} rows with valid geometry. Proceeding to create map HTML.")

        # Create a dictionary to prepare our tract data for JavaScript
        tract_data = {}
        # Iterate over rows *with valid geometry*
        for idx, row in merged_data.iterrows():
            # Use GEOID from the merged_data which should align with the shapefile
            tract_id = row['GEOID'] # Use GEOID which is common after merge

            # --- Demographic Data ---
            demographic_vars = [
                "PEOPCOLORPCT", "LOWINCPCT", "UNEMPPCT",
                "DISABILITYPCT", "UNDER5PCT", "OVER64PCT"
            ]
            demographics = {}
            for var in demographic_vars:
                 # Check if column exists and value is notna before adding
                # Use row.get(var) with a default to avoid KeyError if column is entirely missing
                val = row.get(var)
                if pd.notna(val):
                    demographics[get_readable_name(var)] = format_percentage(val)
                # Optional: Add placeholder if column is expected but value is missing for a specific tract
                # elif var in demographic_vars: # If you expect all 6 demographic columns in the data
                #     demographics[get_readable_name(var)] = "N/A"


            # --- Domain rankings ---
            domain_ranks = {}
            domains = ['Socioeconomic', 'Housing', 'Transportation', 'TransportationSafety', 'Environmental', 'PublicHealth']
            for domain in domains:
                rank_col = f"{domain}_Rank"
                # Check if rank column exists and value is notna before processing
                rank_value = row.get(rank_col)
                if pd.notna(rank_value):
                    try:
                        # Attempt conversion, handle potential errors
                        domain_ranks[domain] = int(rank_value)
                    except (ValueError, TypeError) as e:
                        domain_ranks[domain] = None # Handle conversion errors
                        print(f"Warning: Could not convert rank for tract {tract_id}, domain {domain} to integer: {rank_value} - Error: {e}")
                # Optional: add a placeholder if the rank column is expected but missing
                # elif rank_col in row.index: # If you expect all of them to be there
                #      domain_ranks[domain] = "N/A"


            # --- Top variables by domain ---
            domain_variables = {}
            domains_for_vars = ['Socioeconomic', 'Housing', 'Transportation', 'TransportationSafety', 'Environmental', 'PublicHealth'] # Assuming these domains have top variables
            for domain in domains_for_vars:
                domain_vars_list = []
                for i in range(1, 4):
                    var_col = f"{domain}_Var{i}"
                    # Check if variable column exists and value is notna/not empty string
                    var_value = row.get(var_col)
                    if pd.notna(var_value) and str(var_value).strip() != '':
                        domain_vars_list.append(get_readable_name(var_value))
                if domain_vars_list:
                    domain_variables[domain] = domain_vars_list


            # Add all collected data dictionaries/values to the tract_data entry
            tract_data[tract_id] = {
                'safety_index': float(row['Safety_Index']) if 'Safety_Index' in row.index and pd.notna(row['Safety_Index']) else None,
                'safety_tier': row['Safety_Tier'] if 'Safety_Tier' in row.index and pd.notna(row['Safety_Tier']) else 'N/A',
                'top_domain': row['Top_Domain'] if 'Top_Domain' in row.index and pd.notna(row['Top_Domain']) else 'N/A',
                'domain_ranks': domain_ranks,
                'demographics': demographics, # <-- This includes the collected demographics
                'domain_variables': domain_variables
            }

        # Add safety_index to the GeoJSON properties
        # This adds 'safety_index' directly to the properties dictionary in the GeoJSON output
        if 'Safety_Index' in merged_data.columns:
             merged_data['safety_index'] = merged_data['Safety_Index']
             st.info("Added 'safety_index' property to GeoJSON data.")
        else:
             st.warning("Safety_Index column not found in merged data for adding to GeoJSON properties.")


        # Create map file with modern design
        print("Creating modern safety index map HTML content...")

        # Prepare GeoJSON
        # Check if merged_data still has geometry after processing
        if 'geometry' in merged_data.columns and not merged_data.empty and not merged_data.geometry.is_empty.all() and not merged_data.geometry.isna().all():
             try:
                 geo_data = merged_data.to_json()
                 st.info("GeoJSON data generated successfully from merged_data.")

                 # Add a check for features in the generated GeoJSON string
                 import json
                 try:
                     geo_data_dict = json.loads(geo_data)
                     if not geo_data_dict or 'features' not in geo_data_dict or len(geo_data_dict['features']) == 0:
                          st.warning("GeoJSON data is empty or contains no features after merging. Cannot display map features.")
                          st.info(f"GeoJSON data snippet: {geo_data[:500]}...") # Show a snippet
                     else:
                         st.info(f"GeoJSON data prepared with {len(geo_data_dict['features'])} features.")
                         # Show snippet of one feature's properties for debugging
                         if len(geo_data_dict['features']) > 0 and 'properties' in geo_data_dict['features'][0]:
                             st.info(f"Example feature properties: {geo_data_dict['features'][0]['properties']}")

                 except json.JSONDecodeError:
                     st.error("Failed to parse generated GeoJSON data string into a dictionary. Check data processing steps.")
                     st.info(f"Problematic GeoJSON snippet: {geo_data[:500]}...")
                     geo_data = '{"type": "FeatureCollection", "features": []}' # Provide empty valid GeoJSON
             except Exception as e:
                  st.error(f"Error during GeoJSON generation: {e}")
                  geo_data = '{"type": "FeatureCollection", "features": []}' # Provide empty valid GeoJSON
        else:
            st.warning("Merged data is empty or missing/invalid geometry column before GeoJSON generation. Generating empty GeoJSON.")
            geo_data = '{"type": "FeatureCollection", "features": []}' # Provide empty valid GeoJSON


        # Escape single quotes in tract_data_json for JavaScript
        # Use json.dumps directly as it handles escaping needed for JavaScript string literal
        tract_data_json = json.dumps(tract_data)


        # HTML file name
        output_file = "Modern_Safety_Index_Map.html"

        # Calculate bounds and center coordinates before writing the file
        # Ensure merged_data is not empty and has valid geometry before calculating bounds
        center_lat = 38.668 # Default center for PWC
        center_lon = -77.3 # Default center for PWC
        if not merged_data.empty and 'geometry' in merged_data.columns:
            try:
                # Check if there are any non-empty, non-null geometries before calculating bounds
                if not merged_data.geometry.is_empty.all() and not merged_data.geometry.isna().all():
                     bounds = merged_data.total_bounds
                     center_lat = (bounds[1] + bounds[3]) / 2
                     center_lon = (bounds[0] + bounds[2]) / 2
                     st.info(f"Calculated map center: Lat {center_lat:.4f}, Lon {center_lon:.4f}")
                else:
                    st.warning("Merged data geometry column is empty or all null after cleaning. Using default map center.")

            except Exception as e:
                 st.error(f"Error calculating map bounds: {e}. Using default map center.")
        else:
             st.warning("Merged data is empty before calculating bounds. Using default map center.")


       # HTML file name
        output_file = "Modern_Safety_Index_Map.html"

        # Write HTML file with modern design
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                # Write the static HTML head and body structure
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

                # Write the dynamic JavaScript variables
                # Use json.dumps directly as it handles escaping needed for JavaScript string literal
                f.write(f"\nvar tractDataLookup = {json.dumps(tract_data)};\n")
                # Corrected from .to_dict('geojson') to .to_json()
                f.write(f"\nvar geoData = {geo_data};\n") # Directly embed GeoJSON string


                # Write the static JavaScript functions and remaining HTML
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
                        <h3>Demographic Overview</h3>
                        <table>
                    `;

                    // Check if demographics exist and are not empty
                    var demographics = tractData ? tractData.demographics : null;
                    if (demographics && Object.keys(demographics).length > 0) {{
                        for (var key in demographics) {{
                             // Added check for demographics[key] value
                            if (demographics[key] !== undefined && demographics[key] !== null) {{
                                 html += `<tr><td><strong>${{{{key}}}}</strong></td><td>${{{{demographics[key]}}}}</td></tr>`;
                            }} else {{
                                 html += `<tr><td><strong>${{{{key}}}}</strong></td><td>N/A</td></tr>`;
                            }}
                        }}
                    }} else {{
                         html += `<tr><td>No demographic data available.</td></tr>`;
                    }}
                    html += `</table>`;

                    html += `
                        <h3>Domain Risk Ranking</h3>
                        <table>
                    `;

                    // Add domain rankings in two columns
                    var domains = tractData ? Object.keys(tractData.domain_ranks) : [];
                    if (domains.length > 0) {{
                        for (var i = 0; i < domains.length; i += 2) {{
                            html += '<tr>';

                            // First column
                            var domain1 = domains[i];
                            var rank1 = tractData && tractData.domain_ranks && tractData.domain_ranks[domain1] !== null ? tractData.domain_ranks[domain1] : 'N/A';
                            html += `<td><span class="rank-number">${{rank1}}</span> ${{domain1}}</td>`;

                            // Second column (if exists)
                            if (i + 1 < domains.length) {{
                                var domain2 = domains[i+1];
                                var rank2 = tractData && tractData.domain_ranks && tractData.domain_ranks[domain2] !== null ? tractData.domain_ranks[domain2] : 'N/A';
                                html += `<td><span class="rank-number">${{rank2}}</span> ${{domain2}}</td>`;
                            }} else {{
                                html += '<td></td>';
                            }}
                            html += '</tr>';
                        }}
                     }} else {{
                         html += `<tr><td>No domain ranking data available.</td></tr>`;
                     }}

                    html += `</table>`;

                        html += `
                            <h3>Top Contributing Variables</h3>`;

                    // Add variables by domain
                    var domainVars = tractData ? Object.keys(tractData.domain_variables) : [];
                    if (domainVars.length > 0) {{
                        for (var j = 0; j < domainVars.length; j++) {{
                            var domain = domainVars[j];
                            var variables = tractData.domain_variables[domain];

                             // Check if there are variables listed for this domain and if the list is not empty
                            if (variables && Array.isArray(variables) && variables.length > 0) {{
                                html += `
                                    <div class="domain-section">
                                        <strong>${{domain}}:</strong>
                                        <ul>`;

                                for (var k = 0; k < variables.length; k++) {{
                                     // Check if the variable name is not empty or null
                                    if (variables[k]) {{
                                         html += `<li>${{variables[k]}}</li>`;
                                    }}
                                }}
                                html += `</ul>
                                    </div>`;
                            }} else {{
                                // Message if a domain section exists but has no variables listed
                                html += `<div class="domain-section"><strong>${{domain}}:</strong> <p>No top variables listed.</p></div>`;
                            }}
                        }}
                    }} else {{
                        html += `<p>No contributing variables data available.</p>`;
                    }}

                    // If no data found for the tract at all
                    if (!tractData) {{
                         html = `<div class="welcome-message">No detailed data available for this tract.</div>`;
                    }}


                    panelContent.innerHTML = html;

                    // Zoom to feature only if geometry exists for the clicked feature
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
                var geoData = {geo_data}; // geoData is already a string from Python's .to_json()

                // Check if geoData string represents a valid GeoJSON with features
                try {{
                     var parsedGeoData = JSON.parse(geoData);
                     if (parsedGeoData && parsedGeoData.features && parsedGeoData.features.length > 0) {{
                          console.log("GeoJSON data parsed and contains features.");
                          // Add GeoJSON layer
                          var geojson = L.geoJSON(parsedGeoData, {{
                              style: style,
                              onEachFeature: onEachFeature
                          }}).addTo(map);
                     }} else {{
                         console.warn("GeoJSON data is empty or contains no features to load the map layer.");
                         // Display a message on the map or console if no data is loaded
                     }}
                }} catch (e) {{
                    console.error("Error parsing GeoJSON data string:", e);
                    console.warn("Invalid GeoJSON data. Cannot load map layer.");
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
                    {{name: "Woodbridge", location: [38.668, -77.295]}},
                    {{name: "Dale City", location: [38.637, -77.313]}},
                    {{name: "Manassas", location: [38.751, -77.475]}},
                    {{name: "Dumfries", location: [38.567, -77.329]}}
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
            st.info(f"HTML file '{output_file}' created successfully.")

        except Exception as e:
            st.error(f"Error writing map HTML file: {e}")


        # Display the map
        # Ensure the HTML file exists before trying to display it
        import os
        if os.path.exists(output_file):
            st.info(f"Attempting to display map HTML file: {output_file}")
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
                components.html(html_content, width=1000, height=800) # Increased height slightly
                st.info("Map HTML displayed successfully using components.html.")
            except Exception as e:
                 st.error(f"Error displaying map HTML with components.html: {e}")
                 st.warning("Falling back to st_folium with the output file path...")
                 try:
                      # Fallback to st_folium with file path - generally less reliable for complex custom HTML
                      st_map = st_folium(output_file, width=1000, height=800)
                      st.info("Map displayed using st_folium with file path.")
                 except Exception as e_folium:
                       st.error(f"Error displaying map with st_folium fallback: {e_folium}")

        else:
            st.error(f"Map HTML file not found after attempting to create it: {output_file}")


    else:
        st.warning("No data available to generate the map after applying filters and merging.")

else:
    st.error("Geometry column not found in merged data. Cannot create GeoDataFrame for mapping. Check the shapefile loading and merging steps.")
