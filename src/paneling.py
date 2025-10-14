"""
Core paneling logic - Creating balanced, non-overlapping panels and splits
Based on reference.py with iterative proportional fitting approach
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import streamlit as st


def check_master_distribution(df: pd.DataFrame, 
                              target_dict: Dict[str, Dict[str, float]], 
                              features: List[str]) -> Dict:
    """
    Check if master dataset has enough samples for targets
    Returns detailed distribution information
    """
    distribution_info = {
        'features': {},
        'warnings': [],
        'shortfalls': []
    }
    
    for feature in features:
        if feature not in df.columns:
            distribution_info['warnings'].append(f"Feature '{feature}' not found in dataset")
            continue
        
        dist = df[feature].value_counts(normalize=True).sort_index()
        feature_info = {
            'distribution': dist.to_dict(),
            'counts': df[feature].value_counts().to_dict(),
            'categories': {}
        }
        
        if feature in target_dict:
            for category, target in target_dict[feature].items():
                available = dist.get(category, 0)
                shortfall = max(0, target - available)
                
                feature_info['categories'][category] = {
                    'target': target,
                    'available': available,
                    'shortfall': shortfall,
                    'status': 'OK' if available >= target else 'SHORT'
                }
                
                if available < target:
                    distribution_info['shortfalls'].append({
                        'feature': feature,
                        'category': category,
                        'target': target,
                        'available': available,
                        'shortfall': shortfall
                    })
        
        distribution_info['features'][feature] = feature_info
    
    return distribution_info


def create_balanced_sample(df: pd.DataFrame, 
                          target_dict: Dict[str, Dict[str, float]], 
                          sample_size: int,
                          exclude_indices: Optional[Set] = None,
                          random_state: Optional[int] = None) -> pd.DataFrame:
    """
    Create a sample with iterative proportional fitting approach
    
    Uses multi-dimensional stratified sampling to match target distributions
    across all specified features simultaneously.
    
    Args:
        df: Master dataframe with 'original_index' column
        target_dict: Dictionary of target proportions for each feature
        sample_size: Desired sample size
        exclude_indices: Set of indices to exclude (already used)
        random_state: Random seed for reproducibility
    
    Returns:
        Sampled dataframe matching target distributions
    """
    if exclude_indices is None:
        exclude_indices = set()
    
    # Filter out already used indices
    available_df = df[~df['original_index'].isin(exclude_indices)].copy().reset_index(drop=True)
    
    if len(available_df) < sample_size:
        st.warning(f"⚠️ Only {len(available_df)} samples available, requested {sample_size}")
        return available_df.head(sample_size)
    
    if random_state is not None:
        np.random.seed(random_state)
    
    # Get all features to stratify on
    features = list(target_dict.keys())
    
    # Calculate target counts for each category
    target_counts = {}
    for feature in features:
        target_counts[feature] = {
            cat: int(np.round(sample_size * prob))
            for cat, prob in target_dict[feature].items()
        }
    
    selected_indices = []
    
    # Multi-dimensional stratified sampling
    # Create joint stratification across all features
    if len(features) >= 2:
        # For multiple features, do hierarchical sampling
        # Start with the first feature as primary stratification
        primary_feature = features[0]
        
        for primary_cat, primary_target in target_counts[primary_feature].items():
            primary_pool = available_df[available_df[primary_feature] == primary_cat]
            
            if len(primary_pool) == 0:
                continue
            
            # Within primary category, stratify by other features
            if len(features) > 1:
                secondary_feature = features[1]
                
                for secondary_cat, secondary_prob in target_dict[secondary_feature].items():
                    joint_target = int(np.round(primary_target * secondary_prob))
                    
                    if joint_target == 0:
                        continue
                    
                    joint_pool = primary_pool[primary_pool[secondary_feature] == secondary_cat]
                    
                    if len(joint_pool) == 0:
                        continue
                    
                    # If we have more features, continue stratification
                    if len(features) > 2:
                        for remaining_feature in features[2:]:
                            # Balance within this joint group
                            for remaining_cat, remaining_prob in target_dict[remaining_feature].items():
                                nested_target = int(np.round(joint_target * remaining_prob))
                                
                                if nested_target == 0:
                                    continue
                                
                                nested_pool = joint_pool[joint_pool[remaining_feature] == remaining_cat]
                                
                                if len(nested_pool) >= nested_target:
                                    sample = nested_pool.sample(n=nested_target, replace=False)
                                elif len(nested_pool) > 0:
                                    sample = nested_pool
                                else:
                                    continue
                                
                                selected_indices.extend(sample.index.tolist())
                    else:
                        # Only two features, sample directly
                        if len(joint_pool) >= joint_target:
                            sample = joint_pool.sample(n=joint_target, replace=False)
                        else:
                            sample = joint_pool
                        
                        selected_indices.extend(sample.index.tolist())
    else:
        # Single feature stratification
        feature = features[0]
        for cat, target_count in target_counts[feature].items():
            cat_pool = available_df[available_df[feature] == cat]
            
            if len(cat_pool) >= target_count:
                sample = cat_pool.sample(n=target_count, replace=False)
            else:
                sample = cat_pool
            
            selected_indices.extend(sample.index.tolist())
    
    # Get the sampled dataframe
    sampled_df = available_df.loc[selected_indices].copy()
    
    # Remove duplicates if any
    sampled_df = sampled_df.drop_duplicates()
    
    # If we don't have enough samples, fill up to target with random sampling
    if len(sampled_df) < sample_size:
        remaining_needed = sample_size - len(sampled_df)
        remaining_pool = available_df[~available_df.index.isin(selected_indices)]
        
        if len(remaining_pool) >= remaining_needed:
            additional = remaining_pool.sample(n=remaining_needed, replace=False)
            sampled_df = pd.concat([sampled_df, additional])
    
    # If we have too many, trim to exact size
    elif len(sampled_df) > sample_size:
        sampled_df = sampled_df.sample(n=sample_size, replace=False)
    
    # Return with original indices from master
    original_indices = sampled_df['original_index'].values
    return df[df['original_index'].isin(original_indices)].copy()


def create_panels(master_df: pd.DataFrame,
                 target_dict: Dict[str, Dict[str, float]],
                 features: List[str],
                 num_panels: int,
                 panel_size: int,
                 random_state: int = 42) -> Tuple[List[pd.DataFrame], Dict]:
    """
    Create multiple non-overlapping panels with balanced distributions
    
    Returns:
        Tuple of (list of panels, summary statistics)
    """
    # Add original index for tracking
    master_df = master_df.reset_index(drop=False).rename(columns={'index': 'original_index'})
    master_df.index.name = 'index'
    
    # Check master distribution
    dist_info = check_master_distribution(master_df, target_dict, features)
    
    panels = []
    used_indices = set()
    panel_summaries = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(num_panels):
        status_text.text(f"Creating Panel {i+1} of {num_panels}...")
        progress_bar.progress((i + 1) / num_panels)
        
        panel = create_balanced_sample(
            master_df,
            target_dict,
            panel_size,
            used_indices,
            random_state=random_state + i
        )
        
        panels.append(panel)
        used_indices.update(panel['original_index'].values)
        
        # Calculate summary statistics
        summary = {
            'panel_number': i + 1,
            'size': len(panel),
            'distributions': {}
        }
        
        for feature in features:
            actual = panel[feature].value_counts(normalize=True).sort_index()
            
            feature_summary = {}
            if feature in target_dict:
                for cat, target in target_dict[feature].items():
                    actual_val = actual.get(cat, 0)
                    deviation = actual_val - target
                    
                    feature_summary[cat] = {
                        'target': target,
                        'actual': actual_val,
                        'deviation': deviation,
                        'status': 'Match' if abs(deviation) < 0.03 else 'Deviation'
                    }
            
            summary['distributions'][feature] = feature_summary
        
        panel_summaries.append(summary)
    
    progress_bar.empty()
    status_text.empty()
    
    # Restore original index structure
    panels = [p.set_index('original_index') for p in panels]
    
    return panels, {
        'master_distribution': dist_info,
        'panel_summaries': panel_summaries,
        'total_used': len(used_indices),
        'total_available': len(master_df)
    }


def split_panel_into_two(panel: pd.DataFrame,
                         target_dict: Dict[str, Dict[str, float]],
                         features: List[str],
                         random_state: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a panel into two equal sets while maintaining proportions
    
    Uses joint stratification across all features to ensure balanced splits.
    
    Args:
        panel: Panel dataframe to split
        target_dict: Target distributions (for reference)
        features: List of features to maintain balance for
        random_state: Random seed
    
    Returns:
        Tuple of (Set A, Set B)
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    set_a_indices = []
    set_b_indices = []
    
    panel_copy = panel.copy()
    
    # Create stratification groups based on all target features
    strata_cols = [f for f in features if f in panel_copy.columns]
    
    if len(strata_cols) > 0:
        # Combine all features into a single stratification key
        panel_copy['strata'] = panel_copy[strata_cols[0]].astype(str)
        for col in strata_cols[1:]:
            panel_copy['strata'] = panel_copy['strata'] + '_' + panel_copy[col].astype(str)
        
        # For each unique stratum, split 50-50
        for stratum in panel_copy['strata'].unique():
            stratum_indices = panel_copy[panel_copy['strata'] == stratum].index.tolist()
            
            # Shuffle the indices
            np.random.shuffle(stratum_indices)
            
            # Split approximately 50-50
            mid_point = len(stratum_indices) // 2
            set_a_indices.extend(stratum_indices[:mid_point])
            set_b_indices.extend(stratum_indices[mid_point:])
    else:
        # Fallback: simple random split
        all_indices = panel.index.tolist()
        np.random.shuffle(all_indices)
        mid_point = len(all_indices) // 2
        set_a_indices = all_indices[:mid_point]
        set_b_indices = all_indices[mid_point:]
    
    set_a = panel.loc[set_a_indices]
    set_b = panel.loc[set_b_indices]
    
    return set_a, set_b


def split_all_panels(panels: List[pd.DataFrame],
                    target_dict: Dict[str, Dict[str, float]],
                    features: List[str],
                    random_state: int = 42) -> Tuple[List[Tuple[pd.DataFrame, pd.DataFrame]], Dict]:
    """
    Split all panels into two sets each
    
    Returns:
        Tuple of (list of (Set A, Set B) tuples, summary statistics)
    """
    all_splits = []
    split_summaries = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, panel in enumerate(panels, 1):
        status_text.text(f"Splitting Panel {i} of {len(panels)}...")
        progress_bar.progress(i / len(panels))
        
        set_a, set_b = split_panel_into_two(
            panel, 
            target_dict, 
            features,
            random_state=random_state + i
        )
        
        all_splits.append((set_a, set_b))
        
        # Calculate split summary
        summary = {
            'panel_number': i,
            'set_a_size': len(set_a),
            'set_b_size': len(set_b),
            'comparisons': {}
        }
        
        for feature in features:
            if feature not in set_a.columns:
                continue
            
            dist_a = set_a[feature].value_counts(normalize=True).sort_index()
            dist_b = set_b[feature].value_counts(normalize=True).sort_index()
            
            all_categories = sorted(set(dist_a.index) | set(dist_b.index))
            
            feature_comparison = {}
            for cat in all_categories:
                val_a = dist_a.get(cat, 0)
                val_b = dist_b.get(cat, 0)
                diff = abs(val_a - val_b)
                
                feature_comparison[cat] = {
                    'set_a': val_a,
                    'set_b': val_b,
                    'difference': diff,
                    'status': 'Match' if diff < 0.02 else 'Deviation'
                }
            
            summary['comparisons'][feature] = feature_comparison
        
        split_summaries.append(summary)
    
    progress_bar.empty()
    status_text.empty()
    
    return all_splits, {'split_summaries': split_summaries}
