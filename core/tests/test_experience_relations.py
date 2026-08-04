#!/usr/bin/env python3
import json
import os
import unittest

from core import experience_relations, registres_v2


class TestExperienceRelations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(cls.racine, "manifests", "corpus_actuel.json"), encoding="utf-8") as f:
            cls.manifest = json.load(f)
        with open(os.path.join(cls.racine, "prototypes", "relations_v2",
                               "experience_freud_stekel.json"), encoding="utf-8") as f:
            cls.fichier = json.load(f)

    def test_generation_deterministe(self):
        base = os.path.join(self.racine, "derive", "d1", "corpus.sqlite")
        db = registres_v2.charger_base(base)
        try:
            a = experience_relations.construire(db, self.manifest)
            b = experience_relations.construire(db, self.manifest)
        finally:
            db.close()
        self.assertEqual(experience_relations.json_canonique(a),
                         experience_relations.json_canonique(b))
        self.assertEqual(experience_relations.json_canonique(a),
                         experience_relations.json_canonique(self.fichier))

    def test_positifs_negatifs_ambigus_et_baselines_sont_presents(self):
        r = self.fichier["automatic_preliminary_results"]
        self.assertGreater(r["candidats_v1"], 0)
        self.assertGreater(r["controles_non_candidats"], 0)
        self.assertIn("indecidable", self.fichier["categories_predefined"])
        for item in self.fichier["blind_items"]:
            self.assertEqual(set(item), {"item_id", "source", "target"})
            self.assertRegex(item["item_id"], r"^item:[0-9a-f]{20}$")
            self.assertNotIn("baselines", item)
            for cote in ("source", "target"):
                self.assertIn("context_before", item[cote])
                self.assertIn("context_after", item[cote])
                self.assertIn("date_interval", item[cote])
                self.assertIn("offsets", item[cote])
            baseline = self.fichier["automatic_reference_not_gold"][item["item_id"]]["baselines"]
            self.assertEqual(set(baseline), {
                "b0_noms_explicites", "b1_contenance_6grammes",
                "b2_jaccard_lexical", "systeme_actuel_candidat"})

    def test_identifiants_et_references_automatiques_ne_fuitent_pas_dans_les_items_aveugles(self):
        ids = [i["item_id"] for i in self.fichier["blind_items"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(self.fichier["automatic_reference_not_gold"]))
        serialise = json.dumps(self.fichier["blind_items"], ensure_ascii=False)
        self.assertNotIn("candidate:acte", serialise)
        self.assertNotIn("controle_non_candidat", serialise)
        self.assertNotIn("verdict_legacy", serialise)

    def test_aucune_annotation_humaine_n_est_fabriquee(self):
        self.assertEqual(self.fichier["human_annotations"], [])
        self.assertEqual(self.fichier["automatic_preliminary_results"]["precision_rappel"],
                         "non_calculables_sans_annotations_humaines")


if __name__ == "__main__":
    unittest.main(verbosity=2)
