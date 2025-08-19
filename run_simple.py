#!/usr/bin/env python3
"""
Global Talent Map - Python Version
Converts the R leaflet map to Python using folium
"""

import pandas as pd
import geopandas as gpd
import folium
import requests
import json
import numpy as np
import math
import os
from typing import Tuple, Dict

class GlobalTalentMap:
    def __init__(self):
        self.pins_path = "https://raw.githubusercontent.com/threndash/globtalent-map/main/pins/"
        self.geoboundaries_file = "geoBoundariesCGAZ_ADM0.geojson"
        
    def download_world_data(self) -> str:
        """Download world boundaries if not exists"""
        if not os.path.exists(self.geoboundaries_file):
            url = f"https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/CGAZ/{self.geoboundaries_file}"
            print(f"Downloading world boundaries...")
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(self.geoboundaries_file, 'wb') as f:
                    f.write(response.content)
                print("Download complete!")
            except requests.RequestException as e:
                print(f"Error downloading data: {e}")
                raise
        return self.geoboundaries_file
    
    def load_world_data(self) -> Tuple[gpd.GeoDataFrame, pd.DataFrame]:
        """Load and process world geographic data"""
        gb_file = self.download_world_data()
        
        print("Loading world boundaries...")
        world = gpd.read_file(gb_file)
        
        # Convert to equal area projection (Mollweide) for accurate area representation
        print("Converting to equal area projection...")
        world = world.to_crs('ESRI:54009')  # Mollweide equal area projection
        
        # Simplify geometries for better performance
        world['geometry'] = world['geometry'].simplify(tolerance=10000, preserve_topology=True)  # Adjusted tolerance for projected coordinates
        
        # Calculate centroids in projected coordinates
        print("Calculating country centroids...")
        centroids = world.geometry.centroid
        
        # Convert centroids back to WGS84 for folium compatibility
        centroids_gdf = gpd.GeoDataFrame(geometry=centroids, crs='ESRI:54009')
        centroids_wgs84 = centroids_gdf.to_crs('EPSG:4326')
        
        centroids_df = pd.DataFrame({
            'admin': world['shapeName'],
            'longitude': centroids_wgs84.geometry.x,
            'latitude': centroids_wgs84.geometry.y
        })
        
        # Convert world data back to WGS84 for folium
        world = world.to_crs('EPSG:4326')
        
        return world, centroids_df
    
    def load_excel_data(self) -> pd.DataFrame:
        """Load and process the Excel input data"""
        print("Loading Excel data...")
        
        try:
            # Try to read the Excel file
            dt = pd.read_excel("input_data.xlsx")
        except FileNotFoundError:
            print("Error: input_data.xlsx not found!")
            print("Please make sure the Excel file exists in the current directory.")
            raise
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            raise
        
        # Get column names and process them
        original_cols = dt.columns.tolist()
        print(f"Found columns: {original_cols}")
        
        # Reshape from wide to long format
        dt_melted = dt.melt(var_name='program', value_name='country')
        
        # Remove rows with missing countries
        dt_clean = dt_melted.dropna(subset=['country']).copy()
        
        # Clean program names (remove spaces, special characters)
        dt_clean['program'] = dt_clean['program'].str.strip().str.upper()
        
        print(f"Found programs: {dt_clean['program'].unique()}")
        print(f"Found countries: {sorted(dt_clean['country'].unique())}")
        
        return dt_clean
    
    def standardize_country_names(self, dt: pd.DataFrame) -> pd.DataFrame:
        """Standardize country names to match geographic data"""
        country_mapping = {
            'Bosnia': 'Bosnia and Herzegovina',
            'Cameroun': 'Cameroon',
            'Côte d\'Ivoire': 'Ivory Coast',
            'Czech Republic': 'Czechia',
            'DRC': 'Democratic Republic of the Congo',
            'Eswatini': 'eSwatini',
            'Macedonia': 'North Macedonia',
            'Salvador': 'El Salvador',
            'Serbia': 'Republic of Serbia',
            'Tanzania': 'United Republic of Tanzania'
        }
        
        dt['country'] = dt['country'].replace(country_mapping)
        return dt
    
    def standardize_admin_names(self, centroids_df: pd.DataFrame) -> pd.DataFrame:
        """Standardize admin names in centroids data"""
        name_mapping = {
            'Bosnia & Herzegovina': 'Bosnia and Herzegovina',
            'Samoa': 'American Samoa',
            'Congo, Dem Rep of the': 'Democratic Republic of the Congo',
            'Cote d\'Ivoire': 'Ivory Coast',
            'Macedonia': 'North Macedonia',
            'Serbia': 'Republic of Serbia',
            'Tanzania': 'United Republic of Tanzania',
            'Swaziland': 'eSwatini'
        }
        
        centroids_df['admin'] = centroids_df['admin'].replace(name_mapping)
        
        # Handle Palestine special case
        palestine_mask = centroids_df['admin'].isin(['Gaza Strip', 'West Bank'])
        if palestine_mask.any():
            # Take the first occurrence for Palestine
            centroids_df.loc[palestine_mask, 'admin'] = 'Palestine'
            centroids_df = centroids_df.drop_duplicates(subset=['admin'])
        
        return centroids_df
    
    def process_program_data(self, dt: pd.DataFrame) -> pd.DataFrame:
        """Process program data and calculate angles"""
        # Remove duplicates
        dt = dt.drop_duplicates()
        
        # Calculate program statistics per country
        program_stats = dt.groupby('country').agg({
            'program': ['count', lambda x: ', '.join(sorted(x.unique()))]
        }).reset_index()
        
        program_stats.columns = ['country', 'n_programs', 'all_programs']
        
        # Add order within each country
        dt_with_order = []
        for country in dt['country'].unique():
            country_data = dt[dt['country'] == country].copy()
            country_data = country_data.sort_values('program')
            country_data['ord_program'] = range(1, len(country_data) + 1)
            dt_with_order.append(country_data)
        
        dt_final = pd.concat(dt_with_order, ignore_index=True)
        dt_final = dt_final.merge(program_stats, on='country')
        
        # Calculate angles
        dt_final['ang'] = 0
        
        # Angle assignment based on number of programs
        angle_mapping = {
            2: {1: 320, 2: 40},
            3: {1: 300, 2: 0, 3: 60},
            4: {1: 0, 2: 90, 3: 180, 4: 270}
        }
        
        for n_prog, angles in angle_mapping.items():
            for ord_prog, angle in angles.items():
                mask = (dt_final['n_programs'] == n_prog) & (dt_final['ord_program'] == ord_prog)
                dt_final.loc[mask, 'ang'] = angle
        
        return dt_final
    
    def create_country_program_details(self, dt: pd.DataFrame) -> pd.DataFrame:
        """Create detailed program information for each country"""
        country_details = []
        
        for country in dt['country'].unique():
            country_data = dt[dt['country'] == country]
            programs = sorted(country_data['program'].unique())
            
            # Create a nicely formatted program list
            program_list = []
            for program in programs:
                color = self.get_program_color(program)
                program_list.append(f'<span style="color: {color}; font-weight: bold;">● {program}</span>')
            
            program_details = '<br/>'.join(program_list)
            
            country_details.append({
                'country': country,
                'program_count': len(programs),
                'program_details': program_details,
                'all_programs': ', '.join(programs)
            })
        
        return pd.DataFrame(country_details)
    
    def get_country_style(self, feature):
        """Get styling for countries based on number of programs - button-like appearance"""
        # Enhanced button-like style for countries with programs
        base_style = {
            'color': '#17a2b8',  # Nice teal border
            'weight': 2.5,
            'fillOpacity': 0.85,
            'stroke': True,
            'cursor': 'pointer'  # Show pointer cursor to indicate clickability
        }
        
        # Use the bright teal but more vibrant with slight gradient effect
        base_style['fillColor'] = '#20c997'  # Vibrant teal-green
        
        return base_style
    
    def get_program_color(self, program: str) -> str:
        """Get color for each program"""
        colors = {
            'STAR': '#1f77b4',
            'NATIONS': '#ff7f0e', 
            'BIG': '#2ca02c',
            'EXCL': '#d62728'
        }
        return colors.get(program.upper(), '#666666')
    
    def create_folium_map(self, world: gpd.GeoDataFrame, dt: pd.DataFrame, centroids_df: pd.DataFrame) -> folium.Map:
        """Create the folium map with equal area considerations"""
        print("Creating map with equal area considerations...")
        
        # Merge data with centroids
        dt = dt.merge(centroids_df, left_on='country', right_on='admin', how='left')
        
        # Check for countries without coordinates
        missing_coords = dt[dt['longitude'].isna()]
        if not missing_coords.empty:
            print(f"Warning: Missing coordinates for countries: {missing_coords['country'].unique()}")
            dt = dt.dropna(subset=['longitude', 'latitude'])
        
        # Use original world data and ensure it's in the right format
        print(f"World data shape: {world.shape}")
        print(f"World CRS: {world.crs}")
        
        # Ensure world data is in WGS84
        if world.crs != 'EPSG:4326':
            world = world.to_crs('EPSG:4326')
        
        # Get program countries
        program_country_names = dt['country'].unique()
        print(f"Looking for these program countries: {list(program_country_names)}")
        
        selected_countries = world[world['shapeName'].isin(program_country_names)].copy()
        other_countries = world[~world['shapeName'].isin(program_country_names)].copy()
        
        print(f"Found {len(selected_countries)} program countries in world data")
        print(f"Found {len(other_countries)} other countries in world data")
        
        # Filter out small territories
        exclude_countries = ['Dragonja', 'Vatican City', 'Liancourt Rocks', 'Spratly Is', 'Antarctica']
        other_countries = other_countries[~other_countries['shapeName'].isin(exclude_countries)]
        
        # Add program info to selected countries
        country_program_details = self.create_country_program_details(dt)
        selected_countries = selected_countries.merge(
            country_program_details, left_on='shapeName', right_on='country', how='left'
        )
        
        print(f"Selected countries after merge: {len(selected_countries)}")
        if len(selected_countries) > 0:
            print(f"Sample program details: {selected_countries[['shapeName', 'program_details']].head()}")
        else:
            print("ERROR: No selected countries found after merge!")
        
        # Create base map
        m = folium.Map(
            location=[20, 0],
            zoom_start=2,
            tiles='OpenStreetMap',  # Use simple, reliable tiles
            prefer_canvas=True
        )
        
        # Add simple CSS
        simple_css = """
        <style>
        html, body { width: 100%; height: 100%; margin: 0; padding: 0; }
        .folium-map { width: 100vw; height: 100vh; }
        </style>
        """
        m.get_root().html.add_child(folium.Element(simple_css))
        
        # First, add ALL countries as background layer using simple styling
        print("Adding background countries...")
        try:
            if len(other_countries) > 0:
                folium.GeoJson(
                    other_countries.__geo_interface__,  # Convert to proper GeoJSON
                    style_function=lambda feature: {
                        'fillColor': '#f0f0f0',
                        'color': '#cccccc',
                        'weight': 1,
                        'fillOpacity': 0.7
                    }
                ).add_to(m)
                print(f"✅ Added {len(other_countries)} background countries")
            else:
                print("❌ No background countries to add")
        except Exception as e:
            print(f"❌ Error adding background countries: {e}")
        
        # Then add program countries on top
        print("Adding program countries...")
        try:
            if len(selected_countries) > 0:
                folium.GeoJson(
                    selected_countries.__geo_interface__,  # Convert to proper GeoJSON
                    style_function=lambda feature: {
                        'fillColor': '#00cc66',  # Bright green
                        'color': '#006633',      # Dark green border
                        'weight': 2,
                        'fillOpacity': 1.0
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['shapeName'],
                        aliases=['Country:']
                    )
                ).add_to(m)
                print(f"✅ Added {len(selected_countries)} program countries")
            else:
                print("❌ No program countries to add")
        except Exception as e:
            print(f"❌ Error adding program countries: {e}")
            # If GeoJSON conversion fails, try a different approach
            print("Trying alternative method...")
            try:
                folium.GeoJson(
                    selected_countries,
                    style_function=lambda feature: {
                        'fillColor': '#00cc66',
                        'color': '#006633',
                        'weight': 2,
                        'fillOpacity': 1.0
                    }
                ).add_to(m)
                print("✅ Alternative method worked")
            except Exception as e2:
                print(f"❌ Alternative method also failed: {e2}")
        
        # Add JavaScript for direct click functionality
        click_js = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                const countryElements = document.querySelectorAll('.leaflet-interactive');
                countryElements.forEach(function(element) {
                    element.addEventListener('click', function(e) {
                        e.stopPropagation();
                        window.open('https://globtalent.org', '_blank');
                    });
                    element.style.cursor = 'pointer';
                });
            }, 1000);
        });
        </script>
        """
        m.get_root().html.add_child(folium.Element(click_js))
        
        # Add simplified legend
        self.add_simplified_legend(m)
        
        return m
        
        return m
    
    def add_simplified_legend(self, map_obj: folium.Map):
        """Add a simplified legend"""
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 200px; 
                    background: white; border: 2px solid #00cc66; z-index: 9999; 
                    padding: 15px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <h4 style="margin: 0 0 10px 0; color: #333;">Global Talent Map</h4>
            <div style="margin: 5px 0;">
                <span style="display: inline-block; width: 20px; height: 15px; 
                           background: #00cc66; border: 1px solid #006633; margin-right: 5px;"></span>
                Program Countries
            </div>
            <div style="margin: 5px 0;">
                <span style="display: inline-block; width: 20px; height: 15px; 
                           background: #f0f0f0; border: 1px solid #cccccc; margin-right: 5px;"></span>
                Other Countries
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def add_legend(self, map_obj: folium.Map):
        """Add legend to the map"""
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; 
                    width: min(220px, 40vw); height: min(260px, 50vh); 
                    background: white; 
                    color: #1f2937; border: 2px solid #10b981; 
                    z-index: 9999; 
                    font-size: min(12px, 3vw); padding: min(15px, 3vw); border-radius: 8px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    overflow: auto;">
            
            <!-- Title -->
            <div style="margin-bottom: 15px; padding: 8px; 
                        background: #f0fdf4; 
                        border-radius: 6px; text-align: center; border: 1px solid #10b981;">
                <div style="font-size: min(13px, 3.2vw); color: #1f2937; font-weight: bold;">
                    🌍 Global Talent Map
                </div>
                <div style="font-size: min(10px, 2.5vw); color: #6b7280; font-style: italic;">
                    Equal Area Aware
                </div>
            </div>
            
            <!-- Program countries section -->
            <div style="margin-bottom: 15px; padding: 10px; 
                        background: #f0fdf4; 
                        border-radius: 6px; border: 1px solid #bbf7d0;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(16px, 4vw); height: min(10px, 2.5vw); 
                               background: #10b981; 
                               border: 1px solid #059669; margin-right: 8px; 
                               border-radius: 3px; flex-shrink: 0;"></div>
                    <span style="font-weight: bold; color: #1f2937; font-size: min(12px, 3vw);">
                        Program Countries
                    </span>
                </div>
                <div style="font-size: min(9px, 2.3vw); color: #6b7280; margin-left: min(24px, 6vw);">
                    Countries with active programs
                </div>
            </div>
            
            <!-- Background countries section -->
            <div style="margin-bottom: 15px; padding: 10px; 
                        background: #f8fafc; 
                        border-radius: 6px; border: 1px solid #e2e8f0;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(16px, 4vw); height: min(10px, 2.5vw); 
                               background: #f1f5f9; 
                               border: 1px solid #cbd5e1; margin-right: 8px; 
                               border-radius: 3px; flex-shrink: 0;"></div>
                    <span style="font-weight: bold; color: #1f2937; font-size: min(12px, 3vw);">
                        Other Countries
                    </span>
                </div>
                <div style="font-size: min(9px, 2.3vw); color: #6b7280; margin-left: min(24px, 6vw);">
                    Reference countries
                </div>
            </div>
            
            <!-- Program types section -->
            <div style="background: rgba(248, 249, 250, 0.8); padding: min(12px, 3vw); border-radius: 6px;">
                <div style="font-weight: bold; margin-bottom: 10px; color: #2c3e50; 
                           font-size: min(13px, 3.2vw); text-align: center;">
                    Program Types
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(10px, 2.5vw); height: min(10px, 2.5vw); background-color: #1f77b4; 
                               border-radius: 50%; margin-right: 8px; 
                               box-shadow: 0 1px 3px rgba(31, 119, 180, 0.4); flex-shrink: 0;"></div>
                    <span style="color: #2c3e50; font-weight: 500; font-size: min(11px, 2.8vw);">
                        STAR
                    </span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(10px, 2.5vw); height: min(10px, 2.5vw); background-color: #ff7f0e; 
                               border-radius: 50%; margin-right: 8px; 
                               box-shadow: 0 1px 3px rgba(255, 127, 14, 0.4); flex-shrink: 0;"></div>
                    <span style="color: #2c3e50; font-weight: 500; font-size: min(11px, 2.8vw);">
                        NATIONS
                    </span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(10px, 2.5vw); height: min(10px, 2.5vw); background-color: #2ca02c; 
                               border-radius: 50%; margin-right: 8px; 
                               box-shadow: 0 1px 3px rgba(44, 160, 44, 0.4); flex-shrink: 0;"></div>
                    <span style="color: #2c3e50; font-weight: 500; font-size: min(11px, 2.8vw);">
                        BIG
                    </span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(10px, 2.5vw); height: min(10px, 2.5vw); background-color: #d62728; 
                               border-radius: 50%; margin-right: 8px; 
                               box-shadow: 0 1px 3px rgba(214, 39, 40, 0.4); flex-shrink: 0;"></div>
                    <span style="color: #2c3e50; font-weight: 500; font-size: min(11px, 2.8vw);">
                        EXCL
                    </span>
                </div>
            </div>
        </div>
        '''
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def generate_map(self, output_file: str = "index.html"):
        """Main function to generate the map"""
        try:
            # Load all data
            world, centroids_df = self.load_world_data()
            dt = self.load_excel_data()
            
            # Process data
            dt = self.standardize_country_names(dt)
            centroids_df = self.standardize_admin_names(centroids_df)
            dt = self.process_program_data(dt)
            
            # Create and save map
            map_obj = self.create_folium_map(world, dt, centroids_df)
            map_obj.save(output_file)
            
            print(f"✅ Map successfully saved to {output_file}")
            print(f"📊 Found {len(dt['country'].unique())} countries with {len(dt)} program entries")
            
            return map_obj
            
        except Exception as e:
            print(f"❌ Error generating map: {e}")
            raise

def main():
    """Main entry point"""
    print("Global Talent Map Generator (Python)")
    print("=" * 40)
    
    mapper = GlobalTalentMap()
    mapper.generate_map()

if __name__ == "__main__":
    main()
