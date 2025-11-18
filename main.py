"""
Streamlit Data Paneling Tool - Consolidated Version
Main application for creating balanced, non-overlapping data panels with N-way splitting
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import io
from typing import Dict, List, Tuple, Optional


# ==================== UTILITY FUNCTIONS ====================

def validate_uploaded_file(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate uploaded file meets requirements
    
    Args:
        df: Uploaded dataframe
        
    Returns:
        Tuple of (is_valid, message)
    """
    if df is None or df.empty:
        return False, "File is empty"
    
    if len(df) < 100:
        return False, f"File has only {len(df)} rows. Minimum 100 rows required."
    
    return True, "File validation successful"


def validate_target_proportions(target_dict: Dict) -> Tuple[bool, str]:
    """
    Validate target proportions sum to 1.0 for each feature
    
    Args:
        target_dict: Dictionary of {feature: {category: proportion}}
        
    Returns:
        Tuple of (is_valid, message)
    """
    for feature, proportions in target_dict.items():
        total = sum(proportions.values())
        if abs(total - 1.0) > 0.01:
            return False, f"Proportions for {feature} sum to {total:.3f}, should be 1.0"
    
    return True, "All target proportions are valid"


def check_availability(
    df: pd.DataFrame,
    target_dict: Dict,
    num_panels: int,
    panel_size: int
) -> Tuple[bool, str]:
    """
    Check if enough samples are available for requested configuration
    
    Args:
        df: Master dataframe
        target_dict: Target proportions
        num_panels: Number of panels to create
        panel_size: Size of each panel
        
    Returns:
        Tuple of (is_sufficient, message)
    """
    total_needed = num_panels * panel_size
    total_available = len(df)
    
    if total_needed > total_available:
        return False, f"Insufficient samples: need {total_needed:,}, have {total_available:,}"
    
    # Check each feature category
    warnings = []
    for feature, targets in target_dict.items():
        for category, proportion in targets.items():
            needed = int(total_needed * proportion)
            available = len(df[df[feature] == category])
            
            if needed > available:
                warnings.append(
                    f"{feature}={category}: need {needed}, have {available}"
                )
    
    if warnings:
        warning_msg = "⚠️ Warning: Some categories may not have enough samples:\n" + "\n".join(warnings)
        return True, warning_msg
    
    return True, f"✓ Sufficient samples available ({total_available:,} total)"


