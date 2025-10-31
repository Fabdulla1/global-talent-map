#!/usr/bin/env python3
"""
Data Processing Script for Global Talent Map

This script automatically processes the CSV and Excel files in the data folder
and generates the necessary JavaScript data for the index.html file.

Usage: python process_data.py
"""

import pandas as pd
import json
import os
from pathlib import Path

# Country coordinates mapping (approximate center points)
COUNTRY_COORDINATES = {
    "United States": {"lat": 39.8283, "lng": -98.5795},
    "Canada": {"lat": 56.1304, "lng": -106.3468},
    "Brazil": {"lat": -14.2350, "lng": -51.9253},
    "United Kingdom": {"lat": 55.3781, "lng": -3.4360},
    "Germany": {"lat": 51.1657, "lng": 10.4515},
    "France": {"lat": 46.2276, "lng": 2.2137},
    "India": {"lat": 20.5937, "lng": 78.9629},
    "Hong Kong, China": {"lat": 22.7919, "lng": 114.7157},
    "Japan": {"lat": 36.2048, "lng": 138.2529},
    "Australia": {"lat": -25.2744, "lng": 133.7751},
    "Nigeria": {"lat": 9.0820, "lng": 8.6753},
    "South Africa": {"lat": -30.5595, "lng": 22.9375},
    "Kenya": {"lat": -0.0236, "lng": 37.9062},
    "Italy": {"lat": 41.8719, "lng": 12.5674},
    "Russia": {"lat": 61.5240, "lng": 105.3188},
    "Mexico": {"lat": 23.6345, "lng": -102.5528},
    "Argentina": {"lat": -38.4161, "lng": -63.6167},
    "Colombia": {"lat": 4.5709, "lng": -74.2973},
    "Egypt": {"lat": 26.8206, "lng": 30.8025},
    "Kazakhstan": {"lat": 48.0196, "lng": 66.9237},
    "Bosnia and Herzegovina": {"lat": 43.9159, "lng": 17.6791},
    "Bosnia": {"lat": 43.9159, "lng": 17.6791},  # Alternative name
    "Romania": {"lat": 45.9432, "lng": 24.9668},
    "Serbia": {"lat": 44.0165, "lng": 21.0059},
    "Ukraine": {"lat": 48.3794, "lng": 31.1656},
    "Mongolia": {"lat": 47.8864, "lng": 106.9057},
    "El Salvador": {"lat": 13.7942, "lng": -88.8965},
    "Philippines": {"lat": 12.8797, "lng": 121.7740},
    "Georgia": {"lat": 42.3154, "lng": 43.3569},
    "Costa Rica": {"lat": 9.7489, "lng": -83.7534},
    "Bhutan": {"lat": 27.5142, "lng": 90.4336},
    "Rwanda": {"lat": -1.9403, "lng": 29.8739},
    "Bulgaria": {"lat": 42.7339, "lng": 25.4858},
    "Hungary": {"lat": 47.1625, "lng": 19.5033},
    "Turkey": {"lat": 38.9637, "lng": 35.2433},
    "Indonesia": {"lat": -0.7893, "lng": 113.9213},
    "Iran": {"lat": 32.4279, "lng": 53.6880},
    "Belarus": {"lat": 53.7098, "lng": 27.9534},
    "Greece": {"lat": 39.0742, "lng": 21.8243},
    "Poland": {"lat": 51.9194, "lng": 19.1451},
    "Finland": {"lat": 61.9241, "lng": 25.7482},
    "Singapore": {"lat": 1.3521, "lng": 103.8198},
    "Cyprus": {"lat": 35.1264, "lng": 33.4299},
    "Armenia": {"lat": 40.0691, "lng": 45.0382},
    "North Macedonia": {"lat": 41.6086, "lng": 21.7453},
    "Netherlands": {"lat": 52.1326, "lng": 5.2913},
    "Uzbekistan": {"lat": 41.3775, "lng": 64.5853},
    "Albania": {"lat": 41.1533, "lng": 20.1683},
    "Algeria": {"lat": 28.0339, "lng": 1.6596},
    "Bangladesh": {"lat": 23.6850, "lng": 90.3563},
    "Bolivia": {"lat": -16.2902, "lng": -63.5887},
    "Botswana": {"lat": -22.3285, "lng": 24.6849},
    "Cameroon": {"lat": 7.3697, "lng": 12.3547},
    "Chile": {"lat": -35.6751, "lng": -71.5430},
    "Cuba": {"lat": 21.5218, "lng": -77.7812},
    "Czech Republic": {"lat": 49.8175, "lng": 15.4730},
    "Democratic Republic of the Congo": {"lat": -4.0383, "lng": 21.7587},
    "Dominican Republic": {"lat": 18.7357, "lng": -70.1627},
    "Ethiopia": {"lat": 9.1450, "lng": 40.4897},
    "Guatemala": {"lat": 15.7835, "lng": -90.2308},
    "Ivory Coast": {"lat": 7.5400, "lng": -5.5471},
    "Jordan": {"lat": 30.5852, "lng": 36.2384},
    "Kyrgyzstan": {"lat": 41.2044, "lng": 74.7661},
    "Latvia": {"lat": 56.8796, "lng": 24.6032},
    "Lesotho": {"lat": -29.6100, "lng": 28.2336},
    "Lithuania": {"lat": 55.1694, "lng": 23.8813},
    "Malaysia": {"lat": 4.2105, "lng": 101.9758},
    "Mauritania": {"lat": 21.0079, "lng": -10.9408},
    "Montenegro": {"lat": 42.7087, "lng": 19.3744},
    "Morocco": {"lat": 31.7917, "lng": -7.0926},
    "Namibia": {"lat": -22.9576, "lng": 18.4904},
    "Nepal": {"lat": 28.3949, "lng": 84.1240},
    "Nicaragua": {"lat": 12.2651, "lng": -85.2072},
    "Pakistan": {"lat": 30.3753, "lng": 69.3451},
    "Palestine": {"lat": 31.9522, "lng": 35.2332},
    "Peru": {"lat": -9.1900, "lng": -75.0152},
    "South Korea": {"lat": 35.9078, "lng": 127.7669},
    "South Sudan": {"lat": 6.8770, "lng": 31.3070},
    "Spain": {"lat": 40.4637, "lng": -3.7492},
    "Tanzania": {"lat": -6.3690, "lng": 34.8888},
    "Thailand": {"lat": 15.8700, "lng": 100.9925},
    "Tunisia": {"lat": 33.8869, "lng": 9.5375},
    "Uganda": {"lat": 1.3733, "lng": 32.2903},
    "Vietnam": {"lat": 14.0583, "lng": 108.2772},
    "Zimbabwe": {"lat": -19.0154, "lng": 29.1549},
    "Taiwan": {"lat": 23.6978, "lng": 120.9605},
    "Israel": {"lat": 31.0461, "lng": 34.8516},
    "Croatia": {"lat": 45.1000, "lng": 15.2000},
    "Slovenia": {"lat": 46.1512, "lng": 14.9955},
    "Saudi Arabia": {"lat": 23.8859, "lng": 45.0792},
    "Moldova": {"lat": 47.4116, "lng": 28.3699},
    "Azerbaijan": {"lat": 40.1431, "lng": 47.5769},
    "Slovakia": {"lat": 48.6690, "lng": 19.6990},
    "Estonia": {"lat": 58.5953, "lng": 25.0136},
    "Iceland": {"lat": 64.9631, "lng": -19.0208},
    "Ireland": {"lat": 53.1424, "lng": -7.6921},
    "Norway": {"lat": 60.4720, "lng": 8.4689},
    "Sweden": {"lat": 60.1282, "lng": 18.6435},
    "Denmark": {"lat": 56.2639, "lng": 9.5018},
    "Belgium": {"lat": 50.5039, "lng": 4.4699},
    "Luxembourg": {"lat": 49.8153, "lng": 6.1296},
    "Switzerland": {"lat": 46.8182, "lng": 8.2275},
    "Austria": {"lat": 47.5162, "lng": 14.5501},
    "Portugal": {"lat": 39.3999, "lng": -8.2245},
    "American Samoa": {"lat": -14.2710, "lng": -170.1322},
    "Eswatini": {"lat": -26.5225, "lng": 31.4659}
}

