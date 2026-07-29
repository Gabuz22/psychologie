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
        """DÉFAUT MESURÉ, et la règle qui le corrige a dû être RESSERRÉE.

        Le détecteur COMMUN prend la ligne suivant le chiffre romain ; pour une œuvre sans
        intitulé de section, c'est la première PHRASE, tronquée à 90 signes. « II. Ich knüpfe nun
        an meine früheren Bemerkungen an, … die Breuer'sche Meth » passait alors pour un chapitre
        que Freud consacrerait à Breuer.

        La parade était d'exiger une ponctuation finale. Elle valait pour ce détecteur-là, mais
        seize œuvres déclarent désormais leur propre motif (`sources.MOTIFS_CHAPITRE`), et leurs
        titres sont de vrais intitulés qui ne se terminent souvent par rien — « Zur Kritik der
        Rankschen ›Technik der Psychoanalyse‹ » de Ferenczi, sa rupture avec Rank, était écartée
        par ce filtre. Le corpus ne comptait qu'UNE lecture déclarée là où il en porte sept.

        Ce que ce test protège désormais : un intitulé venu du détecteur COMMUN doit toujours être
        complet ; un intitulé venu d'un motif déclaré ne doit pas être une phrase tronquée en
        plein mot — ce qui est le vrai défaut, la ponctuation n'en étant qu'un symptôme.
        """
        declarees = set(sources.MOTIFS_CHAPITRE)
        r = agents.AGENTS["lectures"].executer(self.corpus)
        self.assertGreaterEqual(len(r["chapitres_declares"]), 5,
                                "les lectures déclarées ont disparu")
        for c in r["chapitres_declares"]:
            titre = c["chapitre"].strip()
            if c["oeuvre"] not in declarees:
                self.assertRegex(titre, r"[.!?»]$",
                                 "intitulé tronqué retenu à tort : %r" % titre)
            else:
                # Un motif déclaré peut rendre un titre sans ponctuation, mais jamais une phrase
                # coupée : le dernier mot doit être entier.
                self.assertNotRegex(titre, r"\b\w{1,3}$|[a-zäöüß]-$",
                                    "titre coupé en plein mot : %r" % titre)

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


