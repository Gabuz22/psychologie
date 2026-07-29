#!/usr/bin/env python3
"""TESTS de Sándor Ferenczi — quatrième auteur doté de son propre lexique.

Ferenczi complète la figure que Rank et Abraham avaient laissée incomplète. Rank déplace une
thèse et rompt ; Abraham prolonge et ne rompt pas ; Ferenczi reste vingt ans le plus proche de
Freud et diverge sur ce que l'analyste FAIT. Trois formes du rapport au maître, chacune décrite
avec ses propres catégories — c'est cette dernière clause que la plupart des tests protègent.

Son intégration a soulevé deux problèmes que le corpus n'avait pas encore rencontrés, et deux
tests leur répondent nommément : un même texte imprimé DEUX FOIS (tirés à part puis recueils),
et un texte d'un AUTRE AUTEUR imprimé au milieu d'un volume.
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import atomisation, collation, comparaison, lexique, lexiques, ocr, sources  # noqa: E402
from core.corpus import Corpus                                             # noqa: E402

FERENCZI = "Sándor Ferenczi"
OEUVRES = ["populaere_vortraege", "genitaltheorie", "bausteine_1", "bausteine_2", "bausteine_3"]


class TestSourcesFerenczi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.charges = {c: sources.charger(c) for c in OEUVRES}

    def test_les_cinq_volumes_sont_declares_de_ferenczi(self):
        for c, r in self.charges.items():
            self.assertEqual(r["meta"]["auteur"], FERENCZI, c)
            self.assertEqual(r["meta"]["langue"], "de", c)

    def test_toutes_les_bornes_ont_ete_trouvees(self):
        """DÉFAUT RÉEL, attrapé par le garde-fou pendant l'intégration. La borne de fin de la
        « Genitaltheorie » avait été relevée sur le fac-similé BRUT (« Eine psycho- »), alors que
        la coupe s'applique APRÈS recollage des césures. Le chargement ne l'a pas trouvée et l'a
        dit — au lieu de laisser 7 500 signes de catalogue d'éditeur dans le texte de l'auteur.
        Ce test transforme cet avertissement en échec, pour toutes les œuvres du corpus.
        """
        for cle in sources.OEUVRES:
            note = sources.charger(cle)["meta"]["bornage_gutenberg"]
            self.assertNotIn("introuvable", note, cle)
            self.assertNotIn("non appliquée", note, cle)

    def test_qualite_ocr_sous_le_seuil(self):
        """Cinq fac-similés non relus. Le seuil est de 2,0 % de phrases atteintes ; ils sont
        tous sous 0,30 %, ce qui est la meilleure série du corpus."""
        for c, r in self.charges.items():
            taux = ocr.corruption(r["texte"])["taux_phrases_pct"]
            self.assertLessEqual(taux, ocr.SEUIL_PHRASES_CORROMPUES_PCT, "%s : %.2f %%" % (c, taux))

    def test_aucun_volume_ne_se_termine_sur_du_paratexte(self):
        """Une borne de fin mal posée laisse un catalogue d'éditeur, qui produit des atomes
        absurdes (« Preis M 10.-- »). On vérifie que la dernière phrase est de la prose."""
        for c, r in self.charges.items():
            fin = r["texte"][-400:]
            self.assertNotIn("VERLAG", fin, c)
            self.assertNotIn("Auflage", fin, c)

    def test_le_texte_co_signe_avec_rank_est_retire(self):
        """LE CAS QUI A CRÉÉ `REGIONS_ECARTEES`.

        Les Bausteine III réimpriment « Entwicklungsziele der Psychoanalyse » (1924), tiré du
        livre co-signé par Ferenczi et Otto Rank. Les éditeurs du volume écrivent eux-mêmes en
        note que seul le chapitre III est attesté de Ferenczi, et que les chapitres I et V lui
        sont attribués parce que sa veuve croit s'en souvenir et qu'ils croient reconnaître son
        style — leur lettre à Rank étant restée sans réponse.

        Un corpus qui existe pour rendre ses attributions vérifiables ne peut pas retenir un
        texte attribué sur un souvenir. On RETIRE, ce qui est décidable, au lieu d'ATTRIBUER,
        ce qui ne l'est pas ici.
        """
        t = self.charges["bausteine_3"]["texte"]
        self.assertNotIn("Wechselbeziehung von Theorie", t)
        self.assertNotIn("Frau Dr. Ferenczi glaubt", t)
        self.assertIn("région(s) écartée(s)",
                      self.charges["bausteine_3"]["meta"]["bornage_gutenberg"])

    def test_une_region_introuvable_fait_echouer_bruyamment(self):
        """Une région qu'on CROIT écartée et qui reste dans le texte est pire que pas de
        mécanisme du tout : elle attribuerait à Ferenczi un texte qu'on aurait cru retiré."""
        sources.REGIONS_ECARTEES["__essai__"] = [("MARQUEUR ABSENT", "AUTRE ABSENT", "essai")]
        try:
            with self.assertRaises(ValueError):
                sources._retirer_regions_ecartees("un texte quelconque", "__essai__")
        finally:
            del sources.REGIONS_ECARTEES["__essai__"]

    def test_aucun_volume_n_en_duplique_un_autre(self):
        """LE SECOND PROBLÈME PROPRE À CET AUTEUR.

        Trois tirés à part de Ferenczi existent sur Internet Archive ET sont réimprimés dans les
        Bausteine — recouvrement mesuré de 49,6 %, 56,4 % et 46,4 % en suites de huit mots. Les
        retenir aurait compté deux fois les mêmes phrases et faussé TOUTES les densités du corpus,
        y compris celles des autres auteurs par comparaison. Ils sont donc écartés, et tracés
        dans `FAC_SIMILES_ECARTES` pour que le prochain qui les trouve sache pourquoi.

        Ce test vérifie que les cinq volumes RETENUS, eux, ne se recouvrent pas.
        """
        grammes = {c: collation.ngrammes(collation.normaliser(r["texte"]), 8)
                   for c, r in self.charges.items()}
        for i, a in enumerate(OEUVRES):
            for b in OEUVRES[i + 1:]:
                inter = len(grammes[a] & grammes[b])
                part = inter / max(min(len(grammes[a]), len(grammes[b])), 1)
                self.assertLess(part, 0.05, "%s et %s se recouvrent à %.1f %%" % (a, b, 100 * part))

    def test_les_tires_a_part_duplicats_sont_traces(self):
        """Une décision NÉGATIVE non écrite sera refaite : le prochain qui trouvera ces scans les
        croira utilisables. La trace doit porter la MESURE qui a motivé l'écart, pas seulement le
        fait qu'on les a écartés."""
        import re
        for ident in ("IntrojektioneUndUbertragung", "HysterieUndPathoneurosen",
                      "Ferenczi_1925_Sexualgewohnheiten_k"):
            self.assertIn(ident, sources.FAC_SIMILES_ECARTES)
            trace = sources.FAC_SIMILES_ECARTES[ident]
            self.assertIn("Bausteine", trace, ident)
            self.assertRegex(trace, r"\d+,\d+ %", ident)

    def test_le_volume_posthume_porte_sa_reserve(self):
        """Les Bausteine III sont posthumes : préface d'un tiers, notes d'éditeurs dans le corps,
        une pièce venue d'une monographie co-signée avec Hollós. Rien de cela n'est un défaut à
        corriger — mais tout cela doit être DIT dans les métadonnées, pas seulement en commentaire.
        """
        meta = self.charges["bausteine_3"]["meta"]
        self.assertIn("reserve_attribution", meta)
        self.assertIn("Rank", meta["reserve_attribution"])
        self.assertEqual(meta["annee_edition"], 1939)   # le volume porte 1939, non 1938

    def test_la_datation_des_recueils_est_une_fenetre_large_et_assumee(self):
        """Un recueil de 1927 réunissant des articles de 1909 à 1926 ne date aucun atome de 1927.
        La fenêtre EST l'incertitude ; l'aplatir serait mentir sur ce que le corpus sait."""
        for cle in ("bausteine_1", "bausteine_2", "bausteine_3", "populaere_vortraege"):
            m = self.charges[cle]["meta"]
            self.assertLess(m["annee_oeuvre"], m["annee_edition"] - 5, cle)
        # Contre-épreuve : la Genitaltheorie est un inédit, sa datation est exacte.
        g = self.charges["genitaltheorie"]["meta"]
        self.assertEqual(g["annee_oeuvre"], g["annee_edition"])

    def test_le_plus_gros_volume_n_est_plus_muet(self):
        """LE DERNIER VOLUME SANS AUCUN CHAPITRE, et le plus lourd du corpus — 3 627 atomes.

        Son motif a dû composer avec une mise en page qui CHANGE en cours de volume : les pièces
        anciennes portent leur année seule sur une ligne sous le titre (« (1908) », « (etwa 1909) »),
        les pièces de 1926-1933 ne portent plus l'année mais la mention de la séance où elles furent
        lues. Les deux terminaisons sont relevées dans le texte, et la table des matières du volume
        (« Originalarbeiten aus den Jahren 1908—1933 ») sert de vérité de terrain.
        """
        r = atomisation.chapitres(self.charges["bausteine_3"]["texte"], "de",
                                  sources.MOTIFS_CHAPITRE["bausteine_3"])
        self.assertGreaterEqual(len(r), 45, "le chapitrage des Bausteine III a reculé")

    def test_aucune_tete_courante_n_est_prise_pour_un_titre(self):
        """CE QUI A FAIT ÉCARTER LE SIGNAL DE MISE EN PAGE SEUL, mesuré : il retenait vingt-six
        têtes courantes, dont « S. Ferenczi » douze fois et « Die Bedeutung Freuds … 303 » trois fois.

        L'enjeu n'est pas cosmétique. Un motif DÉCLARÉ contourne le filtre de ponctuation de
        `comparaison._INTITULE_COMPLET` — c'est voulu, les vrais titres de Ferenczi n'ont pas de
        point final — donc chaque tête courante retenue fabriquerait une FAUSSE lecture déclarée,
        répétée autant de fois que la page.

        Le discriminant n'est PAS le numéro de page. Une première version de ce test refusait tout
        titre finissant par un chiffre, et elle a échoué sur un vrai titre abîmé par le scan
        (« Liöbesult über die Rolle des er 5 ») : elle mesurait la cicatrice d'OCR au lieu du défaut.
        Ce qui caractérise une tête courante, c'est qu'elle SE RÉPÈTE — une par page — et qu'elle
        porte souvent le seul nom de l'auteur du volume. Ce sont ces deux propriétés qui sont
        vérifiées, et ce sont elles qui rendraient une fausse lecture déclarée possible.
        """
        for cle in ("bausteine_1", "bausteine_2", "bausteine_3"):
            titres = [t for _, _, t in atomisation.chapitres(
                self.charges[cle]["texte"], "de", sources.MOTIFS_CHAPITRE[cle])]
            vus = {}
            for titre in titres:
                nu = re.sub(r"[^a-zäöüß]", "", titre.lower())
                self.assertNotIn(nu, ("sferenczi", "ferenczi", "sferenezi"),
                                 "%s : le nom de l'auteur pris pour un titre — %r" % (cle, titre))
                # Une tête courante reprend le titre de l'article page après page : deux repères
                # qui commencent pareil ET nomment un auteur du corpus sont le cas dangereux.
                if any(re.search(j, comparaison.aplatir(titre))
                       for jetons in comparaison.NOMS.values() for j in jetons):
                    tete = nu[:18]
                    self.assertNotIn(tete, vus,
                                     "%s : deux titres nommant un auteur commencent pareil, "
                                     "signe d'une tête courante — %r et %r"
                                     % (cle, vus.get(tete), titre))
                    vus[tete] = titre

    def test_ferenczi_lit_freud_dans_le_volume_posthume(self):
        """CE QUE LE CHANTIER CHERCHAIT. Deux pièces des Bausteine III annoncent Freud dans leur
        titre — « Die Bedeutung Freuds für die Mental Hygiene-Bewegung » (1926) et « Freuds Einfluss
        auf die Medizin » (1933). Elles étaient dans le corpus depuis l'entrée de Ferenczi ; aucun
        détecteur ne pouvait les voir."""
        titres = [t for _, _, t in atomisation.chapitres(
            self.charges["bausteine_3"]["texte"], "de", sources.MOTIFS_CHAPITRE["bausteine_3"])]
        nommant_freud = [t for t in titres if "Freud" in t]
        self.assertGreaterEqual(len(nommant_freud), 2,
                                "les titres nommant Freud ont disparu : %r" % titres)


