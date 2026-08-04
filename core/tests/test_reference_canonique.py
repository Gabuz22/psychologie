#!/usr/bin/env python3
import copy
import os
import unittest

from core import reference_canonique


class TestReferenceCanonique(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registre = reference_canonique.construire()
        cls.racine = reference_canonique.RACINE

    def test_generation_est_deterministe(self):
        a = reference_canonique.json_canonique(self.registre)
        b = reference_canonique.json_canonique(reference_canonique.construire())
        self.assertEqual(a, b)

    def test_artefact_absent_est_refuse(self):
        registre = reference_canonique.copie_avec_artefact_absent(self.registre)
        codes = {e["code"] for e in reference_canonique.valider(registre)["erreurs"]}
        self.assertIn("artefact_absent", codes)

    def test_empreinte_incoherente_est_refusee(self):
        registre = copy.deepcopy(self.registre)
        registre["references"][0]["artefacts"][0]["sha256"] = "0" * 64
        codes = {e["code"] for e in reference_canonique.valider(registre)["erreurs"]}
        self.assertIn("artefact_modifie", codes)

    def test_desynchronisation_documentaire_est_detectee(self):
        chemins = {"README.md", "web/site/index.html", "web/site/app.js",
                   "web/worker/donnees.js", "documentation/CARTE_CITATIONS.md",
                   "documentation/COUVERTURE_MESUREE.md",
                   "documentation/POUR_LES_CHERCHEURS.md",
                   "documentation/SYNTHESE_FREUD.md", "documentation/INVENTAIRE_ATOMES.md",
                   "documentation/CHAPITRAGE.md", "documentation/TRADUCTION.md"}
        textes = {}
        for relatif in chemins:
            with open(os.path.join(self.racine, *relatif.split("/")), encoding="utf-8") as f:
                textes[relatif] = f.read()
        textes["README.md"] = textes["README.md"].replace("**116 545 atomes**",
                                                            "**116 544 atomes**")
        erreurs = reference_canonique.verifier_declarations(
            self.registre, textes=textes)
        self.assertTrue(any(e["code"] == "declaration_absente" and
                            e["fichier"] == "README.md" for e in erreurs))

    def test_d1_reste_canonique_historique_et_v2_experimental(self):
        refs = {r["id"]: r for r in self.registre["references"]}
        self.assertEqual(refs["d1-historique-2026-08-03"]["statut"],
                         "canonique historique")
        self.assertEqual(refs["fondations-relations-v2"]["statut"], "expérimental")
        self.assertNotEqual(refs["d1-historique-2026-08-03"]["statut"],
                            refs["fondations-relations-v2"]["statut"])

    def test_aucun_resultat_automatique_n_est_promu_validation_humaine(self):
        v2 = self.registre["faits"]["v2"]
        self.assertEqual(v2["annotations_humaines_prototype"], 0)
        self.assertEqual(v2["annotations_de_type_humain_dans_relations"], 0)
        self.assertEqual(v2["annotations_humaines_experience"], 0)

    def test_acte_96_est_discordant_sans_modification_de_d1(self):
        d1 = self.registre["faits"]["d1"]
        self.assertTrue(d1["colonnes_actes_v2_absentes"])
        self.assertIsNone(d1["acte_96"]["verdict_historique"])
        self.assertEqual(d1["acte_96"]["etat_interprete_sans_modifier_d1"], "discordant")

    def test_identite_de_libelle_ne_produit_aucune_equivalence(self):
        v2 = self.registre["faits"]["v2"]
        self.assertEqual(v2["homonymes_translexicaux"], 96)
        self.assertEqual(v2["propositions_equivalence"], 0)

    def test_graphes_et_relations_historiques_ne_regressent_pas(self):
        comptes = self.registre["faits"]["d1"]["comptes"]
        self.assertEqual(comptes["concept_liens"], 7646)
        self.assertEqual(comptes["grappes"], 8)
        self.assertEqual(comptes["liens_reprise"], 507)
        self.assertEqual(comptes["carte_actes"], 354)
        self.assertEqual(comptes["mentions"], 2899)

    def test_declarations_courantes_sont_synchronisees(self):
        self.assertEqual(reference_canonique.verifier_declarations(self.registre), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
