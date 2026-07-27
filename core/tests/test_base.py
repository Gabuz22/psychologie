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

    def test_homonymes_de_einwand_ecartes(self):
        """« einwandfrei » (irréprochable) et « einwandern » (immigrer) ne sont pas des objections.

        Trouvés en lisant les candidats un par un : « eine einwandfreie Deutung » est un ÉLOGE, et
        dans Totem und Tabu les âmes qui « migrent » dans d'autres personnes étaient comptées
        comme objections.
        """
        for phrase in ("Das ist eine durchaus einwandfreie Deutung des Kollegen.",
                       "Die Seelen können in andere Menschen einwandern."):
            self.assertNotIn("objection", lexique.fonctions_de(phrase), phrase)
        self.assertIn("objection", lexique.fonctions_de(
            "Der naheliegende Einwand trifft unsere Auffassung."))

    def test_freilich_nest_pas_une_objection(self):
        """« freilich » = « certes », un concessif — pas une objection mise en scène.

        Mesuré : il produisait 60 candidats sur 177, dont aucun des dix lus n'était une
        contre-objection ; dans « Gradiva » il apparaissait jusque dans les dialogues du roman.
        Même défaut que « nicht mehr » pour la révision : un mot fréquent noie le signal rare.
        """
        self.assertNotIn("objection", lexique.fonctions_de(
            "Ein Zuviel von elterlicher Zärtlichkeit wird freilich schädlich werden."))
        self.assertIn("objection", lexique.fonctions_de(
            "Man wird gegen diese Auffassung einwenden, daß sie zu weit geht."))

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

    def test_seconde_topique_detectee(self):
        """Ich / Es / Über-Ich — les trois instances doivent être reconnues.

        PIÈGE DE TRANSLITTÉRATION resté longtemps invisible : le terme était écrit « ueber-ich »,
        comme si le ü devenait « ue ». Or le repliement SUPPRIME les diacritiques (« Über » →
        « uber ») : le SURMOI n'était détecté nulle part dans tout le corpus.
        """
        moi = {x["concept"] for x in lexique.concepts_de("Das Ich ist vom Es abhängig.")}
        surmoi = {x["concept"] for x in lexique.concepts_de(
            "Das Über-Ich ist der Erbe des Ödipuskomplexes.")}
        ca = {x["concept"] for x in lexique.concepts_de("Das Es kennt keine Verneinung.")}
        self.assertIn("ich", moi)
        self.assertIn("ueberich", surmoi)
        self.assertIn("es", ca)

    def test_ich_pronom_nest_pas_le_moi(self):
        """PIÈGE : « ich » = « je » chez Freud qui écrit à la 1re personne. Ne pas taguer « topique »."""
        c = lexique.concepts_de("Ich habe diesen Traum selbst geträumt.")
        self.assertNotIn("ich", {x["concept"] for x in c})

    def test_concept_reserve_a_un_auteur(self):
        """Un concept propre à un auteur ne doit pas être cherché chez les autres.

        Le projet vise à comparer les courants : cela n'a de sens que si l'on ne compte pas chez
        Freud un mot qu'il n'employait pas. Éprouvé ici sur un concept ajouté puis retiré, pour ne
        pas dépendre de l'état du lexique.
        """
        groupe = lexique.CONCEPTS["topique"]["termes"]
        groupe["archetyp_test"] = {"motifs": ["archetyp"], "auteurs": ["jung"]}
        try:
            phrase = "Der Archetypus wirkt im Unbewußten."
            chez_jung = {x["concept"] for x in lexique.concepts_de(phrase, "jung")}
            chez_freud = {x["concept"] for x in lexique.concepts_de(phrase, "freud")}
            self.assertIn("archetyp_test", chez_jung)
            self.assertNotIn("archetyp_test", chez_freud)
            # …et le concept commun reste vu chez les deux.
            self.assertIn("unbewusst", chez_jung)
            self.assertIn("unbewusst", chez_freud)
        finally:
            del groupe["archetyp_test"]

    def test_domaines_de_l_audit_2026_07(self):
        """Les 5 œuvres à fort non-qualifié ont révélé des domaines entiers hors ontologie.

        Mesuré avant l'ajout : Moses des Michelangelo 61 % de non-qualifiés (description
        d'œuvre d'art), Vergänglichkeit 48 % (beauté, deuil), Teufelsneurose 46 % (démonologie),
        Leonardo 44 % (peinture), Zeitgemäßes über Krieg und Tod 44 % (guerre, mort, État).
        """
        cas = {
            "Die Trauer über den Verlust läuft spontan ab.": {"trauer"},
            "Der Tod des Vaters ist das bedeutsamste Ereignis.": {"tod", "vater"},
            "Der Krieg hat die Kulturgüter zerstört.": {"krieg", "kultur"},
            "Gott ist die erhöhte Vaterprojektion.": {"gott", "vater"},
            "Der Teufel ist ein Vaterersatz.": {"teufel", "vater"},
            "Der Maler schuf das Gemälde in Mailand.": {"malerei"},
            "Die Statue stellt einen zornigen Moses dar.": {"statue", "aggression"},
            "Die Schönheit der Natur ist vergänglich.": {"schoenheit", "verganglichkeit"},
            "Der Staat verbietet dem Einzelnen das Unrecht.": {"staat", "verbot"},
            "Der Künstler verfügt über die Kunst.": {"kunst"},
            "Die Melancholie folgt dem Verlust des Objekts.": {"melancholie"},
            "Der Affektbetrag wird verschoben.": {"affekt"},
            "Die Religion des Urmenschen war animistisch.": {"religion", "primitiv", "animismus"},
        }
        for phrase, attendus in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertTrue(attendus <= trouves,
                            "« %s » : manquent %s" % (phrase, attendus - trouves))

    def test_homonymes_de_l_audit_ecartes(self):
        """CONTRE-ÉPREUVES : les homonymes trouvés en inventoriant les formes réellement captées.

        « Göttingen » est une ville, pas le divin ; « Affektion » est l'affection MÉDICALE
        (nervöse Affektion), pas l'affect ; « künstlich » est l'artificiel (les « foules
        artificielles » de la Massenpsychologie), pas l'art ; « kriegen » veut dire recevoir.
        """
        cas = {
            "Er studierte in Göttingen bei den Professoren.": "gott",
            "Eine nervöse Affektion der Patientin.": "affekt",
            "Kirche und Heer sind künstliche Massen.": "kunst",
            # NB : le corpus réel ne contient AUCUN « krieg » nu au sens de « recevoir » (les
            # quatre occurrences nues sont le nom) — la forme familière exclue est « kriegen ».
            "Man kann nicht alles kriegen, was man will.": "krieg",
            "Das ist schon lange bekannt.": "schoenheit",
        }
        for phrase, interdit in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertNotIn(interdit, trouves, "« %s » a capté « %s »" % (phrase, interdit))

    def test_domaines_de_l_audit_4(self):
        """Quatrième audit (2026-07), mené sur les VINGT œuvres et non plus cinq.

        Le scan global des atomes non qualifiés a montré que la majorité des mots fréquents
        restants sont du vocabulaire ORDINAIRE (Person, Leben, Jahre, Stelle, Frage) qu'il ne
        faut surtout pas taguer — mais il a aussi révélé des pans entiers de doctrine absents :
        la différence des sexes (526 occ., 17 œuvres, alors qu'une conférence entière des Neue
        Folge s'intitule « Die Weiblichkeit »), les défenses autres que le refoulement, le
        complexe de castration, le vocabulaire ordinaire de la cure, et le méta-discours
        scientifique de Freud sur son propre travail.
        """
        cas = {
            "Die Hysterie zeigt ein Symptom.": {"hysterie", "symptom", "neurose"},
            "Zwangsvorstellungen und Zwangshandlungen quälen ihn.": {"zwangsneurose"},
            "Die Sublimierung des Triebes schafft Kultur.": {"sublimierung", "trieb", "kultur"},
            "Die Projektion erklärt den Animismus.": {"projektion", "animismus"},
            "Er verleugnet die Wahrnehmung.": {"verleugnung"},
            "Der Kastrationskomplex und der Penisneid.": {"kastration"},
            "Die Weiblichkeit ist ein Rätsel.": {"weiblichkeit"},
            "Die männliche Einstellung.": {"maennlichkeit"},
            "Der somatische Vorgang im Körper.": {"koerper"},
            "Die ärztliche Behandlung führt zur Heilung.": {"arzt", "behandlung"},
            "Die Deutung des Einfalls.": {"deutung", "assoziation"},
            "Die Hypnose und die kathartische Methode.": {"hypnose"},
            "Die Aufmerksamkeit schwankt.": {"aufmerksamkeit"},
            "Die Wissenschaft verlangt Beobachtung und Theorie.":
                {"wissenschaft", "beobachtung", "theorie"},
            "Die menschliche Gesellschaft beruht auf Verzicht.": {"gesellschaft"},
        }
        for phrase, attendus in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertTrue(attendus <= trouves,
                            "« %s » : manquent %s" % (phrase, attendus - trouves))

    def test_homonymes_de_l_audit_4_ecartes(self):
        """CONTRE-ÉPREUVES de l'audit 4 — les pièges relevés en inventoriant les formes captées.

        « Bedeutung » (signification, 375 occurrences) est un tout autre mot que « Deutung »
        (l'interprétation) ; « Wiederholungszwang » est un concept distinct de la névrose
        obsessionnelle ; « der Mann » (l'homme, la personne) n'est pas la masculinité comme
        qualité ; « Sexualtheorie » désigne une théorie particulière, pas le fait d'en avoir une.
        """
        cas = {
            "Die Bedeutung dieses Traumes ist klar.": "deutung",
            "Die Traumdeutung ist sein Hauptwerk.": "deutung",
            "Der Wiederholungszwang beherrscht ihn.": "zwangsneurose",
            "Der Mann trat in das Zimmer.": "maennlichkeit",
            "Die Sexualtheorie von 1905.": "theorie",
        }
        for phrase, interdit in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertNotIn(interdit, trouves, "« %s » a capté « %s »" % (phrase, interdit))

    def test_domaines_de_l_audit_5(self):
        """Cinquième audit (2026-07) — le CORPS CONCRET, le nom propre, l'hallucination.

        Mené sur les six œuvres au non-qualifié le plus haut. Trois œuvres du corpus sont des
        analyses de corps concrets dont le vocabulaire était invisible : la main, la barbe et
        les Tables du *Moses* (43 % de non-qualifiés, le pire du corpus), les yeux arrachés de
        *Das Unheimliche*, le sourire de *Monna Lisa*. S'y ajoutent deux absences criantes : le
        NOM PROPRE (459 occ. — alors que « Zur Psychopathologie » s'ouvre sur « Das Vergessen
        von Eigennamen », et que le concept ne captait que le mot composé) et l'HALLUCINATION
        (67 occ. — alors que la « halluzinatorische Wunscherfüllung » est le modèle du rêve).
        """
        cas = {
            "Die rechte Hand hält die Tafeln.": {"hand"},
            "Der Sandmann reißt den Kindern die Augen aus.": {"auge"},
            "Der Bart des Moses fällt über die Brust.": {"bart"},
            "Er wandte den Kopf zur Seite.": {"kopf"},
            "Das Lächeln der Monna Lisa ist rätselhaft.": {"lacheln"},
            "Ein Ausdruck des Gesichtes verrät den Affekt.": {"gesicht"},
            "Die Mundwinkel verziehen sich.": {"mund"},
            "Das Vergessen von Eigennamen ist häufig.": {"name", "vergessen"},
            "Der Name der Dame fiel mir nicht ein.": {"name"},
            "Die halluzinatorische Wunscherfüllung des Säuglings.":
                {"halluzination", "wunscherfuellung"},
            "Der Maler unterschrieb die Verschreibung mit Blut.": {"pakt", "malerei"},
        }
        for phrase, attendus in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertTrue(attendus <= trouves,
                            "« %s » : manquent %s" % (phrase, attendus - trouves))

    def test_homonymes_de_l_audit_5_ecartes(self):
        """CONTRE-ÉPREUVES de l'audit 5 — les pièges mesurés sur les formes réellement captées.

        « handeln »/« Handlung » (300+ occ.) auraient triplé le concept « hand » avec du bruit ;
        « Augenblick » (l'instant, 41 occ.) n'a rien d'oculaire ; « Gesichtspunkt » (le point de
        vue, 71 occ. sur 166) n'est pas un visage ; « namentlich » veut dire « à savoir » ; et
        « Erscheinung » — écarté à la source — signifie « phénomène » dans tout le corpus, pas
        « apparition » : l'ajouter aurait produit un faux positif de masse.
        """
        cas = {
            "Es handelt sich um eine Handlung.": "hand",
            "Die Behandlung des Kranken.": "hand",
            "Im Augenblick der Erkenntnis.": "auge",
            "Unter diesem Gesichtspunkte betrachtet.": "gesicht",
            "Namentlich die Neurotiker zeigen dies.": "name",
            "Die pathologischen Erscheinungen des Seelenlebens.": "pakt",
        }
        for phrase, interdit in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertNotIn(interdit, trouves, "« %s » a capté « %s »" % (phrase, interdit))

    def test_le_lapsus_calami_et_le_pacte_ne_se_confondent_pas(self):
        """« verschreiben » (lapsus d'écriture) et « Verschreibung » (le pacte signé) sont deux
        mots distincts que la frontière de mot sépare d'elle-même — vérifié dans les deux sens,
        car les confondre rangerait le pacte avec le diable parmi les actes manqués."""
        lapsus = {x["concept"] for x in lexique.concepts_de(
            "Er hat sich beim Schreiben verschreiben können.")}
        self.assertIn("versprechen", lapsus)
        self.assertNotIn("pakt", lapsus)

        pacte = {x["concept"] for x in lexique.concepts_de(
            "Die Verschreibung an den Teufel galt neun Jahre.")}
        self.assertIn("pakt", pacte)
        self.assertNotIn("versprechen", pacte)

    def test_domaines_de_l_audit_6(self):
        """Sixième audit (2026-07) — LA CONSCIENCE MORALE, registre entier absent.

        Découvert en atomisant « Einige Charaktertypen aus der psychoanalytischen Arbeit »
        (1916), entrée au corpus le même jour : sa troisième partie s'intitule « Verbrecher aus
        Schuldbewußtsein » et 42 % de ses atomes restaient non qualifiés. L'omission était de
        taille — Freud définit le Sur-Moi comme l'héritier de la conscience morale, et fait de
        la culpabilité le ressort du totémisme comme de la névrose obsessionnelle.
        """
        cas = {
            "Das Schuldbewußtsein des Verbrechers.": {"schuld", "verbrechen"},
            "Ein Schuldgefühl quält den Neurotiker.": {"schuld", "neurose"},
            "Das Gewissen schweigt in den Träumen.": {"gewissen", "traum"},
            "Die Gewissensangst des Melancholikers.": {"gewissen", "angst", "melancholie"},
            "Sein Gewissen wollte ihn strafen.": {"gewissen", "strafe"},
            "Die moralischen Vorschriften der Kultur.": {"moral", "kultur"},
            "Reue und Selbstvorwürfe folgen der Tat.": {"reue"},
            "Die Charakterbildung des Kindes.": {"charakter"},
            "Ein bemerkenswerter Charakterzug.": {"charakter"},
        }
        for phrase, attendus in cas.items():
            trouves = {x["concept"] for x in lexique.concepts_de(phrase)}
            self.assertTrue(attendus <= trouves,
                            "« %s » : manquent %s" % (phrase, attendus - trouves))

    def test_gewissen_adjectif_ecarte(self):
        """PIÈGE MAJEUR de l'audit 6 : « gewissen » est aussi « gewiß » (certain) décliné.

        « einer gewissen Regel » pèse 108 occurrences dans le corpus, contre ~65 pour le
        substantif « das Gewissen ». Le repliement supprimant la majuscule qui les distingue en
        allemand, seules les formes SÛRES sont retenues. Mieux vaut manquer que sur-détecter —
        même arbitrage que pour « ich » et « es ».
        """
        for phrase in ("In einer gewissen Anzahl von Fällen.",
                       "Bis zu einem gewissen Grade ist das richtig.",
                       "Unter gewissen Bedingungen tritt es auf.",
                       "Ein gewisser Herr aus Wien."):
            self.assertNotIn("gewissen", {x["concept"] for x in lexique.concepts_de(phrase)},
                             "« %s » a capté la conscience morale" % phrase)
        # …et le substantif reste bien capté, dans les deux formes attestées.
        for phrase in ("Das Gewissen ist der Erbe des Ödipuskomplexes.",
                       "Die Entstehung des Gewissens bleibt dunkel.",
                       "Er machte sich Gewissensvorwürfe."):
            self.assertIn("gewissen", {x["concept"] for x in lexique.concepts_de(phrase)}, phrase)

    def test_charakter_ordinaire_ecarte(self):
        """« Charakter » nu désigne aussi la NATURE d'une chose, pas seulement le caractère.

        « die Charaktere des Traumlebens » = les propriétés de la vie onirique. Sur 513
        occurrences du radical, la part psychanalytique n'est pas séparable mécaniquement : le
        concept est donc volontairement restreint à ses composés univoques.
        """
        for phrase in ("Die Charaktere des Traumlebens sind bekannt.",
                       "Eine charakteristische Eigentümlichkeit.",
                       "Das läßt sich so charakterisieren."):
            self.assertNotIn("charakter", {x["concept"] for x in lexique.concepts_de(phrase)},
                             phrase)

    def test_composes_de_angst_captes_et_langst_ecarte(self):
        """Les composés en -angst sont énumérés ; « längst » n'est pas de l'angoisse.

        Défaut décelé par un test de l'audit 6 : « Gewissensangst » n'était pas reconnu. Mais
        le joker qui l'aurait réparé aurait ramassé « längst » (depuis longtemps, 79 occ.) et
        « unlängst » (récemment, 16) — 95 faux positifs. Les deux sens sont donc verrouillés.
        """
        for phrase in ("Die Kastrationsangst des Knaben.",
                       "Die Realangst vor der Gefahr.",
                       "Die Gewissensangst des Melancholikers.",
                       "Die Todesangst überfiel ihn.",
                       "Die Angst ist ein Affektzustand."):
            self.assertIn("angst", {x["concept"] for x in lexique.concepts_de(phrase)}, phrase)
        for phrase in ("Das ist längst bekannt.",
                       "Er hat unlängst davon berichtet."):
            self.assertNotIn("angst", {x["concept"] for x in lexique.concepts_de(phrase)},
                             "« %s » a capté de l'angoisse" % phrase)

    def test_composes_de_besetzung_captes(self):
        """La frontière de mot exclut tout composé : les composés attestés sont donc ÉNUMÉRÉS.

        Défaut décelé par un test de l'audit 4 : « Aufmerksamkeitsbesetzung » (l'investissement
        d'attention) n'était pas reconnu comme un investissement. Même correctif que pour
        « trieb » — énumérer les formes relevées dans le texte, jamais un joker qui ramasserait
        n'importe quel mot finissant par « besetzung ».
        """
        for phrase in ("Die Aufmerksamkeitsbesetzung schwankt.",
                       "Die Objektbesetzung wird aufgegeben.",
                       "Eine Überbesetzung des Systems.",
                       "Die Besetzung der Vorstellung."):
            self.assertIn("besetzung", {x["concept"] for x in lexique.concepts_de(phrase)}, phrase)

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

    def test_paratexte_final_retire(self):
        """Bibliographies et réclames d'éditeur ne sont pas de Freud.

        Atomisées, elles donnaient « #Alix.# Les rêves. Rev. Scient. » ou « Preis M 10.-- ».
        Le seul Literaturverzeichnis de la Traumdeutung pèse 56 000 signes.
        """
        # On teste la BORNE exacte, pas le mot : Freud mentionne lui-même sa bibliographie dans
        # la préface (« Ein zweites Literaturverzeichnis am Ende… ») — c'est son texte à lui.
        interdits = {
            "traumdeutung": "VIII. Literaturverzeichnis.",
            "witz": "VERLAG VON FRANZ DEUTICKE",
            "totem": "Zu beziehen durch",
            "jenseits": "Werke von Prof. Sigm. Freud",
            "gradiva": "Anzeige.",
        }
        for cle, mot in interdits.items():
            t = sources.charger(cle)["texte"]
            self.assertNotIn(mot, t, "paratexte final restant dans %s" % cle)
        # Contre-épreuve : les entrées bibliographiques elles-mêmes ont bien disparu.
        self.assertNotIn("#Achmetis F. Serim.#", sources.charger("traumdeutung")["texte"])
        # …et le texte de Freud qui le précède est intact. On normalise les espaces : le texte
        # d'origine est retourné à la ligne : un saut au milieu d'une phrase n'est pas une coupure.
        aplati = lambda cle: " ".join(sources.charger(cle)["texte"].split())
        self.assertIn("Ebenbilde jener Vergangenheit gestaltet", aplati("traumdeutung"))
        self.assertIn("nur Geschöpfe des Dichters sind", aplati("gradiva"))

    def test_notes_wikisource_retirees(self):
        """Wikisource ajoute ses propres notes (« ↑ Karl Marx (Wikipedia) ») : ce n'est pas Freud.

        Mais ses notes de bas de page À LUI, rendues avec la même flèche, doivent rester : on ne
        retire que le signe de renvoi.
        """
        t = sources.charger("neue_folge")["texte"]
        self.assertNotIn("Anmerkungen (Wikisource)", t)
        self.assertNotIn("(Wikipedia)", t)
        self.assertNotIn("Bearbeiten", t)
        self.assertNotIn("↑", t)
        # note authentique de Freud, conservée sans sa flèche
        self.assertIn("So wurde es mir im ersten Kriegsjahr", t)
        for conference in ("REVISION DER TRAUMLEHRE", "ANGST UND TRIEBLEBEN"):
            self.assertIn(conference, t)

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

    def test_appendice_de_rank_nest_pas_attribue_a_freud(self):
        """La 4e éd. de la Traumdeutung contient un appendice d'OTTO RANK — 7 % du volume.

        Sa page de titre l'annonce (« MIT BEITRÄGEN VON Dr. OTTO RANK ») et le texte le confirme
        (« (183) Von Dr. Otto Rank »). Sans déclaration, ces pages passaient pour du Freud — le
        défaut a été décelé par des passages parlant de « der Freudschen Auffassung » à la
        TROISIÈME personne. Une analyse d'auteur qui l'ignore mesure deux plumes pour une.
        """
        r = atomisation.atomiser("traumdeutung")
        par_auteur = r["controles"]["par_auteur"]
        self.assertIn("Otto Rank", par_auteur)
        self.assertGreater(par_auteur["Otto Rank"], 200)
        self.assertGreater(par_auteur["Sigmund Freud"], par_auteur["Otto Rank"] * 10)
        rank = [a for a in r["atomes"] if a["auteur"] == "Otto Rank"]
        self.assertIn("Traum und Dichtung", rank[0]["texte"])
        # Les œuvres sans contribution déclarée restent intégralement de Freud.
        for cle in ("jenseits", "massenpsychologie"):
            self.assertEqual(list(atomisation.atomiser(cle)["controles"]["par_auteur"]),
                             ["Sigmund Freud"])

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
