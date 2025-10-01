# Global Talent Map

An interactive world map visualization displaying countries participating in Global Talent Fund programs. Built with OpenLayers and modern web technologies.

![Global Talent Map Preview](https://img.shields.io/badge/Interactive-Map-brightgreen)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![OpenLayers](https://img.shields.io/badge/OpenLayers-1F6B75?logo=openlayers&logoColor=white)

## Features

### Interactive Map Visualization
- **World Map Projection**: Robinson projection (Winkel Tripel fallback) for accurate global representation
- **Color-Coded Countries**: Visual hierarchy showing program participation levels
  - **Elite (3+ programs)**: Dark navy
  - **High (2 programs)**: Blue
  - **Active (1 program)**: Light blue
- **Responsive Design**: Optimized for desktop and mobile viewing

### Interactive Features
- **Hover Tooltips**: Rich information display showing:
  - Country name and participation level
  - Program badges (STAR, NATIONS, BIG, EXCL)
  - BIG Scholars by year with individual names
- **Click Navigation**: Direct links to country collection pages
- **Zoom Controls**: Constrained zoom levels for optimal viewing
- **Legend Panel**: Toggleable statistics and program information

### Data Display
- **105 Countries** across all programs
- **Automated Data Processing**: Real-time updates from CSV files
- **BIG Scholars Database**: Individual scholar tracking by year (2024, 2025)
- **Program Categories**:
  - **STAR**: Scholarship and Talent programs
  - **NATIONS**: National talent initiatives
  - **BIG**: BIG Scholars program with detailed tracking
  - **EXCL**: Excellence programs

## For Non-Technical Users: How to Update Data

### Adding New BIG Scholars

#### Option 1: Update 2025 Scholars List
1. Open `data/Big_scholars_list_2025.csv` in Excel or any spreadsheet application
2. Add a new row with the scholar's information:
   - **Email**: Scholar's email address
   - **Name**: Full name of the scholar
   - **Country**: Country name (must match exactly with map)
   - **Gender**: M or F
   - Fill in other columns as appropriate
3. Save the file
4. Run the update script: 
   - **Windows**: Double-click `update_data.bat` or run `.\update_data.bat` in PowerShell
   - **Mac/Linux**: Run `./update_data.sh` in terminal
   - **Manual**: Run `python process_data.py`
5. Refresh your website to see the changes

#### Option 2: Add New Year's Data
1. Create a new CSV file: `data/BIG_scholars_[YEAR]_entry.csv`
2. Use the same format as `data/BIG_scholars_2024_entry.csv`:
   - **Country**: Country name
   - **Gender**: M or F  
   - **Name**: Scholar's full name
   - Other columns as needed
3. The script will automatically detect and process the new file
4. Run: `python process_data.py`

### Managing Country Website Links

#### Adding New Country Links
1. Open `data/country_links.csv` in Excel
2. Find the country you want to add a link for
3. In the **Website_URL** column, add the globtalent.org link:
   - Format: `https://www.globtalent.org/country-collection/[country-name]`
   - Example: `https://www.globtalent.org/country-collection/france`
4. Change **Active** from "No" to "Yes"
5. Update **Link_Type** to "globtalent"
6. Add any notes in the **Notes** column
7. Save the file - **changes will appear immediately when you refresh the website**

#### Important Notes:
- **Only use globtalent.org links** - external links are not supported
- **Match country names exactly** as they appear on the map
- **Set Active to "Yes"** for links to work
- **Save the CSV file** after making changes

## How Automatic Updates Work

The system has two different update mechanisms:

### 1. Country Links (Fully Automatic)
- **File**: `data/country_links.csv`
- **Update Method**: Automatic when page loads
- **How it works**: The website reads the CSV file every time someone visits the page
- **User Action**: Simply save the CSV file and refresh the browser
- **No scripts needed**: Changes are visible immediately

### 2. Scholar Data (Requires Script)
- **Files**: `data/BIG_scholars_*.csv` 
- **Update Method**: Manual script execution required
- **How it works**: Python script processes CSV files and updates the HTML file
- **User Action**: 
  1. Edit CSV files
  2. Run update script (`update_data.bat` or `python process_data.py`)
  3. Refresh browser

### Updating the Website

The update process depends on which type of data you're changing:

#### For Country Links (`country_links.csv`):
1. **Save the CSV file** in Excel or your spreadsheet application
2. **Refresh your browser** - changes appear immediately
3. **No additional steps needed**

#### For Scholar Data (`BIG_scholars_*.csv`):
1. **Save the CSV file** with your new scholar information
2. **Run the update script**:
   - **Windows**: Double-click `update_data.bat` or run `.\update_data.bat` in PowerShell
   - **Mac/Linux**: Run `./update_data.sh` in terminal  
   - **Manual**: Run `python process_data.py`
3. **Refresh your browser** to see the updated scholar information on the map

#### Technical Details:
- **Country links load dynamically** from CSV when the page opens
- **Scholar data is embedded** in the HTML file and requires script processing
- **Browser cache**: Use Ctrl+F5 (Windows) or Cmd+Shift+R (Mac) for hard refresh if changes don't appear

### Data File Structure

```
data/
├── BIG_scholars_2024_entry.csv     # 2024 BIG Scholars data
├── Big_scholars_list_2025.csv      # 2025 BIG Scholars data  
├── country_links.csv               # Country website links
└── input_data.xlsx                 # Excel backup/reference
```

### Important Guidelines

- **Backup First**: Always make a copy of data files before editing
- **Consistent Naming**: Use exact country names as they appear on the map
- **Globtalent Links Only**: Only globtalent.org links are supported for click navigation
- **Test Changes**: After updating, always test the website to ensure everything works
- **Excel Compatibility**: CSV files can be opened and edited in Excel, Google Sheets, or any spreadsheet application

## Quick Start

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for CDN dependencies and map data)
- Python 3.x (for data processing)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/global-talent-map.git
cd global-talent-map
```

### 2. Set Up Python Environment (for data processing)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install pandas openpyxl
```

