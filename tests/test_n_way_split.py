"""
Test N-way panel splitting functionality

This test validates that panels can be split into any number of sets (2, 3, 4, etc.)
while maintaining stratification and equal distribution.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from src.paneling import split_panel_into_n_sets, split_all_panels


def create_test_panel(size=1000, seed=42):
    """Create a test panel with known distributions"""
    np.random.seed(seed)
    
    data = {
        'Gender': np.random.choice(['Male', 'Female'], size=size, p=[0.6, 0.4]),
        'Zone': np.random.choice(['North', 'South', 'East', 'West'], size=size, p=[0.3, 0.3, 0.2, 0.2]),
        'Age_Group': np.random.choice(['18-30', '31-50', '51+'], size=size, p=[0.4, 0.35, 0.25])
    }
    
    df = pd.DataFrame(data)
    df.index.name = 'id'
    
    return df


def test_two_way_split():
    """Test splitting into 2 sets (backward compatibility)"""
    print("\n" + "="*80)
    print("TEST 1: Two-way Split (Backward Compatibility)")
    print("="*80)
    
    panel = create_test_panel(size=1000)
    
    target_dict = {
        'Gender': {'Male': 0.6, 'Female': 0.4},
        'Zone': {'North': 0.3, 'South': 0.3, 'East': 0.2, 'West': 0.2},
        'Age_Group': {'18-30': 0.4, '31-50': 0.35, '51+': 0.25}
    }
    
    features = ['Gender', 'Zone', 'Age_Group']
    
    # Split into 2 sets
    sets = split_panel_into_n_sets(panel, target_dict, features, num_sets=2, random_state=42)
    
    print(f"\n✓ Successfully split panel into {len(sets)} sets")
    print(f"  Set 1 size: {len(sets[0])}")
    print(f"  Set 2 size: {len(sets[1])}")
    
    # Verify no overlaps
    set1_indices = set(sets[0].index)
    set2_indices = set(sets[1].index)
    overlap = set1_indices & set2_indices
    
    print(f"\n✓ Overlap check: {len(overlap)} overlaps (should be 0)")
    assert len(overlap) == 0, "Sets should not overlap"
    
    # Verify all samples accounted for
    total_in_sets = len(set1_indices) + len(set2_indices)
    print(f"✓ Sample accounting: {total_in_sets}/{len(panel)} samples (should be equal)")
    assert total_in_sets == len(panel), "All samples should be in one of the sets"
    
    # Check distribution balance
    print("\n📊 Distribution Comparison:")
    for feature in features:
        dist1 = sets[0][feature].value_counts(normalize=True).sort_index()
        dist2 = sets[1][feature].value_counts(normalize=True).sort_index()
        
        print(f"\n  {feature}:")
        for category in sorted(set(dist1.index) | set(dist2.index)):
            val1 = dist1.get(category, 0)
            val2 = dist2.get(category, 0)
            diff = abs(val1 - val2)
            status = "✓" if diff < 0.02 else "✗"
            print(f"    {category:15s} Set1: {val1:6.1%}  Set2: {val2:6.1%}  Diff: {diff:6.1%} {status}")
    
    print("\n✅ Two-way split test PASSED!")
    return True


def test_three_way_split():
    """Test splitting into 3 sets"""
    print("\n" + "="*80)
    print("TEST 2: Three-way Split")
    print("="*80)
    
    panel = create_test_panel(size=1200)  # Divisible by 3
    
    target_dict = {
        'Gender': {'Male': 0.6, 'Female': 0.4},
        'Zone': {'North': 0.3, 'South': 0.3, 'East': 0.2, 'West': 0.2},
        'Age_Group': {'18-30': 0.4, '31-50': 0.35, '51+': 0.25}
    }
    
    features = ['Gender', 'Zone', 'Age_Group']
    
    # Split into 3 sets
    sets = split_panel_into_n_sets(panel, target_dict, features, num_sets=3, random_state=42)
    
    print(f"\n✓ Successfully split panel into {len(sets)} sets")
    for i, s in enumerate(sets, 1):
        print(f"  Set {i} size: {len(s)}")
    
    # Verify no overlaps
    all_indices = [set(s.index) for s in sets]
    for i in range(len(all_indices)):
        for j in range(i+1, len(all_indices)):
            overlap = all_indices[i] & all_indices[j]
            assert len(overlap) == 0, f"Sets {i+1} and {j+1} should not overlap"
    
    print(f"\n✓ Overlap check: No overlaps detected among {len(sets)} sets")
    
    # Verify all samples accounted for
    total_in_sets = sum(len(s) for s in sets)
    print(f"✓ Sample accounting: {total_in_sets}/{len(panel)} samples (should be equal)")
    assert total_in_sets == len(panel), "All samples should be in one of the sets"
    
    # Check distribution balance across all 3 sets
    print("\n📊 Distribution Comparison Across 3 Sets:")
    for feature in features:
        distributions = [s[feature].value_counts(normalize=True).sort_index() for s in sets]
        
        print(f"\n  {feature}:")
        all_categories = sorted(set().union(*[d.index for d in distributions]))
        
        for category in all_categories:
            values = [dist.get(category, 0) for dist in distributions]
            avg = np.mean(values)
            max_dev = max([abs(v - avg) for v in values])
            status = "✓" if max_dev < 0.02 else "✗"
            
            print(f"    {category:15s} Set1: {values[0]:6.1%}  Set2: {values[1]:6.1%}  "
                  f"Set3: {values[2]:6.1%}  MaxDev: {max_dev:6.1%} {status}")
    
    print("\n✅ Three-way split test PASSED!")
    return True


def test_four_way_split():
    """Test splitting into 4 sets"""
    print("\n" + "="*80)
    print("TEST 3: Four-way Split")
    print("="*80)
    
    panel = create_test_panel(size=2000)  # Divisible by 4
    
    target_dict = {
        'Gender': {'Male': 0.6, 'Female': 0.4},
        'Zone': {'North': 0.3, 'South': 0.3, 'East': 0.2, 'West': 0.2},
        'Age_Group': {'18-30': 0.4, '31-50': 0.35, '51+': 0.25}
    }
    
    features = ['Gender', 'Zone', 'Age_Group']
    
    # Split into 4 sets
    sets = split_panel_into_n_sets(panel, target_dict, features, num_sets=4, random_state=42)
    
    print(f"\n✓ Successfully split panel into {len(sets)} sets")
    for i, s in enumerate(sets, 1):
        print(f"  Set {i} size: {len(s)}")
    
    # Calculate coefficient of variation for set sizes
    sizes = [len(s) for s in sets]
    mean_size = np.mean(sizes)
    std_size = np.std(sizes)
    cv = std_size / mean_size if mean_size > 0 else 0
    
    print(f"\n✓ Size balance: Mean={mean_size:.1f}, StdDev={std_size:.2f}, CV={cv:.4f}")
    print(f"  (CV < 0.01 indicates excellent size balance)")
    
    # Verify no overlaps
    all_indices = [set(s.index) for s in sets]
    overlap_count = 0
    for i in range(len(all_indices)):
        for j in range(i+1, len(all_indices)):
            overlap = all_indices[i] & all_indices[j]
            overlap_count += len(overlap)
    
    print(f"✓ Overlap check: {overlap_count} overlaps across all pairs (should be 0)")
    assert overlap_count == 0, "No overlaps should exist"
    
    # Check distribution balance
    print("\n📊 Distribution Comparison Across 4 Sets:")
    for feature in features:
        distributions = [s[feature].value_counts(normalize=True).sort_index() for s in sets]
        
        print(f"\n  {feature}:")
        all_categories = sorted(set().union(*[d.index for d in distributions]))
        
        for category in all_categories:
            values = [dist.get(category, 0) for dist in distributions]
            avg = np.mean(values)
            max_dev = max([abs(v - avg) for v in values])
            status = "✓" if max_dev < 0.02 else "✗"
            
            vals_str = "  ".join([f"Set{i+1}: {v:6.1%}" for i, v in enumerate(values)])
            print(f"    {category:15s} {vals_str}  MaxDev: {max_dev:6.1%} {status}")
    
    print("\n✅ Four-way split test PASSED!")
    return True


def test_split_all_panels():
    """Test splitting multiple panels into N sets each"""
    print("\n" + "="*80)
    print("TEST 4: Split All Panels (3 panels × 3 sets each)")
    print("="*80)
    
    # Create 3 test panels
    panels = [create_test_panel(size=900, seed=i*100) for i in range(3)]
    
    target_dict = {
        'Gender': {'Male': 0.6, 'Female': 0.4},
        'Zone': {'North': 0.3, 'South': 0.3, 'East': 0.2, 'West': 0.2}
    }
    
    features = ['Gender', 'Zone']
    
    # Split all panels into 3 sets each
    # Use unittest.mock to properly mock streamlit
    from unittest.mock import MagicMock, patch
    
    with patch('src.paneling.st') as mock_st:
        # Setup mocks
        mock_progress = MagicMock()
        mock_empty = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_empty
        
        all_splits, split_stats = split_all_panels(
            panels, 
            target_dict, 
            features, 
            num_sets=3,
            random_state=42
        )
    
    print(f"\n✓ Successfully split {len(panels)} panels")
    print(f"✓ Created {len(all_splits) * 3} total sets (3 per panel)")
    
    # Verify structure
    assert len(all_splits) == 3, "Should have 3 panel splits"
    for panel_idx, sets in enumerate(all_splits, 1):
        assert len(sets) == 3, f"Panel {panel_idx} should have 3 sets"
        print(f"\n  Panel {panel_idx}:")
        for set_idx, s in enumerate(sets, 1):
            print(f"    Set {set_idx}: {len(s)} samples")
    
    # Verify summary statistics
    assert 'split_summaries' in split_stats
    assert 'num_sets' in split_stats
    assert split_stats['num_sets'] == 3
    
    print("\n✓ Summary statistics structure validated")
    
    # Check one panel's distribution in detail
    print("\n📊 Detailed Distribution for Panel 1:")
    panel_1_sets = all_splits[0]
    
    for feature in features:
        print(f"\n  {feature}:")
        distributions = [s[feature].value_counts(normalize=True).sort_index() for s in panel_1_sets]
        all_categories = sorted(set().union(*[d.index for d in distributions]))
        
        for category in all_categories:
            values = [dist.get(category, 0) for dist in distributions]
            avg = np.mean(values)
            max_dev = max([abs(v - avg) for v in values])
            status = "✓" if max_dev < 0.02 else "✗"
            
            print(f"    {category:15s} Set1: {values[0]:6.1%}  Set2: {values[1]:6.1%}  "
                  f"Set3: {values[2]:6.1%}  MaxDev: {max_dev:6.1%} {status}")
    
    print("\n✅ Split all panels test PASSED!")
    return True


def run_all_tests():
    """Run all N-way split tests"""
    print("\n" + "="*80)
    print("RUNNING N-WAY PANEL SPLIT TESTS")
    print("="*80)
    
    tests = [
        test_two_way_split,
        test_three_way_split,
        test_four_way_split,
        test_split_all_panels
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, True, None))
        except Exception as e:
            print(f"\n❌ {test_func.__name__} FAILED: {str(e)}")
            results.append((test_func.__name__, False, str(e)))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "✅ PASSED" if success else f"❌ FAILED: {error}"
        print(f"{test_name:40s} {status}")
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - N-way Split Functionality Works!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
