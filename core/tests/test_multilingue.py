#!/usr/bin/env python3
"""Tests du corpus MULTILINGUE — l'entrée de Le Bon (1895, français).

Deux familles de garanties :
  1. Le chemin FRANÇAIS fonctionne (segmentation, lexique, atomisation de l'œuvre réelle).
  2. Le chemin ALLEMAND n'a pas bougé — une langue ajoutée ne doit jamais déplacer un défaut
     vers l'autre (leçon de l'audit des liminaires : un correctif local, un régressif ailleurs).
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import atomisation, lexique, sources                       # noqa: E402
from core.segmentation import segmenter                              # noqa: E402


class TestSegmentationFrancaise(unittest.TestCase):

    def test_deux_phrases_simples(self):
        p = segmenter("La foule est crédule. Le meneur le sait.", langue="fr")
        self.assertEqual([x["texte"] for x in p],
                         ["La foule est crédule.", "Le meneur le sait."])

    def test_abreviations_francaises(self):
        # « M. Taine », « vol. III », « p. 12 » : aucun de ces points ne clôt une phrase.
        for t in ["M. Taine a décrit les faits.",
                  "On lira vol. III. de cet ouvrage.",
                  "Voir p. ex. la Révolution."]:
            self.assertEqual(len(segmenter(t, langue="fr")), 1, "coupé sur « %s »" % t)

    def test_majuscule_accentuee_ouvre_une_phrase(self):
        # « À » ouvre très souvent une phrase française ; la classe allemande l'ignorerait.
        p = segmenter("Les faits changent. À peine réunis, ils se transforment.", langue="fr")
        self.assertEqual(len(p), 2)

    def test_recomposition_exacte(self):
        src = "L'âme des foules ? Elle est mobile. M. Taine l'a montré."
        p = segmenter(src, langue="fr")
        for x in p:
            self.assertEqual(src[x["debut"]:x["fin"]], x["texte"])


LE_BON = "Gustave Le Bon"


class TestLexiqueFrancais(unittest.TestCase):
    """Le Bon a SES concepts, sous SES noms — pas des identifiants freudiens francisés."""

    def test_concepts_de_la_controverse(self):
        trouves = {c["concept"] for c in lexique.concepts_de(
            "La foule obéit au meneur par contagion, imitation et prestige.", LE_BON)}
        self.assertTrue({"foule", "meneur", "contagion", "imitation", "prestige"} <= trouves)

    def test_concepts_homonymes_mais_distincts(self):
        """Le Bon écrit « inconscient » dès 1895, dans un tout autre sens que Freud : un fonds
        héréditaire de race, non un refoulé. Les lexiques restent séparés, sinon la seule chose
        qu'une comparaison mesurerait serait l'homonymie."""
        fr = {c["concept"] for c in lexique.concepts_de("L'inconscient des foules domine.", LE_BON)}
        de = {c["concept"] for c in lexique.concepts_de("Das Unbewußte ist verdrängt.")}
        self.assertIn("inconscient", fr)      # nom français, chez Le Bon
        self.assertIn("unbewusst", de)        # nom allemand, chez Freud
        self.assertNotIn("unbewusst", fr)     # aucun identifiant emprunté à l'autre

    def test_inconscient_et_conscience_separes(self):
        """« conscien » nu prendrait aussi « inconscient » : les deux concepts doivent rester
        distincts, sinon toute mesure de l'inconscient chez Le Bon serait doublée."""
        seul = {c["concept"] for c in lexique.concepts_de("L'inconscient domine.", LE_BON)}
        self.assertIn("inconscient", seul)
        self.assertNotIn("conscient", seul)

    def test_statut_francais(self):
        self.assertEqual(lexique.statut_de("La foule a-t-elle peut-être raison ?", LE_BON),
                         "interrogatif")     # le plus prudent gagne sur « peut-être »
        self.assertEqual(lexique.statut_de("La foule est sans doute crédule.", LE_BON), "modalise")
        self.assertEqual(lexique.statut_de("D'après Taine, la foule détruisit tout.", LE_BON),
                         "rapporte")
        self.assertEqual(lexique.statut_de("La foule est crédule.", LE_BON), "affirme")

    def test_faux_amis_ecartes(self):
        """« la cité » n'est pas une citation, « se rapporte à » n'est pas un rapport."""
        self.assertEqual(lexique.statut_de("Ces faits se rapportent à la cité antique.", LE_BON),
                         "affirme")

    def test_fonctions_francaises(self):
        etablies, a_confirmer = lexique.fonctions_par_fiabilite(
            "On objectera sans doute que les foules ne raisonnent pas.", LE_BON)
        self.assertIn("hypothese", etablies)
        self.assertIn("objection", a_confirmer)       # signal, jamais un fait acquis

    def test_validation_tables_francaises(self):
        """Chaque clé française renvoie à un identifiant existant — pas de concept fantôme."""
        v = lexique.valider()
        self.assertTrue(v["ok"], v["erreurs"])


