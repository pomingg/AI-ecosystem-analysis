"""Validate downloaded datasets and generate markdown reports.

Runs quality checks on arXiv and GitHub trending datasets,
outputting structured markdown reports to data/validation/.

Usage:
    python -m ai_ecosystem.ingest.validate
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ai_ecosystem.constants import AIML_KEYWORDS

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VALIDATION_DIR = PROJECT_ROOT / "data" / "validation"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find a DataFrame column by trying candidate names (case-insensitive).

    Tries exact match first, then partial (substring) match.

    Args:
        df: The DataFrame to search.
        candidates: List of possible column name patterns.

    Returns:
        The actual column name if found, None otherwise.
    """
    cols_lower = {c.lower(): c for c in df.columns}

    # Exact match
    for candidate in candidates:
        if candidate.lower() in cols_lower:
            return cols_lower[candidate.lower()]

    # Partial match
    for candidate in candidates:
        for col_lower, col_orig in cols_lower.items():
            if candidate.lower() in col_lower:
                return col_orig

    return None


class ValidationReport:
    """Builds a structured markdown validation report."""

    def __init__(self, dataset_name: str, source_url: str = ""):
        self.dataset_name = dataset_name
        self.source_url = source_url
        self.timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        self.overview: dict[str, str] = {}
        self.column_rows: list[dict] = []
        self.findings: list[dict] = []
        self.decisions: list[str] = []

    def set_overview(self, total_rows: int, num_columns: int, time_range: str):
        self.overview = {
            "total_rows": f"{total_rows:,}",
            "columns": str(num_columns),
            "time_range": time_range,
        }

    def add_column_detail(
        self,
        name: str,
        dtype: str,
        null_pct: float,
        unique: int,
        sample_values: str,
        status: str = "✅",
    ):
        self.column_rows.append({
            "name": name,
            "dtype": dtype,
            "null_pct": f"{null_pct:.1f}%",
            "unique": str(unique),
            "sample_values": sample_values,
            "status": status,
        })

    def add_finding(self, text: str, status: str = "INFO"):
        """Add a key finding. status: PASS / WARN / FAIL / INFO."""
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "INFO": "ℹ️"}.get(status, "")
        self.findings.append({"text": text, "icon": icon})

    def add_decision(self, text: str):
        self.decisions.append(text)

    def to_markdown(self) -> str:
        lines = [
            f"# {self.dataset_name} Validation Report",
            "",
            f"- Generated: {self.timestamp}",
        ]
        if self.source_url:
            lines.append(f"- Source: {self.source_url}")

        # Overview
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        for key, val in self.overview.items():
            lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        # Column Details
        if self.column_rows:
            lines.append("")
            lines.append("## Column Details")
            lines.append("")
            lines.append("| Column | Dtype | Null% | Unique | Sample Values | Status |")
            lines.append("|--------|-------|-------|--------|---------------|--------|")
            for row in self.column_rows:
                lines.append(
                    f"| {row['name']} | {row['dtype']} | {row['null_pct']} "
                    f"| {row['unique']} | {row['sample_values']} | {row['status']} |"
                )

        # Key Findings
        if self.findings:
            lines.append("")
            lines.append("## Key Findings")
            lines.append("")
            for f in self.findings:
                lines.append(f"- {f['icon']} {f['text']}")

        # Decisions
        if self.decisions:
            lines.append("")
            lines.append("## Decision")
            lines.append("")
            for d in self.decisions:
                lines.append(f"- {d}")

        lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# arXiv validation
# ---------------------------------------------------------------------------

