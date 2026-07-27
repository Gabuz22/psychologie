#!/usr/bin/env python3
"""SOURCES — chargement des œuvres et TRAÇABILITÉ de leur provenance.

Reprend la doctrine éprouvée sur le corpus AXA : on ne présente jamais comme certain ce qui ne
l'est pas, et on rend chaque affirmation re-vérifiable dans la source. Ici, deux vérités
inconfortables doivent être portées par les DONNÉES elles-mêmes, jamais tues :

  1. LES TEXTES NE SONT PAS DES PREMIÈRES ÉDITIONS. « Die Traumdeutung » disponible est la 4e éd.
     (1914) d'une œuvre de 1900 ; « Drei Abhandlungen » la 4e éd. (1920) d'une œuvre de 1905.

  2. LES COUCHES D'AJOUT SONT INVISIBLES. Freud écrit lui-même, préface à la 3e éd. des « Drei
     Abhandlungen » : « Ich habe in dieser dritten Auflage reichliche Einschaltungen vorgenommen,
     aber darauf verzichtet, dieselben wie in der vorigen Auflage durch besondere Zeichen
     kenntlich zu machen. » (« j'ai fait d'abondantes insertions, mais j'ai renoncé à les signaler
     par des signes particuliers comme dans l'édition précédente »).

Conséquence directe sur le modèle de données : un atome n'est JAMAIS daté de l'année de l'œuvre.
Il est « attesté AU PLUS TARD » dans l'édition lue (terminus ante quem). Dater un atome « 1900 »
alors qu'il vient d'un ajout de 1914 fausserait toute analyse chronologique — c'est-à-dire l'objet
même du projet. Seules les préfaces, que Freud signe et date, sont datées avec certitude.

La levée de cette incertitude est possible mais reste À FAIRE : elle demande une COLLATION entre
éditions (la 1re éd. est disponible en fac-similé). C'est un chantier distinct, pas une supposition.
"""
import hashlib
import json
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_DE = os.path.join(RACINE, "sources", "freud", "de")

# Bornes du texte utile dans un fichier Project Gutenberg (l'en-tête et la licence n'appartiennent
# pas à l'œuvre : les inclure polluerait les atomes avec du texte administratif anglais).
_DEBUT = re.compile(r"\*\*\* ?START OF TH[EI][^\n]*\*\*\*[^\n]*\n")
_FIN = re.compile(r"\*\*\* ?END OF TH[EI][^\n]*\*\*\*")

# PARATEXTE DU TRANSCRIPTEUR — à l'INTÉRIEUR des bornes ci-dessus, donc invisible au premier
# nettoyage. Deux blocs, vérifiés présents dans les trois œuvres :
#   • en tête  : « Produced by … » + « [ Anmerkungen zur Transkription: … ] » (conventions de
#                transcription : _ = espacé, ~ = italique, # = gras) ;
#   • en queue : « [ Im folgenden werden alle geänderten Textzeilen angeführt … ] », la liste des
#                coquilles corrigées, sous forme de paires avant/après (~25 000 signes dans la
#                Traumdeutung — soit autant de faux atomes si on l'oublie).
# Les laisser produisait des atomes administratifs (« Produced by Jana Srna… ») mêlés à l'œuvre.
_NOTE_TETE = re.compile(r"\A.{0,400}?\[\s*Anmerkungen zur Transkription:.*?^\s*\]\s*$",
                        re.S | re.M)
# Deux formes de note finale coexistent selon le transcripteur — les deux doivent partir, sinon
# des errata (« Seite 57: Unbebewußten -> Unbewußten ») deviennent des atomes de Freud.
_NOTE_QUEUE = re.compile(
    r"^\s*\[\s*Im folgenden werden alle geänderten Textzeilen.*\Z"
    r"|^[ \t]*(?:ANMERKUNGEN ZUR TRANSKRIPTION|TRANSCRIBER'?S NOTES?)\b.*\Z",
    re.S | re.M)

