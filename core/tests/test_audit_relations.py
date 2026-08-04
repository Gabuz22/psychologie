#!/usr/bin/env python3
import sqlite3
import unittest

from core.audit_relations import auditer_connexion


def base_minimale():
    db = sqlite3.connect(":memory:")
    db.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE atomes (id INTEGER PRIMARY KEY, atome_id TEXT NOT NULL);
        CREATE TABLE liens_reprise (
          atome_a TEXT, atome_b TEXT, source_tierce INTEGER, sens TEXT, verdict TEXT);
        CREATE TABLE carte_actes (verdict TEXT);
        CREATE TABLE concepts (nom TEXT, auteur_id INTEGER);
        CREATE TABLE meta (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
        CREATE TABLE mentions (id INTEGER);
        CREATE TABLE lectures_declarees (id INTEGER);
        CREATE TABLE usages (id INTEGER);
        CREATE TABLE socle_liens (id INTEGER);
        CREATE TABLE socle_densites (id INTEGER);
        CREATE TABLE concept_liens (id INTEGER);
        INSERT INTO meta VALUES ('version_comparaison','1.0.0');
        INSERT INTO meta VALUES ('version_carte','1.0.0');
        INSERT INTO meta VALUES ('version_socle_par_couple','1.0.0');
    """)
    return db


class TestAuditRelations(unittest.TestCase):

    def test_base_coherente(self):
        db = base_minimale()
        db.execute("INSERT INTO atomes VALUES (1, 'o:a1')")
        db.execute("INSERT INTO liens_reprise VALUES ('o:a1','p:a1',0,'a_vers_b','confirme')")
        self.assertTrue(auditer_connexion(db)["ok"])

    def test_detecte_duplication_reflexivite_et_tierce_orientee(self):
        db = base_minimale()
        db.executemany("INSERT INTO atomes VALUES (?,?)", [(1, "o:a1"), (2, "o:a1")])
        db.executemany("INSERT INTO liens_reprise VALUES (?,?,?,?,?)", [
            ("o:a1", "o:a1", 1, "a_vers_b", None),
            ("o:a1", "o:a1", 1, "a_vers_b", None),
        ])
        r = auditer_connexion(db)
        codes = {c["code"]: c for c in r["constats"]}
        self.assertFalse(r["ok"])
        for code in ("atomes_dupliques", "reprises_reflexives", "reprises_dupliquees",
                     "tierce_orientee"):
            self.assertEqual(codes[code]["severite"], "erreur")

    def test_homonymie_et_versions_absentes_restent_des_alertes(self):
        db = base_minimale()
        db.execute("DELETE FROM meta WHERE cle = 'version_carte'")
        db.executemany("INSERT INTO concepts VALUES (?,?)", [("angoisse", 1), ("angoisse", 2)])
        r = auditer_connexion(db)
        codes = {c["code"]: c for c in r["constats"]}
        self.assertTrue(r["ok"], "une alerte méthodologique n'est pas une corruption mécanique")
        self.assertEqual(codes["concepts_homonymes"]["nombre"], 1)
        self.assertEqual(codes["versions_regles"]["nombre"], 1)

    def test_un_agregat_discordant_n_est_pas_un_acte_non_lu(self):
        db = base_minimale()
        db.execute("DROP TABLE carte_actes")
        db.execute("CREATE TABLE carte_actes (verdict TEXT, sens_lu TEXT, reclasse_vers TEXT)")
        db.execute("INSERT INTO carte_actes VALUES (NULL, 'b_vers_a', 'source commune')")
        r = auditer_connexion(db)
        codes = {c["code"]: c for c in r["constats"]}
        self.assertEqual(codes["actes_non_lus"]["nombre"], 0)
        self.assertEqual(codes["actes_validation_discordante"]["nombre"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
