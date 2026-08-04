#!/usr/bin/env python3
"""TESTS de la carte des actes de citation.

Cette couche est née d'un DOUBLE échec, et chaque test protège une leçon de l'un des deux.

Le premier échec est documenté ailleurs : apparier des concepts par leur voisinage ne marche pas
(`documentation/APPARIEMENT_ECARTE.md`). Le second guettait ici même, et a été mesuré avant
d'écrire une ligne : agréger les liens de reprise en arêtes CONCEPT-À-CONCEPT donne 1 366 arêtes
là où il y a 107 actes réels, parce que chaque phrase porte 3,5 concepts et que le produit croisé
fabrique le reste. C'est la même accumulation combinatoire, sous une autre forme.

Ce que ces tests interdisent, donc : que le poids redevienne un produit de concepts, que la carte
se taise sur ce qu'elle ne voit pas, et que la preuve cesse d'être vérifiable dans le livre.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import carte, collation                                    # noqa: E402


def _paire(ida, idb, ia, ib, texte_a, texte_b, **kw):
    """Un lien de reprise minimal, tel que `comparaison.qualifier` en produit."""
    base = {
        "a": {"id": ida, "index": ia, "oeuvre": ida.split(":")[0], "texte": texte_a},
        "b": {"id": idb, "index": ib, "oeuvre": idb.split(":")[0], "texte": texte_b},
        "contenance": 0.8, "force": "manifeste", "sens": None, "source_tierce": False,
        "partages": [],
    }
    base.update(kw)
    return base


class TestPoids(unittest.TestCase):
    """LE PIÈGE CENTRAL, mesuré avant construction : 1 366 arêtes concept-à-concept pour
    107 actes réels. Le poids doit rester un nombre de PHRASES."""

    def test_le_poids_est_un_nombre_de_phrases(self):
        paires = [_paire("x:a1", "y:b1", 1, 1, "Der Traum ist eine Wunscherfüllung des Kindes.",
                         "Der Traum ist eine Wunscherfüllung des Kindes."),
                  _paire("x:a2", "y:b2", 2, 2, "Die Verdrängung wirkt auf das Kind.",
                         "Die Verdrängung wirkt auf das Kind.")]
        # Chaque atome porte trois concepts : un produit croisé en ferait neuf « liens ».
        cs = {("g", "traum"), ("g", "kind"), ("g", "wunsch")}
        concepts = {p[c]["id"]: cs for p in paires for c in ("a", "b")}
        evts = carte.evenements_de_carte({("A", "B"): paires}, concepts)
        self.assertEqual(len(evts), 1, "deux phrases contiguës = UN acte")
        self.assertEqual(evts[0]["poids"], 2, "le poids compte les phrases, pas les concepts")

    def test_les_concepts_sont_separes_en_trois(self):
        """Seuls les concepts portés des DEUX côtés renseignent. Les deux autres ensembles sont
        rendus pour qu'on puisse constater ce qu'un produit croisé aurait fabriqué — jamais pour
        en faire des arêtes."""
        paires = [_paire("x:a1", "y:b1", 1, 1, "Der Traum des Kindes.", "Die Angst des Kindes.")]
        concepts = {"x:a1": {("g", "traum"), ("g", "kind")},
                    "y:b1": {("h", "angst"), ("h", "kind")}}
        e = carte.evenements_de_carte({("A", "B"): paires}, concepts)[0]
        self.assertEqual(e["concepts_communs"], ["kind"])
        self.assertEqual(e["concepts_a_seul"], ["traum"])
        self.assertEqual(e["concepts_b_seul"], ["angst"])

    def test_verdicts_discordants_ne_deviennent_pas_un_acte_non_lu(self):
        paires = [
            _paire("x:a1", "y:b1", 1, 1, "Phrase partagée assez longue ici.",
                   "Phrase partagée assez longue ici.", verdict="confirme"),
            _paire("x:a2", "y:b2", 2, 2, "Deuxième phrase partagée assez longue.",
                   "Deuxième phrase partagée assez longue.", verdict="reclasse"),
        ]
        e = carte.evenements_de_carte({("A", "B"): paires}, {})[0]
        self.assertIsNone(e["verdict"])
        self.assertEqual(e["etat_validation"], "discordant")
        self.assertEqual(e["verdicts_elementaires"], ["confirme", "reclasse"])


class TestPreuve(unittest.TestCase):
    """La preuve doit être VÉRIFIABLE DANS LE LIVRE. Deux défauts l'en empêchaient."""

    def test_les_suites_qui_se_chevauchent_sont_recollees(self):
        """DÉFAUT MESURÉ. Le détecteur travaille par suites de six mots et les rendait triées
        ALPHABÉTIQUEMENT : les douze premières preuves affichées commençaient toutes par « a ».
        La preuve montrée était arbitraire et tronquée à six mots. Recollées, elles restituent le
        passage réel — 21 mots en médiane sur le corpus, jusqu'à 54."""
        mots = "ich zitiere woertlich aus den drei abhandlungen zur sexualtheorie seite".split()
        grammes = [" ".join(mots[i:i + 6]) for i in range(len(mots) - 5)]
        recolle = carte.recoller(list(reversed(grammes)))
        self.assertEqual(len(recolle), 1)
        self.assertEqual(recolle[0], " ".join(mots))

    def test_deux_passages_distincts_ne_sont_pas_fusionnes(self):
        a = "der traum ist die erfuellung eines verdraengten wunsches".split()
        b = "die angst entsteht aus der libido durch verdraengung".split()
        g = ([" ".join(a[i:i + 6]) for i in range(len(a) - 5)]
             + [" ".join(b[i:i + 6]) for i in range(len(b) - 5)])
        self.assertEqual(len(carte.recoller(g)), 2)

    def test_le_passage_est_rendu_tel_qu_il_est_imprime(self):
        """DÉFAUT MESURÉ. La comparaison travaille sur une forme repliée qui neutralise
        l'orthographe d'avant 1901 et les géminations instables de l'OCR : « hattest » y devient
        « hatest », « Stückes » devient « stukes ». Publier CETTE forme comme preuve était
        doublement fautif — illisible, et absente du livre, donc invérifiable."""
        texte = "Es war im Sommer eine Zeit intensiver Hitze gewesen, und Patientin hatte Durst."
        replie = collation.normaliser(texte)
        cible = " ".join(replie.split()[3:12])
        self.assertIn("hate", cible)           # la forme repliée est bien abîmée
        origine = carte.retrouver_original(texte, cible)
        self.assertIn("hatte", origine)        # l'originale est rendue
        self.assertIn("Sommer", origine)       # majuscule conservée
        self.assertIn(",", origine)            # ponctuation conservée

    def test_un_passage_introuvable_ne_produit_rien_plutot_qu_un_texte_reconstruit(self):
        self.assertIsNone(carte.retrouver_original("Ein kurzer Satz.", "ceci nest pas dedans"))


