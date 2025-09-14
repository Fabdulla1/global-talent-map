# Contributing to Global Talent Map

Thank you for your interest in contributing to the Global Talent Map project! This document provides guidelines for contributing to this interactive visualization project.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/global-talent-map.git
   cd global-talent-map
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Start local development server**:
   ```bash
   python -m http.server 8000
   ```
5. **Open** `http://localhost:8000/leaflet_map.html` to test your changes

## 🎯 Types of Contributions

### Data Updates
- **New Countries**: Add countries to existing programs
- **Scholar Information**: Update BIG Scholars database
- **Program Changes**: Modify country participation levels
- **Coordinate Corrections**: Fix country positioning

### Features
- **UI Improvements**: Enhance user interface elements
- **Interactive Features**: Add new map interactions
- **Performance**: Optimize rendering and data loading
- **Accessibility**: Improve screen reader and keyboard navigation support

### Bug Fixes
- **Cross-browser Issues**: Fix compatibility problems
- **Visual Glitches**: Correct styling or layout issues
- **Data Inconsistencies**: Fix program or scholar information

### Documentation
- **Code Documentation**: Improve inline comments
- **User Guides**: Enhance README or create tutorials
- **Developer Docs**: Document architecture and APIs

## 📝 Development Guidelines

### Code Style
- **HTML**: Use semantic HTML5 elements
- **CSS**: Follow BEM methodology for class naming
- **JavaScript**: Use ES6+ features, prefer const/let over var
- **Indentation**: 2 spaces for HTML/CSS, 2 spaces for JavaScript
- **Comments**: Document complex logic and data structures

### Testing Your Changes
1. **Visual Testing**: Check appearance in multiple browsers
2. **Interaction Testing**: Verify hover, click, and zoom behaviors
3. **Responsive Testing**: Test on different screen sizes
4. **Performance**: Ensure smooth interactions with large datasets

### Data Format Guidelines

#### Adding Countries
```javascript
"Country Name": {
  programs: ["STAR", "NATIONS", "BIG", "EXCL"], // Array of program codes
  lat: 12.3456,     // Decimal latitude
  lng: -98.7654,    // Decimal longitude
  bigScholars: {    // Optional: BIG scholars by year
    "2024": ["Scholar Name 1", "Scholar Name 2"],
    "2025": ["Scholar Name 3"]
  }
}
```

#### URL Mapping
```javascript
"Country Name": "https://global-talent-fund.webflow.io/country-collection/country-slug"
```

## 🔍 Pull Request Process

### Before Submitting
- [ ] Test changes in multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Verify responsive design on mobile and desktop
- [ ] Check console for JavaScript errors
- [ ] Ensure hover tooltips and click navigation work correctly
- [ ] Validate HTML and CSS if possible

### Pull Request Description
Include:
1. **Summary**: Brief description of changes
2. **Type**: Bug fix, feature, documentation, etc.
3. **Testing**: How you tested the changes
4. **Screenshots**: Before/after images for visual changes
5. **Breaking Changes**: Any backward compatibility issues

### Example PR Template
```markdown
## Summary
Added support for new "RESEARCH" program type with purple color coding.

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- Tested in Chrome, Firefox, and Safari
- Verified responsive design on mobile
- Confirmed hover tooltips display new program type
- Added test countries with RESEARCH program

## Screenshots
[Include before/after screenshots if applicable]

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review of code completed
- [x] Changes tested across browsers
- [x] Documentation updated if needed
```

## 🌐 Data Sources and Standards

### Country Names
Use standard country names from Natural Earth data:
- "United States" not "USA"
- "United Kingdom" not "UK"
- Check existing data for proper naming conventions

### Coordinates
- Use decimal degrees format
- Latitude: -90 to +90 (negative = South)
- Longitude: -180 to +180 (negative = West)
- Verify coordinates using online tools

### Program Codes
Current valid program codes:
- `STAR`: Scholarship and Talent programs
- `NATIONS`: National talent initiatives  
- `BIG`: BIG Scholars program
- `EXCL`: Excellence programs

## 🐛 Reporting Issues

### Bug Reports
Include:
- **Browser**: Version and operating system
- **Steps to reproduce**: Detailed reproduction steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Screenshots**: Visual evidence if applicable
- **Console errors**: Any JavaScript errors from browser console

### Feature Requests
Include:
- **Use case**: Why this feature would be valuable
- **Proposed solution**: How you envision it working
- **Alternatives**: Other approaches considered
- **Impact**: Who would benefit from this feature

## 📊 Data Privacy and Security

### Sensitive Information
- Do not include personal contact information for scholars
- Verify permission before adding detailed biographical data
- Follow data protection guidelines for participant information

### External Links
- Verify all country website URLs are official government sites
- Check for HTTPS where available
- Ensure links are appropriate and safe

## 🤝 Community Guidelines

### Communication
- Be respectful and constructive in all interactions
- Provide clear, detailed feedback on contributions
- Help newcomers understand the project structure
- Share knowledge and best practices

### Collaboration
- Coordinate on large changes through issues first
- Break large features into smaller, reviewable chunks
- Document decisions and architectural choices
- Consider backward compatibility in changes

## 📚 Resources

### Development Tools
- **Browser Dev Tools**: For debugging and testing
- **Lighthouse**: For performance auditing
- **WAVE**: For accessibility testing
- **Can I Use**: For browser compatibility checking

### External Documentation
- [OpenLayers Documentation](https://openlayers.org/en/latest/doc/)
- [MDN Web Docs](https://developer.mozilla.org/): HTML, CSS, JavaScript reference
- [Natural Earth Data](https://www.naturalearthdata.com/): Geographic data source

### Project-Specific
- Review existing code in `leaflet_map.html`
- Check `programData` object for data structure examples
- Examine CSS variables in `:root` for styling constants

## 📋 Release Process

For maintainers:
1. **Version Planning**: Discuss major changes in issues
2. **Testing**: Comprehensive testing across browsers and devices  
3. **Documentation**: Update README and inline documentation
4. **Tagging**: Use semantic versioning for releases
5. **Deployment**: Ensure GitHub Pages or hosting is updated

## ❓ Questions?

- **General Questions**: Open a GitHub issue with the "question" label
- **Development Help**: Check existing issues or create a new one
- **Data Questions**: Review the data format guidelines above

Thank you for contributing to the Global Talent Map! 🗺️✨