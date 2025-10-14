# Data Paneling Tool

A comprehensive Streamlit-based application for creating balanced, non-overlapping data panels with precise stratification control.

## 🎉 New in Version 1.3

- **N-Way Panel Splitting**: Split panels into any number of sets (2, 3, 4, etc.) - not just two!
- **User-Specified Subdivision**: Choose exactly how many sub-sets each panel should be split into
- **Enhanced Statistics**: Compare distributions across all N sets with max deviation tracking
- **Flexible File Naming**: Automatic naming convention `panel_X_set_Y.csv` for any number of sets

## Features

- **Upload & Analyze**: Support for CSV and Excel files with automatic validation
- **Flexible Stratification**: Select any columns for stratification with custom target proportions
- **Equal Deviation Distribution**: When samples are insufficient, deviation is distributed equally across ALL panels (Version 1.2)
- **Multi-Panel Creation**: Create multiple non-overlapping panels with iterative proportional fitting
- **N-Way Splitting**: Split each panel into 2, 3, 4, or more equally sized, stratified sets (NEW!)
- **Comprehensive Validation**: 
  - Distribution matching verification
  - Overlap detection across all panels and sets
  - Detailed statistical summaries for all N sets
- **Easy Export**: Download individual files or batch export all results to CSV

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   streamlit --version
   ```

## Usage

1. **Launch the application:**
   ```bash
   streamlit run src/main.py
   ```

2. **Follow the workflow:**
   
   **Step 1: Upload Data**
   - Upload your CSV or Excel file
   - Review dataset overview and column information
   
   **Step 2: Configure Targets**
   - Select columns for stratification
   - Define target proportions for each category
   - Option to use current dataset distributions
   
   **Step 3: Create Panels**
   - Specify number of panels and panel size
   - System checks data availability
   - Creates non-overlapping panels with balanced distributions
   - Review detailed statistics for each panel
   
   **Step 4: Split Panels**
   - Split each panel into Set A and Set B
   - Maintains proportional balance across all stratification variables
   - Compare distributions between sets
   
   **Step 5: Validate & Export**
   - Verify no overlaps exist between any sets
   - Export all files to CSV
   - Download individual files or batch export
   - Generate summary report

## Folder Structure

```
Panneling/
├── src/
│   ├── main.py          # Main Streamlit application
│   ├── paneling.py      # Core paneling logic
│   └── utils.py         # Utility functions
├── data/                # Output directory for CSV files
├── config/             
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── instructions.md     # Project instructions
├── reference.py        # Reference implementation
└── Bihar_panels.xlsx   # Example data
```

## Algorithm Details

### Panel Creation

The tool uses **iterative proportional fitting with multi-dimensional stratified sampling**:

1. **Hierarchical Stratification**: Stratifies across multiple features simultaneously
2. **Joint Sampling**: Creates joint strata from combinations of target features
3. **Proportional Allocation**: Allocates samples to match target proportions
4. **Non-Overlapping**: Maintains a set of used indices to ensure exclusivity

### Panel Splitting

Each panel is split using **joint stratification**:

1. **Strata Creation**: Combines all target features into unique strata
2. **50-50 Split**: Within each stratum, randomly assigns half to Set A, half to Set B
3. **Balance Preservation**: Ensures both sets maintain the same proportional distributions

## Key Functions

### `paneling.py`

- `check_master_distribution()`: Validates dataset has sufficient samples
- `create_balanced_sample()`: Creates a single balanced sample with target distributions
- `create_panels()`: Creates multiple non-overlapping panels
- `split_panel_into_two()`: Splits a panel into two balanced sets
- `split_all_panels()`: Splits all panels

### `utils.py`

- `validate_uploaded_file()`: Validates input data
- `validate_target_proportions()`: Ensures targets sum to 1.0
- `check_availability()`: Verifies sufficient samples for requested panels
- `print_distribution_table()`: Creates formatted distribution tables
- `check_overlap_between_sets()`: Verifies mutual exclusivity
- `create_comparison_table()`: Compares two sets side-by-side

## Example Workflow

```python
# This is handled through the Streamlit UI, but the underlying logic:

# 1. Load data
df = pd.read_excel('Bihar_panels.xlsx')

# 2. Define targets
targets = {
    'Gender': {'Male': 0.5, 'Female': 0.5},
    'zone': {...},
    '2020 AE': {...},
    '2024 GE': {...}
}

# 3. Create panels
panels, stats = create_panels(
    df, targets, features=['Gender', 'zone', '2020 AE', '2024 GE'],
    num_panels=3, panel_size=1050, random_state=42
)

# 4. Split panels
splits, split_stats = split_all_panels(panels, targets, features, random_state=42)

# 5. Export
for i, (set_a, set_b) in enumerate(splits, 1):
    set_a.to_csv(f'data/panel_{i}_set_a.csv')
    set_b.to_csv(f'data/panel_{i}_set_b.csv')
```

## Validation & Quality Checks

The tool performs multiple validation checks:

- **Pre-Creation**: Checks if master dataset has sufficient samples for targets
- **Post-Creation**: Compares actual vs. target distributions for each panel
- **Post-Split**: Verifies Set A and Set B have matching distributions
- **Overlap Check**: Ensures complete mutual exclusivity across all sets

## Output Files

Generated CSV files follow this naming convention:
- `panel_1_set_a.csv`
- `panel_1_set_b.csv`
- `panel_2_set_a.csv`
- `panel_2_set_b.csv`
- etc.

Each file contains:
- All original columns from the input dataset
- Original index preserved for traceability

## Performance Considerations

- **Large Datasets**: The tool handles datasets with 40,000+ rows efficiently
- **Multiple Features**: Supports stratification across 4+ features simultaneously
- **Progress Tracking**: Shows progress bars for long-running operations
- **Memory Efficient**: Uses pandas for efficient data handling

## Troubleshooting

**Issue**: "Not enough samples" error
- **Solution**: Reduce panel size or number of panels, or adjust target proportions to match available data

**Issue**: Target proportions don't sum to 1.0
- **Solution**: Use the "Use current distribution" option or manually adjust proportions

**Issue**: Large deviations from targets
- **Solution**: Some categories may be underrepresented in the master dataset. Check availability warnings.

## Technical Details

- **Python Version**: 3.8+
- **Main Dependencies**: 
  - Streamlit 1.28+
  - pandas 2.0+
  - numpy 1.24+
- **Random State**: Fully reproducible results with seed control

## Reference Implementation

See `reference.py` for the original implementation logic that this tool is based on. The Streamlit application wraps this logic with an interactive interface while maintaining the same rigorous statistical approach.

## Support

For questions or issues, refer to the `instructions.md` file or contact your administrator.

## License

Internal use only.
