#!/usr/bin/env python3
"""TESTS des candidats de divergence — et de ce qu'ils s'interdisent d'affirmer.

Ce module est un GÉNÉRATEUR DE CANDIDATS, pas un quatrième détecteur automatique sur un terrain où
trois ont déjà échoué (ecart_freud 0/5, appariement 1/16, signature lexicale 0/35). Les tests
protègent la seule chose que ce module a le droit de faire : croiser un lien déjà vérifié avec une
trajectoire déjà mesurée, sans jamais transformer ce croisement en verdict.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import divergences          # noqa: E402


def _traj(classe, oeuvre="livre", annee=1920, part=0.8, avant=1.0, apres=20.0, occurrences=100):
    return {"classe": classe, "oeuvre_dominante": oeuvre, "annee_dominante": annee,
            "part_dominante": part, "pour_mille_avant": avant, "pour_mille_apres": apres,
            "occurrences": occurrences}


class TestCandidats(unittest.TestCase):

    def test_seules_apparait_et_disparait_produisent_un_candidat(self):
        """« constant » ne bouge pas — rien à lire. « livre_unique » n'a pas de direction propre,
        `branches.trajectoire` le distingue déjà d'une vraie apparition ou disparition."""
        trajectoires = {"Otto Rank": [
            ("geburtstrauma", _traj("apparait")),
            ("vater", _traj("constant")),
            ("mutter", _traj("livre_unique")),
            ("kind", _traj("disparait")),
        ]}
        touches = {("Otto Rank", s): {"Sigmund Freud"} for s in ("geburtstrauma", "vater",
                                                                  "mutter", "kind")}
        r = divergences.candidats(trajectoires, touches)
        classes = {c["concept"]: c["classe"] for c in r}
        self.assertEqual(set(classes), {"geburtstrauma", "kind"})

    def test_sans_lien_verifie_pas_de_candidat_meme_avec_une_vraie_trajectoire(self):
        """Le premier ingrédient est aussi obligatoire que le second : une trajectoire seule,
        c'est `branches.py`, déjà fait, déjà publié. Ce module n'ajoute que le croisement."""
        trajectoires = {"Otto Rank": [("geburtstrauma", _traj("apparait"))]}
        r = divergences.candidats(trajectoires, touches={})
        self.assertEqual(r, [])

    def test_chaque_candidat_dit_AVEC_QUI_il_est_lie(self):
        trajectoires = {"Otto Rank": [("geburtstrauma", _traj("apparait"))]}
        touches = {("Otto Rank", "geburtstrauma"): {"Sigmund Freud", "Karl Abraham"}}
        r = divergences.candidats(trajectoires, touches)
        self.assertEqual(r[0]["lie_a"], ["Karl Abraham", "Sigmund Freud"])

    def test_deux_ecritures_du_meme_sous_concept_ne_comptent_qu_une_fois(self):
        """Même défaut que celui déjà mesuré et corrigé dans `branches.dedoublonner` : deux
        lexiques peuvent nommer le même concept différemment (« identifizier » vs
        « identifizierung ») tout en sélectionnant EXACTEMENT les mêmes phrases — la trajectoire
        calculée est alors identique dans toutes ses valeurs, seul le nom diffère."""
        meme_trajectoire = _traj("apparait", oeuvre="genetische_psychologie_2", part=0.53,
                                 avant=5.3, apres=21.5)
        trajectoires = {"Otto Rank": [
            ("identifizier", meme_trajectoire),
            ("identifizierung", dict(meme_trajectoire)),   # même mesure, nom différent
        ]}
        touches = {("Otto Rank", "identifizier"): {"Sigmund Freud"},
                   ("Otto Rank", "identifizierung"): {"Sigmund Freud"}}
        r = divergences.candidats(trajectoires, touches)
        self.assertEqual(len(r), 1)

    def test_deux_concepts_qui_se_ressemblent_mais_diffèrent_vraiment_restent_distincts(self):
        """Le dédoublonnage porte sur la VALEUR, pas seulement le nom : deux concepts au nom
        proche mais à la trajectoire réellement différente ne doivent jamais fusionner."""
        trajectoires = {"Otto Rank": [
            ("angst", _traj("apparait", oeuvre="a", part=0.9, avant=1.0, apres=50.0)),
            ("angstneurose", _traj("disparait", oeuvre="b", part=0.7, avant=30.0, apres=2.0)),
        ]}
        touches = {("Otto Rank", "angst"): {"Sigmund Freud"},
                   ("Otto Rank", "angstneurose"): {"Sigmund Freud"}}
        r = divergences.candidats(trajectoires, touches)
        self.assertEqual(len(r), 2)

    def test_le_tri_met_la_concentration_la_plus_forte_en_tete(self):
        trajectoires = {"Otto Rank": [
            ("a", _traj("apparait", part=0.3)), ("b", _traj("apparait", part=0.9)),
        ]}
        touches = {("Otto Rank", "a"): {"Sigmund Freud"}, ("Otto Rank", "b"): {"Sigmund Freud"}}
        r = divergences.candidats(trajectoires, touches)
        self.assertEqual([c["concept"] for c in r], ["b", "a"])

    def test_deux_concepts_aux_ratios_arrondis_identiques_mais_aux_occurrences_differentes_restent_distincts(self):
        """Le risque que `branches.dedoublonner` neutralise en gardant `occurrences` (un compte
        entier, non arrondi) dans sa clé : deux sous-concepts réellement distincts peuvent produire
        des `part_dominante`/`pour_mille_*` arrondis identiques par coïncidence. Sans `occurrences`
        dans la clé, ce module fusionnerait à tort deux candidats qui ne mesurent pas la même
        chose."""
        trajectoires = {"Otto Rank": [
            ("motif_rare", _traj("apparait", part=0.5, avant=2.0, apres=10.0, occurrences=12)),
            ("motif_frequent", _traj("apparait", part=0.5, avant=2.0, apres=10.0, occurrences=1200)),
        ]}
        touches = {("Otto Rank", "motif_rare"): {"Sigmund Freud"},
                   ("Otto Rank", "motif_frequent"): {"Sigmund Freud"}}
        r = divergences.candidats(trajectoires, touches)
        self.assertEqual(len(r), 2)

    def test_traj_none_est_ignore_sans_planter(self):
        """`branches.trajectoire()` peut renvoyer `None` (corpus trop clairsemé) ; `candidats()`
        doit l'ignorer proprement plutôt que planter — un futur appelant pourrait un jour lui
        passer des trajectoires non filtrées en amont."""
        trajectoires = {"Otto Rank": [("geburtstrauma", None), ("kind", _traj("disparait"))]}
        touches = {("Otto Rank", "geburtstrauma"): {"Sigmund Freud"},
                   ("Otto Rank", "kind"): {"Sigmund Freud"}}
        r = divergences.candidats(trajectoires, touches)
        self.assertEqual([c["concept"] for c in r], ["kind"])