class TestPsychologieDesFoules(unittest.TestCase):
    """L'œuvre réelle, de bout en bout."""

    @classmethod
    def setUpClass(cls):
        cls.r = atomisation.atomiser("psychologie_des_foules")

    def test_integrite(self):
        c = self.r["controles"]
        self.assertTrue(c["recomposition_ordre_ok"])
        self.assertTrue(c["localisation_complete"])

    def test_auteur_du_volume(self):
        self.assertEqual(self.r["controles"]["par_auteur"], {"Gustave Le Bon": 1485})

    def test_liminaires_retires(self):
        """Le catalogue de l'éditeur (« La Fumée du Tabac »…), la page de titre et la dédicace
        à Ribot ne sont pas des atomes ; le texte commence à la préface."""
        premier = self.r["atomes"][0]["texte"]
        self.assertIn("PRÉFACE", premier)
        tous = " ".join(a["texte"] for a in self.r["atomes"][:50])
        self.assertNotIn("Fumée du Tabac", tous)
        self.assertNotIn("FÉLIX ALCAN, ÉDITEUR", tous)

    def test_table_des_matieres_finale_retiree(self):
        """La table analytique (13 500 signes de libellés + numéros de page) clôt le volume :
        aucun atome ne doit en provenir."""
        dernier = self.r["atomes"][-1]["texte"]
        self.assertNotIn("TABLE DES MATIÈRES", dernier)
        self.assertIn("lendemains", dernier)       # la vraie dernière phrase du livre

    def test_chapitres_par_livre(self):
        """La numérotation repart à chaque livre : le repère porte le livre (« II.III »),
        sans quoi trois « chapitre premier » seraient indiscernables."""
        numeros = {a["chapitre"]["numero"] for a in self.r["atomes"] if a["chapitre"]}
        self.assertIn("I.I", numeros)
        self.assertIn("III.V", numeros)
        self.assertEqual(len(numeros), 13)         # 4 + 4 + 5 chapitres

    def test_datation_certaine(self):
        """Édition d'origine (1895 = 1895) : chaque atome est daté avec certitude."""
        self.assertTrue(all(a["attestation"]["precise"] for a in self.r["atomes"]))

    def test_le_style_peremptoire_est_mesurable(self):
        """Le contraste Freud/Le Bon n'est pas une impression : Le Bon AFFIRME massivement
        (~90 %), là où Freud module. Si ce chiffre s'effondre, c'est que les marqueurs français
        de modalisation se sont mis à surproduire — le test protège la mesure, pas le style."""
        atomes = self.r["atomes"]
        part_affirme = sum(1 for a in atomes if a["statut"] == "affirme") / len(atomes)
        self.assertGreater(part_affirme, 0.80)

    def test_licence_propre_a_l_auteur(self):
        meta = sources.charger("psychologie_des_foules")["meta"]
        self.assertIn("Gustave Le Bon", meta["licence"])
        self.assertNotIn("Freud", meta["licence"])


class TestNonRegressionAllemande(unittest.TestCase):
    """L'ajout du français ne doit RIEN changer à l'allemand."""

    def test_segmentation_allemande_inchangee(self):
        p = segmenter("Der Traum ist eine Wunscherfüllung. Das ist die These.")
        self.assertEqual(len(p), 2)
        # Le guillemet ouvrant « n'appartient qu'à la classe française.
        self.assertEqual(len(segmenter("Er sagte « nichts » dazu. Dann ging er.")), 2)

    def test_oeuvre_allemande_meme_compte(self):
        """Jenseits : compte d'atomes témoin. S'il bouge sans raison déclarée, une modification
        destinée à une autre langue a fui vers l'allemand.

        VALEUR MISE À JOUR le 2026-07-28 : 545 → 538. La cause est connue et voulue — l'apparat
        bibliographique a rejoint la liste des abréviations (« Zeitschr. », « Jahrb. », « Vgl. »),
        ce qui a supprimé sept coupures abusives dans ce volume et 791 dans le corpus entier.
        Un témoin de non-régression n'interdit pas le changement : il exige qu'il soit expliqué.
        """
        r = atomisation.atomiser("jenseits")
        self.assertEqual(r["controles"]["total_atomes"], 538)

    def test_auteur_par_defaut_reste_freud(self):
        r = atomisation.atomiser("jenseits")
        self.assertEqual(set(r["controles"]["par_auteur"]), {"Sigmund Freud"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
