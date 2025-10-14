# Changelog

## Version 1.3 - October 14, 2025

### 🎯 Major Feature: N-Way Panel Splitting

**New Feature**: Panels can now be split into any number of sets (2, 3, 4, etc.), not just two.

#### Overview
Users can now specify exactly how many sub-sets to split each panel into. The tool maintains stratification and equal distribution across all N sets using the same joint stratification algorithm.

#### Key Features

1. **Flexible Set Configuration**
   - User-specified number of sets per panel (2-10)
   - Each panel splits into the same number of sets
   - Equal distribution of samples across all sets

2. **Maintained Stratification**
   - Joint stratification across all target columns
   - Each unique stratum distributed evenly via round-robin
   - All sets maintain target proportions

3. **Enhanced Statistics Display**
   - Shows distribution across all N sets
   - Calculates max deviation among sets
   - Compares each set to target proportions
   - Summary table with all sets side-by-side

4. **Updated File Naming**
   - New format: `panel_1_set_1.csv`, `panel_1_set_2.csv`, etc.
   - Consistent numbering across all panels
   - Example with 3 sets: `panel_1_set_1.csv` through `panel_3_set_3.csv`

#### Example Scenarios

**Scenario 1: Three-way Split**
```
Configuration:
- 3 panels of 1,050 samples each
- Split into 3 sets per panel
- Result: 9 sets of ~350 samples each

Panel 1: Set 1 (350), Set 2 (350), Set 3 (350)
Panel 2: Set 1 (350), Set 2 (350), Set 3 (350)
Panel 3: Set 1 (350), Set 2 (350), Set 3 (350)
```

**Scenario 2: Four-way Split**
```
Configuration:
- 2 panels of 2,000 samples each
- Split into 4 sets per panel
- Result: 8 sets of ~500 samples each

Panel 1: Set 1 (500), Set 2 (500), Set 3 (500), Set 4 (500)
Panel 2: Set 1 (500), Set 2 (500), Set 3 (500), Set 4 (500)
```

#### UI Changes

**Step 4: Split Panels**
- Added "Number of Sets per Panel" input (2-10)
- Info box shows total sets to be created
- Progress indicator for splitting
- Enhanced statistics display for N sets

**Split Statistics View**
- Dynamic columns based on number of sets
- Comparison table shows all sets side-by-side
- Max deviation calculated across all sets
- Color-coded status indicators

**Export Section**
- Updated file naming preview
- Batch export handles variable number of sets
- Individual download buttons organized by panel
- Up to 3 download buttons per row for readability

#### Technical Implementation

```python
# New function: split_panel_into_n_sets()
def split_panel_into_n_sets(panel, target_dict, features, num_sets=2):
    """Split panel into N sets using round-robin stratification"""
    # For each stratum, distribute samples evenly via modulo
    for i, idx in enumerate(stratum_indices):
        set_num = i % num_sets
        set_indices[set_num].append(idx)
    return sets

# Updated: split_all_panels()
def split_all_panels(panels, target_dict, features, num_sets=2):
    """Split all panels into N sets each"""
    # Returns list of lists: [[set1, set2, ...], [set1, set2, ...], ...]
    # Statistics include max_deviation across all N sets
```

#### Algorithm Details

**Round-Robin Distribution:**
1. Create joint strata from all target columns
2. For each stratum, shuffle indices
3. Distribute indices across N sets using modulo: `set_num = i % num_sets`
4. Ensures even distribution regardless of N

**Benefits:**
- ✅ Equal sample sizes across all sets (±1-2 samples)
- ✅ Maintains proportions in each set
- ✅ Max deviation typically < 2% across all sets
- ✅ Mutually exclusive sets (no overlaps)
- ✅ Scales to any number of sets

#### Test Results

All tests pass with excellent metrics:

**Two-way Split (Backward Compatibility)**
- Set sizes: 507, 493 (balanced)
- Max deviation: < 0.2% across all features
- Zero overlaps ✓

**Three-way Split**
- Set sizes: 405, 403, 392 (well-balanced)
- Max deviation: < 0.4% across all features
- Zero overlaps ✓

**Four-way Split**
- Set sizes: 509, 505, 497, 489 (CV=0.0154, excellent)
- Max deviation: < 0.4% across all features
- Zero overlaps ✓

