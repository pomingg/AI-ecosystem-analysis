"""Descriptive EDA for arXiv and GitHub trending datasets.

Produces summary DataFrames suitable for Tableau visualization.
Each function returns a dict of named DataFrames.

Usage:
    from ai_ecosystem.analysis.descriptive import eda_arxiv, eda_github
"""

import logging

import pandas as pd

from ai_ecosystem.constants import AIML_KEYWORDS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# arXiv EDA
# ---------------------------------------------------------------------------

def eda_arxiv(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Run descriptive EDA on the arXiv dataset.

    Args:
        df: Raw arXiv DataFrame.

    Returns:
        Dict mapping table names to Tableau-ready DataFrames.
    """
    results = {}

    df = df.copy()
    df["submitted_date"] = pd.to_datetime(
        df["submitted_date"], errors="coerce"
    )
    df["year_month"] = df["submitted_date"].dt.to_period("M").astype(str)

    # 1. Monthly paper volume
    monthly = (
        df.groupby("year_month")
        .size()
        .reset_index(name="paper_count")
        .sort_values("year_month")
    )
    results["arxiv_monthly_volume"] = monthly
    logger.info(
        "arxiv_monthly_volume: %d months, total %d papers",
        len(monthly), monthly["paper_count"].sum(),
    )

    # 2. Category counts (primary_category)
    cat_counts = (
        df["primary_category"]
        .value_counts()
        .reset_index()
    )
    cat_counts.columns = ["category", "paper_count"]
    results["arxiv_category_counts"] = cat_counts

    # 3. Category × month (for stacked area chart)
    cat_monthly = (
        df.groupby(["year_month", "primary_category"])
        .size()
        .reset_index(name="paper_count")
        .sort_values(["year_month", "primary_category"])
    )
    results["arxiv_category_monthly"] = cat_monthly

    # 4. Top 20 most prolific authors
    top_authors = (
        df["first_author"]
        .value_counts()
        .head(20)
        .reset_index()
    )
    top_authors.columns = ["author", "paper_count"]
    results["arxiv_top_authors"] = top_authors

    # 5. Abstract stats per month
    abstract_stats = (
        df.groupby("year_month")
        .agg(
            avg_word_count=("word_count", "mean"),
            avg_abstract_length=("abstract_length", "mean"),
            paper_count=("paper_id", "count"),
        )
        .round(1)
        .reset_index()
        .sort_values("year_month")
    )
    results["arxiv_abstract_stats"] = abstract_stats

    # 6. Cross-category co-occurrence
    results["arxiv_cross_category"] = _category_cooccurrence(df)

    return results


def _category_cooccurrence(df: pd.DataFrame) -> pd.DataFrame:
    """Build category co-occurrence table from all_categories column.

    Returns long-format DataFrame: category_a, category_b, co_count.
    """
    from collections import Counter

    pairs = Counter()
    for cats_str in df["all_categories"].dropna():
        cats = [c.strip() for c in cats_str.split(";")]
        for i, a in enumerate(cats):
            for b in cats[i + 1:]:
                key = tuple(sorted([a, b]))
                pairs[key] += 1

    if not pairs:
        return pd.DataFrame(
            columns=["category_a", "category_b", "co_count"]
        )

    rows = [
        {"category_a": k[0], "category_b": k[1], "co_count": v}
        for k, v in pairs.most_common(50)
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# GitHub trending EDA
# ---------------------------------------------------------------------------

def eda_github(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Run descriptive EDA on the GitHub trending dataset.

    Args:
        df: Raw GitHub trending DataFrame.

    Returns:
        Dict mapping table names to Tableau-ready DataFrames.
    """
    results = {}

    df = df.copy()

    # 1. Monthly entry count
    monthly = (
        df.groupby("month")
        .size()
        .reset_index(name="repo_count")
        .sort_values("month")
    )
    results["github_monthly_entries"] = monthly
    logger.info(
        "github_monthly_entries: %d months", len(monthly),
    )

    # 2. Top repos by ranking appearances
    top_repos = (
        df.groupby(["repository", "repo_owner", "repo_name"])
        .agg(
            appearances=("ranking_appearances", "max"),
            avg_rank=("rank", "mean"),
            latest_stars=("star_count", "last"),
            latest_forks=("fork_count", "last"),
        )
        .round(1)
        .reset_index()
        .sort_values("appearances", ascending=False)
        .head(50)
    )
    results["github_top_repos"] = top_repos

    # 3. AI/ML tagged repos per month
    pattern = "|".join(AIML_KEYWORDS)
    repo_lower = df["repo_name"].astype(str).str.lower()
    owner_lower = df["repo_owner"].astype(str).str.lower()
    df["is_aiml"] = (
        repo_lower.str.contains(pattern, na=False)
        | owner_lower.str.contains(pattern, na=False)
    )

    aiml_monthly = (
        df[df["is_aiml"]]
        .groupby("month")
        .size()
        .reset_index(name="aiml_repo_count")
        .sort_values("month")
    )
    results["github_aiml_monthly"] = aiml_monthly

    # 4. AI/ML ratio over time
    total_monthly = df.groupby("month").size().reset_index(name="total")
    aiml_ratio = total_monthly.merge(
        aiml_monthly, on="month", how="left"
    )
    aiml_ratio["aiml_repo_count"] = (
        aiml_ratio["aiml_repo_count"].fillna(0).astype(int)
    )
    aiml_ratio["aiml_ratio"] = (
        aiml_ratio["aiml_repo_count"] / aiml_ratio["total"]
    ).round(4)
    results["github_aiml_ratio"] = aiml_ratio

    # 5. Owner concentration
    owner_counts = (
        df.groupby("repo_owner")["repo_name"]
        .nunique()
        .reset_index(name="unique_repos")
        .sort_values("unique_repos", ascending=False)
        .head(30)
    )
    results["github_owner_concentration"] = owner_counts

    # 6. Star growth for repos appearing 3+ months
    results["github_star_growth"] = _star_growth(df)

    return results


def _star_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate star growth trajectories for multi-month repos."""
    valid = df.dropna(subset=["star_count"])
    repo_months = valid.groupby("repository")["month"].nunique()
    multi_month = repo_months[repo_months >= 3].index

    if len(multi_month) == 0:
        return pd.DataFrame(
            columns=[
                "repository", "first_month", "last_month",
                "first_stars", "last_stars", "star_growth",
                "months_tracked",
            ]
        )

    rows = []
    for repo in multi_month:
        repo_data = (
            valid[valid["repository"] == repo]
            .sort_values("month")
        )
        first = repo_data.iloc[0]
        last = repo_data.iloc[-1]
        rows.append({
            "repository": repo,
            "first_month": first["month"],
            "last_month": last["month"],
            "first_stars": first["star_count"],
            "last_stars": last["star_count"],
            "star_growth": last["star_count"] - first["star_count"],
            "months_tracked": len(repo_data),
        })

    return (
        pd.DataFrame(rows)
        .sort_values("star_growth", ascending=False)
    )
