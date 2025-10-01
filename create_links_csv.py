#!/usr/bin/env python3
"""
Create Country Links CSV

This script creates a CSV file for managing country links, keeping only globtalent.org links
and setting up placeholders for non-technical users to add missing links.
"""

import pandas as pd
from pathlib import Path

# Manually extracted data from the HTML file, keeping only globtalent.org links
GLOBTALENT_LINKS = {
    "United Kingdom": "https://www.globtalent.org/country-collection/united-kingdom",
    "Australia": "https://www.globtalent.org/country-collection/australia", 
    "India": "https://www.globtalent.org/country-collection/india",
    "Romania": "https://www.globtalent.org/country-collection/romania",
    "Ukraine": "https://www.globtalent.org/country-collection/ukraine",
    "Germany": "https://www.globtalent.org/country-collection/germany",
    "Brazil": "https://www.globtalent.org/country-collection/brazil",
    "Mexico": "https://www.globtalent.org/country-collection/latin-america",
    "Argentina": "https://www.globtalent.org/country-collection/latin-america",
    "Colombia": "https://www.globtalent.org/country-collection/latin-america",
    "Chile": "https://www.globtalent.org/country-collection/latin-america",
    "Peru": "https://www.globtalent.org/country-collection/latin-america",
    "Bolivia": "https://www.globtalent.org/country-collection/latin-america",
    "El Salvador": "https://www.globtalent.org/country-collection/el-salvador",
    "Costa Rica": "https://www.globtalent.org/country-collection/costa-rica",
    "Guatemala": "https://www.globtalent.org/country-collection/latin-america",
    "Nicaragua": "https://www.globtalent.org/country-collection/latin-america",
    "Cuba": "https://www.globtalent.org/country-collection/latin-america",
    "Dominican Republic": "https://www.globtalent.org/country-collection/latin-america",
    "Philippines": "https://www.globtalent.org/country-collection/philippines",
    "Georgia": "https://www.globtalent.org/country-collection/georgia",
    "Mongolia": "https://www.globtalent.org/country-collection/mongolia",
    "Bhutan": "https://www.globtalent.org/country-collection/bhutan",
    "Rwanda": "https://www.globtalent.org/country-collection/rwanda",
    "Serbia": "https://www.globtalent.org/country-collection/serbia",
    "Bosnia and Herzegovina": "https://www.globtalent.org/country-collection/bosnia-and-herzegovina",
    "Bulgaria": "https://www.globtalent.org/country-collection/bulgaria",
    "Hungary": "https://www.globtalent.org/country-collection/hungary",
    "Turkey": "https://www.globtalent.org/country-collection/turkey"
}

# Countries that appear in the program data but don't have links yet
ALL_COUNTRIES = [
    "United States", "Canada", "Brazil", "United Kingdom", "Germany", "France", 
    "India", "China", "Japan", "Australia", "Nigeria", "South Africa", "Kenya", 
    "Italy", "Russia", "Mexico", "Argentina", "Colombia", "Egypt", "Kazakhstan", 
    "Bosnia and Herzegovina", "Romania", "Serbia", "Ukraine", "Mongolia", 
    "El Salvador", "Philippines", "Georgia", "Costa Rica", "Bhutan", "Rwanda", 
    "Bulgaria", "Hungary", "Turkey", "Indonesia", "Iran", "Belarus", "Greece", 
    "Poland", "Finland", "Singapore", "Cyprus", "Armenia", "North Macedonia", 
    "Netherlands", "Uzbekistan", "Albania", "Algeria", "Bangladesh", "Bolivia", 
    "Botswana", "Cameroon", "Chile", "Cuba", "Czech Republic", 
    "Democratic Republic of the Congo", "Dominican Republic", "Ethiopia", 
    "Guatemala", "Ivory Coast", "Jordan", "Kyrgyzstan", "Latvia", "Lesotho", 
    "Lithuania", "Malaysia", "Mauritania", "Montenegro", "Morocco", "Namibia", 
    "Nepal", "Nicaragua", "Pakistan", "Palestine", "Peru", "South Korea", 
    "South Sudan", "Spain", "Tanzania", "Thailand", "Tunisia", "Uganda", 
    "Vietnam", "Zimbabwe", "Taiwan", "Israel", "Croatia", "Slovenia", 
    "Saudi Arabia", "Moldova", "Azerbaijan", "Slovakia", "Estonia", "Iceland", 
    "Ireland", "Norway", "Sweden", "Denmark", "Belgium", "Luxembourg", 
    "Switzerland", "Austria", "Portugal", "American Samoa", "Eswatini"
]

