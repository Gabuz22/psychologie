#!/usr/bin/env python3
"""TESTS du socle commun — et surtout de ce qu'il REFUSE de conclure.

Ce module répond à la question la plus tentante du corpus (« qu'est-ce que ces auteurs ont en
commun ? ») et c'est celle où il est le plus facile de publier un chiffre flatteur et faux. Le
projet en a déjà payé deux : l'appariement de concepts par voisinage (6 % de précision, une
divergence confirmée sur seize) et l'agrégation concept-à-concept des reprises (1 366 arêtes
fabriquées pour 354 actes réels). Les tests ci-dessous existent pour que ni l'un ni l'autre ne
revienne sous le nom de « socle ».
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import socle          # noqa: E402


def _acte(a, b, verdict, atomes_a=(), atomes_b=(), vers=None):
    return {"auteur_a": a, "auteur_b": b, "verdict": verdict,
            "atomes_a": list(atomes_a), "atomes_b": list(atomes_b), "reclasse_vers": vers}


class TestPartageAtteste(unittest.TestCase):

    def test_seuls_les_actes_CONFIRMES_comptent(self):
        """Un acte rejeté ou non lu n'est pas du partage. C'est la règle qui distingue cette
        couche d'un simple comptage de ressemblances."""
        actes = [_acte("A", "B", "confirme"), _acte("A", "B", "rejete"),
                 _acte("A", "B", "reclasse", vers="Hebbel"), _acte("A", "B", None)]
        r = socle.partage_atteste(actes)
        self.assertEqual(r["actes_confirmes"], 1)

    def test_la_forme_du_partage_est_mesuree_pas_supposee(self):
        """LE RÉSULTAT CENTRAL DE LA COUCHE. Un socle véritable relierait les disciples entre eux ;
        une étoile les relie tous au même centre et presque pas entre eux. La différence se mesure,
        et `part_par_le_centre` est le chiffre qui la porte."""
        actes = ([_acte("Freud", "Rank", "confirme")] * 8
                 + [_acte("Freud", "Abraham", "confirme")] * 8
                 + [_acte("Rank", "Abraham", "confirme")] * 1)
        r = socle.partage_atteste(actes)
        self.assertEqual(r["centre"], "Freud")
        self.assertEqual(r["actes_confirmes"], 17)
        self.assertEqual(r["actes_sans_le_centre"], 1)
        self.assertAlmostEqual(r["part_par_le_centre"], 16 / 17, places=2)

    def test_la_profondeur_dit_si_un_NOYAU_existe(self):
        """Un noyau commun se prouverait par un passage que TROIS auteurs partagent. La mesure doit
        pouvoir le voir si c'est le cas — et dire zéro quand ce n'est pas le cas, ce qui est
        l'état réel du corpus."""
        # Un même atome de Freud repris par Rank ET par Abraham : profondeur 2.
        actes = [_acte("Freud", "Rank", "confirme", atomes_a=["f:a1"], atomes_b=["r:a9"]),
                 _acte("Freud", "Abraham", "confirme", atomes_a=["f:a1"], atomes_b=["ab:a4"])]
        r = socle.partage_atteste(actes)
        self.assertEqual(r["profondeur_maximale"], 2)
        self.assertIn("f:a1", r["passages_a_deux_partenaires"])
        # Les deux passages qui ne sont repris que d'un côté restent à 1.
        self.assertEqual(r["profondeur"][1], 2)


