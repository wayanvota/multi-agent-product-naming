"""Synthetic regression for withdrawal policy, retries, and checkpoint reuse."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from naming import Runner
from contracts import Invalid
import test_pipeline
from test_pipeline import SyntheticBackend

class WithdrawalTests(unittest.TestCase):
    setUp = test_pipeline.PipelineTests.setUp

    def runner(self, backend):
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        runner.brief = {}
        runner.candidates = {k: dict(id=k, name=k) for k in ['moderate', 'high', 'subjective', 'unverified']}
        runner.reviews = {k: [dict(findings=[dict(basis=b, severity=s)])] for k,b,s in [
            ('moderate','factual','Moderate'), ('high','factual','High'),
            ('subjective','subjective','High'), ('unverified','unverified','Disqualifying')]}
        return runner

    def test_eligibility_and_specific_retry_error(self):
        prompts=[]
        def backend(role,payload,schema,prompt,path,attempt):
            self.assertEqual(payload['withdrawal_policy']['eligible_candidate_ids'], ['high'])
            self.assertIn('Moderate factual conflicts',payload['withdrawal_policy']['rule'])
            prompts.append(prompt)
            return dict(actions=[dict(candidate_id=c['id'], action='withdraw' if c['id'] in (['moderate','high'] if attempt==1 else ['high']) else 'concede', reason='Fixture', replacement=[]) for c in payload['candidates']])
        runner=self.runner(backend)
        with contextlib.redirect_stdout(io.StringIO()):
            remaining,_,_=runner.response('09-response-2',list(runner.candidates),False)
        self.assertEqual(set(remaining), {'moderate','subjective','unverified'})
        self.assertEqual(len(prompts),2)
        self.assertIn('Cannot withdraw moderate (moderate)',prompts[1])
        self.assertIn("Only these candidate IDs may withdraw: ['high']",prompts[1])

    def test_forbidden_withdrawals_still_fail(self):
        for cid in ['moderate','subjective','unverified']:
            def backend(role,payload,*args):
                return dict(actions=[dict(candidate_id=c['id'],action='withdraw' if c['id']==cid else 'concede',reason='Fixture',replacement=[]) for c in payload['candidates']])
            if cid=='moderate': runner=self.runner(backend)
            else: runner.backend=backend
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(Invalid,'Cannot withdraw '+cid):
                runner.response('test-'+cid,list(runner.candidates),False)

    def test_failed_stage_resumes_without_repeating_prior_stages(self):
        original=SyntheticBackend(self.cfg)
        def failing(role,payload,schema,prompt,path,attempt):
            if path.name=='09-response-2': raise Invalid('synthetic interruption')
            return original(role,payload,schema,prompt,path,attempt)
        runner=Runner(self.cfg,self.run_dir,backend=failing)
        with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(Invalid): runner.run()
        old={str(p):p.read_bytes() for p in self.run_dir.glob('*/accepted.json')}
        backend=SyntheticBackend(self.cfg)
        resumed=Runner(self.cfg,self.run_dir,backend=backend,resume=True)
        with contextlib.redirect_stdout(io.StringIO()): resumed.run()
        self.assertEqual(backend.calls[0]['stage'],'09-response-2')
        self.assertTrue(all(Path(p).read_bytes()==data for p,data in old.items()))
