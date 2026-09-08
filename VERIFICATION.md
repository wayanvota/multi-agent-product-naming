# Verification

The offline test suite checks the full 20 → 12 → 8 → 5 workflow using synthetic candidates and evidence. It also exercises replacement screening, persona independence, single revisions, repeated-risk deductions, Referee authority over disqualifications, fewer surviving finalists, source integrity, bounded failure, and cached resume.

A small live Codex request previously verified session startup and structured output using the same adapter. A complete live naming debate and the quality or availability of actual public research have not been validated. No real shortlist is included.

Reproduce the offline checks:

```sh
python3 naming.py check
python3 -m unittest discover -s tests -v
python3 -m py_compile naming.py contracts.py
```

On macOS, check the launcher syntax with `zsh -n 'Run Naming.command'`. The launcher itself starts a full live run; a syntax check does not establish that all its research stages will complete.

The synthetic examples and test source URLs do not establish any brand conflict, available name, actual customer preference, or legal conclusion.
