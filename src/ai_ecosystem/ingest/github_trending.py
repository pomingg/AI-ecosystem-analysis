"""Download GitHub top projects dataset from HuggingFace.

This dataset contains monthly snapshots of top GitHub repositories,
tracking stars, forks, and ranking over time.

No authentication required (public dataset).

Usage:
    python -m ai_ecosystem.ingest.github_trending
"""

import logging
from pathlib import Path

import pandas as pd
from datasets import load_dataset

logger = logging.getLogger(__name__)

DATASET_NAME = "ronantakizawa/github-top-projects"
DATASET_CONFIG = "monthly"

# Project root: src/ai_ecosystem/ingest/github_trending.py -> 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "github_trending"
DEFAULT_OUTPUT_FILE = DEFAULT_OUTPUT_DIR / "github_trending_monthly.parquet"


def download_github_trending(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Path:
    """Download the GitHub top projects (monthly) dataset.

    Args:
        output_dir: Directory to store the downloaded data.
        force: If True, re-download even if output file exists.

    Returns:
        Path to the directory containing the downloaded file.
    """
    output_file = output_dir / "github_trending_monthly.parquet"

    if output_file.exists() and not force:
        logger.info(
            "Data already exists at %s — skipping (use force=True to re-download)",
            output_file,
        )
        return output_dir

    logger.info("Loading dataset from HuggingFace: %s (config=%s)", DATASET_NAME, DATASET_CONFIG)
    dataset = load_dataset(DATASET_NAME, DATASET_CONFIG)

    output_dir.mkdir(parents=True, exist_ok=True)

    for split_name, split_data in dataset.items():
        logger.info("Split '%s': %d rows", split_name, len(split_data))
        df = split_data.to_pandas()

        split_file = output_dir / f"github_trending_{split_name}.parquet"
        df.to_parquet(split_file, index=False)
        logger.info("Saved to: %s", split_file)

    # Save the primary file (typically the 'train' split)
    primary_split = list(dataset.keys())[0]
    df = dataset[primary_split].to_pandas()
    df.to_parquet(output_file, index=False)
    logger.info("Primary output: %s (%d rows)", output_file, len(df))

    return output_dir


def load_github_trending(data_dir: Path = DEFAULT_OUTPUT_DIR) -> pd.DataFrame:
    """Load the GitHub trending dataset from disk into a DataFrame.

    Args:
        data_dir: Directory containing the downloaded parquet file.

    Returns:
        DataFrame with the GitHub trending data.

    Raises:
        FileNotFoundError: If no data files are found.
    """
    primary = data_dir / "github_trending_monthly.parquet"
    if primary.exists():
        logger.info("Loading: %s", primary.name)
        return pd.read_parquet(primary)

    parquet_files = sorted(data_dir.glob("*.parquet"))
    if parquet_files:
        logger.info("Loading: %s", parquet_files[0].name)
        return pd.read_parquet(parquet_files[0])

    csv_files = sorted(data_dir.glob("*.csv"))
    if csv_files:
        logger.info("Loading CSV: %s", csv_files[0].name)
        return pd.read_csv(csv_files[0])

    raise FileNotFoundError(
        f"No parquet or CSV files found in {data_dir}. "
        "Run download_github_trending() first."
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    download_github_trending()
