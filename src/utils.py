"""
Utility functions for data validation and checks
"""
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Set, Tuple, Optional


def validate_uploaded_file(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate the uploaded DataFrame
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"
    
    if len(df) < 100:
        return False, f"Dataset too small. Found {len(df)} rows, need at least 100."
    
    return True, "Valid"


def validate_target_proportions(target_dict: Dict[str, Dict[str, float]]) -> Tuple[bool, str]:
    """
    Validate that target proportions sum to approximately 1.0 for each feature
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    for feature, proportions in target_dict.items():
        total = sum(proportions.values())
        if not (0.99 <= total <= 1.01):
            return False, f"{feature} proportions sum to {total:.4f}, should be 1.0"
    
    return True, "Valid"


def check_availability(df: pd.DataFrame, 
                       target_dict: Dict[str, Dict[str, float]], 
                       num_panels: int, 
                       panel_size: int) -> Tuple[bool, str]:
    """
    Check if there are enough samples for the requested panels
    
    Returns:
        Tuple of (is_sufficient, message)
    """
    total_needed = num_panels * panel_size
    total_available = len(df)
    
    if total_available < total_needed:
        return False, f"Not enough samples. Need {total_needed}, have {total_available}"
    
    # Check each category
    warnings = []
    for feature, targets in target_dict.items():
        feature_dist = df[feature].value_counts(normalize=True)
        
        for category, target_prop in targets.items():
            available_prop = feature_dist.get(category, 0)
            needed_prop = target_prop
            
            if available_prop < needed_prop:
                shortfall = needed_prop - available_prop
                warnings.append(
                    f"  ⚠️ {feature}={category}: Target={target_prop:.3f}, "
                    f"Available={available_prop:.3f} (short by {shortfall:.3f})"
                )
    
    if warnings:
        message = "⚠️ Some categories may be underrepresented:\n" + "\n".join(warnings)
        return True, message
    
    return True, "✓ Sufficient samples available for all categories"


def print_distribution_table(df: pd.DataFrame, 
                            feature: str, 
                            target_dict: Optional[Dict[str, float]] = None,
                            set_name: str = "Dataset") -> pd.DataFrame:
    """
    Create a distribution comparison table for display
    
    Returns:
        DataFrame with distribution statistics
    """
    actual = df[feature].value_counts(normalize=True).sort_index()
    
    if target_dict and feature in target_dict:
        rows = []
        for category in sorted(target_dict[feature].keys()):
            target_val = target_dict[feature][category]
            actual_val = actual.get(category, 0)
            deviation = actual_val - target_val
            count = len(df[df[feature] == category])
            
            status = "✓" if abs(deviation) < 0.03 else "✗"
            
            rows.append({
                'Category': category,
                'Count': count,
                'Target': f"{target_val:.3f}",
                'Actual': f"{actual_val:.3f}",
                'Deviation': f"{deviation:+.3f}",
                'Status': status
            })
        
        result_df = pd.DataFrame(rows)
    else:
        rows = []
        for category, proportion in actual.items():
            count = len(df[df[feature] == category])
            rows.append({
                'Category': category,
                'Count': count,
                'Proportion': f"{proportion:.3f}"
            })
        result_df = pd.DataFrame(rows)
    
    return result_df


def check_overlap_between_sets(set_list: List[Tuple[str, pd.DataFrame]]) -> Dict:
    """
    Check for overlap between all pairs of sets
    
    Args:
        set_list: List of tuples (set_name, dataframe)
    
    Returns:
        Dictionary with overlap information
    """
    overlap_results = []
    has_overlap = False
    
    for i in range(len(set_list)):
        for j in range(i + 1, len(set_list)):
            name_i, df_i = set_list[i]
            name_j, df_j = set_list[j]
            
            indices_i = set(df_i.index)
            indices_j = set(df_j.index)
            
            overlap = len(indices_i & indices_j)
            
            if overlap > 0:
                has_overlap = True
                status = "❌ OVERLAP"
            else:
                status = "✓ No overlap"
            
            overlap_results.append({
                'Set 1': name_i,
                'Set 2': name_j,
                'Overlap Count': overlap,
                'Status': status
            })
    
    return {
        'has_overlap': has_overlap,
        'results': overlap_results
    }


def create_comparison_table(set_a: pd.DataFrame, 
                           set_b: pd.DataFrame, 
                           feature: str,
                           name_a: str = "Set A",
                           name_b: str = "Set B") -> pd.DataFrame:
    """
    Create a comparison table for two sets
    
    Returns:
        DataFrame with side-by-side comparison
    """
    dist_a = set_a[feature].value_counts(normalize=True).sort_index()
    dist_b = set_b[feature].value_counts(normalize=True).sort_index()
    
    all_categories = sorted(set(dist_a.index) | set(dist_b.index))
    
    rows = []
    for cat in all_categories:
        val_a = dist_a.get(cat, 0)
        val_b = dist_b.get(cat, 0)
        diff = abs(val_a - val_b)
        status = "✓" if diff < 0.02 else "✗"
        
        rows.append({
            'Category': cat,
            f'{name_a} Prop': f"{val_a:.3f}",
            f'{name_b} Prop': f"{val_b:.3f}",
            'Difference': f"{diff:.3f}",
            'Status': status
        })
    
    return pd.DataFrame(rows)


def format_number(num: int) -> str:
    """Format number with thousands separator"""
    return f"{num:,}"


def calculate_max_possible_panels(df: pd.DataFrame, panel_size: int) -> int:
    """Calculate maximum possible number of panels given dataset size"""
    return len(df) // panel_size


def get_feature_statistics(df: pd.DataFrame, features: List[str]) -> Dict:
    """
    Get comprehensive statistics for selected features
    
    Returns:
        Dictionary with feature statistics
    """
    stats = {}
    
    for feature in features:
        value_counts = df[feature].value_counts()
        proportions = df[feature].value_counts(normalize=True)
        
        stats[feature] = {
            'unique_values': len(value_counts),
            'value_counts': value_counts.to_dict(),
            'proportions': proportions.to_dict(),
            'categories': sorted(df[feature].unique().tolist())
        }
    
    return stats
