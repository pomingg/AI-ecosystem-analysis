"""Download arXiv AI/ML research papers dataset from Kaggle.

Authentication:
    Set up Kaggle credentials before running. Either:
    1. Place kaggle.json at ~/.kaggle/kaggle.json, or
    2. Set KAGGLE_USERNAME and KAGGLE_KEY environment variables.
    See: https://www.kaggle.com/docs/api

Usage:
    python -m ai_ecosystem.ingest.arxiv
"""

import logging
import shutil
from pathlib import Path

import kagglehub
import pandas as pd

logger = logging.getLogger(__name__)

DATASET_HANDLE = "shree0910/arxiv-aiml-research-papers-20252026"

# Project root: src/ai_ecosystem/ingest/arxiv.py -> 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "arxiv"


def download_arxiv_dataset(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Path:
    """Download the arXiv AI/ML dataset to the specified directory.

    Args:
        output_dir: Directory to store the downloaded data.
        force: If True, re-download even if files already exist.

    Returns:
        Path to the directory containing the downloaded files.
    """
    if not force and output_dir.exists() and any(output_dir.iterdir()):
        logger.info(
            "Data already exists at %s — skipping (use force=True to re-download)",
            output_dir,
        )
        return output_dir

    logger.info("Downloading arXiv dataset: %s", DATASET_HANDLE)
    try:
        cached_path = kagglehub.dataset_download(
            DATASET_HANDLE, force_download=force
        )
    except Exception:
        logger.exception(
            "Failed to download dataset. Check your Kaggle credentials: "
            "https://www.kaggle.com/docs/api"
        )
        raise

    logger.info("Dataset cached at: %s", cached_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(cached_path, output_dir, dirs_exist_ok=True)

    files = list(output_dir.iterdir())
    logger.info("Downloaded %d file(s) to %s: %s", len(files), output_dir, [f.name for f in files])

    return output_dir


def load_arxiv_data(data_dir: Path = DEFAULT_OUTPUT_DIR) -> pd.DataFrame:
    """Load the arXiv dataset from disk into a DataFrame.

    Tries CSV first, then parquet.

    Args:
        data_dir: Directory containing the downloaded data files.

    Returns:
        DataFrame with the arXiv paper data.

    Raises:
        FileNotFoundError: If no data files are found.
    """
    csv_files = sorted(data_dir.glob("*.csv"))
    parquet_files = sorted(data_dir.glob("*.parquet"))

    if csv_files:
        logger.info("Loading CSV: %s", csv_files[0].name)
        return pd.read_csv(csv_files[0])
    elif parquet_files:
        logger.info("Loading parquet: %s", parquet_files[0].name)
        return pd.read_parquet(parquet_files[0])
    else:
        raise FileNotFoundError(
            f"No CSV or parquet files found in {data_dir}. "
            "Run download_arxiv_dataset() first."
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    download_arxiv_dataset()
