#!/usr/bin/env python3
"""Simple test map to verify folium is working"""

import folium
import pandas as pd

def create_simple_test_map():
    print("Creating simple test map...")
    
    # Create a basic map
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    # Add a simple marker
    folium.Marker(
        [40.7128, -74.0060],  # New York
        popup='New York City',
        tooltip='Click me!'
    ).add_to(m)
    
    # Add another marker
    folium.Marker(
        [51.5074, -0.1278],  # London
        popup='London',
        tooltip='London, UK'
    ).add_to(m)
    
    # Save the map
    m.save('test_map.html')
    print("✅ Simple test map saved to test_map.html")

if __name__ == "__main__":
    create_simple_test_map()