# LIMINAIRES DE L'ÉDITEUR — page de titre et table des matières. Ce ne sont pas des énoncés de
# Freud : atomisés, ils produisaient des unités absurdes (« DR. », « SIGM. », « Die Realität 472 »)
# qui gonflaient artificiellement le corpus et le taux de non-qualifiés.
#   • Page de titre : du début jusqu'au premier vrai titre de section (Vorbemerkung/Vorwort/…).
#     Elle est conservée AILLEURS — c'est elle qui atteste l'édition (« VIERTE, VERMEHRTE
#     AUFLAGE … 1914 »), information déjà portée par le registre OEUVRES.
#   • Table des matières : de son titre jusqu'à sa dernière entrée. Une entrée a une signature
#     nette et vérifiable : un libellé, au moins trois espaces, un numéro de page, fin de ligne.
# Les PRÉFACES, elles, sont conservées : Freud les date et les signe — c'est le seul matériau du
# corpus dont la datation soit certaine (voir `datation`).
# Repli pour les œuvres sans préface (« Jenseits des Lustprinzips » paraît comme supplément de
# revue : sa page de titre est suivie d'un copyright et de l'imprimeur, puis du chapitre « I. »).
_PREMIER_TITRE = re.compile(r"^\s*(Vorbemerkung|Vorwort|Einleitung|Inhaltsverzeichnis|Inhaltsangabe)\b",
                            re.M)
_PREMIER_CHAPITRE = re.compile(r"^[ \t]*I\.[ \t]*$", re.M)
_TOC_TITRE = re.compile(r"^[ \t]*(Inhaltsverzeichnis|Inhaltsangabe)\.?[ \t]*$", re.M)
# Variante pour les transcriptions WIKISOURCE page par page, qui conservent la CAPITALE de la
# page imprimée (« VORWORT. », « INHALTS-VERZEICHNISS. ») là où Gutenberg normalise la casse.
# Elle est séparée à dessein : rendre le motif principal insensible à la casse faisait matcher
# « INHALTSVERZEICHNIS » en tête d'« Über Psychoanalyse » et CONSERVAIT sa table des matières —
# 51 faux atomes. Un correctif ne doit pas déplacer le défaut vers une autre œuvre.
_PREMIER_TITRE_WS = re.compile(r"^\s*(VORBEMERKUNG|VORWORT|EINLEITUNG)\b", re.M)
_TOC_TITRE_WS = re.compile(r"^[ \t]*INHALTS-?VERZEICHNIS{1,2}\.?[ \t]*$", re.M)
_TOC_LIGNE = re.compile(r"^.{3,75}?[ \t]{3,}\d{1,3}[ \t]*$")

# PARATEXTE DE FIN DE VOLUME — bibliographies et réclames d'éditeur. Ce n'est pas Freud, et cela
# produisait des atomes absurdes : « #Alix.# Les rêves. Rev. Scient. » ou « Preis M 10.-- ».
# Chaque borne a été RELEVÉE DANS LE TEXTE, jamais devinée ; elle n'est retenue que si elle tombe
# au-delà des deux tiers du volume — le même mot peut figurer sur la page de titre.
# La bibliographie de la Traumdeutung pèse à elle seule ~56 000 signes, soit 4 % du livre.
PARATEXTE_FINAL = {
    "traumdeutung": "VIII. Literaturverzeichnis.",
    "witz": "VERLAG VON FRANZ DEUTICKE",
    "gradiva": "Anzeige.",
    "totem": "INTERNATIONALER PSYCHOANALYTISCHER VERLAG",
    "jenseits": "Werke von Prof. Sigm. Freud",
}

