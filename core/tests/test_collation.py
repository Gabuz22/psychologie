#!/usr/bin/env python3
"""TESTS de la collation — dater les couches d'écriture par confrontation aux premières éditions.

Ce qui est protégé ici : la méthode ne conclut QUE si elle a prouvé qu'elle sait discriminer, et
un passage retrouvé dans la première édition est daté avec certitude — les autres gardent leur
réserve. Une datation fausse serait pire que l'incertitude qu'elle prétend lever.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import atomisation, collation, sources     # noqa: E402


class TestNormalisation(unittest.TestCase):
    """Les écarts systématiques entre 1900 et 1914 doivent disparaître, pas les mots."""

    def test_reforme_de_1901_neutralisee(self):
        """« Werthe » (1900) et « Werte » (1914) sont le même mot : sans cela, rien ne correspond."""
        self.assertEqual(collation.normaliser("Werthe des Theiles"),
                         collation.normaliser("Werte des Teiles"))
        self.assertEqual(collation.normaliser("Litteratur"), collation.normaliser("Literatur"))

    def test_mots_distincts_le_restent(self):
        self.assertNotEqual(collation.normaliser("Traum"), collation.normaliser("Trauma"))

    def test_ngrammes_tolerent_une_faute_isolee(self):
        """L'océrisation se trompe au hasard : une faute doit casser UN n-gramme, pas tous."""
        propre = collation.ngrammes(collation.normaliser(
            "der Traum ist eine verkleidete Erfuellung eines verdraengten Wunsches"))
        abime = collation.ngrammes(collation.normaliser(
            "der Traum ist eine verkleidete Erfuellung eines verdrangten Wunsches"))
        self.assertTrue(propre & abime, "une seule faute a tout cassé")


class TestEtalonnage(unittest.TestCase):
    """Aucune datation sans preuve préalable que la méthode discrimine."""

    @classmethod
    def setUpClass(cls):
        cls.temoin = collation.temoin_de("traumdeutung")

    def test_facsimile_present(self):
        self.assertIsNotNone(self.temoin, "fac-similé de 1900 absent du dépôt")
        self.assertGreater(len(self.temoin.index), 100000)

    def test_texte_etranger_ne_correspond_pas(self):
        """Témoin négatif universel : une phrase d'une AUTRE œuvre ne peut pas être dans ce livre."""
        etrangers = [a["texte"] for a in atomisation.atomiser("totem")["atomes"]
                     if a["nb_mots"] >= 15][:40]
        for t in etrangers:
            self.assertLess(self.temoin.couverture(t), 0.10)

    def test_preface_de_la_premiere_edition_retrouvee(self):
        """TÉMOIN POSITIF : la préface de 1900, reproduite en 1914, doit se retrouver."""
        texte = sources.charger("traumdeutung")["texte"]
        debut = texte.find("Vorbemerkung")
        fin = texte.find("Vorwort zur zweiten Auflage")
        atomes = [a for a in atomisation.atomiser("traumdeutung")["atomes"]
                  if debut <= a["debut"] < fin and a["nb_mots"] >= 15]
        self.assertGreater(len(atomes), 3)
        retrouves = sum(1 for a in atomes if self.temoin.couverture(a["texte"]) >= 0.125)
        self.assertEqual(retrouves, len(atomes), "la préface de 1900 devrait être intégralement là")

    def test_prefaces_posterieures_absentes(self):
        """TÉMOIN NÉGATIF interne : la préface de 1908 ne peut pas figurer dans le livre de 1900."""
        texte = sources.charger("traumdeutung")["texte"]
        debut = texte.find("Vorwort zur zweiten Auflage")
        fin = texte.find("Vorwort zur dritten Auflage")
        atomes = [a for a in atomisation.atomiser("traumdeutung")["atomes"]
                  if debut <= a["debut"] < fin and a["nb_mots"] >= 15]
        self.assertGreater(len(atomes), 3)
        for a in atomes:
            self.assertLess(self.temoin.couverture(a["texte"]), 0.125)

    def test_refus_de_conclure_quand_la_separation_manque(self):
        """« Jenseits » : océrisation trop dégradée → la collation NE conclut PAS, et le dit."""
        r = atomisation.atomiser("jenseits")
        couches = {a["attestation"].get("couche") for a in r["atomes"]}
        self.assertEqual(couches, {None}, "une œuvre non concluante ne doit pas être datée")
        self.assertIn("au plus tard", r["atomes"][0]["attestation"]["regle"])


class TestDatationParAtome(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.r = atomisation.atomiser("traumdeutung")

    def test_trois_couches_distinctes(self):
        c = self.r["controles"]["par_couche"]
        self.assertGreater(c["origine"], 3000)
        self.assertGreater(c["ajout"], 500)
        self.assertIn("indecis", c)

    def test_appendice_de_rank_entierement_posterieur(self):
        """Ajouté en 1914 : aucun de ses atomes ne peut se trouver dans l'édition de 1900."""
        rank = [a for a in self.r["atomes"]
                if a["auteur"] == "Otto Rank" and a["nb_mots"] >= 15]
        self.assertGreater(len(rank), 100)
        origine = [a for a in rank if a["attestation"].get("couche") == "origine"]
        self.assertEqual(origine, [], "l'appendice de Rank ne peut pas dater de 1900")

    def test_atome_datable_porte_une_date_certaine(self):
        a = next(x for x in self.r["atomes"] if x["attestation"].get("couche") == "origine")
        self.assertEqual(a["attestation"]["annee"], 1900)
        self.assertIn("certitude", a["attestation"]["regle"])

    def test_atome_ajoute_garde_sa_fourchette(self):
        a = next(x for x in self.r["atomes"] if x["attestation"].get("couche") == "ajout")
        self.assertEqual((a["attestation"]["annee_min"], a["attestation"]["annee_max"]), (1900, 1914))

    def test_symbolisme_majoritairement_posterieur(self):
        """RÉSULTAT DE FOND : la théorie du symbolisme onirique est surtout POST-1900.

        Freud le dit lui-même dans un passage que la collation classe en « ajout » : « … durch die
        Arbeiten von W. Stekel und anderen habe ich SEITHER den Umfang und die Bedeutung der
        Symbolik im Traume … ». Sans collation, on lui prêterait en 1900 une théorie qu'il n'avait
        pas encore — l'erreur exacte que ce projet doit rendre impossible.
        """
        sym = [a for a in self.r["atomes"]
               if any(c["concept"] == "symbol" for c in a["concepts"])
               and a["auteur"] == "Sigmund Freud"]
        ajouts = sum(1 for a in sym if a["attestation"].get("couche") == "ajout")
        self.assertGreater(ajouts, len(sym) * 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
