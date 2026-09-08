# Multi-agent product naming

A naming workflow that separates idea generation, risk discovery, customer preference, and final judgment. It uses a Creator, an Adversary, three independent persona judges, and a Referee to produce an auditable shortlist of five names.

The point is to preserve strong preference and meaningful disagreement. A name two priority personas love and one distrusts can outperform a name all three merely tolerate. External conflicts are assessed separately from enthusiasm.

**Experimental prototype.** Offline tests exercise the full workflow. A small live test verified Codex session startup and structured output. A complete live naming debate has not yet been validated. Persona reactions are simulated hypotheses, not customer research. Brand screening is preliminary, not trademark clearance.

## How it works

1. Read and snapshot the product documents, three priority profiles, two secondary profiles, and naming history. Validate a source-backed brief before generating names.
2. Generate 20 candidates across at least five naming strategies, with individual rationales and provisional scores.
3. Challenge every candidate using public research. The Referee narrows the pool to 12 and records why others were rejected.
4. Let the Creator defend, concede, withdraw, or replace. Replacements receive new identities and fresh screening.
5. Run the three priority judges independently. Each sees its own profile and the same product/name evidence, without other votes or Creator estimates.
6. Use the Referee's strategic judgments, the three persona scores, and adjudicated risks to select eight semifinalists.
7. Conduct a deeper challenge and, if warranted, one additional targeted evidence round. Each persona may revise once after material evidence arrives.
8. Calculate the final ranking and write a Markdown report with individual reactions, risks, research coverage, the weakest argument for each finalist, and rejection reasons.

Secondary personas provide context, not votes. The Adversary proposes risks but cannot unilaterally disqualify. The Referee cannot generate names or change computed totals in the final report. A run can return fewer than five names when the eligible pool is exhausted.

## Try it

Requires Python 3.11 or later and an installed, signed-in Codex CLI. No Python packages or separate API key are required by this adapter.

```sh
git clone https://github.com/wayanvota/multi-agent-product-naming.git
cd multi-agent-product-naming
python3 naming.py check
python3 -m unittest discover -s tests -v
```

Those commands are offline. Without a local `config.json`, the runner reads `config.example.json`, which points to an entirely fictional community-workshop example.

To make a small live request or start a full naming debate:

```sh
python3 naming.py smoke
python3 naming.py run
```

On macOS, you can also double-click **Run Naming.command**. This starts a full live run. Results appear in a new dated `runs/` folder.

**Live runs use your Codex account and usage.** Configured documents and illustrative profiles are sent to Codex. Candidate names and research terms are sent to public search. Files and orchestration remain local; model processing is not on-device. The runner makes no purchases, publishes nothing, contacts no people, and does not register names or domains.

## Use your own product evidence

```sh
cp config.example.json config.json
mkdir -p private
```

Put your documents in `private/` and edit `config.json`. Set `source_root` relative to the configuration file, or use an absolute path. Configure exactly three distinct priority personas and two secondary personas, product sources, historical sources if any, research markets and languages, and excluded names. The included profiles are examples of input structure, not validated customer segments.

Local configuration, private inputs, and run folders are ignored by Git. Run files contain full source snapshots and agent conversations, so review them before sharing. Ignore rules do not protect files explicitly force-added or already tracked.

The example uses United States/English research and `.com`, `.net`, `.ai`, `.app`, and `.co` checks. Change these for the intended markets and product category. Unchecked languages and inaccessible registries remain unresolved.

## Scoring

| Positive criterion | Weight |
|---|---:|
| Priority persona resonance | 30 |
| Distinctiveness | 15 |
| Memorability | 10 |
| Emotional fit | 10 |
| Credibility | 10 |
| Clarity | 10 |
| Pronunciation and spelling | 5 |
| Searchability | 5 |
| Extensibility | 5 |

Each criterion is judged from 0 to 10. The code applies the weights and computes the total, rather than trusting model-written arithmetic.

Persona resonance uses `0.6 × mean(all three) + 0.4 × mean(strongest two)`. The result is scaled to its 30-point weight. This is a configurable policy favoring concentrated preference, not a validated behavioral model. The report preserves individual scores, mean, spread, strongest-two mean, and preferred/acceptable/rejected reactions. Forced choices remain in the audit record; they do not become a majority vote.

Adjudicated risk is deducted separately: Low 2, Moderate 7, High 18. Repeated manifestations of one underlying issue share an `issue_key` and use only its highest deduction. Total deductions are capped at 35. Unverified leads receive at most 5 per issue and cannot disqualify. Subjective objections receive no second deduction. An upheld, attributable Disqualifying finding removes a name before ranking.

Scores floor at zero. Exact ties break on strongest-two mean, then three-person mean, then stable candidate ID. Adjacent names within two points are reported as effectively tied. Scores express judgment, not probabilities or measured customer preference.

## Audit trail and recovery

Every run saves source snapshots and hashes in `manifest.json`. Numbered stage folders contain exact inputs, role instructions, response schemas, raw tool events, failures, and accepted responses. `candidate-ledger.json` preserves name ancestry, findings, votes, scoring, and eliminations. `shortlist.md` is the human-readable result.

```sh
python3 naming.py resume --run-dir runs/YOUR-RUN-FOLDER
```

Resume reuses accepted stages only with unchanged sources, configuration, prompts, and runner version, on the same UTC day. A new day requires fresh research. Each stage permits two attempts per launch by default, with a 20-minute limit per attempt. Manual resume grants another bounded attempt budget and preserves previous logs. Concurrent use of a run folder is blocked by a lock file.

New runs carry forward rejected names from completed runs in the same parent folder. Set `include_previous_rejections` to `false` to reopen that pool deliberately. Historical rejection is a decision record, not a refreshed external fact.

## Evidence limits

Source quotations must match the supplied text. External factual findings require a URL, excerpt, current date, and a recorded web-search tool event. Checked external categories need queries and supporting URLs. Failed lookups remain partial or unverified. A sparse result set, registered domain, failed page, or registry 404 does not establish legal usability or purchasability.

These controls validate attribution and structure. They cannot prove that every source supports every model interpretation. Review the actual sources before committing to a name. Formal trademark review, linguistic checks, domain purchasing, and real customer preference and recall testing remain separate work.

Child sessions use a read-only sandbox, an isolated temporary working directory, disabled shell tools, and fresh contexts. They do not load personal Codex configuration. Only the Adversary has web search. The adapter uses existing Codex authentication and does not provision an API key. See [OpenAI's non-interactive mode reference](https://learn.chatgpt.com/docs/non-interactive-mode) for the underlying runner.

## Repository contents

- `naming.py`: orchestration, provenance checks, resume, and report generation.
- `contracts.py`: strict response contracts, validation, and deterministic scoring.
- `prompts/`: separate instructions for each decision function and stage.
- `config.example.json` and `examples/demo/`: generic configuration and fictional inputs.
- `tests/`: offline contract and end-to-end tests with synthetic evidence.
- `BUILD-SPEC.md`: the reusable product requirements.
- `VERIFICATION.md`: completed checks and unvalidated behavior.

No real product profiles, business documents, candidate research, local account data, or naming-run artifacts are included.