# Registre des œuvres. `annee_edition` = ce qu'on LIT ; `annee_oeuvre` = première parution.
# L'écart entre les deux EST l'incertitude de datation, portée explicitement.
OEUVRES = {
    "traumdeutung": {
        "fichier": "1900_traumdeutung.pg.txt",
        "titre": "Die Traumdeutung",
        "titre_fr": "L'interprétation des rêves",
        "annee_oeuvre": 1900,
        "annee_edition": 1914,
        "edition": "4. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #40739 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/40739",
        "fac_simile": "https://archive.org/details/Freud_1900_Die_Traumdeutung_k (1re éd., scan)",
        # TOUT CE LIVRE N'EST PAS DE FREUD. Sa page de titre l'annonce — « MIT BEITRÄGEN VON
        # Dr. OTTO RANK » — et le texte le confirme par une note : « (183) Von Dr. Otto Rank ».
        # Il s'agit d'un APPENDICE entier (« Traum und Dichtung », « Traum und Mythus »), inséré
        # entre les chapitres VI et VII : environ 100 000 signes, soit 7 % du volume.
        # Sans cette déclaration, ces pages étaient attribuées à Freud — et des lecteurs l'ont
        # décelé en trouvant des passages qui parlent de « der Freudschen Auffassung » à la
        # TROISIÈME personne. Une analyse d'auteur qui ignore cela mesure deux plumes pour une.
        "contributions": [{"auteur": "Otto Rank", "debut": "Anhang(183)", "jusqu_au_chapitre": "VII"}],
    },
    "drei_abhandlungen": {
        "fichier": "1905_drei_abhandlungen.pg.txt",
        "titre": "Drei Abhandlungen zur Sexualtheorie",
        "titre_fr": "Trois essais sur la théorie sexuelle",
        "annee_oeuvre": 1905,
        "annee_edition": 1920,
        "edition": "4. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #39938 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/39938",
        "fac_simile": "https://archive.org/details/Freud_1905_Drei_Abhandlungen (1re éd., scan)",
    },
    "psychopathologie": {
        "fichier": "1901_psychopathologie_alltagsleben.pg.txt",
        "titre": "Zur Psychopathologie des Alltagslebens",
        "titre_fr": "Psychopathologie de la vie quotidienne",
        "annee_oeuvre": 1901,
        "annee_edition": 1904,
        "edition": "Durchgesehener Abdruck",
        "editeur": "S. Karger, Berlin",
        "source": "Project Gutenberg #24429 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/24429",
    },
    "witz": {
        "fichier": "1905_witz.pg.txt",
        "titre": "Der Witz und seine Beziehung zum Unbewußten",
        "titre_fr": "Le mot d'esprit et sa relation à l'inconscient",
        "annee_oeuvre": 1905,
        "annee_edition": 1912,
        "edition": "2. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #76423 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/76423",
    },
    "gradiva": {
        "fichier": "1907_gradiva.pg.txt",
        "titre": "Der Wahn und die Träume in W. Jensens »Gradiva«",
        "titre_fr": "Le délire et les rêves dans la « Gradiva » de W. Jensen",
        "annee_oeuvre": 1907,
        "annee_edition": 1907,     # PREMIÈRE édition — datation exacte
        "edition": "1. Auflage (Schriften zur angewandten Seelenkunde, erstes Heft)",
        "editeur": "Hugo Heller & Cie., Wien/Leipzig",
        "source": "Project Gutenberg #35549 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/35549",
    },
    "ueber_psychoanalyse": {
        "fichier": "1910_ueber_psychoanalyse.pg.txt",
        "titre": "Über Psychoanalyse: Fünf Vorlesungen",
        "titre_fr": "Cinq leçons sur la psychanalyse",
        "annee_oeuvre": 1910,
        "annee_edition": 1910,     # 2e tirage la même année — aucun écart
        "edition": "2. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #20613 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/20613",
    },
    "totem": {
        "fichier": "1913_totem_und_tabu.pg.txt",
        "titre": "Totem und Tabu",
        "titre_fr": "Totem et tabou",
        "annee_oeuvre": 1913,
        "annee_edition": 1922,
        "edition": "3., unveränderte Auflage",
        # La page de titre porte « UNVERÄNDERTE » : réimpression SANS modification. L'écart de
        # neuf ans n'introduit donc AUCUNE couche d'écriture — cas différent des éditions
        # « vermehrte » (augmentées) où les ajouts sont indiscernables. Voir `datation`.
        "texte_inchange": True,
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Project Gutenberg #37065 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/37065",
    },
    "unheimliche": {
        "fichier": "1919_das_unheimliche.pg.txt",
        "titre": "Das Unheimliche",
        "titre_fr": "L'inquiétante étrangeté",
        "annee_oeuvre": 1919,
        "annee_edition": 1919,     # parution originale dans Imago V — datation exacte
        "edition": "1re publication (Imago, Bd. V)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #34222 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/34222",
    },
    "massenpsychologie": {
        "fichier": "1921_massenpsychologie.pg.txt",
        "titre": "Massenpsychologie und Ich-Analyse",
        "titre_fr": "Psychologie des masses et analyse du moi",
        "annee_oeuvre": 1921,
        "annee_edition": 1921,     # PREMIÈRE édition — datation exacte
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Project Gutenberg #30843 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/30843",
    },
    "teufelsneurose": {
        "fichier": "1923_teufelsneurose.ws.txt",
        "titre": "Eine Teufelsneurose im siebzehnten Jahrhundert",
        "titre_fr": "Une névrose diabolique au XVIIᵉ siècle",
        "annee_oeuvre": 1923,
        "annee_edition": 1923,     # 1re publication (Imago IX) — datation exacte
        "edition": "1. Auflage (Imago, Bd. IX)",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien",
        "provenance": "wikisource",
        "source": "Wikisource DE (Bearbeitungsstand « fertig »)",
        "url": "https://de.wikisource.org/wiki/Eine_Teufelsneurose_im_siebzehnten_Jahrhundert",
        "fac_simile": "Imago 9-1.djvu (Wikimedia Commons)",
    },
    "neue_folge": {
        "fichier": "1933_neue_folge.ws.txt",
        "titre": "Neue Folge der Vorlesungen zur Einführung in die Psychoanalyse",
        "titre_fr": "Nouvelles conférences d'introduction à la psychanalyse",
        "annee_oeuvre": 1933,
        "annee_edition": 1933,     # 1. Auflage — datation exacte
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Wien",
        # PROVENANCE DIFFÉRENTE : Wikisource (allemand), et non Project Gutenberg. Le site
        # américain gutenberg.org ne distribue pas les œuvres tardives de Freud — non parce
        # qu'elles seraient protégées (mort en 1939 → libres depuis 2010 en Europe) mais parce
        # que le droit AMÉRICAIN se règle sur la date de publication. Wikisource, hébergé
        # ailleurs et sous licence libre, les propose légalement.
        "provenance": "wikisource",
        "source": "Wikisource DE (Bearbeitungsstand « fertig » : relu deux fois sur le fac-similé)",
        "url": "https://de.wikisource.org/wiki/Neue_Folge_der_Vorlesungen_zur_Einführung_in_die_Psychoanalyse",
        "fac_simile": "https://archive.org/details/Freud_1933_Neue_Folge_k",
    },
    "jenseits": {
        "fichier": "1920_jenseits_lustprinzips.pg.txt",
        "titre": "Jenseits des Lustprinzips",
        "titre_fr": "Au-delà du principe de plaisir",
        "annee_oeuvre": 1920,
        "annee_edition": 1921,
        # Établi par la page de titre elle-même : « 2. DURCHGESEHENE AUFLAGE (2.-4. TAUSEND) 1921 ».
        # Plus une supposition à confirmer : le texte le dit.
        "edition": "2. durchgesehene Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Project Gutenberg #28220 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/28220",
        "fac_simile": "https://archive.org/details/II_Freud_1920_Jenseits_k (1re éd., scan)",
    },
    "kindheitserinnerung_leonardo": {
        "fichier": "1910_kindheitserinnerung_leonardo.pg.txt",
        "titre": "Eine Kindheitserinnerung des Leonardo da Vinci",
        "titre_fr": "Un souvenir d'enfance de Léonard de Vinci",
        "annee_oeuvre": 1910,
        "annee_edition": 1910,     # PREMIÈRE édition — datation exacte
        "edition": "1. Auflage (Schriften zur angewandten Seelenkunde, VII. Heft)",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #75455 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/75455",
    },
    "schwierigkeit_psychoanalyse": {
        "fichier": "1917_schwierigkeit_psychoanalyse.pg.txt",
        "titre": "Eine Schwierigkeit der Psychoanalyse",
        "titre_fr": "Une difficulté de la psychanalyse",
        "annee_oeuvre": 1917,
        "annee_edition": 1917,     # 1re publication (Imago V, p. 1-7) — datation exacte
        "edition": "1. Auflage (Imago, Bd. V)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #29097 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/29097",
    },
    "moses_michelangelo": {
        "fichier": "1914_moses_michelangelo.pg.txt",
        "titre": "Der Moses des Michelangelo",
        "titre_fr": "Le Moïse de Michel-Ange",
        "annee_oeuvre": 1914,
        "annee_edition": 1914,     # 1re publication (Imago III, p. 15-36) — datation exacte
        "edition": "1. Auflage (Imago, Bd. III)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #30762 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/30762",
        # PUBLIÉ ANONYME EN 1914 : la page de titre porte « Von *** », et une note de la
        # rédaction d'Imago précise seulement que « der ihr bekannte Verfasser analytischen
        # Kreisen nahe steht » (l'auteur, connu de la rédaction, est proche des cercles
        # analytiques) — sans le nommer. Freud n'a reconnu la paternité du texte qu'en 1924,
        # dans ses Gesammelte Schriften. L'attribution à Freud est établie de longue date par
        # la recherche freudienne (confirmée par sa propre correspondance et son inclusion dans
        # ses œuvres complètes) : elle n'est donc pas déclarée par CE texte lui-même, à la
        # différence de tout le reste du corpus, qui se signe. Fait à savoir, pas à cacher.
        "attribution_non_signee": True,
    },
    "dichter_phantasieren": {
        "fichier": "1908_dichter_phantasieren.pg.txt",
        "titre": "Der Dichter und das Phantasieren",
        "titre_fr": "Le créateur littéraire et la fantaisie",
        "annee_oeuvre": 1908,
        "annee_edition": 1908,     # 1re publication (Neue Revue I, p. 716-724) — datation exacte
        "edition": "1. Auflage (Neue Revue, Bd. I, 1907/08)",
        "editeur": "Neue Revue, Wien",
        "source": "Project Gutenberg #28863 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/28863",
    },
    "zeitgemaesses_krieg_tod": {
        "fichier": "1915_zeitgemaesses_krieg_tod.pg.txt",
        "titre": "Zeitgemäßes über Krieg und Tod",
        "titre_fr": "Considérations actuelles sur la guerre et sur la mort",
        "annee_oeuvre": 1915,
        "annee_edition": 1915,     # 1re publication (Imago IV, p. 1-21) — datation exacte
        "edition": "1. Auflage (Imago, Bd. IV)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #29941 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/29941",
    },
    "traum_telepathie": {
        "fichier": "1922_traum_telepathie.pg.txt",
        "titre": "Traum und Telepathie",
        "titre_fr": "Rêve et télépathie",
        "annee_oeuvre": 1922,
        "annee_edition": 1922,     # 1re publication (Imago VIII, p. 1-22) — datation exacte
        "edition": "1. Auflage (Imago, Bd. VIII)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #31560 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/31560",
    },
    "vergaenglichkeit": {
        "fichier": "1916_vergaenglichkeit.pg.txt",
        "titre": "Vergänglichkeit",
        "titre_fr": "Éphémère destinée",
        "annee_oeuvre": 1916,
        "annee_edition": 1916,     # 1re publication — datation exacte
        "edition": "1. Auflage (« Das Land Goethes 1914-1916 », recueil du Berliner Goethebund)",
        "editeur": "Deutsche Verlags-Anstalt, Stuttgart/Berlin",
        "source": "Project Gutenberg #29514 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/29514",
    },
    "kindheitserinnerung_dichtung_wahrheit": {
        "fichier": "1917_kindheitserinnerung_dichtung_wahrheit.pg.txt",
        "titre": "Eine Kindheitserinnerung aus »Dichtung und Wahrheit«",
        "titre_fr": "Un souvenir d'enfance tiré de « Poésie et vérité »",
        "annee_oeuvre": 1917,
        "annee_edition": 1917,     # 1re publication (Imago V, p. 49-57) — datation exacte
        "edition": "1. Auflage (Imago, Bd. V)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #29946 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/29946",
    },
    "studien_ueber_hysterie": {
        "fichier": "1895_studien_ueber_hysterie.ws.txt",
        "titre": "Studien über Hysterie",
        "titre_fr": "Études sur l'hystérie",
        "annee_oeuvre": 1895,
        "annee_edition": 1895,     # PREMIÈRE édition — datation exacte
        "edition": "1. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "provenance": "wikisource",
        "source": ("Wikisource DE — 275 pages, toutes en Bearbeitungsstand « fertig » "
                   "(relues deux fois sur le fac-similé)"),
        "url": "https://de.wikisource.org/wiki/Studien_über_Hysterie",
        # ŒUVRE CO-ÉCRITE, et pas à la marge : le volume fondateur de la psychanalyse est signé
        # « Dr. Jos. Breuer und Dr. Sigm. Freud ». Josef Breuer y écrit DEUX blocs — le cas
        # d'Anna O. (la patiente qui a nommé la « talking cure ») et l'INTÉGRALITÉ du chapitre
        # théorique III —, soit environ 30 % du volume. Le texte le déclare lui-même à chaque
        # section : « Beobachtung I. Frl. Anna O … (Breuer) », « III. Theoretisches. (J. Breuer.) ».
        # Sans ces bornes, un tiers de la théorie de BREUER — l'état hypnoïde, qu'il défend et
        # que Freud abandonnera — serait mesuré comme du Freud.
        "contributions": [
            {"auteur": "Josef Breuer",
             "debut": "Beobachtung I. Frl. Anna O",
             "fin": "II. Frau Emmy v. N"},
            {"auteur": "Josef Breuer",
             "debut": "III. Theoretisches.",
             "fin": "IV. Zur Psychotherapie der Hysterie."},
        ],
    },
    "kaestchenwahl": {
        "fichier": "1913_kaestchenwahl.pg.txt",
        "titre": "Das Motiv der Kästchenwahl",
        "titre_fr": "Le motif du choix des coffrets",
        "annee_oeuvre": 1913,
        "annee_edition": 1913,     # 1re publication (Imago II.3) — datation exacte
        "edition": "1. Auflage (Imago, Bd. II, Heft 3)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #24017 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/24017",
    },
    "charaktertypen": {
        "fichier": "1916_charaktertypen.pg.txt",
        "titre": "Einige Charaktertypen aus der psychoanalytischen Arbeit",
        "titre_fr": "Quelques types de caractères dégagés par la psychanalyse",
        "annee_oeuvre": 1916,
        "annee_edition": 1916,     # 1re publication (Imago IV, p. 317-336) — datation exacte
        "edition": "1. Auflage (Imago, Bd. IV)",
        "editeur": "Internationaler Psychoanalytischer Verlag",
        "source": "Project Gutenberg #29101 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/29101",
    },
}

