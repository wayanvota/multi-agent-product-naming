# Changelog

## September 9, 2026

- Give replacement agents all reserved candidate IDs and names, including eliminated candidates, plus exclusions, source text, and the required survivor count. Report ID collisions separately from name reuse. [Code and tests](https://github.com/wayanvota/multi-agent-product-naming/commit/0ba7739).
- Ignore whitespace and source line wrapping during quote validation, while preserving wording, case, punctuation, and attribution requirements. Revalidate eligible saved responses without regenerating names. [Code and tests](https://github.com/wayanvota/multi-agent-product-naming/commit/59f2fe5).
- Supply exact final-withdrawal eligibility and actionable retry errors. Archive changed requests before retrying a failed stage. [Code and tests](https://github.com/wayanvota/multi-agent-product-naming/commit/1bb0b37).
- Update the README and verification record with 50 passing public offline tests and explicit limits on what synthetic tests establish. Add a 1,000-word synopsis of intended users, benefits, and limitations.

## September 8, 2026

- Accept recorded direct URL lookups as research attempts. Downgrade checked searches without source URLs to partial coverage. Revalidate unchanged archived responses only after current schema, evidence, and tool-trace checks pass. [Code and tests](https://github.com/wayanvota/multi-agent-product-naming/commit/397e689).
- Constrain source references to actual source IDs and appropriate evidence fields before generation. [Code and tests](https://github.com/wayanvota/multi-agent-product-naming/commit/4b334cb).

The changelog describes the reusable core. Private product materials and naming results remain outside this repository.