class TestTetesCourantes(unittest.TestCase):
    """DÉFAUT MESURÉ, trouvé en lisant les atomes les plus longs de Ferenczi — puis retrouvé dans
    TOUT le corpus de fac-similés.

    L'imprimeur répète en haut de chaque page le titre de l'ouvrage, du chapitre ou le nom de
    l'auteur. L'OCR la lit comme une ligne ordinaire, et comme elle tombe entre les deux moitiés
    d'une phrase que la page a coupée, elle se retrouve SOUDÉE au milieu de cette phrase. Elle
    échappe à `retirer_blocs_illisibles` : « 122 S. Ferenczi » est parfaitement lisible.

    1 544 lignes dans le corpus. Le dégât n'est pas la longueur des atomes (281 signes avant,
    281 après) : c'est (1) les suites de six mots brisées au milieu des phrases, unité exacte de
    la couche de comparaison, et (2) le COMPTE DES CONCEPTS — « Das Trauma der Geburt » figure
    85 fois en tête de page dans le livre de Rank de 1924, « Versuch einer Genitaltheorie » 48
    fois chez Ferenczi. Le titre de l'ouvrage gonflait la densité du concept dont l'ouvrage
    traite : un artefact typographique qui ressemblait exactement au résultat attendu.
    """

    def test_la_tete_courante_repetee_est_retiree(self):
        t = "\n".join(["Erste Zeile."] + ["%d S. Ferenczi" % n for n in (10, 12, 14, 16, 18)]
                      + ["Letzte Zeile."])
        propre, r = ocr.retirer_tetes_courantes(t)
        self.assertEqual(r["tetes_retirees"], 5)
        self.assertNotIn("S. Ferenczi", propre)
        self.assertIn("Erste Zeile.", propre)
        self.assertIn("Letzte Zeile.", propre)

    def test_la_regle_ne_connait_aucun_titre(self):
        """Elle ne repère pas ce qu'on lui a dit de chercher : elle repère ce qui SE RÉPÈTE.
        Un titre jamais vu du code est retiré comme les autres."""
        t = "\n".join(["a."] + ["%d Versuch einer Genitaltheorie" % n for n in range(2, 40, 2)])
        _, r = ocr.retirer_tetes_courantes(t)
        self.assertEqual(r["tetes_retirees"], 19)

    def test_une_ligne_repetee_avec_LE_MEME_numero_n_est_pas_une_tete(self):
        """LA CONDITION QUI PROTÈGE LE TEXTE. Une tête courante change de numéro à chaque page.
        Une ligne répétée avec toujours le même chiffre est autre chose — un artefact de scan,
        un refrain, une entrée d'index — et le texte n'a pas à en décider ici."""
        t = "\n".join(["7 Der Wanderer"] * 8)
        _, r = ocr.retirer_tetes_courantes(t)
        self.assertEqual(r["tetes_retirees"], 0)

    def test_une_ligne_sans_numero_n_est_jamais_touchee(self):
        t = "\n".join(["Die Verdrängung ist der Kern."] * 9)
        propre, r = ocr.retirer_tetes_courantes(t)
        self.assertEqual(r["tetes_retirees"], 0)
        self.assertEqual(propre, t)

    def test_sous_le_seuil_de_repetition_rien_n_est_retire(self):
        """Quatre occurrences ne font pas une tête courante : le seuil est à cinq, et il est
        volontairement haut — mieux vaut laisser passer une tête que manger une phrase."""
        t = "\n".join(["%d S. Ferenczi" % n for n in (10, 12, 14, 16)])
        _, r = ocr.retirer_tetes_courantes(t)
        self.assertEqual(r["tetes_retirees"], 0)

    def test_une_phrase_qui_nomme_l_auteur_n_est_pas_touchee(self):
        """Une note où Ferenczi cite son propre article ne doit pas disparaître : c'est du texte,
        pas de l'apparat. Il en reste une, réelle, dans les Bausteine I."""
        t = "\n2) S. Ferenczi, Introjektion und Übertragung. 1909. (S. 9 ff.)\n"
        propre, r = ocr.retirer_tetes_courantes(t * 6)
        self.assertEqual(r["tetes_retirees"], 0)

    def test_les_volumes_charges_n_en_contiennent_plus(self):
        import re
        motif = re.compile(r"^[^\w\n]*\d{1,4}[^\w\n]+S[.,]?\s*Ferenczi[^\w\n]*$", re.M)
        for cle in ("bausteine_1", "bausteine_2", "bausteine_3"):
            restantes = motif.findall(sources.charger(cle)["texte"])
            self.assertFalse(restantes, "%s : %s" % (cle, restantes[:3]))

    def test_le_corpus_entier_en_est_debarrasse(self):
        """Le retrait vaut pour TOUS les fac-similés, pas seulement pour Ferenczi : Rank et
        Abraham en portaient aussi. Un second passage ne doit plus rien trouver."""
        for cle, m in sources.OEUVRES.items():
            if m.get("provenance") != "archive":
                continue
            _, r = ocr.retirer_tetes_courantes(sources.charger(cle)["texte"])
            self.assertEqual(r["tetes_retirees"], 0, "%s : %s" % (cle, r["formes"][:3]))


