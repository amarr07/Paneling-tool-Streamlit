#!/bin/bash
# Launch script for Data Paneling Tool

echo "🚀 Launching Data Paneling Tool..."
echo ""
echo "Opening in your default browser..."
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
streamlit run main.py
