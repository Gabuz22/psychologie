#!/usr/bin/env python3
"""TESTS des branches et dérivations — et du négatif qui a fait changer la méthode.

Ce module a d'abord été écrit pour comparer les auteurs entre eux ; la mesure n'a rien donné après
contrôles, et l'axe a été déplacé vers la chronologie interne de chaque œuvre. Les tests ci-dessous
protègent les deux choses : que le négatif reste calculable (un résultat négatif non conservé se
refait) et que la chronologie garde les garde-fous qui la rendent défendable.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import branches          # noqa: E402


def _o(cle, annee, atomes, porteurs):
    return {"cle": cle, "annee": annee, "atomes": atomes, "porteurs": porteurs}


class TestTrajectoire(unittest.TestCase):

    def test_un_vocabulaire_qui_APPARAIT_est_reconnu(self):
        """LE CAS RÉEL QUE LA MESURE DOIT RETROUVER : `es` et `ueberich` n'existent pas chez Freud
        avant « Das Ich und das Es » (1923). C'est le tournant structural, et il se voit."""
        t = branches.trajectoire(r"\b(es)", [
            _o("traumdeutung", 1900, 3000, 1), _o("witz", 1905, 1200, 0),
            _o("totem", 1913, 1500, 2), _o("jenseits", 1920, 600, 8),
            _o("ich_und_es", 1923, 560, 90), _o("neue_folge", 1933, 2000, 40)])
        self.assertEqual(t["classe"], "apparait")
        self.assertGreater(t["pour_mille_apres"], t["pour_mille_avant"])

    def test_un_vocabulaire_qui_DISPARAIT_est_reconnu(self):
        """AUTRE CAS RÉEL : `hypnoid` — la théorie des états hypnoïdes empruntée à Breuer —
        disparaît de Freud après les « Studien über Hysterie ». C'est la rupture, et elle est
        lexicale."""
        t = branches.trajectoire(r"\b(hypnoid)", [
            _o("studien_ueber_hysterie", 1895, 1000, 26),
            _o("traumdeutung", 1900, 3000, 2), _o("witz", 1905, 1200, 1),
            _o("totem", 1913, 1500, 0), _o("jenseits", 1920, 600, 0)])
        # LE PIÈGE QUE CE CAS A RÉVÉLÉ : 26 des 29 occurrences sont dans une seule œuvre, donc la
        # concentration seule le classerait « livre unique » — et l'histoire serait perdue. Ce qui
        # tranche, c'est que cette œuvre est la PREMIÈRE.
        self.assertGreaterEqual(t["part_dominante"], branches.PART_LIVRE_UNIQUE)
        self.assertEqual(t["classe"], "disparait")

    def test_un_vocabulaire_d_UN_SEUL_LIVRE_n_est_pas_attribue_a_l_auteur(self):
        """`geburtstrauma` pèse 121,6 ‰ dans le « Trauma der Geburt » de Rank et 0 ‰ dans tout le
        reste de son œuvre. Dire « Rank diverge » surinterprète : le mot est le vocabulaire de CE
        LIVRE. La classe le dit, au lieu de laisser croire à un trait d'auteur."""
        t = branches.trajectoire(r"\b(geburtstrauma)", [
            _o("kuenstler", 1907, 800, 0), _o("mythus", 1909, 1200, 0),
            _o("lohengrin", 1911, 900, 0), _o("trauma_der_geburt", 1924, 1000, 120),
            _o("genetische_2", 1928, 700, 0)])
        self.assertEqual(t["classe"], "livre_unique")
        self.assertGreaterEqual(t["part_dominante"], branches.PART_LIVRE_UNIQUE)

    def test_une_oeuvre_MINUSCULE_ne_peut_pas_emporter_la_mesure(self):
        """DÉFAUT MESURÉ SUR LE CORPUS RÉEL. Il contient une « œuvre » de Freud de CINQ atomes —
        sa préface aux « Nervöse Angstzustände » de Stekel. Une seule occurrence y vaut 200 ‰ et
        raflait le maximum de n'importe quel motif : le classement était dominé par un accident
        d'échantillon."""
        avec = branches.trajectoire(r"\b(x)", [
            _o("grand_1", 1900, 3000, 30), _o("grand_2", 1910, 3000, 30),
            _o("grand_3", 1920, 3000, 30), _o("preface_minuscule", 1908, 5, 4)])
        self.assertNotEqual(avec["oeuvre_dominante"], "preface_minuscule")
        self.assertEqual(avec["oeuvres_mesurees"], 3, "l'œuvre de 5 atomes doit être écartée")

    def test_un_motif_trop_rare_ne_produit_PAS_de_trajectoire(self):
        """Trois occurrences dans une œuvre ne dessinent pas une trajectoire. Mieux vaut ne rien
        rendre qu'un classement que le hasard aurait pu produire."""
        self.assertIsNone(branches.trajectoire(r"\b(rare)", [
            _o("a", 1900, 3000, 1), _o("b", 1910, 3000, 1), _o("c", 1920, 3000, 1)]))

    def test_moins_de_trois_oeuvres_ne_produit_PAS_de_trajectoire(self):
        """Une trajectoire demande un avant et un après. Deux points font une droite, pas une
        histoire — et Breuer, Le Bon n'ont qu'une œuvre chacun."""
        self.assertIsNone(branches.trajectoire(r"\b(x)", [
            _o("a", 1895, 900, 60), _o("b", 1900, 900, 5)]))


