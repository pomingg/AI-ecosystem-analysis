# AI Ecosystem Cross-Dataset Analysis

Cross-dataset analysis bridging arXiv AI/ML research trends with GitHub
open-source adoption patterns. How long does it take for a hot research topic
to become a trending open-source tool? Which topics are flash-in-the-pan, and
which become evergreen?

**Status: v0.1** — Data ingestion and validation pipeline.

## Data Sources

| Dataset | Source | Records | Description |
|---------|--------|---------|-------------|
| arXiv AI/ML Papers | [Kaggle](https://www.kaggle.com/datasets/shree0910/arxiv-aiml-research-papers-20252026) | ~7,700 | AI/ML research papers with titles, abstracts, and categories |
| GitHub Top Projects | [HuggingFace](https://huggingface.co/datasets/ronantakizawa/github-top-projects) | ~420,000 | Monthly snapshots of top GitHub repositories (2013–2025) |

## Setup

```bash
# Clone the repository
git clone https://github.com/pomingg/ai-ecosystem-analysis.git
cd ai-ecosystem-analysis

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in development mode
pip install -e ".[dev]"
```

### Kaggle Credentials

The arXiv dataset requires Kaggle API credentials. Set up one of:

1. **Environment variables**: `KAGGLE_USERNAME` and `KAGGLE_KEY`
2. **Config file**: Place `kaggle.json` at `~/.kaggle/kaggle.json`

See the [Kaggle API docs](https://www.kaggle.com/docs/api) for details.

## Usage

```bash
# Download arXiv dataset
python -m ai_ecosystem.ingest.arxiv

# Download GitHub trending dataset
python -m ai_ecosystem.ingest.github_trending

# Run data validation (generates reports in data/validation/)
python -m ai_ecosystem.ingest.validate
```

## Version Roadmap

| Version | Layer | Milestone |
|---------|-------|-----------|
| **v0.1** | — | Repo skeleton, data ingestion, validation |
| v0.2 | Descriptive | EDA for each dataset, Tableau-ready data output |
| v0.3 | Bridging | Topic keyword extraction, cross-dataset alignment (NLP) |
| v0.4 | Diagnostic | Lead-lag analysis, cross-correlation, time gap detection |
| v0.5 | Predictive | ML model to predict next trending research topics |
| v0.6 | Prescriptive | Actionable recommendations and strategic insights |
| v1.0 | Integration | Insight report + Tableau Public dashboard + release |

## Project Structure

```
ai-ecosystem-analysis/
├── src/ai_ecosystem/
│   ├── ingest/          # Data download, validation
│   ├── bridge/          # Topic bridging (Layer 1-3)
│   ├── analysis/        # Lead-lag, cross-correlation
│   └── viz/             # Streamlit dashboard
├── notebooks/           # EDA and experiments
├── data/
│   ├── raw/             # Downloaded data (git-ignored)
│   ├── processed/       # Cleaned data (git-ignored)
│   └── validation/      # Validation reports (tracked)
├── tests/               # pytest test suite
├── reports/             # Analysis reports
├── dashboards/          # Tableau Public links
└── docs/                # Methodology documentation
```

## Development

```bash
# Run linter
ruff check src/ tests/

# Run tests
pytest -v
```

## License

MIT
