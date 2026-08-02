#!/usr/bin/env python3
"""TESTS du registre de traduction — la mémoire des lectures françaises des citations.

Ce qui est protégé ici : une traduction est toujours ancrée sur l'EMPREINTE du texte (jamais un
rang qui dérive), jamais vide, toujours datée, et fusionner un nouveau lot n'écrase jamais ce qui
est déjà acquis — une interruption en cours de fusion ne doit perdre que le lot en cours.
"""
import os
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import traductions           # noqa: E402


class TestRegistre(unittest.TestCase):

    def test_integrite_du_registre_reel(self):
        """Vide (rien traduit encore) ou peuplé : le registre réel doit toujours être valide."""
        r = traductions.valider()
        self.assertTrue(r["ok"], "registre incohérent : %s" % r["erreurs"])

    def test_absence_de_fichier_rend_un_registre_vide_pas_une_erreur(self):
        # charger() sur un chemin inexistant ne doit jamais lever — un registre pas encore
        # commencé est un état légitime, pas une panne.
        with unittest.mock.patch.object(traductions, "FICHIER", "/chemin/inexistant.json"):
            t = traductions.charger()
        self.assertEqual(t, {"meta": {"scope": []}, "traductions": {}})

    def test_cle_est_l_empreinte_jamais_un_rang(self):
        atome = {"empreinte": "abc123", "id": "traumdeutung:a42"}
        self.assertEqual(traductions.cle(atome), "abc123")
        self.assertEqual(traductions.cle("abc123"), "abc123")

    def test_traduction_absente_rend_none(self):
        table = {"meta": {}, "traductions": {}}
        self.assertIsNone(traductions.traduction({"empreinte": "inconnue"}, table))

    def test_traduction_presente_est_rendue(self):
        table = {"meta": {}, "traductions": {"abc": {"texte_fr": "Le rêve est un accomplissement "
                                                                  "de désir.", "genere_le": "2026-08-02"}}}
        self.assertEqual(traductions.traduction({"empreinte": "abc"}, table),
                         "Le rêve est un accomplissement de désir.")

    def test_valider_refuse_une_traduction_vide(self):
        r = traductions.valider({"traductions": {"abc": {"texte_fr": "  ", "genere_le": "2026-08-02"}}})
        self.assertFalse(r["ok"])
        self.assertIn("vide", r["erreurs"][0])

    def test_valider_refuse_une_traduction_sans_date(self):
        r = traductions.valider({"traductions": {"abc": {"texte_fr": "Le rêve."}}})
        self.assertFalse(r["ok"])
        self.assertIn("date", r["erreurs"][0])


class TestEnregistrer(unittest.TestCase):
    """`enregistrer()` travaille sur un fichier temporaire dédié — jamais le registre réel,
    pour que ces tests ne polluent jamais les traductions déjà produites."""

    def setUp(self):
        self.dossier = tempfile.mkdtemp()
        self.chemin = os.path.join(self.dossier, "citations_fr.json")

    def test_un_premier_lot_cree_le_fichier(self):
        n = traductions.enregistrer({"abc": "Le rêve est un accomplissement de désir."},
                                     "2026-08-02", scope_ajoute="Sigmund Freud", chemin=self.chemin)
        self.assertEqual(n, 1)
        self.assertTrue(os.path.exists(self.chemin))

    def test_un_second_lot_s_ajoute_sans_ecraser_le_premier(self):
        traductions.enregistrer({"abc": "Premier."}, "2026-08-02", chemin=self.chemin)
        traductions.enregistrer({"def": "Second."}, "2026-08-02", chemin=self.chemin)
        with open(self.chemin, encoding="utf-8") as f:
            import json
            t = json.load(f)
        self.assertEqual(t["traductions"]["abc"]["texte_fr"], "Premier.")
        self.assertEqual(t["traductions"]["def"]["texte_fr"], "Second.")

    def test_reenregistrer_la_meme_empreinte_remplace_sans_dupliquer(self):
        traductions.enregistrer({"abc": "Brouillon."}, "2026-08-02", chemin=self.chemin)
        traductions.enregistrer({"abc": "Version corrigée."}, "2026-08-03", chemin=self.chemin)
        with open(self.chemin, encoding="utf-8") as f:
            import json
            t = json.load(f)
        self.assertEqual(len(t["traductions"]), 1)
        self.assertEqual(t["traductions"]["abc"]["texte_fr"], "Version corrigée.")

    def test_scope_s_accumule_sans_doublon(self):
        traductions.enregistrer({"abc": "Un."}, "2026-08-02", scope_ajoute="Sigmund Freud",
                                 chemin=self.chemin)
        traductions.enregistrer({"def": "Deux."}, "2026-08-02", scope_ajoute="Sigmund Freud",
                                 chemin=self.chemin)
        traductions.enregistrer({"ghi": "Trois."}, "2026-08-02", scope_ajoute="Otto Rank",
                                 chemin=self.chemin)
        with open(self.chemin, encoding="utf-8") as f:
            import json
            t = json.load(f)
        self.assertEqual(t["meta"]["scope"], ["Otto Rank", "Sigmund Freud"])

    def test_un_lot_avec_une_traduction_vide_est_refuse_en_bloc(self):
        with self.assertRaises(ValueError):
            traductions.enregistrer({"abc": "Bien.", "def": "   "}, "2026-08-02", chemin=self.chemin)
        # RIEN ne doit avoir été écrit — un lot refusé est refusé EN BLOC, jamais à moitié fusionné.
        self.assertFalse(os.path.exists(self.chemin))


class TestCouverture(unittest.TestCase):

    def test_couverture_se_mesure_sur_la_portee_donnee_pas_le_corpus_entier(self):
        table = {"meta": {"scope": ["Sigmund Freud"]},
                 "traductions": {"a": {"texte_fr": "Un.", "genere_le": "x"},
                                 "b": {"texte_fr": "Deux.", "genere_le": "x"}}}
        atomes_freud = [{"empreinte": "a"}, {"empreinte": "b"}, {"empreinte": "c"}]
        c = traductions.couverture(atomes_freud, table)
        self.assertEqual(c, {"total": 3, "traduits": 2, "part": round(2 / 3, 4)})

    def test_couverture_ne_faussee_pas_par_un_auteur_hors_portee(self):
        """Un auteur pas encore commencé (aucune entrée dans le registre) ne doit jamais faire
        chuter une couverture mesurée sur un AUTRE auteur, déjà complet."""
        table = {"meta": {"scope": ["Sigmund Freud"]},
                 "traductions": {"a": {"texte_fr": "Un.", "genere_le": "x"}}}
        atomes_freud_seuls = [{"empreinte": "a"}]
        self.assertEqual(traductions.couverture(atomes_freud_seuls, table)["part"], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