class TestPrudence(unittest.TestCase):

    def test_aucun_champ_ne_nomme_une_nature(self):
        """MÊME GARANTIE QUE PARTOUT AILLEURS dans ce corpus. Un candidat est un endroit où lire,
        jamais un verdict — la tentation est ici la plus forte de tout le projet, puisque le
        module s'appelle « divergences »."""
        trajectoires = {"Otto Rank": [("geburtstrauma", _traj("apparait"))]}
        touches = {("Otto Rank", "geburtstrauma"): {"Sigmund Freud"}}
        r = divergences.candidats(trajectoires, touches)
        interdits = {"divergence", "accord", "desaccord", "rupture", "opposition", "socle",
                     "emprunt", "contradiction", "bifurcation", "convergence"}

        def _valeurs_str(valeur):
            """Chaque chaîne portée par un champ, y compris à l'intérieur d'une liste (`lie_a`) —
            un champ de type liste ne doit pas non plus échapper à la garantie."""
            if isinstance(valeur, str):
                yield valeur
            elif isinstance(valeur, (list, tuple)):
                for element in valeur:
                    yield from _valeurs_str(element)

        for candidat in r:
            for cle, valeur in candidat.items():
                for texte in _valeurs_str(valeur):
                    self.assertFalse(interdits & set(texte.lower().split("_")),
                                     "le champ %r nomme une nature non lue : %r" % (cle, texte))

    def test_resume_ne_fait_que_compter(self):
        trajectoires = {"Otto Rank": [("a", _traj("apparait")), ("b", _traj("disparait"))]}
        touches = {("Otto Rank", "a"): {"Sigmund Freud"}, ("Otto Rank", "b"): {"Sigmund Freud"}}
        r = divergences.resume(divergences.candidats(trajectoires, touches))
        self.assertEqual(r["total"], 2)
        self.assertEqual(r["par_classe"], {"apparait": 1, "disparait": 1})

    def test_la_reserve_dit_les_quatre_issues_possibles_de_la_lecture(self):
        r = divergences.reserve()
        for attendu in ("AUCUN verdict", "divergence réelle", "convergence",
                        "développement", "artefact"):
            self.assertIn(attendu, r, "réserve incomplète : %s" % attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
