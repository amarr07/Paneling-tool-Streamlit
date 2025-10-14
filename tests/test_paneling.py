"""
Test script to verify the paneling logic works correctly
Run this to test the core functionality without the Streamlit UI
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
import numpy as np
from paneling import create_panels, split_all_panels
from utils import check_overlap_between_sets

def test_basic_paneling():
    """Test basic paneling functionality"""
    print("="*80)
    print("TESTING DATA PANELING TOOL")
    print("="*80)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 10000
    
    sample_data = {
        'ID': range(n_samples),
        'Gender': np.random.choice(['Male', 'Female'], n_samples, p=[0.5, 0.5]),
        'Zone': np.random.choice(['Zone A', 'Zone B', 'Zone C'], n_samples, p=[0.33, 0.33, 0.34]),
        'Party_2020': np.random.choice(['Party 1', 'Party 2', 'Party 3'], n_samples, p=[0.4, 0.35, 0.25]),
        'Value': np.random.randint(1, 100, n_samples)
    }
    
    df = pd.DataFrame(sample_data)
    print(f"\n✓ Created test dataset: {len(df)} rows, {len(df.columns)} columns")
    
    # Define targets
    targets = {
        'Gender': {'Male': 0.5, 'Female': 0.5},
        'Zone': {'Zone A': 0.33, 'Zone B': 0.33, 'Zone C': 0.34},
        'Party_2020': {'Party 1': 0.4, 'Party 2': 0.35, 'Party 3': 0.25}
    }
    
    features = ['Gender', 'Zone', 'Party_2020']
    
    print(f"\n✓ Configured targets for {len(features)} features")
    
    # Test panel creation
    print("\n" + "="*80)
    print("TEST 1: Creating 3 non-overlapping panels")
    print("="*80)
    
    try:
        panels, stats = create_panels(
            df, targets, features,
            num_panels=3,
            panel_size=1000,
            random_state=42
        )
        
        print(f"\n✓ Successfully created {len(panels)} panels")
        
        for i, panel in enumerate(panels, 1):
            print(f"\nPanel {i}: {len(panel)} samples")
            for feature in features:
                dist = panel[feature].value_counts(normalize=True)
                print(f"  {feature}: {dict(dist.round(3))}")
        
    except Exception as e:
        print(f"\n❌ Panel creation failed: {e}")
        return False
    
    # Test panel splitting
    print("\n" + "="*80)
    print("TEST 2: Splitting panels into Set A and Set B")
    print("="*80)
    
    try:
        splits, split_stats = split_all_panels(
            panels, targets, features,
            random_state=42
        )
        
        print(f"\n✓ Successfully split {len(panels)} panels into {len(splits)*2} sets")
        
        for i, (set_a, set_b) in enumerate(splits, 1):
            print(f"\nPanel {i}: Set A = {len(set_a)}, Set B = {len(set_b)}")
        
    except Exception as e:
        print(f"\n❌ Panel splitting failed: {e}")
        return False
    
    # Test overlap detection
    print("\n" + "="*80)
    print("TEST 3: Checking for overlaps")
    print("="*80)
    
    try:
        all_sets = []
        for i, (set_a, set_b) in enumerate(splits, 1):
            all_sets.append((f"Panel {i} Set A", set_a))
            all_sets.append((f"Panel {i} Set B", set_b))
        
        overlap_results = check_overlap_between_sets(all_sets)
        
        if overlap_results['has_overlap']:
            print("\n❌ FAIL: Overlaps detected!")
            return False
        else:
            print("\n✓ PASS: No overlaps detected!")
        
        print(f"\nChecked {len(overlap_results['results'])} pairs")
        
    except Exception as e:
        print(f"\n❌ Overlap check failed: {e}")
        return False
    
    # All tests passed
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nThe paneling tool is working correctly.")
    print("You can now run the Streamlit app: streamlit run src/main.py")
    
    return True

if __name__ == "__main__":
    success = test_basic_paneling()
    sys.exit(0 if success else 1)