class TestReprisePosterieure(unittest.TestCase):

    def test_un_rameau_que_PERSONNE_ne_reprend_est_signale_comme_tel(self):
        """LE RÉSULTAT UTILE EST L'ABSENCE. Un vocabulaire qu'un auteur introduit et que personne
        ne reprend est une branche qui n'a pas pris — et le corpus en compte bien plus que
        l'inverse."""
        r = branches.reprise_posterieure(r"\b(amphimixis)", {
            "Sándor Ferenczi": [_o("genitaltheorie", 1924, 900, 41)],
            "Sigmund Freud": [_o("traumdeutung", 1900, 3000, 0)],
        })
        self.assertEqual(r["premier"], "Sándor Ferenczi")
        self.assertEqual(r["repreneurs"], [])
        self.assertTrue(r["rameau_isole"])

    def test_UNE_occurrence_isolee_ne_fait_pas_un_repreneur(self):
        """DÉFAUT MESURÉ SUR LE PREMIER DOCUMENT PRODUIT. Sans seuil d'emploi, une seule
        occurrence chez un autre auteur suffisait à transformer un vocabulaire propre en
        vocabulaire repris — et le corpus est océrisé, donc une occurrence isolée peut n'être
        qu'une coquille. Le document annonçait 7 rameaux isolés là où 36 motifs ne sont
        réellement employés que par un seul auteur : le résultat de la section était effacé."""
        r = branches.reprise_posterieure(r"\b(amphimixis)", {
            "Sándor Ferenczi": [_o("genitaltheorie", 1924, 900, 41)],
            # Une occurrence sur 20 000 atomes = 0,05 ‰ : ce n'est pas un emploi.
            "Sigmund Freud": [_o("neue_folge", 1933, 20000, 1)],
        })
        self.assertEqual(r["repreneurs"], [])
        self.assertTrue(r["rameau_isole"])

    def test_une_reprise_posterieure_est_distinguee_d_une_SIMULTANEITE(self):
        """CAS RÉEL DU CORPUS, ET IL INTERDIT DE CONCLURE : le « Trauma der Geburt » de Rank et la
        « Genitaltheorie » de Ferenczi partagent leur vocabulaire central et paraissent tous deux
        en 1924. Deux livres de la même année ne s'ordonnent pas — les compter comme une reprise
        fabriquerait une filiation que rien n'établit."""
        r = branches.reprise_posterieure(r"\b(mutterleib)", {
            "Otto Rank": [_o("trauma_der_geburt", 1924, 1000, 70)],
            "Sándor Ferenczi": [_o("genitaltheorie", 1924, 900, 60)],
            "Sigmund Freud": [_o("neue_folge", 1933, 2000, 12)],
        })
        self.assertIn("Sándor Ferenczi", r["simultanes"])
        self.assertNotIn("Sándor Ferenczi", r["repreneurs"])
        self.assertIn("Sigmund Freud", r["repreneurs"])
        self.assertFalse(r["rameau_isole"])


