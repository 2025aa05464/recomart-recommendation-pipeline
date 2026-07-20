# RecoMart Data Quality Report — 2026-07-20

## Source 1: Ratings / Interactions Data

- Total rows: **100000**
- Unique users: **943**
- Unique items: **1682**
- Rating range found: **1 to 5**
- Total missing values: **0**
- Duplicate rows: **0**
- Out-of-range ratings (outside 1-5): **0**
- ✅ Schema check passed

### Missing values by column
- user_id: 0
- item_id: 0
- rating: 0
- timestamp: 0

## Source 2: Movie Metadata (OMDb API)

- Total rows: **41**
- Missing IMDb ratings: **0**
- Missing genre: **0**

## Overall Verdict
✅ Data passed all validation checks. Safe to proceed to Data Preparation.