def validate_arxiv(df: pd.DataFrame) -> ValidationReport:
    """Run all validation checks on the arXiv dataset.

    Args:
        df: arXiv papers DataFrame.

    Returns:
        A populated ValidationReport.
    """
    report = ValidationReport(
        "arXiv AI/ML Research Papers",
        source_url="https://www.kaggle.com/datasets/shree0910/arxiv-aiml-research-papers-20252026",
    )

    # --- Column details ---
    for col in df.columns:
        null_pct = df[col].isna().mean() * 100
        unique = df[col].nunique()
        sample = str(df[col].dropna().head(3).tolist())
        if len(sample) > 60:
            sample = sample[:57] + "..."
        status = "⚠️" if null_pct > 20 else "✅"
        report.add_column_detail(col, str(df[col].dtype), null_pct, unique, sample, status)

    # --- Time field analysis ---
    time_col = find_column(df, [
        "submitted_date", "submission_date", "date", "published",
        "created", "update_date", "last_revised_date",
    ])

    time_range_str = "N/A"
    if time_col:
        try:
            dates = pd.to_datetime(df[time_col], errors="coerce")
            valid_dates = dates.dropna()
            if len(valid_dates) > 0:
                date_min = valid_dates.min()
                date_max = valid_dates.max()
                time_range_str = f"{date_min.strftime('%Y-%m')} to {date_max.strftime('%Y-%m')}"

                day_values = valid_dates.dt.day.unique()
                if len(day_values) > 1:
                    report.add_finding(
                        f"Time precision: daily or finer "
                        f"(column '{time_col}', {len(valid_dates)} valid dates, "
                        f"days range {day_values.min()}-{day_values.max()})",
                        "PASS",
                    )
                else:
                    report.add_finding(
                        f"Time precision: monthly only "
                        f"(column '{time_col}', all on day {day_values[0]})",
                        "PASS",
                    )

                span_months = (
                    (date_max.year - date_min.year) * 12
                    + (date_max.month - date_min.month)
                )
                if span_months < 12:
                    report.add_finding(
                        f"Time span: {span_months} months "
                        "— insufficient for robust lead-lag analysis",
                        "WARN",
                    )
                else:
                    report.add_finding(
                        f"Time span: {span_months} months — sufficient for lead-lag analysis",
                        "PASS",
                    )

                parse_fail_pct = (1 - len(valid_dates) / len(df)) * 100
                if parse_fail_pct > 5:
                    report.add_finding(
                        f"Date parsing: {parse_fail_pct:.1f}% of rows failed to parse",
                        "WARN",
                    )
            else:
                report.add_finding(f"Time field '{time_col}' could not be parsed as dates", "FAIL")
                time_range_str = "PARSE ERROR"
        except Exception as e:
            report.add_finding(f"Error analyzing time field '{time_col}': {e}", "FAIL")
    else:
        report.add_finding(
            f"No time/date column found. Available columns: {list(df.columns)}",
            "FAIL",
        )

    report.set_overview(len(df), len(df.columns), time_range_str)

    # --- Category distribution ---
    cat_col = find_column(df, ["categories", "category", "primary_category", "subject"])
    if cat_col:
        cat_counts = df[cat_col].value_counts()
        target_cats = ["cs.CL", "cs.CV", "cs.LG", "cs.AI"]
        cat_summary_parts = []
        for cat in target_cats:
            # Categories may be multi-valued (e.g. "cs.CV cs.LG"), so check with str.contains
            count = df[cat_col].astype(str).str.contains(cat, na=False).sum()
            cat_summary_parts.append(f"{cat}: {count:,}")
        report.add_finding(
            f"Category distribution — {'; '.join(cat_summary_parts)} "
            f"(total unique values: {cat_counts.nunique():,})",
            "PASS",
        )
    else:
        report.add_finding("No category column found", "WARN")

    # --- Abstract analysis ---
    abs_col = find_column(df, ["abstract", "summary", "description"])
    if abs_col:
        null_rate = df[abs_col].isna().mean() * 100
        lengths = df[abs_col].dropna().str.len()
        report.add_finding(
            f"Abstracts — null rate: {null_rate:.1f}%, "
            f"avg length: {lengths.mean():.0f} chars, "
            f"median: {lengths.median():.0f} chars, "
            f"min: {lengths.min():.0f}, max: {lengths.max():.0f}",
            "PASS" if null_rate < 5 else "WARN",
        )
    else:
        report.add_finding("No abstract column found", "WARN")

    # --- Decisions ---
    if time_col:
        dates = pd.to_datetime(df[time_col], errors="coerce").dropna()
        if len(dates) > 0:
            span = (
                (dates.max().year - dates.min().year) * 12
                + (dates.max().month - dates.min().month)
            )
            if span < 12:
                report.add_decision(
                    "⚠️ Time span < 12 months. Consider switching to the Cornell "
                    "arXiv dataset (1.7M papers, weekly updates) for better lead-lag statistics."
                )
            else:
                report.add_decision("✅ Time span is sufficient. No need to switch data sources.")

            day_values = dates.dt.day.unique()
            if len(day_values) <= 1:
                report.add_decision(
                    "⚠️ Time precision is monthly only. Daily precision would be ideal "
                    "but monthly is acceptable for this analysis."
                )
            else:
                report.add_decision("✅ Time precision is daily or finer — meets requirements.")
    else:
        report.add_decision("❌ No usable time field found. Must switch to Cornell arXiv dataset.")

    return report


