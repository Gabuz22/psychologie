#!/usr/bin/env python3
"""TESTS de la base d'atomisation — ils protègent les invariants, pas le confort.

Chaque test correspond à une garantie annoncée dans la documentation. Si une garantie tombe, un
test doit tomber : c'est ce qui distingue une base fiable d'une base qui a l'air de marcher.
Stdlib seulement (unittest), aucune dépendance, exécutable partout.
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import atomisation, lexique, sources          # noqa: E402
from core.segmentation import recomposable, segmenter   # noqa: E402


class TestSegmentation(unittest.TestCase):
    """Le découpage en phrases : la brique dont tout dépend."""

    def test_phrase_simple(self):
        p = segmenter("Der Traum ist eine Wunscherfüllung. Das ist die These.")
        self.assertEqual(len(p), 2)
        self.assertEqual(p[0]["texte"], "Der Traum ist eine Wunscherfüllung.")

    def test_abreviation_ne_coupe_pas(self):
        """« z. B. » et « d. h. » sont omniprésents chez Freud : les couper briserait les atomes."""
        for abbr in ("z. B.", "d. h.", "u. dgl.", "vgl."):
            t = "Man sieht dies %s im Traum vom Onkel." % abbr
            self.assertEqual(len(segmenter(t)), 1, "coupé sur « %s »" % abbr)

    def test_initiale_ne_coupe_pas(self):
        """L'anonymisation des patients par initiale est constante (« Dr. M. »)."""
        self.assertEqual(len(segmenter("Dr. M. ist mit meiner Lösung nicht einverstanden.")), 1)

    def test_ordinal_ne_coupe_pas(self):
        self.assertEqual(len(segmenter("In der 3. Auflage habe ich das geändert.")), 1)

    def test_liste_numerotee_se_decoupe(self):
        """Freud énumère ses rêves (« 1. Ich mache einen Besuch… ») : chaque item est un atome.

        Sans frontière dédiée, toute l'énumération se soudait en un seul atome de 250 mots — et le
        numéro doit ouvrir son item, pas rester collé à la fin du précédent.
        """
        p = segmenter("Ich teile die Träume mit.\n\n1. Ich mache einen Besuch.\n\n2. Sie wartet.\n")
        self.assertEqual(len(p), 3)
        self.assertTrue(p[1]["texte"].startswith("1."))
        self.assertTrue(p[2]["texte"].startswith("2."))
        self.assertFalse(p[0]["texte"].rstrip().endswith("1."))

    def test_question_coupe(self):
        p = segmenter("Wie komme ich dazu? Am selben Abend kam der Einfall.")
        self.assertEqual(len(p), 2)

    def test_offsets_exacts(self):
        """Une citation doit être re-localisable dans la source, sinon elle n'est pas vérifiable."""
        src = "Der Traum ist eine Wunscherfüllung. Wie komme ich dazu? Das ist merkwürdig."
        p = segmenter(src)
        self.assertTrue(recomposable(p, src))
        for x in p:
            self.assertEqual(src[x["debut"]:x["fin"]], x["texte"])

    def test_texte_vide(self):
        self.assertEqual(segmenter(""), [])
        self.assertEqual(segmenter("   \n  "), [])


