"""
Streamlit Data Paneling Tool
Main application interface for creating balanced, non-overlapping data panels
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from paneling import (
    check_master_distribution,
    create_panels,
    split_all_panels
)
from utils import (
    validate_uploaded_file,
    validate_target_proportions,
    check_availability,
    print_distribution_table,
    check_overlap_between_sets,
    create_comparison_table,
    calculate_max_possible_panels,
    get_feature_statistics
)


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
    - Split each panel into two balanced sets (Set A & Set B)
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
            for i, (panel, summary) in enumerate(zip(panels, panel_stats['panel_summaries'])):
                with st.expander(f"📋 Panel {i+1} Details (n={len(panel):,})", expanded=False):
                    
                    for feature in selected_features:
                        st.write(f"**{feature} Distribution:**")
                        
                        dist_table = print_distribution_table(
                            panel, feature, target_dict, f"Panel {i+1}"
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
        Split each panel into two equal, balanced sets (Set A and Set B).
        Each set will maintain the same proportional distributions as the parent panel.
        """)
        
        # Random seed for splitting
        split_seed = st.number_input(
            "Random Seed for Splitting",
            min_value=0,
            value=42,
            help="Set seed for reproducible splits"
        )
        
        if st.button("✂️ Split All Panels", type="primary"):
            with st.spinner("Splitting panels... Please wait."):
                try:
                    panel_splits, split_stats = split_all_panels(
                        panels,
                        target_dict,
                        selected_features,
                        split_seed
                    )
                    
                    st.session_state.panel_splits = panel_splits
                    st.session_state.split_stats = split_stats
                    
                    st.success(f"✓ Successfully split {len(panels)} panels into {len(panel_splits) * 2} sets!")
                    
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
            
            for i, ((set_a, set_b), summary) in enumerate(zip(panel_splits, split_stats['split_summaries']), 1):
                with st.expander(f"📊 Panel {i} Split Analysis", expanded=False):
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"Set A Size", f"{len(set_a):,}")
                    with col2:
                        st.metric(f"Set B Size", f"{len(set_b):,}")
                    
                    st.markdown("---")
                    
                    # Compare distributions
                    for feature in selected_features:
                        st.write(f"**{feature} Comparison:**")
                        
                        comparison_table = create_comparison_table(
                            set_a, set_b, feature,
                            f"Panel {i} Set A", f"Panel {i} Set B"
                        )
                        st.dataframe(comparison_table, use_container_width=True)
                        
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
                for i, (set_a, set_b) in enumerate(panel_splits, 1):
                    all_sets.append((f"Panel {i} Set A", set_a))
                    all_sets.append((f"Panel {i} Set B", set_b))
                
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
        
        st.markdown("""
        Export all panels and sets to CSV files. Files will be generated with clear naming:
        - `panel_1_set_a.csv`, `panel_1_set_b.csv`
        - `panel_2_set_a.csv`, `panel_2_set_b.csv`
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
                
                for i, (set_a, set_b) in enumerate(panel_splits, 1):
                    file_a = output_path / f"panel_{i}_set_a.csv"
                    file_b = output_path / f"panel_{i}_set_b.csv"
                    
                    set_a.to_csv(file_a, index=True)
                    set_b.to_csv(file_b, index=True)
                    
                    exported_files.append(str(file_a))
                    exported_files.append(str(file_b))
                
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
        
        for i, (set_a, set_b) in enumerate(panel_splits, 1):
            col1, col2 = st.columns(2)
            
            with col1:
                csv_a = set_a.to_csv(index=True)
                st.download_button(
                    label=f"📥 Download Panel {i} Set A",
                    data=csv_a,
                    file_name=f"panel_{i}_set_a.csv",
                    mime="text/csv"
                )
            
            with col2:
                csv_b = set_b.to_csv(index=True)
                st.download_button(
                    label=f"📥 Download Panel {i} Set B",
                    data=csv_b,
                    file_name=f"panel_{i}_set_b.csv",
                    mime="text/csv"
                )
        
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
            summary_text.write(f"Total Sets Generated: {len(panel_splits) * 2}\n\n")
            
            summary_text.write("PANEL & SET SIZES:\n")
            summary_text.write("-" * 80 + "\n")
            for i, (set_a, set_b) in enumerate(panel_splits, 1):
                summary_text.write(f"Panel {i}: Set A = {len(set_a):,}, Set B = {len(set_b):,}\n")
            
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