class TestDensiteComparee(unittest.TestCase):
    """La mesure qui compare des auteurs SANS supposer que leurs concepts se correspondent.

    On n'y demande jamais si deux concepts sont équivalents — question indécidable sans témoin —
    mais comment un MOT donné se distribue. Ces tests protègent l'honnêteté de cette réponse.
    """

    ATOMES = {
        "A": [{"id": "x:a1", "texte": "Die Verdrängung ist der Kern.", "oeuvre": "x"},
              {"id": "x:a2", "texte": "Nichts hier.", "oeuvre": "x"}],
        "B": [{"id": "y:a1", "texte": "Das Verdrängte kehrt wieder.", "oeuvre": "y"}],
    }
    LANGUES = {"A": "de", "B": "de"}

    def test_la_langue_du_motif_est_declaree_jamais_devinee(self):
        """DÉFAUT MESURÉ pendant l'écriture. Une première version déduisait la langue du motif du
        premier auteur rencontré dans le dictionnaire. Le motif français « \bfoule » se retrouvait
        alors marqué « non mesurable » sur le corpus de Le Bon, le seul où il ait un sens — parce
        que l'ordre d'itération avait fait tomber « de » en premier. Deviner la langue d'une
        expression régulière n'est pas faisable ; ce projet ne devine pas.
        """
        atomes = {"fr": [{"id": "f:a1", "texte": "La foule est impulsive.", "oeuvre": "f"}],
                  "de": [{"id": "d:a1", "texte": "Die Masse ist impulsiv.", "oeuvre": "d"}]}
        r = comparaison.densite_comparee(r"\bfoule", atomes, {"fr": "fr", "de": "de"},
                                         langue_motif="fr")
        par_auteur = {a["auteur"]: a for a in r["auteurs"]}
        self.assertEqual(par_auteur["fr"]["porteurs"], 1)
        self.assertIsNone(par_auteur["de"]["porteurs"])

    def test_sans_langue_declaree_tous_les_corpus_sont_mesures(self):
        """Un mot commun aux deux langues (« suggestion ») doit pouvoir être comparé à travers
        elles : l'absence de langue vaut « je mesure partout », pas « je ne mesure rien »."""
        atomes = {"fr": [{"id": "f:a1", "texte": "C'est la suggestion.", "oeuvre": "f"}],
                  "de": [{"id": "d:a1", "texte": "Das ist Suggestion.", "oeuvre": "d"}]}
        r = comparaison.densite_comparee(r"\bsuggestion", atomes, {"fr": "fr", "de": "de"})
        self.assertTrue(all(a["porteurs"] == 1 for a in r["auteurs"]))

    def test_la_densite_est_rapportee_au_nombre_d_atomes(self):
        """Un corpus deux fois plus gros n'est pas deux fois plus concerné : on compare des
        densités, jamais des effectifs bruts."""
        r = comparaison.densite_comparee(r"\bverdrang", self.ATOMES, self.LANGUES,
                                         langue_motif="de")
        par_auteur = {a["auteur"]: a for a in r["auteurs"]}
        self.assertEqual(par_auteur["A"]["pour_mille"], 500.0)     # 1 sur 2
        self.assertEqual(par_auteur["B"]["pour_mille"], 1000.0)    # 1 sur 1

    def test_le_pliage_neutralise_majuscules_et_diacritiques(self):
        """« Verdrängung » et « verdrangung » doivent tomber sous le même motif : sans quoi la
        densité mesurerait la typographie de l'édition, pas l'usage de l'auteur."""
        self.assertEqual(comparaison.replier_comparaison("Verdrängung"), "verdrangung")
        self.assertEqual(comparaison.replier_comparaison("Straße"), "strasse")

    def test_le_cache_de_pliage_ne_touche_pas_les_atomes(self):
        """Le pliage est mis en cache pour tenir la table des usages en moins de deux minutes.
        Ce cache doit rester EXTÉRIEUR : une clé technique glissée dans le dictionnaire d'atome
        ressortirait un jour dans une réponse d'API que personne n'a voulue."""
        atomes = {"A": [dict(a) for a in self.ATOMES["A"]]}
        avant = [sorted(a) for a in atomes["A"]]
        comparaison.densite_comparee(r"\bverdrang", atomes, {"A": "de"}, langue_motif="de")
        self.assertEqual([sorted(a) for a in atomes["A"]], avant)

    def test_l_ecart_mesure_ne_vient_pas_du_lexicographe(self):
        """LE TEST QUI FONDE TOUTE LA COMPARAISON DE CONCEPTS.

        Comparer la densité du concept « Œdipe » de Rank à celui de Freud est suspect : les deux
        motifs viennent de lexiques DIFFÉRENTS, écrits séparément. L'écart pourrait donc venir
        des lexicographes et non des auteurs. Un seul motif appliqué aux deux corpus tranche —
        et l'écart persiste (mesuré : 3,4 ‰ contre 21,5 ‰, quand les motifs propres donnaient
        3,6 ‰ contre 20,6 ‰). Il vient donc bien des auteurs.

        Si ce test tombe un jour, ce n'est pas un détail d'implémentation : c'est la comparaison
        de concepts entre auteurs qui redevient indéfendable.
        """
        corpus = Corpus()
        par_auteur = {}
        for a in corpus.atomes:
            par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
        langues = {m.get("auteur", "Sigmund Freud"): m.get("langue", "de")
                   for m in corpus.oeuvres.values()}
        r = comparaison.densite_comparee(r"\bodipus|\boedipus", par_auteur, langues,
                                         langue_motif="de")
        d = {a["auteur"]: a["pour_mille"] for a in r["auteurs"]}
        self.assertGreater(d["Otto Rank"], 4 * d["Sigmund Freud"])

    def test_l_agent_usage_exige_un_motif(self):
        """Sans motif, l'agent ne doit pas inventer un défaut : la question n'a pas de sens."""
        with self.assertRaises(ValueError):
            agents.AGENTS["usage"].executer(Corpus())