class TestSilences(unittest.TestCase):
    """LE DÉFAUT LE PLUS GRAVE DE LA PREMIÈRE VERSION, et il était d'omission.

    Le résumé était bâti sur les seuls actes trouvés : un couple sans acte ne produisait pas une
    ligne à zéro, il n'existait pas. Neuf couples sur quinze disparaissaient sans un mot — dont
    cinq où la détection est IMPOSSIBLE par construction, les corpus français et allemand du
    projet ne partageant qu'UN seul groupe de six mots. Pendant ce temps Freud consacre à Le Bon
    un chapitre entier de 105 atomes. Taire cela, c'est présenter un aveuglement de méthode comme
    un fait de corpus.
    """

    LANGUES = {"Freud": "de", "Rank": "de", "Le Bon": "fr"}

    def test_un_couple_sans_acte_existe_quand_meme(self):
        cpl = carte.couples([], self.LANGUES.keys(), self.LANGUES)
        self.assertEqual(len(cpl), 3, "trois auteurs = trois couples, tous rendus")
        self.assertTrue(all(c["silence"] for c in cpl))

    def test_le_silence_de_langue_est_distingue_du_silence_de_corpus(self):
        cpl = {(c["auteur_a"], c["auteur_b"]): c
               for c in carte.couples([], self.LANGUES.keys(), self.LANGUES)}
        self.assertEqual(cpl[("Freud", "Le Bon")]["silence"], "langues")
        self.assertEqual(cpl[("Freud", "Rank")]["silence"], "aucun_acte")

    def test_un_couple_avec_actes_ne_porte_pas_de_silence(self):
        evts = [{"auteur_a": "Freud", "auteur_b": "Rank", "poids": 2, "force": "manifeste",
                 "sens": None, "sens_lu": None, "verdict": "confirme", "source_tierce": False}]
        cpl = {(c["auteur_a"], c["auteur_b"]): c
               for c in carte.couples(evts, self.LANGUES.keys(), self.LANGUES)}
        self.assertIsNone(cpl[("Freud", "Rank")]["silence"])
        self.assertEqual(cpl[("Freud", "Rank")]["confirmes"], 1)


