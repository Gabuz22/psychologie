#!/usr/bin/env python3
import os
import tempfile
import unittest

from core import manifeste_corpus


class TestManifesteCorpus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.base = os.path.join(racine, "derive", "d1", "corpus.sqlite")
        cls.manifeste = manifeste_corpus.construire(cls.base, "a35fe07")

    def test_generation_deterministe(self):
        a = manifeste_corpus.json_canonique(self.manifeste)
        b = manifeste_corpus.json_canonique(
            manifeste_corpus.construire(self.base, "a35fe07"))
        self.assertEqual(a, b)

    def test_versions_source_schema_regles_export_code_sont_distinguees(self):
        self.assertIn("corpus_source", self.manifeste["versions"])
        self.assertIn("schema_export_attendu", self.manifeste["versions"])
        self.assertIn("enregistrees_dans_export", self.manifeste["versions"])
        self.assertIn("regles_code_lu", self.manifeste["versions"])
        self.assertIn("commit_git", self.manifeste["reference"])

    def test_auteurs_oeuvres_fichiers_et_comptes_sont_coherents(self):
        self.assertTrue(self.manifeste["validation"]["ok"],
                        self.manifeste["validation"]["erreurs"])
        self.assertEqual(self.manifeste["comptes"]["auteurs"], 7)
        self.assertEqual(self.manifeste["comptes"]["oeuvres"], 57)
        self.assertEqual(self.manifeste["comptes"]["atomes"], 116545)
        self.assertFalse(self.manifeste["avertissements"]["fichiers_txt_orphelins"])

    def test_export_historique_signale_sa_version_source_inconnue(self):
        codes = {a["code"] for a in self.manifeste["validation"]["avertissements"]}
        self.assertIn("version_sources_export_inconnue", codes)

    def test_detection_documentation_numerique_desynchronisee(self):
        with tempfile.TemporaryDirectory() as d:
            chemin = os.path.join(d, "README.md")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("État actuel du corpus : 54 626 atomes sur 40 œuvres.\n")
            ancienne_racine = manifeste_corpus.RACINE
            try:
                manifeste_corpus.RACINE = d
                os.mkdir(os.path.join(d, "documentation"))
                ecarts = manifeste_corpus.divergences_documentaires(116545, 57)
            finally:
                manifeste_corpus.RACINE = ancienne_racine
            self.assertEqual({e["mesure"] for e in ecarts}, {"atomes", "oeuvres"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
