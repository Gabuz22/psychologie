#!/usr/bin/env python3
"""TESTS de Karl Abraham — troisième auteur doté de son propre lexique.

Abraham est le contre-cas de Rank : celui qui approfondit là où l'autre s'écarte. Ce que ces
tests protègent, au-delà de son intégration, c'est la garantie que les DEUX se décrivent avec
leurs propres catégories — sans quoi le jour où on mesurera un socle partagé, on ne mesurerait
que la grille commune qu'on leur aurait imposée.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import agents, atomisation, lexique, lexiques, ocr, sources     # noqa: E402
from core.corpus import Corpus                                            # noqa: E402

ABRAHAM = "Karl Abraham"
OEUVRES = ["traum_und_mythus", "segantini", "klinische_beitraege",
           "entwicklungsgeschichte_libido", "charakterbildung"]


class TestLexiqueAbraham(unittest.TestCase):

    def test_concepts_signature(self):
        """Sa contribution propre : les stades de la libido, chacun dédoublé, avec leur point de
        fixation. Aucun autre auteur du corpus n'a ce jeu de concepts."""
        phrase = "Der Patient zeigte eine Regression auf die orale Stufe der Libido."
        c = {x["concept"] for x in lexique.concepts_de(phrase, ABRAHAM)}
        self.assertTrue({"oral", "libido", "regression", "patient"} <= c)

    def test_anal_nest_pas_analyse(self):
        """PIÈGE MESURÉ : « anal » nu capte « Analyse », mot omniprésent chez un psychanalyste.
        Sans l'exclusion, le concept CENTRAL d'Abraham compterait chaque occurrence du mot."""
        c = {x["concept"] for x in lexique.concepts_de(
            "Die Analyse des Patienten dauerte ein Jahr.", ABRAHAM)}
        self.assertNotIn("anal", c)
        c2 = {x["concept"] for x in lexique.concepts_de(
            "Der Analcharakter zeigt sich in Sparsamkeit und Eigensinn.", ABRAHAM)}
        self.assertIn("anal", c2)

    def test_bewusst_nest_pas_unbewusst(self):
        """Même piège que chez Le Bon : « bewusst » nu prendrait aussi « unbewusst », et toute
        mesure de l'inconscient serait doublée."""
        c = {x["concept"] for x in lexique.concepts_de(
            "Das Unbewußte bestimmt das Verhalten.", ABRAHAM)}
        self.assertIn("unbewusst", c)
        self.assertNotIn("bewusstsein", c)

    def test_fonction_propre_observation(self):
        """Abraham part TOUJOURS d'un malade : « Patient » ×30 par rapport à Freud. La fonction
        « observation » n'existe que dans son lexique."""
        etablies, _ = lexique.fonctions_par_fiabilite(
            "Der Patient, ein dreißigjähriger Mann, kam wegen Angstzuständen.", ABRAHAM)
        self.assertIn("observation", etablies)
        self.assertNotIn("observation", [f["id"] for f in lexique.FONCTIONS])

    def test_renvoi_freud_est_etabli_pas_a_confirmer(self):
        """DÉCISION DOCUMENTÉE. Ce signal s'appelait d'abord « appui déclaré sur Freud » et était
        `a_confirmer`, sur le modèle d'« ecart_freud » chez Rank. Celui-ci a donné 0 confirmé sur
        5 : un motif ne peut pas décider si une mention est un appui, un prolongement ou une
        réserve. On nomme donc la fonction pour ce que le marqueur PROUVE — la phrase invoque
        Freud — et rien de plus. Si ce test tombe, c'est qu'on a réintroduit une prétention que
        le marqueur ne peut pas tenir."""
        etablies, a_confirmer = lexique.fonctions_par_fiabilite(
            "Nach Freud ist der Traum eine Wunscherfüllung.", ABRAHAM)
        self.assertIn("renvoi_freud", etablies)
        self.assertNotIn("renvoi_freud", a_confirmer)

    def test_lexiques_des_deux_disciples_sont_distincts(self):
        """Rank et Abraham ont chacun leur grille. Un recouvrement de noms est permis, mais les
        tables doivent rester des objets séparés — c'est la garantie qui interdit de sommer."""
        a = lexiques.PAR_AUTEUR[ABRAHAM].CONCEPTS
        r = lexiques.PAR_AUTEUR["Otto Rank"].CONCEPTS
        self.assertIsNot(a, r)
        for g in set(a) & set(r):
            self.assertIsNot(a[g], r[g])
        # « aussetzung » est à Rank seul ; « dementia_praecox » à Abraham seul.
        self.assertIn("aussetzung", {c for m in r.values() for c in m["termes"]})
        self.assertNotIn("aussetzung", {c for m in a.values() for c in m["termes"]})
        self.assertIn("dementia_praecox", {c for m in a.values() for c in m["termes"]})
        self.assertNotIn("dementia_praecox", {c for m in r.values() for c in m["termes"]})


