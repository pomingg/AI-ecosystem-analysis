"""Smoke tests for ingestion module — no data files required."""


def test_package_import():
    import ai_ecosystem

    assert ai_ecosystem.__version__ == "0.1.0"


def test_ingest_modules_importable():
    from ai_ecosystem.ingest import arxiv, github_trending

    assert hasattr(arxiv, "download_arxiv_dataset")
    assert hasattr(github_trending, "download_github_trending")
