#!/usr/bin/env python3
"""TESTS DU BANC D'ÉPREUVE — parce qu'un banc de mesure faux invente des défauts.

Ces tests ne protègent pas un résultat, ils protègent un INSTRUMENT. L'audit du lexique de Stekel
(2026-07-31) a mesuré autre chose que ce qu'il croyait deux fois de suite, et les deux fois le banc
fabriquait des faux positifs qu'il fallait ensuite démentir un par un :

  • il repliait avec `collation.normaliser` (fait pour comparer deux éditions, donc agressif :
    Mutter → muter) au lieu de `segmentation.replier` — cinq sous-concepts sortaient à ZÉRO ;
  • il ne bordait pas les motifs à gauche, alors que le moteur compile `re.compile(r"\\b" + m)` —
    « tur » attrapait natur/kultur, « leiche » attrapait gleiche.

Un banc jeté dans un bac à sable se réécrit à chaque audit et refait les mêmes fautes. Versionné,
il les fait une fois. C'est la même raison qui a fait de `bin/auditer_lexique.py` un outil du dépôt
après treize usages.

LE TROISIÈME TEST EST LE PLUS IMPORTANT. Le détecteur de paratexte est ÉTALONNÉ sur deux motifs
dont l'audit a établi en LISANT qu'ils étaient massivement du paratexte, et sur six témoins
négatifs dont on sait qu'ils sont de la prose. Sans cet étalonnage, le détecteur peut se dégrader
en silence et rendre « 0 % de paratexte » sur un motif qui n'est QUE cela — c'est exactement ce
qu'a fait sa première version, qui cherchait des atomes répétés à l'identique alors que l'OCR
SOUDE la tête courante au milieu des phrases.
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "bin"))

import eprouver_sous_concept as banc                    # noqa: E402
import mesurer_tetes_courantes as mesure                # noqa: E402
from core import lexique                                # noqa: E402
from core.segmentation import replier                   # noqa: E402

STEKEL = "Wilhelm Stekel"

# Motifs dont l'audit a établi EN LISANT qu'ils sont massivement du paratexte imprimé. Les taux
# lus étaient de 87,5 % et 80 % ; le détecteur mécanique n'a pas à les retrouver exactement, il a
# à les placer très au-dessus des témoins négatifs.
PARATEXTE_CONNU = ["rundfrage", "berufsneurose"]

# Témoins négatifs : des mots de la prose de Stekel, dont l'audit a gardé les sous-concepts.
PROSE_CONNUE = ["onani", "koitus", "neuros", "tod", "mutter", "symbol"]

# L'écart doit rester net. Mesuré à l'étalonnage : positifs 70-74 %, négatifs 3-7 %.
PLANCHER_POSITIF = 0.50
PLAFOND_NEGATIF = 0.20


class TestBancPartageLeCodeDuMoteur(unittest.TestCase):
    """Le banc doit mesurer AVEC le moteur, pas à côté de lui."""

    def test_le_banc_replie_comme_le_moteur(self):
        """`collation.normaliser` écraserait Mutter → muter et sortirait des zéros fantômes.

        Le contrôle porte sur le CODE, pas sur le fichier : le nom fautif est cité en toutes
        lettres dans l'en-tête pour expliquer le piège, et une recherche naïve le trouverait là.
        """
        with open(banc.__file__, encoding="utf-8") as f:
            source = f.read()
        code = source.split('"""', 2)[2] if source.count('"""') >= 2 else source
        self.assertIn("from core.segmentation import replier", source)
        self.assertNotIn("collation.normaliser", code)
        self.assertNotIn("import collation", code)

    def test_le_banc_borde_les_motifs_comme_le_moteur(self):
        """Sans le `\\b` de gauche, « tier » attrape konstatieren : des faux positifs imaginaires."""
        with open(banc.__file__, encoding="utf-8") as f:
            source = f.read()
        self.assertIn(r're.compile(r"\b" + m)', source)


class TestDetecteurDeParatexte(unittest.TestCase):
    """ÉTALONNAGE. Un détecteur non étalonné se dégrade sans que rien ne le dise."""

    @classmethod
    def setUpClass(cls):
        tous = banc.atomes_par_auteur()
        cls.textes = [replier(a["texte"]).strip() for a in tous[STEKEL]]
        cls.ouvertures = banc._ouvertures_repetees(cls.textes)

    def part_paratexte(self, motif):
        r = re.compile(r"\b" + motif)
        touches = para = 0
        for t in self.textes:
            positions = [m.start() for m in r.finditer(t)]
            if not positions:
                continue
            touches += 1
            if all(banc._est_paratexte(t, p, self.ouvertures) for p in positions):
                para += 1
        self.assertTrue(touches, "motif %r introuvable — l'étalonnage ne mesure rien" % motif)
        return para / touches

    def test_les_deux_motifs_condamnes_ressortent(self):
        """`rundfrage` et `berufsneurose` : 87 % et 80 % de paratexte à la LECTURE."""
        for motif in PARATEXTE_CONNU:
            self.assertGreaterEqual(
                self.part_paratexte(motif), PLANCHER_POSITIF,
                "%r est du paratexte à plus de 80 %% et le détecteur ne le voit plus" % motif)

    def test_la_prose_reste_de_la_prose(self):
        """Un détecteur qui crie partout ne sert à rien : les vrais concepts doivent rester bas."""
        for motif in PROSE_CONNUE:
            self.assertLessEqual(
                self.part_paratexte(motif), PLAFOND_NEGATIF,
                "%r est de la prose et le détecteur le donne pour du paratexte" % motif)

    def test_l_ecart_separe_vraiment_les_deux_familles(self):
        """Le pire positif doit rester au-dessus du pire négatif — sinon le seuil n'existe pas."""
        pire_positif = min(self.part_paratexte(m) for m in PARATEXTE_CONNU)
        pire_negatif = max(self.part_paratexte(m) for m in PROSE_CONNUE)
        self.assertGreater(pire_positif, pire_negatif,
                           "les deux familles ne sont plus séparables : le signal est perdu")

    def test_la_tete_courante_n_est_pas_un_atome_repete(self):
        """LE DÉFAUT DE LA PREMIÈRE VERSION, gardé comme test.

        Chercher des atomes identiques ne trouve RIEN sur `berufsneurose`, dont 80 % des atomes
        sont pourtant du paratexte : l'OCR soude la tête courante EN PLEIN MILIEU de la phrase de
        la page, si bien que chaque occurrence est textuellement unique.
        """
        import collections
        r = re.compile(r"\bberufsneurose")
        touches = [t for t in self.textes if r.search(t)]
        doublons = [k for k, n in collections.Counter(touches).items() if n >= 3]
        self.assertFalse(doublons,
                         "si des atomes identiques existent, le raccourci naïf redevient tentant")
        self.assertGreaterEqual(self.part_paratexte("berufsneurose"), PLANCHER_POSITIF)


