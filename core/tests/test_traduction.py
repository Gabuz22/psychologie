#!/usr/bin/env python3
"""TESTS de la couche de traduction — et surtout de ce qu'elle s'interdit de juger.

Le risque propre à cette couche est différent des autres : ce n'est pas de publier un chiffre
faux, c'est de publier un JUGEMENT DE TRADUCTION que le corpus ne fonde pas. Un corpus de 1 485
atomes français, écrits par un auteur qui n'est pas psychanalyste, ne peut pas valider « pulsion »
pour Trieb. Il peut compter des formes, et il peut refuser des correspondances.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import traduction          # noqa: E402


class TestFamille(unittest.TestCase):

    def test_la_charge_compte_les_formes_a_couvrir_pas_les_occurrences(self):
        """LA MESURE CENTRALE. Un mot français unique doit couvrir toute la famille allemande ;
        le chiffre utile est donc le nombre de FORMES DISTINCTES qui portent l'essentiel, pas le
        nombre d'occurrences — un terme fréquent sous deux formes est plus facile à traduire qu'un
        terme rare sous quarante."""
        vocab = {"trieb": 400, "triebe": 300, "triebregung": 200, "sexualtrieb": 100,
                 "triebleben": 50, "triebkraft": 10}
        f = traduction.famille(
            {"id": "t", "allemand": "Trieb", "francais_courant": "pulsion", "radical": "trieb",
             "faux_amis": []}, vocab)
        self.assertEqual(f["formes"], 6)
        self.assertEqual(f["occurrences"], 1060)
        # 400+300+200 = 900 < 954 ; il faut la quatrième forme pour atteindre 90 %.
        self.assertEqual(f["charge"], 4)

    def test_les_faux_amis_sont_RETIRES_et_leur_poids_est_rendu(self):
        """`Verlust` est LA PERTE et le radical `lust` l'attrape. Le retirer ne suffit pas : il
        faut dire combien il pesait, sans quoi « attention aux faux amis » reste une précaution
        de style au lieu d'un fait mesuré."""
        vocab = {"lust": 900, "unlust": 234, "verlust": 191, "lustig": 79}
        f = traduction.famille(
            {"id": "lust", "allemand": "Lust", "francais_courant": "plaisir", "radical": "lust",
             "faux_amis": ["verlust", "lustig"]}, vocab)
        self.assertEqual(f["occurrences"], 1134, "Verlust et lustig doivent sortir du compte")
        self.assertEqual(f["occurrences_faux_amis"], 270)
        self.assertAlmostEqual(f["contamination"], 270 / 1404, places=3)
        # `Unlust` DOIT rester : c'est le déplaisir freudien, second terme du couple.
        self.assertIn("unlust", dict(f["principales"]))

    def test_la_part_INTERNE_dit_ou_vit_l_ambiguite(self):
        """Un radical toujours en tête de mot est sûr ; un radical souvent à l'intérieur demande
        du jugement à chaque composé. `Besetzung` est le cas extrême du corpus — plus de la moitié
        de ses occurrences sont dans un composé."""
        vocab = {"besetzung": 156, "objektbesetzung": 46, "gegenbesetzung": 42,
                 "libidobesetzung": 34, "uberbesetzung": 18}
        f = traduction.famille(
            {"id": "b", "allemand": "Besetzung", "francais_courant": "investissement",
             "radical": "besetzung", "faux_amis": []}, vocab)
        self.assertLess(f["part_initiale"], 0.60)
        self.assertGreater(f["part_interne"], 0.40)
        self.assertAlmostEqual(f["part_initiale"] + f["part_interne"], 1.0, places=2)

    def test_une_forme_trop_rare_n_entre_pas_dans_la_famille(self):
        """Sous trois occurrences on décrit des coquilles d'OCR, pas du vocabulaire — et le corpus
        est majoritairement océrisé sans relecture."""
        vocab = {"trieb": 400, "triebxx": 1, "triebyy": 2}
        f = traduction.famille(
            {"id": "t", "allemand": "Trieb", "francais_courant": "pulsion", "radical": "trieb",
             "faux_amis": []}, vocab)
        self.assertEqual(f["formes"], 1)


