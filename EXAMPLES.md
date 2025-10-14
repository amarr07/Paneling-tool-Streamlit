# Example Use Cases & Scenarios

## Use Case 1: Political Survey Panel Creation (Bihar Example)

### Scenario
Create balanced survey panels for a political research study in Bihar, maintaining representation across demographics and voting patterns.

### Dataset
- **File**: Bihar_panels.xlsx
- **Size**: 43,853 respondents
- **Columns**: Mobile Number, AC No., Gender, 2025 AE, 2020 AE, 2024 GE, Caste, Income, Zone, etc.

### Requirements
- 3 independent panels for multi-wave survey
- Each panel: 3,150 respondents
- Stratification: Gender, Zone, 2020 AE, 2024 GE
- Each panel split into Set A and Set B for treatment/control

### Configuration

**Step 1: Upload**
- Upload Bihar_panels.xlsx

**Step 2: Target Configuration**
```
Gender:
  • Male: 50%
  • Female: 50%

Zone (10 zones):
  • Tirhut: 19.05%
  • Darbhanga: 9.52%
  • Kosi: 7.14%
  • Purnia: 9.52%
  • Saran: 9.52%
  • Munger: 9.52%
  • Bhagalpur: 7.14%
  • Patna: 9.52%
  • Bhojpur: 9.52%
  • Magadh: 9.52%

2020 Assembly Election:
  • INC: 10%
  • BJP: 20%
  • Others: 27%
  • JD(U): 15%
  • LJP: 6%
  • RJD: 23%

2024 General Election:
  • BJP: 21%
  • RJD: 22%
  • Others: 23%
  • INC: 9%
  • JD(U): 19%
  • LJP: 7%
```

**Step 3: Panel Creation**
- Number of panels: 3
- Panel size: 3,150
- Random seed: 42

**Step 4: Split Panels**
- Each panel → Set A (1,575) + Set B (1,575)
- Random seed: 42

**Step 5: Export**
- 6 CSV files generated
- Total samples used: 9,450 of 43,853 (21.5%)

### Expected Output
```
✓ panel_1_set_a.csv (1,575 rows)
✓ panel_1_set_b.csv (1,575 rows)
✓ panel_2_set_a.csv (1,575 rows)
✓ panel_2_set_b.csv (1,575 rows)
✓ panel_3_set_a.csv (1,575 rows)
✓ panel_3_set_b.csv (1,575 rows)
```

### Use in Research
- **Wave 1**: Panel 1 (baseline)
- **Wave 2**: Panel 2 (mid-point)
- **Wave 3**: Panel 3 (final)
- **A/B Testing**: Set A receives treatment, Set B is control

---

## Use Case 2: Customer Segmentation for Marketing Campaign

### Scenario
E-commerce company wants to test new marketing messages on balanced customer segments.

### Dataset
- **Size**: 50,000 customers
- **Stratification**: Age Group, Region, Purchase History, Customer Tier

### Requirements
- 4 panels for different message variants
- Each panel: 2,000 customers
- Ensure representation across all segments

### Configuration

**Target Proportions:**
```
Age Group:
  • 18-25: 20%
  • 26-35: 30%
  • 36-45: 25%
  • 46-55: 15%
  • 56+: 10%

Region:
  • North: 25%
  • South: 25%
  • East: 25%
  • West: 25%

Purchase History:
  • High: 15%
  • Medium: 35%
  • Low: 30%
  • None: 20%

Customer Tier:
  • Gold: 10%
  • Silver: 30%
  • Bronze: 60%
```

**Panel Setup:**
- 4 panels × 2,000 customers = 8,000 total
- Split each into A/B for message testing

### Output
- 8 files (4 panels × 2 sets)
- Each set: 1,000 customers
- Use for A/B testing different messages

---

## Use Case 3: Clinical Trial Patient Recruitment

### Scenario
Medical research requiring balanced patient cohorts for multi-center trial.

### Dataset
- **Size**: 10,000 eligible patients
- **Stratification**: Age, Gender, Condition Severity, Location

### Requirements
- 2 panels (Treatment vs. Control baseline)
- Each panel: 500 patients
- Strict balance across all factors

### Configuration

**Target Proportions:**
```
Age:
  • 20-40: 30%
  • 41-60: 45%
  • 61+: 25%

Gender:
  • Male: 50%
  • Female: 50%

Condition Severity:
  • Mild: 40%
  • Moderate: 35%
  • Severe: 25%

Location:
  • Center A: 33%
  • Center B: 33%
  • Center C: 34%
```

**Panel Setup:**
- 2 panels × 500 patients = 1,000 total
- No splitting (panels themselves are treatment/control)

### Quality Checks
- Maximum deviation: < 2% per category
- Zero overlap between panels
- Documented random seed for FDA compliance

---

## Use Case 4: Educational Assessment Study

### Scenario
Testing new teaching method across multiple schools with balanced student samples.

### Dataset
- **Size**: 15,000 students
- **Stratification**: Grade, School, Previous Performance, Socioeconomic Status

### Requirements
- 3 panels (Control, Method A, Method B)
- Each panel: 1,200 students
- Split for pre/post assessment

### Configuration

**Target Proportions:**
```
Grade:
  • 6: 25%
  • 7: 25%
  • 8: 25%
  • 9: 25%

School:
  • School 1: 20%
  • School 2: 20%
  • School 3: 20%
  • School 4: 20%
  • School 5: 20%

Previous Performance:
  • High: 30%
  • Medium: 45%
  • Low: 25%

Socioeconomic Status:
  • Upper: 20%
  • Middle: 50%
  • Lower: 30%
```

**Panel Setup:**
- 3 panels × 1,200 students
- Each split into pre-test and post-test groups

---

## Use Case 5: Product Testing with Demographics

