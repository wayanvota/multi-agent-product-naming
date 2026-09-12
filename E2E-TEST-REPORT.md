# Multi-agent product naming end-to-end test report

## Scope

This harness exercises the Python runner from the public CLI configuration
through source snapshots, the complete synthetic 20 to 12 to 8 to 5 debate,
replacement lineage, persona isolation, bounded research rounds, scoring,
resume, audit files, and final Markdown report. It uses fictional inputs and the
existing synthetic backend. It never calls Codex, OpenAI, public search, domain
services, or trademark services.

## Required categories

| ID | Category | Expected behavior |
| --- | --- | --- |
| U01 | CLI check | Public example validates through `naming.py` |
| U02 | Source snapshot | Eight configured sources are hashed |
| U03 | Full run | Five ranked finalists and complete status are written |
| U04 | Stage counts | 20 to 12 to 8 to 5 contract is preserved |
| U05 | Replacement | Parentage survives and withdrawn identity stays out |
| U06 | Persona isolation | Three judges receive independent inputs |
| U07 | Bounded debate | One gate, two challenges, three revisions |
| U08 | Decision report | Evidence, disagreement, limits, and rejections render |
| U09 | Resume | Same-day accepted work is reused |
| U10 | Provenance | Manifest hashes match source snapshots |
| A01 | Path traversal | Source cannot escape configured root |
| A02 | Source mutation | Midrun change stops the pipeline |
| A03 | Persona collision | Duplicate priority identities are rejected |
| A04 | Invalid weights | Non-100 total is rejected |
| A05 | Missing source | Missing evidence file is not ignored |
| A06 | Unsupported research | Bounded retries end without a shortlist |
| A07 | Disqualification | Final count may fall below five visibly |
| A08 | Evidence crossover | Unrelated revision evidence is rejected |
| A09 | Concurrent run | Existing lock fails closed |
| A10 | Stale research | Next-day resume requires a fresh run |

## Verification record

Status: local verification passed on September 11, 2026. GitHub Actions
verification is pending the branch push.

```bash
python3 naming.py check
python3 -m unittest discover -s tests -v
python3 -m py_compile naming.py contracts.py
zsh -n 'Run Naming.command'
```

The E2E layer contains exactly U01-U10 and A01-A10. Live runs remain outside
this deterministic gate because they consume the signed-in Codex account and
may perform public web research.

Local results with Python 3.12:

- 20 of 20 explicit E2E categories passed.
- 70 of 70 total tests passed.
- The public configuration check passed with eight readable sources and three
  primary judges.
- Python byte-compilation and launcher syntax checks passed.
