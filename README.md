# 🌍 Global Talent Map

An interactive world map visualization displaying countries participating in Global Talent Fund programs. Built with OpenLayers and modern web technologies.

![Global Talent Map Preview](https://img.shields.io/badge/Interactive-Map-brightgreen)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![OpenLayers](https://img.shields.io/badge/OpenLayers-1F6B75?logo=openlayers&logoColor=white)

## ✨ Features

### 🗺️ Interactive Map Visualization
- **World Map Projection**: Robinson projection (Winkel Tripel fallback) for accurate global representation
- **Color-Coded Countries**: Visual hierarchy showing program participation levels
  - 🖤 **Elite (3+ programs)**: Dark navy
  - 🔵 **High (2 programs)**: Blue
  - 🔷 **Active (1 program)**: Light blue
- **Responsive Design**: Optimized for desktop and mobile viewing

### 🎯 Interactive Features
- **Hover Tooltips**: Rich information display showing:
  - Country name and participation level
  - Program badges (STAR, NATIONS, BIG, EXCL)
  - BIG Scholars by year with individual names
- **Click Navigation**: Direct links to country collection pages
- **Zoom Controls**: Constrained zoom levels for optimal viewing
- **Legend Panel**: Toggleable statistics and program information

### 📊 Data Display
- **82 Countries** across all programs
- **135 Total Program Participations**
- **BIG Scholars Database**: Individual scholar tracking by year (2024, 2025)
- **Program Categories**:
  - **STAR**: Scholarship and Talent programs
  - **NATIONS**: National talent initiatives
  - **BIG**: BIG Scholars program with detailed tracking
  - **EXCL**: Excellence programs

## 🚀 Quick Start

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for CDN dependencies and map data)
- Python 3.x (for local server)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/global-talent-map.git
cd global-talent-map
```

### 2. Start Local Server
```bash
# Using Python 3
python -m http.server 8000

# Using Python 2 (fallback)
python -m SimpleHTTPServer 8000
```

### 3. Open in Browser
Navigate to: `http://localhost:8000/`

## 🏗️ Project Structure

```
global-talent-map/
├── index.html               # Main application file
├── requirements.txt          # Optional Python dependencies
├── README.md                # Project documentation
├── data/                    # Data directory
│   └── ne_countries_110m_simplified.geojson
├── BIG_scholars_2024_entry.csv     # Scholar data (2024)
├── Big_scholars_list_2025.csv      # Scholar data (2025)
├── input_data.xlsx          # Original data file
└── .gitignore              # Git ignore rules
```

## 🛠️ Technical Architecture

### Frontend Technologies
- **HTML5**: Semantic structure and modern web standards
- **CSS3**: Custom styling with CSS variables and responsive design
- **JavaScript ES6+**: Modern JavaScript features and async operations

### Dependencies (CDN)
- **OpenLayers 10.6.1**: Advanced web mapping library
- **proj4 2.9.0**: Coordinate projection transformations
- **Inter Font**: Modern typography via Google Fonts

### Data Sources
- **Country Boundaries**: Natural Earth 110m Admin 0 Countries (GitHub)
- **Program Data**: Embedded JavaScript object with country coordinates
- **Scholar Information**: Integrated BIG Scholars database by year

## 💻 Code Structure

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

## 🎨 Customization

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

## 📱 Browser Compatibility

| Browser | Minimum Version | Notes |
|---------|----------------|-------|
| Chrome  | 80+           | Full support |
| Firefox | 75+           | Full support |
| Safari  | 13+           | Full support |
| Edge    | 80+           | Full support |

## 🔧 Development

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check existing documentation
- Review browser console for debugging information

## 🙏 Acknowledgments

- **Natural Earth**: Country boundary data
- **OpenLayers**: Mapping library
- **Global Talent Fund**: Data and program information
- **BIG Scholars**: Individual scholar tracking