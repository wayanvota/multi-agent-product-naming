"""Strict response contracts and deterministic naming arithmetic (standard library only)."""
import math
import unicodedata
import json

WEIGHTS = dict(persona_resonance=30, distinctiveness=15, memorability=10,
               emotional_fit=10, credibility=10, clarity=10,
               pronunciation_spelling=5, searchability=5, extensibility=5)
QUALITY = [k for k in WEIGHTS if k != 'persona_resonance']
CATEGORIES = ['company', 'trademark', 'domain', 'apps', 'search', 'language', 'strategic']
LEVELS = ['None', 'Low', 'Moderate', 'High', 'Disqualifying']

def obj(**props):
    return dict(type='object', properties=props, required=list(props), additionalProperties=False)

def arr(item):
    return dict(type='array', items=item)

def enum(*values):
    return dict(type='string', enum=list(values))

S = dict(type='string', minLength=1)
TEXT = dict(type='string')
SCORE = dict(type='number', minimum=0, maximum=10)
BOOL = dict(type='boolean')
STRINGS = arr(S)
REF = obj(source_id=S, quote=S)
REFS = dict(type='array', items=REF, minItems=1)
SCORES = obj(**{key: SCORE for key in QUALITY})
CANDIDATE = obj(id=S, name=S, parent_id=TEXT, pronunciation=S,
                strategy=enum('descriptive', 'suggestive', 'metaphorical', 'evocative',
                              'compound', 'invented', 'unexpected_familiar'),
                rationale=S, customer_insight=S, source_refs=REFS, strengths=STRINGS,
                weaknesses=STRINGS, preliminary_scores=obj(**{k: SCORE for k in WEIGHTS}))
FINDING = obj(id=S, category=enum(*CATEGORIES), issue_key=S,
              severity=enum(*LEVELS), basis=enum('factual', 'subjective', 'unverified'),
              claim=S, source_url=TEXT, excerpt=TEXT, checked_on=TEXT)
CHECK = obj(category=enum(*CATEGORIES), status=enum('checked', 'partial', 'unverified'),
            queries=STRINGS, urls=STRINGS, note=S)
REVIEW = obj(candidate_id=S, findings=arr(FINDING), checks=arr(CHECK),
             brand_space=S, recommendation=S)
PERSONA_REVIEW = obj(candidate_id=S, score=SCORE, emotional_reaction=S, trust_reaction=S,
                     memorability=S, engagement=S, recommendation=S,
                     choice=enum('preferred', 'acceptable', 'rejected'), source_refs=REFS,
                     material_evidence_ids=STRINGS)
JUDGMENT = obj(candidate_id=S, scores=SCORES, rationale=S, weakest_joint=S,
               upheld_finding_ids=STRINGS, dismissed_findings=arr(obj(finding_id=S, reason=S)),
               double_counting_note=S)
SCHEMAS = {
    'intake': obj(product_purpose=S, value_proposition=S, product_status=S,
                  priority_personas=arr(obj(id=S, motivations=S, anxieties=S,
                                            trust_triggers=S, source_refs=REFS)),
                  secondary_context=S, desired_characteristics=STRINGS,
                  competitive_context=S, constraints=STRINGS,
                  historical_names=arr(obj(name=S, status=S, source_refs=REFS)),
                  source_conflicts=STRINGS, product_refs=REFS),
    'creator': obj(candidates=arr(CANDIDATE), diversity_explanation=S),
    'adversary': obj(reviews=arr(REVIEW)),
    'cut': obj(advance=STRINGS, eliminate=arr(obj(candidate_id=S, reason=S)), rationale=S,
               disqualification_decisions=arr(obj(finding_id=S, uphold=BOOL, reason=S))),
    'response': obj(actions=arr(obj(candidate_id=S, action=enum('defend', 'concede', 'withdraw', 'replace'),
                                    reason=S, replacement=arr(CANDIDATE)))),
    'persona': obj(persona_id=S, reviews=arr(PERSONA_REVIEW), forced_choice=TEXT),
    'referee': obj(judgments=arr(JUDGMENT), disagreement=S),
    'challenge_gate': obj(request_more=BOOL, candidate_ids=STRINGS, questions=STRINGS, reason=S),
    'final': obj(details=arr(obj(candidate_id=S, strategic_rationale=S,
                                  weakest_joint=S, referee_judgment=S)),
                 decision=S, unresolved_questions=STRINGS),
    'smoke': obj(ok=BOOL, role=S),
}