### Scenario
Consumer electronics company testing new product with diverse user groups.

### Dataset
- **Size**: 8,000 registered users
- **Stratification**: Age, Tech Savviness, Device Usage, Location

### Requirements
- 2 panels for iterative testing
- Each panel: 500 users
- Split for different product features

### Configuration

**Target Proportions:**
```
Age:
  • 18-30: 40%
  • 31-45: 35%
  • 46-60: 20%
  • 60+: 5%

Tech Savviness:
  • Expert: 20%
  • Intermediate: 50%
  • Beginner: 30%

Device Usage:
  • Heavy: 30%
  • Moderate: 45%
  • Light: 25%

Location:
  • Urban: 60%
  • Suburban: 30%
  • Rural: 10%
```

**Panel Setup:**
- 2 panels × 500 users
- Panel 1: Beta testing phase 1
- Panel 2: Beta testing phase 2
- Sets A/B for different feature combinations

---

## Common Patterns Across Use Cases

### Panel Sizing Guidelines

| Purpose | Recommended Panel Size | Number of Panels |
|---------|----------------------|------------------|
| Survey Research | 1,000-3,000 | 2-4 |
| A/B Testing | 500-2,000 | 2 |
| Clinical Trials | 100-1,000 | 2-3 |
| Market Research | 500-1,500 | 3-5 |
| Product Testing | 200-500 | 2-3 |

### Stratification Complexity

| Features | Complexity | Recommended |
|----------|-----------|-------------|
| 1-2 | Simple | ✓ Good for basic segmentation |
| 3-4 | Moderate | ✓ Recommended for most cases |
| 5-6 | Complex | ⚠️ Ensure sufficient sample size |
| 7+ | Very Complex | ⚠️ May require larger datasets |

### Random Seeds for Reproducibility

Always document your random seeds:
- **Panel Creation Seed**: 42
- **Panel Splitting Seed**: 42
- **Purpose**: Reproducibility, audit trail, FDA/regulatory compliance

### Quality Metrics

Target tolerances:
- **Distribution Matching**: ≤ 3% deviation from target
- **Split Balance**: ≤ 2% difference between Set A and Set B
- **Overlap**: 0 (strict requirement)

---

## Step-by-Step: Bihar Example Walkthrough

### Preparation (5 minutes)
1. Launch application: `./run_app.sh`
2. Prepare Bihar_panels.xlsx file

### Execution (10 minutes)

**Minute 1-2: Upload**
- Navigate to "1. Upload Data"
- Upload Bihar_panels.xlsx
- Verify 43,853 rows loaded

**Minute 3-5: Configure Targets**
- Navigate to "2. Configure Targets"
- Select: Gender, zone, 2020 AE, 2024 GE
- Click "Use current distribution" for each
- Click "Validate and Save Targets"

**Minute 6-7: Create Panels**
- Navigate to "3. Create Panels"
- Set: 3 panels, 3,150 size, seed 42
- Click "Create Panels"
- Wait for processing (~30 seconds)
- Review distribution tables

**Minute 8-9: Split Panels**
- Navigate to "4. Split Panels"
- Set seed: 42
- Click "Split All Panels"
- Review Set A vs. Set B comparisons

**Minute 10: Export**
- Navigate to "5. Validate & Export"
- Click "Check for Overlaps" (verify 0 overlaps)
- Set output directory: ./data
- Click "Export All to CSV"
- Download summary report

### Result
6 CSV files ready for use in survey waves:
- Wave 1: panel_1_set_a.csv, panel_1_set_b.csv
- Wave 2: panel_2_set_a.csv, panel_2_set_b.csv
- Wave 3: panel_3_set_a.csv, panel_3_set_b.csv

---

## Tips for Different Research Contexts

### Academic Research
- Document all random seeds
- Save summary report for methodology section
- Export distribution tables for appendix
- Keep reproducibility trail

### Commercial Research
- Focus on business-relevant segments
- Consider cost constraints in panel sizing
- Balance statistical rigor with practical needs
- Plan for attrition in panel sizing

### Clinical Trials
- Follow regulatory requirements (FDA, IRB)
- Maintain strict balance requirements
- Document all steps for audit trail
- Consider dropout rates in sizing

### Product Testing
- Align panels with user personas
- Test representative edge cases
- Plan iterative testing cycles
- Balance diversity with target market

---

## Troubleshooting Common Scenarios

### "Not enough samples in rare categories"
**Solution**: 
- Adjust target proportions to match availability
- Reduce panel size
- Consider combining rare categories

### "Large deviations in specific features"
**Solution**:
- Check if features are correlated
- Review dataset for imbalances
- Consider prioritizing features (use fewer)
- Increase panel size if dataset allows

### "Need to add more panels later"
**Solution**:
- Use different random seed
- Re-run with cumulative panel count
- Tool excludes already-used samples automatically

### "Need to regenerate with same criteria"
**Solution**:
- Use same random seed values
- Results will be identical
- Useful for audit/verification purposes

---

## Advanced Techniques

### Hierarchical Stratification
Prioritize features by importance:
1. Primary: Demographics (Gender, Age)
2. Secondary: Behavior (Purchase History)
3. Tertiary: Context (Location)

### Weighted Sampling
Adjust proportions to oversample rare but important groups:
- Example: Oversample minority groups for statistical power
- Adjust weights in analysis phase

### Sequential Panel Design
Create panels in sequence for longitudinal studies:
- Panel 1: Baseline (Month 0)
- Panel 2: Follow-up 1 (Month 3)
- Panel 3: Follow-up 2 (Month 6)

### Quota Filling
When exact targets can't be met:
1. Fill high-priority categories first
2. Fill remaining slots with best available
3. Document deviations in report

---

**Ready to implement your use case? Follow the QUICKSTART.md guide!**