class TestLexiqueFerenczi(unittest.TestCase):

    def test_il_a_son_propre_lexique(self):
        self.assertIn(FERENCZI, lexiques.PAR_AUTEUR)
        self.assertEqual(lexiques.PAR_AUTEUR[FERENCZI].LANGUE, "de")

    def test_les_quatre_lexiques_sont_distincts(self):
        """L'INVARIANT DU PROJET. Si deux auteurs partageaient leurs catégories, le jour où l'on
        mesurera un socle partagé, on ne mesurerait que la grille commune qu'on leur a imposée.
        """
        jeux = {}
        for auteur, module in lexiques.PAR_AUTEUR.items():
            jeux[auteur] = {(g, s) for g, m in module.CONCEPTS.items() for s in m["termes"]}
        jeux["Sigmund Freud"] = {(g, s) for g, m in lexique.CONCEPTS.items() for s in m["termes"]}
        noms = sorted(jeux)
        for i, a in enumerate(noms):
            for b in noms[i + 1:]:
                self.assertNotEqual(jeux[a], jeux[b], "%s et %s ont le même jeu" % (a, b))

    def test_concepts_signature(self):
        """Sa contribution propre : la théorie génitale. Aucun autre auteur du corpus n'écrit
        « amphimixis » — le mot est de lui, et il ne désigne rien chez les autres."""
        phrase = ("Die Amphimixis der Erotismen führt zur genitalen Regression in den "
                  "Mutterleib, zur thalassalen Regressionstendenz.")
        c = {x["concept"] for x in lexique.concepts_de(phrase, FERENCZI)}
        self.assertIn("amphimixis", c)

    def test_la_technique_est_un_domaine_propre(self):
        """Là où Rank déplace une thèse et Abraham prolonge une doctrine, Ferenczi change ce que
        l'analyste FAIT. Sa divergence est technique, et son lexique doit le montrer."""
        phrase = ("Die aktive Technik wurde später durch die Relaxation und die Neokatharsis "
                  "ergänzt; die Gegenübertragung des Analytikers verlangt Beachtung.")
        c = {x["concept"] for x in lexique.concepts_de(phrase, FERENCZI)}
        self.assertTrue(c, "aucun concept technique reconnu")