class Invalid(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise Invalid(message)

def validate(value, schema, path='$'):
    """Validate the exact JSON Schema subset we emit, including finite numeric values."""
    kind = schema['type']
    valid = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'number': type(value) in (int, float),
             'boolean': type(value) is bool}[kind]
    require(valid, f'{path}: expected {kind}')
    if kind == 'object':
        require(set(value) == set(schema['properties']), f'{path}: missing or extra fields')
        for key, subschema in schema['properties'].items():
            validate(value[key], subschema, f'{path}.{key}')
    elif kind == 'array':
        require(len(value) >= schema.get('minItems', 0), f'{path}: at least {schema.get("minItems")} item(s) required')
        for i, item in enumerate(value):
            validate(item, schema['items'], f'{path}[{i}]')
    elif kind == 'number':
        require(math.isfinite(value), f'{path}: nonfinite number')
        require(schema.get('minimum', value) <= value <= schema.get('maximum', value), f'{path}: out of range')
    elif kind == 'string':
        require(len(value.strip()) >= schema.get('minLength', 0), f'{path}: empty string')
        if 'enum' in schema:
            require(value in schema['enum'], f'{path}: invalid enum {value}')

def normalized(name):
    return ''.join(c for c in unicodedata.normalize('NFKC', name).casefold() if c.isalnum())

def response_schema(name, source_ids, product_ids, persona_id=None):
    """Expose reference constraints to the model, not only to post-response validation."""
    # JSON round-trip intentionally breaks shared schema-node aliases between fields.
    schema = json.loads(json.dumps(SCHEMAS[name]))
    def bind(node):
        if isinstance(node, dict):
            props = node.get('properties', {})
            if 'source_id' in props and 'quote' in props:
                props['source_id'] = enum(*([persona_id] if persona_id else sorted(source_ids)))
            for value in node.values():
                bind(value)
        elif isinstance(node, list):
            for value in node:
                bind(value)
    bind(schema)
    if name == 'intake':
        schema['properties']['product_refs']['items']['properties']['source_id'] = enum(*sorted(product_ids))
    return schema

def exact_ids(rows, ids, key='candidate_id'):
    got = [r[key] for r in rows]
    require(len(got) == len(set(got)) and set(got) == set(ids), f'Expected exactly {list(ids)}; got {got}')

def score_candidate(judgment, personas, findings, config):
    scores = [p['score'] for p in personas]
    require(len(scores) == 3, 'Exactly three primary scores required')
    mean = sum(scores) / 3
    top_two = sum(sorted(scores)[-2:]) / 2
    emphasis = config['preference_emphasis']
    resonance = (1 - emphasis) * mean + emphasis * top_two
    positive = resonance * config['weights']['persona_resonance'] / 10
    positive += sum(judgment['scores'][k] * config['weights'][k] / 10 for k in QUALITY)
    by_id = {f['id']: f for f in findings}
    upheld = judgment['upheld_finding_ids']
    dismissed = [d['finding_id'] for d in judgment['dismissed_findings']]
    require(len(upheld + dismissed) == len(set(upheld + dismissed)), 'Finding adjudicated twice')
    require(set(upheld + dismissed) == set(by_id), 'Referee must adjudicate every finding')
    groups = {}
    disqualified = False
    worst = 'None'
    for fid in upheld:
        f = by_id[fid]
        # Subjective problems belong in positive quality/persona scores, never a second deduction.
        if f['basis'] == 'subjective':
            continue
        level = f['severity']
        if level == 'Disqualifying':
            require(f['basis'] == 'factual' and f['source_url'] and f['excerpt'],
                    'Disqualification requires an attributable factual finding')
            disqualified = True
        if LEVELS.index(level) > LEVELS.index(worst):
            worst = level
        penalty = config['risk_penalties'][level]
        if f['basis'] == 'unverified':
            penalty = min(penalty, config['unknown_penalty_cap'])
        groups[f['issue_key']] = max(groups.get(f['issue_key'], 0), penalty)
    penalty = min(config['total_risk_cap'], sum(groups.values()))
    return dict(candidate_id=judgment['candidate_id'], positive=round(positive, 2),
                penalty=penalty, overall=round(max(0, positive - penalty), 2),
                persona_scores=scores, mean=round(mean, 2), top_two=round(top_two, 2),
                spread=round(max(scores) - min(scores), 2),
                preferred_by=[i for i, p in enumerate(personas) if p['choice'] == 'preferred'],
                risk=worst, disqualified=disqualified)

def rank(scores):
    # Scores determine rank; no majority vote or unexplained referee override.
    return sorted([s for s in scores if not s['disqualified']],
                  key=lambda s: (-s['overall'], -s['top_two'], -s['mean'], s['candidate_id']))
