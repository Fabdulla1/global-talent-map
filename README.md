# Global Talent Map - Python Version

This is a Python conversion of the original R-based Global Talent Fund interactive world map. The map displays countries participating in different Global Talent Fund programs with colored markers.

## Features

- Interactive world map using Folium (Python's equivalent to R's Leaflet)
- Color-coded markers for different programs (STAR, NATIONS, BIG, EXCL)
- Hover tooltips showing country names and programs
- Automatic handling of multiple programs per country with offset markers
- Custom legend and styling

## Requirements

- Python 3.8 or higher
- Internet connection (for downloading world boundary data)

## Quick Start

### 1. Install Dependencies

Run the setup script to install all required packages:

```bash
python setup.py
```

Or install manually:

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data

Ensure you have the `input_data.xlsx` file in the same directory. This should be an Excel file with:
- Columns representing different programs (STAR, NATIONS, BIG, EXCL)
- Rows containing country names for each program
- Country names should match standard geographic naming conventions

### 3. Generate the Map

Run the simple version (recommended):

```bash
python run_simple.py
```

Or the advanced version:

```bash
python run.py
```

### 4. View the Map

Open the generated `index_python.html` file in your web browser to view the interactive map.

## File Structure

```
├── run_simple.py          # Main Python script (recommended)
├── run.py                 # Alternative Python script  
├── setup.py               # Setup script for dependencies
├── requirements.txt       # Python package requirements
├── input_data.xlsx        # Your data file (required)
├── README_Python.md       # This file
└── index_python.html      # Generated map (after running script)
```

## Key Differences from R Version

### Libraries Used:
- **Folium** instead of Leaflet (for interactive maps)
- **Pandas** instead of data.table (for data manipulation)
- **GeoPandas** instead of sf (for geographic data)
- **Requests** for downloading geographic boundaries

### Features:
- Uses circle markers instead of custom SVG icons (simpler but equally effective)
- Automatic data downloading and caching
- Better error handling and user feedback
- More modular, object-oriented code structure

### Output:
- Generates `index_python.html` instead of `index.html`
- Similar visual appearance and functionality
- Works in any modern web browser

## Programs Supported

The map supports visualization of four Global Talent Fund programs:

- **STAR** (Blue markers)
- **NATIONS** (Orange markers)  
- **BIG** (Green markers)
- **EXCL** (Red markers)

Countries participating in multiple programs will have multiple markers positioned around the country centroid.

## Troubleshooting

### Common Issues:

1. **Missing packages**: Run `python setup.py` to install dependencies
2. **Excel file not found**: Ensure `input_data.xlsx` is in the same directory
3. **Country names not matching**: Check the console output for countries that couldn't be matched with geographic data
4. **Internet connection required**: The script downloads world boundary data on first run

### Error Messages:

- "input_data.xlsx not found!" - Place your Excel file in the script directory
- "Missing coordinates for countries" - Some country names in your data don't match the geographic database
- Download errors - Check your internet connection

## Customization

You can customize the map by modifying `run_simple.py`:

- Change marker colors in the `get_program_color()` method
- Adjust marker positioning in the `add_program_marker()` method  
- Modify the legend in the `add_legend()` method
- Change map styling in the `create_folium_map()` method

## Performance Notes

- The script downloads ~50MB of world boundary data on first run
- Geographic data is simplified for better performance
- Generated HTML file is typically 5-10MB

## License

This Python conversion maintains the same license as the original R project.
