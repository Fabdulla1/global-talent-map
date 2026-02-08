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
    "Latin America & Ibero-America": {"lat": 13.4099, "lng": -78.6099},
    "United States of America": {"lat": 39.8283, "lng": -98.5795},
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
    "Russian Federation": {"lat": 61.5240, "lng": 105.3188},
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
    "The Philippines": {"lat": 12.8797, "lng": 121.7740},
    "Georgia": {"lat": 42.3154, "lng": 43.3569},
    "Costa Rica": {"lat": 9.7489, "lng": -83.7534},
    "Bhutan": {"lat": 27.5142, "lng": 90.4336},
    "Rwanda": {"lat": -1.9403, "lng": 29.8739},
    "Bulgaria": {"lat": 42.7339, "lng": 25.4858},
    "Hungary": {"lat": 47.1625, "lng": 19.5033},
    "Türkiye": {"lat": 38.9637, "lng": 35.2433},
    "Indonesia": {"lat": -6.0092, "lng": 106.5373},
    "Iran": {"lat": 32.4279, "lng": 53.6880},
    "Belarus": {"lat": 53.7098, "lng": 27.9534},
    "Greece": {"lat": 39.0742, "lng": 21.8243},
    "Poland": {"lat": 51.9194, "lng": 19.1451},
    "Finland": {"lat": 61.9241, "lng": 25.7482},
    "Singapore": {"lat": 1.3521, "lng": 103.8198},
    "Cyprus": {"lat": 35.1264, "lng": 33.4299},
    "Armenia": {"lat": 40.0691, "lng": 45.0382},
    "North Macedonia": {"lat": 41.6086, "lng": 21.7453},
    "The Netherlands": {"lat": 52.1326, "lng": 5.2913},
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
    "West Bank and Gaza": {"lat": 31.9522, "lng": 35.2332},
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
        "Turkey": "Türkiye"
        # Will add more mappings if needed
    }
    return name_mapping.get(country, country)

def load_bigscholars_data():
    """Load and process BIG scholars data from Excel (clean dataset)."""
    df = pd.read_excel(Path("data") / "GTF BIG Talent Scholars.xlsx")

    big_scholars = {}
    for _, row in df.iterrows():
        country = normalize_country_name(row["Country"])
        year = str(row["Year"])
        name = row["Name"]

        if country not in big_scholars:
            big_scholars[country] = {}
        if year not in big_scholars[country]:
            big_scholars[country][year] = []

        big_scholars[country][year].append(name)

    return big_scholars

def load_program_data():
    """
    Load the program data file, containing the countries and the respective programs they are enrolled in.
    """
    df = pd.read_excel(Path("data") / "Program Data.xlsx")

    gtf_programs = {}

    for _, row in df.iterrows():
        country = normalize_country_name(row["Country"])
        gtf_programs[country] = []
        if row["NATIONS"] == 1:
            gtf_programs[country].append("NATIONS")
        if row["EXCL"] == 1:
            gtf_programs[country].append("EXCL")
        if row["STAR"] == 1:
            gtf_programs[country].append("STAR")

    return gtf_programs

def generate_program_data():
    """Generate the program data structure"""
    big_scholars = load_bigscholars_data()
    gtf_programs = load_program_data()

    program_data = {}
    
    # Get all countries that have data
    all_countries = set()
    all_countries.update(big_scholars.keys())
    all_countries.update(gtf_programs.keys())
    
    for country in all_countries:
        country_data = {"programs":[]}
        
        # Add programs

        if country in big_scholars:
            country_data["programs"].append("BIG")
        if country in gtf_programs:
            country_data["programs"].extend(gtf_programs[country])
        
        # Add coordinates

        # assert country in COUNTRY_COORDINATES, f"{country} coordinates not found"

        if country in COUNTRY_COORDINATES:
            country_data["lat"] = COUNTRY_COORDINATES[country]["lat"]
            country_data["lng"] = COUNTRY_COORDINATES[country]["lng"]
        
        # Add BIG scholars if available
        if country in big_scholars:
            country_data["bigScholars"] = big_scholars[country]
        
        program_data[country] = country_data
    
    return program_data

def write_program_data_json(output_path=Path("data") / "programData.json"):
    """Write programData.json into /data/programData.json"""
    program_data = generate_program_data()

    print(program_data.get("Russian Federation", "Russia not found"))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(program_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote {output_path.as_posix()}")
    print(f"📊 Generated data for {len(program_data)} countries")

def main():
    """Main function"""
    print("🚀 Starting data processing...")

    if not Path("data").exists():
        print("Error: 'data' directory not found. Please run this script from the project root.")
        return

    try:
        write_program_data_json()
        print("✨ Data processing completed successfully!")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()