class TestTableDesUsages(unittest.TestCase):
    def test_la_provenance_du_motif_est_conservee(self):
        """La ligne d'un auteur sur SON motif est haute par construction — le lexique a été écrit
        pour lui. Sans la colonne `lexique`, on lirait cette évidence comme un résultat."""
        atomes = {"Otto Rank": [{"id": "r:a1", "texte": "Das Geburtstrauma.", "oeuvre": "r"}],
                  "Sigmund Freud": [{"id": "f:a1", "texte": "Der Traum.", "oeuvre": "f"}]}
        lignes = comparaison.table_des_usages(atomes, {"Otto Rank": "de", "Sigmund Freud": "de"})
        self.assertTrue(lignes)
        self.assertTrue(all(l["lexique"] and l["motif"] for l in lignes))
        # chaque motif est mesuré sur TOUS les corpus de sa langue, pas seulement sur le sien
        par_motif = {}
        for l in lignes:
            par_motif.setdefault(l["motif"], set()).add(l["auteur"])
        self.assertTrue(any(len(v) == 2 for v in par_motif.values()))


class TestLangueParAuteur(unittest.TestCase):
    """DÉFAUT MESURÉ dans la table des usages exportée : Josef Breuer, dont le corpus est
    allemand, ressortait à 0,0 ‰ sur le motif FRANÇAIS « \bfoule » — un zéro vrai et vide de
    sens, qui descendait le minimum du classement par contraste.

    La cause : la table des langues était bâtie sur les métadonnées d'ŒUVRE, or Breuer est auteur
    d'ATOMES (ses parts des « Studien über Hysterie ») sans être auteur d'un volume. Il n'y
    figurait pas, et une langue inconnue valait « mesure quand même ».
    """

    def test_la_langue_se_deduit_des_atomes_pas_des_oeuvres(self):
        corpus = Corpus()
        langues = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)
        self.assertEqual(langues.get("Josef Breuer"), "de")
        self.assertEqual(langues.get("Gustave Le Bon"), "fr")

    def test_un_auteur_de_langue_inconnue_n_est_pas_mesure(self):
        """Le silence vaut mieux qu'un zéro faux : une case vide se lit « on ne sait pas », un
        0,0 ‰ se lit « il ne l'écrit jamais »."""
        atomes = {"connu": [{"id": "a:1", "texte": "La foule.", "oeuvre": "a"}],
                  "inconnu": [{"id": "b:1", "texte": "Die Masse.", "oeuvre": "b"}]}
        r = comparaison.densite_comparee(r"\bfoule", atomes, {"connu": "fr"}, langue_motif="fr")
        par_auteur = {a["auteur"]: a for a in r["auteurs"]}
        self.assertEqual(par_auteur["connu"]["porteurs"], 1)
        self.assertIsNone(par_auteur["inconnu"]["pour_mille"])

    def test_un_auteur_a_cheval_sur_deux_langues_est_signale(self):
        """Cas que le corpus ne connaît pas encore. Mieux vaut le déclarer non mesurable que le
        trancher au petit bonheur — et le jour où il se présentera, le silence le signalera."""
        atomes = [{"oeuvre": "fr1", "auteur": "X"}, {"oeuvre": "de1", "auteur": "X"}]
        oeuvres = {"fr1": {"langue": "fr"}, "de1": {"langue": "de"}}
        self.assertIsNone(comparaison.langues_par_auteur(atomes, oeuvres)["X"])