class TestMotifsEcritsCorrectement(unittest.TestCase):
    """DEUX FAUTES D'ÉCRITURE QUI RENDENT UN MOTIF DÉFINITIVEMENT MUET, et qui sont INVISIBLES.

    Ni l'une ni l'autre ne lève d'erreur, ni ne se voit à la relecture du fichier — le motif a
    l'air juste. Seule une mesure les trouve, et elles ont vécu des mois dans le dépôt.

    1. `\\b` DANS UNE CHAÎNE NON BRUTE. Python lit alors un caractère BACKSPACE (0x08), pas une
       frontière de mot. Trois motifs de Freud en portaient un — `"real\\b"`, `"bube\\b"`,
       `"junge\\b"` — et aucun texte allemand ne contient ce caractère : 116 atomes de « Junge »
       et 49 de « real » passaient au travers, dans le sous-concept qui porte la différence des
       sexes. Il faut écrire `r"junge\\b"`.

    2. UN DIACRITIQUE. Le lexique s'applique après `segmentation.replier`, qui les SUPPRIME. Un
       motif portant « ä », « ö », « ü » ou « ß » ne peut jamais se déclencher. La faute est
       documentée trois fois dans le lexique de Stekel et une fois chez Freud (`abergläubisch`).
    """

    def _tous_les_motifs(self):
        from core import lexiques
        tables = [("Freud", lexique.CONCEPTS)]
        tables += [(nom, mod.CONCEPTS) for nom, mod in lexiques.PAR_AUTEUR.items()]
        for nom, concepts in tables:
            for groupe, meta in concepts.items():
                for sous, motifs in meta["termes"].items():
                    for m in motifs:
                        yield nom, groupe, sous, m

    def test_aucun_motif_ne_contient_de_caractere_de_controle(self):
        """Un `\\b` oublié en chaîne brute devient un backspace, et le motif meurt en silence."""
        fautifs = [(n, g, s, repr(m)) for n, g, s, m in self._tous_les_motifs()
                   if any(ord(c) < 32 for c in m)]
        self.assertFalse(fautifs, "motifs portant un caractère de contrôle : %s" % fautifs)

    def test_aucun_motif_ne_porte_de_diacritique(self):
        """Le lexique s'applique APRÈS le repli : « ä » ne peut jamais être rencontré."""
        fautifs = [(n, g, s, m) for n, g, s, m in self._tous_les_motifs()
                   if any(c in m for c in "äöüßÄÖÜàéèêç")]
        self.assertFalse(fautifs, "motifs portant un diacritique, donc muets : %s" % fautifs)


