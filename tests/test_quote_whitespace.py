"""Synthetic quotation regressions: tolerate layout, never changed wording."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from naming import Runner, refs_valid
from contracts import Invalid
import test_pipeline
from test_pipeline import SyntheticBackend

class QuoteWhitespaceTests(unittest.TestCase):
    def test_layout_differences_preserve_raw_quote(self):
        sources={'p':dict(text='They\nkeep\tcomplete records. Next paragraph.')}
        refs=[dict(source_id='p',quote='They keep complete records.')]
        refs_valid(refs,sources,{'p'})
        self.assertEqual(refs[0]['quote'],'They keep complete records.')
        refs_valid([dict(source_id='p',quote='They\r\nkeep  complete\u00a0records.')],sources)

    def test_altered_words_punctuation_case_and_empty_quotes_fail(self):
        sources={'p':dict(text='They\nkeep complete records.')}
        for quote in ['They keep incomplete records.','They keep complete records!','they keep complete records.', 'Theykeep complete records.', 'complete keep records.', ' \n\t']:
            with self.subTest(quote=quote),self.assertRaisesRegex(Invalid,'Quote wording not found'):
                refs_valid([dict(source_id='p',quote=quote)],sources)

    def test_wrong_source_still_fails(self):
        with self.assertRaises(Invalid):
            refs_valid([dict(source_id='p',quote='Exact words.')],{'p':dict(text='Exact words.')},{'other'})

class QuoteRecoveryTests(unittest.TestCase):
    setUp=test_pipeline.PipelineTests.setUp
    def test_saved_creator_output_revalidated_without_new_generation(self):
        synthetic=SyntheticBackend(self.cfg)
        def backend(role,payload,schema,prompt,path,attempt):
            value=synthetic(role,payload,schema,prompt,path,attempt)
            if role=='creator':
                ref=value['candidates'][0]['source_refs'][0]
                ref['quote']=ref['quote'].replace('fixture evidence','fixture\nevidence')
                (path/f'answer-{attempt}.json').write_text(json.dumps(value))
                raise Invalid('Synthetic old strict-whitespace failure')
            return value
        with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(Invalid):
            Runner(self.cfg,self.run_dir,backend=backend).run()
        intake=(self.run_dir/'01-intake/accepted.json').read_bytes()
        resumed_backend=SyntheticBackend(self.cfg)
        with contextlib.redirect_stdout(io.StringIO()):
            Runner(self.cfg,self.run_dir,backend=resumed_backend,resume=True).run()
        self.assertNotIn('creator',[c['role'] for c in resumed_backend.calls])
        accepted=json.loads((self.run_dir/'02-create/accepted.json').read_text())
        self.assertEqual(accepted['recovered_from'],'answer-2.json')
        self.assertEqual(intake,(self.run_dir/'01-intake/accepted.json').read_bytes())
        self.assertTrue((self.run_dir/'02-create/failure-2.json').exists())