def normalize_country_name(country):
    """Normalize country names to match the standard format"""
    name_mapping = {
        "Bosnia": "Bosnia and Herzegovina",
        "Eswatini": "Eswatini",
        "UK": "United Kingdom"
        # Add more mappings as needed
    }
    return name_mapping.get(country, country)

def load_csv_data():
    """Load and process CSV data files"""
    data_dir = Path("data")
    
    # Load BIG scholars data
    big_scholars = {}
    
    # Process 2024 data
    big_2024_file = data_dir / "BIG_scholars_2024_entry.csv"
    if big_2024_file.exists():
        df_2024 = pd.read_csv(big_2024_file)
        print(f"Processing 2024 data: {len(df_2024)} rows")
        for _, row in df_2024.iterrows():
            country = normalize_country_name(row['Country'])
            name = row['Name']
            if pd.notna(country) and pd.notna(name):  # Skip empty rows
                if country not in big_scholars:
                    big_scholars[country] = {}
                if '2024' not in big_scholars[country]:
                    big_scholars[country]['2024'] = []
                big_scholars[country]['2024'].append(name)
    
    # Process 2025 data - this has a complex header structure
    big_2025_file = data_dir / "Big_scholars_list_2025.csv"
    if big_2025_file.exists():
        # Read with header=1 to skip the first row which is a multi-header
        df_2025 = pd.read_csv(big_2025_file, header=1)
        print(f"Processing 2025 data: {len(df_2025)} rows")
        
        # The columns should now be: Email, Name, Country, Gender, etc.
        for _, row in df_2025.iterrows():
            # Skip rows where essential data is missing
            if pd.isna(row.get('Country')) or pd.isna(row.get('Name')):
                continue
                
            country = normalize_country_name(row['Country'])
            name = row['Name']
            
            # Skip rows with placeholder data
            if 'Do not contact' in str(name) or name == 'Name':
                continue
                
            if country not in big_scholars:
                big_scholars[country] = {}
            if '2025' not in big_scholars[country]:
                big_scholars[country]['2025'] = []
            big_scholars[country]['2025'].append(name)
    
    return big_scholars