class TestOeuvresAbraham(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.r = {c: atomisation.atomiser(c) for c in OEUVRES}

    def test_integrite(self):
        for cle, r in self.r.items():
            self.assertTrue(r["controles"]["recomposition_ordre_ok"], cle)
            self.assertTrue(r["controles"]["localisation_complete"], cle)
            self.assertEqual(set(r["controles"]["par_auteur"]), {ABRAHAM}, cle)

    def test_qualite_des_facsimiles(self):
        """Ses cinq scans sont les meilleurs du corpus : 0,05 à 0,54 ‰ de caractères parasites,
        soit AU NIVEAU OU SOUS celui des transcriptions relues (0,45 à 1,23 ‰)."""
        for cle in OEUVRES:
            t = sources.charger(cle)["texte"]
            self.assertLess(ocr.corruption(t)["taux_phrases_pct"],
                            ocr.SEUIL_PHRASES_CORROMPUES_PCT, cle)

    def test_signature_thematique(self):
        """Le lexique doit retrouver seul l'objet de chaque volume — signal de validation employé
        depuis le début du projet."""
        def densite(cle, concept):
            n = sum(1 for a in self.r[cle]["atomes"]
                    if any(c["concept"] == concept for c in a["concepts"]))
            return n / len(self.r[cle]["atomes"])
        # Le « Segantini » (1911) est une monographie sur un peintre.
        self.assertEqual(max(OEUVRES, key=lambda c: densite(c, "malerei")), "segantini")
        # « Traum und Mythus » (1909) doit être le plus dense en mythe.
        self.assertEqual(max(OEUVRES, key=lambda c: densite(c, "mythus")), "traum_und_mythus")
        # La « Charakterbildung » (1925) porte sur le caractère.
        self.assertEqual(max(OEUVRES, key=lambda c: densite(c, "charakterzug")), "charakterbildung")

    def test_la_seule_revision_datee_du_corpus(self):
        """Abraham réédite en 1921 un article de 1907 et signale en post-scriptum ce qu'il y tient
        désormais pour faux — « Nachwort (1920) … enthält mancherlei Irrtümliches ».

        C'est exactement ce que Freud a CESSÉ de faire dès la 3e édition des « Drei Abhandlungen »,
        d'où l'incertitude de datation qui pèse sur tout son corpus. Ce passage est donc le
        contre-exemple qui montre ce que le corpus aurait pu être si les auteurs avaient tous
        déclaré leurs couches."""
        trouve = [a for a in self.r["klinische_beitraege"]["atomes"]
                  if "Nachwort (1920)" in a["texte"]]
        self.assertTrue(trouve, "le post-scriptum daté de 1920 a disparu du volume")
        self.assertIn("revision", trouve[0]["signaux_a_confirmer"])


class TestCooccurrenceParAuteur(unittest.TestCase):
    """L'entrée de Rank et d'Abraham a révélé un défaut d'architecture, et un test l'a signalé."""

    def test_cooccurrence_ne_melange_pas_les_auteurs(self):
        """Mesurer les cooccurrences sur le corpus entier produisait un classement où les couples
        de Le Bon, de Rank et de Freud se départageaient par leurs fréquences respectives — et le
        couple sadisme/masochisme de Freud en était sorti. Chaque fiche porte donc sur UN auteur."""
        corpus = Corpus()
        for auteur, attendu in [("Sigmund Freud", "traum"), (ABRAHAM, "libido")]:
            r = agents.AGENTS["cooccurrence"].executer(corpus, auteur=auteur)
            self.assertEqual(r["auteur"], auteur)
            siens = {c for m in lexique.pour_auteur(auteur).CONCEPTS.values() for c in m["termes"]}
            for lien in r["liens"]:
                for c in lien["concepts"]:
                    self.assertIn(c, siens, "%s : concept étranger dans ses cooccurrences" % auteur)


if __name__ == "__main__":
    unittest.main(verbosity=2)
