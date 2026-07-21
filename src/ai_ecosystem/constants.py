"""Shared constants for the AI ecosystem analysis project."""

AIML_KEYWORDS = [
    "ai", "ml", "llm", "gpt", "transformer", "neural", "deep-learning",
    "deeplearning", "machine-learning", "machinelearning", "nlp",
    "computer-vision", "pytorch", "tensorflow", "keras", "bert",
    "diffusion", "stable-diffusion", "langchain", "huggingface",
    "openai", "rag", "agent", "rlhf", "reinforcement", "generative",
    "chatbot", "embedding", "fine-tune", "finetune", "lora", "qlora",
    "llama", "mistral", "gemma", "whisper", "sam", "yolo", "detectron",
    "onnx", "vllm", "ollama", "copilot", "autopilot", "automl",
]

# arXiv column names (confirmed from validation report)
ARXIV_COLS = {
    "paper_id": "paper_id",
    "title": "title",
    "authors": "authors",
    "first_author": "first_author",
    "num_authors": "num_authors",
    "abstract": "abstract",
    "abstract_length": "abstract_length",
    "word_count": "word_count",
    "primary_category": "primary_category",
    "all_categories": "all_categories",
    "num_categories": "num_categories",
    "submitted_date": "submitted_date",
    "updated_date": "updated_date",
    "year": "year",
    "month": "month",
}

# GitHub trending column names (confirmed from validation report)
GITHUB_COLS = {
    "month": "month",
    "rank": "rank",
    "repository": "repository",
    "repo_owner": "repo_owner",
    "repo_name": "repo_name",
    "star_count": "star_count",
    "fork_count": "fork_count",
    "ranking_appearances": "ranking_appearances",
}
