# PRD: Multi-Agent Product Naming System

**Version:** 1.0  
**Date:** September 8, 2026  
**Status:** Build specification  
**Primary implementation environment:** Codex project

## 1. Product Summary

Build a multi-agent naming system that reads existing project files describing the product and its target customers, generates potential product names, subjects those names to adversarial review, evaluates them through the perspectives of three priority customer personas, and produces a final ranked shortlist of five names.

The system should simulate a structured naming debate rather than a single-pass brainstorming exercise.

The core objective is:

> Produce five product names that generate strong preference among the three priority customer personas while surviving serious challenges around distinctiveness, credibility, brand space, confusion, and naming risk.

The system should optimize for **strength of preference**, not bland consensus.

---

## 2. Product Goal

The tool should answer:

**Given what this product does, who its most important customers are, and the competitive naming environment, what five names have the strongest combination of customer resonance and defensible brand space?**

The system should make its reasoning visible. A user should be able to understand:

- Why each name was proposed.
- Which personas respond strongly to it.
- Which personas dislike or distrust it.
- What weaknesses the adversarial review identified.
- Whether the name appears to have usable brand space.
- Why the referee ultimately advanced or rejected it.

---

## 3. Source Material

The tool operates inside an existing Codex project.

It should inspect relevant project files before beginning the naming process. These files may include:

- Product concept documents.
- Product requirements or strategy documents.
- Competitive analysis.
- Existing naming research.
- Five customer persona profiles.
- Psychographic descriptions.
- Demographic descriptions.
- Brand positioning or messaging.
- Previous naming attempts or rejected names.

The system must distinguish between:

1. **Three priority personas**, whose preferences drive the naming decision.
2. **Two secondary personas**, which provide context but do not vote in the primary naming process.

The secondary personas must not be allowed to dilute or override strong preference among the three priority personas.

If the project files do not clearly identify which three personas are primary, the system should require that configuration before running the naming process.

---

## 4. Agent Architecture

The initial system contains six functional agents.

### Agent 1: Name Creator

**Purpose:** Generate strong, differentiated naming candidates.

The Creator should:

- Read the product and customer evidence.
- Generate a deliberately diverse naming pool.
- Avoid producing twenty minor variations of the same idea.
- Explain the strategic logic behind every candidate.
- Identify which customer motivations or psychographics the name is intended to activate.
- Estimate how the name performs against the naming rubric.
- Respond to substantive criticism from the Adversary and persona agents.
- Revise or replace weak candidates when appropriate.

The Creator is an advocate for good ideas, but should not defend a name merely because it generated it.

### Agent 2: Adversary

**Purpose:** Try to kill weak names before they reach the final shortlist.

The Adversary should assume that attractive naming ideas may contain hidden weaknesses.

It should challenge candidates for issues including:

- Existing companies with identical or highly similar names.
- Similar products using confusingly similar names.
- Weak brand space.
- Trademark risk signals.
- Genericness.
- Search competition.
- Negative meanings or associations.
- Pronunciation problems.
- Spelling ambiguity.
- Confusion with unrelated products or categories.
- Trendiness or likelihood of aging badly.
- Cultural or international interpretation problems.
- Excessive abstraction.
- Misleading product implications.
- Lack of credibility.
- Domain and digital identity constraints where relevant.

The Adversary is **not a voter**. Its role is risk discovery.

A serious factual conflict may trigger a substantial penalty or disqualification. Mere personal dislike should not.

Where external verification is available, factual claims about companies, trademarks, domains, app stores, search competition, or other brand conflicts should be researched rather than invented.

### Agents 3–5: Priority Persona Judges

Create one agent for each of the three priority customer personas.

Each persona agent should be grounded in the corresponding persona file rather than a generic demographic stereotype.

Each agent should evaluate names from the perspective of that customer's:

- Needs.
- Motivations.
- Anxieties.
- Aspirations.
- Trust triggers.
- Skepticism.
- Vocabulary.
- Product expectations.
- Emotional response.
- Likely buying or adoption behavior.

Each persona agent should answer questions such as:

- Would I remember this?
- Would I understand enough to become curious?
- Would I trust something with this name?
- Does this sound like it is meant for someone like me?
- Does it activate an important need or aspiration?
- Does it create an unwanted association?
- Would I tell another person about it?
- Which candidate would I choose if these were competing products?