def create_country_links_csv():
    """Create a CSV file for country links management"""
    print("🔗 Creating country links CSV...")
    
    data = []
    
    for country in sorted(ALL_COUNTRIES):
        if country in GLOBTALENT_LINKS:
            # Country has a globtalent.org link
            data.append({
                "Country": country,
                "Website_URL": GLOBTALENT_LINKS[country],
                "Link_Type": "globtalent",
                "Active": "Yes",
                "Notes": "Globtalent.org country collection page"
            })
        else:
            # Country needs a link to be added
            data.append({
                "Country": country,
                "Website_URL": "",
                "Link_Type": "pending",
                "Active": "No", 
                "Notes": "Please add globtalent.org link when available"
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_file = Path("data/country_links.csv")
    df.to_csv(output_file, index=False)
    
    print(f"✅ Created {output_file}")
    print(f"📈 Total countries: {len(df)}")
    print(f"🌐 Countries with globtalent.org links: {len(df[df['Link_Type'] == 'globtalent'])}")
    print(f"⏳ Countries pending links: {len(df[df['Link_Type'] == 'pending'])}")
    
    return df

def update_html_for_csv_loading():
    """Update HTML to load country links from CSV instead of hardcoded object"""
    html_file = Path("index.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the countryWebsites object and replace it
    start_marker = "    const countryWebsites = {"
    end_marker = "    };\n\n    /* Legend toggle */"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Error: Could not find countryWebsites section in HTML file")
        return
    
    # Create replacement code that loads from CSV
    replacement_code = """    let countryWebsites = {};

    // Load country links from CSV
    async function loadCountryLinks() {
      try {
        const response = await fetch('data/country_links.csv');
        const csvText = await response.text();
        const lines = csvText.split('\\n');
        
        // Skip header row
        for (let i = 1; i < lines.length; i++) {
          const line = lines[i].trim();
          if (line) {
            // Simple CSV parsing - assumes no commas in values
            const [country, url, linkType, active, notes] = line.split(',').map(s => s.replace(/"/g, ''));
            
            if (active === 'Yes' && url && url.startsWith('http')) {
              countryWebsites[country] = url;
            }
          }
        }
        console.log(`Loaded ${Object.keys(countryWebsites).length} country links from CSV`);
      } catch (err) {
        console.warn('Failed to load country links CSV:', err);
        // Fallback - keep some essential globtalent.org links
        countryWebsites = {
          "United Kingdom": "https://www.globtalent.org/country-collection/united-kingdom",
          "Australia": "https://www.globtalent.org/country-collection/australia",
          "India": "https://www.globtalent.org/country-collection/india",
          "Romania": "https://www.globtalent.org/country-collection/romania",
          "Ukraine": "https://www.globtalent.org/country-collection/ukraine",
          "Germany": "https://www.globtalent.org/country-collection/germany"
        };
      }
    }

    // Load links when page loads
    loadCountryLinks();"""

    # Replace in content
    new_content = content[:start_idx] + replacement_code + "\n\n    /* Legend toggle */" + content[end_idx + len(end_marker):]
    
    # Write back to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Updated HTML to load country links from CSV")

def main():
    """Main function"""
    print("🚀 Setting up country links management...")
    
    # Check if we're in the right directory
    if not Path("data").exists():
        print("Error: 'data' directory not found. Please run this script from the project root.")
        return
    
    try:
        # Create the CSV file
        df = create_country_links_csv()
        
        # Update HTML to use CSV
        update_html_for_csv_loading()
        
        print("\n📝 CSV Structure:")
        print("   - Country: Country name")
        print("   - Website_URL: The website URL for the country (globtalent.org preferred)")
        print("   - Link_Type: 'globtalent', 'external', or 'pending'")
        print("   - Active: 'Yes' or 'No' (controls if link is used)")
        print("   - Notes: Additional information")
        
        print("\n📋 To add/update country links:")
        print("   1. Open data/country_links.csv in Excel or any spreadsheet application")
        print("   2. For countries with empty Website_URL, add the appropriate globtalent.org link")
        print("   3. Set Active to 'Yes' to enable the link")
        print("   4. Save the file - changes will be reflected automatically on the website")
        
        print("\n⚠️  Important: Only globtalent.org links are retained. Non-globtalent.org links have been removed.")
        
        print("\n✨ Country links setup completed!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()