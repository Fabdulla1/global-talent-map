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
        
        # Simplify geometries for better performance
        world['geometry'] = world['geometry'].simplify(tolerance=0.01, preserve_topology=True)
        
        # Calculate centroids
        print("Calculating country centroids...")
        centroids = world.geometry.centroid
        centroids_df = pd.DataFrame({
            'admin': world['shapeName'],
            'longitude': centroids.x,
            'latitude': centroids.y
        })
        
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
        """Get styling for countries based on number of programs"""
        # Enhanced style for countries with programs - building on light theme
        base_style = {
            'color': '#17a2b8',  # Nice teal border
            'weight': 2.5,
            'fillOpacity': 0.75,
            'stroke': True
        }
        
        # Use the bright teal but more vibrant
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
        """Create the folium map"""
        print("Creating map...")
        
        # Merge data with centroids
        dt = dt.merge(centroids_df, left_on='country', right_on='admin', how='left')
        
        # Check for countries without coordinates
        missing_coords = dt[dt['longitude'].isna()]
        if not missing_coords.empty:
            print(f"Warning: Missing coordinates for countries: {missing_coords['country'].unique()}")
            dt = dt.dropna(subset=['longitude', 'latitude'])
        
        # Separate countries
        selected_countries = world[world['shapeName'].isin(dt['country'])]
        other_countries = world[~world['shapeName'].isin(dt['country'])]
        
        # Filter out small territories
        exclude_countries = ['Dragonja', 'Vatican City', 'Liancourt Rocks', 'Spratly Is', 'Fiji', 'Antarctica']
        other_countries = other_countries[~other_countries['shapeName'].isin(exclude_countries)]
        
        # Add program info to selected countries with detailed program breakdown
        country_program_details = self.create_country_program_details(dt)
        selected_countries = selected_countries.merge(
            country_program_details, left_on='shapeName', right_on='country', how='left'
        )
        
        # Create base map with no default tiles
        m = folium.Map(
            location=[20, 20],
            zoom_start=10,  
            tiles=None,  # No default tiles to avoid conflicts
            prefer_canvas=True,
            world_copy_jump=False,  # Prevent infinite horizontal scrolling
            no_wrap=True,  # Prevent map wrapping
            max_bounds=True,  # Enable bounds restriction
            min_zoom=1,
            max_zoom=10
        )
        
        # Add custom CSS to ensure the map fills the entire viewport
        viewport_css = """
        <style>
        html, body {
            width: 100vw !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            background: #fff !important;
        }
        .folium-map, .folium-map > div, [id*="map_"] {
            width: 100vw !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            z-index: 1 !important;
        }
        .leaflet-container {
            width: 100vw !important;
            height: 100vh !important;
            background: #fff !important;
        }
        </style>
        """
        m.get_root().html.add_child(folium.Element(viewport_css))
        
        # Set world bounds to prevent infinite scrolling
        m.fit_bounds([[-85, -180], [85, 180]])
        
        # Add the clean light theme base tile layer
        folium.TileLayer(
            tiles='CartoDB positron',
            name='Base Map',
            control=False,
            overlay=False,
            no_wrap=True  # Prevent tile wrapping
        ).add_to(m)
          # Add program countries with vibrant highlighting
        program_countries_layer = folium.GeoJson(
            selected_countries,
            style_function=lambda feature: self.get_country_style(feature),
            tooltip=folium.GeoJsonTooltip(
                fields=['shapeName', 'program_details'],
                aliases=['Country:', 'Programs:'],
                style="font-size: 15px; font-weight: normal; padding: 12px 18px; background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,249,250,0.98)); color: #212529; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.15), 0 0 20px rgba(32, 201, 151, 0.3); border: 3px solid #20c997; backdrop-filter: blur(5px);",
                sticky=True,
                labels=True
            ),
            highlight_function=lambda feature: {
                'weight': 3.5,
                'color': '#17a2b8',
                'fillOpacity': 0.9,
                'fillColor': '#17a2b8'
            },
            name='Program Countries'
        )
        program_countries_layer.add_to(m)
        
        # Add legend
        self.add_legend(m)
        
        return m
    
    def add_legend(self, map_obj: folium.Map):
        """Add legend to the map"""
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; 
                    width: min(220px, 45vw); height: min(260px, 50vh); 
                    background: rgba(255,255,255,0.95); 
                    color: #212529; border: 2px solid #20c997; 
                    z-index: 9999; 
                    font-size: min(12px, 3vw); padding: min(15px, 3vw); border-radius: 8px; 
                    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                    overflow: auto;">
            
            <!-- Program countries section -->
            <div style="margin-bottom: 15px; padding: 10px; 
                        background: rgba(32, 201, 151, 0.1); 
                        border-radius: 6px;">
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: min(16px, 4vw); height: min(10px, 2.5vw); 
                               background: #20c997; 
                               border: 1px solid #17a2b8; margin-right: 8px; 
                               border-radius: 3px; flex-shrink: 0;"></div>
                    <span style="font-weight: bold; color: #2c3e50; font-size: min(13px, 3.2vw);">
                        Program Countries
                    </span>
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
