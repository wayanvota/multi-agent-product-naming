"""Explicit 10 user-behavior and 10 adversarial end-to-end categories."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from contracts import Invalid
from naming import Runner, collect_sources, digest, load_config

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_pipeline import SyntheticBackend

HERE = Path(__file__).resolve().parents[1]


class EndToEndContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cfg = json.loads((HERE / "config.example.json").read_text())
        self.cfg["source_root"] = str(self.root / "sources")
        entries = [dict(id=key, path=value["path"]) for key, value in self.cfg["personas"].items()]
        entries += self.cfg["product_sources"] + self.cfg["history_sources"]
        for entry in entries:
            path = Path(self.cfg["source_root"]) / entry["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Test fixture evidence for {entry['id']}.")
        self.run_dir = self.root / "run"

    def execute(self, mode="normal"):
        backend = SyntheticBackend(self.cfg, mode)
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = runner.run()
        return backend, runner, ledger

    def write_config(self, cfg):
        path = self.root / "config.json"
        path.write_text(json.dumps(cfg))
        return path

    def test_U01_example_configuration_passes_the_real_cli(self):
        result = subprocess.run(
            [sys.executable, "naming.py", "check", "--config", "config.example.json"],
            cwd=HERE,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("8 readable sources", result.stdout)
        self.assertIn("Three primary judges", result.stdout)

    def test_U02_all_configured_sources_are_snapshotted(self):
        sources = collect_sources(self.cfg)
        self.assertEqual(len(sources), 8)
        self.assertTrue(all(source["sha256"] for source in sources.values()))

    def test_U03_full_pipeline_finishes_with_five_ranked_names(self):
        _, _, ledger = self.execute()
        self.assertEqual(len(ledger["ranking"]), 5)
        self.assertEqual(json.loads((self.run_dir / "status.json").read_text())["status"], "complete")

    def test_U04_pipeline_preserves_twenty_twelve_eight_five_counts(self):
        backend, _, ledger = self.execute()
        calls = {call["stage"]: call for call in backend.calls}
        self.assertEqual(len(calls["03-screen"]["payload"]["candidates"]), 20)
        self.assertEqual(len(calls["07-semifinal"]["payload"]["candidates"]), 12)
        first_challenge = next(call for call in backend.calls if call["stage"].startswith("08-challenge"))
        self.assertEqual(len(first_challenge["payload"]["candidates"]), 8)
        self.assertEqual(len(ledger["ranking"]), 5)

    def test_U05_replacement_identity_and_parentage_survive(self):
        _, _, ledger = self.execute()
        replacement = ledger["candidates"]["fixture_replacement"]
        self.assertEqual(replacement["parent_id"], "fixture_00")
        self.assertNotIn("fixture_00", [item["candidate_id"] for item in ledger["ranking"]])

    def test_U06_priority_personas_receive_independent_inputs(self):
        backend, _, _ = self.execute()
        persona_calls = [call for call in backend.calls if call["stage"].startswith("06-persona-")]
        self.assertEqual(len(persona_calls), 3)
        for call in persona_calls:
            self.assertEqual(call["payload"]["prior_reviews"], [])
            self.assertEqual(call["payload"]["material_evidence"], [])
            self.assertNotIn("priority_personas", call["payload"]["product"])

    def test_U07_targeted_research_round_and_revisions_are_bounded(self):
        backend, _, _ = self.execute()
        self.assertEqual(len([call for call in backend.calls if call["stage"].startswith("08-challenge")]), 2)
        self.assertEqual(len([call for call in backend.calls if call["role"] == "challenge_gate"]), 1)
        self.assertEqual(len([call for call in backend.calls if call["stage"].startswith("11-revision")]), 3)

    def test_U08_shortlist_contains_decision_evidence_and_limits(self):
        self.execute()
        report = (self.run_dir / "shortlist.md").read_text()
        for phrase in ["Priority persona response", "Adversarial assessment", "Weakest joint", "Rejected candidates", "AI simulations"]:
            self.assertIn(phrase, report)

    def test_U09_same_day_resume_reuses_accepted_work(self):
        _, _, original = self.execute()
        def forbidden(*args, **kwargs):
            raise AssertionError("resume invoked the backend")
        with contextlib.redirect_stdout(io.StringIO()):
            resumed = Runner(self.cfg, self.run_dir, backend=forbidden, resume=True).run()
        self.assertEqual(resumed, original)

    def test_U10_manifest_hashes_match_the_source_snapshots(self):
        self.execute()
        manifest = json.loads((self.run_dir / "manifest.json").read_text())
        for source in manifest["sources"].values():
            self.assertEqual(source["sha256"], digest(Path(source["absolute_path"]).read_text()))

    def test_A01_source_path_cannot_escape_the_configured_root(self):
        outside = self.root / "outside.md"
        outside.write_text("Test fixture evidence.")
        cfg = copy.deepcopy(self.cfg)
        cfg["product_sources"][0]["path"] = "../outside.md"
        with self.assertRaisesRegex(Invalid, "escapes configured project root"):
            collect_sources(cfg)

    def test_A02_midrun_source_change_stops_the_pipeline(self):
        runner = Runner(self.cfg, self.run_dir, backend=SyntheticBackend(self.cfg))
        first = next(iter(runner.sources.values()))
        Path(first["absolute_path"]).write_text("Changed after snapshot.")
        with self.assertRaisesRegex(Invalid, "Source changed during run"):
            runner.run()

    def test_A03_duplicate_priority_personas_are_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["priority_personas"][1] = cfg["priority_personas"][0]
        with self.assertRaisesRegex(Invalid, "three distinct primary personas"):
            load_config(self.write_config(cfg))

    def test_A04_invalid_weight_total_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["weights"]["clarity"] = 9
        with self.assertRaisesRegex(Invalid, "Weights must total 100"):
            load_config(self.write_config(cfg))

    def test_A05_missing_source_file_is_not_silently_ignored(self):
        missing = Path(self.cfg["source_root"]) / self.cfg["product_sources"][0]["path"]
        missing.unlink()
        with self.assertRaises(FileNotFoundError):
            collect_sources(self.cfg)

    def test_A06_unsupported_research_claims_stop_after_bounded_attempts(self):
        backend = SyntheticBackend(self.cfg, "unsupported_checks")
        runner = Runner(self.cfg, self.run_dir, backend=backend)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(Invalid, "external research needs"):
            runner.run()
        attempts = [call for call in backend.calls if call["stage"] == "03-screen"]
        self.assertEqual(len(attempts), self.cfg["max_attempts"])
        self.assertFalse((self.run_dir / "shortlist.md").exists())

    def test_A07_upheld_disqualifications_can_reduce_the_final_count(self):
        _, _, ledger = self.execute("few")
        self.assertEqual(len(ledger["ranking"]), 4)
        self.assertIn("Only 4 of the requested 5", (self.run_dir / "shortlist.md").read_text())

    def test_A08_cross_candidate_revision_evidence_is_rejected(self):
        runner = Runner(self.cfg, self.run_dir, backend=SyntheticBackend(self.cfg, "wrong_revision"))
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(Invalid, "unrelated or nonmaterial"):
            runner.run()
        self.assertFalse((self.run_dir / "shortlist.md").exists())

    def test_A09_concurrent_run_lock_fails_closed(self):
        runner = Runner(self.cfg, self.run_dir, backend=SyntheticBackend(self.cfg))
        (self.run_dir / "run.lock").write_text("99999\n")
        with self.assertRaisesRegex(Invalid, "Run already locked"):
            runner.run()

    def test_A10_next_day_resume_requires_fresh_research(self):
        self.execute()
        path = self.run_dir / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["created_at"] = "2000-01-01T00:00:00+00:00"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(Invalid, "another UTC day"):
            Runner(self.cfg, self.run_dir, backend=SyntheticBackend(self.cfg), resume=True)


if __name__ == "__main__":
    unittest.main()