### 3. Start Local Server
```bash
# Using Python 3
python -m http.server 8000

# Using Python 2 (fallback)
python -m SimpleHTTPServer 8000
```

### 4. Open in Browser
Navigate to: `http://localhost:8000/`

## For Developers: Technical Setup

### Automated Data Processing

The project includes automated scripts for processing scholar data and country links:

```bash
# Process CSV files and update website data
python process_data.py

# Create/update country links CSV (run once)
python create_links_csv.py
```

### Easy Update Scripts

For non-technical users, we've included simple scripts to update data:

**Windows users:**
```bash
# Double-click or run from PowerShell/Command Prompt
.\update_data.bat
```

**Mac/Linux users:**
```bash
# Run from terminal (make executable first if needed)
chmod +x update_data.sh
./update_data.sh
```

### Data Processing Pipeline

The system uses two different approaches for data updates:

#### 1. Runtime CSV Loading (Country Links)
- **File**: `data/country_links.csv`
- **Method**: JavaScript `fetch()` API loads CSV when page opens
- **Frequency**: Every page load/refresh
- **Code**: `loadCountryLinks()` function in `index.html`
- **Result**: Immediate updates without requiring scripts

#### 2. Build-Time Processing (Scholar Data)  
- **Files**: `data/BIG_scholars_*.csv`
- **Method**: Python script processes CSV and embeds data in HTML
- **Frequency**: Only when script is manually executed
- **Code**: `process_data.py` script
- **Result**: Requires script execution for updates

#### Technical Implementation:
```javascript
// Country links - loaded dynamically
async function loadCountryLinks() {
  const response = await fetch('data/country_links.csv');
  // Parse CSV and populate countryWebsites object
}

// Scholar data - embedded statically  
const programData = {
  "Country": {programs: [...], bigScholars: {...}}
  // Generated by Python script
};
```

## Project Structure

```
global-talent-map/
├── index.html                      # Main application file
├── process_data.py                 # Automated data processing script
├── create_links_csv.py            # Country links management script
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
├── data/                          # Data directory
│   ├── BIG_scholars_2024_entry.csv      # 2024 Scholar data
│   ├── Big_scholars_list_2025.csv       # 2025 Scholar data
│   ├── country_links.csv               # Country website links
│   ├── input_data.xlsx                 # Excel backup/reference
│   └── ne_countries_110m_simplified.geojson  # Map boundaries
└── .gitignore                     # Git ignore rules
```