class TestCouverture(unittest.TestCase):
    """Ce que la carte ne voit pas doit être rendu AVEC elle. Mesuré : elle touche 0,45 % du
    corpus et 22 œuvres sur 40 n'y apparaissent jamais."""

    def test_les_oeuvres_muettes_sont_listees_avec_leur_part_de_phrases_trop_courtes(self):
        atomes = ([{"oeuvre": "vue", "nb_mots": 40} for _ in range(50)]
                  + [{"oeuvre": "muette", "nb_mots": 5} for _ in range(30)]
                  + [{"oeuvre": "muette", "nb_mots": 40} for _ in range(10)])
        evts = [{"oeuvre_a": "vue", "oeuvre_b": "vue", "poids": 2, "verdict": None}]
        cov = carte.couverture(evts, atomes, {"vue": {"titre": "Vue"}, "muette": {"titre": "Muette"}})
        self.assertEqual(cov["oeuvres_muettes"], 1)
        m = cov["muettes"][0]
        self.assertEqual(m["oeuvre"], "muette")
        # 30 des 40 phrases sont sous le seuil de comparabilité : c'est peut-être TOUTE
        # l'explication de son silence, et le lecteur doit pouvoir le voir.
        self.assertAlmostEqual(m["part_trop_courts"], 0.75, places=2)

    def test_les_actes_non_lus_sont_comptes(self):
        evts = [{"oeuvre_a": "x", "oeuvre_b": "y", "poids": 1, "verdict": None},
                {"oeuvre_a": "x", "oeuvre_b": "y", "poids": 1, "verdict": "confirme"}]
        cov = carte.couverture(evts, [{"oeuvre": "x", "nb_mots": 40}], {})
        self.assertEqual(cov["actes_non_lus"], 1)
        self.assertEqual(cov["actes"], 2)

    def test_un_acte_discordant_n_est_pas_compte_comme_non_lu(self):
        evts = [{"oeuvre_a": "x", "oeuvre_b": "y", "poids": 2, "verdict": None,
                 "etat_validation": "discordant"}]
        cov = carte.couverture(evts, [{"oeuvre": "x", "nb_mots": 40}], {})
        self.assertEqual(cov["actes_non_lus"], 0)
        self.assertEqual(cov["actes_discordants"], 1)

    def test_un_atome_cite_deux_fois_ne_compte_qu_une_fois(self):
        """DÉFAUT MESURÉ SUR LA MESURE ELLE-MÊME, et sur le chiffre le plus en vue de la page.

        La couverture rendait `somme(poids × 2)` : un nombre de CÔTÉS d'acte. Or un même atome
        peut appartenir à plusieurs actes — il est alors compté autant de fois. Le corpus publiait
        284 atomes touchés (0,52 %) là où il y en a 248 (0,454 %) : un surcompte de 14,5 % sur la
        seule mesure dont ce module a la charge, celle de dire ce que la carte NE voit PAS. La
        docstring de `couverture` portait déjà le bon chiffre — code et documentation se
        contredisaient.

        Ici, trois actes couvrent quatre côtés mais seulement TROIS atomes distincts : `x:a1`
        apparaît dans deux actes.
        """
        evts = [{"oeuvre_a": "x", "oeuvre_b": "y", "poids": 1, "verdict": None,
                 "atomes_a": ["x:a1"], "atomes_b": ["y:b1"]},
                {"oeuvre_a": "x", "oeuvre_b": "y", "poids": 1, "verdict": None,
                 "atomes_a": ["x:a1"], "atomes_b": ["y:b2"]}]
        atomes = [{"oeuvre": "x", "nb_mots": 40} for _ in range(100)]
        cov = carte.couverture(evts, atomes, {})
        self.assertEqual(cov["atomes_touches"], 3,
                         "un atome cité par deux actes a été compté deux fois")
        self.assertAlmostEqual(cov["part_touchee"], 0.03, places=4)

    def test_la_couverture_se_compte_sur_les_atomes_que_les_actes_declarent(self):
        """Contre-épreuve du test précédent : sans recouvrement, le compte est bien la somme des
        côtés — pour qu'on ne « corrige » pas un surcompte en fabriquant un sous-compte."""
        evts = [{"oeuvre_a": "x", "oeuvre_b": "y", "poids": 2, "verdict": None,
                 "atomes_a": ["x:a1", "x:a2"], "atomes_b": ["y:b1", "y:b2"]}]
        cov = carte.couverture(evts, [{"oeuvre": "x", "nb_mots": 40}] * 100, {})
        self.assertEqual(cov["atomes_touches"], 4)


