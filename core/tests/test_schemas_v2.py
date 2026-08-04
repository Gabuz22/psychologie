#!/usr/bin/env python3
import json
import os
import sqlite3
import sys
import unittest

from core import relations_v2


class TestSchemasV2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def test_schema_json_et_sql_sont_synchronises_avec_le_code(self):
        with open(os.path.join(self.racine, "schemas", "relations_v2.schema.json"),
                  encoding="utf-8") as f:
            self.assertEqual(json.load(f), relations_v2.JSON_SCHEMA)
        with open(os.path.join(self.racine, "schemas", "relations_v2.sql"), encoding="utf-8") as f:
            self.assertEqual(f.read(), relations_v2.SQL_SCHEMA.strip() + "\n")
        with open(os.path.join(self.racine, "schemas", "relations_v2_rollback.sql"),
                  encoding="utf-8") as f:
            self.assertEqual(f.read(), relations_v2.SQL_ROLLBACK.strip() + "\n")

    def test_chaque_objet_canonique_est_complet(self):
        with open(os.path.join(self.racine, "schemas", "objets_analytiques_v2.json"),
                  encoding="utf-8") as f:
            schema = json.load(f)
        attendus = {"auteur", "oeuvre", "edition", "passage_source", "atome", "terme",
                    "entree_lexique", "notion", "concept_reconstruit", "famille_conceptuelle",
                    "proposition", "acte_analytique", "assertion", "relation", "preuve",
                    "contre_preuve", "annotation", "validation", "desaccord",
                    "resultat_calcule", "regle", "execution"}
        self.assertEqual(set(schema["objects"]), attendus)
        champs = {"definition", "epistemic_status", "required", "optional", "identifier",
                  "provenance", "allowed_relations", "invariants", "example", "distinct_from"}
        for nom, objet in schema["objects"].items():
            self.assertEqual(set(objet), champs, nom)

    def test_schema_export_d1_est_executable_et_expose_le_statut_agrege(self):
        bin_dir = os.path.join(self.racine, "bin")
        sys.path.insert(0, bin_dir)
        try:
            import exporter_d1
            db = sqlite3.connect(":memory:")
            try:
                db.executescript(exporter_d1.SCHEMA)
                colonnes = {r[1] for r in db.execute("PRAGMA table_info(carte_actes)")}
            finally:
                db.close()
        finally:
            sys.path.remove(bin_dir)
        self.assertIn("etat_validation", colonnes)
        self.assertIn("verdicts_elementaires", colonnes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
