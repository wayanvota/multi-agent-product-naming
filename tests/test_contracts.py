"""Deterministic contract and source-boundary tests; no live model or network calls."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contracts import (Invalid, WEIGHTS, QUALITY, SCORE, SCHEMAS, exact_ids,
                       normalized, rank, score_candidate, validate)
from naming import Runner, collect_sources, digest, load_config, refs_valid, same_sources


def config(root='.'):
    return dict(source_root=str(root), weights=dict(WEIGHTS),
                priority_personas=['p1', 'p2', 'p3'], secondary_personas=['p4', 'p5'],
                personas={f'p{i}': dict(path=f'p{i}.md', label=f'Persona {i}') for i in range(1, 6)},
                product_sources=[dict(id='product', path='product.md', kind='product')],
                history_sources=[], initial_candidate_count=20, first_cut_count=12,
                semifinal_count=8, final_count=5, max_debate_rounds=3,
                agent_timeout_seconds=60, max_attempts=2, preference_emphasis=.25,
                tie_margin=2, minimum_strategy_count=4,
                risk_penalties=dict(None_=0), unknown_penalty_cap=4,
                total_risk_cap=40, excluded_names=['LegacyPlaceholder'])


def scoring_config():
    cfg = config()
    cfg['risk_penalties'] = {'None': 0, 'Low': 3, 'Moderate': 8, 'High': 20, 'Disqualifying': 40}
    return cfg


def judgment(score=10):
    return dict(candidate_id='n1', scores={k: score for k in QUALITY},
                upheld_finding_ids=[], dismissed_findings=[])


def personas(scores=(10, 10, 10)):
    return [dict(score=s, choice='preferred' if s >= 8 else 'acceptable') for s in scores]


def finding(fid='f1', severity='High', basis='factual', issue='collision'):
    return dict(id=fid, severity=severity, basis=basis, issue_key=issue,
                source_url='https://example.org/evidence', excerpt='An existing product')


class ScoreTests(unittest.TestCase):
    def score(self, scores=(10, 10, 10), findings=None, judge=None, cfg=None):
        return score_candidate(judge or judgment(), personas(scores), findings or [], cfg or scoring_config())

    def test_positive_total_is_exactly_100(self):
        result = self.score()
        self.assertEqual(result['positive'], 100)
        self.assertEqual(result['overall'], 100)

    def test_strong_two_person_preference_is_explicit_and_bounded(self):
        polarized = self.score((10, 10, 2))
        consensus = self.score((7, 7, 7))
        self.assertEqual(polarized['persona_scores'], [10, 10, 2])
        self.assertEqual(polarized['mean'], 7.33)
        self.assertEqual(polarized['top_two'], 10)
        self.assertEqual(polarized['spread'], 8)
        self.assertEqual(polarized['positive'], 94)
        self.assertGreater(polarized['overall'], consensus['overall'])

    def test_emphasis_zero_uses_all_three_equally(self):
        cfg = scoring_config()
        cfg['preference_emphasis'] = 0
        self.assertEqual(self.score((10, 10, 2), cfg=cfg)['positive'], 92)

    def test_only_three_priority_scores_accepted(self):
        for count in (0, 2, 4, 5):
            with self.subTest(count=count), self.assertRaises(Invalid):
                score_candidate(judgment(), personas([10] * count), [], scoring_config())

    def test_related_findings_use_largest_single_penalty(self):
        fs = [finding(), finding('f2', 'Moderate')]
        j = judgment()
        j['upheld_finding_ids'] = ['f1', 'f2']
        self.assertEqual(self.score(findings=fs, judge=j)['penalty'], 20)

    def test_unrelated_risks_accumulate_only_to_cap(self):
        fs = [finding(f'f{i}', issue=f'issue{i}') for i in range(4)]
        j = judgment()
        j['upheld_finding_ids'] = [f['id'] for f in fs]
        self.assertEqual(self.score(findings=fs, judge=j)['penalty'], 40)

    def test_subjective_objection_has_no_second_deduction(self):
        j = judgment()
        j['upheld_finding_ids'] = ['f1']
        result = self.score(findings=[finding(basis='subjective')], judge=j)
        self.assertEqual(result['penalty'], 0)
        self.assertFalse(result['disqualified'])

    def test_unverified_high_risk_is_capped_but_visible(self):
        j = judgment()
        j['upheld_finding_ids'] = ['f1']
        result = self.score(findings=[finding(basis='unverified')], judge=j)
        self.assertEqual(result['penalty'], 4)
        self.assertEqual(result['risk'], 'High')

    def test_unverified_disqualifier_is_rejected(self):
        j = judgment()
        j['upheld_finding_ids'] = ['f1']
        with self.assertRaises(Invalid):
            self.score(findings=[finding(severity='Disqualifying', basis='unverified')], judge=j)

    def test_disqualification_cannot_be_offset_by_perfect_score(self):
        j = judgment()
        j['upheld_finding_ids'] = ['f1']
        dq = self.score(findings=[finding(severity='Disqualifying')], judge=j)
        self.assertTrue(dq['disqualified'])
        self.assertEqual(rank([dq]), [])

    def test_every_finding_must_be_adjudicated_once(self):
        for j in (judgment(), dict(judgment(), upheld_finding_ids=['f1', 'f1']),
                  dict(judgment(), upheld_finding_ids=['f1'], dismissed_findings=[dict(finding_id='f1', reason='x')])):
            with self.subTest(j=j), self.assertRaises(Invalid):
                self.score(findings=[finding()], judge=j)

    def test_dismissed_risk_does_not_lower_score(self):
        j = judgment()
        j['dismissed_findings'] = [dict(finding_id='f1', reason='Different market')]
        self.assertEqual(self.score(findings=[finding()], judge=j)['overall'], 100)

    def test_ranking_is_stable_without_persona_majority_override(self):
        a, b = self.score(), self.score()
        a['candidate_id'], b['candidate_id'] = 'a', 'b'
        self.assertEqual([s['candidate_id'] for s in rank([b, a])], ['a', 'b'])


class ValidationTests(unittest.TestCase):
    def test_invalid_numeric_model_scores(self):
        for value in (-1, 10.01, True, '8', float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value), self.assertRaises(Invalid):
                validate(value, SCORE)

    def test_schema_rejects_missing_and_extra_fields(self):
        for value in (dict(ok=True), dict(ok=True, role='smoke', invented='x')):
            with self.subTest(value=value), self.assertRaises(Invalid):
                validate(value, SCHEMAS['smoke'])

    def test_ids_require_exact_coverage_and_no_duplicates(self):
        for rows in ([dict(candidate_id='a')], [dict(candidate_id='a'), dict(candidate_id='a')]):
            with self.subTest(rows=rows), self.assertRaises(Invalid):
                exact_ids(rows, ['a', 'b'])

    def test_unicode_space_case_do_not_allow_duplicate_name(self):
        self.assertEqual(normalized('ＳＡＭＰＬＥ Name'), normalized('samplename'))

    def test_config_persona_and_weight_guards(self):
        mutations = [lambda c: c['weights'].update(clarity=9),
                     lambda c: c.update(priority_personas=['p1', 'p1', 'p3']),
                     lambda c: c.update(secondary_personas=['p3', 'p5']),
                     lambda c: c['personas']['p2'].update(path='p1.md'),
                     lambda c: c.update(max_debate_rounds=99),
                     lambda c: c.update(initial_candidate_count=4)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.json'
            for mutate in mutations:
                cfg = scoring_config()
                mutate(cfg)
                path.write_text(json.dumps(cfg))
                with self.subTest(cfg=cfg), self.assertRaises(Invalid):
                    load_config(path)


class SourceBoundaryTests(unittest.TestCase):
    def test_reference_requires_exact_quote_and_allowed_persona(self):
        sources = {'p1': dict(text='Workshop responsibility'), 'p2': dict(text='Workshop responsibility')}
        refs_valid([dict(source_id='p1', quote='responsibility')], sources, {'p1'})
        for ref in (dict(source_id='p2', quote='responsibility'),
                    dict(source_id='p1', quote='invented quote'),
                    dict(source_id='missing', quote='responsibility')):
            with self.subTest(ref=ref), self.assertRaises(Invalid):
                refs_valid([ref], sources, {'p1'})

    def test_source_snapshot_detects_midrun_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'profile.md'
            path.write_text('original')
            sources = dict(p1=dict(absolute_path=str(path), sha256=digest('original')))
            same_sources(sources)
            path.write_text('changed')
            with self.assertRaises(Invalid):
                same_sources(sources)

    def test_source_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'project'
            root.mkdir()
            cfg = scoring_config()
            cfg['source_root'] = str(root)
            cfg['personas']['p1']['path'] = '../outside.md'
            (Path(tmp) / 'outside.md').write_text('outside')
            with self.assertRaises(Invalid):
                collect_sources(cfg)

    def test_persona_payload_hides_other_profiles_and_creator_scores(self):
        runner = Runner.__new__(Runner)
        runner.sources = {'p1': dict(text='A coordinator has workshop responsibility')}
        runner.brief = dict(product_purpose='Records', value_proposition='Evidence',
                            product_status='Prototype', constraints=[],
                            priority_personas=['secret_other_profile'], historical_names=['secret_incumbent'])
        runner.candidates = {'n1': dict(name='Name', pronunciation='name', preliminary_scores={'clarity': 10}, rationale='Creator sales pitch')}
        runner.votes = {}
        captured = {}
        def ask(stage, role, payload, check):
            captured.update(payload)
            return payload
        runner.ask = ask
        runner.persona('persona', 'p1', ['n1'])
        self.assertEqual(set(captured['product']), {'product_purpose', 'value_proposition', 'product_status', 'constraints'})
        self.assertEqual(captured['candidates'], [dict(id='n1', name='Name', pronunciation='name')])
        self.assertEqual(captured['prior_reviews'], [])
        self.assertNotIn('secret_other_profile', json.dumps(captured))
        self.assertNotIn('Creator sales pitch', json.dumps(captured))


if __name__ == '__main__':
    unittest.main()