class TestUnanimite(unittest.TestCase):
    def test_deux_paires_qui_se_contredisent_font_taire_l_acte(self):
        """Un acte hérite du sens de ses paires, mais seulement s'il est UNANIME : deux paires du
        même acte qui se contrediraient signaleraient une erreur de regroupement, et il vaut mieux
        ne rien dire que trancher au hasard."""
        paires = [_paire("x:a1", "y:b1", 1, 1, "Ein Satz mit vielen Woertern hier.",
                         "Ein Satz mit vielen Woertern hier.", sens="a_vers_b"),
                  _paire("x:a2", "y:b2", 2, 2, "Noch ein Satz mit Woertern.",
                         "Noch ein Satz mit Woertern.", sens="b_vers_a")]
        e = carte.evenements_de_carte({("A", "B"): paires}, {})[0]
        self.assertEqual(e["poids"], 2)
        self.assertIsNone(e["sens"])

    def test_une_source_tierce_dans_une_seule_paire_desoriente_tout_l_acte(self):
        """DOCTRINE VIOLÉE PAR L'AGRÉGATION, mesurée : 2 des 4 actes portant une source tierce
        étaient publiés ORIENTÉS, alors qu'aucun de leurs liens ne l'était.

        `comparaison.qualifier` pose `sens = None` dès que les deux passages nomment un auteur
        extérieur au corpus : chacun peut tenir sa formulation de ce tiers plutôt que de l'autre.
        Mais `_unanime` IGNORE les None — ce qu'il faut pour un verdict pas encore lu, et ce qui
        est faux ici, où le None est un refus délibéré de conclure. Un acte mêlant une paire à
        tiers et une paire sans tiers héritait donc du sens de la seconde et effaçait le refus de
        la première.
        """
        paires = [_paire("x:a1", "y:b1", 1, 1, "Sancho Pansa sagt es mit vielen Woertern hier.",
                         "Sancho Pansa sagt es mit vielen Woertern hier.",
                         source_tierce=True, sens=None),
                  _paire("x:a2", "y:b2", 2, 2, "Noch ein Satz mit vielen Woertern.",
                         "Noch ein Satz mit vielen Woertern.",
                         source_tierce=False, sens="a_vers_b")]
        e = carte.evenements_de_carte({("A", "B"): paires}, {})[0]
        self.assertTrue(e["source_tierce"], "le tiers d'une seule paire marque tout l'acte")
        self.assertIsNone(e["sens"], "un acte à source tierce ne doit JAMAIS être orienté")
        self.assertIsNone(e["sens_lu"], "y compris par une attribution écrite")