class TestLexique(unittest.TestCase):
    """La taxonomie : ce qui décide de la qualification de chaque atome."""

    def test_integrite(self):
        r = lexique.valider()
        self.assertTrue(r["ok"], "lexique incohérent : %s" % r["erreurs"])

    def test_inference(self):
        self.assertIn("inference", lexique.fonctions_de(
            "Ich habe also in diesem Traume bereits an zwei Personen Rache genommen."))

    def test_hypothese_et_statut_modalise(self):
        t = "Vielleicht ist der Traum eine Wunscherfüllung."
        self.assertIn("hypothese", lexique.fonctions_de(t))
        self.assertEqual(lexique.statut_de(t), "modalise")

    def test_objection(self):
        self.assertIn("objection", lexique.fonctions_de(
            "Hier verlangt aber ein Einwand gehört zu werden."))

    def test_revision(self):
        """Le signal d'évolution théorique — la raison d'être du projet."""
        self.assertIn("revision", lexique.fonctions_de(
            "Mit welchem Rechte haben wir früher behauptet, daß der Traum den Schlaf schützt?"))

    def test_auto_citation(self):
        self.assertIn("auto_citation", lexique.fonctions_de(
            "Wir haben selbst die unbewußten Wünsche als immer rege bezeichnet."))

    def test_rapport_tiers(self):
        self.assertIn("rapport_tiers", lexique.fonctions_de(
            "So erging es Maury einmal mit einer Reihe von grotesken Gestalten."))

    def test_statut_le_plus_prudent_gagne(self):
        """On ne durcit JAMAIS un propos : une question reste une question."""
        self.assertEqual(lexique.statut_de("Ist der Traum also eine Wunscherfüllung?"), "interrogatif")
        self.assertEqual(lexique.statut_de("Der Traum ist eine Wunscherfüllung."), "affirme")

    def test_concepts_multigroupe(self):
        """Un atome peut relever de plusieurs groupes à la fois — c'est voulu."""
        c = lexique.concepts_de("Die Verdrängung des unbewußten Wunsches erzeugt das Symptom.")
        groupes = {x["groupe"] for x in c}
        self.assertIn("conflit", groupes)
        self.assertIn("topique", groupes)
        self.assertIn("desir", groupes)

    def test_orthographe_1900_ss_et_eszett(self):
        """« unbewußt » (1900) et « unbewusst » (moderne) doivent être reconnus pareil."""
        a = {x["concept"] for x in lexique.concepts_de("Das Unbewußte ist wirksam.")}
        b = {x["concept"] for x in lexique.concepts_de("Das Unbewusste ist wirksam.")}
        self.assertEqual(a, b)
        self.assertIn("unbewusst", a)

    def test_trauma_nest_pas_traum(self):
        """PIÈGE VÉRIFIÉ SUR LE TEXTE : « Trauma » ≠ « Traum ».

        « traum » nu captait « traumatisch » : dans Jenseits des Lustprinzips, 24 des 38 atomes
        « rêve » parlaient en réalité de névrose TRAUMATIQUE — c'est-à-dire l'appui empirique de
        la compulsion de répétition, attribué au mauvais concept.
        """
        c = {x["concept"] for x in lexique.concepts_de(
            "Die traumatische Neurose zeigt einen Wiederholungszwang.")}
        self.assertIn("trauma", c)
        self.assertNotIn("traum", c)
        # et inversement, le rêve reste bien détecté
        c2 = {x["concept"] for x in lexique.concepts_de("Der Traum ist eine Wunscherfüllung.")}
        self.assertIn("traum", c2)
        self.assertNotIn("trauma", c2)

    def test_composes_du_reve_en_a_restent_des_reves(self):
        """CONTRE-ÉPREUVE : l'allemand compose. « Traumarbeit » est un mot du RÊVE, pas du trauma.

        Une première version du correctif excluait « traum » suivi d'un « a » : elle perdait
        Traumarbeit (126 occurrences — le travail du rêve !), Traumanalyse, Traumangst,
        Traumätiologie. Corriger un faux positif en créant un faux négatif ne vaut rien.
        """
        for mot in ("Die Traumarbeit leistet die Verdichtung.",
                    "Die Traumanalyse führt zum Wunsch.",
                    "Die Traumangst ist keine gewöhnliche Angst.",
                    "Zur Traumätiologie gehören die Tagesreste."):
            c = {x["concept"] for x in lexique.concepts_de(mot)}
            self.assertIn("traum", c, "« %s » devrait relever du rêve" % mot)
            self.assertNotIn("trauma", c, "« %s » n'est pas un trauma" % mot)

    def test_lustig_nest_pas_lust(self):
        """« lustig » (amusant) n'est pas le plaisir freudien."""
        c = {x["concept"] for x in lexique.concepts_de("Es war eine lustige Geschichte.")}
        self.assertNotIn("lustprinzip", c)
        c2 = {x["concept"] for x in lexique.concepts_de("Das Lustprinzip beherrscht den Vorgang.")}
        self.assertIn("lustprinzip", c2)

    def test_masse_nest_pas_masze(self):
        """« Masse » (la foule) et « Maße » (les mesures) : seul le ß les distingue.

        Le repliement ordinaire (ß→ss, nécessaire pour l'orthographe de 1900) les confondait, et
        rattachait « in hohem Maße » à la psychologie des foules. Les termes marqués « § » se
        jugent donc sur le texte où le ß subsiste.
        """
        foule = {x["concept"] for x in lexique.concepts_de("Die Masse verhält sich wie eine Horde.")}
        mesure = {x["concept"] for x in lexique.concepts_de("Das gilt in hohem Maße für den Traum.")}
        self.assertIn("masse", foule)
        self.assertNotIn("masse", mesure)

    def test_domaines_ouverts_par_l_extension(self):
        """Les 7 œuvres ajoutées apportent des domaines entiers : ils doivent être reconnus."""
        cas = {
            "Das Tabu der Berührung beim Totemismus.": {"tabu", "totem", "beruehrung"},
            "Der tendenziöse Witz erzeugt Komik.": {"witz", "komik", "tendenz"},
            "Die Identifizierung mit dem Führer.": {"identifizierung", "fuehrer"},
            "Das Unheimliche in der Erzählung des Dichters.": {"unheimlich", "erzaehlung", "dichter"},
            "Das Versprechen ist eine Fehlleistung.": {"versprechen", "fehlleistung"},
        }
        for phrase, attendus in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertTrue(attendus <= trouves,
                            "« %s » : manquent %s" % (phrase, attendus - trouves))

    def test_ich_pronom_nest_pas_le_moi(self):
        """PIÈGE : « ich » = « je » chez Freud qui écrit à la 1re personne. Ne pas taguer « topique »."""
        c = lexique.concepts_de("Ich habe diesen Traum selbst geträumt.")
        self.assertNotIn("ich", {x["concept"] for x in c})

    def test_aucune_qualification_forcee(self):
        """Une phrase neutre ne doit RIEN déclencher — mieux vaut vide que faux."""
        self.assertEqual(lexique.fonctions_de("Das Haus stand am Ufer."), [])

    def test_signaux_rares_ne_sont_jamais_des_faits(self):
        """GARDE-FOU CENTRAL : révision/objection/auto-citation restent des CANDIDATS.

        Mesuré sur le texte réel : ~3 vrais positifs sur 7 pour « révision ». Les faire passer
        pour établis fausserait l'analyse d'évolution théorique, qui est l'objet du projet.
        """
        for rare in ("revision", "objection", "auto_citation"):
            self.assertEqual(lexique.FIABILITE[rare], "a_confirmer",
                             "« %s » ne doit pas être présenté comme établi" % rare)
        etablies, a_confirmer = lexique.fonctions_par_fiabilite(
            "Ich hatte damals die als unrichtig erkannte Meinung vertreten.")
        self.assertIn("revision", a_confirmer)
        self.assertNotIn("revision", etablies)

    def test_fonctions_frequentes_restent_etablies(self):
        """À l'inverse, les fonctions à marqueur net ne doivent pas être dégradées en candidats."""
        for sure in ("inference", "hypothese", "question", "methode"):
            self.assertEqual(lexique.FIABILITE[sure], "etablie")