def print_distribution_table(
    df: pd.DataFrame,
    feature: str,
    target_dict: Dict,
    panel_name: str = "Panel",
    adjusted_dict: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Create distribution comparison table
    
    Args:
        df: Panel dataframe
        feature: Feature to analyze
        target_dict: Original target proportions
        panel_name: Name for display
        adjusted_dict: Optional adjusted proportions after equal deviation
        
    Returns:
        DataFrame with distribution comparison
    """
    actual_counts = df[feature].value_counts()
    actual_props = df[feature].value_counts(normalize=True)
    
    categories = list(target_dict.get(feature, {}).keys())
    
    data = []
    for cat in categories:
        target_prop = target_dict[feature].get(cat, 0)
        actual_prop = actual_props.get(cat, 0)
        count = actual_counts.get(cat, 0)
        
        # Use adjusted target if available
        if adjusted_dict and feature in adjusted_dict:
            target_prop = adjusted_dict[feature].get(cat, target_prop)
        
        deviation = actual_prop - target_prop
        
        data.append({
            'Category': cat,
            'Target': f"{target_prop:.1%}",
            'Actual': f"{actual_prop:.1%}",
            'Count': count,
            'Deviation': f"{deviation:+.1%}",
            'Status': '✓' if abs(deviation) < 0.02 else '⚠️'
        })
    
    return pd.DataFrame(data)


def check_overlap_between_sets(sets: List[Tuple[str, pd.DataFrame]]) -> Dict:
    """
    Check for overlaps between multiple sets
    
    Args:
        sets: List of (name, dataframe) tuples
        
    Returns:
        Dictionary with overlap information
    """
    results = []
    has_overlap = False
    
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            name1, df1 = sets[i]
            name2, df2 = sets[j]
            
            overlap = set(df1.index) & set(df2.index)
            overlap_count = len(overlap)
            
            if overlap_count > 0:
                has_overlap = True
            
            results.append({
                'Set 1': name1,
                'Set 2': name2,
                'Overlap Count': overlap_count,
                'Status': '❌ Overlap' if overlap_count > 0 else '✓ No Overlap'
            })
    
    return {
        'has_overlap': has_overlap,
        'results': results
    }


def create_comparison_table(
    sets: List[pd.DataFrame],
    feature: str,
    target_dict: Dict
) -> pd.DataFrame:
    """
    Create comparison table across multiple sets
    
    Args:
        sets: List of dataframes
        feature: Feature to compare
        target_dict: Target proportions
        
    Returns:
        Comparison dataframe
    """
    categories = list(target_dict[feature].keys())
    
    data = []
    for cat in categories:
        row = {'Category': cat}
        
        for i, df in enumerate(sets, 1):
            prop = df[feature].value_counts(normalize=True).get(cat, 0)
            row[f'Set {i}'] = f"{prop:.1%}"
        
        data.append(row)
    
    return pd.DataFrame(data)


def format_number(n: float) -> str:
    """Format number with thousands separator"""
    return f"{int(n):,}"


def calculate_max_possible_panels(
    df: pd.DataFrame,
    target_dict: Dict,
    panel_size: int
) -> int:
    """
    Calculate maximum number of panels possible
    
    Args:
        df: Master dataframe
        target_dict: Target proportions
        panel_size: Desired panel size
        
    Returns:
        Maximum number of panels
    """
    max_panels = len(df) // panel_size
    
    for feature, targets in target_dict.items():
        for category, proportion in targets.items():
            available = len(df[df[feature] == category])
            needed_per_panel = panel_size * proportion
            
            if needed_per_panel > 0:
                category_max = int(available / needed_per_panel)
                max_panels = min(max_panels, category_max)
    
    return max_panels


def get_feature_statistics(df: pd.DataFrame, feature: str) -> Dict:
    """
    Get statistics for a feature
    
    Args:
        df: Dataframe
        feature: Feature name
        
    Returns:
        Dictionary with statistics
    """
    value_counts = df[feature].value_counts()
    proportions = df[feature].value_counts(normalize=True)
    
    return {
        'unique_values': len(value_counts),
        'value_counts': value_counts.to_dict(),
        'proportions': proportions.to_dict(),
        'most_common': value_counts.index[0],
        'least_common': value_counts.index[-1]
    }


# ==================== CORE PANELING FUNCTIONS ====================

def check_master_distribution(
    master_sample: pd.DataFrame,
    target_dict: Dict[str, Dict],
    features: List[str],
    panel_size: int,
    num_panels: int
) -> Tuple[bool, Dict]:
    """
    Check if master sample has sufficient data for all target distributions
    
    Args:
        master_sample: Full dataset
        target_dict: Target proportions {feature: {category: proportion}}
        features: List of features to check
        panel_size: Size of each panel
        num_panels: Number of panels to create
        
    Returns:
        Tuple of (is_sufficient, info_dict)
    """
    total_needed = panel_size * num_panels
    info = {
        'total_available': len(master_sample),
        'total_needed': total_needed,
        'is_sufficient': True,
        'warnings': [],
        'details': {}
    }
    
    for feature in features:
        feature_info = {'categories': {}}
        
        for category, target_prop in target_dict[feature].items():
            available = len(master_sample[master_sample[feature] == category])
            needed = int(total_needed * target_prop)
            
            feature_info['categories'][category] = {
                'available': available,
                'needed': needed,
                'target_proportion': target_prop,
                'is_sufficient': available >= needed
            }
            
            if available < needed:
                info['is_sufficient'] = False
                info['warnings'].append(
                    f"{feature}={category}: need {needed}, have {available}"
                )
        
        info['details'][feature] = feature_info
    
    return info['is_sufficient'], info


def create_balanced_sample(
    master_sample: pd.DataFrame,
    target_dict: Dict[str, Dict],
    features: List[str],
    sample_size: int,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Create a balanced sample matching target proportions across multiple features
    
    Args:
        master_sample: Source dataframe
        target_dict: Target proportions for each feature
        features: List of features to balance
        sample_size: Desired sample size
        random_state: Random seed
        
    Returns:
        Balanced sample dataframe
    """
    np.random.seed(random_state)
    
    # Calculate target counts for each combination
    target_combinations = {}
    
    # Get all unique combinations in the data
    combinations = master_sample[features].drop_duplicates()
    
    for _, row in combinations.iterrows():
        combination = tuple(row[features])
        
        # Calculate target proportion for this combination
        proportion = 1.0
        for feature, value in zip(features, combination):
            proportion *= target_dict[feature].get(value, 0)
        
        target_count = int(sample_size * proportion)
        target_combinations[combination] = target_count
    
    # Sample from each combination
    sampled_indices = []
    
    for combination, target_count in target_combinations.items():
        if target_count == 0:
            continue
        
        # Filter for this combination
        mask = pd.Series([True] * len(master_sample), index=master_sample.index)
        for feature, value in zip(features, combination):
            mask &= (master_sample[feature] == value)
        
        available_indices = master_sample[mask].index.tolist()
        
        if len(available_indices) >= target_count:
            selected = np.random.choice(available_indices, size=target_count, replace=False)
            sampled_indices.extend(selected)
        else:
            # Use all available samples if not enough
            sampled_indices.extend(available_indices)
    
    return master_sample.loc[sampled_indices]


def compute_adjusted_targets(
    master_sample: pd.DataFrame,
    target_dict: Dict[str, Dict],
    features: List[str],
    total_needed: int
) -> Tuple[Dict[str, Dict], Dict]:
    """
    Compute adjusted target proportions using equal deviation distribution
    
    Args:
        master_sample: Full dataset
        target_dict: Original target proportions
        features: List of features
        total_needed: Total samples needed across all panels
        
    Returns:
        Tuple of (adjusted_targets, allocation_info)
    """
    adjusted_targets = {}
    allocation_info = {
        'adjustments_made': False,
        'features': {}
    }
    
    for feature in features:
        feature_info = {'categories': {}, 'needs_adjustment': False}
        adjusted_targets[feature] = {}
        
        categories = list(target_dict[feature].keys())
        original_targets = [target_dict[feature][cat] for cat in categories]
        availabilities = [len(master_sample[master_sample[feature] == cat]) for cat in categories]
        
        # Check if any category is insufficient
        needs_adjustment = any(
            avail < (total_needed * target) 
            for avail, target in zip(availabilities, original_targets)
        )
        
        if needs_adjustment:
            feature_info['needs_adjustment'] = True
            allocation_info['adjustments_made'] = True
            
            # Apply equal deviation distribution
            target_counts = [int(total_needed * t) for t in original_targets]
            allocated = [0] * len(categories)
            
            # First pass: allocate up to availability
            for i, (target, avail) in enumerate(zip(target_counts, availabilities)):
                allocated[i] = min(target, avail)
            
            # Calculate deficit
            total_allocated = sum(allocated)
            deficit = total_needed - total_allocated
            
            # Distribute deficit proportionally among categories with surplus
            if deficit > 0:
                surplus_indices = [
                    i for i in range(len(categories))
                    if availabilities[i] > allocated[i]
                ]
                
                if surplus_indices:
                    # Calculate proportional shares of deficit
                    surplus_capacities = [
                        availabilities[i] - allocated[i]
                        for i in surplus_indices
                    ]
                    total_surplus = sum(surplus_capacities)
                    
                    for i in surplus_indices:
                        additional = int(
                            deficit * (availabilities[i] - allocated[i]) / total_surplus
                        )
                        allocated[i] += additional
                    
                    # Handle rounding: distribute remaining to largest surplus
                    remaining = total_needed - sum(allocated)
                    if remaining > 0:
                        sorted_surplus = sorted(
                            surplus_indices,
                            key=lambda i: availabilities[i] - allocated[i],
                            reverse=True
                        )
                        for i in sorted_surplus[:remaining]:
                            allocated[i] += 1
            
            # Convert to proportions
            for i, cat in enumerate(categories):
                adjusted_targets[feature][cat] = allocated[i] / total_needed
                feature_info['categories'][cat] = {
                    'original_proportion': original_targets[i],
                    'adjusted_proportion': allocated[i] / total_needed,
                    'original_count': target_counts[i],
                    'adjusted_count': allocated[i],
                    'available': availabilities[i]
                }
        else:
            # No adjustment needed, use original targets
            for cat in categories:
                adjusted_targets[feature][cat] = target_dict[feature][cat]
                feature_info['categories'][cat] = {
                    'original_proportion': target_dict[feature][cat],
                    'adjusted_proportion': target_dict[feature][cat],
                    'available': len(master_sample[master_sample[feature] == cat])
                }
        
        allocation_info['features'][feature] = feature_info
    
    return adjusted_targets, allocation_info


def create_panels(
    master_sample: pd.DataFrame,
    target_dict: Dict[str, Dict],
    features: List[str],
    num_panels: int,
    panel_size: int,
    random_state: int = 42
) -> Tuple[List[pd.DataFrame], Dict]:
    """
    Create multiple non-overlapping panels with target distributions
    
    Args:
        master_sample: Source dataframe
        target_dict: Target proportions
        features: Features to balance
        num_panels: Number of panels to create
        panel_size: Size of each panel
        random_state: Random seed
        
    Returns:
        Tuple of (list of panel dataframes, statistics dict)
    """
    # Check availability and compute adjusted targets if needed
    total_needed = num_panels * panel_size
    adjusted_targets, allocation_info = compute_adjusted_targets(
        master_sample, target_dict, features, total_needed
    )
    
    # Use adjusted targets for panel creation
    working_targets = adjusted_targets if allocation_info['adjustments_made'] else target_dict
    
    panels = []
    panel_summaries = []
    remaining_sample = master_sample.copy()
    
    for i in range(num_panels):
        panel = create_balanced_sample(
            remaining_sample,
            working_targets,
            features,
            panel_size,
            random_state=random_state + i
        )
        
        panels.append(panel)
        
        # Remove used samples
        remaining_sample = remaining_sample.drop(panel.index)
        
        # Create summary
        summary = {
            'panel_number': i + 1,
            'size': len(panel),
            'distributions': {}
        }
        
        for feature in features:
            dist = panel[feature].value_counts(normalize=True).to_dict()
            summary['distributions'][feature] = dist
        
        panel_summaries.append(summary)
    
    stats = {
        'num_panels': num_panels,
        'panel_size': panel_size,
        'total_used': sum(len(p) for p in panels),
        'total_available': len(master_sample),
        'panel_summaries': panel_summaries,
        'allocation_info': allocation_info
    }
    
    return panels, stats


def split_panel_into_n_sets(
    panel: pd.DataFrame,
    target_dict: Dict[str, Dict],
    features: List[str],
    num_sets: int = 2,
    random_state: int = 42
) -> Tuple[List[pd.DataFrame], Dict]:
    """
    Split a single panel into N equal, balanced sets using round-robin stratified assignment
    
    Args:
        panel: Panel dataframe to split
        target_dict: Target proportions (for validation)
        features: Features to maintain balance on
        num_sets: Number of sets to create (default: 2)
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (list of N set dataframes, statistics dict)
    """
    np.random.seed(random_state)
    
    # Initialize sets
    sets = [[] for _ in range(num_sets)]
    
    # Get all unique combinations of feature values
    combinations = panel[features].drop_duplicates()
    
    # For each combination, split its samples evenly across sets
    for _, combo_row in combinations.iterrows():
        # Create mask for this combination
        mask = pd.Series([True] * len(panel), index=panel.index)
        for feature in features:
            mask &= (panel[feature] == combo_row[feature])
        
        # Get indices for this combination
        combo_indices = panel[mask].index.tolist()
        
        # Shuffle indices
        np.random.shuffle(combo_indices)
        
        # Distribute round-robin across sets
        for i, idx in enumerate(combo_indices):
            set_num = i % num_sets
            sets[set_num].append(idx)
    
    # Convert to dataframes
    set_dfs = [panel.loc[indices] for indices in sets]
    
    # Calculate statistics
    stats = {
        'num_sets': num_sets,
        'set_sizes': [len(s) for s in set_dfs],
        'comparisons': {}
    }
    
    # Compare distributions across sets
    for feature in features:
        feature_comparison = {}
        
        # Get all categories for this feature
        categories = panel[feature].unique()
        
        for category in categories:
            cat_info = {
                'values': {},
                'target': target_dict[feature].get(category, None)
            }
            
            # Get proportion in each set
            proportions = []
            for set_idx, set_df in enumerate(set_dfs):
                prop = (set_df[feature] == category).sum() / len(set_df)
                cat_info['values'][f'set_{set_idx + 1}'] = prop
                proportions.append(prop)
            
            # Calculate deviation
            if proportions:
                cat_info['mean'] = np.mean(proportions)
                cat_info['std'] = np.std(proportions)
                cat_info['max_deviation'] = max(proportions) - min(proportions)
                cat_info['status'] = '✓' if cat_info['max_deviation'] < 0.02 else '⚠️'
            
            feature_comparison[category] = cat_info
        
        stats['comparisons'][feature] = feature_comparison
    
    return set_dfs, stats


def split_panel_into_two(
    panel: pd.DataFrame,
    target_dict: Dict[str, Dict],
    features: List[str],
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Legacy function: Split a panel into two equal sets (wrapper around split_panel_into_n_sets)
    
    Args:
        panel: Panel dataframe to split
        target_dict: Target proportions
        features: Features to maintain balance on
        random_state: Random seed
        
    Returns:
        Tuple of (set_a, set_b, statistics dict)
    """
    sets, stats = split_panel_into_n_sets(
        panel, target_dict, features, num_sets=2, random_state=random_state
    )
    return sets[0], sets[1], stats


def split_all_panels(
    panels: List[pd.DataFrame],
    target_dict: Dict[str, Dict],
    features: List[str],
    num_sets: int = 2,
    random_state: int = 42
) -> Tuple[List[List[pd.DataFrame]], Dict]:
    """
    Split all panels into N sets each
    
    Args:
        panels: List of panel dataframes
        target_dict: Target proportions
        features: Features to balance
        num_sets: Number of sets to create per panel (default: 2)
        random_state: Random seed
        
    Returns:
        Tuple of (list of panel splits, where each split is a list of N sets, statistics dict)
    """
    all_splits = []
    split_summaries = []
    
    for i, panel in enumerate(panels):
        sets, stats = split_panel_into_n_sets(
            panel,
            target_dict,
            features,
            num_sets=num_sets,
            random_state=random_state + i
        )
        
        all_splits.append(sets)
        split_summaries.append(stats)
    
    overall_stats = {
        'num_panels': len(panels),
        'num_sets': num_sets,
        'split_summaries': split_summaries
    }
    
    return all_splits, overall_stats


# ==================== STREAMLIT UI ====================

# Page configuration
st.set_page_config(
    page_title="Data Paneling Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .error-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'target_dict' not in st.session_state:
        st.session_state.target_dict = {}
    if 'panels' not in st.session_state:
        st.session_state.panels = None
    if 'panel_splits' not in st.session_state:
        st.session_state.panel_splits = None
    if 'panel_stats' not in st.session_state:
        st.session_state.panel_stats = None
    if 'split_stats' not in st.session_state:
        st.session_state.split_stats = None


def main():
    initialize_session_state()
    
    # Title and description
    st.title("📊 Data Paneling Tool")
    st.markdown("""
    Create balanced, non-overlapping data panels with precise stratification.
    
    **Features:**
    - Upload and analyze your dataset
    - Define target proportions for multiple stratification variables
    - Create multiple non-overlapping panels
    - Split each panel into N balanced sets (2-10 sets)
    - Validate distributions and check for overlaps
    - Export results to CSV
    """)
    
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Step:",
        ["1. Upload Data", 
         "2. Configure Targets", 
         "3. Create Panels", 
         "4. Split Panels",
         "5. Validate & Export"]
    )
    
    # Step 1: Upload Data
    if page == "1. Upload Data":
        st.header("Step 1: Upload Data")
        
        uploaded_file = st.file_uploader(
            "Upload your CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload the master dataset containing all samples"
        )
        
        if uploaded_file is not None:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Validate
                is_valid, message = validate_uploaded_file(df)
                
                if is_valid:
                    st.session_state.df = df
                    st.success(f"✓ File loaded successfully! {len(df):,} rows, {len(df.columns)} columns")
                    
                    # Show dataset overview
                    st.subheader("Dataset Overview")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Rows", f"{len(df):,}")
                    with col2:
                        st.metric("Total Columns", len(df.columns))
                    with col3:
                        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                    
                    # Show column info
                    st.subheader("Column Information")
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes.values,
                        'Non-Null Count': df.count().values,
                        'Null Count': df.isnull().sum().values,
                        'Unique Values': [df[col].nunique() for col in df.columns]
                    })
                    st.dataframe(col_info, use_container_width=True)
                    
                    # Show sample data
                    st.subheader("Sample Data (First 10 rows)")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                else:
                    st.error(f"❌ Validation failed: {message}")
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        elif st.session_state.df is not None:
            st.info("📁 Dataset already loaded. Upload a new file to replace it.")
            st.metric("Current Dataset Rows", f"{len(st.session_state.df):,}")
    
    
    # Step 2: Configure Targets
    elif page == "2. Configure Targets":
        st.header("Step 2: Configure Target Proportions")
        
        if st.session_state.df is None:
            st.warning("⚠️ Please upload data first (Step 1)")
            return
        
        df = st.session_state.df
        
        st.markdown("""
        Select columns to use for stratification and optionally define target proportions.
        You can choose to maintain current distributions or set custom proportions for specific columns.
        """)
        
        # Select columns for paneling
        st.subheader("Select Stratification Columns")
        
        # Suggest categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        selected_features = st.multiselect(
            "Choose columns for stratification:",
            options=df.columns.tolist(),
            default=[col for col in categorical_cols[:4] if col in df.columns],
            help="Select columns that should maintain specific proportions in panels"
        )
        
        if not selected_features:
            st.warning("⚠️ Please select at least one column for stratification")
            return
        
        st.markdown("---")
        
        # Option to select which columns to configure proportions for
        st.subheader("Choose Columns for Custom Proportions")
        
        st.info("""
        💡 **Tip**: You don't need to set target proportions for every column. 
        - Select only the columns where you want to control specific proportions
        - Unselected columns will use their natural distribution from the dataset
        """)
        
        columns_for_targets = st.multiselect(
            "Select columns to define target proportions (optional):",
            options=selected_features,
            default=selected_features,
            help="Choose which columns you want to set custom proportions for. Leave empty to use natural distributions for all."
        )
        
        # Show current distributions for all selected features
        st.subheader("Current Dataset Distributions")
        
        st.markdown("Review the natural distributions of your selected columns:")
        
        for feature in selected_features:
            with st.expander(f"📊 {feature} Distribution", expanded=False):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**Value Counts:**")
                    value_counts = df[feature].value_counts()
                    proportions = df[feature].value_counts(normalize=True)
                    
                    dist_df = pd.DataFrame({
                        'Category': value_counts.index,
                        'Count': value_counts.values,
                        'Proportion': proportions.values
                    })
                    st.dataframe(dist_df, use_container_width=True)
                
                with col2:
                    st.write("**Distribution Chart:**")
                    st.bar_chart(proportions)
        
        # Configure target proportions only for selected columns
        if columns_for_targets:
            st.markdown("---")
            st.subheader("Define Target Proportions")
            
            st.markdown(f"""
            Configure proportions for **{len(columns_for_targets)}** selected column(s).
            Other columns will maintain their natural distribution.
            """)
        else:
            st.info("""
            ℹ️ No columns selected for custom proportions. 
            All columns will use their natural distribution from the dataset.
            You can proceed to the next step.
            """)
        
        target_dict = {}
        
        # Set target proportions for selected columns
        for feature in columns_for_targets:
            st.markdown(f"### {feature}")
            
            # Convert to string for sorting to handle mixed types
            try:
                unique_values = sorted(df[feature].unique())
            except TypeError:
                # Handle mixed types by converting to string
                unique_values = sorted(df[feature].astype(str).unique())
            
            current_props = df[feature].value_counts(normalize=True).to_dict()
            
            # Option to use current distribution
            use_current = st.checkbox(
                f"Use current distribution for {feature}",
                key=f"use_current_{feature}",
                value=True
            )
            
            feature_targets = {}
            
            if use_current:
                for val in unique_values:
                    feature_targets[val] = current_props.get(val, 0)
                st.success(f"✓ Using natural distribution from dataset")
            else:
                st.write("Enter target proportion for each category:")
                cols = st.columns(min(3, len(unique_values)))
                
                for idx, val in enumerate(unique_values):
                    with cols[idx % len(cols)]:
                        default_val = current_props.get(val, 1.0 / len(unique_values))
                        prop = st.number_input(
                            f"{val}",
                            min_value=0.0,
                            max_value=1.0,
                            value=float(default_val),
                            step=0.01,
                            format="%.3f",
                            key=f"target_{feature}_{val}"
                        )
                        feature_targets[val] = prop
                
                # Show sum
                total = sum(feature_targets.values())
                if abs(total - 1.0) > 0.01:
                    st.error(f"❌ Proportions sum to {total:.3f}, should be 1.0")
                else:
                    st.success(f"✓ Proportions sum to {total:.3f}")
            
            target_dict[feature] = feature_targets
        
        # For columns without explicit targets, use current distribution
        for feature in selected_features:
            if feature not in target_dict:
                current_props = df[feature].value_counts(normalize=True).to_dict()
                target_dict[feature] = current_props
        
        # Validate and save
        st.markdown("---")
        
        if st.button("✓ Validate and Save Configuration", type="primary"):
            is_valid, message = validate_target_proportions(target_dict)
            
            if is_valid:
                st.session_state.target_dict = target_dict
                st.session_state.selected_features = selected_features
                st.session_state.columns_for_targets = columns_for_targets
                st.success("✓ Configuration saved successfully!")
                
                # Show summary
                st.subheader("Configuration Summary")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Stratification Columns", len(selected_features))
                with col2:
                    st.metric("Columns with Custom Proportions", len(columns_for_targets))
                
                # Show details
                if columns_for_targets:
                    st.markdown("**Columns with Custom Proportions:**")
                    for feature in columns_for_targets:
                        targets = target_dict[feature]
                        with st.expander(f"{feature} Targets"):
                            target_df = pd.DataFrame({
                                'Category': list(targets.keys()),
                                'Target Proportion': list(targets.values())
                            })
                            st.dataframe(target_df, use_container_width=True)
                
                # Show columns using natural distribution
                natural_cols = [f for f in selected_features if f not in columns_for_targets]
                if natural_cols:
                    st.markdown("**Columns using Natural Distribution:**")
                    st.write(", ".join(natural_cols))
            else:
                st.error(f"❌ Validation failed: {message}")
    
    
    # Step 3: Create Panels
    elif page == "3. Create Panels":
        st.header("Step 3: Create Panels")
        
        if st.session_state.df is None:
            st.warning("⚠️ Please upload data first (Step 1)")
            return
        
        if not st.session_state.target_dict:
            st.warning("⚠️ Please configure target proportions first (Step 2)")
            return
        
        df = st.session_state.df
        target_dict = st.session_state.target_dict
        selected_features = st.session_state.selected_features
        
        # Panel configuration
        st.subheader("Panel Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_panels = st.number_input(
                "Number of Panels",
                min_value=1,
                max_value=10,
                value=3,
                help="How many independent panels to create"
            )
        
        with col2:
            max_panel_size = len(df) // num_panels
            panel_size = st.number_input(
                "Panel Size (samples per panel)",
                min_value=100,
                max_value=max_panel_size,
                value=min(1050, max_panel_size),
                help="Number of samples in each panel"
            )
        
        # Show availability check
        total_needed = num_panels * panel_size
        st.info(f"ℹ️ Total samples needed: {total_needed:,} of {len(df):,} available")
        
        # Check availability
        is_sufficient, avail_message = check_availability(
            df, target_dict, num_panels, panel_size
        )
        
        if is_sufficient:
            if "⚠️" in avail_message:
                st.warning(avail_message)
            else:
                st.success(avail_message)
        else:
            st.error(avail_message)
            return
        
        # Random seed
        random_seed = st.number_input(
            "Random Seed (for reproducibility)",
            min_value=0,
            value=42,
            help="Set seed for reproducible results"
        )
        
        # Create panels button
        st.markdown("---")
        
        if st.button("🚀 Create Panels", type="primary"):
            with st.spinner("Creating panels... This may take a moment."):
                try:
                    panels, panel_stats = create_panels(
                        df,
                        target_dict,
                        selected_features,
                        num_panels,
                        panel_size,
                        random_seed
                    )
                    
                    st.session_state.panels = panels
                    st.session_state.panel_stats = panel_stats
                    
                    st.success(f"✓ Successfully created {len(panels)} panels!")
                    
                except Exception as e:
                    st.error(f"❌ Error creating panels: {str(e)}")
                    st.exception(e)
                    return
        
        # Show panel statistics if available
        if st.session_state.panels is not None:
            st.markdown("---")
            st.subheader("Panel Statistics")
            
            panels = st.session_state.panels
            panel_stats = st.session_state.panel_stats
            
            # Overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Panels Created", len(panels))
            with col2:
                st.metric("Samples Used", f"{panel_stats['total_used']:,}")
            with col3:
                utilization = (panel_stats['total_used'] / panel_stats['total_available']) * 100
                st.metric("Dataset Utilization", f"{utilization:.1f}%")
            
            # Individual panel statistics
            # Extract adjusted targets if adjustments were made
            adjusted_targets = None
            if 'allocation_info' in panel_stats and panel_stats['allocation_info']['adjustments_made']:
                # Build adjusted_targets dict from allocation_info
                adjusted_targets = {}
                for feature, feature_info in panel_stats['allocation_info']['features'].items():
                    if feature_info.get('needs_adjustment', False):
                        adjusted_targets[feature] = {}
                        for cat, cat_info in feature_info['categories'].items():
                            adjusted_targets[feature][cat] = cat_info['adjusted_proportion']
            
            for i, (panel, summary) in enumerate(zip(panels, panel_stats['panel_summaries'])):
                with st.expander(f"📋 Panel {i+1} Details (n={len(panel):,})", expanded=False):
                    
                    for feature in selected_features:
                        st.write(f"**{feature} Distribution:**")
                        
                        dist_table = print_distribution_table(
                            panel, feature, target_dict, f"Panel {i+1}",
                            adjusted_dict=adjusted_targets
                        )
                        st.dataframe(dist_table, use_container_width=True)
                        
                        st.markdown("---")
    
    
    # Step 4: Split Panels
    elif page == "4. Split Panels":
        st.header("Step 4: Split Panels into Sets")
        
        if st.session_state.panels is None:
            st.warning("⚠️ Please create panels first (Step 3)")
            return
        
        panels = st.session_state.panels
        target_dict = st.session_state.target_dict
        selected_features = st.session_state.selected_features
        
        st.markdown("""
        Split each panel into multiple equal, balanced sets.
        Each set will maintain the same proportional distributions as the parent panel.
        """)
        
        # Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            num_sets = st.number_input(
                "Number of Sets per Panel",
                min_value=2,
                max_value=10,
                value=2,
                help="How many sets to split each panel into (e.g., 2, 3, 4, etc.)"
            )
        
        with col2:
            split_seed = st.number_input(
                "Random Seed for Splitting",
                min_value=0,
                value=42,
                help="Set seed for reproducible splits"
            )
        
        # Info box
        st.info(f"ℹ️ Each of the {len(panels)} panels will be split into {num_sets} sets. "
                f"Total: **{len(panels) * num_sets} sets** will be created.")
        
        if st.button("✂️ Split All Panels", type="primary"):
            with st.spinner(f"Splitting panels into {num_sets} sets each... Please wait."):
                try:
                    panel_splits, split_stats = split_all_panels(
                        panels,
                        target_dict,
                        selected_features,
                        num_sets=num_sets,
                        random_state=split_seed
                    )
                    
                    st.session_state.panel_splits = panel_splits
                    st.session_state.split_stats = split_stats
                    
                    total_sets = len(panel_splits) * num_sets
                    st.success(f"✓ Successfully split {len(panels)} panels into {total_sets} sets "
                              f"({num_sets} sets per panel)!")
                    
                except Exception as e:
                    st.error(f"❌ Error splitting panels: {str(e)}")
                    st.exception(e)
                    return
        
        # Show split statistics
        if st.session_state.panel_splits is not None:
            st.markdown("---")
            st.subheader("Split Statistics")
            
            panel_splits = st.session_state.panel_splits
            split_stats = st.session_state.split_stats
            num_sets_created = split_stats.get('num_sets', 2)
            
            for panel_idx, (sets, summary) in enumerate(zip(panel_splits, split_stats['split_summaries']), 1):
                with st.expander(f"📊 Panel {panel_idx} Split Analysis", expanded=False):
                    
                    # Display sizes for all sets
                    cols = st.columns(min(num_sets_created, 5))  # Max 5 columns per row
                    for set_idx, set_df in enumerate(sets):
                        with cols[set_idx % 5]:
                            st.metric(f"Set {set_idx + 1} Size", f"{len(set_df):,}")
                    
                    st.markdown("---")
                    
                    # Compare distributions across all sets
                    for feature in selected_features:
                        st.write(f"**{feature} Distribution Across Sets:**")
                        
                        # Create comprehensive comparison table
                        comparison_data = []
                        
                        if feature in summary['comparisons']:
                            for category, cat_info in summary['comparisons'][feature].items():
                                row = {
                                    'Category': category,
                                    'Target': f"{cat_info.get('target', 0):.1%}" if cat_info.get('target') is not None else 'N/A'
                                }
                                
                                # Add column for each set
                                for set_idx in range(num_sets_created):
                                    set_val = cat_info['values'].get(f'set_{set_idx + 1}', 0)
                                    row[f'Set {set_idx + 1}'] = f"{set_val:.1%}"
                                
                                # Add deviation metrics
                                row['Max Deviation'] = f"{cat_info['max_deviation']:.1%}"
                                row['Status'] = cat_info['status']
                                
                                comparison_data.append(row)
                        
                        if comparison_data:
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True)
                        
                        st.markdown("---")
    
    
    # Step 5: Validate & Export
    elif page == "5. Validate & Export":
        st.header("Step 5: Validate & Export")
        
        if st.session_state.panel_splits is None:
            st.warning("⚠️ Please split panels first (Step 4)")
            return
        
        panel_splits = st.session_state.panel_splits
        
        # Overlap Check
        st.subheader("🔍 Overlap Verification")
        
        if st.button("Check for Overlaps"):
            with st.spinner("Checking for overlaps..."):
                # Prepare all sets for checking
                all_sets = []
                for panel_idx, sets in enumerate(panel_splits, 1):
                    for set_idx, set_df in enumerate(sets, 1):
                        all_sets.append((f"Panel {panel_idx} Set {set_idx}", set_df))
                
                overlap_results = check_overlap_between_sets(all_sets)
                
                if overlap_results['has_overlap']:
                    st.error("❌ Overlaps detected!")
                else:
                    st.success("✓ No overlaps detected! All sets are mutually exclusive.")
                
                # Show detailed results
                st.subheader("Detailed Overlap Check Results")
                overlap_df = pd.DataFrame(overlap_results['results'])
                st.dataframe(overlap_df, use_container_width=True)
        
        st.markdown("---")
        
        # Export Section
        st.subheader("💾 Export Results")
        
        num_sets_created = st.session_state.split_stats.get('num_sets', 2)
        
        st.markdown(f"""
        Export all panels and sets to CSV files. Files will be generated with clear naming:
        - `panel_1_set_1.csv`, `panel_1_set_2.csv`, ... `panel_1_set_{num_sets_created}.csv`
        - `panel_2_set_1.csv`, `panel_2_set_2.csv`, ... `panel_2_set_{num_sets_created}.csv`
        - etc.
        """)
        
        # Output directory selection
        output_dir = st.text_input(
            "Output Directory",
            value="./data",
            help="Directory where CSV files will be saved"
        )
        
        # Export button
        if st.button("📥 Export All to CSV", type="primary"):
            try:
                # Create output directory if it doesn't exist
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Export each set
                exported_files = []
                
                for panel_idx, sets in enumerate(panel_splits, 1):
                    for set_idx, set_df in enumerate(sets, 1):
                        file_path = output_path / f"panel_{panel_idx}_set_{set_idx}.csv"
                        set_df.to_csv(file_path, index=True)
                        exported_files.append(str(file_path))
                
                st.success(f"✓ Successfully exported {len(exported_files)} files to {output_dir}")
                
                # Show exported files
                st.subheader("Exported Files")
                for file in exported_files:
                    st.text(f"✓ {file}")
                
            except Exception as e:
                st.error(f"❌ Error exporting files: {str(e)}")
        
        # Individual download buttons
        st.markdown("---")
        st.subheader("Download Individual Files")
        
        for panel_idx, sets in enumerate(panel_splits, 1):
            st.markdown(f"**Panel {panel_idx}:**")
            
            # Create columns based on number of sets (max 3 per row for readability)
            sets_per_row = min(3, len(sets))
            
            for row_start in range(0, len(sets), sets_per_row):
                cols = st.columns(sets_per_row)
                for col_idx, set_idx in enumerate(range(row_start, min(row_start + sets_per_row, len(sets)))):
                    with cols[col_idx]:
                        set_df = sets[set_idx]
                        csv_data = set_df.to_csv(index=True)
                        st.download_button(
                            label=f"📥 Set {set_idx + 1}",
                            data=csv_data,
                            file_name=f"panel_{panel_idx}_set_{set_idx + 1}.csv",
                            mime="text/csv",
                            key=f"download_panel_{panel_idx}_set_{set_idx + 1}"
                        )
            
            st.markdown("")  # Add spacing between panels
        
        # Export summary report
        st.markdown("---")
        st.subheader("📊 Summary Report")
        
        if st.button("Generate Summary Report"):
            # Create comprehensive summary
            summary_text = io.StringIO()
            
            summary_text.write("="*80 + "\n")
            summary_text.write("DATA PANELING SUMMARY REPORT\n")
            summary_text.write("="*80 + "\n\n")
            
            summary_text.write(f"Total Panels Created: {len(panel_splits)}\n")
            summary_text.write(f"Total Sets Generated: {len(panel_splits) * num_sets_created}\n\n")
            
            summary_text.write("PANEL & SET SIZES:\n")
            summary_text.write("-" * 80 + "\n")
            for i, sets in enumerate(panel_splits, 1):
                size_str = ", ".join([f"Set {j+1} = {len(s):,}" for j, s in enumerate(sets)])
                summary_text.write(f"Panel {i}: {size_str}\n")
            
            summary_text.write("\n" + "="*80 + "\n")
            
            summary_report = summary_text.getvalue()
            
            st.text_area("Summary Report", summary_report, height=300)
            
            st.download_button(
                label="📥 Download Summary Report",
                data=summary_report,
                file_name="paneling_summary_report.txt",
                mime="text/plain"
            )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Status")
    
    status_items = [
        ("Data Loaded", st.session_state.df is not None),
        ("Targets Configured", bool(st.session_state.target_dict)),
        ("Panels Created", st.session_state.panels is not None),
        ("Panels Split", st.session_state.panel_splits is not None)
    ]
    
    for item, status in status_items:
        icon = "✅" if status else "⬜"
        st.sidebar.text(f"{icon} {item}")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **Data Paneling Tool v1.0**
    
    Built with Streamlit
    
    For support, contact your administrator.
    """)


if __name__ == "__main__":
    main()
