#!/usr/bin/env python3
"""
Global Talent Map - Advanced Version with Robinson Projection
A sophisticated map that fairly represents all regions, especially the Global South
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
import warnings
warnings.filterwarnings('ignore')

class AdvancedGlobalTalentMap:
    def __init__(self):
        self.pins_path = "https://raw.githubusercontent.com/threndash/globtalent-map/main/pins/"
        self.geoboundaries_file = "geoBoundariesCGAZ_ADM0.geojson"
        
    def download_world_data(self) -> str:
        """Download world boundaries if not exists"""
        if not os.path.exists(self.geoboundaries_file):
            url = f"https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/CGAZ/{self.geoboundaries_file}"
            print(f"📥 Downloading world boundaries...")
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(self.geoboundaries_file, 'wb') as f:
                    f.write(response.content)
                print("✅ Download complete!")
            except requests.RequestException as e:
                print(f"❌ Error downloading data: {e}")
                raise
        return self.geoboundaries_file
    
    def load_world_data(self) -> Tuple[gpd.GeoDataFrame, pd.DataFrame]:
        """Load and process world geographic data with Robinson projection"""
        gb_file = self.download_world_data()
        
        print("🌍 Loading world boundaries...")
        world = gpd.read_file(gb_file)
        
        # Use Robinson projection (ESRI:54030) for fair global representation
        print("🗺️  Converting to Robinson projection for fair global representation...")
        world_robinson = world.to_crs('ESRI:54030')  # Robinson projection
        
        # Simplify geometries for better performance while preserving accuracy
        world_robinson['geometry'] = world_robinson['geometry'].simplify(
            tolerance=5000, preserve_topology=True
        )
        
        # Calculate centroids in Robinson projection for better accuracy
        print("📍 Calculating country centroids...")
        centroids_robinson = world_robinson.geometry.centroid
        
        # Convert centroids back to WGS84 for web mapping
        centroids_gdf = gpd.GeoDataFrame(
            geometry=centroids_robinson, crs='ESRI:54030'
        )
        centroids_wgs84 = centroids_gdf.to_crs('EPSG:4326')
        
        centroids_df = pd.DataFrame({
            'admin': world_robinson['shapeName'],
            'longitude': centroids_wgs84.geometry.x,
            'latitude': centroids_wgs84.geometry.y
        })
        
        # Convert world data back to WGS84 for web display
        world_final = world_robinson.to_crs('EPSG:4326')
        
        return world_final, centroids_df
    
    def load_excel_data(self) -> pd.DataFrame:
        """Load and process the Excel input data"""
        print("📊 Loading Excel data...")
        
        try:
            dt = pd.read_excel("input_data.xlsx")
        except FileNotFoundError:
            print("❌ Error: input_data.xlsx not found!")
            print("Please make sure the Excel file exists in the current directory.")
            raise
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            raise
        
        original_cols = dt.columns.tolist()
        print(f"📋 Found columns: {original_cols}")
        
        # Reshape from wide to long format
        dt_melted = dt.melt(var_name='program', value_name='country')
        dt_clean = dt_melted.dropna(subset=['country']).copy()
        dt_clean['program'] = dt_clean['program'].str.strip().str.upper()
        
        print(f"🎯 Found programs: {dt_clean['program'].unique()}")
        print(f"🌎 Found {len(dt_clean['country'].unique())} countries")
        
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
            centroids_df.loc[palestine_mask, 'admin'] = 'Palestine'
            centroids_df = centroids_df.drop_duplicates(subset=['admin'])
        
        return centroids_df
    
    def process_program_data(self, dt: pd.DataFrame) -> pd.DataFrame:
        """Process program data and calculate statistics"""
        dt = dt.drop_duplicates()
        
        # Calculate program statistics per country
        program_stats = dt.groupby('country').agg({
            'program': ['count', lambda x: ', '.join(sorted(x.unique()))]
        }).reset_index()
        
        program_stats.columns = ['country', 'n_programs', 'all_programs']
        dt_final = dt.merge(program_stats, on='country')
        
        return dt_final
    
    def create_country_program_details(self, dt: pd.DataFrame) -> pd.DataFrame:
        """Create detailed program information for each country"""
        country_details = []
        
        for country in dt['country'].unique():
            country_data = dt[dt['country'] == country]
            programs = sorted(country_data['program'].unique())
            
            # Create beautifully formatted program list
            program_list = []
            for program in programs:
                color = self.get_program_color(program)
                program_list.append(
                    f'<span style="color: {color}; font-weight: 600; '
                    f'text-shadow: 0 1px 2px rgba(0,0,0,0.1);">● {program}</span>'
                )
            
            program_details = '<br/>'.join(program_list)
            
            country_details.append({
                'country': country,
                'program_count': len(programs),
                'program_details': program_details,
                'all_programs': ', '.join(programs)
            })
        
        return pd.DataFrame(country_details)
    
    def get_program_color(self, program: str) -> str:
        """Get sophisticated color palette for each program"""
        colors = {
            'STAR': '#3b82f6',      # Blue - Innovation
            'NATIONS': '#f59e0b',   # Amber - Collaboration  
            'BIG': '#10b981',       # Emerald - Growth
            'EXCL': '#ef4444'       # Red - Excellence
        }
        return colors.get(program.upper(), '#6b7280')
    
    def get_country_fill_color(self, program_count: int) -> str:
        """Get sophisticated fill color based on program count"""
        if program_count >= 3:
            return '#059669'  # Dark emerald for high participation
        elif program_count == 2:
            return '#10b981'  # Medium emerald
        else:
            return '#34d399'  # Light emerald for single program
    
    def create_advanced_map(self, world: gpd.GeoDataFrame, dt: pd.DataFrame, centroids_df: pd.DataFrame) -> folium.Map:
        """Create the sophisticated folium map"""
        print("🎨 Creating sophisticated map...")
        
        # Merge data with centroids
        dt = dt.merge(centroids_df, left_on='country', right_on='admin', how='left')
        
        # Check for countries without coordinates
        missing_coords = dt[dt['longitude'].isna()]
        if not missing_coords.empty:
            print(f"⚠️  Missing coordinates for: {missing_coords['country'].unique()}")
            dt = dt.dropna(subset=['longitude', 'latitude'])
        
        # Process program countries with detailed info
        country_program_details = self.create_country_program_details(dt)
        
        # Separate program and non-program countries
        program_countries = world[world['shapeName'].isin(dt['country'])].copy()
        other_countries = world[~world['shapeName'].isin(dt['country'])].copy()
        
        # Exclude small territories and disputed areas
        exclude_list = [
            'Dragonja', 'Vatican City', 'Liancourt Rocks', 'Spratly Is', 
            'Antarctica', 'Paracel Is', 'Scarborough Reef'
        ]
        other_countries = other_countries[~other_countries['shapeName'].isin(exclude_list)]
        
        # Merge program details
        program_countries = program_countries.merge(
            country_program_details, left_on='shapeName', right_on='country', how='left'
        )
        
        print(f"✨ Found {len(program_countries)} program countries")
        print(f"🌐 Found {len(other_countries)} reference countries")
        
        # Create sophisticated base map
        m = folium.Map(
            location=[10, 0],  # Slightly south of equator to better center Global South
            zoom_start=3,      # More zoomed in for better initial view
            tiles=None,
            prefer_canvas=True,
            world_copy_jump=False,
            no_wrap=True,
            max_bounds=True,
            min_zoom=1,
            max_zoom=8,
            zoom_control=True,
            scroll_wheel_zoom=True,
            double_click_zoom=True,
            dragging=True,
            touch_zoom=True,
            keyboard=True,
            box_zoom=True
        )
        
        # Add sophisticated CSS styling
        self.add_advanced_styling(m)
        
        # Add high-quality base tiles
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            attr='Esri, HERE, Garmin, FAO, NOAA, USGS',
            name='Light Gray Canvas',
            control=False,
            overlay=False,
            no_wrap=True
        ).add_to(m)
        
        # Add reference countries with very subtle background styling
        if len(other_countries) > 0:
            print("Adding reference countries...")
            reference_layer = folium.GeoJson(
                other_countries,
                style_function=lambda feature: {
                    'fillColor': '#f8fafc',    # Very light background
                    'color': '#e2e8f0',        # Very subtle border
                    'weight': 0.3,             # Thin border
                    'fillOpacity': 0.25,       # Very transparent
                    'stroke': True,
                    'opacity': 0.4             # Very subtle border
                },
                name='Reference Countries'
            )
            reference_layer.add_to(m)
            print(f"✅ Added {len(other_countries)} reference countries")
        
        # Add program countries with SOPHISTICATED NAVY/SLATE HIGHLIGHTING - ALWAYS VISIBLE
        if len(program_countries) > 0:
            print("Adding SOPHISTICATED program countries...")
            
            # Create separate layers for different program levels with SOPHISTICATED COLORS
            high_participation = program_countries[program_countries['program_count'] >= 3]
            medium_participation = program_countries[program_countries['program_count'] == 2] 
            single_participation = program_countries[program_countries['program_count'] == 1]
            
            # Add high participation countries (DEEP NAVY - ALWAYS VISIBLE)
            if len(high_participation) > 0:
                folium.GeoJson(
                    high_participation,
                    style_function=lambda feature: {
                        'fillColor': '#1e293b',    # DEEP SLATE - ALWAYS VISIBLE
                        'color': '#f1f5f9',        # LIGHT BORDER 
                        'weight': 2.5,             # VISIBLE BORDER
                        'fillOpacity': 0.9,        # ALWAYS VISIBLE
                        'stroke': True,
                        'opacity': 1.0             # ALWAYS VISIBLE BORDER
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['shapeName', 'program_count', 'program_details'],
                        aliases=['Country:', 'Programs:', 'Details:'],
                        style="background: linear-gradient(135deg, #1e293b, #334155); color: white; border: none; border-radius: 12px; padding: 20px; font-weight: 600; box-shadow: 0 10px 25px rgba(0,0,0,0.3);",
                        sticky=False,
                        labels=True
                    ),
                    name='High Participation Countries'
                ).add_to(m)
                print(f"🔷 Added {len(high_participation)} HIGH PARTICIPATION countries - ALWAYS VISIBLE")
            
            # Add medium participation countries (SLATE BLUE - ALWAYS VISIBLE)
            if len(medium_participation) > 0:
                folium.GeoJson(
                    medium_participation,
                    style_function=lambda feature: {
                        'fillColor': '#334155',    # SLATE BLUE - ALWAYS VISIBLE
                        'color': '#f1f5f9',        # LIGHT BORDER 
                        'weight': 2,               # VISIBLE BORDER
                        'fillOpacity': 0.85,       # ALWAYS VISIBLE
                        'stroke': True,
                        'opacity': 1.0             # ALWAYS VISIBLE BORDER
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['shapeName', 'program_count', 'program_details'],
                        aliases=['Country:', 'Programs:', 'Details:'],
                        style="background: linear-gradient(135deg, #334155, #475569); color: white; border: none; border-radius: 12px; padding: 20px; font-weight: 600; box-shadow: 0 10px 25px rgba(0,0,0,0.3);",
                        sticky=False,
                        labels=True
                    ),
                    name='Medium Participation Countries'
                ).add_to(m)
                print(f"🔷 Added {len(medium_participation)} MEDIUM PARTICIPATION countries - ALWAYS VISIBLE")
            
            # Add single participation countries (SLATE - ALWAYS VISIBLE)
            if len(single_participation) > 0:
                folium.GeoJson(
                    single_participation,
                    style_function=lambda feature: {
                        'fillColor': '#475569',    # SLATE - ALWAYS VISIBLE
                        'color': '#f1f5f9',        # LIGHT BORDER 
                        'weight': 2,               # VISIBLE BORDER
                        'fillOpacity': 0.8,        # ALWAYS VISIBLE
                        'stroke': True,
                        'opacity': 1.0             # ALWAYS VISIBLE BORDER
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['shapeName', 'program_count', 'program_details'],
                        aliases=['Country:', 'Programs:', 'Details:'],
                        style="background: linear-gradient(135deg, #475569, #64748b); color: white; border: none; border-radius: 12px; padding: 20px; font-weight: 600; box-shadow: 0 10px 25px rgba(0,0,0,0.3);",
                        sticky=False,
                        labels=True
                    ),
                    name='Single Participation Countries'
                ).add_to(m)
                print(f"🔷 Added {len(single_participation)} SINGLE PARTICIPATION countries - ALWAYS VISIBLE")
            
            print(f"✨ Total SOPHISTICATED program countries: {len(program_countries)} - ALL ALWAYS VISIBLE")
        else:
            print("❌ No program countries found!")
        
        # Add interactive elements
        self.add_click_functionality(m)
        
        # Add sophisticated legend
        self.add_sophisticated_legend(m)
        
        # Add program statistics overlay
        self.add_statistics_overlay(m, dt)
        
        return m
    
    def add_advanced_styling(self, map_obj: folium.Map):
        """Add advanced CSS styling"""
        advanced_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: 'Inter', system-ui, sans-serif;
        }
        
        .folium-map {
            width: 100vw;
            height: 100vh;
            margin: 0;
            padding: 0;
        }
        
        .leaflet-container {
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            font-family: 'Inter', system-ui, sans-serif;
        }
        
        /* REMOVE ALL CSS HOVER EFFECTS - WILL USE JAVASCRIPT INSTEAD */
        .leaflet-interactive {
            cursor: pointer !important;
            transition: filter 0.2s ease, box-shadow 0.2s ease !important;
        }
        
        .leaflet-tooltip {
            animation: fadeInUp 0.3s ease-out;
            background: rgba(255, 255, 255, 0.98) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(30, 41, 59, 0.1) !important;
            border-radius: 12px !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
            font-family: 'Inter', system-ui, sans-serif !important;
            font-weight: 600 !important;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translate3d(0, 10px, 0);
            }
            to {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }
        }
        
        .leaflet-control-zoom {
            border: none !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12) !important;
        }
        
        .leaflet-control-zoom a {
            background: rgba(255,255,255,0.95) !important;
            color: #374151 !important;
            border: none !important;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            transition: all 0.2s ease !important;
        }
        
        .leaflet-control-zoom a:hover {
            background: white !important;
            transform: scale(1.05);
        }
        </style>
        """
        map_obj.get_root().html.add_child(folium.Element(advanced_css))
    
    def add_click_functionality(self, map_obj: folium.Map):
        """Add sophisticated click functionality and individual hover effects"""
        click_js = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                const countryElements = document.querySelectorAll('.leaflet-interactive');
                
                countryElements.forEach(function(element) {
                    // Store original style
                    const originalFilter = element.style.filter || '';
                    const originalBoxShadow = element.style.boxShadow || '';
                    
                    // Add individual hover effects
                    element.addEventListener('mouseenter', function(e) {
                        // Only affect this specific element
                        this.style.filter = 'brightness(1.2) saturate(1.3)';
                        this.style.boxShadow = 'inset 0 0 0 2px rgba(255, 255, 255, 0.8)';
                    });
                    
                    element.addEventListener('mouseleave', function(e) {
                        // Reset only this specific element
                        this.style.filter = originalFilter;
                        this.style.boxShadow = originalBoxShadow;
                    });
                    
                    // Add click functionality
                    element.addEventListener('click', function(e) {
                        e.stopPropagation();
                        
                        // Add click animation to this element only
                        this.style.transform = 'scale(0.98)';
                        setTimeout(() => {
                            this.style.transform = 'scale(1.02)';
                        }, 100);
                        setTimeout(() => {
                            this.style.transform = 'scale(1)';
                        }, 200);
                        
                        // Open in new tab
                        window.open('https://globtalent.org', '_blank');
                    });
                    
                    element.style.cursor = 'pointer';
                });
            }, 1000);
        });
        </script>
        """
        map_obj.get_root().html.add_child(folium.Element(click_js))
    
    def add_sophisticated_legend(self, map_obj: folium.Map):
        """Add sophisticated legend with program details"""
        legend_html = '''
        <div style="position: fixed; top: 20px; right: 20px; width: 280px; 
                    background: rgba(255,255,255,0.98); 
                    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    z-index: 9999; padding: 24px; border-radius: 16px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.08), 0 0 0 1px rgba(255,255,255,0.5);
                    font-family: 'Inter', system-ui, sans-serif;">
            
            <!-- Header -->
            <div style="margin-bottom: 20px; text-align: center;">
                <div style="font-size: 18px; font-weight: 700; color: #1f2937; margin-bottom: 4px;">
                    💎 Global Talent Map
                </div>
                <div style="font-size: 13px; color: #6b7280; font-weight: 500;">
                    Robinson Projection • Sophisticated Design
                </div>
            </div>
            
            <!-- Program Participation Levels -->
            <div style="margin-bottom: 20px;">
                <div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 12px;">
                    Program Participation
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 20px; height: 14px; background: #1e293b; 
                               border: 2px solid #f1f5f9; border-radius: 4px; margin-right: 10px; 
                               box-shadow: 0 2px 8px rgba(30, 41, 59, 0.4);"></div>
                    <span style="font-size: 13px; color: #374151; font-weight: 600;">
                        3+ Programs (ELITE PARTICIPATION) 💎
                    </span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 20px; height: 14px; background: #334155; 
                               border: 2px solid #f1f5f9; border-radius: 4px; margin-right: 10px;
                               box-shadow: 0 2px 8px rgba(51, 65, 85, 0.4);"></div>
                    <span style="font-size: 13px; color: #374151; font-weight: 600;">
                        2 Programs (HIGH PARTICIPATION) 🔷
                    </span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 20px; height: 14px; background: #475569; 
                               border: 2px solid #f1f5f9; border-radius: 4px; margin-right: 10px;
                               box-shadow: 0 2px 8px rgba(71, 85, 105, 0.4);"></div>
                    <span style="font-size: 13px; color: #374151; font-weight: 600;">
                        1 Program (ACTIVE PARTICIPATION) 🔹
                    </span>
                </div>
                
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 14px; background: #f8fafc; 
                               border: 1px solid #e2e8f0; border-radius: 4px; margin-right: 10px;"></div>
                    <span style="font-size: 13px; color: #6b7280; font-weight: 500;">
                        No Programs
                    </span>
                </div>
            </div>
            
            <!-- Program Types -->
            <div style="margin-bottom: 16px;">
                <div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 12px;">
                    Program Types
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 12px; height: 12px; background: #3b82f6; 
                               border-radius: 50%; margin-right: 8px;
                               box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);"></div>
                    <span style="font-size: 12px; color: #374151; font-weight: 500;">STAR</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 12px; height: 12px; background: #f59e0b; 
                               border-radius: 50%; margin-right: 8px;
                               box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);"></div>
                    <span style="font-size: 12px; color: #374151; font-weight: 500;">NATIONS</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 12px; height: 12px; background: #10b981; 
                               border-radius: 50%; margin-right: 8px;
                               box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);"></div>
                    <span style="font-size: 12px; color: #374151; font-weight: 500;">BIG</span>
                </div>
                
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background: #ef4444; 
                               border-radius: 50%; margin-right: 8px;
                               box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);"></div>
                    <span style="font-size: 12px; color: #374151; font-weight: 500;">EXCL</span>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; padding-top: 16px; border-top: 1px solid #f3f4f6;">
                <div style="font-size: 11px; color: #9ca3af; font-weight: 500;">
                    Click any program country to learn more
                </div>
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def add_statistics_overlay(self, map_obj: folium.Map, dt: pd.DataFrame):
        """Add statistics overlay"""
        total_countries = len(dt['country'].unique())
        total_programs = len(dt)
        
        stats_html = f'''
        <div style="position: fixed; bottom: 20px; left: 20px; 
                    background: rgba(255,255,255,0.95); 
                    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    z-index: 9999; padding: 16px 20px; border-radius: 12px; 
                    box-shadow: 0 12px 24px rgba(0,0,0,0.08);
                    font-family: 'Inter', system-ui, sans-serif;">
            
            <div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">
                📊 Program Statistics
            </div>
            
            <div style="display: flex; gap: 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #059669;">
                        {total_countries}
                    </div>
                    <div style="font-size: 11px; color: #6b7280; font-weight: 500;">
                        Countries
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #3b82f6;">
                        {total_programs}
                    </div>
                    <div style="font-size: 11px; color: #6b7280; font-weight: 500;">
                        Programs
                    </div>
                </div>
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(stats_html))
    
    def generate_map(self, output_file: str = "advanced_map.html"):
        """Main function to generate the sophisticated map"""
        try:
            print("🚀 Starting Advanced Global Talent Map Generation")
            print("=" * 55)
            
            # Load all data
            world, centroids_df = self.load_world_data()
            dt = self.load_excel_data()
            
            # Process data
            dt = self.standardize_country_names(dt)
            centroids_df = self.standardize_admin_names(centroids_df)
            dt = self.process_program_data(dt)
            
            # Create and save map
            map_obj = self.create_advanced_map(world, dt, centroids_df)
            map_obj.save(output_file)
            
            print("\n" + "=" * 55)
            print(f"✅ Sophisticated map successfully saved to {output_file}")
            print(f"🌍 Featured {len(dt['country'].unique())} countries")
            print(f"🎯 Total {len(dt)} program entries")
            print(f"🗺️  Using Robinson projection for fair global representation")
            print("=" * 55)
            
            return map_obj
            
        except Exception as e:
            print(f"❌ Error generating sophisticated map: {e}")
            raise

def main():
    """Main entry point"""
    print("🌍 Advanced Global Talent Map Generator")
    print("Robinson Projection • Fair Global Representation")
    print("=" * 55)
    
    mapper = AdvancedGlobalTalentMap()
    mapper.generate_map()

if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                             