"""Keyword-based topic taxonomy for bridging arXiv and GitHub datasets.

Maps arXiv primary_category values and GitHub repo keywords into
shared topic buckets so the two datasets can be compared on a
common dimension in Tableau.
"""

import pandas as pd

TOPIC_TAXONOMY: dict[str, dict] = {
    "NLP": {
        "arxiv_categories": ["cs.CL"],
        "github_keywords": [
            "llm", "gpt", "bert", "nlp", "langchain", "chatbot",
            "rag", "mistral", "llama", "gemma",
        ],
    },
    "Computer Vision": {
        "arxiv_categories": ["cs.CV"],
        "github_keywords": [
            "yolo", "detectron", "sam", "computer-vision",
            "opencv", "image", "video",
        ],
    },
    "Machine Learning": {
        "arxiv_categories": ["cs.LG", "stat.ML"],
        "github_keywords": [
            "ml", "machine-learning", "machinelearning",
            "automl", "sklearn", "xgboost",
        ],
    },
    "Deep Learning Frameworks": {
        "arxiv_categories": [],
        "github_keywords": [
            "pytorch", "tensorflow", "keras", "onnx", "vllm",
            "deep-learning", "deeplearning", "neural",
        ],
    },
    "Generative AI": {
        "arxiv_categories": [],
        "github_keywords": [
            "generative", "diffusion", "stable-diffusion",
            "whisper", "copilot",
        ],
    },
    "Fine-tuning & Alignment": {
        "arxiv_categories": [],
        "github_keywords": [
            "fine-tune", "finetune", "lora", "qlora", "rlhf",
        ],
    },
    "AI Agents & Tools": {
        "arxiv_categories": ["cs.AI"],
        "github_keywords": [
            "ai", "agent", "autopilot", "openai", "ollama",
        ],
    },
    "Embeddings & Retrieval": {
        "arxiv_categories": ["cs.IR"],
        "github_keywords": [
            "embedding", "huggingface", "transformer",
        ],
    },
    "Robotics & Control": {
        "arxiv_categories": ["cs.RO"],
        "github_keywords": ["reinforcement"],
    },
    "Other AI/ML": {
        "arxiv_categories": [],
        "github_keywords": [],
    },
}

_arxiv_to_topic: dict[str, str] = {}
for topic, cfg in TOPIC_TAXONOMY.items():
    for cat in cfg["arxiv_categories"]:
        _arxiv_to_topic[cat] = topic

_github_keyword_to_topic: dict[str, str] = {}
for topic, cfg in TOPIC_TAXONOMY.items():
    for kw in cfg["github_keywords"]:
        _github_keyword_to_topic[kw] = topic


def classify_arxiv_topic(primary_category: str) -> str:
    """Map an arXiv primary_category to a topic name."""
    return _arxiv_to_topic.get(primary_category, "Other AI/ML")


def classify_github_topic(repo_name: str, repo_owner: str) -> list[str]:
    """Match a GitHub repo to topic(s) via keyword matching.

    Returns a list of matched topics (may be empty or have multiple).
    """
    text = f"{repo_name} {repo_owner}".lower()
    matched: dict[str, bool] = {}
    for kw, topic in _github_keyword_to_topic.items():
        if kw in text:
            matched[topic] = True
    return list(matched.keys()) if matched else ["Other AI/ML"]


def get_taxonomy() -> pd.DataFrame:
    """Return the taxonomy as a flat table for Tableau reference."""
    rows = []
    for topic, cfg in TOPIC_TAXONOMY.items():
        if topic == "Other AI/ML":
            continue
        for cat in cfg["arxiv_categories"]:
            rows.append({"topic": topic, "source": "arxiv", "match_key": cat})
        for kw in cfg["github_keywords"]:
            rows.append({"topic": topic, "source": "github", "match_key": kw})
    return pd.DataFrame(rows)