**Split All Panels (3×3)**
- 9 sets created successfully
- All distributions balanced
- Summary statistics validated ✓

#### Documentation Updates

- ✅ Updated WORKFLOW_DIAGRAM.md with N-way split diagram
- ✅ Updated export file naming examples
- ✅ Updated algorithm section with round-robin details
- ✅ Created comprehensive test suite (test_n_way_split.py)
- ✅ This changelog entry

#### Backward Compatibility

✅ **Fully backward compatible!**
- Default is still 2 sets (existing behavior)
- `split_panel_into_two()` still available (calls new function)
- All existing code continues to work
- New parameter is optional with default value

#### Use Cases

**2 Sets (A/B Testing)**
- Standard experimental design
- Control vs. Treatment
- Pre/Post comparison

**3 Sets (Multi-arm Trials)**
- Control + 2 treatments
- Training + Validation + Test
- Regional studies (North, Central, South)

**4 Sets (Quarterly Analysis)**
- Four quarters
- Four regions
- Four treatment variations
- Longitudinal studies with 4 waves

**5+ Sets (Large Studies)**
- Multi-center trials
- Complex experimental designs
- Large-scale surveys with multiple waves

#### Example Output Files

**3 Panels × 3 Sets:**
```
✓ panel_1_set_1.csv
✓ panel_1_set_2.csv
✓ panel_1_set_3.csv
✓ panel_2_set_1.csv
✓ panel_2_set_2.csv
✓ panel_2_set_3.csv
✓ panel_3_set_1.csv
✓ panel_3_set_2.csv
✓ panel_3_set_3.csv
```

#### Next Steps for Users

1. Create panels as usual (Step 3)
2. Go to Step 4: Split Panels
3. **NEW**: Specify number of sets (2-10)
4. Click "Split All Panels"
5. Review statistics for all N sets
6. Export with new naming convention

---

## Version 1.2 - October 14, 2025

### 🎯 Major Feature: Equal Deviation Distribution Across Panels

**Breaking Change**: Panel creation logic now distributes deviation equally across ALL panels when samples are insufficient.

#### Previous Behavior ❌
When target categories were underrepresented:
- Panel 1, 2, 3... would hit exact targets
- Last panel absorbed ALL deviation
- Example: Panels 1-3 get 1500 females each, Panel 4 gets 0 (if only 4500 available for 6000 needed)
- Result: Highly imbalanced final panel

#### New Behavior ✅
When target categories are underrepresented:
- Pre-allocation phase calculates feasible distribution
- **ALL panels share deviation EQUALLY**
- Example: Panels 1-4 each get 1125 females (4500÷4) instead of 1500+1500+1500+0
- Result: All panels balanced and usable

#### Key Changes

1. **New Function: `compute_adjusted_targets()`**
   - Pre-computes feasible targets before sampling
   - Distributes available samples equally across all panels
   - Normalizes adjusted proportions to sum to 1.0

2. **Updated `create_panels()`**
   - Now uses adjusted targets instead of ideal targets when samples insufficient
   - Displays warnings showing adjustments made
   - Reports both ideal and adjusted targets in summary

3. **Enhanced Display**
   - Shows "Ideal Target" (user-specified)
   - Shows "Adjusted Target" (feasible with equal distribution)
   - Shows "Actual" (achieved distribution)
   - Calculates deviation from adjusted target
   - Clear warnings when adjustments are made

#### Example Scenario

**Setup:**
- 4 panels of 3000 samples each (12,000 total needed)
- Target: 50% female (6,000 females needed)
- Available: Only 2,500 females in dataset

**Old Behavior:**
```
Panel 1: 1500 females (50% ✓)
Panel 2: 1000 females (33% ✗)
Panel 3: 0 females (0% ✗✗✗)
Panel 4: 0 females (0% ✗✗✗)
```

**New Behavior:**
```
⚠️ Adjustment: Only 2,500 females available, need 6,000
Each panel will get ~625 females instead of 1,500

Panel 1: 625 females (20.8% ✓ matches adjusted target)
Panel 2: 625 females (20.8% ✓ matches adjusted target)
Panel 3: 625 females (20.8% ✓ matches adjusted target)
Panel 4: 625 females (20.8% ✓ matches adjusted target)
```