class TestMotPartage(unittest.TestCase):

    def _mesure(self, motif, densites, par_oeuvre=None, atomes=None):
        auteurs = []
        for nom, pm in densites.items():
            auteurs.append({"auteur": nom, "pour_mille": pm,
                            "atomes": (atomes or {}).get(nom, 10000),
                            "par_oeuvre": (par_oeuvre or {}).get(nom, [])})
        return {"motif": motif, "auteurs": auteurs}

    def test_un_mot_que_tous_emploient_egalement_est_stable(self):
        r = socle.mot_partage([self._mesure(r"\b(leben)", {"A": 30.0, "B": 41.0, "C": 39.0})])
        self.assertEqual(r[0]["classe"], "stable")
        self.assertLessEqual(r[0]["etendue"], socle.ETENDUE_STABLE)

    def test_un_mot_qu_un_auteur_n_emploie_pas_n_est_PAS_compare(self):
        """« Partiel » n'est pas une divergence : c'est l'absence de terrain commun. Les traiter
        ensemble ferait passer un mot que cinq auteurs ignorent pour un désaccord entre eux."""
        r = socle.mot_partage([self._mesure(r"\b(amphimixis)", {"A": 40.0, "B": 0.0, "C": 0.1})])
        self.assertEqual(r[0]["classe"], "partiel")
        self.assertIsNone(r[0]["etendue"], "un mot non commun ne doit pas porter d'étendue")

    def test_l_artefact_d_OEUVRE_est_signale_et_non_corrige(self):
        """SEPT DES SEIZE DIVERGENCES DÉJÀ LUES DANS CE PROJET étaient des artefacts d'œuvre unique.
        Le drapeau existe pour que la huitième ne soit pas publiée. Il SIGNALE, il ne filtre pas :
        filtrer supposerait qu'on sait trancher, et on ne sait pas."""
        r = socle.mot_partage([self._mesure(
            r"\b(hysterie)", {"Breuer": 198.0, "Freud": 29.0, "Rank": 6.0},
            par_oeuvre={"Breuer": [{"porteurs": 95}, {"porteurs": 5}]})])
        self.assertEqual(r[0]["classe"], "disperse")
        self.assertTrue(r[0]["porte_par_une_oeuvre"])
        self.assertGreaterEqual(r[0]["concentration_haut"], socle.CONCENTRATION_ARTEFACT)

    def test_l_extremum_porte_par_le_PETIT_corpus_est_signale(self):
        """Un « détecteur » n'utilisant QUE le rapport des effectifs atteint déjà une AUC de 0,576
        sur ce corpus. Sans ce drapeau, on publierait une différence de volume pour une différence
        d'usage."""
        r = socle.mot_partage([self._mesure(
            r"\b(hypnose)", {"Breuer": 60.0, "Freud": 10.0, "Rank": 2.0},
            atomes={"Breuer": 700, "Freud": 60000, "Rank": 20000})])
        self.assertTrue(r[0]["extremum_petit_corpus"])


class TestTiersCommun(unittest.TestCase):

    def test_le_tiers_est_EXCLU_du_socle_et_nomme(self):
        """Deux auteurs qui recopient la même page d'un troisième se ressemblent sans rien se
        devoir. Sans la lecture, chacun de ces actes serait publié comme un emprunt — c'est-à-dire
        comme du socle."""
        actes = [_acte("Rank", "Stekel", "reclasse", vers="Friedrich Hebbel"),
                 _acte("Rank", "Stekel", "confirme")]
        r = socle.tiers_commun(actes)
        self.assertEqual(r["actes_reclasses"], 1)
        self.assertEqual(r["tiers"][0]["tiers"], "Friedrich Hebbel")
        # Et l'acte confirmé ne doit PAS y figurer : les deux couches ne se mélangent pas.
        self.assertEqual(sum(t["actes"] for t in r["tiers"]), 1)

    def test_un_meme_tiers_cite_avec_des_references_differentes_ne_compte_qu_une_fois(self):
        """DÉFAUT MESURÉ : les verdicts citent l'ouvrage entier, et compter ces chaînes telles
        quelles éclatait Rosegger en cinq « tiers » distincts — 52 pour une vingtaine de noms
        réels. La bibliothèque commune paraissait deux fois plus large qu'elle n'est."""
        actes = [
            _acte("F", "S", "reclasse", vers="Peter Rosegger (Waldheimat, Bd. II)"),
            _acte("F", "S", "reclasse", vers="Peter Rosegger, récit de l'apprenti tailleur"),
            _acte("F", "S", "reclasse", vers="Peter Rosegger"),
        ]
        r = socle.tiers_commun(actes)
        self.assertEqual(r["tiers_distincts"], 1, r["tiers"])
        self.assertEqual(r["tiers"][0], {"tiers": "Peter Rosegger", "actes": 3})

    def test_un_reclassement_sans_cible_reste_visible(self):
        """Ne pas savoir qui est le tiers est une information ; l'effacer en ferait disparaître
        l'acte du décompte, et le socle paraîtrait plus propre qu'il n'est."""
        r = socle.tiers_commun([_acte("A", "B", "reclasse", vers=None)])
        self.assertEqual(r["actes_reclasses"], 1)
        self.assertEqual(r["tiers"][0]["tiers"], "(non renseigné)")


