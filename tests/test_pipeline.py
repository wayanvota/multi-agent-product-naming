"""Synthetic end-to-end fixtures. These names and findings are not naming research."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contracts import CATEGORIES, QUALITY, WEIGHTS, Invalid
from naming import Runner

HERE = Path(__file__).resolve().parents[1]
STRATEGIES = ['descriptive', 'suggestive', 'metaphorical', 'evocative', 'compound', 'invented', 'unexpected_familiar']


class SyntheticBackend:
    def __init__(self, cfg, mode='normal'):
        self.cfg, self.mode, self.calls = cfg, mode, []

    @staticmethod
    def quote(sid):
        return [dict(source_id=sid, quote=f'Test fixture evidence for {sid}.')]

    def candidate(self, index, parent=''):
        cid = 'fixture_replacement' if parent else f'fixture_{index:02d}'
        return dict(id=cid, name=f'TEST ONLY Synthetic Name {index}' + (' Replacement' if parent else ''),
                    parent_id=parent, pronunciation=f'test fixture {index}', strategy=STRATEGIES[index % len(STRATEGIES)],
                    rationale='Synthetic rationale for exercising the protocol.', customer_insight='Test evidence insight.',
                    source_refs=self.quote(self.cfg['product_sources'][0]['id']), strengths=['Fixture strength'],
                    weaknesses=['Fixture weakness'], preliminary_scores={k: 8 for k in WEIGHTS})

    def __call__(self, role, payload, schema, prompt, directory, attempt):
        stage = directory.name
        self.calls.append(dict(stage=stage, role=role, payload=copy.deepcopy(payload), attempt=attempt))
        if role == 'intake':
            return dict(product_purpose='Synthetic scheduling product', value_proposition='Synthetic evidence retrieval',
                        product_status='Test only', priority_personas=[dict(id=p, motivations='Test motivation', anxieties='Test concern',
                        trust_triggers='Test source', source_refs=self.quote(p)) for p in self.cfg['priority_personas']],
                        secondary_context='Two context-only test profiles', desired_characteristics=['Test clarity'],
                        competitive_context='No actual research', constraints=['Do not publish test fixtures'],
                        historical_names=[dict(name='TEST ONLY Old Name', status='Test rejection',
                        source_refs=self.quote(self.cfg['history_sources'][0]['id']))], source_conflicts=[],
                        product_refs=self.quote(self.cfg['product_sources'][0]['id']))
        if role == 'creator':
            return dict(candidates=[self.candidate(i) for i in range(payload['count'])], diversity_explanation='Synthetic strategy coverage')
        if role == 'adversary':
            reviews = []
            for c in payload['candidates']:
                cid = c['id']
                findings = []
                dq = self.mode == 'few' and stage == '03-screen' and int(cid.rsplit('_', 1)[1]) >= 4
                if stage.startswith('08-challenge') or dq:
                    findings = [dict(id=f'{stage}-{cid}', category='company', issue_key=f'{cid}-test-issue',
                        severity='Disqualifying' if dq else 'Low', basis='factual',
                        claim='SYNTHETIC TEST EVIDENCE. Not a real company or conflict.',
                        source_url=f'https://example.invalid/{cid}', excerpt='SYNTHETIC TEST QUOTE', checked_on=payload['date'])]
                checks = [dict(category=cat, status='unverified', queries=[], urls=[], note='Synthetic backend does not research.') for cat in CATEGORIES]
                if self.mode == 'unsupported_checks':
                    checks[0]['status'] = 'checked'
                reviews.append(dict(candidate_id=cid, findings=findings, checks=checks,
                                    brand_space='Unverified test-only brand space.', recommendation='Continue test protocol.'))
            return dict(reviews=reviews)
        if role == 'cut':
            ids = [c['id'] for c in payload['candidates']]
            eligible = [cid for cid in ids if not any(f['severity'] == 'Disqualifying'
                        for r in payload['reviews'].get(cid, []) for f in r['findings'])]
            advance = eligible[:payload['advance_count']]
            return dict(advance=advance, eliminate=[dict(candidate_id=i, reason='Synthetic elimination reason') for i in ids if i not in advance],
                        rationale='Synthetic first cut', disqualification_decisions=[
                            dict(finding_id=f['id'], uphold=True, reason='Synthetic referee finding')
                            for cid in ids for r in payload['reviews'].get(cid, []) for f in r['findings']
                            if f['severity'] == 'Disqualifying'])
        if role == 'response':
            actions = []
            for c in payload['candidates']:
                replace = stage == '05-creator-response' and c['id'] == 'fixture_00' and self.mode != 'few'
                actions.append(dict(candidate_id=c['id'], action='replace' if replace else 'concede',
                                    reason='Synthetic response', replacement=[self.candidate(0, c['id'])] if replace else []))
            return dict(actions=actions)
        if role == 'persona':
            reviews = []
            prior = {r['candidate_id']: r for r in payload['prior_reviews']}
            for c in payload['candidates']:
                cid = c['id']
                own_material = [f['id'] for f in payload['material_evidence'] if f['candidate_id'] == cid]
                if prior:
                    review = copy.deepcopy(prior[cid])
                    review['score'] -= .1
                    review['material_evidence_ids'] = own_material[:1]
                    if self.mode == 'wrong_revision':
                        review['material_evidence_ids'] = [next(f['id'] for f in payload['material_evidence'] if f['candidate_id'] != cid)]
                else:
                    index = 0 if cid == 'fixture_replacement' else int(cid.rsplit('_', 1)[1])
                    score = 9 - self.cfg['priority_personas'].index(payload['persona_id']) - index / 100
                    review = dict(candidate_id=cid, score=score, emotional_reaction='Synthetic emotional response',
                        trust_reaction='Synthetic trust response', memorability='Untested simulated recall',
                        engagement='Synthetic curiosity', recommendation='Synthetic preference explanation', choice='preferred',
                        source_refs=self.quote(payload['persona_id']), material_evidence_ids=[])
                reviews.append(review)
            return dict(persona_id=payload['persona_id'], reviews=reviews, forced_choice=payload['candidates'][0]['id'])
        if role == 'referee':
            judgments = []
            for c in payload['candidates']:
                cid = c['id']
                judgments.append(dict(candidate_id=cid, scores={k: 8 for k in QUALITY}, rationale='Synthetic rubric judgment',
                    weakest_joint='Synthetic limitation', upheld_finding_ids=[f['id'] for r in payload['reviews'][cid] for f in r['findings']],
                    dismissed_findings=[], double_counting_note='Same test issue grouped across rounds.'))
            return dict(judgments=judgments, disagreement='Synthetic individual score disagreement remains visible.')
        if role == 'challenge_gate':
            return dict(request_more=True, candidate_ids=[c['id'] for c in payload['candidates']],
                        questions=['Resolve synthetic evidence question.'], reason='Exercise exactly one additional research round.')
        if role == 'final':
            return dict(details=[dict(candidate_id=s['candidate_id'], strategic_rationale='Synthetic finalist rationale',
                        weakest_joint='No human customer research', referee_judgment='Synthetic ranking follows computed scores') for s in payload['ranking']],
                        decision='TEST ONLY. Not a naming recommendation.', unresolved_questions=['Actual research has not been performed.'])
        raise AssertionError(f'Unexpected role {role}')


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cfg = json.loads((HERE / 'config.example.json').read_text())
        self.cfg['source_root'] = str(self.root / 'sources')
        entries = [dict(id=k, path=v['path']) for k, v in self.cfg['personas'].items()]
        entries += self.cfg['product_sources'] + self.cfg['history_sources']
        for entry in entries:
            path = Path(self.cfg['source_root']) / entry['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Test fixture evidence for {entry['id']}.")
        self.run_dir = self.root / 'run'

    def execute(self, mode='normal'):
        backend = SyntheticBackend(self.cfg, mode)
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = runner.run()
        return backend, runner, ledger

    def test_complete_pipeline_replacement_bounded_rounds_and_report(self):
        backend, runner, ledger = self.execute()
        by_stage = {c['stage']: c for c in backend.calls}
        self.assertEqual(len(by_stage['03-screen']['payload']['candidates']), 20)
        self.assertEqual(len(by_stage['07-semifinal']['payload']['candidates']), 12)
        self.assertEqual(len(by_stage['08-challenge-2']['payload']['candidates']), 8)
        self.assertEqual(len(ledger['ranking']), 5)
        self.assertEqual(len(ledger['candidates']), 21)
        self.assertIn('05b-replacement-screen', by_stage)
        self.assertIn('05c-replacement-gate', by_stage)
        self.assertEqual(by_stage['05b-replacement-screen']['payload']['candidates'][0]['parent_id'], 'fixture_00')
        self.assertEqual(len([c for c in backend.calls if c['stage'].startswith('08-challenge')]), 2)
        self.assertEqual(len([c for c in backend.calls if c['role'] == 'challenge_gate']), 1)
        self.assertEqual(len([c for c in backend.calls if c['stage'].startswith('11-revision')]), 3)
        self.assertNotIn('fixture_00', [s['candidate_id'] for s in ledger['ranking']])
        self.assertEqual(set(ledger['personas']), set(self.cfg['priority_personas']))
        for p in self.cfg['priority_personas']:
            initial = by_stage[f'06-persona-{p}']['payload']
            self.assertEqual(initial['prior_reviews'], [])
            self.assertEqual(initial['material_evidence'], [])
            self.assertNotIn('priority_personas', initial['product'])
        self.assertTrue((self.run_dir / 'candidate-ledger.json').is_file())
        self.assertEqual(json.loads((self.run_dir / 'status.json').read_text())['status'], 'complete')
        report = (self.run_dir / 'shortlist.md').read_text()
        self.assertTrue(report.startswith('| Rank | Name | Overall Score |'))
        for heading in ('Strategic rationale', 'Priority persona response', 'Adversarial assessment', 'Brand-space assessment', 'Weakest joint', 'Referee judgment', 'Rejected candidates'):
            self.assertIn(heading, report)
        self.assertIn('checks incomplete', report)
        self.assertIn('AI simulations', report)
        self.assertFalse((self.run_dir / 'run.lock').exists())

    def test_same_day_resume_reuses_all_accepted_stages(self):
        _, _, original = self.execute()
        def forbidden(*args, **kwargs):
            raise AssertionError('Resume called backend despite unchanged accepted stages')
        resumed = Runner(self.cfg, self.run_dir, backend=forbidden, resume=True)
        with contextlib.redirect_stdout(io.StringIO()):
            actual = resumed.run()
        self.assertEqual(original, actual)

    def test_external_checked_without_evidence_stops_after_bounded_attempts(self):
        backend = SyntheticBackend(self.cfg, 'unsupported_checks')
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(Invalid, 'external research needs'):
            runner.run()
        self.assertEqual(len([c for c in backend.calls if c['stage'] == '03-screen']), self.cfg['max_attempts'])
        self.assertEqual(json.loads((self.run_dir / 'status.json').read_text())['status'], 'incomplete')
        self.assertFalse((self.run_dir / 'shortlist.md').exists())
        self.assertFalse((self.run_dir / 'run.lock').exists())

    def test_cross_candidate_revision_evidence_is_rejected(self):
        backend = SyntheticBackend(self.cfg, 'wrong_revision')
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(Invalid, 'unrelated or nonmaterial'):
            runner.run()
        self.assertFalse((self.run_dir / 'shortlist.md').exists())
        self.assertEqual(json.loads((self.run_dir / 'status.json').read_text())['status'], 'incomplete')

    def test_material_disqualification_can_leave_exactly_four_survivors(self):
        backend, runner, ledger = self.execute('few')
        self.assertEqual(len(ledger['ranking']), 4)
        self.assertEqual(len(ledger['rejected']), 16)
        self.assertIn('Only 4 of the requested 5', (self.run_dir / 'shortlist.md').read_text())
        self.assertEqual(set(s['candidate_id'] for s in ledger['ranking']), {f'fixture_{i:02d}' for i in range(4)})

    def test_next_day_resume_requires_fresh_run(self):
        self.execute()
        path = self.run_dir / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['created_at'] = '2000-01-01T00:00:00+00:00'
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(Invalid, 'another UTC day'):
            Runner(self.cfg, self.run_dir, backend=SyntheticBackend(self.cfg), resume=True)

    def test_later_run_blocks_previous_rejected_names(self):
        self.execute()
        backend = SyntheticBackend(self.cfg)
        runner = Runner(self.cfg, self.root / 'next-run', backend=backend)
        self.assertTrue(runner.previous_rejections)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(Invalid, 'excluded name'):
            runner.run()
        self.assertFalse((self.root / 'next-run' / 'shortlist.md').exists())

    def test_adversary_cannot_unilaterally_disqualify(self):
        runner = Runner(self.cfg, self.run_dir, backend=SyntheticBackend(self.cfg))
        runner.reviews = {'one': [dict(findings=[dict(id='finding-one', severity='Disqualifying')])]}
        answer = dict(advance=['one'], eliminate=[], rationale='Referee rejected the interpretation.',
                      disqualification_decisions=[dict(finding_id='finding-one', uphold=False,
                                                       reason='Related source does not establish category conflict.')])
        runner.check_cut(answer, ['one'], 1)
        answer['disqualification_decisions'][0]['uphold'] = True
        with self.assertRaisesRegex(Invalid, 'upheld a disqualifier'):
            runner.check_cut(answer, ['one'], 1)


if __name__ == '__main__':
    unittest.main()