# ŒUVRES ÉCARTÉES APRÈS VÉRIFICATION — à ne pas réintroduire par inadvertance.
#
# Project Gutenberg publie AUSSI les quatre essais de « Totem und Tabu » séparément, tels
# qu'ils parurent dans la revue Imago (1912-1913), AVANT leur réunion en volume :
#   #37066 Die Inzestscheu · #37069 Das Tabu und die Ambivalenz der Gefühlsregungen
#   #37070 Animismus, Magie und Allmacht der Gedanken · #37071 Die infantile Wiederkehr des Totemismus
# Ce sont des DOUBLONS du volume déjà présent (#37065) : vérifié par comparaison de fragments —
# 8 fragments longs sur 8, pris au tiers du texte, se retrouvent mot pour mot dans « totem ».
# Les ajouter compterait deux fois les mêmes phrases et fausserait toute densité.
DOUBLONS_ECARTES = {
    "37066": "Die Inzestscheu — chapitre I de Totem und Tabu (#37065)",
    "37069": "Das Tabu und die Ambivalenz — chapitre II de Totem und Tabu",
    "37070": "Animismus, Magie und Allmacht der Gedanken — chapitre III de Totem und Tabu",
    "37071": "Die infantile Wiederkehr des Totemismus — chapitre IV de Totem und Tabu",
}

