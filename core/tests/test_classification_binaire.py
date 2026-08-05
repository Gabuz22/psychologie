#!/usr/bin/env python3
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from core import classification_binaire as cb
from classification_commune import ClassificationOrchestrator, ClassificationStore, OldestFirstVerifier


class TestClassificationBinairePsychologie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = cb.build_registry()

    def test_toutes_les_categories_ont_un_agent_unique(self):
        description = self.registry.describe()
        self.assertGreaterEqual(description["agent_count"], 600)
        self.assertEqual(description["by_kind"]["concept_group"], 83)
        self.assertEqual(description["by_kind"]["concept"], 588)
        self.assertEqual(description["by_kind"]["status"], 4)

    def test_lexiques_d_auteurs_restent_cloisonnes(self):
        rank = cb.Atom(cb.PROJECT_ID, "rank:1", "Das Trauma der Geburt.", taxonomy_scope="Otto Rank")
        active = {a.category_id for a in self.registry.agents_for(rank)}
        self.assertTrue(any(x.startswith("psy.otto_rank.concept.") for x in active))
        self.assertFalse(any(x.startswith("psy.sigmund_freud.concept.") for x in active))

    def test_signal_a_confirmer_n_est_jamais_materialise_comme_acquis(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ClassificationStore(os.path.join(tmp, "decisions.sqlite"))
            report = ClassificationOrchestrator(self.registry, store).classify(
                cb.Atom(cb.PROJECT_ID, "revision:1", "Nunmehr ist die Annahme zu prüfen.",
                        taxonomy_scope="Sigmund Freud"))
            revision = next(x for x in report["labels"]
                            if x["category_id"] == "psy.function.revision")
            self.assertEqual(revision["state"], "candidate_review")

    def test_decisions_oui_et_non_persistent_et_verification_oldest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ClassificationStore(os.path.join(tmp, "decisions.sqlite"))
            orchestrator = ClassificationOrchestrator(self.registry, store)
            older = cb.Atom(cb.PROJECT_ID, "old", "Vielleicht ist dies ein Traum.",
                            source_created_at="1900-01-01T00:00:00+00:00",
                            taxonomy_scope="Sigmund Freud")
            newer = cb.Atom(cb.PROJECT_ID, "new", "Dies ist bekanntlich eine Analyse.",
                            source_created_at="1920-01-01T00:00:00+00:00",
                            taxonomy_scope="Sigmund Freud")
            orchestrator.classify(newer)
            orchestrator.classify(older)
            labels = {x["category_id"] for x in store.labels(cb.PROJECT_ID, "old")}
            self.assertIn("psy.status.modalise", labels)
            with store._connection() as db:
                db.execute("UPDATE atoms SET registry_hash='ancienne-version' WHERE project_id=?",
                           (cb.PROJECT_ID,))
            verified = OldestFirstVerifier(orchestrator, cb.PROJECT_ID).verify(limit=1)
            self.assertEqual(verified["results"][0]["atom_id"], "old")


if __name__ == "__main__":
    unittest.main()
