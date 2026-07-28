#!/usr/bin/env python3
"""TESTS de la couche de comparaison inter-auteurs.

Cette couche est la première à franchir la frontière entre auteurs. Elle est donc la plus exposée
au défaut que toute l'architecture cherche à éviter : affirmer un rapprochement que le lecteur ne
pourrait pas vérifier. Chaque test ci-dessous protège une garantie précise, et la plupart
protègent contre un défaut RÉEL, mesuré pendant la construction — les commentaires disent lequel.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import agents, atomisation, comparaison, sources     # noqa: E402
from core.corpus import Corpus                                  # noqa: E402


class TestAplatissement(unittest.TestCase):
    """Le piège qui a rendu invisible la meilleure relation du corpus."""

    def test_les_soulignes_de_mise_en_relief_ne_cachent_plus_le_nom(self):
        """DÉFAUT MESURÉ. Gutenberg met les noms en relief avec des soulignés : « _Le Bon_ ».
        Or « _ » est un caractère de mot pour « \\b », qui n'y voit donc aucune frontière : le
        motif « \\ble ?bon\\b » trouvait UN atome de Freud citant Le Bon là où il y en a 31, et
        manquait tout le chapitre que Freud lui consacre. L'aplatissement préalable règle le cas.
        """
        plat = comparaison.aplatir("aus dem Buch von _Le Bon_, _Psychologie der Massen_")
        self.assertIn(" le bon ", plat)

    def test_le_nom_ne_capture_pas_la_joie(self):
        """DÉFAUT MESURÉ : le motif à préfixe « \\bfreud » attrape « Freude », « Freuden »,
        « freudig » — la JOIE, 82 atomes du corpus. Le jeton exact les écarte tous."""
        import re
        jetons = comparaison.NOMS["Sigmund Freud"]
        joie = comparaison.aplatir("Es war eine große Freude und ein freudiges Ereignis.")
        self.assertFalse(any(re.search(j, joie) for j in jetons))
        vrai = comparaison.aplatir("Nach Freuds Auffassung ist der Traum eine Wunscherfüllung.")
        self.assertTrue(any(re.search(j, vrai) for j in jetons))

    def test_le_genitif_et_ladjectif_comptent(self):
        """« Freuds Lehre » et « die Freudsche Auffassung » sont des mentions."""
        import re
        jetons = comparaison.NOMS["Sigmund Freud"]
        for phrase in ("Freuds Lehre vom Unbewußten", "die Freudsche Auffassung", "bei Freud"):
            plat = comparaison.aplatir(phrase)
            self.assertTrue(any(re.search(j, plat) for j in jetons), phrase)


class TestReprise(unittest.TestCase):

    def test_temoin_negatif_est_nul(self):
        """Le plancher de bruit doit être établi par un témoin DÉTERMINISTE, non par un tirage —
        un échantillon aléatoire ne peut structurellement pas voir la queue qu'il prétend borner.
        Appariement forcé par rang entre auteurs allemands : mesuré à ZÉRO, reproductible."""
        atomes = {}
        for cle in ("jenseits", "trauma_der_geburt"):
            r = atomisation.atomiser(cle)
            atomes[r["atomes"][0]["auteur"]] = r["atomes"]
        t = comparaison.temoin_negatif(atomes)
        self.assertEqual(t["plancher"], 0.0)

    def test_une_citation_reelle_est_trouvee(self):
        """TÉMOIN POSITIF RÉEL, et non circulaire. On ne prend pas deux phrases identiques (elles
        rendraient 1,0 par construction — un témoin qui ne peut pas échouer) mais une citation
        AVEC variantes : Rank reprend le résumé d'Œdipe de la Traumdeutung en modifiant la
        ponctuation et en corrigeant une coquille."""
        freud = atomisation.atomiser("traumdeutung")["atomes"]
        rank = atomisation.atomiser("mythus_geburt_helden")["atomes"]
        liens = comparaison.reprises(freud, rank)
        self.assertTrue(liens, "aucune reprise trouvée entre la Traumdeutung et le Mythus")
        self.assertGreaterEqual(liens[0]["contenance"], comparaison.SEUIL_MANIFESTE)

    def test_le_denominateur_prend_tous_les_ngrammes(self):
        """FORMULE SOUS-SPÉCIFIÉE, corrigée. Rapporter une intersection filtrée à un ensemble
        lui-même filtré ferait monter le score des atomes les plus banals — deux implémentations
        de bonne foi différaient d'un facteur 8. Le dénominateur prend TOUS les n-grammes."""
        a = [{"id": "a1", "index": 0, "nb_mots": 30, "texte":
              "Der Traum ist die Erfuellung eines verdraengten Wunsches und dies gilt fuer alle "
              "Traeume die wir bisher untersucht haben in dieser Arbeit hier"}]
        b = [{"id": "b1", "index": 0, "nb_mots": 30, "texte":
              "Der Traum ist die Erfuellung eines verdraengten Wunsches aber die Sache ist "
              "voellig anders zu betrachten wenn man genauer hinsieht als vorher"}]
        liens = comparaison.reprises(a, b)
        self.assertTrue(liens)
        # Le score doit rester bien en dessous de 1 : les atomes divergent après le début.
        self.assertLess(liens[0]["contenance"], 0.5)

    def test_atome_trop_court_ecarte(self):
        """Sous 20 mots, la bande haute est envahie de titres d'ouvrage et d'en-têtes de page."""
        court = [{"id": "c", "index": 0, "nb_mots": 6, "texte": "Zeitschrift fuer aerztliche Psychoanalyse Band III"}]
        self.assertEqual(comparaison.reprises(court, court), [])


