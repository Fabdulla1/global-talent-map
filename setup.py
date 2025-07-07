#!/usr/bin/env python3
"""
Setup script for Global Talent Map Python version
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Setting up Global Talent Map Python environment")
    print("=" * 50)
    
    # Required packages
    packages = [
        "folium>=0.14.0",
        "pandas>=1.5.0", 
        "geopandas>=0.13.0",
        "requests>=2.28.0",
        "numpy>=1.24.0",
        "shapely>=2.0.0",
        "openpyxl>=3.1.0"
    ]
    
    print("Installing required packages...")
    
    failed_packages = []
    for package in packages:
        print(f"  Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Some packages failed to install: {failed_packages}")
        print("You may need to install them manually or check your internet connection.")
    else:
        print("\n🎉 All packages installed successfully!")
        print("\nYou can now run the map generator with:")
        print("python run_simple.py")
    
    # Check if input file exists
    if not os.path.exists("input_data.xlsx"):
        print("\n⚠️  Warning: input_data.xlsx not found!")
        print("Make sure to place your Excel data file in this directory before running the script.")
    else:
        print("\n✅ input_data.xlsx found!")

if __name__ == "__main__":
    main()
