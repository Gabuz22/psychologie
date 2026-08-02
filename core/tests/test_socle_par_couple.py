#!/usr/bin/env python3
"""TESTS du socle par couple — et de ce qu'il refuse de fusionner.

Deux fusions sont possibles ici, et toutes deux déjà interdites ailleurs dans ce projet : additionner
`actes_confirmes` et `mentions_confirmees` (le schéma D1 le dit en toutes lettres pour `mentions`),
et combiner l'axe 1 (liens vérifiés) avec l'axe 2 (densité comparée) en un score de « force »
(`donnees.js:RESERVE_DOSSIER`). Les tests protègent les deux, en plus des garanties habituelles
(seuls les verdicts confirmés comptent, le lexicographe voyage avec sa mesure, les couples sans
candidat restent visibles).
"""
import collections
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import socle_par_couple as spc          # noqa: E402


def _evt(a, b, verdict, concepts_communs=()):
    return {"auteur_a": a, "auteur_b": b, "verdict": verdict,
            "concepts_communs": list(concepts_communs)}


def _usage(sous_concept, motif, lexique, auteur, pour_mille):
    return {"sous_concept": sous_concept, "motif": motif, "lexique": lexique,
            "auteur": auteur, "pour_mille": pour_mille}


class TestActesConfirmesParConcept(unittest.TestCase):

    def test_seuls_les_actes_confirmes_comptent(self):
        evenements = [
            _evt("Freud", "Rank", "confirme", ["geburt"]),
            _evt("Freud", "Rank", "rejete", ["geburt"]),
            _evt("Freud", "Rank", "reclasse", ["geburt"]),
            _evt("Freud", "Rank", None, ["geburt"]),
        ]
        r = spc.actes_confirmes_par_concept(evenements)
        self.assertEqual(r[("Freud", "Rank")]["geburt"], 1)

    def test_le_poids_de_l_acte_n_est_jamais_compte(self):
        """Un acte qui couvre dix phrases ne vaut pas dix fois plus qu'un acte qui n'en couvre
        qu'une — sinon ce module referait, sous une autre forme, le produit croisé déjà mesuré
        et écarté dans `core/carte.py`."""
        evenements = [_evt("Freud", "Rank", "confirme", ["geburt", "mutter"])]
        r = spc.actes_confirmes_par_concept(evenements)
        self.assertEqual(r[("Freud", "Rank")]["geburt"], 1)
        self.assertEqual(r[("Freud", "Rank")]["mutter"], 1)

    def test_la_cle_du_couple_est_triee(self):
        r = spc.actes_confirmes_par_concept([_evt("Rank", "Abraham", "confirme", ["angst"])])
        self.assertIn(("Abraham", "Rank"), r)


class TestMentionsConfirmeesParConcept(unittest.TestCase):

    def test_seules_les_mentions_confirmees_comptent(self):
        """`mentions_confirmees` est déjà filtré par l'appelant : cette fonction ne sait rien
        d'un verdict, elle compte ce qu'on lui donne — le filtrage est vérifié côté appelant
        réel (bin/exporter_d1.py), pas ici."""
        concepts_par_atome = {"a1": {("pulsion", "libido")}}
        mentions = [{"auteur": "Ferenczi", "auteur_nomme": "Freud", "atome_id": "a1"}]
        r = spc.mentions_confirmees_par_concept(mentions, concepts_par_atome)
        self.assertEqual(r[("Ferenczi", "Freud")]["libido"], 1)

    def test_le_concept_vient_du_lexique_de_celui_qui_nomme(self):
        """`concepts_par_atome` porte les concepts de L'ATOME (donc du lexique de son auteur, celui
        qui nomme) — jamais ceux de la personne nommée, qui n'a rien écrit ici."""
        concepts_par_atome = {"a1": {("groupe", "trauma")}}
        mentions = [{"auteur": "Rank", "auteur_nomme": "Freud", "atome_id": "a1"}]
        r = spc.mentions_confirmees_par_concept(mentions, concepts_par_atome)
        self.assertEqual(set(r[("Freud", "Rank")]), {"trauma"})

    def test_un_atome_sans_concept_ne_plante_pas(self):
        r = spc.mentions_confirmees_par_concept(
            [{"auteur": "Rank", "auteur_nomme": "Freud", "atome_id": "inconnu"}], {})
        self.assertEqual(r[("Freud", "Rank")], collections.Counter())


class TestDensitesDuConcept(unittest.TestCase):

    def test_deux_lexiques_differents_du_meme_concept_ne_sont_pas_fusionnes(self):
        """Deux lexiques peuvent écrire le même NOM de concept avec des motifs regex différents :
        les fusionner ferait l'erreur que `socle.mot_partage` évite déjà en dédoublonnant sur le
        vecteur de densités, pas sur le nom."""
        usages = [
            _usage("angst", r"\b(angst)", "Sigmund Freud", "Sigmund Freud", 40.0),
            _usage("angst", r"\b(angst)", "Sigmund Freud", "Otto Rank", 30.0),
            _usage("angst", r"\b(angstneurose)", "Otto Rank", "Sigmund Freud", 2.0),
            _usage("angst", r"\b(angstneurose)", "Otto Rank", "Otto Rank", 90.0),
        ]
        r = spc.densites_du_concept(usages, "angst", "Sigmund Freud", "Otto Rank")
        self.assertEqual(len(r), 2)

    def test_le_lexicographe_est_signale(self):
        usages = [
            _usage("geburt", r"\b(geburt)", "Otto Rank", "Otto Rank", 77.0),
            _usage("geburt", r"\b(geburt)", "Otto Rank", "Sigmund Freud", 0.1),
        ]
        r = spc.densites_du_concept(usages, "geburt", "Sigmund Freud", "Otto Rank")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["lexicographe"], "b")
        self.assertEqual(r[0]["pour_mille_a"], 0.1)
        self.assertEqual(r[0]["pour_mille_b"], 77.0)

    def test_un_concept_sans_mesure_pour_la_paire_rend_une_liste_vide(self):
        usages = [_usage("angst", r"\b(angst)", "Sigmund Freud", "Wilhelm Stekel", 12.0)]
        r = spc.densites_du_concept(usages, "angst", "Sigmund Freud", "Otto Rank")
        self.assertEqual(r, [])

    def test_un_seul_auteur_mesure_reste_visible(self):
        """L'un des deux auteurs peut ne pas être mesurable (langue différente, corpus absent) —
        l'autre reste affiché plutôt que la ligne entière disparaître."""
        usages = [_usage("angst", r"\b(angst)", "Sigmund Freud", "Sigmund Freud", 12.0)]
        r = spc.densites_du_concept(usages, "angst", "Sigmund Freud", "Otto Rank")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["pour_mille_a"], 12.0)
        self.assertIsNone(r[0]["pour_mille_b"])


