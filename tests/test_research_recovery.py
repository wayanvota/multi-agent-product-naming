"""Lookup and archived-response regressions using synthetic evidence only."""
import contextlib
import io
import json
from pathlib import Path
import unittest

from contracts import Invalid
from naming import Runner, validate_research_trace, normalize_research_coverage
import test_pipeline
from test_pipeline import SyntheticBackend


class ResearchRecoveryTests(unittest.TestCase):
    setUp = test_pipeline.PipelineTests.setUp
    def backend(self, fail_screen=False, record_trace=True):
        synthetic = SyntheticBackend(self.cfg)
        def call(role, payload, schema, prompt, directory, attempt):
            value = synthetic(role, payload, schema, prompt, directory, attempt)
            if role == 'adversary':
                for review in value['reviews']:
                    check = next(c for c in review['checks'] if c['category'] == 'domain')
                    check.update(status='partial', queries=[], urls=['https://example.invalid/'],
                                 note='Direct URL request failed; registration remains unknown.')
            (directory / f'answer-{attempt}.json').write_text(json.dumps(value))
            if record_trace:
                (directory / f'events-{attempt}.jsonl').write_text(json.dumps(
                    dict(type='item.completed', item=dict(type='web_search', query='https://example.invalid/', action=dict(type='other')))))
            if fail_screen and directory.name == '03-screen':
                raise Invalid('Simulated obsolete validator rejected URL-only coverage')
            return value
        return call, synthetic

    def test_partial_direct_lookup_is_accepted_without_invented_query(self):
        backend, _ = self.backend()
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = runner.run()
        check = next(c for c in ledger['reviews']['fixture_01'][0]['checks'] if c['category']=='domain')
        self.assertEqual(check['queries'], [])
        self.assertEqual(check['status'], 'partial')
        self.assertIn('unknown', check['note'])

    def test_resume_revalidates_archived_response_without_repeat_research(self):
        backend, _ = self.backend(fail_screen=True)
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(Invalid):
            runner.run()
        backend, synthetic = self.backend()
        resumed = Runner(self.cfg, self.run_dir, backend=backend, resume=True)
        with contextlib.redirect_stdout(io.StringIO()):
            resumed.run()
        self.assertNotIn('03-screen', [c['stage'] for c in synthetic.calls])
        accepted = json.loads((self.run_dir/'03-screen/accepted.json').read_text())
        self.assertEqual(accepted['recovered_from'], 'answer-2.json')
        self.assertTrue((self.run_dir/'03-screen/failure-1.json').exists())

    def test_saved_external_response_without_trace_is_not_reused(self):
        backend, _ = self.backend(fail_screen=True, record_trace=False)
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(Invalid):
            runner.run()
        backend, synthetic = self.backend()
        resumed = Runner(self.cfg, self.run_dir, backend=backend, resume=True)
        with contextlib.redirect_stdout(io.StringIO()):
            resumed.run()
        self.assertIn('03-screen', [c['stage'] for c in synthetic.calls])

    def test_url_in_prose_is_not_a_tool_trace(self):
        value = dict(reviews=[dict(findings=[],checks=[dict(category='domain',status='partial')])])
        with self.assertRaisesRegex(Invalid, 'recorded web-search'):
            validate_research_trace(value,[dict(type='item.completed',item=dict(type='agent_message',text='web_search https://example.invalid'))])

    def test_checked_search_without_source_urls_is_downgraded_with_audit(self):
        original = dict(reviews=[dict(candidate_id='example', findings=[],checks=[
            dict(category='search',status='checked',queries=['fictional name'],urls=[],note='No confirmed primary source.')])])
        normalized, adjustments = normalize_research_coverage(original)
        self.assertEqual(original['reviews'][0]['checks'][0]['status'], 'checked')
        self.assertEqual(normalized['reviews'][0]['checks'][0]['status'], 'partial')
        self.assertEqual(normalized['reviews'][0]['checks'][0]['urls'], [])
        self.assertEqual(len(adjustments), 1)
        self.assertIn('no supporting source URL', adjustments[0]['reason'])

    def test_no_query_and_no_url_is_not_rescued(self):
        original = dict(reviews=[dict(candidate_id='example',findings=[],checks=[
            dict(category='search',status='checked',queries=[],urls=[],note='Unsupported claim.')])])
        _, adjustments = normalize_research_coverage(original)
        self.assertEqual(adjustments, [])
