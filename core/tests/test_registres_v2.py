#!/usr/bin/env python3
import json
import os
import unittest

from core import registres_v2


class TestRegistresV2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.base = os.path.join(cls.racine, "derive", "d1", "corpus.sqlite")
        with open(os.path.join(cls.racine, "prototypes", "relations_v2",
                               "candidats_translexicaux.json"), encoding="utf-8") as f:
            cls.translexical = json.load(f)
        with open(os.path.join(cls.racine, "prototypes", "relations_v2",
                               "registre_probatoire_freud_stekel.json"), encoding="utf-8") as f:
            cls.prototype = json.load(f)

    def test_les_96_noms_restent_des_candidats_non_examined(self):
        self.assertEqual(self.translexical["nombre"], 96)
        self.assertEqual(len(self.translexical["candidats"]), 96)
        for c in self.translexical["candidats"]:
            self.assertEqual(c["statut_automatique"], "identite_terminologique_seulement")
            self.assertEqual(c["statut_humain"], "homonymie_non_examinee")
            self.assertEqual(c["propositions_equivalence"], [])

    def test_registre_translexical_est_regenerable_octet_pour_octet(self):
        db = registres_v2.charger_base(self.base)
        try:
            regenere = registres_v2.registre_translexical(db)
        finally:
            db.close()
        self.assertEqual(registres_v2.json_canonique(regenere),
                         registres_v2.json_canonique(self.translexical))

    def test_tirage_probatoire_est_reproductible_et_non_humain(self):
        db = registres_v2.charger_base(self.base)
        try:
            actes, tirage = registres_v2.echantillon_actes(db)
        finally:
            db.close()
        ids_fichier = sorted({r["legacy"]["id"] for r in self.prototype["relations"]})
        self.assertEqual([a["id"] for a in actes], ids_fichier)
        self.assertEqual(tirage, self.prototype["tirage"])
        self.assertEqual(self.prototype["human_annotations"], [])
        self.assertIn("non_valide_humainement", self.prototype["status"])

    def test_plusieurs_relations_coexistent_pour_un_meme_acte(self):
        par_acte = {}
        for r in self.prototype["relations"]:
            par_acte.setdefault(r["legacy"]["id"], set()).add(r["type"])
        self.assertTrue(any(len(types) > 1 for types in par_acte.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
