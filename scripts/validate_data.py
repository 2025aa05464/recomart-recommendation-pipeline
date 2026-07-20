import os
import pandas as pd
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
RATINGS_PATH = f"data/raw/interactions/{TODAY}/ratings.csv"
METADATA_PATH = f"data/raw/metadata/{TODAY}/movie_metadata.csv"
REPORT_PATH = f"docs/data_quality_report_{TODAY}.md"

EXPECTED_COLUMNS = {"user_id", "item_id", "rating", "timestamp"}


def validate_ratings():
    df = pd.read_csv(RATINGS_PATH)
    issues = []

    actual_columns = set(df.columns)
    if actual_columns != EXPECTED_COLUMNS:
        issues.append(f"Schema mismatch. Expected {EXPECTED_COLUMNS}, got {actual_columns}")

    missing = df.isnull().sum()
    missing_total = missing.sum()
    duplicate_count = df.duplicated().sum()
    out_of_range = df[(df["rating"] < 1) | (df["rating"] > 5)]

    return {
        "total_rows": len(df),
        "missing_values_by_column": missing.to_dict(),
        "total_missing": int(missing_total),
        "duplicate_rows": int(duplicate_count),
        "out_of_range_ratings": len(out_of_range),
        "schema_issues": issues,
        "rating_min": df["rating"].min(),
        "rating_max": df["rating"].max(),
        "unique_users": df["user_id"].nunique(),
        "unique_items": df["item_id"].nunique(),
    }


def validate_metadata():
    if not os.path.exists(METADATA_PATH):
        return None
    df = pd.read_csv(METADATA_PATH)
    return {
        "total_rows": len(df),
        "missing_imdb_rating": int(df["imdb_rating"].isnull().sum()),
        "missing_genre": int(df["genre"].isnull().sum()),
    }


def write_report(ratings_stats, metadata_stats):
    os.makedirs("docs", exist_ok=True)
    lines = []
    lines.append(f"# RecoMart Data Quality Report — {TODAY}\n")

    lines.append("## Source 1: Ratings / Interactions Data\n")
    lines.append(f"- Total rows: **{ratings_stats['total_rows']}**")
    lines.append(f"- Unique users: **{ratings_stats['unique_users']}**")
    lines.append(f"- Unique items: **{ratings_stats['unique_items']}**")
    lines.append(f"- Rating range found: **{ratings_stats['rating_min']} to {ratings_stats['rating_max']}**")
    lines.append(f"- Total missing values: **{ratings_stats['total_missing']}**")
    lines.append(f"- Duplicate rows: **{ratings_stats['duplicate_rows']}**")
    lines.append(f"- Out-of-range ratings (outside 1-5): **{ratings_stats['out_of_range_ratings']}**")

    if ratings_stats["schema_issues"]:
        lines.append(f"- ⚠️ Schema issues: {ratings_stats['schema_issues']}")
    else:
        lines.append("- ✅ Schema check passed")

    lines.append("\n### Missing values by column")
    for col, count in ratings_stats["missing_values_by_column"].items():
        lines.append(f"- {col}: {count}")

    if metadata_stats:
        lines.append("\n## Source 2: Movie Metadata (OMDb API)\n")
        lines.append(f"- Total rows: **{metadata_stats['total_rows']}**")
        lines.append(f"- Missing IMDb ratings: **{metadata_stats['missing_imdb_rating']}**")
        lines.append(f"- Missing genre: **{metadata_stats['missing_genre']}**")

    lines.append("\n## Overall Verdict")
    if ratings_stats["total_missing"] == 0 and ratings_stats["duplicate_rows"] == 0 and ratings_stats["out_of_range_ratings"] == 0:
        lines.append("✅ Data passed all validation checks. Safe to proceed to Data Preparation.")
    else:
        lines.append("⚠️ Some issues found above — should be handled in the Data Preparation step.")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))

    print(f"[OK] Data quality report written to {REPORT_PATH}")


if __name__ == "__main__":
    print("Running data validation...")
    ratings_stats = validate_ratings()
    metadata_stats = validate_metadata()
    write_report(ratings_stats, metadata_stats)
    print("Validation complete.")