class TestMesureDesTetesCourantes(unittest.TestCase):
    """ÉTALONNAGE CONTRE DEUX COMPTES ÉTABLIS À LA MAIN.

    `bin/mesurer_tetes_courantes.py` a mesuré autre chose que ce qu'il croyait à sa première
    version : il prenait pour tête courante tout atome dont les deux premiers mots se répètent, et
    trouvait donc « ich habe » (91), « es ist » (91), « er war » (70) — les ouvertures de phrase
    ordinaires de la langue allemande. Il annonçait 30,9 % du corpus « touché ». C'était la
    deuxième erreur du même genre : le premier détecteur du banc, lui, ne trouvait RIEN.

    Ce qui rend la version actuelle croyable n'est pas sa plausibilité, c'est qu'elle retrouve
    EXACTEMENT deux comptes obtenus par des contradicteurs qui ont lu les atomes un par un :
    dans « Nervöse Angstzustände », les deux parties du volume s'intitulent « Die Angstneurose » et
    « Die Angsthysterie », et leurs titres sont imprimés en haut de chaque page.
    """

    ATTENDU = {"die angsthysterie.": 61, "die angstneurose.": 46}

    @classmethod
    def setUpClass(cls):
        from core import atomisation
        cls.atomes = atomisation.atomiser("nervoese_angstzustaende")["atomes"]
        cls.tetes = mesure.tetes_courantes(cls.atomes)

    def test_retrouve_les_deux_comptes_lus_a_la_main(self):
        for tete, n in self.ATTENDU.items():
            self.assertEqual(self.tetes.get(tete), n,
                             "« %s » a été compté %s fois à la main dans ce volume" % (tete, n))

    def test_ne_prend_pas_une_ouverture_de_phrase_pour_un_titre(self):
        """LE DÉFAUT DE LA PREMIÈRE VERSION, gardé comme test.

        « ich habe », « es ist », « er war » ouvrent des centaines de phrases allemandes. Un
        détecteur qui les compte ne mesure pas le paratexte, il mesure la langue.
        """
        for phrase in ["ich habe", "es ist", "er war", "in der", "es war", "sie war"]:
            self.assertNotIn(phrase, self.tetes)
            self.assertNotIn(phrase + ".", self.tetes)

    def test_ecarte_la_numerotation_des_listes(self):
        """Stekel numérote ses cas : « 3. » est court et suivi d'un point, mais ce n'est pas un titre."""
        for faux in ["3.", "12.", "dr.", "s.", "vgl.", "ii."]:
            self.assertNotIn(faux, self.tetes)

    def test_une_tete_courante_est_bien_un_intitule(self):
        """Tout ce qui est retenu doit ressembler à un titre : court, terminé par un point."""
        for tete in self.tetes:
            self.assertTrue(tete.endswith("."), tete)
            self.assertLessEqual(len(tete), mesure.TETE_SIGNES + 1, tete)