class TestPrudence(unittest.TestCase):

    def test_le_francais_courant_est_declare_EXTERIEUR_et_jamais_valide(self):
        """LE REFUS CENTRAL DE CETTE COUCHE. Aucun champ ne doit porter un verdict sur la
        traduction : ni « correct », ni « juste », ni « validé ». Le corpus mesure une charge ; il
        ne valide pas un choix de traducteur."""
        vocab = {"trieb": 400, "triebe": 300}
        f = traduction.famille(traduction.TERMES[0], vocab)
        interdits = {"correct", "juste", "valide", "validee", "mauvais", "equivalent"}
        # `note` est de la prose libre et porte des noms propres : la première version de ce test
        # y cherchait aussi « bon » et tombait sur **Gustave Le Bon**. C'est très exactement
        # l'homographe que le corpus documente pour « Abraham », reproduit dans son propre
        # garde-fou — et la parade est la même : ne pas appliquer un motif de mot là où il ne peut
        # pas trancher. Les champs STRUCTURÉS, eux, doivent rester nets.
        for cle, valeur in f.items():
            if isinstance(valeur, str) and cle != "note":
                self.assertFalse(interdits & set(valeur.lower().split()),
                                 "le champ %r juge une traduction : %r" % (cle, valeur))
        self.assertIn("francais_courant", f,
                      "le rendu français doit être rendu, mais comme une donnée à confronter")
        self.assertNotIn("verdict", f, "aucun verdict de traduction ne doit exister")

    def test_les_refus_sont_tous_ARGUMENTES(self):
        """Un refus sans motif ne vaut pas mieux qu'une correspondance sans preuve. Même règle que
        les registres de lecture : le jugement doit pouvoir être contesté."""
        for r in traduction.refus_documentes():
            self.assertTrue(r["refuse"])
            self.assertGreater(len(r["motif"]), 40, "refus non argumenté : %s" % r["francais"])

    def test_les_quatre_refus_du_lexique_sont_TOUS_repris(self):
        """Ils vivent dans `lexique.MOTIFS_FR` et sont la matière première de cette couche. En
        perdre un en chemin ferait réapparaître une correspondance déjà écartée."""
        attendus = {("instinct", "Trieb"), ("rêve", "Traum"),
                    ("illusion", "Wahn"), ("état", "Staat")}
        rendus = {(r["francais"], r["allemand"]) for r in traduction.refus_documentes()}
        self.assertEqual(attendus, rendus)

    def test_chaque_terme_canonique_porte_une_note(self):
        """La note dit ce que le chiffre ne dit pas — pourquoi tel composé est un faux ami, ou
        pourquoi tel radical est inutilisable. Un tableau de chiffres sans elle se lirait comme un
        verdict de traduction."""
        for t in traduction.TERMES:
            self.assertTrue(t.get("note"), "terme sans note : %s" % t["id"])
            self.assertGreater(len(t["note"]), 60, "note trop courte : %s" % t["id"])

    def test_la_reserve_dit_l_ancre_unique_et_la_contamination(self):
        r = traduction.reserve()
        for attendu in ("NE JUGE AUCUNE TRADUCTION", "EXTÉRIEURE", "1 485", "40,4 %",
                        "schwanger", "REFUS"):
            self.assertIn(attendu, r, "réserve incomplète : %s" % attendu)

    def test_aucune_note_ne_RECOPIE_un_chiffre_du_tableau_genere(self):
        """DÉFAUT RÉEL, TROUVÉ EN RELISANT LE PREMIER DOCUMENT PRODUIT. La note de *Verdrängung*
        annonçait « 14 formes portent 90 % du total » quand le générateur en calculait 9 : la
        prose écrite à la main avait déjà divergé du calcul, dans le document même qui existe pour
        empêcher cette dérive. Les notes disent désormais ce que le tableau ne dit pas ; les
        chiffres de charge et de part interne restent au tableau, qui est recalculé.
        """
        import re
        for t in traduction.TERMES:
            chiffres = re.findall(r"\b\d+(?:[,.]\d+)?\s*(?:%|formes|occurrences)", t["note"])
            self.assertEqual(chiffres, [],
                             "la note de %s recopie un chiffre du tableau généré : %s"
                             % (t["id"], chiffres))

    def test_le_radical_ich_est_declare_inutilisable(self):
        """LE CAS QUI VALIDE LA MÉTHODE. Le lexique du projet ne cherche jamais `ich` par son
        radical — il cherche « das Ich », « Ich-Ideal ». Ce module doit dire pourquoi, avec le
        chiffre : 36,7 % des occurrences du radical sont `sich`, `nicht`, `mich`."""
        ich = next(t for t in traduction.TERMES if t["id"] == "ich")
        for forme in ("sich", "nicht", "mich"):
            self.assertIn(forme, ich["faux_amis"])
        self.assertIn("_RE_ICH_MOI", ich["note"],
                      "la note doit renvoyer à la parade déjà en place dans le lexique")
        # ET SURTOUT : le drapeau, sans lequel `ich` remporte tous les classements du document
        # avec des chiffres qui mesurent l'échec de la méthode et non le terme.
        self.assertFalse(ich["radical_utilisable"])
        self.assertFalse(traduction.famille(ich, {"ich": 10, "sich": 90})["radical_utilisable"])

    def test_tous_les_AUTRES_radicaux_sont_utilisables_par_defaut(self):
        """Le drapeau doit rester l'exception : s'il se répandait, le document ne classerait plus
        rien et la mesure perdrait son objet."""
        inutilisables = [t["id"] for t in traduction.TERMES
                         if not t.get("radical_utilisable", True)]
        self.assertEqual(inutilisables, ["ich"])


class TestDocumentGenere(unittest.TestCase):

    def _doc(self):
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        chemin = os.path.join(racine, "documentation", "TRADUCTION.md")
        self.assertTrue(os.path.exists(chemin), "document non généré : bin/generer_traduction.py")
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def test_le_document_se_declare_genere(self):
        self.assertIn("**DOCUMENT GÉNÉRÉ**", self._doc())

    def test_le_document_refuse_de_juger_une_traduction(self):
        """Un tableau « allemand → français » se lit spontanément comme un verdict. Le refus doit
        donc être dans le document, pas seulement dans le code qui le produit."""
        texte = self._doc()
        for attendu in ("ne juge aucune traduction", "EXTÉRIEURE", "refus", "schwanger"):
            self.assertIn(attendu, texte.replace("NE JUGE AUCUNE TRADUCTION",
                                                 "ne juge aucune traduction"),
                          "le document a perdu son refus : %s" % attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
