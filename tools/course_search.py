"""
Course search and lookup tools using the all-course-list.csv dataset.
Loaded once at startup into a pandas DataFrame.
"""
import pandas as pd
from pathlib import Path
from typing import Optional

_df: Optional[pd.DataFrame] = None
DATA_PATH = Path(__file__).parents[1] / "data" / "all-course-list.csv"


def _load_data() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
        # Normalize column names
        _df.columns = [c.strip() for c in _df.columns]
        # Ensure Course column is string
        _df["Course"] = _df["Course"].astype(str).str.strip()
        _df["Title"] = _df["Title"].astype(str).str.strip()
        print(f"[course_search] Loaded {len(_df)} course records")
    return _df


def search_courses(query: str, max_results: int = 10) -> str:
    """
    Search courses by keyword (title, instructor, course number, quarter, schedule).
    Returns a formatted table of matching courses.
    """
    df = _load_data()
    query_lower = query.lower()

    # Search across multiple columns
    mask = (
        df["Title"].str.lower().str.contains(query_lower, na=False)
        | df["Course"].str.lower().str.contains(query_lower, na=False)
        | df["Faculty"].str.lower().str.contains(query_lower, na=False)
        | df["Quarter"].str.lower().str.contains(query_lower, na=False)
        | df["Schedule"].str.lower().str.contains(query_lower, na=False)
        | df["Program"].str.lower().str.contains(query_lower, na=False)
    )
    results = df[mask].head(max_results)

    if results.empty:
        return f"No courses found matching '{query}'."

    lines = [f"Found {len(results)} course(s) matching '{query}':\n"]
    for _, row in results.iterrows():
        lines.append(
            f"- {row['Course']} | {row['Title']} | {row['Quarter']} | "
            f"Instructor: {row['Faculty']} | Schedule: {row['Schedule']} | "
            f"Capacity: {row['Capacity']} | Room: {row['Building']} {row['Location']}"
        )
    return "\n".join(lines)


def lookup_course_by_number(course_number: str) -> str:
    """
    Get all offerings for a specific course number.
    Returns all sections across all quarters.
    """
    df = _load_data()
    number = str(course_number).strip()
    results = df[df["Course"] == number]

    if results.empty:
        # Try partial match
        results = df[df["Course"].str.contains(number, na=False)]

    if results.empty:
        return f"Course number {number} not found in the course catalog."

    title = results.iloc[0]["Title"]
    lines = [f"Course {number}: {title}\n"]
    for _, row in results.iterrows():
        lines.append(
            f"  Section {row['Section']} | {row['Quarter']} | "
            f"Instructor: {row['Faculty']} | Schedule: {row['Schedule']} | "
            f"Capacity: {row['Capacity']}"
        )
    return "\n".join(lines)


def get_course_title(course_number: str) -> str:
    """Look up a course title given a course number."""
    df = _load_data()
    number = str(course_number).strip()
    matches = df[df["Course"] == number]
    if matches.empty:
        return f"Course number {number} not found."
    return f"{number}: {matches.iloc[0]['Title']}"


def list_courses_by_quarter(quarter: str, max_results: int = 20) -> str:
    """List all courses offered in a given quarter (e.g., 'Spring 2025')."""
    df = _load_data()
    results = df[df["Quarter"].str.lower().str.contains(quarter.lower(), na=False)]
    results = results.drop_duplicates(subset=["Course", "Title"]).head(max_results)

    if results.empty:
        return f"No courses found for quarter '{quarter}'."

    lines = [f"Courses offered in {quarter} (showing up to {max_results}):\n"]
    for _, row in results.iterrows():
        lines.append(f"- {row['Course']} | {row['Title']} | {row['Faculty']}")
    return "\n".join(lines)
