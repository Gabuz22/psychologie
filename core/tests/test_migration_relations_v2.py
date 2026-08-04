#!/usr/bin/env python3
import json
import os
import sqlite3
import tempfile
import unittest

from core import migration_relations_v2, registres_v2


class TestMigrationRelationsV2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.base = os.path.join(cls.racine, "derive", "d1", "corpus.sqlite")
        with open(os.path.join(cls.racine, "manifests", "corpus_actuel.json"), encoding="utf-8") as f:
            cls.manifest = json.load(f)
        with open(os.path.join(cls.racine, "prototypes", "relations_v2",
                               "registre_probatoire_freud_stekel.json"), encoding="utf-8") as f:
            cls.prototype = json.load(f)

    def rapport(self):
        db = registres_v2.charger_base(self.base)
        try:
            return migration_relations_v2.rapport_a_blanc(db, self.prototype, self.manifest)
        finally:
            db.close()

    def test_dry_run_necrit_rien_et_produit_un_differentiel(self):
        avant = os.path.getsize(self.base)
        r = self.rapport()
        self.assertEqual(os.path.getsize(self.base), avant)
        self.assertEqual(r["mode"], "dry_run")
        self.assertEqual(r["would_modify_historical_rows"], 0)
        self.assertGreater(r["would_create"]["relations"], 1)

    def test_acte_discordant_est_conserve_comme_non_convertible(self):
        r = self.rapport()
        u = {x["source_id"]: x for x in r["unconvertible"]}
        self.assertIn("96", u)
        self.assertIn("discordant_agrege", u["96"]["reason"])

    def test_application_separee_et_ancien_score_non_canonique(self):
        with tempfile.TemporaryDirectory() as d:
            cible = os.path.join(d, "prototype.sqlite")
            comptes = migration_relations_v2.appliquer(
                cible, self.prototype, self.manifest, self.rapport())
            self.assertGreater(comptes["v2_relations"], 1)
            db = sqlite3.connect(cible)
            try:
                self.assertEqual(db.execute(
                    "SELECT COUNT(*) FROM v2_legacy_metrics WHERE canonical != 0").fetchone()[0], 0)
                self.assertIn("ni confiance", db.execute(
                    "SELECT caveat FROM v2_legacy_metrics LIMIT 1").fetchone()[0])
            finally:
                db.close()

    def test_seconde_application_est_refusee(self):
        with tempfile.TemporaryDirectory() as d:
            cible = os.path.join(d, "prototype.sqlite")
            migration_relations_v2.appliquer(cible, self.prototype, self.manifest, self.rapport())
            with self.assertRaises(FileExistsError):
                migration_relations_v2.appliquer(cible, self.prototype, self.manifest, self.rapport())

    def test_rollback_ne_touche_pas_une_table_historique(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE historique (id INTEGER)")
        db.executescript(__import__("core.relations_v2", fromlist=["SQL_SCHEMA"]).SQL_SCHEMA)
        migration_relations_v2.rollback_schema(db)
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("historique", tables)
        self.assertFalse(any(t.startswith("v2_") for t in tables))


if __name__ == "__main__":
    unittest.main(verbosity=2)
