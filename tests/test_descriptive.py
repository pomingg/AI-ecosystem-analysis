"""Tests for descriptive EDA — uses synthetic data, no files needed."""

import pandas as pd

from ai_ecosystem.analysis.descriptive import eda_arxiv, eda_github


def _make_arxiv_df(n: int = 20) -> pd.DataFrame:
    """Create a minimal synthetic arXiv DataFrame."""
    return pd.DataFrame({
        "paper_id": [f"2025.{i:05d}v1" for i in range(n)],
        "title": [f"Paper {i}" for i in range(n)],
        "first_author": [f"Author {i % 5}" for i in range(n)],
        "abstract": ["Some abstract text here."] * n,
        "abstract_length": [25] * n,
        "word_count": [5] * n,
        "primary_category": ["cs.CL", "cs.CV", "cs.LG", "cs.AI"] * 5,
        "all_categories": [
            "cs.CL; cs.AI", "cs.CV", "cs.LG; cs.CL",
            "cs.AI; cs.LG", "cs.CL",
        ] * 4,
        "num_categories": [2, 1, 2, 2, 1] * 4,
        "submitted_date": pd.date_range("2025-10-01", periods=n, freq="D"),
        "updated_date": pd.date_range("2025-10-01", periods=n, freq="D"),
        "year": [2025] * n,
        "month": [10] * n,
        "num_authors": [3] * n,
    })


def _make_github_df(n: int = 30) -> pd.DataFrame:
    """Create a minimal synthetic GitHub trending DataFrame."""
    months = ["2024-01", "2024-02", "2024-03"] * 10
    return pd.DataFrame({
        "month": months[:n],
        "rank": list(range(1, 11)) * 3,
        "repository": [f"owner{i % 5}/repo{i}" for i in range(n)],
        "repo_owner": [f"owner{i % 5}" for i in range(n)],
        "repo_name": [f"repo{i}" for i in range(n)],
        "star_count": [100.0 + i * 10 for i in range(n)],
        "fork_count": [10.0 + i for i in range(n)],
        "ranking_appearances": [5] * n,
    })


def test_eda_arxiv_returns_expected_keys():
    df = _make_arxiv_df()
    result = eda_arxiv(df)
    expected_keys = {
        "arxiv_monthly_volume",
        "arxiv_category_counts",
        "arxiv_category_monthly",
        "arxiv_top_authors",
        "arxiv_abstract_stats",
        "arxiv_cross_category",
    }
    assert set(result.keys()) == expected_keys


def test_eda_arxiv_monthly_volume():
    df = _make_arxiv_df(20)
    result = eda_arxiv(df)
    vol = result["arxiv_monthly_volume"]
    assert "year_month" in vol.columns
    assert "paper_count" in vol.columns
    assert vol["paper_count"].sum() == 20


def test_eda_arxiv_category_counts():
    df = _make_arxiv_df(20)
    result = eda_arxiv(df)
    cats = result["arxiv_category_counts"]
    assert cats["paper_count"].sum() == 20
    assert "cs.CL" in cats["category"].values


def test_eda_arxiv_cross_category():
    df = _make_arxiv_df()
    result = eda_arxiv(df)
    cc = result["arxiv_cross_category"]
    assert "category_a" in cc.columns
    assert "co_count" in cc.columns
    assert len(cc) > 0


def test_eda_github_returns_expected_keys():
    df = _make_github_df()
    result = eda_github(df)
    expected_keys = {
        "github_monthly_entries",
        "github_top_repos",
        "github_aiml_monthly",
        "github_aiml_ratio",
        "github_owner_concentration",
        "github_star_growth",
    }
    assert set(result.keys()) == expected_keys


def test_eda_github_monthly_entries():
    df = _make_github_df(30)
    result = eda_github(df)
    monthly = result["github_monthly_entries"]
    assert monthly["repo_count"].sum() == 30


def test_eda_github_aiml_ratio_between_0_and_1():
    df = _make_github_df()
    result = eda_github(df)
    ratio = result["github_aiml_ratio"]
    assert (ratio["aiml_ratio"] >= 0).all()
    assert (ratio["aiml_ratio"] <= 1).all()


def test_eda_github_owner_concentration():
    df = _make_github_df()
    result = eda_github(df)
    owners = result["github_owner_concentration"]
    assert "repo_owner" in owners.columns
    assert "unique_repos" in owners.columns
    assert len(owners) > 0