class TestReserve(unittest.TestCase):
    def test_la_reserve_dit_ce_que_la_carte_ne_voit_pas(self):
        """Une réserve qui ne parle que de ce que la mesure n'établit pas, sans dire ce qu'elle
        ne VOIT pas, laisse conclure d'un silence. C'était le cas de la première version."""
        r = carte.reserve()
        for attendu in ("ne relie pas", "0,45 %", "22 œuvres", "aveugle", "Le Bon"):
            self.assertIn(attendu, r, "réserve incomplète : %s" % attendu)


if __name__ == "__main__":
    unittest.main()


class TestMentions(unittest.TestCase):
    """LA SECONDE COUCHE, et elle pèse presque tout le volume de la carte.

    Mesuré : 2 899 mentions sur 2 796 phrases, contre 938 phrases touchées par un lien de
    reprise ; vingt-sept couples orientés contre dix ; recouvrement entre les deux quasi nul
    (3,8 % des mentions). Ce ne sont pas deux mesures du même fait, ce sont deux faits.

    Sans elle, la carte ment par omission : Ferenczi nomme Freud dans 960 de ses phrases et ne
    partage un texte avec lui que dans vingt-trois actes. Une carte des seuls actes le montrerait
    comme un satellite lointain de Freud.
    """

    def test_un_auteur_ne_se_nomme_pas_lui_meme(self):
        from core import comparaison
        atomes = [{"id": "x:1", "texte": "Nach Freuds Auffassung ist der Traum eine Erfüllung.",
                   "oeuvre": "x"}]
        m = comparaison.mentions(atomes, "Sigmund Freud")
        self.assertEqual(m, [], "se nommer soi-même n'est pas nommer autrui")

    def test_ferenczi_est_dans_la_table_des_noms(self):
        """OUBLI RÉEL, trouvé en auditant la carte. Sándor Ferenczi est entré dans le corpus sans
        que son nom entre dans `comparaison.NOMS` : il pesait 16,8 % des atomes et AUCUN auteur
        ne pouvait être enregistré comme le nommant. Le couple Freud ↔ Ferenczi paraissait donc
        unidirectionnel — un accident de configuration présenté comme un fait de texte.
        Mesuré après correction : 80 atomes le nomment."""
        from core import comparaison
        self.assertIn("Sándor Ferenczi", comparaison.NOMS)
        atomes = [{"id": "x:1", "texte": "Wie Ferenczi in seiner Genitaltheorie zeigte.",
                   "oeuvre": "x"}]
        m = comparaison.mentions(atomes, "Sigmund Freud")
        self.assertEqual([x["auteur_nomme"] for x in m], ["Sándor Ferenczi"])

    def test_tous_les_auteurs_du_corpus_ont_un_jeton(self):
        """Le garde-fou qui empêche l'oubli de se reproduire : tout auteur ayant des atomes doit
        pouvoir être nommé, sinon la couche des mentions le rend invisible en silence."""
        from core import comparaison
        from core.corpus import Corpus
        auteurs = {a.get("auteur", "Sigmund Freud") for a in Corpus().atomes}
        manquants = auteurs - set(comparaison.NOMS)
        self.assertFalse(manquants, "auteurs sans jeton de nom : %s" % sorted(manquants))

    def test_l_homographe_est_porte_par_la_mention(self):
        """« Abraham » désigne aussi le patriarche biblique, que Rank et Freud citent abondamment
        dans leurs travaux sur le mythe. L'avertissement voyage avec la mention, il n'est pas
        relégué dans une note — et la lecture des 2 899 mentions a montré qu'il était FONDÉ :
        sur les 145 mentions portant ce nom, 57 ont été rejetées, soit 39 %. Aucun autre nom du
        corpus n'approche ce taux."""
        from core import comparaison
        atomes = [{"id": "x:1", "texte": "Der Traum Abrahams von der Opferung des Sohnes Isaak.",
                   "oeuvre": "x"}]
        m = comparaison.mentions(atomes, "Otto Rank")
        self.assertEqual(len(m), 1)
        self.assertTrue(m[0]["homographe"], "l'avertissement d'homographe manque")