# ---------------------------------------------------------------------------
# GitHub trending validation
# ---------------------------------------------------------------------------

def validate_github(df: pd.DataFrame) -> ValidationReport:
    """Run all validation checks on the GitHub trending dataset.

    Args:
        df: GitHub trending repositories DataFrame.

    Returns:
        A populated ValidationReport.
    """
    report = ValidationReport(
        "GitHub Top Projects (Monthly)",
        source_url="https://huggingface.co/datasets/ronantakizawa/github-top-projects",
    )

    # --- Column details ---
    for col in df.columns:
        null_pct = df[col].isna().mean() * 100
        unique = df[col].nunique()
        sample = str(df[col].dropna().head(3).tolist())
        if len(sample) > 60:
            sample = sample[:57] + "..."
        status = "⚠️" if null_pct > 20 else "✅"
        report.add_column_detail(col, str(df[col].dtype), null_pct, unique, sample, status)

    # --- Time range ---
    month_col = find_column(df, ["month", "date", "snapshot_date", "yearmonth"])
    time_range_str = "N/A"

    if month_col:
        months = df[month_col].dropna().astype(str).unique()
        months_sorted = sorted(months)
        if len(months_sorted) > 0:
            time_range_str = f"{months_sorted[0]} to {months_sorted[-1]}"

    report.set_overview(len(df), len(df.columns), time_range_str)

    # --- Month continuity ---
    if month_col:
        months_series = pd.to_datetime(df[month_col].astype(str), format="mixed", errors="coerce")
        unique_months = sorted(months_series.dropna().dt.to_period("M").unique())

        if len(unique_months) > 1:
            expected_range = pd.period_range(
                start=unique_months[0], end=unique_months[-1], freq="M"
            )
            missing = set(expected_range) - set(unique_months)
            if missing:
                missing_sorted = sorted(str(m) for m in missing)
                report.add_finding(
                    f"Month continuity: {len(missing)} gap(s) found — {missing_sorted[:10]}"
                    + ("..." if len(missing) > 10 else ""),
                    "WARN",
                )
            else:
                report.add_finding(
                    f"Month continuity: {len(unique_months)} consecutive months, no gaps",
                    "PASS",
                )
        else:
            report.add_finding(
                f"Only {len(unique_months)} unique month(s) found",
                "WARN",
            )
    else:
        report.add_finding("No month/date column found", "FAIL")

    # --- Star/fork: cumulative vs incremental ---
    star_col = find_column(df, ["star_count", "stars", "stargazers_count"])
    repo_col = find_column(df, ["repository", "repo_name", "name", "full_name"])

    if star_col and repo_col and month_col:
        # Sample a few repos that appear in multiple months
        repo_counts = df[repo_col].value_counts()
        multi_month_repos = repo_counts[repo_counts >= 3].index[:20]

        if len(multi_month_repos) > 0:
            cumulative_count = 0
            decreasing_count = 0

            for repo in multi_month_repos:
                repo_data = df[df[repo_col] == repo].sort_values(month_col)
                stars = repo_data[star_col].dropna().values
                if len(stars) >= 2:
                    diffs = [stars[i + 1] - stars[i] for i in range(len(stars) - 1)]
                    if all(d >= 0 for d in diffs):
                        cumulative_count += 1
                    if any(d < 0 for d in diffs):
                        decreasing_count += 1

            total_checked = cumulative_count + decreasing_count
            if total_checked > 0:
                if cumulative_count > decreasing_count:
                    report.add_finding(
                        f"Star values appear CUMULATIVE "
                        f"({cumulative_count}/{total_checked} sampled repos "
                        f"non-decreasing)",
                        "PASS",
                    )
                else:
                    report.add_finding(
                        f"Star values appear SNAPSHOTS or INCREMENTAL "
                        f"({decreasing_count}/{total_checked} repos show "
                        f"decreasing values between months)",
                        "INFO",
                    )
            else:
                report.add_finding(
                    "Could not determine star value type "
                    "(insufficient multi-month data)",
                    "WARN",
                )
        else:
            report.add_finding(
                "No repos appear in 3+ months "
                "— cannot determine cumulative vs incremental",
                "WARN",
            )
    elif not star_col:
        report.add_finding("No star count column found", "WARN")

    # --- AI/ML proportion ---
    name_col = find_column(df, ["repository", "repo_name", "name", "full_name"])
    if name_col:
        name_lower = df[name_col].astype(str).str.lower()
        pattern = "|".join(AIML_KEYWORDS)
        aiml_mask = name_lower.str.contains(pattern, na=False)
        aiml_count = aiml_mask.sum()
        aiml_unique = df.loc[aiml_mask, name_col].nunique()
        total_unique = df[name_col].nunique()

        row_pct = aiml_count / len(df) * 100
        repo_pct = aiml_unique / total_unique * 100
        report.add_finding(
            f"AI/ML related rows: {aiml_count:,} / {len(df):,} "
            f"({row_pct:.1f}%). "
            f"Unique AI/ML repos: {aiml_unique:,} / {total_unique:,} "
            f"({repo_pct:.1f}%)",
            "PASS" if aiml_unique >= 2000 else "WARN",
        )
    else:
        report.add_finding(
            "No repo name column found — cannot estimate AI/ML proportion",
            "FAIL",
        )

    # --- Decisions ---
    if name_col:
        name_lower = df[name_col].astype(str).str.lower()
        pattern = "|".join(AIML_KEYWORDS)
        aiml_mask = name_lower.str.contains(pattern, na=False)
        aiml_unique = df.loc[aiml_mask, name_col].nunique()
        if aiml_unique < 2000:
            report.add_decision(
                f"⚠️ Only {aiml_unique:,} unique AI/ML repos found. "
                "Consider broadening keyword list or "
                "supplementing with additional data."
            )
        else:
            report.add_decision(
                f"✅ {aiml_unique:,} unique AI/ML repos "
                "— sufficient sample size."
            )

    return report


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_validation() -> None:
    """Load datasets and run all validations, writing reports to data/validation/."""
    from ai_ecosystem.ingest.arxiv import load_arxiv_data
    from ai_ecosystem.ingest.github_trending import load_github_trending

    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    # Validate arXiv
    try:
        arxiv_df = load_arxiv_data()
        report = validate_arxiv(arxiv_df)
        output_path = VALIDATION_DIR / "arxiv_validation_report.md"
        output_path.write_text(report.to_markdown(), encoding="utf-8")
        logger.info("arXiv validation report written to: %s", output_path)
    except FileNotFoundError as e:
        logger.warning("Skipping arXiv validation: %s", e)

    # Validate GitHub
    try:
        github_df = load_github_trending()
        report = validate_github(github_df)
        output_path = VALIDATION_DIR / "github_trending_validation_report.md"
        output_path.write_text(report.to_markdown(), encoding="utf-8")
        logger.info("GitHub validation report written to: %s", output_path)
    except FileNotFoundError as e:
        logger.warning("Skipping GitHub validation: %s", e)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run_validation()