def generate_program_data():
    """Generate the program data structure"""
    big_scholars = load_csv_data()
    
    # Base program data - this would need to be expanded based on your full requirements
    # For now, I'm including the countries that have BIG scholars and some default programs
    program_data = {}
    
    # Default program assignments (you may want to make this configurable)
    default_programs = {
        "United States": ["NATIONS", "STAR"],
        "Canada": ["NATIONS", "STAR"],
        "United Kingdom": ["BIG", "EXCL", "STAR"],
        "Germany": ["BIG", "NATIONS", "EXCL", "STAR"],
        "France": ["NATIONS"],
        "India": ["BIG", "STAR"],
        "China": ["BIG"],
        "Japan": ["NATIONS", "STAR"],
        "Australia": ["BIG", "NATIONS", "STAR"],
        "Nigeria": ["NATIONS", "EXCL", "STAR"],
        "South Africa": ["NATIONS", "STAR"],
        "Kenya": ["EXCL", "STAR"],
        "Italy": ["EXCL"],
        "Russia": ["NATIONS", "EXCL"],
        "Mexico": ["NATIONS"],
        "Argentina": ["STAR"],
        "Colombia": ["NATIONS"],
        "Egypt": ["EXCL", "STAR"],
        "Kazakhstan": ["NATIONS"],
        "Philippines": ["NATIONS", "STAR"],
        "Georgia": ["NATIONS", "STAR"],
        "Bhutan": ["EXCL", "STAR"],
        "Rwanda": ["NATIONS", "EXCL", "STAR"],
        "Albania": ["STAR"],
        "Algeria": ["EXCL", "STAR"],
        "Bangladesh": ["STAR"],
        "Bolivia": ["STAR"],
        "Botswana": ["NATIONS", "STAR"],
        "Cameroon": ["STAR"],
        "Chile": ["NATIONS"],
        "Cuba": ["STAR"],
        "Czech Republic": ["STAR"],
        "Democratic Republic of the Congo": ["EXCL"],
        "Dominican Republic": ["STAR"],
        "Ethiopia": ["NATIONS", "STAR"],
        "Guatemala": ["EXCL", "STAR"],
        "Ivory Coast": ["STAR"],
        "Jordan": ["NATIONS", "STAR"],
        "Kyrgyzstan": ["NATIONS", "STAR"],
        "Latvia": ["STAR"],
        "Lesotho": ["STAR"],
        "Lithuania": ["NATIONS", "STAR"],
        "Malaysia": ["NATIONS", "STAR"],
        "Mauritania": ["NATIONS", "EXCL", "STAR"],
        "Montenegro": ["STAR"],
        "Morocco": ["NATIONS", "EXCL", "STAR"],
        "Namibia": ["NATIONS"],
        "Nepal": ["STAR"],
        "Nicaragua": ["EXCL", "STAR"],
        "Pakistan": ["NATIONS", "STAR"],
        "Palestine": ["STAR"]
    }
    
    # Get all countries that have data
    all_countries = set()
    all_countries.update(big_scholars.keys())
    all_countries.update(default_programs.keys())
    
    for country in all_countries:
        country_data = {}
        
        # Add programs
        if country in default_programs:
            country_data["programs"] = default_programs[country]
        elif country in big_scholars:
            country_data["programs"] = ["BIG"]
        else:
            country_data["programs"] = ["STAR"]  # Default program
        
        # Add coordinates
        if country in COUNTRY_COORDINATES:
            country_data["lat"] = COUNTRY_COORDINATES[country]["lat"]
            country_data["lng"] = COUNTRY_COORDINATES[country]["lng"]
        
        # Add BIG scholars if available
        if country in big_scholars:
            country_data["bigScholars"] = big_scholars[country]
        
        program_data[country] = country_data
    
    return program_data

def update_html_file():
    """Update the HTML file with new data"""
    html_file = Path("index.html")
    
    if not html_file.exists():
        print("Error: index.html not found")
        return
    
    # Generate new program data
    program_data = generate_program_data()
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert program data to JavaScript format
    js_data = "    const programData = " + json.dumps(program_data, indent=6) + ";"
    
    # Find and replace the programData section
    start_marker = "    /* ---------- DATA: keep exactly as-is from your app ---------- */"
    end_marker = "    // Country website mappings for click navigation"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Error: Could not find data section markers in HTML file")
        return
    
    # Replace the data section
    new_content = (
        content[:start_idx] + 
        start_marker + "\n" + 
        js_data + "\n\n    " +
        content[end_idx:]
    )
    
    # Write back to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully updated index.html with new data")
    print(f"📊 Generated data for {len(program_data)} countries")

def main():
    """Main function"""
    print("🚀 Starting data processing...")
    
    # Check if we're in the right directory
    if not Path("data").exists():
        print("Error: 'data' directory not found. Please run this script from the project root.")
        return
    
    try:
        update_html_file()
        print("✨ Data processing completed successfully!")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()