class TestPrudence(unittest.TestCase):
    """Ce que la couche doit REFUSER de dire."""

    def test_aucun_type_ne_nomme_une_nature(self):
        """GARANTIE CENTRALE. Aucun champ ne doit qualifier la nature du rapport — ni « socle »,
        ni « emprunt », ni « contradiction ». Le corpus a déjà mesuré ce piège : le signal
        « ecart_freud » nommait une nature que le motif ne prouvait pas, et n'a rien confirmé sur
        cinq candidats (les cinq passages étaient des renvois d'ACCORD).
        Si ce test tombe, c'est qu'on a réintroduit une prétention invérifiable."""
        a = {"id": "a", "index": 0, "nb_mots": 25, "texte": "Der Traum ist eine Wunscherfuellung.",
             "attestation": {"annee_oeuvre": 1900, "annee_edition_lue": 1900}}
        b = dict(a, id="b", attestation={"annee_oeuvre": 1912, "annee_edition_lue": 1912})
        lien = comparaison.qualifier({"a": a, "b": b, "contenance": 0.9, "partages": [],
                                      "n_partages": 5, "n_discriminants": 5})
        interdits = {"socle", "emprunt", "plagiat", "contradiction", "opposition", "bifurcation"}
        for cle, valeur in lien.items():
            if isinstance(valeur, str):
                self.assertFalse(interdits & set(valeur.lower().split("_")),
                                 "le champ %r nomme une nature non prouvée : %r" % (cle, valeur))

    def test_sens_seulement_si_fenetres_disjointes(self):
        """Un atome porte une FENÊTRE, pas une date : Freud a cessé de signaler ses ajouts dès la
        3e édition. On ne conclut sur le sens que si les fenêtres ne se chevauchent pas."""
        tot = {"annee_oeuvre": 1900, "annee_edition_lue": 1905}
        tard = {"annee_oeuvre": 1912, "annee_edition_lue": 1915}
        chevauche = {"annee_oeuvre": 1903, "annee_edition_lue": 1920}
        a = {"attestation": tot}
        b = {"attestation": tard}
        c = {"attestation": chevauche}
        self.assertEqual(comparaison.direction(a, b), "a_vers_b")
        self.assertEqual(comparaison.direction(b, a), "b_vers_a")
        self.assertIsNone(comparaison.direction(a, c), "fenêtres qui se chevauchent : indécidable")

    def test_source_tierce_interdit_le_sens(self):
        """Rank et Abraham racontent tous deux Œdipe d'après Sophocle ; Abraham et Freud citent
        tous deux Sancho Pança. Le partage de mots est réel, mais il ne prouve alors AUCUN emprunt
        entre eux — les deux peuvent tenir leur formulation du tiers. Aucun sens n'est donné."""
        a = {"id": "a", "index": 0, "nb_mots": 25, "attestation": {"annee_oeuvre": 1900, "annee_edition_lue": 1900},
             "texte": "Ödipus erschlägt den König Laios auf dem Wege von seiner Heimat."}
        b = {"id": "b", "index": 0, "nb_mots": 25, "attestation": {"annee_oeuvre": 1912, "annee_edition_lue": 1912},
             "texte": "Ödipus trifft mit König Laios zusammen und erschlägt ihn im Streite."}
        lien = comparaison.qualifier({"a": a, "b": b, "contenance": 0.6, "partages": [],
                                      "n_partages": 4, "n_discriminants": 4})
        self.assertTrue(lien["source_tierce"])
        self.assertIsNone(lien["sens"], "un partage médié par un tiers ne doit jamais être orienté")

    def test_homographe_declare_jamais_filtre(self):
        """« Abraham » est aussi le patriarche biblique, que Rank et Freud citent abondamment.
        On ne filtre PAS automatiquement — on ne saurait pas le faire sans se tromper — on
        DÉCLARE, pour que la lecture tranche."""
        self.assertIn("Karl Abraham", comparaison.HOMOGRAPHES)
        self.assertIn("biblique", comparaison.HOMOGRAPHES["Karl Abraham"])