#### Benefits

✅ **Fair Distribution**: All panels equally usable  
✅ **Transparent**: Clear warnings about adjustments  
✅ **Predictable**: No surprise deviation in last panel  
✅ **Documented**: Shows ideal vs adjusted vs actual  
✅ **Professional**: All panels meet research standards  

#### Technical Details

```python
# Pre-allocation logic
for each feature and category:
    ideal_total = num_panels × panel_size × target_proportion
    available_count = count in master dataset
    
    if available_count < ideal_total:
        feasible_per_panel = available_count / num_panels
        adjusted_proportion = feasible_per_panel / panel_size
        # Use adjusted_proportion for all panels
    else:
        # Use ideal target_proportion
```

#### UI Updates

- **Warnings Section**: Shows which categories are adjusted
- **Distribution Tables**: Now display 3 values:
  - Ideal Target (user input)
  - Adjusted Target (system computed)
  - Actual (achieved)
- **Status Indicators**: Compare actual to adjusted target (not ideal)

#### Documentation Updates

- ✅ Updated WORKFLOW_DIAGRAM.md with pre-allocation phase
- ✅ Updated algorithm overview section
- ✅ This changelog entry

---

## Version 1.1 - October 14, 2025

### 🎉 Feature Update: Optional Target Proportions

**Update**: Flexible Target Proportion Configuration

## 📝 Summary

The Data Paneling Tool now supports **optional target proportion configuration**. You no longer need to set custom proportions for every column - you can choose which specific columns require custom proportions while letting others use their natural distribution.

## 🆕 New Features

### 1. Two-Step Column Selection

**Step 1: Select Stratification Columns**
- Choose all columns you want to consider for stratification
- These columns will be used to maintain balance in your panels

**Step 2: Choose Columns for Custom Proportions (OPTIONAL)**
- Select only the columns where you want to define specific target proportions
- Leave empty to use natural distributions for all columns
- Or select a subset of columns for fine-tuned control

### 2. Flexible Configuration Options

You now have three approaches:

#### Option A: Natural Distribution for All
- Select stratification columns
- Skip custom proportion selection
- All columns use their dataset distribution
- **Use case**: Quick panel creation maintaining natural patterns

#### Option B: Custom Proportions for Specific Columns
- Select stratification columns
- Choose 1-2 critical columns for custom proportions
- Other columns use natural distribution
- **Use case**: Control key variables (e.g., Gender) while preserving others

#### Option C: Full Custom Control
- Select stratification columns
- Choose all columns for custom proportions
- Define exact targets for each
- **Use case**: Precise control over all distributions

## 📊 Example Workflows

### Example 1: Simple Gender Balance Only

```
Step 1: Select Stratification Columns
☑ Gender
☑ Zone
☑ 2020 AE
☑ 2024 GE

Step 2: Choose Columns for Custom Proportions
☑ Gender  ← Only this one!
□ Zone
□ 2020 AE
□ 2024 GE

Result:
✓ Gender: 50% Male, 50% Female (custom)
✓ Zone: Natural distribution from dataset
✓ 2020 AE: Natural distribution from dataset
✓ 2024 GE: Natural distribution from dataset
```

### Example 2: No Custom Proportions

```
Step 1: Select Stratification Columns
☑ Gender
☑ Zone
☑ 2020 AE

Step 2: Choose Columns for Custom Proportions
□ (Leave empty)

Result:
✓ All columns use natural distribution
✓ Panels maintain dataset proportions
✓ Faster configuration
```

### Example 3: Multiple Custom Columns

```
Step 1: Select Stratification Columns
☑ Gender
☑ Zone
☑ Income Group

Step 2: Choose Columns for Custom Proportions
☑ Gender
☑ Income Group
□ Zone

Result:
✓ Gender: Custom proportions (e.g., 50/50)
✓ Income Group: Custom proportions (e.g., 30/40/30)
✓ Zone: Natural distribution from dataset
```

## 🎯 Benefits

### 1. **Faster Workflow**
- No need to configure proportions for every column
- Skip unnecessary configuration steps
- Focus only on critical variables