class TestSources(unittest.TestCase):
    """La provenance : ce qui rend le corpus opposable à un chercheur."""

    def test_manifeste_complet(self):
        m = sources.manifeste()
        self.assertEqual(len(m["oeuvres"]), len(sources.OEUVRES))
        for o in m["oeuvres"]:
            self.assertTrue(o["present"], "œuvre absente du dépôt : %s" % o["cle"])
            self.assertTrue(o["empreinte_fichier"])

    def test_datation_jamais_faussement_precise(self):
        """Le cœur de l'honnêteté du projet : ne jamais dater un atome de l'année de l'œuvre."""
        d = sources.datation(sources.OEUVRES["traumdeutung"])
        self.assertFalse(d["precise"])
        self.assertEqual(d["fenetre_incertitude_annees"], 14)
        self.assertIn("au plus tard", d["regle"])

    def test_entete_gutenberg_retiree(self):
        c = sources.charger("jenseits")
        self.assertNotIn("PROJECT GUTENBERG", c["texte"].upper()[:2000])
        self.assertLess(len(c["texte"]), c["meta"]["caracteres_fichier"])

    def test_liminaires_editeur_retires(self):
        """Page de titre et table des matières ne sont pas des énoncés de Freud.

        Atomisées, elles produisaient « DR. », « SIGM. », « Die Realität 472 » — du bruit qui
        gonflait le corpus et le taux de non-qualifiés.
        """
        for cle in sources.OEUVRES:
            t = sources.charger(cle)["texte"]
            # On teste la STRUCTURE (un titre de table en tête de ligne), pas le mot : Freud parle
            # parfois de la table des matières d'un AUTRE livre en plein texte — c'est du contenu.
            self.assertIsNone(re.search(r"^[ 	]*(Inhaltsverzeichnis|Inhaltsangabe)\.?[ 	]*$",
                                        t, re.M), "table des matières restante : %s" % cle)
            self.assertNotIn("VERLAGS-NR", t.upper(), "page de titre restante : %s" % cle)
            self.assertNotIn("TRANSCRIBER", t.upper(), "note de transcription restante : %s" % cle)

    def test_prefaces_datees_preservees(self):
        """À l'inverse, les préfaces sont le SEUL matériau daté avec certitude : jamais retirées."""
        t = sources.charger("traumdeutung")["texte"]
        self.assertTrue(t.lstrip().startswith("Vorbemerkung"))
        self.assertIn("Vorwort zur zweiten Auflage", t)