# Domaine public : Freud est mort en 1939 → libre de droits (vie + 70 ans) depuis 2010, et les
# éditions utilisées sont antérieures à 1931 (règle américaine). Le texte allemand ORIGINAL est
# donc libre ; c'est aussi ce qui garantit au lecteur la citation authentique, sans intermédiaire
# de traduction.
LICENCE = ("Domaine public — Sigmund Freud (1856-1939), œuvre libre de droits depuis 2010 "
           "(vie + 70 ans). Éditions utilisées antérieures à 1931. Texte allemand original.")


def charger(cle):
    """Charge une œuvre → {texte, meta}. `texte` = l'œuvre SEULE (hors en-tête/licence Gutenberg)."""
    if cle not in OEUVRES:
        raise KeyError("œuvre inconnue : %s (connues : %s)" % (cle, ", ".join(sorted(OEUVRES))))
    meta = dict(OEUVRES[cle])
    chemin = os.path.join(DOSSIER_DE, meta["fichier"])
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    texte, bornage = _extraire_corps(brut, meta.get("provenance", "gutenberg"))
    texte, note_fin = _retirer_paratexte_final(texte, cle)
    bornage += " ; " + note_fin
    meta.update({
        "cle": cle,
        "empreinte_fichier": hashlib.sha256(brut.encode("utf-8")).hexdigest()[:16],
        "caracteres_fichier": len(brut),
        "caracteres_oeuvre": len(texte),
        "bornage_gutenberg": bornage,
        "licence": LICENCE,
        "datation": datation(meta),
    })
    return {"texte": texte, "meta": meta}