class TestDedoublonnage(unittest.TestCase):

    def test_deux_ecritures_du_meme_concept_ne_comptent_qu_une_fois(self):
        """DÉFAUT MESURÉ SUR LE PREMIER DOCUMENT PRODUIT. Les lexiques écrivent le même concept
        autrement — `identifizier`, `identifizierung|identifizier` — et les deux retiennent les
        mêmes phrases. Le tableau montrait trois fois « identifizier » et trois fois « traum » sur
        quatorze lignes : ce n'est pas un défaut d'affichage, c'est un compte faux."""
        t = {"classe": "apparait", "oeuvre_dominante": "genetische_2", "part_dominante": 0.5,
             "pour_mille_avant": 5.3, "pour_mille_apres": 21.5, "occurrences": 60}
        trajectoires = [
            ("Otto Rank", dict(t, motif=r"\b(identifizierung|identifizier)")),
            ("Otto Rank", dict(t, motif=r"\b(identifizier)")),
            ("Otto Rank", dict(t, motif=r"\b(identifizierung|identifiziert)")),
        ]
        uniques = branches.dedoublonner(trajectoires)
        self.assertEqual(len(uniques), 1)
        # Le motif le plus court est retenu, pour que le choix ne dépende pas de l'ordre des
        # lexiques.
        self.assertEqual(uniques[0][1]["motif"], r"\b(identifizier)")

    def test_le_meme_motif_chez_DEUX_auteurs_reste_deux_trajectoires(self):
        """Le dédoublonnage ne doit pas fusionner deux auteurs : c'est l'auteur qui fait la
        trajectoire, et le même mot peut se déplacer différemment chez chacun."""
        t = {"motif": r"\b(angst)", "classe": "apparait", "oeuvre_dominante": "x",
             "part_dominante": 0.5, "pour_mille_avant": 5.0, "pour_mille_apres": 20.0,
             "occurrences": 60}
        self.assertEqual(len(branches.dedoublonner(
            [("Otto Rank", dict(t)), ("Sigmund Freud", dict(t))])), 2)


