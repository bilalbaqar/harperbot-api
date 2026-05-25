"""
Bidding history tool using the bidding-history.csv dataset.
Loaded once at startup into a pandas DataFrame.
"""
import pandas as pd
from pathlib import Path
from typing import Optional

_df: Optional[pd.DataFrame] = None
DATA_PATH = Path(__file__).parents[1] / "data" / "bidding-history.csv"


def _load_data() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
        _df.columns = [c.strip() for c in _df.columns]
        _df["Course_Number"] = _df["Course_Number"].astype(str).str.strip()
        # Convert price columns to numeric, coerce errors
        for col in ["Phase 1 Price", "Phase 2 Price", "Phase 3 Price"]:
            if col in _df.columns:
                _df[col] = pd.to_numeric(_df[col], errors="coerce")
        print(f"[bidding_history] Loaded {len(_df)} bidding records")
    return _df


def get_bid_history(course_number: str) -> str:
    """
    Return bidding history for a course number.
    Shows bid prices across all recorded quarters.
    """
    df = _load_data()
    number = str(course_number).strip()
    filtered = df[df["Course_Number"] == number].copy()

    if filtered.empty:
        return f"No bidding history found for course {number}."

    title = filtered.iloc[0]["Title"] if "Title" in filtered.columns else ""
    filtered["Quarter-Year"] = filtered["Quarter"].astype(str) + " " + filtered["Year"].astype(str)

    # Group by Quarter-Year, take first section's prices
    grouped = (
        filtered[["Quarter-Year", "Phase 1 Price", "Phase 2 Price", "Phase 3 Price"]]
        .groupby("Quarter-Year")
        .first()
        .reset_index()
        .sort_values("Quarter-Year", ascending=False)
    )

    lines = [f"Bidding History for {number} — {title}\n"]
    for _, row in grouped.iterrows():
        p1 = f"{int(row['Phase 1 Price'])}" if pd.notna(row["Phase 1 Price"]) else "N/A"
        p2 = f"{int(row['Phase 2 Price'])}" if pd.notna(row["Phase 2 Price"]) else "N/A"
        p3 = f"{int(row['Phase 3 Price'])}" if pd.notna(row["Phase 3 Price"]) else "N/A"
        lines.append(
            f"  {row['Quarter-Year']}: Phase 1 = {p1} pts | Phase 2 = {p2} pts | Phase 3 = {p3} pts"
        )

    # Add summary stats
    phase1_vals = grouped["Phase 1 Price"].dropna()
    if not phase1_vals.empty:
        lines.append(
            f"\nPhase 1 stats: avg={phase1_vals.mean():.0f} pts, "
            f"max={phase1_vals.max():.0f} pts, min={phase1_vals.min():.0f} pts"
        )

    return "\n".join(lines)


def search_bidding_by_name(course_name: str) -> str:
    """
    Search bidding history by course name (when user doesn't have the number).
    """
    df = _load_data()
    name_lower = course_name.lower()
    matches = df[df["Title"].str.lower().str.contains(name_lower, na=False)]

    if matches.empty:
        return (
            f"No courses found matching '{course_name}'. "
            "Please try with the exact course number (e.g., 35150)."
        )

    # Show unique courses found
    unique = matches[["Course_Number", "Title"]].drop_duplicates()
    lines = [f"Courses matching '{course_name}':\n"]
    for _, row in unique.iterrows():
        lines.append(f"  {row['Course_Number']} — {row['Title']}")
    lines.append("\nPlease use the course number for detailed bid history.")
    return "\n".join(lines)