def _extraire_corps(brut, provenance="gutenberg"):
    """Retire l'en-tête/licence Gutenberg PUIS le paratexte du transcripteur.

    Si une borne manque, on le DIT dans le rapport plutôt que de laisser croire à un texte propre :
    un corpus silencieusement pollué est pire qu'un corpus dont on connaît le défaut.
    """
    if provenance != "gutenberg":
        corps, note = _nettoyer_wikisource(brut)
        corps, note_lim = _retirer_liminaires_wikisource(corps)
        return corps, "source Wikisource — " + note + " ; " + note_lim
    d = _DEBUT.search(brut)
    f = _FIN.search(brut)
    if not d or not f or f.start() <= d.end():
        return brut, "bornes Gutenberg introuvables — texte pris intégralement, À VÉRIFIER"
    corps = brut[d.end():f.start()]
    notes = []
    corps, n = _NOTE_TETE.subn("", corps)
    notes.append("note de transcription en tête %s" % ("retirée" if n else "absente"))
    corps, n = _NOTE_QUEUE.subn("", corps)
    notes.append("liste d'errata en queue %s" % ("retirée" if n else "absente"))
    corps, note = _retirer_liminaires(corps)
    notes.append(note)
    return corps.strip(), "bornes Gutenberg retirées ; " + " ; ".join(notes)


