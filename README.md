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
   ./run_app.sh
   ```
   
   Or directly:
   ```bash
   streamlit run main.py
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
   - **NEW**: Choose how many sets to split each panel into (2-10 sets)
   - Split each panel into N equal, balanced sets
   - Maintains proportional balance across all stratification variables
   - Compare distributions across all sets
   
   **Step 5: Validate & Export**
   - Verify no overlaps exist between any sets
   - Export all files to CSV
   - Download individual files or batch export
   - Generate summary report

## Project Structure

```
Panneling/
├── main.py              # Consolidated Streamlit application (all-in-one)
├── tests/               # Test files
│   ├── test_paneling.py
│   ├── test_n_way_split.py
│   └── test_equal_deviation.py
├── data/                # Output directory for CSV files
├── config/             
├── requirements.txt     # Python dependencies
├── run_app.sh          # Launch script
├── README.md           # This file
└── Bihar_panels.xlsx   # Example dataset
```

**Note**: All code has been consolidated into a single `main.py` file for easier deployment and distribution.

## Algorithm Details

### Panel Creation

The tool uses **iterative proportional fitting with multi-dimensional stratified sampling**:

1. **Hierarchical Stratification**: Stratifies across multiple features simultaneously
2. **Joint Sampling**: Creates joint strata from combinations of target features
3. **Proportional Allocation**: Allocates samples to match target proportions
4. **Non-Overlapping**: Maintains a set of used indices to ensure exclusivity

### Panel Splitting (N-Way)

Each panel can be split into N equal sets using **round-robin stratified assignment**:

1. **Strata Creation**: Combines all target features into unique strata
2. **N-Way Distribution**: Within each stratum, distributes samples evenly across N sets using round-robin
3. **Balance Preservation**: Ensures all N sets maintain the same proportional distributions
4. **Max Deviation Tracking**: Monitors maximum deviation across all sets for each category

## Key Functions (in main.py)

The consolidated `main.py` file contains all functionality organized into sections:

### Core Paneling Functions

- `check_master_distribution()`: Validates dataset has sufficient samples
- `create_balanced_sample()`: Creates a single balanced sample with target distributions
- `compute_adjusted_targets()`: Applies equal deviation distribution when samples are insufficient
- `create_panels()`: Creates multiple non-overlapping panels
- `split_panel_into_n_sets()`: Splits a panel into N balanced sets (NEW!)
- `split_panel_into_two()`: Legacy function, wrapper around N-way split
- `split_all_panels()`: Splits all panels into N sets each

### Utility Functions

- `validate_uploaded_file()`: Validates input data
- `validate_target_proportions()`: Ensures targets sum to 1.0
- `check_availability()`: Verifies sufficient samples for requested panels
- `print_distribution_table()`: Creates formatted distribution tables
- `check_overlap_between_sets()`: Verifies mutual exclusivity
- `create_comparison_table()`: Compares distributions across multiple sets
- `calculate_max_possible_panels()`: Calculates maximum feasible panels
- `get_feature_statistics()`: Provides feature-level statistics

### Streamlit UI

- `initialize_session_state()`: Manages application state
- `main()`: Main application with 5-step workflow

## Example Workflow

The Streamlit UI handles this automatically, but the underlying logic flow is:

```python
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

# 4. Split panels into N sets (e.g., 3 sets per panel)
splits, split_stats = split_all_panels(
    panels, targets, features, num_sets=3, random_state=42
)

# 5. Export (e.g., for 3 sets per panel)
for panel_idx, sets in enumerate(splits, 1):
    for set_idx, set_df in enumerate(sets, 1):
        set_df.to_csv(f'data/panel_{panel_idx}_set_{set_idx}.csv')
```

## Validation & Quality Checks

The tool performs multiple validation checks:

- **Pre-Creation**: Checks if master dataset has sufficient samples for targets
- **Post-Creation**: Compares actual vs. target distributions for each panel
- **Post-Split**: Verifies all N sets have matching distributions with deviation tracking
- **Overlap Check**: Ensures complete mutual exclusivity across all panels and sets

## Output Files

Generated CSV files follow this naming convention (example with 3 sets per panel):
- `panel_1_set_1.csv`
- `panel_1_set_2.csv`
- `panel_1_set_3.csv`
- `panel_2_set_1.csv`
- `panel_2_set_2.csv`
- `panel_2_set_3.csv`
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
- **Architecture**: Single consolidated Python file for easy deployment
- **Main Dependencies**: 
  - Streamlit 1.28+
  - pandas 2.0+
  - numpy 1.24+
- **Random State**: Fully reproducible results with seed control
- **Code Organization**: ~1,570 lines organized into utility, core paneling, and UI sections

## Support

For questions or issues, please refer to this README or contact your administrator.

## Version History

- **v1.3**: N-way panel splitting (2-10 sets per panel)
- **v1.2**: Equal deviation distribution for insufficient samples
- **v1.1**: Initial release with 2-way splitting
- **v1.4**: Consolidated all code into single `main.py` file (Current)

## License

Internal use only.
