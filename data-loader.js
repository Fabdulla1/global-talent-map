// Excel Data Loader for Global Talent Map
// This script converts your Excel data into the format needed for the interactive map

class ExcelDataLoader {
    constructor() {
        this.programData = {};
        this.countryStats = {};
    }
    
    // Simulate loading Excel data (replace with actual Excel reading logic)
    async loadExcelData() {
        // This would normally use a library like SheetJS to read the Excel file
        // For now, we'll simulate the data structure from your input_data.xlsx
        
        const excelData = {
            'STAR': ['United States', 'Canada', 'United Kingdom', 'Germany', 'India', 'Japan', 'Australia', 'Kenya', 'Argentina', 'Egypt'],
            'NATIONS': ['United States', 'Canada', 'Germany', 'France', 'Japan', 'Australia', 'South Africa', 'Russia', 'Colombia', 'Kazakhstan'],
            'BIG students': ['United States', 'Brazil', 'India', 'China', 'Nigeria', 'Mexico', 'Egypt'], // Note: 'BIG students' from Excel
            'EXCL': ['United Kingdom', 'Germany', 'Italy', 'Russia']
        };
        
        return excelData;
    }
    
    // Process Excel data into program participation format
    processData(excelData) {
        const programData = {};
        
        // Process each program column
        Object.keys(excelData).forEach(program => {
            const normalizedProgram = program.toUpperCase().replace(' STUDENTS', '');
            
            excelData[program].forEach(country => {
                if (!programData[country]) {
                    programData[country] = [];
                }
                programData[country].push(normalizedProgram);
            });
        });
        
        this.programData = programData;
        return programData;
    }
    
    // Calculate statistics
    calculateStats() {
        const stats = {
            elite: 0,
            high: 0, 
            active: 0,
            none: 0,
            totalCountries: 0,
            totalPrograms: 0
        };
        
        Object.keys(this.programData).forEach(country => {
            const programs = this.programData[country];
            const level = this.getParticipationLevel(programs);
            
            stats[level]++;
            stats.totalPrograms += programs.length;
        });
        
        stats.totalCountries = Object.keys(this.programData).length;
        this.countryStats = stats;
        
        return stats;
    }
    
    getParticipationLevel(programs) {
        if (!programs || programs.length === 0) return 'none';
        if (programs.length >= 3) return 'elite';
        if (programs.length === 2) return 'high';
        return 'active';
    }
    
    // Export data for the map
    exportForMap() {
        return {
            programData: this.programData,
            stats: this.countryStats,
            programTypes: ['STAR', 'NATIONS', 'BIG', 'EXCL']
        };
    }
}

// Country coordinate mapping (simplified - in production you'd use a proper geo library)
const countryCoordinates = {
    'United States': { x: 200, y: 180 },
    'Canada': { x: 180, y: 140 },
    'Mexico': { x: 190, y: 240 },
    'Brazil': { x: 280, y: 320 },
    'Argentina': { x: 260, y: 380 },
    'Colombia': { x: 240, y: 280 },
    'United Kingdom': { x: 490, y: 170 },
    'France': { x: 510, y: 190 },
    'Germany': { x: 530, y: 180 },
    'Italy': { x: 540, y: 210 },
    'Russia': { x: 650, y: 160 },
    'Nigeria': { x: 520, y: 280 },
    'South Africa': { x: 540, y: 360 },
    'Kenya': { x: 580, y: 300 },
    'Egypt': { x: 550, y: 250 },
    'China': { x: 750, y: 220 },
    'India': { x: 700, y: 280 },
    'Japan': { x: 820, y: 240 },
    'Kazakhstan': { x: 680, y: 180 },
    'Australia': { x: 820, y: 370 },
    'New Zealand': { x: 860, y: 390 }
};

// Initialize data loading
async function initializeDataLoader() {
    const loader = new ExcelDataLoader();
    
    try {
        console.log('📊 Loading Excel data...');
        const excelData = await loader.loadExcelData();
        
        console.log('🔄 Processing program data...');
        const programData = loader.processData(excelData);
        
        console.log('📈 Calculating statistics...');
        const stats = loader.calculateStats();
        
        console.log('✅ Data loaded successfully!');
        console.log(`📍 ${stats.totalCountries} countries with ${stats.totalPrograms} total programs`);
        
        return loader.exportForMap();
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        throw error;
    }
}

// Export for use in the main map
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ExcelDataLoader, countryCoordinates, initializeDataLoader };
}