### 2. **More Flexibility**
- Mix custom and natural distributions
- Control only what matters
- Preserve natural patterns in other variables

### 3. **Reduced Errors**
- Fewer proportions to validate
- Less chance of input errors
- Simpler configuration

### 4. **Better User Experience**
- Clear two-step process
- Optional vs. required clearly marked
- Helpful tips and guidance

## 🔧 Technical Changes

### Modified Files

1. **`src/main.py`**
   - Added `columns_for_targets` selection
   - Conditional proportion configuration
   - Auto-fill natural distributions for unselected columns
   - Better validation messages

2. **`WORKFLOW_DIAGRAM.md`**
   - Updated Step 2 to show optional selection
   - Clearer visual representation

3. **`QUICKSTART.md`**
   - Updated instructions for new workflow
   - Added optional step clarification

### New Functionality

```python
# New session state variable
st.session_state.columns_for_targets  # Tracks which columns have custom proportions

# Automatic natural distribution filling
for feature in selected_features:
    if feature not in target_dict:
        current_props = df[feature].value_counts(normalize=True).to_dict()
        target_dict[feature] = current_props
```

## 📋 Updated UI Elements

### New Selection Widget
```
"Select columns to define target proportions (optional):"
- Multiselect from stratification columns
- Default: all selected (backward compatible)
- Can be empty for all-natural distribution
```

### Enhanced Info Messages
```
💡 Tip: You don't need to set target proportions for every column.
- Select only the columns where you want to control specific proportions
- Unselected columns will use their natural distribution from the dataset
```

### Better Status Display
```
Configuration Summary:
✓ Total Stratification Columns: 4
✓ Columns with Custom Proportions: 2

Columns with Custom Proportions:
- Gender: [Male: 0.500, Female: 0.500]
- Zone: [custom proportions]

Columns using Natural Distribution:
- 2020 AE, 2024 GE
```

## 🚀 Migration Guide

### For Existing Users

**No changes needed!** The tool is backward compatible:
- Default behavior selects all columns for custom proportions
- Existing workflows work exactly as before
- You can now simplify by deselecting columns

### To Use New Features

1. Upload your data as usual
2. Select stratification columns
3. **NEW**: Choose which columns need custom proportions
   - Leave empty for all natural
   - Select some for mixed approach
   - Select all for full control (old behavior)
4. Configure only selected columns
5. Continue with panel creation

## 💡 Use Case Recommendations

### When to Use Natural Distribution
- Exploratory analysis
- Quick panel creation
- When dataset is already well-balanced
- Secondary variables that don't need control

### When to Use Custom Proportions
- Critical demographic variables (Gender, Age)
- Business-critical segments
- Variables with known target distributions
- Compliance requirements (e.g., representative samples)

### When to Mix Both
- Control primary variables (Gender, Region)
- Let secondary variables follow natural patterns
- Balance between control and simplicity
- Most common real-world scenario

## 🐛 Bug Fixes

### Fixed Mixed Type Sorting Error
**Issue**: Columns with mixed data types (int and str) caused sorting errors  
**Fix**: Added try-except to handle mixed types gracefully  
**Impact**: Now handles all column types automatically

```python
try:
    unique_values = sorted(df[feature].unique())
except TypeError:
    # Handle mixed types by converting to string
    unique_values = sorted(df[feature].astype(str).unique())
```

## 📖 Documentation Updates

All documentation has been updated:
- ✅ QUICKSTART.md
- ✅ WORKFLOW_DIAGRAM.md
- ✅ This changelog (CHANGELOG.md)

## 🎓 Examples

See `EXAMPLES.md` for updated use cases showing:
- Natural distribution approach
- Mixed custom/natural approach
- Full custom control approach

## 🔜 Future Enhancements

Potential future improvements:
- Save/load proportion templates
- Proportion presets for common scenarios
- Visual proportion editors
- Import proportions from CSV

## ✅ Testing

All functionality tested with:
- ✓ No custom proportions selected
- ✓ Some columns with custom proportions
- ✓ All columns with custom proportions
- ✓ Mixed data types in columns
- ✓ Large datasets (40K+ rows)

---

**Enjoy the enhanced flexibility!** 🎊

For questions or feedback, refer to the updated documentation in `QUICKSTART.md` and `README.md`.
