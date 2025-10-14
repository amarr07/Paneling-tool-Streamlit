# Quick Start Guide - Data Paneling Tool

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Open Terminal and navigate to the project directory:**
   ```bash
   cd /Users/amartyaanand/Documents/inclusive/Panneling
   ```

2. **Install dependencies (already done if you see streamlit installed):**
   ```bash
   pip3 install -r requirements.txt
   ```

### Launch the Application

**Option 1: Using the launch script (Recommended)**
```bash
./run_app.sh
```

**Option 2: Direct command**
```bash
streamlit run src/main.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

## 📋 Step-by-Step Workflow

### Step 1: Upload Data
1. Click on **"1. Upload Data"** in the sidebar
2. Click **"Browse files"** or drag-and-drop your CSV/Excel file
3. Review the dataset overview and column information
4. Example file: Use `Bihar_panels.xlsx` to test

### Step 2: Configure Targets
1. Click on **"2. Configure Targets"** in the sidebar
2. Select columns to use for stratification (e.g., Gender, zone, 2020 AE, 2024 GE)
3. **OPTIONAL**: Choose which columns you want to set custom proportions for
   - You can leave this empty to use natural distributions for all columns
   - Or select only specific columns where you need custom proportions
4. For columns you selected for custom proportions:
   - Check **"Use current distribution"** to match existing proportions
   - Or manually enter target proportions for each category
5. Ensure proportions sum to 1.0 for each customized column
6. Click **"✓ Validate and Save Configuration"**

### Step 3: Create Panels
1. Click on **"3. Create Panels"** in the sidebar
2. Set the number of panels (e.g., 3)
3. Set the panel size (e.g., 1050 samples per panel)
4. Review the availability check
5. Set a random seed for reproducibility (e.g., 42)
6. Click **"🚀 Create Panels"**
7. Review detailed statistics for each panel

### Step 4: Split Panels
1. Click on **"4. Split Panels"** in the sidebar
2. Set a random seed for splitting
3. Click **"✂️ Split All Panels"**
4. Review the comparison between Set A and Set B for each panel

### Step 5: Validate & Export
1. Click on **"5. Validate & Export"** in the sidebar
2. Click **"Check for Overlaps"** to verify no overlap exists
3. Specify output directory (default: `./data`)
4. Click **"📥 Export All to CSV"** to save all files
5. Or use individual download buttons for specific files
6. Generate a summary report for documentation

## 📁 Output Files

Files are saved with clear naming:
- `panel_1_set_a.csv`
- `panel_1_set_b.csv`
- `panel_2_set_a.csv`
- `panel_2_set_b.csv`
- etc.

## 💡 Tips & Best Practices

### For Best Results:
1. **Use the example file first**: Test with `Bihar_panels.xlsx` to understand the workflow
2. **Start with current distributions**: Use the "Use current distribution" option initially
3. **Check availability warnings**: Pay attention to warnings about underrepresented categories
4. **Use consistent random seeds**: For reproducibility, use the same seed values

### Common Settings:
- **Survey Research**: 3 panels × 1000-1500 samples each
- **A/B Testing**: 2 panels × 500-2000 samples each
- **Multi-wave Studies**: 4-6 panels × 800-1200 samples each

## 🔍 Quality Checks

The tool automatically performs:
- ✓ Pre-creation availability checks
- ✓ Post-creation distribution validation
- ✓ Set balance verification
- ✓ Complete overlap detection
- ✓ Statistical summary reports

## 🛠️ Troubleshooting

### "Not enough samples" error
**Problem**: Dataset too small for requested panels
**Solution**: 
- Reduce panel size
- Reduce number of panels
- Check for missing data in stratification columns

### Target proportions don't sum to 1.0
**Problem**: Manual entry errors
**Solution**: 
- Use the "Use current distribution" option
- Double-check all proportion values
- Use decimals (e.g., 0.50, not 50%)

### Large deviations from targets
**Problem**: Some categories underrepresented in dataset
**Solution**: 
- Review availability warnings in Step 3
- Adjust targets to match available proportions
- Consider excluding rare categories

### Import errors
**Problem**: Missing dependencies
**Solution**: 
```bash
pip3 install -r requirements.txt
```

## 📊 Example: Bihar Panels

Using the included `Bihar_panels.xlsx`:

1. **Dataset**: 43,853 rows
2. **Stratification columns**: Gender, zone, 2020 AE, 2024 GE
3. **Recommended panels**: 3 panels × 3,150 samples each
4. **Result**: 6 balanced sets (3 × 2) with maintained distributions

### Expected Distributions:
- **Gender**: Male ~50%, Female ~50%
- **Zones**: 10 zones with varying proportions
- **2020 AE**: 6 parties (INC, BJP, Others, JD(U), LJP, RJD)
- **2024 GE**: 6 parties (BJP, RJD, Others, INC, JD(U), LJP)

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review the main README.md
3. Check instructions.md for detailed specifications
4. Review reference.py for algorithm details

## 🎯 Next Steps

After successful paneling:
1. **Validate results**: Review all distribution tables
2. **Check overlaps**: Ensure complete mutual exclusivity
3. **Export data**: Save CSV files for analysis
4. **Document**: Generate and save the summary report
5. **Use data**: Import CSV files into your analysis tools

---

**Ready to start? Launch the application and follow the steps above!**

```bash
./run_app.sh
```

or

```bash
streamlit run src/main.py
```