## Technical Architecture

### Frontend Technologies
- **HTML5**: Semantic structure and modern web standards
- **CSS3**: Custom styling with CSS variables and responsive design
- **JavaScript ES6+**: Modern JavaScript features and async operations

### Data Management
- **CSV-Based**: All data stored in easily editable CSV files
- **Automated Processing**: Python scripts for data pipeline
- **Real-time Updates**: Changes reflected immediately on website
- **Non-technical Friendly**: Excel-compatible data files

### Dependencies (CDN)
- **OpenLayers 10.6.1**: Advanced web mapping library
- **proj4 2.9.0**: Coordinate projection transformations
- **Inter Font**: Modern typography via Google Fonts

### Data Sources
- **Country Boundaries**: Natural Earth 110m Admin 0 Countries (GitHub)
- **Program Data**: Embedded JavaScript object with country coordinates
- **Scholar Information**: Integrated BIG Scholars database by year

## Code Structure

### Main Components

#### 1. Data Layer (`programData`)
```javascript
const programData = {
  "Country Name": {
    programs: ["STAR", "NATIONS", "BIG", "EXCL"],
    lat: latitude,
    lng: longitude,
    bigScholars: {
      "2024": ["Scholar Name 1", "Scholar Name 2"],
      "2025": ["Scholar Name 3"]
    }
  }
}
```

#### 2. Visualization Layer
- **Map Projection**: Custom Robinson projection registration
- **Vector Layers**: Countries and program points
- **Styling**: Dynamic color coding based on participation level
- **Interactions**: Hover tooltips and click navigation

#### 3. User Interface
- **Legend Panel**: Collapsible statistics and program information
- **Hover System**: Rich tooltips with program and scholar details
- **Responsive Layout**: Mobile-optimized interface

### Key Functions

#### Map Initialization
```javascript
function initWintri() {
  // Projection setup
  // Layer creation
  // Map configuration
  // Event handlers
}
```

#### Feature Generation
```javascript
function programsToFeatures() {
  // Convert country data to map features
  // Apply color coding
  // Set participation levels
}
```

#### Interactive Events
- `pointermove`: Hover tooltip display
- `singleclick`: Country website navigation

## Customization

### Adding New Countries
1. Update `programData` object with country information:
```javascript
"New Country": {
  programs: ["STAR"], 
  lat: latitude, 
  lng: longitude
}
```

2. Add website URL to `countryWebsites` object:
```javascript
"New Country": "https://country-website.com"
```

### Modifying Visual Styling
- **Colors**: Update CSS variables in `:root`
- **Fonts**: Change Google Fonts import and font-family declarations
- **Layout**: Modify responsive breakpoints and component sizing

### Program Categories
Add new program types by:
1. Including in country `programs` arrays
2. Adding CSS styles for new program badges
3. Updating legend information

## Browser Compatibility

| Browser | Minimum Version | Notes |
|---------|----------------|-------|
| Chrome  | 80+           | Full support |
| Firefox | 75+           | Full support |
| Safari  | 13+           | Full support |
| Edge    | 80+           | Full support |

## Development

### Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd global-talent-map

# Start development server
python -m http.server 8000

# Optional: Install data processing dependencies
pip install -r requirements.txt
```

### Making Changes
1. Edit `index.html` for application changes
2. Test locally using the development server
3. Commit changes following conventional commit standards

### Data Updates
- **Scholar Information**: Update `bigScholars` objects in `programData`
- **New Programs**: Add to country `programs` arrays
- **Coordinates**: Verify using latitude/longitude standards

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For questions or issues:
- Open an issue on GitHub
- Check existing documentation
- Review browser console for debugging information

## Acknowledgments

- **Natural Earth**: Country boundary data
- **OpenLayers**: Mapping library
- **Global Talent Fund**: Data and program information
- **BIG Scholars**: Individual scholar tracking