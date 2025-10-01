#!/usr/bin/env python3
"""
Country Links Extractor

This script extracts country website links from the HTML file and creates a CSV
for non-technical users to manage country links. It also filters out non-globtalent.org links.
"""

import pandas as pd
import re
import json
from pathlib import Path

def extract_country_links_from_html():
    """Extract country website mappings from the HTML file"""
    html_file = Path("index.html")
    
    if not html_file.exists():
        print("Error: index.html not found")
        return {}
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the countryWebsites object
    start_marker = "const countryWebsites = {"
    end_marker = "};\n\n    /* Legend toggle */"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Error: Could not find countryWebsites section in HTML file")
        return {}
    
    # Extract the JavaScript object content
    js_section = content[start_idx + len(start_marker):end_idx].strip()
    
    country_links = {}
    
    # Split by lines and process each line
    lines = js_section.split('\n')
    current_country = None
    current_url = None
    
    for line in lines:
        line = line.strip()
        
        # Skip comments and empty lines
        if line.startswith('//') or not line:
            continue
            
        # Look for country-URL pairs
        if '"' in line and ':' in line and not line.startswith('//'):
            # Remove comments from the line
            if '//' in line:
                line = line[:line.find('//')]
            
            # Extract country and URL
            parts = line.split(':', 1)
            if len(parts) == 2:
                country_part = parts[0].strip().strip('"')
                url_part = parts[1].strip().rstrip(',').strip('"')
                
                if country_part and url_part.startswith('http'):
                    country_links[country_part] = url_part
    
    return country_links

def create_country_links_csv():
    """Create a CSV file for country links management"""
    print("🔗 Extracting country links from HTML...")
    
    # Extract links from HTML
    country_links = extract_country_links_from_html()
    
    if not country_links:
        print("❌ No country links found")
        return
    
    print(f"📊 Found {len(country_links)} country links")
    
    # Create a DataFrame with country information
    data = []
    
    for country, url in country_links.items():
        is_globtalent = "globtalent.org" in url
        status = "globtalent" if is_globtalent else "external"
        
        data.append({
            "Country": country,
            "Website_URL": url,
            "Link_Type": status,
            "Active": "Yes",
            "Notes": "" if is_globtalent else "Non-globtalent.org link - review needed"
        })
    
    # Sort by country name
    data.sort(key=lambda x: x["Country"])
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_file = Path("data/country_links.csv")
    df.to_csv(output_file, index=False)
    
    print(f"✅ Created {output_file}")
    print(f"📈 Total links: {len(df)}")
    print(f"🌐 Globtalent.org links: {len(df[df['Link_Type'] == 'globtalent'])}")
    print(f"🔗 External links: {len(df[df['Link_Type'] == 'external'])}")
    
    # Print external links for review
    external_links = df[df['Link_Type'] == 'external']
    if not external_links.empty:
        print("\n⚠️  External (non-globtalent.org) links found:")
        for _, row in external_links.iterrows():
            print(f"   {row['Country']}: {row['Website_URL']}")
    
    return df

def update_html_to_load_csv():
    """Update HTML to load country links from CSV instead of hardcoded object"""
    html_file = Path("index.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the countryWebsites object
    start_marker = "const countryWebsites = {"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Error: Could not find countryWebsites in HTML file")
        return
    
    # Find the matching closing brace
    brace_count = 0
    i = start_idx + len(start_marker) - 1  # Start from the opening brace
    end_idx = -1
    
    for j in range(i, len(content)):
        if content[j] == '{':
            brace_count += 1
        elif content[j] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = j + 1
                break
    
    if end_idx == -1:
        print("Error: Could not find end of countryWebsites object")
        return
    
    # Replace the hardcoded object with CSV loading code
    replacement_code = """let countryWebsites = {};

    // Load country links from CSV
    fetch('data/country_links.csv')
      .then(response => response.text())
      .then(csv => {
        const lines = csv.split('\\n');
        const headers = lines[0].split(',');
        
        for (let i = 1; i < lines.length; i++) {
          if (lines[i].trim()) {
            const values = lines[i].split(',');
            const country = values[0].replace(/"/g, '');
            const url = values[1].replace(/"/g, '');
            const active = values[3].replace(/"/g, '');
            
            if (active === 'Yes') {
              countryWebsites[country] = url;
            }
          }
        }
        console.log('Loaded country links from CSV:', Object.keys(countryWebsites).length);
      })
      .catch(err => {
        console.warn('Failed to load country links CSV:', err);
        // Fallback to empty object
        countryWebsites = {};
      });"""
    
    # Replace in content
    new_content = content[:start_idx] + replacement_code + content[end_idx:]
    
    # Write back to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Updated HTML to load country links from CSV")

def main():
    """Main function"""
    print("🚀 Processing country links...")
    
    # Check if we're in the right directory
    if not Path("data").exists():
        print("Error: 'data' directory not found. Please run this script from the project root.")
        return
    
    try:
        # Create the CSV file
        df = create_country_links_csv()
        
        if df is not None:
            print("\n📝 CSV Structure:")
            print("   - Country: Country name")
            print("   - Website_URL: The website URL for the country")
            print("   - Link_Type: 'globtalent' or 'external'")
            print("   - Active: 'Yes' or 'No' (controls if link is used)")
            print("   - Notes: Additional information")
            
            print("\n📋 To update country links:")
            print("   1. Edit data/country_links.csv")
            print("   2. Change Website_URL to update links")
            print("   3. Set Active to 'No' to disable a country's link")
            print("   4. Save the file - changes will be reflected on the website")
            
        print("\n✨ Country links processing completed!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()