# Mermaid Diagram Fix Plan

## Problem
Mermaid diagrams in documentation files are not rendering on GitHub due to HTML tags (`<br/>`, `<code>`) inside node labels, and complexity issues.

## Diagrams Fixed (Completed)

### README.md - 7 Diagrams - ALL FIXED ✓

| # | Diagram | Status | Changes |
|---|---------|--------|---------|
| 1 | Solution Architecture (flowchart TB) | ✓ Fixed | Removed HTML tags, simplified labels, added `htmlLabels: false` |
| 2 | ETL Workflow (flowchart LR) | ✓ Fixed | Removed HTML tags, simplified labels, added `htmlLabels: false` |
| 3 | Repository Structure (graph TD) | ✓ Fixed | Split multi-line node into separate single-line nodes |
| 4 | Incremental ETL (flowchart LR) | ✓ Fixed | Removed `<br/>` tags, simplified labels, added `htmlLabels: false` |
| 5 | CI Pipeline (flowchart LR) | ✓ Fixed | Removed `<br/>` tags, simplified labels, added `htmlLabels: false` |
| 6 | Validation Framework (flowchart TB) | ✓ Fixed | Removed `<br/>` tags, removed emoji/special chars, added `htmlLabels: false` |
| 7 | Project Roadmap (gantt) | ✓ No changes needed | No HTML tags present |

### docs/Architecture.md - Diagrams - FIXED
| # | Diagram | Status | Changes |
|---|---------|--------|---------|
| 1 | Architecture Diagram (flowchart TB) | ✓ Fixed | Removed `<br/>`, `<code>` tags, added `htmlLabels: false` |
| 2 | Airflow Orchestration (flowchart LR) | ✓ Fixed | Removed `<br/>` tags, added `htmlLabels: false` |
| 3 | Incremental Processing (flowchart LR) | ✓ Fixed | Removed `<br/>` tags, added `htmlLabels: false` |
| 4 | CI/CD Pipeline (flowchart LR) | ✓ Fixed | Removed `<br/>` tags, added `htmlLabels: false` |

### docs/project-flow.md - Diagrams - ALL FIXED ✓
| # | Diagram | Status | Changes |
|---|---------|--------|---------|
| 1 | Pipeline Overview (flowchart TB) | ✓ Fixed | Removed `<br/>`, `<code>` tags, emoji, added `htmlLabels: false` |
| 2 | Python Pipeline (flowchart TB) | ✓ Fixed | Removed `<code>` tag, emoji, added `htmlLabels: false` |

## Approach Used
- Removed all HTML tags (`<br/>`, `<code>`) from Mermaid node labels
- Used simpler plain-text labels with `-` or `()` separators
- Added `%%{init: {"flowchart": {"htmlLabels": false}} }%%` config headers to all flowchart diagrams
- For Repository Structure diagram, split multi-line node into individual single-line nodes
- Removed emoji characters from subgraph names that could cause rendering issues
- Kept the overall structure and data flow intact