def _nettoyer_wikisource(brut):
    """Retire les apports de Wikisource : blocs de notes et liens d'édition.

    Wikisource clôt chaque page par « Anmerkungen (Wikisource) » suivi d'entrées « ↑ … » — des
    notes rédigées par les contributeurs pour identifier personnes et ouvrages cités. Utiles au
    lecteur du site, ce ne sont PAS des phrases de Freud : atomisées, elles produisaient des
    énoncés du genre « ↑ Karl Marx (Wikipedia) ». Huit blocs, 92 entrées dans les Neue Folge.
    """
    # Le bloc de notes clôt toujours une section et court jusqu'au TITRE de la suivante (ligne
    # entièrement capitale, posée à l'assemblage). Borner sur « la première ligne qui commence par
    # une majuscule » ne suffisait pas : une note longue se poursuit sur plusieurs lignes, dont
    # certaines commencent par une majuscule — onze notes survivaient ainsi.
    est_titre = lambda s: bool(s) and s == s.upper() and any(c.isalpha() for c in s) and len(s) < 80
    lignes, garde, dans_notes, retires = brut.split("\n"), [], False, 0
    for ligne in lignes:
        nu = ligne.strip()
        if nu.startswith("Anmerkungen (Wikisource)"):
            dans_notes, retires = True, retires + 1
            continue
        if dans_notes:
            if est_titre(nu):
                dans_notes = False          # la section suivante commence : le bloc est clos
            else:
                continue
        if nu == "Bearbeiten":              # lien d'édition MediaWiki égaré
            continue
        garde.append(ligne)
    texte = "\n".join(garde)
    # Flèche de retour restante : elle ouvre les notes de bas de page DE FREUD, que Wikisource rend
    # ainsi. Le texte est de lui — on ne retire que le signe de renvoi, jamais la note.
    texte = re.sub(r"^[ \t]*↑[ \t]*", "", texte, flags=re.M)
    texte = re.sub(r"\n{3,}", "\n\n", texte).strip()
    return texte, ("%d bloc(s) de notes Wikisource retiré(s)" % retires if retires
                   else "aucun bloc de notes")


def _retirer_paratexte_final(corps, cle):
    """Coupe la bibliographie ou la réclame d'éditeur qui clôt certains volumes."""
    marqueur = PARATEXTE_FINAL.get(cle)
    if not marqueur:
        return corps, "pas de paratexte final déclaré"
    i = corps.find(marqueur)
    # Garde-fou : le même intitulé peut apparaître ailleurs (page de titre, note). On ne coupe que
    # si la borne tombe dans le dernier tiers — sinon on le signale plutôt que d'amputer le texte.
    if i < 0:
        return corps, "paratexte final « %s » introuvable — À VÉRIFIER" % marqueur[:30]
    if i < 0.66 * len(corps):
        return corps, "borne « %s » trouvée trop tôt (%d %%) — non appliquée" % (
            marqueur[:24], round(100 * i / len(corps)))
    return corps[:i].strip(), "paratexte final retiré (%d signes)" % (len(corps) - i)


def _retirer_liminaires_wikisource(corps):
    """Page de titre et table des matières d'une transcription Wikisource page par page.

    Ces transcriptions incluent le livre TEL QU'IMPRIMÉ, page de titre comprise — à la
    différence des pages d'espace principal déjà assemblées (« Neue Folge », « Teufelsneurose »),
    qui n'en ont pas. Sans ce retrait, « STUDIEN ÜBER HYSTERIE VON Dr. JOS. » devenait le premier
    atome de l'œuvre.

    La PRÉFACE est conservée — elle est datée et signée (« April 1895. J. Breuer, S. Freud »),
    donc le seul matériau dont la datation soit certaine. On coupe jusqu'à son titre, pas au-delà.
    """
    faits = []
    t = _PREMIER_TITRE_WS.search(corps)
    if t and t.start() > 0:
        corps = corps[t.start():]
        faits.append("page de titre retirée")
    # Table des matières : son intitulé et la ligne de titre du premier chapitre qu'elle annonce.
    # Le tableau lui-même a déjà disparu à la récupération (bin/recuperer_wikisource.py).
    m = _TOC_TITRE_WS.search(corps)
    if m:
        corps = corps[:m.start()] + corps[m.end():]
        faits.append("intitulé de table des matières retiré")
    return corps.strip(), (" ; ".join(faits) if faits else "aucun liminaire détecté")


