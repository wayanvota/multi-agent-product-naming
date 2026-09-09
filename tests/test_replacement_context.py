"""Replacement agents must see reserved identities and survival constraints."""
import contextlib
import io
import unittest
from contracts import Invalid
from naming import Runner
import test_pipeline
from test_pipeline import SyntheticBackend

class ReplacementContextTests(unittest.TestCase):
    setUp=test_pipeline.PipelineTests.setUp

    def exercise(self, failure):
        synthetic=SyntheticBackend(self.cfg);prompts=[]
        def backend(role,payload,schema,prompt,path,attempt):
            value=synthetic(role,payload,schema,prompt,path,attempt)
            if path.name=='05-creator-response':
                policy=payload['replacement_policy']
                reserved={c['id'] for c in policy['reserved_candidates']}
                visible={c['id'] for c in payload['candidates']}
                self.assertEqual(len(reserved),20)
                self.assertNotIn('fixture_19',visible)
                self.assertIn('fixture_19',reserved)
                self.assertEqual(policy['minimum_remaining_candidates'],5)
                self.assertEqual(policy['maximum_withdrawals'],7)
                self.assertTrue(set(self.cfg['excluded_names'])<=set(policy['excluded_names']))
                self.assertTrue(payload['sources'])
                prompts.append(prompt)
                if attempt==1:
                    if failure=='id':value['actions'][0]['replacement'][0]['id']='fixture_19'
                    else:
                        for a in value['actions']:a.update(action='withdraw',replacement=[])
            return value
        with contextlib.redirect_stdout(io.StringIO()):
            ledger=Runner(self.cfg,self.run_dir,backend=backend).run()
        self.assertEqual(len(ledger['ranking']),5)
        self.assertEqual(len(prompts),2)
        return prompts[1]

    def test_reserved_eliminated_ids_are_visible_and_collision_error_is_specific(self):
        prompt=self.exercise('id')
        self.assertIn("Duplicate candidate ID 'fixture_19'",prompt)

    def test_survival_count_is_visible_and_retry_has_exact_shortfall(self):
        prompt=self.exercise('withdraw')
        self.assertIn('withdrawals leave 0 candidates; at least 5 must remain',prompt)

    def test_new_id_does_not_allow_reuse_of_an_eliminated_name(self):
        synthetic=SyntheticBackend(self.cfg)
        runner=Runner(self.cfg,self.run_dir,backend=synthetic)
        old=synthetic.candidate(19);runner.candidates={old['id']:old}
        new=synthetic.candidate(20);new['name']=old['name']
        with self.assertRaisesRegex(Invalid,'Reused candidate name'):
            runner.check_candidates([new])
