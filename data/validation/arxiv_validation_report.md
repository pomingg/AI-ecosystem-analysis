# arXiv AI/ML Research Papers Validation Report

- Generated: 2026-07-20
- Source: https://www.kaggle.com/datasets/shree0910/arxiv-aiml-research-papers-20252026

## Overview

- **Total Rows**: 7,701
- **Columns**: 26
- **Time Range**: 2025-09 to 2026-04

## Column Details

| Column | Dtype | Null% | Unique | Sample Values | Status |
|--------|-------|-------|--------|---------------|--------|
| paper_id | object | 0.0% | 7701 | ['2604.26951v1', '2604.26231v1', '2604.26567v1'] | ✅ |
| title | object | 0.0% | 7701 | ['Turning the TIDE: Cross-Architecture Distillation for D... | ✅ |
| authors | object | 0.0% | 7503 | ['Gongbo Zhang; Wen Wang; Ye Tian; Li Yuan', 'Yi Zhang; Y... | ✅ |
| num_authors | int64 | 0.0% | 59 | [4, 5, 9] | ✅ |
| first_author | object | 0.0% | 7037 | ['Gongbo Zhang', 'Yi Zhang', 'Xiaoya Cheng'] | ✅ |
| abstract | object | 0.0% | 7701 | ["Diffusion large language models (dLLMs) offer parallel ... | ✅ |
| abstract_length | int64 | 0.0% | 1306 | [1269, 1748, 1692] | ✅ |
| word_count | int64 | 0.0% | 240 | [167, 233, 217] | ✅ |
| primary_category | object | 0.0% | 107 | ['cs.CL', 'cs.IR', 'cs.CV'] | ✅ |
| all_categories | object | 0.0% | 1597 | ['cs.CL; cs.AI; cs.LG', 'cs.IR', 'cs.CV'] | ✅ |
| num_categories | int64 | 0.0% | 6 | [3, 1, 1] | ✅ |
| submitted_date | object | 0.0% | 211 | ['2026-04-29', '2026-04-29', '2026-04-29'] | ✅ |
| updated_date | object | 0.0% | 209 | ['2026-04-29', '2026-04-29', '2026-04-29'] | ✅ |
| year | int64 | 0.0% | 2 | [2026, 2026, 2026] | ✅ |
| month | int64 | 0.0% | 8 | [4, 4, 4] | ✅ |
| has_journal_ref | int64 | 0.0% | 2 | [0, 0, 0] | ✅ |
| journal_ref | object | 0.0% | 235 | ['Not Available', 'Not Available', 'Not Available'] | ✅ |
| comment | object | 0.0% | 3224 | ['15 pages, 3 figures. Code: https://github.com/PKU-YuanG... | ✅ |
| has_doi | int64 | 0.0% | 2 | [0, 0, 0] | ✅ |
| doi | object | 0.0% | 339 | ['Not Available', 'Not Available', 'Not Available'] | ✅ |
| arxiv_url | object | 0.0% | 7701 | ['https://arxiv.org/abs/2604.26951v1', 'https://arxiv.org... | ✅ |
| pdf_url | object | 0.0% | 7701 | ['https://arxiv.org/pdf/2604.26951v1', 'https://arxiv.org... | ✅ |
| is_large_collaboration | int64 | 0.0% | 2 | [0, 0, 0] | ✅ |
| is_updated | int64 | 0.0% | 2 | [0, 0, 0] | ✅ |
| update_lag_days | int64 | 0.0% | 113 | [0, 0, 0] | ✅ |
| days_since_submission | int64 | 0.0% | 211 | [1, 1, 1] | ✅ |

## Key Findings

- ✅ Time precision: daily or finer (column 'submitted_date', 7701 valid dates, days range 1-31)
- ⚠️ Time span: 7 months — insufficient for robust lead-lag analysis
- ✅ Category distribution — cs.CL: 1,119; cs.CV: 1,418; cs.LG: 1,392; cs.AI: 555 (total unique values: 40)
- ✅ Abstracts — null rate: 0.0%, avg length: 1362 chars, median: 1364 chars, min: 147, max: 2031

## Decision

- ⚠️ Time span < 12 months. Consider switching to the Cornell arXiv dataset (1.7M papers, weekly updates) for better lead-lag statistics.
- ✅ Time precision is daily or finer — meets requirements.
