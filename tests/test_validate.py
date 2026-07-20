"""Tests for data validation logic — no data files required."""

import pandas as pd

from ai_ecosystem.ingest.validate import ValidationReport, find_column


def test_validation_report_renders_markdown():
    report = ValidationReport("Test Dataset", source_url="https://example.com")
    report.set_overview(total_rows=1000, num_columns=5, time_range="2024-01 to 2024-12")
    report.add_column_detail("col_a", "int64", 0.0, 10, "[1, 2, 3]", "✅")
    report.add_finding("Everything looks good", "PASS")
    report.add_decision("No changes needed.")

    md = report.to_markdown()
    assert "# Test Dataset Validation Report" in md
    assert "https://example.com" in md
    assert "1,000" in md
    assert "col_a" in md
    assert "Everything looks good" in md
    assert "No changes needed." in md


def test_find_column_exact_match():
    df = pd.DataFrame({"Stars": [1], "Name": ["a"]})
    assert find_column(df, ["stars"]) == "Stars"


def test_find_column_case_insensitive():
    df = pd.DataFrame({"STAR_COUNT": [1]})
    assert find_column(df, ["star_count"]) == "STAR_COUNT"


def test_find_column_partial_match():
    df = pd.DataFrame({"stargazers_count": [1], "other": [2]})
    assert find_column(df, ["star"]) == "stargazers_count"


def test_find_column_not_found():
    df = pd.DataFrame({"col_a": [1], "col_b": [2]})
    assert find_column(df, ["xyz", "nonexistent"]) is None


def test_find_column_prefers_exact_over_partial():
    df = pd.DataFrame({"month": [1], "monthly_rank": [2]})
    assert find_column(df, ["month"]) == "month"
