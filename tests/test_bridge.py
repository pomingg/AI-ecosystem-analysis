"""Tests for the cross-dataset bridge module."""

import pandas as pd

from ai_ecosystem.bridge.matcher import (
    bridge_arxiv_topics,
    bridge_combined_timeline,
    bridge_github_topics,
    bridge_topic_summary,
)
from ai_ecosystem.bridge.taxonomy import (
    classify_arxiv_topic,
    classify_github_topic,
    get_taxonomy,
)

# --- Taxonomy tests ---


def test_classify_arxiv_known_categories():
    assert classify_arxiv_topic("cs.CL") == "NLP"
    assert classify_arxiv_topic("cs.CV") == "Computer Vision"
    assert classify_arxiv_topic("cs.LG") == "Machine Learning"
    assert classify_arxiv_topic("cs.AI") == "AI Agents & Tools"
    assert classify_arxiv_topic("cs.RO") == "Robotics & Control"


def test_classify_arxiv_unknown_category():
    assert classify_arxiv_topic("cs.DS") == "Other AI/ML"
    assert classify_arxiv_topic("math.CO") == "Other AI/ML"


def test_classify_github_nlp_keywords():
    topics = classify_github_topic("llm-chatbot", "someuser")
    assert "NLP" in topics


def test_classify_github_cv_keywords():
    topics = classify_github_topic("yolo-detector", "someuser")
    assert "Computer Vision" in topics


def test_classify_github_no_match():
    topics = classify_github_topic("my-website", "webdev")
    assert topics == ["Other AI/ML"]


def test_classify_github_multiple_topics():
    topics = classify_github_topic("pytorch-yolo", "aiuser")
    assert len(topics) >= 2


def test_get_taxonomy_returns_dataframe():
    tax = get_taxonomy()
    assert isinstance(tax, pd.DataFrame)
    assert set(tax.columns) == {"topic", "source", "match_key"}
    assert len(tax) > 0
    assert set(tax["source"].unique()) == {"arxiv", "github"}


# --- Matcher tests ---


def _make_arxiv_df(n: int = 20) -> pd.DataFrame:
    return pd.DataFrame({
        "paper_id": [f"2025.{i:05d}v1" for i in range(n)],
        "title": [f"Paper {i}" for i in range(n)],
        "first_author": [f"Author {i % 5}" for i in range(n)],
        "abstract": ["Some abstract text here."] * n,
        "abstract_length": [25] * n,
        "word_count": [5] * n,
        "primary_category": ["cs.CL", "cs.CV", "cs.LG", "cs.AI"] * 5,
        "all_categories": ["cs.CL; cs.AI"] * n,
        "num_categories": [2] * n,
        "submitted_date": pd.date_range("2025-10-01", periods=n, freq="D"),
        "updated_date": pd.date_range("2025-10-01", periods=n, freq="D"),
        "year": [2025] * n,
        "month": [10] * n,
        "num_authors": [3] * n,
    })


def _make_github_df(n: int = 30) -> pd.DataFrame:
    months = ["2024-01", "2024-02", "2024-03"] * 10
    return pd.DataFrame({
        "month": months[:n],
        "rank": list(range(1, 11)) * 3,
        "repository": [f"owner{i % 5}/repo{i}" for i in range(n)],
        "repo_owner": [f"owner{i % 5}" for i in range(n)],
        "repo_name": [f"llm-tool{i}" if i % 3 == 0 else f"repo{i}" for i in range(n)],
        "star_count": [100.0 + i * 10 for i in range(n)],
        "fork_count": [10.0 + i for i in range(n)],
        "ranking_appearances": [5] * n,
    })


def test_bridge_arxiv_topics_columns():
    df = _make_arxiv_df()
    result = bridge_arxiv_topics(df)
    assert set(result.columns) == {"topic", "year_month", "paper_count"}
    assert result["paper_count"].sum() == 20


def test_bridge_arxiv_topics_has_expected_topics():
    df = _make_arxiv_df()
    result = bridge_arxiv_topics(df)
    topics = set(result["topic"])
    assert "NLP" in topics
    assert "Computer Vision" in topics


def test_bridge_github_topics_columns():
    df = _make_github_df()
    result = bridge_github_topics(df)
    assert "topic" in result.columns
    assert "month" in result.columns
    assert "repo_count" in result.columns
    assert "avg_stars" in result.columns


def test_bridge_github_topics_has_nlp():
    df = _make_github_df()
    result = bridge_github_topics(df)
    assert "NLP" in result["topic"].values


def test_bridge_combined_timeline():
    arxiv = bridge_arxiv_topics(_make_arxiv_df())
    github = bridge_github_topics(_make_github_df())
    timeline = bridge_combined_timeline(arxiv, github)
    assert set(timeline.columns) == {"topic", "month", "arxiv_papers", "github_repos"}
    assert len(timeline) > 0
    assert (timeline["arxiv_papers"] >= 0).all()
    assert (timeline["github_repos"] >= 0).all()


def test_bridge_topic_summary():
    arxiv = bridge_arxiv_topics(_make_arxiv_df())
    github = bridge_github_topics(_make_github_df())
    summary = bridge_topic_summary(arxiv, github)
    expected_cols = {
        "topic", "total_arxiv_papers", "total_github_repos", "arxiv_months", "github_months",
    }
    assert set(summary.columns) == expected_cols
    assert len(summary) > 0