class TestPrudence(unittest.TestCase):
    """Ce que le module doit REFUSER de dire — même quand son nom invite à le dire."""

    def test_aucun_champ_ne_nomme_une_nature(self):
        """MÊME GARANTIE QUE `comparaison.qualifier`, et elle est plus difficile à tenir ici :
        le module s'appelle « socle ». Il calcule un partage ; il ne doit à aucun moment qualifier
        ce partage d'accord, de dette ou d'opposition. Le corpus a mesuré ce que valent ces
        qualifications — le signal « ecart_freud » n'a rien confirmé sur cinq candidats."""
        actes = [_acte("Freud", "Rank", "confirme", atomes_a=["f:a1"], atomes_b=["r:a2"]),
                 _acte("Freud", "Stekel", "reclasse", vers="Hebbel")]
        mesures = [{"motif": r"\b(traum)", "auteurs": [
            {"auteur": "Freud", "pour_mille": 40.0, "atomes": 60000, "par_oeuvre": []},
            {"auteur": "Rank", "pour_mille": 30.0, "atomes": 20000, "par_oeuvre": []}]}]
        interdits = {"emprunt", "plagiat", "contradiction", "opposition", "bifurcation",
                     "accord", "desaccord", "influence", "dette"}
        rendus = [socle.partage_atteste(actes), socle.tiers_commun(actes),
                  {"lignes": socle.mot_partage(mesures)}]
        for r in rendus:
            for cle, valeur in r.items():
                if isinstance(valeur, str):
                    self.assertFalse(interdits & set(valeur.lower().split("_")),
                                     "le champ %r nomme une nature non prouvée : %r" % (cle, valeur))

    def test_la_reserve_porte_les_trois_refus(self):
        """La réserve voyage avec la mesure. La séparer ferait dire aux chiffres ce que le module
        refuse de dire — et c'est la seule protection d'un lecteur qui ne lira pas le code."""
        r = socle.reserve()
        for attendu in ("étoile", "aucun passage", "PAS un désaccord", "seize", "aveugle"):
            self.assertIn(attendu, r, "réserve incomplète : %s" % attendu)

    def test_les_trois_couches_ne_se_multiplient_jamais(self):
        """L'ERREUR DÉJÀ COMMISE, ET REFAITE ICI AVANT D'ÊTRE VUE. Attribuer un acte de citation à
        chacun des concepts que la phrase touche donnait 341 motifs « attestés » — le même produit
        croisé qui fabriquait 1 366 arêtes pour 354 actes dans `core/carte.py`.

        Aucune fonction de ce module ne doit donc recevoir À LA FOIS des actes et des motifs : la
        première qui le fera pourra les croiser. On vérifie les NOMS des paramètres et non leur
        nombre — `mot_partage` en a légitimement un second, `lexique_par_motif`, qui est de la
        métadonnée SUR les motifs et non une seconde unité de mesure."""
        import inspect
        actes = {"actes", "evenements", "liens", "reprises"}
        motifs = {"mesures", "motifs", "densites", "usages"}
        for nom in ("partage_atteste", "mot_partage", "tiers_commun"):
            params = set(inspect.signature(getattr(socle, nom)).parameters)
            self.assertFalse(params & actes and params & motifs,
                             "%s reçoit à la fois des actes et des motifs (%s) : une couche qui "
                             "tient les deux finit par les multiplier" % (nom, sorted(params)))

    def test_le_lexicographe_du_motif_voyage_avec_la_mesure(self):
        """RÈGLE DÉJÀ ÉCRITE POUR `table_des_usages`, et l'omettre ici la contredirait : la ligne
        d'un auteur sur SON PROPRE motif est haute par construction. Sans cette colonne, « Rank
        domine sur `dichter` » se lit comme un fait d'auteur alors que le motif peut venir du
        lexique de Rank."""
        mesure = {"motif": r"\b(dichter)", "auteurs": [
            {"auteur": "Otto Rank", "pour_mille": 77.3, "atomes": 14938, "par_oeuvre": []},
            {"auteur": "Sigmund Freud", "pour_mille": 1.1, "atomes": 40276, "par_oeuvre": []}]}
        r = socle.mot_partage([mesure], {r"\b(dichter)": "Otto Rank"})[0]
        self.assertEqual(r["lexique"], "Otto Rank")
        self.assertTrue(r["haut_est_le_lexicographe"],
                        "le motif vient du lexique de celui qui domine — il faut le dire")
        # Et sans la table, la mesure reste rendue : l'information manque, elle n'est pas inventée.
        self.assertIsNone(socle.mot_partage([mesure])[0]["lexique"])


class TestDocumentGenere(unittest.TestCase):
    """Le document existe, et il porte ce que la mesure a coûté.

    On n'assert PAS les chiffres volatils — ils changent à chaque œuvre ajoutée, et un test qui
    tombe pour cette raison finit par être désactivé. On assert ce qui est durable : l'en-tête qui
    interdit l'édition à la main, et les trois refus doctrinaux sans lesquels les tableaux se
    liraient comme une carte des idées.
    """

    def _doc(self):
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        chemin = os.path.join(racine, "documentation", "SOCLE_COMMUN.md")
        self.assertTrue(os.path.exists(chemin), "document non généré : bin/generer_socle.py")
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def test_le_document_se_declare_genere(self):
        self.assertIn("**DOCUMENT GÉNÉRÉ**", self._doc())
        self.assertIn("bin/generer_socle.py", self._doc())

    def test_le_document_porte_les_trois_refus(self):
        texte = self._doc()
        for attendu in ("étoile", "aucun passage", "PAS un désaccord", "bibliothèque"):
            self.assertIn(attendu, texte, "le document a perdu un refus : %s" % attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
