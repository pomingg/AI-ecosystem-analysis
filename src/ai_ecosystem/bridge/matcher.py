"""Cross-dataset topic alignment and matching logic.

Produces Tableau-ready bridge tables that connect arXiv papers
and GitHub trending repos through the shared topic taxonomy.
"""

import logging

import pandas as pd

from ai_ecosystem.bridge.taxonomy import (
    classify_arxiv_topic,
    classify_github_topic,
)

logger = logging.getLogger(__name__)


def bridge_arxiv_topics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate arXiv papers by topic and month.

    Returns:
        DataFrame with columns: topic, year_month, paper_count.
    """
    df = df.copy()
    df["submitted_date"] = pd.to_datetime(df["submitted_date"], errors="coerce")
    df["year_month"] = df["submitted_date"].dt.to_period("M").astype(str)
    df["topic"] = df["primary_category"].apply(classify_arxiv_topic)

    result = (
        df.groupby(["topic", "year_month"])
        .size()
        .reset_index(name="paper_count")
        .sort_values(["topic", "year_month"])
    )
    logger.info("bridge_arxiv_by_topic: %d rows, %d topics", len(result), result["topic"].nunique())
    return result


def bridge_github_topics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate GitHub repos by topic and month.

    A repo can match multiple topics, so it may appear in multiple rows.

    Returns:
        DataFrame with columns: topic, month, repo_count, avg_stars.
    """
    df = df.copy()

    rows = []
    for _, row in df.iterrows():
        topics = classify_github_topic(
            str(row.get("repo_name", "")),
            str(row.get("repo_owner", "")),
        )
        for topic in topics:
            rows.append({
                "topic": topic,
                "month": row["month"],
                "star_count": row.get("star_count"),
            })

    if not rows:
        return pd.DataFrame(columns=["topic", "month", "repo_count", "avg_stars"])

    exploded = pd.DataFrame(rows)
    result = (
        exploded.groupby(["topic", "month"])
        .agg(repo_count=("topic", "size"), avg_stars=("star_count", "mean"))
        .round(1)
        .reset_index()
        .sort_values(["topic", "month"])
    )
    logger.info(
        "bridge_github_by_topic: %d rows, %d topics", len(result), result["topic"].nunique(),
    )
    return result


def bridge_combined_timeline(
    arxiv_topics: pd.DataFrame,
    github_topics: pd.DataFrame,
) -> pd.DataFrame:
    """Merge arXiv and GitHub topic aggregations into a single timeline.

    Args:
        arxiv_topics: Output of bridge_arxiv_topics().
        github_topics: Output of bridge_github_topics().

    Returns:
        DataFrame with columns: topic, month, arxiv_papers, github_repos.
    """
    arxiv = arxiv_topics.rename(columns={"year_month": "month", "paper_count": "arxiv_papers"})
    github = github_topics[["topic", "month", "repo_count"]].rename(
        columns={"repo_count": "github_repos"}
    )

    merged = pd.merge(arxiv, github, on=["topic", "month"], how="outer")
    merged["arxiv_papers"] = merged["arxiv_papers"].fillna(0).astype(int)
    merged["github_repos"] = merged["github_repos"].fillna(0).astype(int)
    merged = merged.sort_values(["topic", "month"]).reset_index(drop=True)

    logger.info(
        "bridge_topic_timeline: %d rows, months %s to %s",
        len(merged),
        merged["month"].min(),
        merged["month"].max(),
    )
    return merged


def bridge_topic_summary(
    arxiv_topics: pd.DataFrame,
    github_topics: pd.DataFrame,
) -> pd.DataFrame:
    """Produce an overall topic comparison table.

    Returns:
        DataFrame with columns: topic, total_arxiv_papers,
        total_github_repos, arxiv_months, github_months.
    """
    arxiv_agg = (
        arxiv_topics.groupby("topic")
        .agg(total_arxiv_papers=("paper_count", "sum"), arxiv_months=("year_month", "nunique"))
        .reset_index()
    )

    github_agg = (
        github_topics.groupby("topic")
        .agg(total_github_repos=("repo_count", "sum"), github_months=("month", "nunique"))
        .reset_index()
    )

    summary = pd.merge(arxiv_agg, github_agg, on="topic", how="outer").fillna(0)
    for col in ["total_arxiv_papers", "arxiv_months", "total_github_repos", "github_months"]:
        summary[col] = summary[col].astype(int)

    return summary.sort_values("total_arxiv_papers", ascending=False).reset_index(drop=True)
