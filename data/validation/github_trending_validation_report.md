# GitHub Top Projects (Monthly) Validation Report

- Generated: 2026-07-20
- Source: https://huggingface.co/datasets/ronantakizawa/github-top-projects

## Overview

- **Total Rows**: 3,200
- **Columns**: 8
- **Time Range**: 2013-08 to 2025-11

## Column Details

| Column | Dtype | Null% | Unique | Sample Values | Status |
|--------|-------|-------|--------|---------------|--------|
| month | object | 0.0% | 128 | ['2025-11', '2025-11', '2025-11'] | ✅ |
| rank | int64 | 0.0% | 25 | [1, 2, 3] | ✅ |
| repository | object | 0.0% | 2188 | ['google/adk-go', 'sansan0/TrendRadar', 'TapXWorld/ChinaT... | ✅ |
| repo_owner | object | 0.0% | 1863 | ['google', 'sansan0', 'TapXWorld'] | ✅ |
| repo_name | object | 0.0% | 2137 | ['adk-go', 'TrendRadar', 'ChinaTextbook'] | ✅ |
| star_count | float64 | 32.2% | 1347 | [5494.0, 32930.0, 60009.0] | ⚠️ |
| fork_count | float64 | 32.2% | 1176 | [366.0, 17869.0, 13357.0] | ⚠️ |
| ranking_appearances | int64 | 0.0% | 132 | [55, 49, 52] | ✅ |

## Key Findings

- ⚠️ Month continuity: 20 gap(s) found — ['2013-09', '2014-01', '2014-03', '2014-07', '2014-09', '2014-10', '2014-11', '2014-12', '2015-05', '2015-09']...
- ✅ Star values appear CUMULATIVE (19/19 sampled repos non-decreasing)
- ⚠️ AI/ML related rows: 491 / 3,200 (15.3%). Unique AI/ML repos: 358 / 2,188 (16.4%)

## Decision

- ⚠️ Only 358 unique AI/ML repos found. Consider broadening keyword list or supplementing with additional data.
