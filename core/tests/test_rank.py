#!/usr/bin/env python3
"""TESTS d'Otto Rank — premier auteur doté de SON PROPRE lexique, et première source OCRisée.

Deux garanties nouvelles à protéger :
  1. LES LEXIQUES SONT ÉTANCHES. Chaque auteur est décrit avec ses catégories, jamais avec
     celles d'un autre. C'est la règle fondatrice posée le 2026-07-28, qui RENVERSE la règle
     antérieure du projet — un test doit donc empêcher qu'on la rétablisse par inadvertance.
  2. UN FAC-SIMILÉ N'EST PAS UNE TRANSCRIPTION. Le corpus accepte désormais de l'OCR non relu,
     faute d'alternative pour cet auteur, mais à une condition stricte : la qualité est mesurée,
     les défauts réparables sont réparés, et ce qui reste douteux est marqué.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import atomisation, lexique, lexiques, ocr, sources     # noqa: E402

RANK = "Otto Rank"
OEUVRES_RANK = ["mythus_geburt_helden", "lohengrinsage", "inzest_motiv",
                "trauma_der_geburt", "genetische_psychologie_2"]


class TestEtancheiteDesLexiques(unittest.TestCase):
    """La règle fondatrice : un auteur n'est jamais décrit avec la grille d'un autre."""

    def test_concept_signature_absent_ailleurs(self):
        """`aussetzung` — l'enfant exposé sauvé des eaux — est LE motif de Rank, et n'a aucune
        case chez Freud. Sans lexique séparé, il serait purement invisible."""
        phrase = "Der ausgesetzte Knabe wird aus dem Wasser gerettet."
        self.assertIn("aussetzung", {c["concept"] for c in lexique.concepts_de(phrase, RANK)})
        self.assertNotIn("aussetzung",
                         {c["concept"] for c in lexique.concepts_de(phrase, "Sigmund Freud")})

    def test_aucun_concept_emprunte_a_freud(self):
        """Les tables sont des objets DISTINCTS, jamais partagés ni importés l'un dans l'autre.

        Un recouvrement de NOMS reste permis et attendu — les deux auteurs parlent de refoulement,
        et un groupe « cure » existe chez l'un comme chez l'autre. Ce qui est interdit, c'est que
        les deux lexiques soient le même objet : c'est cela qui rendrait un cumul possible par
        accident. Le test vérifie donc l'identité des objets et la divergence du CONTENU, pas une
        disjonction des noms qui n'aurait aucun sens.
        """
        rank = lexiques.PAR_AUTEUR[RANK].CONCEPTS
        self.assertIsNot(rank, lexique.CONCEPTS)
        for groupe in set(rank) & set(lexique.CONCEPTS):
            self.assertIsNot(rank[groupe], lexique.CONCEPTS[groupe])
            self.assertNotEqual(set(rank[groupe]["termes"]),
                                set(lexique.CONCEPTS[groupe]["termes"]),
                                "le groupe « %s » est identique chez les deux auteurs" % groupe)

    def test_trois_auteurs_trois_grilles(self):
        """La même phrase allemande n'est pas lue pareil selon l'auteur — c'est le but."""
        phrase = "Die Geburt des Helden vollzieht sich im Wasser."
        chez_rank = {c["concept"] for c in lexique.concepts_de(phrase, RANK)}
        chez_freud = {c["concept"] for c in lexique.concepts_de(phrase, "Sigmund Freud")}
        self.assertIn("geburt", chez_rank)
        self.assertIn("held", chez_rank)
        self.assertNotIn("geburt", chez_freud)      # Freud n'a pas thématisé la naissance

    def test_fonction_propre_a_rank(self):
        """« comparaison » est le geste de Rank (aligner les versions d'un même récit), comme
        l'association libre est celui de Freud. Elle n'existe que dans son lexique."""
        etablies, _ = lexique.fonctions_par_fiabilite(
            "Eine ähnliche Fassung der Sage findet sich bei den Babyloniern.", RANK)
        self.assertIn("comparaison", etablies)
        self.assertNotIn("comparaison", [f["id"] for f in lexique.FONCTIONS])

    def test_einwanderung_nest_pas_une_objection(self):
        """PIÈGE MESURÉ : « vor der dorischen Einwanderung » (la migration dorienne) était compté
        comme une objection. L'exclusion héritée de Freud ne couvrait que le VERBE einwandern."""
        _, a_confirmer = lexique.fonctions_par_fiabilite(
            "Der Kult hatte schon vor der dorischen Einwanderung Heimatrecht.", RANK)
        self.assertNotIn("objection", a_confirmer)
        _, vrai = lexique.fonctions_par_fiabilite(
            "Ein zweiter Einwand wird sich gegen unsere Auffassung erheben.", RANK)
        self.assertIn("objection", vrai)