class TestCandidats(unittest.TestCase):

    def test_union_des_deux_axes_pas_intersection(self):
        """Un concept avec 0 acte mais une densité mesurée doit rester visible — sinon baisser le
        seuil de l'axe 1 à zéro ne le ferait jamais apparaître."""
        usages = [_usage("angst", r"\b(angst)", "Sigmund Freud", "Sigmund Freud", 12.0),
                  _usage("angst", r"\b(angst)", "Sigmund Freud", "Otto Rank", 8.0)]
        r = spc.candidats("Sigmund Freud", "Otto Rank",
                          collections.Counter(), collections.Counter(), usages)
        self.assertEqual([c["concept"] for c in r["concepts"]], ["angst"])
        self.assertEqual(r["concepts"][0]["actes_confirmes"], 0)

    def test_le_tri_met_le_plus_de_liens_verifies_en_tete(self):
        actes = collections.Counter({"a": 1, "b": 5})
        r = spc.candidats("Freud", "Rank", actes, collections.Counter(), [])
        self.assertEqual([c["concept"] for c in r["concepts"]], ["b", "a"])

    def test_actes_et_mentions_restent_deux_champs_separes(self):
        actes = collections.Counter({"trauma": 3})
        mentions = collections.Counter({"trauma": 960})
        r = spc.candidats("Ferenczi", "Freud", actes, mentions, [])
        c = r["concepts"][0]
        self.assertEqual(c["actes_confirmes"], 3)
        self.assertEqual(c["mentions_confirmees"], 960)
        # Aucun champ combiné (ni "liens", ni "total", ni la somme 963) n'est jamais rendu.
        self.assertEqual(set(c) - {"concept"}, {"actes_confirmes", "mentions_confirmees",
                                                "densites"})


class TestToutesLesPaires(unittest.TestCase):

    def test_les_couples_sans_candidat_restent_visibles_avec_leur_silence(self):
        """Même discipline que `carte.couples` : un couple qu'on tait présente un aveuglement de
        méthode comme un fait de corpus."""
        r = spc.toutes_les_paires([], [], {}, [],
                                  auteurs=["Sigmund Freud", "Gustave Le Bon", "Otto Rank"],
                                  langues={"Sigmund Freud": "de", "Gustave Le Bon": "fr",
                                          "Otto Rank": "de"})
        par_paire = {(c["auteur_a"], c["auteur_b"]): c["silence"] for c in r}
        self.assertEqual(par_paire[("Gustave Le Bon", "Sigmund Freud")], "langues")
        self.assertEqual(par_paire[("Otto Rank", "Sigmund Freud")], "aucun_candidat")

    def test_un_couple_avec_un_acte_confirme_n_a_pas_de_silence(self):
        evenements = [_evt("Sigmund Freud", "Otto Rank", "confirme", ["geburt"])]
        r = spc.toutes_les_paires(evenements, [], {}, [],
                                  auteurs=["Sigmund Freud", "Otto Rank"],
                                  langues={"Sigmund Freud": "de", "Otto Rank": "de"})
        self.assertIsNone(r[0]["silence"])


class TestPrudence(unittest.TestCase):

    def test_aucun_champ_ne_combine_les_deux_axes(self):
        """Ni ici ni dans une future extension : aucune clé numérique ne doit s'appeler `force`,
        `score`, `solidite` ou `socle` — la garantie porte sur le NOM du champ, pas seulement sur
        sa valeur, parce que la tentation de nommer une synthèse est ce que ce module existe pour
        refuser."""
        usages = [_usage("angst", r"\b(angst)", "Sigmund Freud", "Sigmund Freud", 12.0),
                  _usage("angst", r"\b(angst)", "Sigmund Freud", "Otto Rank", 8.0)]
        actes = collections.Counter({"angst": 2})
        r = spc.candidats("Sigmund Freud", "Otto Rank", actes, collections.Counter(), usages)
        interdits = {"force", "score", "solidite", "socle"}
        for c in r["concepts"]:
            for cle, valeur in c.items():
                if isinstance(valeur, (int, float)):
                    self.assertNotIn(cle, interdits,
                                     "le champ %r combine ce que ce module refuse de fusionner" % cle)

    def test_la_reserve_porte_le_refus_de_fusion(self):
        r = spc.reserve()
        for attendu in ("JAMAIS", "actes_confirmes", "mentions_confirmees", "densites", "960", "9"):
            self.assertIn(attendu, r, "réserve incomplète : %s" % attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