class TestCorpusFerenczi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()
        cls.atomes = [a for a in cls.corpus.atomes if a.get("auteur") == FERENCZI]

    def test_son_corpus_pese_assez_pour_etre_compare(self):
        """2,6 millions de signes retenus — deuxième corpus du projet en VOLUME DE TEXTE, après
        Freud. En nombre d'ATOMES il vient troisième, derrière Rank : ses phrases sont plus
        longues (281 signes en moyenne contre 232 chez Rank et 227 chez Freud). L'écart est
        réel et mesuré, non un défaut de segmentation — le taux de frontière de phrase manquée
        est de 4,8 à 7,7 % chez lui contre 4,4 % dans la Traumdeutung, du même ordre.

        Un auteur sous-représenté ne peut pas être comparé aux autres sans que la taille de son
        corpus explique tout : c'est ce seuil-là que le test protège."""
        self.assertGreater(len(self.atomes), 8000)
        signes = sum(len(a["texte"]) for a in self.atomes)
        self.assertGreater(signes, 2_000_000)

    def test_les_atomes_portent_leur_oeuvre_et_leur_fenetre(self):
        """Aucun atome d'un recueil n'est daté de l'année du recueil : il porte la fenêtre
        [première parution, édition]. Pour les Bausteine III, c'est [1908, 1939] — trente et un
        ans d'incertitude, et il vaut mieux les porter que les cacher."""
        from core.corpus import fenetre_datation
        for a in self.atomes[:2000]:
            self.assertIn(a["oeuvre"], OEUVRES)
            debut, fin = fenetre_datation(a)
            self.assertLessEqual(debut, fin)
            self.assertGreaterEqual(debut, 1907)

    def test_son_vocabulaire_le_distingue_dans_le_corpus(self):
        """CONTRÔLE DE BOUT EN BOUT. « begattung », « genitalitat », « homoerotik » ont été
        mesurés 25 à 57 fois plus fréquents chez lui que dans le reste du corpus allemand. Si ce
        test tombe, c'est que le texte chargé n'est pas celui qu'on croit."""
        from core import comparaison
        par_auteur = {}
        for a in self.corpus.atomes:
            par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
        langues = {m.get("auteur", "Sigmund Freud"): m.get("langue", "de")
                   for m in self.corpus.oeuvres.values()}
        r = comparaison.densite_comparee(r"\bbegattung|\bamphimix|\bgenitalitat",
                                         par_auteur, langues, langue_motif="de")
        d = {x["auteur"]: x["pour_mille"] for x in r["auteurs"]}
        self.assertGreater(d[FERENCZI], 5 * max(v for a, v in d.items()
                                                if a != FERENCZI and v is not None))


if __name__ == "__main__":
    unittest.main()