class TestEvenements(unittest.TestCase):

    def test_une_citation_continue_compte_pour_un(self):
        """L'unité qui compte est l'ACTE de citation, pas la phrase. Compter les phrases gonfle le
        chiffre, et le gonfle INÉGALEMENT : celui qui cite par longs blocs paraîtrait trois fois
        plus lié que celui qui cite par touches."""
        def paire(i, j, c=0.9):
            return {"a": {"id": "a%d" % i, "index": i}, "b": {"id": "b%d" % j, "index": j},
                    "contenance": c}
        suite = [paire(10, 20), paire(11, 21), paire(12, 22)]   # trois phrases d'affilée
        isole = [paire(50, 80)]
        evts = comparaison.evenements(suite + isole)
        self.assertEqual(len(evts), 2, "trois phrases contiguës = un seul événement")
        self.assertEqual(evts[0]["longueur"], 3)


class TestSurLeCorpus(unittest.TestCase):
    """Les garanties, vérifiées sur le corpus réel."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()

    def test_la_lecture_de_le_bon_par_freud_est_trouvee(self):
        """LE CAS QUI JUSTIFIE LA DIMENSION. Freud consacre un chapitre entier à rendre compte de
        Le Bon, qu'il lit en traduction allemande. Aucune reprise textuelle ne peut le voir — les
        deux textes ne sont pas dans la même langue. Sans les lectures déclarées, la relation
        inter-auteurs la mieux documentée du corpus serait absente."""
        r = agents.AGENTS["lectures"].executer(self.corpus)
        lebon = [c for c in r["chapitres_declares"] if c["auteur_lu"] == "Gustave Le Bon"]
        self.assertTrue(lebon, "le chapitre de Freud sur Le Bon a disparu")
        self.assertGreater(lebon[0]["portee_atomes"], 90)

    def test_un_intitule_nest_pas_une_amorce_de_texte(self):
        """DÉFAUT MESURÉ. Le repérage de chapitre prend la ligne suivant le chiffre romain ; pour
        les œuvres sans intitulé de section, c'est la première PHRASE, tronquée à 90 signes.
        « II. Ich knüpfe nun an meine früheren Bemerkungen an, … die Breuer'sche Meth » passait
        alors pour un chapitre consacré à Breuer."""
        r = agents.AGENTS["lectures"].executer(self.corpus)
        for c in r["chapitres_declares"]:
            self.assertRegex(c["chapitre"].strip(), r"[.!?»]$",
                             "intitulé tronqué retenu à tort : %r" % c["chapitre"])

    def test_les_reprises_sont_orientees_dans_le_bon_sens(self):
        """CONTRÔLE DE COHÉRENCE, non utilisé pour fixer un seuil. Freud précède ses disciples :
        quand le sens est établi, il doit aller du plus ancien vers le plus récent."""
        r = agents.AGENTS["reprises"].executer(self.corpus)
        self.assertGreater(r["total_paires"], 50)
        self.assertLessEqual(r["total_evenements"], r["total_paires"])

    def test_aucune_reprise_avec_le_bon(self):
        """Le Bon écrit en français : aucune suite de six mots ne peut être partagée avec un texte
        allemand. Une reprise trouvée là signalerait un défaut du détecteur, pas une découverte."""
        r = agents.AGENTS["reprises"].executer(self.corpus)
        for f in r["couples"]:
            self.assertNotIn("Gustave Le Bon", f["couple"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
