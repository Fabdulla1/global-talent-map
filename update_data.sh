#!/bin/bash

echo "🚀 Global Talent Map - Data Processing"
echo "====================================="
echo

echo "Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing/updating dependencies..."
pip install pandas openpyxl --quiet

echo
echo "📊 Processing scholar data..."
python process_data.py

echo
echo "✨ Data processing completed!"
echo "The website has been updated with the latest data."
echo