class TestSignatureNegative(unittest.TestCase):
    """LE NÉGATIF, CONSERVÉ PARCE QU'IL A FAIT CHANGER LA MÉTHODE."""

    def test_une_signature_sur_son_PROPRE_lexique_ne_survit_pas(self):
        """Le motif `amphimixis` a été écrit POUR Ferenczi, dans le lexique de Ferenczi. Qu'il y
        domine n'établit rien : c'est vrai par construction. 31 des 35 signatures du corpus sont
        dans ce cas, et les publier ferait passer un choix de lexicographe pour un trait d'auteur.
        """
        r = branches.signature_apres_controles(
            {r"\b(amphimixis)": {"Sándor Ferenczi": (3.8, 35), "Sigmund Freud": (0.0, 0)}},
            {r"\b(amphimixis)": "Sándor Ferenczi"},
            {"Sándor Ferenczi": (9158, 5), "Sigmund Freud": (40276, 35)})
        self.assertEqual(r["brutes"], 1)
        self.assertEqual(r["apres_controle_du_lexique"], 0)

    def test_une_signature_portee_par_un_corpus_d_UNE_SEULE_OEUVRE_ne_survit_pas(self):
        """Les 4 signatures du corpus qui passaient le contrôle de lexique venaient TOUTES de
        Josef Breuer — 885 atomes, une seule œuvre. C'est le double artefact (petit corpus, livre
        unique) qui avait déjà fait confirmer sept fausses divergences."""
        r = branches.signature_apres_controles(
            {r"\b(hypnoid)": {"Josef Breuer": (30.5, 27), "Sigmund Freud": (1.4, 57)}},
            {r"\b(hypnoid)": "Sigmund Freud"},
            {"Josef Breuer": (885, 1), "Sigmund Freud": (40276, 35)})
        self.assertEqual(r["apres_controle_du_lexique"], 1, "elle doit passer le premier contrôle")
        self.assertEqual(r["apres_controle_du_corpus"], 0, "et tomber au second")

    def test_une_signature_reellement_informative_survivrait(self):
        """Le filtre n'est pas un refus de principe : une signature sur le motif d'un autre, portée
        par un auteur au corpus large et varié, passerait. Le corpus n'en contient aucune — c'est
        un fait mesuré sur lui, pas une impossibilité de la méthode."""
        r = branches.signature_apres_controles(
            {r"\b(libido)": {"Karl Abraham": (36.5, 275), "Sigmund Freud": (1.0, 40)}},
            {r"\b(libido)": "Sigmund Freud"},
            {"Karl Abraham": (7543, 5), "Sigmund Freud": (40276, 35), "Josef Breuer": (885, 1)})
        self.assertEqual(r["apres_controle_du_corpus"], 1)
        self.assertEqual(r["survivantes"][0]["auteur"], "Karl Abraham")


class TestPrudence(unittest.TestCase):

    def test_aucune_classe_ne_nomme_une_intention(self):
        """MÊME GARANTIE QUE `comparaison.qualifier` ET `socle`. Une trajectoire décrit un
        vocabulaire dans le temps ; elle ne dit ni rupture, ni reniement, ni changement d'avis —
        le corpus a mesuré qu'un renversement doctrinal ne laisse presque aucune trace lexicale de
        première personne (deux révisions confirmées sur 74 signaux chez Ferenczi)."""
        interdits = {"rupture", "reniement", "abandon", "revision", "contradiction", "opposition",
                     "bifurcation", "influence", "emprunt"}
        t = branches.trajectoire(r"\b(x)", [
            _o("a", 1900, 3000, 30), _o("b", 1910, 3000, 3), _o("c", 1920, 3000, 1)])
        for cle, valeur in t.items():
            if isinstance(valeur, str):
                self.assertFalse(interdits & set(valeur.lower().split("_")),
                                 "le champ %r nomme une intention : %r" % (cle, valeur))

    def test_la_reserve_porte_le_negatif_et_la_fenetre_de_datation(self):
        """Les deux choses qu'un lecteur pressé prendrait de travers : que la comparaison entre
        auteurs a échoué, et qu'une date d'œuvre n'est pas une date d'écriture."""
        r = branches.reserve()
        for attendu in ("35", "31", "885", "0 confirmé sur 5", "1 sur 16", "FENÊTRE",
                        "jamais des changements d'avis"):
            self.assertIn(attendu, r, "réserve incomplète : %s" % attendu)


class TestDocumentGenere(unittest.TestCase):

    def _doc(self):
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        chemin = os.path.join(racine, "documentation", "BRANCHES_ET_DERIVATIONS.md")
        self.assertTrue(os.path.exists(chemin), "document non généré : bin/generer_branches.py")
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def test_le_document_se_declare_genere(self):
        self.assertIn("**DOCUMENT GÉNÉRÉ**", self._doc())

    def test_le_document_PUBLIE_le_negatif_au_lieu_de_le_taire(self):
        """C'est la raison d'être du document. Une méthode essayée et abandonnée dont on ne publie
        que la version qui marche laisse le prochain refaire la mauvaise — et ce dépôt en est déjà
        à trois échecs du même ordre."""
        texte = self._doc()
        for attendu in ("ecart_freud", "sur seize", "885", "propre lexique"):
            self.assertIn(attendu, texte, "le négatif a été perdu : %s" % attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