class TestQualiteOCR(unittest.TestCase):
    """Un fac-similé entre au corpus MESURÉ, jamais sur parole."""

    def test_corruption_ch_disqualifie(self):
        """Les deux défauts qui ont fait écarter deux volumes de Rank, chacun sur son motif."""
        di = ocr.corruption("Das ist nidit die Persönlidikeit der Geistes" + "wissensdiaften. "
                            "Er sagte nidit viel. Sie war nidit da. Es war nidit so.")
        self.assertGreater(di["taux_mots_pct"], 50)
        h = ocr.corruption("Er hat sih geirrt und auh niht verstanden, was noh zu tun war. "
                           "Das ist natürlih so gewesen bei ihm.")
        self.assertGreater(h["taux_phrases_pct"], 50)
        sain = ocr.corruption("Er hat sich geirrt und auch nicht verstanden, was noch zu tun war.")
        self.assertEqual(sain["taux_phrases_pct"], 0.0)

    def test_toutes_les_oeuvres_sous_le_seuil(self):
        """Les cinq œuvres admises restent sous le seuil de phrases corrompues. Si l'une le
        dépasse un jour, c'est qu'une source a été remplacée : il faut le savoir aussitôt."""
        for cle in OEUVRES_RANK:
            c = ocr.corruption(sources.charger(cle)["texte"])
            self.assertLess(c["taux_phrases_pct"], ocr.SEUIL_PHRASES_CORROMPUES_PCT,
                            "%s : %s %% de phrases corrompues" % (cle, c["taux_phrases_pct"]))

    def test_recollage_des_cesures(self):
        """L'OCR laisse les mots coupés en fin de ligne ; les relecteurs humains, non."""
        # « Entstehung » est dans le vocabulaire de référence, « Brautgemach » non : le premier
        # est recollé sur PREUVE, le second sur la règle d'orthographe allemande. Les deux
        # degrés sont comptés séparément pour que le lecteur sache lequel a joué.
        voc = {"entstehung"}
        net, rap = ocr.recoller_cesures("Die Ent-\nstehung des Brautge-\nmach ist alt.", voc)
        self.assertIn("Entstehung", net)
        self.assertIn("Brautgemach", net)
        self.assertEqual(rap["cesures_recollees_attestees"], 1)
        self.assertEqual(rap["cesures_recollees_par_regle"], 1)

    def test_elision_jamais_soudee(self):
        """« Kunst- und Wissenschaft » : le trait d'union marque une ÉLISION, pas une coupure.
        Le souder produirait « Kunstund », un mot qui n'existe pas."""
        net, rap = ocr.recoller_cesures("Er sprach über Kunst-\nund Wissenschaft.", set())
        self.assertIn("Kunst-", net)
        self.assertEqual(rap["cesures_laissees"], 1)

    def test_composition_jamais_soudee(self):
        """« Über-Ich » porte un vrai trait d'union : le souder détruirait le surmoi."""
        net, _ = ocr.recoller_cesures("Das Über-\nIch ist streng.", {"überich"})
        self.assertIn("Über-", net)

    def test_blocs_illisibles_ne_mangent_pas_la_prose(self):
        """GARANTIE LA PLUS IMPORTANTE de la couche OCR : le nettoyage ne doit JAMAIS retirer du
        texte réel. Une ligne isolée mal notée reste ; seules les pages de garde partent."""
        voc = ocr.vocabulaire_de_reference([sources.charger("gradiva")["texte"]])
        prose = sources.charger("gradiva")["texte"][20000:40000]
        net, rap = ocr.retirer_blocs_illisibles(prose, voc)
        self.assertEqual(rap["lignes_retirees"], 0)

    def test_rognage_ne_coupe_pas_dans_la_prose(self):
        voc = ocr.vocabulaire_de_reference([sources.charger("gradiva")["texte"]])
        prose = sources.charger("gradiva")["texte"][20000:40000]
        net, _ = ocr.rogner_aux_extremites(prose, voc)
        self.assertGreater(len(net), 0.95 * len(prose))


