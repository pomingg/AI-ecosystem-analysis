"""Export Tableau-ready CSV files from EDA results.

Loads raw datasets, runs descriptive EDA, and saves each summary
table as a clean CSV in data/processed/.

Usage:
    python -m ai_ecosystem.analysis.export_tableau
"""

import logging
from pathlib import Path

from ai_ecosystem.analysis.descriptive import eda_arxiv, eda_github
from ai_ecosystem.ingest.arxiv import load_arxiv_data
from ai_ecosystem.ingest.github_trending import load_github_trending

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def export_all(output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Run EDA on both datasets and export CSVs for Tableau.

    Args:
        output_dir: Directory to write CSV files.

    Returns:
        List of paths to the exported CSV files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    exported = []

    # --- arXiv ---
    try:
        arxiv_df = load_arxiv_data()
        arxiv_tables = eda_arxiv(arxiv_df)
        for name, table in arxiv_tables.items():
            path = output_dir / f"{name}.csv"
            table.to_csv(path, index=False)
            exported.append(path)
            logger.info("Exported %s (%d rows)", path.name, len(table))
    except FileNotFoundError as e:
        logger.warning("Skipping arXiv export: %s", e)

    # --- GitHub ---
    try:
        github_df = load_github_trending()
        github_tables = eda_github(github_df)
        for name, table in github_tables.items():
            path = output_dir / f"{name}.csv"
            table.to_csv(path, index=False)
            exported.append(path)
            logger.info("Exported %s (%d rows)", path.name, len(table))
    except FileNotFoundError as e:
        logger.warning("Skipping GitHub export: %s", e)

    logger.info("Export complete: %d files in %s", len(exported), output_dir)
    return exported


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    export_all()
