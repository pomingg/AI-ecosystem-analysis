"""Export Tableau-ready CSV files from EDA results.

Loads raw datasets, runs descriptive EDA and bridge analysis,
and saves each summary table as a clean CSV in data/processed/.

Usage:
    python -m ai_ecosystem.analysis.export_tableau
"""

import logging
from pathlib import Path

import pandas as pd

from ai_ecosystem.analysis.descriptive import eda_arxiv, eda_github
from ai_ecosystem.bridge.matcher import (
    bridge_arxiv_topics,
    bridge_combined_timeline,
    bridge_github_topics,
    bridge_topic_summary,
)
from ai_ecosystem.bridge.taxonomy import get_taxonomy
from ai_ecosystem.ingest.arxiv import load_arxiv_data
from ai_ecosystem.ingest.github_trending import load_github_trending

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def _save_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> list[Path]:
    exported = []
    for name, table in tables.items():
        path = output_dir / f"{name}.csv"
        table.to_csv(path, index=False)
        exported.append(path)
        logger.info("Exported %s (%d rows)", path.name, len(table))
    return exported


def export_all(output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Run EDA and bridge analysis on both datasets, export CSVs.

    Args:
        output_dir: Directory to write CSV files.

    Returns:
        List of paths to the exported CSV files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []

    arxiv_df: pd.DataFrame | None = None
    github_df: pd.DataFrame | None = None

    # --- arXiv descriptive ---
    try:
        arxiv_df = load_arxiv_data()
        exported.extend(_save_tables(eda_arxiv(arxiv_df), output_dir))
    except FileNotFoundError as e:
        logger.warning("Skipping arXiv export: %s", e)

    # --- GitHub descriptive ---
    try:
        github_df = load_github_trending()
        exported.extend(_save_tables(eda_github(github_df), output_dir))
    except FileNotFoundError as e:
        logger.warning("Skipping GitHub export: %s", e)

    # --- Bridge (cross-dataset) ---
    bridge_tables: dict[str, pd.DataFrame] = {}

    arxiv_by_topic = bridge_arxiv_topics(arxiv_df) if arxiv_df is not None else None
    github_by_topic = bridge_github_topics(github_df) if github_df is not None else None

    if arxiv_by_topic is not None:
        bridge_tables["bridge_arxiv_by_topic"] = arxiv_by_topic
    if github_by_topic is not None:
        bridge_tables["bridge_github_by_topic"] = github_by_topic
    if arxiv_by_topic is not None and github_by_topic is not None:
        bridge_tables["bridge_topic_timeline"] = bridge_combined_timeline(
            arxiv_by_topic, github_by_topic,
        )
        bridge_tables["bridge_topic_summary"] = bridge_topic_summary(
            arxiv_by_topic, github_by_topic,
        )

    bridge_tables["bridge_taxonomy"] = get_taxonomy()
    exported.extend(_save_tables(bridge_tables, output_dir))

    logger.info("Export complete: %d files in %s", len(exported), output_dir)
    return exported


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    export_all()