class TestOeuvresDeRank(unittest.TestCase):
    """Les cinq volumes, de bout en bout."""

    @classmethod
    def setUpClass(cls):
        cls.r = {c: atomisation.atomiser(c) for c in OEUVRES_RANK}

    def test_integrite(self):
        for cle, r in self.r.items():
            self.assertTrue(r["controles"]["recomposition_ordre_ok"], cle)
            self.assertTrue(r["controles"]["localisation_complete"], cle)

    def test_auteur_et_lexique(self):
        for cle, r in self.r.items():
            self.assertEqual(set(r["controles"]["par_auteur"]), {RANK}, cle)
            # Les concepts trouvés appartiennent tous au lexique de Rank, jamais à un autre.
            siens = {c for m in lexiques.PAR_AUTEUR[RANK].CONCEPTS.values() for c in m["termes"]}
            for a in r["atomes"][:400]:
                for c in a["concepts"]:
                    self.assertIn(c["concept"], siens, "%s : concept étranger" % cle)

    def test_datation_certaine(self):
        """Les cinq volumes sont des PREMIÈRES ÉDITIONS — situation plus favorable que pour
        Freud, dont la plupart des textes sont lus dans une édition tardive."""
        for cle, r in self.r.items():
            self.assertTrue(all(a["attestation"]["precise"] for a in r["atomes"]), cle)

    def test_liminaires_du_facsimile_retires(self):
        """Le charabia des couvertures numérisées ne doit produire aucun atome. Sans ce
        nettoyage, le premier atome du Doppelgänger aurait été « Okto Rank »."""
        premier = self.r["mythus_geburt_helden"]["atomes"][0]["texte"]
        self.assertTrue(premier.startswith("Die vorliegende Arbeit"))
        dernier = self.r["genetische_psychologie_2"]["atomes"][-1]["texte"]
        self.assertNotIn("Preis M", dernier)

    def test_signature_thematique(self):
        """Sans rien savoir du contenu, le lexique doit retrouver l'objet de chaque livre.
        C'est le signal de validation employé depuis le début du projet."""
        def concepts(cle):
            c = {}
            for a in self.r[cle]["atomes"]:
                for x in a["concepts"]:
                    c[x["concept"]] = c.get(x["concept"], 0) + 1
            return c
        # « Das Trauma der Geburt » doit parler de naissance plus que tout autre volume.
        part = {cle: concepts(cle).get("geburt", 0) / len(self.r[cle]["atomes"])
                for cle in OEUVRES_RANK}
        self.assertEqual(max(part, key=part.get), "trauma_der_geburt")
        # Le « Mythus von der Geburt des Helden » doit être le plus dense en exposition du héros.
        aus = {cle: concepts(cle).get("aussetzung", 0) / len(self.r[cle]["atomes"])
               for cle in OEUVRES_RANK}
        self.assertEqual(max(aus, key=aus.get), "mythus_geburt_helden")


if __name__ == "__main__":
    unittest.main(verbosity=2)