class TestFichesDuBanc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tous = banc.atomes_par_auteur()
        cls.fiches = banc.eprouver(STEKEL, cls.tous, groupe_filtre="onanie")

    def test_le_banc_rend_une_fiche_par_sous_concept(self):
        attendus = set(lexique.pour_auteur(STEKEL).CONCEPTS["onanie"]["termes"])
        self.assertEqual({f["sous"] for f in self.fiches}, attendus)

    def test_les_formes_captees_sont_des_mots_entiers(self):
        """La règle d'or : on juge un motif sur ce qu'il RAMÈNE, pas sur ce qu'il vise."""
        fiche = next(f for f in self.fiches if f["sous"] == "onanie")
        formes = dict(fiche["formes"])
        self.assertTrue(formes, "aucune forme captée : le banc ne montre plus rien à juger")
        for forme in formes:
            # Le motif est ouvert à gauche (`[a-z]*onani`) pour attraper kinderonanie et
            # säuglingsonanie : la forme captée peut donc commencer AVANT « onani », ou par lui.
            self.assertRegex(forme, r"^[a-z]*onani", forme)

    def test_le_cout_propre_ne_depasse_jamais_le_compte(self):
        for f in self.fiches:
            self.assertLessEqual(f["propres"], f["atomes"], f["sous"])

    def test_la_cle_lue_pour_le_cout_propre_existe_sur_les_atomes(self):
        """DÉFAUT RÉEL, trouvé par un contradicteur : le banc lisait une clé INEXISTANTE.

        Il demandait `c.get("sous_concepts", [])` alors qu'un concept d'atome porte `groupe` et
        `concept`. Le `.get()` rendait sa valeur par défaut, l'ensemble « autres » restait toujours
        vide, et la colonne « propres » — celle qu'on cite pour condamner un sous-concept —
        mesurait en réalité « atomes sans fonction ». Surestimation mesurée : facteur ~2,3.

        Une clé absente lue par `.get()` échoue EN SILENCE et rend un chiffre plausible. Ce test
        vérifie la clé sur de vrais atomes, plutôt que de faire confiance au nom.
        """
        vus = False
        for atomes in self.tous.values():
            for a in atomes:
                for c in a["concepts"]:
                    self.assertIn("concept", c)
                    self.assertNotIn("sous_concepts", c)
                    vus = True
                if vus:
                    break
            if vus:
                break
        self.assertTrue(vus, "aucun atome qualifié : le test ne vérifie rien")

    def test_le_cout_propre_distingue_bien_un_atome_multi_concepts(self):
        """Un atome portant DEUX sous-concepts ne doit être « propre » à aucun des deux."""
        multi = [a for a in self.tous[STEKEL]
                 if len({c["concept"] for c in a["concepts"]}) >= 2]
        self.assertTrue(multi, "aucun atome multi-concepts : la mesure serait triviale")
        a = multi[0]
        concepts = {c["concept"] for c in a["concepts"]}
        for sous in concepts:
            self.assertTrue(concepts - {sous},
                            "cet atome doit rester attribué à un autre sous-concept que %r" % sous)


if __name__ == "__main__":
    unittest.main()
