# Verification

Verified September 9, 2026.

## Offline checks

All **50 tests pass** in the public repository. The suite exercises the full 20 → 12 → 8 → 5 workflow with synthetic candidates and evidence, plus replacement screening, persona independence, single revisions, repeated-risk deductions, Referee authority over disqualifications, fewer surviving finalists, source integrity, bounded failure, and cached resume.

Recent regressions cover:

- Explicit final-withdrawal eligibility and candidate-specific retry messages.
- Quotation line wrapping and whitespace tolerance, while rejecting altered wording, punctuation, case, empty quotations, and invalid source attribution.
- Recovery of saved Creator output without regenerating candidates.
- Visibility of eliminated candidates' reserved IDs, minimum survivors, exclusions, and source text during replacement creation.
- Rejection of duplicate IDs and reused names, with precise corrective feedback.
- Direct URL research attempts, conservative coverage downgrades, and archived-response recovery with trace validation.

The example configuration validates with eight readable fictional sources and three priority judges. The macOS launcher's syntax check passes. GitHub Actions passed for the code improvements through commit `0ba7739`; subsequent documentation updates can be checked in the repository's [Actions history](https://github.com/wayanvota/multi-agent-product-naming/actions).

## Scope of this verification

The reproducible evidence published here consists of code, fictional example inputs, and synthetic tests. It does not include a public benchmark of live-run completion reliability or research accuracy. A passing offline pipeline test does not establish that a live web-research stage will finish, that every source interpretation is sound, or that the resulting names will perform well with customers.

The generic changes and their regression coverage are recorded in the [changelog](CHANGELOG.md). No private product inputs, actual naming candidates, source snapshots, or run transcripts are published.

## What remains unvalidated

No study establishes better names, faster naming decisions, financial savings, customer preference, recall, or launch outcomes. Persona judgments are simulations. Web-tool traces and source references establish recorded activity and attribution structure; they do not independently prove every interpretation. Formal trademark review, domain availability, linguistic suitability, and actual customer response require separate verification.

## Reproduce the checks

```sh
python3 naming.py check
python3 -m unittest discover -s tests -v
python3 -m py_compile naming.py contracts.py
zsh -n 'Run Naming.command'
```

The launcher starts a full live run when executed. Its syntax check does not establish that live research will finish. The synthetic examples and test URLs establish no real brand conflict, available name, customer preference, or legal conclusion.