def _retirer_liminaires(corps):
    """Retire la page de titre puis la table des matières. Déterministe et borné."""
    faits = []
    # 1. Page de titre : tout ce qui précède le premier vrai titre de section — une préface si
    #    elle existe, sinon le premier chapitre (œuvre sans préface).
    t = _PREMIER_TITRE.search(corps) or _PREMIER_CHAPITRE.search(corps)
    if t and t.start() > 0:
        corps = corps[t.start():]
        faits.append("page de titre retirée")
    # 2. Table des matières : de son titre à sa DERNIÈRE entrée « libellé … numéro ».
    m = _TOC_TITRE.search(corps)
    if m:
        lignes = corps[m.end():].split("\n")
        fin_relative, curseur, hors_toc = 0, 0, 0
        for ligne in lignes:
            curseur += len(ligne) + 1
            if _TOC_LIGNE.match(ligne):
                fin_relative, hors_toc = curseur, 0
            elif ligne.strip():
                hors_toc += 1
                if hors_toc >= 3:      # trois lignes pleines non conformes → on a quitté la table
                    break
        if fin_relative:
            corps = corps[:m.start()] + corps[m.end() + fin_relative:]
            faits.append("table des matières retirée")
    return corps, (" ; ".join(faits) if faits else "aucun liminaire détecté")


def datation(meta):
    """Statut de datation d'un atome issu de cette œuvre — honnête par construction.

    Trois cas, et non deux :
      • ÉDITION D'ORIGINE (écart nul) → date certaine.
      • RÉIMPRESSION INCHANGÉE (« unveränderte Auflage ») → le texte est celui de l'origine
        même si l'exemplaire est tardif : aucune couche ajoutée, donc date certaine elle aussi.
        Ignorer cette distinction ferait rejeter comme incertaines des œuvres parfaitement datées.
      • ÉDITION AUGMENTÉE OU REVUE → on ne connaît qu'une borne SUPÉRIEURE : Freud a cessé de
        signaler ses ajouts, ils sont indiscernables dans le texte.
    """
    ecart = meta["annee_edition"] - meta["annee_oeuvre"]
    inchange = bool(meta.get("texte_inchange"))
    precise = ecart == 0 or inchange
    if ecart == 0:
        regle = "édition d'origine (%d) — date certaine" % meta["annee_oeuvre"]
    elif inchange:
        regle = ("réimpression INCHANGÉE de %d (exemplaire de %d) — texte d'origine, date certaine"
                 % (meta["annee_oeuvre"], meta["annee_edition"]))
    else:
        regle = ("attesté au plus tard dans l'édition %d ; première apparition inconnue dans [%d, %d]"
                 % (meta["annee_edition"], meta["annee_oeuvre"], meta["annee_edition"]))
    return {
        "annee_oeuvre": meta["annee_oeuvre"],
        "annee_edition_lue": meta["annee_edition"],
        "fenetre_incertitude_annees": 0 if precise else ecart,
        "precise": precise,
        "texte_inchange": inchange,
        "regle": regle,
        "levee_possible_par": (None if precise else
                               "collation avec la 1re édition (fac-similé) — chantier distinct, non fait"),
    }


def manifeste():
    """Manifeste de provenance de tout le corpus — ce qu'un chercheur doit pouvoir vérifier."""
    entrees = []
    for cle in OEUVRES:
        chemin = os.path.join(DOSSIER_DE, OEUVRES[cle]["fichier"])
        present = os.path.exists(chemin)
        e = dict(OEUVRES[cle], cle=cle, present=present)
        if present:
            with open(chemin, "rb") as f:
                donnees = f.read()
            e["empreinte_fichier"] = hashlib.sha256(donnees).hexdigest()[:16]
            e["octets"] = len(donnees)
            e["datation"] = datation(OEUVRES[cle])
        entrees.append(e)
    return {
        "version": "1.0.0",
        "licence": LICENCE,
        "avertissement_datation": (
            "Aucune de ces éditions n'est une première édition. Freud a renoncé, à partir de la 3e "
            "édition des Drei Abhandlungen, à signaler ses ajouts. Les couches d'écriture sont donc "
            "INDISCERNABLES dans le texte : un atome est attesté au plus tard dans l'édition lue, "
            "jamais daté de l'année de l'œuvre."),
        "oeuvres": entrees,
    }


if __name__ == "__main__":
    print(json.dumps(manifeste(), ensure_ascii=False, indent=1))