class TestAtomisation(unittest.TestCase):
    """Les invariants de la source de données principale."""

    @classmethod
    def setUpClass(cls):
        cls.r = atomisation.atomiser("jenseits")     # la plus courte : test rapide et réel

    def test_atomes_produits(self):
        self.assertGreater(len(self.r["atomes"]), 500)

    def test_recomposition_et_localisation(self):
        c = self.r["controles"]
        self.assertTrue(c["recomposition_ordre_ok"])
        self.assertTrue(c["localisation_complete"],
                        "%d/%d atomes localisés" % (c["localisation_exacte"], c["total_atomes"]))

    def test_chaque_atome_porte_sa_datation(self):
        for a in self.r["atomes"][:50]:
            self.assertIn("attestation", a)
            self.assertIn("regle", a["attestation"])

    def test_non_qualifie_est_dit(self):
        """Les atomes sans catégorie sont comptés et visibles, jamais comblés en silence."""
        c = self.r["controles"]
        self.assertEqual(c["qualifies"] + c["non_qualifies"], c["total_atomes"])

    def test_signaux_a_confirmer_separes_des_fonctions(self):
        """Aucun signal « à confirmer » ne doit fuiter dans les fonctions établies d'un atome."""
        for a in self.r["atomes"]:
            for s in a["signaux_a_confirmer"]:
                self.assertNotIn(s, a["fonctions"])

    def test_paratexte_transcripteur_absent(self):
        """Le paratexte Gutenberg (producteur, errata) ne doit produire AUCUN atome."""
        debut = " ".join(a["texte"] for a in self.r["atomes"][:20])
        self.assertNotIn("Produced by", debut)
        for a in self.r["atomes"]:
            self.assertNotIn("geänderten Textzeilen", a["texte"])

    def test_index_coherent(self):
        idx = self.r["index"]
        total_statuts = sum(idx["par_statut"].values())
        self.assertEqual(total_statuts, len(self.r["atomes"]))

    def test_ids_uniques(self):
        ids = [a["id"] for a in self.r["atomes"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_deterministe(self):
        """Même entrée → même sortie. Sans ça, aucune analyse n'est reproductible."""
        encore = atomisation.atomiser("jenseits")
        self.assertEqual([a["id"] for a in encore["atomes"]], [a["id"] for a in self.r["atomes"]])
        self.assertEqual([a["fonctions"] for a in encore["atomes"]],
                         [a["fonctions"] for a in self.r["atomes"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