Persona agents should be allowed to disagree strongly.

The system should preserve those disagreements rather than forcing artificial consensus.

### Agent 6: Referee

**Purpose:** Manage the process and select the final five names.

The Referee does not generate names.

It should:

- Manage each round.
- Enforce the evaluation rubric.
- Track candidate scores and arguments.
- Eliminate weak candidates.
- Identify unresolved disagreements.
- Request another round when evidence could materially change a decision.
- Prevent endless debate.
- Distinguish factual risk from subjective preference.
- Give priority to the three customer persona agents.
- Apply adversarial findings as risk penalties.
- Produce the final ranking.

The Referee's goal is not unanimous agreement.

Its goal is to identify the five candidates with the strongest combination of:

**customer desire + strategic naming quality - material naming risk**

---

## 5. Evaluation Framework

Names should be scored against a common 100-point positive-value rubric.

| Criterion | Weight | Question |
|---|---:|---|
| Priority persona resonance | 30 | How strongly does this appeal to the three priority personas? |
| Distinctiveness | 15 | Does the name stand apart from competitors and category conventions? |
| Memorability | 10 | Is it likely to be remembered after limited exposure? |
| Emotional fit | 10 | Does it evoke the right feeling, aspiration, or relationship? |
| Credibility | 10 | Does it sound trustworthy and appropriate for the product promise? |
| Clarity | 10 | Does it provide useful orientation without requiring excessive explanation? |
| Pronunciation and spelling | 5 | Can people comfortably say, hear, spell, and repeat it? |
| Searchability / brand discoverability | 5 | Can the product plausibly establish a distinct searchable identity? |
| Extensibility | 5 | Can the name support future products, features, or positioning? |

**Total positive score: 100**

### Persona Resonance

The 30-point persona-resonance component should be based only on the three priority personas.

The system should preserve each persona's individual score and explanation rather than displaying only an average.

A candidate that inspires strong preference in two personas and skepticism in one may be more interesting than a candidate all three merely find acceptable.

The Referee should therefore consider both:

- Average persona score.
- Strength and distribution of preference.

### Adversarial Risk

Adversarial review is handled separately from the positive 100-point score.

Risk categories should be rated:

- None
- Low
- Moderate
- High
- Disqualifying

Risk findings may reduce a candidate's final score or remove it entirely.

A factual conflict such as a highly similar technology product occupying the same brand territory should receive substantially more weight than a subjective criticism such as "the name feels slightly cold."

---

## 6. Naming Workflow

### Stage 1: Evidence Intake

The system reads the relevant project files and produces an internal naming brief containing:

- Product purpose.
- Core value proposition.
- Three priority personas.
- Relevant secondary-persona context.
- Customer motivations.
- Customer anxieties.
- Desired brand characteristics.
- Competitive context.
- Explicit naming constraints.
- Previously rejected names, if available.

No names should be generated before this step is complete.

### Stage 2: Initial Generation

The Creator generates approximately **15–20 candidates**.

The candidate pool should intentionally cover multiple naming strategies, such as:

- Descriptive.
- Suggestive.
- Metaphorical.
- Evocative.
- Compound words.
- Invented words.
- Familiar words used in an unexpected context.

For each candidate, provide:

- Name.
- Pronunciation if ambiguous.
- Naming strategy.
- Rationale.
- Customer insight it targets.
- Expected strengths.
- Expected weaknesses.
- Preliminary rubric score.

### Stage 3: First Adversarial Review

The Adversary reviews every candidate.

It identifies:

- Immediate disqualifiers.
- Likely brand-space problems.
- Competitive confusion.
- Linguistic weaknesses.
- Strategic weaknesses.
- Candidates that deserve deeper investigation.

The Referee then narrows the field to approximately **10–12 candidates**.

### Stage 4: Creator Response

The Creator receives the adversarial critique.

For each surviving candidate, it may:

- Defend the candidate with reasoning.
- Concede the criticism.
- Modify the candidate.
- Replace it.
- Withdraw it.

The Creator should not be rewarded for defending weak ideas.

### Stage 5: Persona Evaluation

Each of the three priority persona agents independently reviews the surviving candidates.

Each persona provides:

- Score.
- Emotional reaction.
- Trust reaction.
- Memorability assessment.
- Likelihood of engagement.
- Preferred candidates.
- Rejected candidates.
- Explanation grounded in the persona profile.

Persona agents should evaluate candidates independently before seeing the other personas' judgments where practical. This reduces groupthink.

### Stage 6: Referee Semifinal

The Referee integrates:

- Naming rubric.
- Persona responses.
- Strength of persona preference.
- Adversarial findings.
- Creator defenses.

The field is reduced to approximately **6–8 finalists**.

The Referee should explicitly document why each eliminated candidate failed.

### Stage 7: Final Challenge

The Adversary conducts a deeper challenge against the finalists.

The Creator receives one final opportunity to respond.

The three persona agents may revise their evaluations once after seeing material new evidence.

A persona should not change its score simply because another persona disagrees.

### Stage 8: Final Referee Decision

The Referee selects and ranks **five names**.

The Referee should not manufacture a false level of certainty. If two candidates are effectively tied or have substantially different strengths, the output should say so.

---

## 7. Final Output

Generate a Markdown report.

### Executive Shortlist

Begin with a table:

| Rank | Name | Overall Score | Persona 1 | Persona 2 | Persona 3 | Risk | Core Reason |
|---|---|---:|---:|---:|---:|---|---|

### Candidate Detail

For each of the five finalists include:

#### Name

**Strategic rationale**

Why the name works and what positioning it creates.

**Priority persona response**

Separate analysis for all three priority personas.

**Adversarial assessment**

The strongest objections, factual conflicts, and unresolved risks.

**Brand-space assessment**

Known conflicts or evidence suggesting usable brand space.

Do not represent this as legal trademark clearance unless actual legal clearance has been performed.

**Weakest joint**

Identify the single most credible reason not to choose the name.

**Referee judgment**

Explain why the candidate survived and why it occupies its final ranking.

### Rejected Candidates

Include a compact appendix showing meaningful rejected candidates and the primary reason each was eliminated.

This prevents the same weak ideas from being regenerated in later runs.

---

## 8. System Behavior Requirements

The system must:

1. Ground persona judgments in project evidence.
2. Keep the three priority personas separate.
3. Treat secondary personas as context, not primary voters.
4. Preserve disagreement.
5. Avoid simple majority voting.
6. Avoid optimizing for universal bland acceptability.
7. Distinguish factual objections from subjective objections.
8. Never invent brand conflicts, trademark findings, domain availability, or company names.
9. Clearly label unverified external risks.
10. Maintain an audit trail of candidate evolution and elimination.
11. Terminate after a defined number of rounds.
12. Produce exactly five finalists unless fewer than five candidates survive material risk review.

---

## 9. Configuration

The implementation should make the following configurable rather than hard-coded:

```yaml
priority_personas:
  - persona_1
  - persona_2
  - persona_3

initial_candidate_count: 20
first_cut_count: 12
semifinal_count: 8
final_count: 5
max_debate_rounds: 3

weights:
  persona_resonance: 30
  distinctiveness: 15
  memorability: 10
  emotional_fit: 10
  credibility: 10
  clarity: 10
  pronunciation_spelling: 5
  searchability: 5
  extensibility: 5
```

---

## 10. Implementation Principle

The multi-agent structure should represent genuinely different decision functions, not six prompts producing variations of the same generic branding advice.

The architecture should enforce:

**Creator:** What could work?

**Adversary:** Why might this fail?

**Persona 1:** Would I want this?

**Persona 2:** Would I want this?

**Persona 3:** Would I want this?

**Referee:** Given the evidence, disagreement, and risk, which five deserve to survive?

That separation of roles is the central product behavior.

---

## 11. Success Criteria

A successful run produces:

- Five genuinely differentiated naming candidates.
- Clear evidence connecting each finalist to customer psychographics.
- Visible disagreement among personas where disagreement exists.
- Evidence-based adversarial challenges.
- No invented claims about external brand conflicts.
- A defensible explanation for every finalist.
- A record of why major rejected candidates failed.
- A ranking that reflects the three priority personas rather than averaging all five customer types equally.
- Enough information for a human decision-maker to choose which names merit formal trademark, domain, linguistic, and market validation.

The output should make the naming decision **harder to fool and easier to defend**, rather than merely generating more names.
