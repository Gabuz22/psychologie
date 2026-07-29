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
DOSSIER_SOURCES = os.path.join(RACINE, "sources")
DOSSIER_DE = os.path.join(DOSSIER_SOURCES, "freud", "de")

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
    # L'édition de 1895 clôt le volume par sa table analytique (libellés + numéros de page) :
    # du paratexte de navigation, pas du texte de Le Bon.
    "psychologie_des_foules": "TABLE DES MATIÈRES",
    # Otto Rank — catalogues d'éditeur, bibliographies et, pour l'Inzest-Motiv, la fiche de prêt
    # de la bibliothèque de l'Université de Colombie-Britannique, scannée avec le volume.
    "der_kuenstler": "Hugo Heller",
    "mythus_geburt_helden": "Verlag von Franz Deuticke",
    "lohengrinsage": "Literaturverzeichnis",
    # Espaces SIMPLES : le traitement OCR normalise les blancs avant cette coupe.
    "inzest_motiv": "University of British Columbia",
    # Le volume se clôt sur « Geschrieben im April 1923 », puis la liste des livres de Rank.
    "trauma_der_geburt": "Von Dr. Otto Rank erschienen früher:",
    # L'en-tête du catalogue est ici cassé par l'OCR — « Franz Den ticke » —, ce qui a fait
    # échouer la borne évidente. On prend donc la forme RÉELLEMENT présente dans ce scan.
    "genetische_psychologie_2": "Verlag von Franz Den ticke",
    # Karl Abraham — catalogues d'éditeur en fin de volume.
    "traum_und_mythus": "Verlag von Franz Deuticke",
    "segantini": "VERLAG VON FRANZ DEUTICKE",
    # Ces deux volumes placent leur table des matières EN FIN de livre : la borne est donc
    # cette table, non le catalogue de l'éditeur qui vient encore après.
    "klinische_beitraege": "Inhaltsübersicht.",
    "entwicklungsgeschichte_libido": "Inhaltsverzeichnis",
    "charakterbildung": "INTERNATIONALER PSYCHOANALYTISCHER",
    # Sándor Ferenczi — tables des matières de fin, bibliographies et index dressés par l'éditeur.
    "populaere_vortraege": "Inhaltsverzeichnis",
    # La borne est relevée sur le texte APRÈS recollage des césures : le fac-similé imprime
    # « psycho-\nanalytische », que le traitement ressoude avant que cette coupe s'applique.
    # Relevée sur le fac-similé brut, elle était introuvable — et le garde-fou l'a dit.
    "genitaltheorie": "Introjektion und Übertragung. Eine psychoanalytische Studie",
    "bausteine_1": "Von Dr. S. Ferenczi ist früher im Internationalen",
    # Le « Register » des Bausteine II est un index de matières couvrant les DEUX tomes, dressé
    # par l'éditeur : ce n'est pas Ferenczi, et il pèse 10 % du volume.
    "bausteine_2": "Register",
    # Ce volume-ci n'a ni bibliographie ni catalogue : seule la dernière page, que l'OCR ne lit
    # pas, est écartée — d'où une borne qui est une tête courante mutilée, relevée telle quelle.
    "bausteine_3": "Freuds Einfluss auf die en",
}


# RÉGIONS ÉCARTÉES AU MILIEU D'UN VOLUME — attribution NON ÉTABLIE, donc texte non retenu.
# Le format est (début, fin, motif). Les deux bornes sont relevées dans le texte ; leur absence
# fait ÉCHOUER le chargement, pour qu'une région qu'on croit écartée ne reste jamais en place.
REGIONS_ECARTEES = {
    "bausteine_3": [(
        "Entwicklungsziele der Psychoanalyse",
        "von Sexualgewohnheiten",
        "« Entwicklungsziele der Psychoanalyse » (1924) est tiré du livre CO-SIGNÉ par Ferenczi "
        "et Otto Rank. Les éditeurs du volume l'écrivent eux-mêmes en note : seul le chapitre III "
        "est attesté de Ferenczi (le chapitre II est de Rank et n'est pas réimprimé ici) ; les "
        "chapitres I et V lui sont attribués parce que « Frau Dr. Ferenczi glaubt sich erinnern "
        "zu können » et parce qu'ils croient y reconnaître son style. Leur lettre à Rank est "
        "restée sans réponse. Un corpus qui existe pour rendre ses attributions vérifiables ne "
        "peut pas retenir un texte attribué sur un souvenir et un jugement de style. On RETIRE "
        "— ce qui est décidable — au lieu d'attribuer, ce qui ne l'est pas ici."
    )],
}

# FAC-SIMILÉS ÉCARTÉS APRÈS MESURE — deux volumes de Rank existent en ligne mais ne sont PAS
# citables. Leur OCR confond le digramme « ch » de la typographie ancienne, et le défaut est
# invisible au comptage de caractères parasites : les formes produites n'utilisent que des
# lettres ordinaires. Seule la mesure de `core/ocr.py:corruption()` les distingue.
# Trace obligatoire : une décision négative non écrite sera refaite, et le prochain qui trouvera
# ces scans les croira utilisables.
FAC_SIMILES_ECARTES = {
    "DieDonJuan-gestalt": (
        "Die Don Juan-Gestalt (1924) — « ch » lu « di » : 30 des 92 « nicht » écrits « nidit », "
        "184 séquences impossibles, 32,6 % des mots témoins corrompus. Inutilisable pour citer."),
    "Rank_1925_Doppelgaenger_k": (
        "Der Doppelgänger (1925, texte de 1914) — « ch » réduit à « h » : « sih », « auh », "
        "« natürlih ». 7,1 % des PHRASES atteintes, soit un atome sur quatorze. Sous le seuil "
        "du premier contrôle (écrit pour « di »), ce défaut n'a été trouvé qu'en LISANT le texte."),
    "ZurPsychoanalyseDerKriegsneurosen": (
        "Zur Psychoanalyse der Kriegsneurosen (1919) — écarté pour une raison de STRUCTURE, non "
        "de qualité : son OCR est excellent. C'est un SYMPOSIUM à cinq voix — Freud signe "
        "l'introduction, puis Ferenczi, Abraham, Simmel et Jones discutent tour à tour. Or le "
        "lexique suit l'auteur du VOLUME, et un volume à cinq auteurs n'en a pas. L'accueillir "
        "demanderait un lexique par RÉGION, extension de l'architecture à part entière. "
        "À reprendre quand Ferenczi entrera : ce volume les concerne tous les deux."),
    # SÁNDOR FERENCZI — trois tirés à part ÉCARTÉS POUR DUPLICATION, non pour qualité : leur OCR
    # est excellent. Chacun est réimprimé dans les Bausteine, et les garder aurait compté deux
    # fois les mêmes phrases. Le recouvrement est mesuré en suites de HUIT mots ; il plafonne
    # vers 50 % parce que l'OCR des deux tirages diffère, non parce que la moitié du texte
    # manquerait.
    "IntrojektioneUndUbertragung": (
        "Introjektion und \u00dcbertragung (1910) \u2014 49,6 % de ses suites de huit mots se retrouvent "
        "dans les Bausteine I (1927), qui le r\u00e9impriment. C'est l'article fondateur de "
        "l'introjection : il EST dans le corpus, par le recueil."),
    "HysterieUndPathoneurosen": (
        "Hysterie und Pathoneurosen (1919) \u2014 56,4 % de recouvrement avec les Bausteine III."),
    "Ferenczi_1925_Sexualgewohnheiten_k": (
        "Psychoanalyse der Sexualgewohnheiten (1925) \u2014 46,4 % de recouvrement avec les "
        "Bausteine III, qui le r\u00e9impriment sous le titre \u00ab Zur Psychoanalyse von "
        "Sexualgewohnheiten \u00bb."),
    # Ce volume-ci reste écarté, mais son motif a CHANGÉ avec l'arrivée de Ferenczi : le problème
    # n'est plus qu'on ignore comment traiter un volume à cinq auteurs, c'est qu'on ne saurait
    # pas découper les cinq contributions sur des bornes vérifiables. REGIONS_ECARTEES sait
    # désormais RETIRER une région ; il faudrait ici en RETENIR cinq, et les attribuer chacune.
    # Chantier à part, et toujours pas ouvert.
    "EineNeurosenanalyseInTraeumen": (
        "Eine Neurosenanalyse in Träumen (1924) — 2,6 % des phrases atteintes, au-dessus du seuil "
        "de 2 %. Cas limite, et c'est précisément pour ceux-là qu'un seuil existe : sans lui, "
        "chaque volume douteux se discuterait au cas par cas et finirait par entrer."),
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
    # ------------------------------------------------------------------- OTTO RANK (1884-1939)
    # Premier auteur traité POUR LUI-MÊME, avec ses propres catégories (voir core/lexiques/).
    # Le corpus le connaissait déjà par fragment : l'appendice de la 4e édition de la
    # Traumdeutung, 334 atomes — un cas de calibrage idéal, on avait un échantillon de sa plume
    # avant d'avoir son œuvre.
    #
    # PROVENANCE « archive » : ce sont des FAC-SIMILÉS OCRISÉS, non relus par des humains. Le
    # corpus avait refusé l'OCR pour Freud, et il avait raison de le faire : Gutenberg offrait
    # une transcription relue, l'OCR n'aurait été qu'une dégradation gratuite. Pour Rank, aucune
    # transcription relue n'existe — ni Gutenberg, ni Wikisource. L'arbitrage n'est donc plus
    # « OCR ou mieux » mais « OCR ou rien », et renoncer laisserait le corpus définitivement
    # monopolaire, contre le but même du projet. La qualité est MESURÉE œuvre par œuvre
    # (`core/ocr.py`), les défauts sont recollés quand c'est déterministe, et chaque phrase
    # encore suspecte est MARQUÉE individuellement. Voir FAC_SIMILES_ECARTES : deux volumes ont
    # été refusés sur ces mesures.
    "der_kuenstler": {
        "fichier": "1907_der_kuenstler.ia.txt",
        "dossier": ("rank", "de"),
        "provenance": "archive",
        "auteur": "Otto Rank",
        "titre": "Der Künstler. Ansätze zu einer Sexual-Psychologie",
        "titre_fr": "L'artiste. Éléments d'une psychologie sexuelle",
        "annee_oeuvre": 1907,
        "annee_edition": 1907,     # 1re édition — datation exacte
        "edition": "1. Auflage",
        "editeur": "Hugo Heller & Cie, Wien",
        "source": "Internet Archive (numérisation Google) — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/derknstleranstz00rankgoog",
        # LE PREMIER LIVRE DE RANK, publié à vingt-trois ans, celui qui lui a valu l'attention de
        # Freud. Sa thèse de l'artiste y est déjà entière, dix-sept ans avant la rupture : le
        # corpus tient donc son point de départ ET son point d'arrivée.
        "debut_corps": "Eine richtige Erkenntnis vom Wesen des Künstlers",
    },
    "mythus_geburt_helden": {
        "fichier": "1909_mythus_geburt_helden.ia.txt",
        "dossier": ("rank", "de"),
        "provenance": "archive",
        "auteur": "Otto Rank",
        "titre": "Der Mythus von der Geburt des Helden",
        "titre_fr": "Le mythe de la naissance du héros",
        "annee_oeuvre": 1909,
        "annee_edition": 1909,     # 1re édition — datation exacte
        "edition": "1. Auflage (Schriften zur angewandten Seelenkunde, V. Heft)",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/SzaS_5_Rank_1909_Mythus_von_der_Geburt_des_Helden",
        # Même série et même éditeur que la « Gradiva » de Freud (Heft 1), déjà au corpus.
        "debut_corps": "Vorbemerkung.",
    },
    "lohengrinsage": {
        "fichier": "1911_lohengrinsage.ia.txt",
        "dossier": ("rank", "de"),
        "provenance": "archive",
        "auteur": "Otto Rank",
        "titre": "Die Lohengrinsage",
        "titre_fr": "La légende de Lohengrin",
        "annee_oeuvre": 1911,
        "annee_edition": 1911,     # 1re édition — datation exacte
        "edition": "1. Auflage (Schriften zur angewandten Seelenkunde, XIII. Heft)",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/SzaS_13_Rank_1911_Die_Lohengrinsage",
        # Borne prise sur la PREMIÈRE PHRASE et non sur le titre « Einführung » : ce mot
        # reparaît trois fois dans le corps du texte, et la borne y tombait en pleine phrase.
        "debut_corps": "Die Sage von Lohengrin, dem Ritter mit dem Schwane",
    },
    "inzest_motiv": {
        "fichier": "1912_inzest_motiv.ia.txt",
        "dossier": ("rank", "de"),
        "provenance": "archive",
        "auteur": "Otto Rank",
        "titre": "Das Inzest-Motiv in Dichtung und Sage",
        "titre_fr": "Le motif de l'inceste dans la poésie et la légende",
        "annee_oeuvre": 1912,
        "annee_edition": 1912,     # 1re édition — datation exacte
        "edition": "1. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/dasinzestmotivin00rank",
        # 2,3 Mo : de loin le plus gros volume du corpus, toutes plumes confondues.
        "debut_corps": "Vorwort.",
    },
    "trauma_der_geburt": {
        "fichier": "1924_trauma_der_geburt.ia.txt",
        "dossier": ("rank", "de"),
        "provenance": "archive",
        "auteur": "Otto Rank",
        "titre": "Das Trauma der Geburt und seine Bedeutung für die Psychoanalyse",
        "titre_fr": "Le traumatisme de la naissance",
        "annee_oeuvre": 1924,
        "annee_edition": 1924,     # 1re édition — datation exacte
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/DasTraumaDerGeburtUndSeineBedeutungFrDiePsychoanalyse",
        # LE livre de la rupture avec Freud : Rank y place l'angoisse de la naissance là où
        # Freud met le complexe d'Œdipe. Sa présence au corpus rend la divergence mesurable.
        # « Vorbemerkung » apparaît d'abord dans la TABLE DES MATIÈRES : la borne y tombait,
        # et le premier atome du livre était une ligne de points de conduite.
        "debut_corps": "Die nachstehenden Ausführungen bedeuten einen ersten Versuch",
    },
    "genetische_psychologie_2": {
        "fichier": "1928_genetische_psychologie_2.ia.txt",
        "dossier": ("rank", "de"),
        "provenance": "archive",
        "auteur": "Otto Rank",
        "titre": "Grundzüge einer Genetischen Psychologie, II. Teil",
        "titre_fr": "Principes d'une psychologie génétique, IIe partie",
        "annee_oeuvre": 1928,
        "annee_edition": 1928,     # 1re édition — datation exacte
        "edition": "1. Auflage (Genetische Psychologie, II. Teil)",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/Rank_1928_Genetische_Psychologie_II_k",
        # Même piège que pour le Trauma : « Einleitung. » ouvre la table des matières.
        "debut_corps": "Die Psychoanalyse hat im",
    },
    # ------------------------------------------------------------ KARL ABRAHAM (1877-1925)
    # Troisième auteur traité pour lui-même. Le cas de figure INVERSE de Rank, et c'est pourquoi
    # il vient tout de suite après : Abraham n'a jamais rompu avec Freud. Fondateur de la société
    # de Berlin, analyste de Klein et de Horney, il meurt à quarante-huit ans en pleine fidélité.
    # Le corpus tient donc les deux figures de l'entourage — celui qui s'écarte et celui qui
    # approfondit —, ce qui est la condition pour distinguer un jour, sur des mesures, un SOCLE
    # PARTAGÉ d'une divergence.
    #
    # Domaine public depuis 1996 (mort en 1925 + 70 ans) ; toutes les éditions sont antérieures
    # à 1930, donc libres aussi selon la règle américaine.
    # Fac-similés OCRisés comme pour Rank, mais d'une qualité nettement supérieure : 0,10 à
    # 0,95 ‰ de caractères parasites — au niveau ou SOUS celui des transcriptions relues — et
    # 0,0 à 0,1 % de phrases corrompues.
    "traum_und_mythus": {
        "fichier": "1909_traum_und_mythus.ia.txt",
        "dossier": ("abraham", "de"),
        "provenance": "archive",
        "auteur": "Karl Abraham",
        "titre": "Traum und Mythus. Eine Studie zur Völkerpsychologie",
        "titre_fr": "Rêve et mythe. Une étude de psychologie des peuples",
        "annee_oeuvre": 1909,
        "annee_edition": 1909,     # 1re édition — datation exacte
        "edition": "1. Auflage (Schriften zur angewandten Seelenkunde, IV. Heft)",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/TraumUndMythus.EineStudieZurVoumllkerpsychologie",
        # HEFT IV de la série où la « Gradiva » de Freud est le Heft I et le « Mythus » de Rank
        # le Heft V : trois auteurs du corpus, à deux ans d'intervalle, dans la même collection.
        "debut_corps": "Die psychologischen Theorien, welche sich an den Namen",
    },
    "segantini": {
        "fichier": "1911_segantini.ia.txt",
        "dossier": ("abraham", "de"),
        "provenance": "archive",
        "auteur": "Karl Abraham",
        "titre": "Giovanni Segantini. Ein psychoanalytischer Versuch",
        "titre_fr": "Giovanni Segantini. Un essai psychanalytique",
        "annee_oeuvre": 1911,
        "annee_edition": 1911,     # 1re édition — datation exacte
        "edition": "1. Auflage (Schriften zur angewandten Seelenkunde, XI. Heft)",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/SzaS_11_Abraham_1911_Segantini",
        "debut_corps": "Über Giovanni Segantinis Leben und Kunst besitzen wir",
    },
    "klinische_beitraege": {
        "fichier": "1921_klinische_beitraege.ia.txt",
        "dossier": ("abraham", "de"),
        "provenance": "archive",
        "auteur": "Karl Abraham",
        "titre": "Klinische Beiträge zur Psychoanalyse",
        "titre_fr": "Contributions cliniques à la psychanalyse",
        # RECUEIL D'ARTICLES parus de 1907 à 1920, réunis en volume en 1921. L'écart de quatorze
        # ans n'est pas une incertitude d'édition : c'est l'étendue réelle du matériau. La
        # datation reste bornée par le volume, comme pour toute œuvre dont les couches ne sont
        # pas signalées dans le texte.
        "annee_oeuvre": 1907,
        "annee_edition": 1921,
        "edition": "1. Auflage (Internationale Psychoanalytische Bibliothek, Bd. 10)",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/KlinischeBeitraumlgeZurPsychoanalyse",
        "debut_corps": "Wenn ich, einer Aufforderung des",
    },
    "entwicklungsgeschichte_libido": {
        "fichier": "1924_entwicklungsgeschichte_libido.ia.txt",
        "dossier": ("abraham", "de"),
        "provenance": "archive",
        "auteur": "Karl Abraham",
        "titre": "Versuch einer Entwicklungsgeschichte der Libido",
        "titre_fr": "Esquisse d'une histoire du développement de la libido",
        "annee_oeuvre": 1924,
        "annee_edition": 1924,     # 1re édition — datation exacte
        "edition": "1. Auflage (Neue Arbeiten zur ärztlichen Psychoanalyse, Heft II)",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/VersuchEinerEntwicklungsgeschichteDerLibidoAufGrundDerPsychoanalyse",
        # SON ŒUVRE MAJEURE, parue l'année même du « Trauma der Geburt » de Rank : les deux
        # hommes proposent la même année deux prolongements opposés de Freud. Le meilleur
        # matériau qu'on puisse souhaiter pour éprouver, plus tard, la mesure d'une divergence.
        "debut_corps": "Vor mehr als zehn Jahren habe ich zuerst den Versuch",
    },
    "charakterbildung": {
        "fichier": "1925_charakterbildung.ia.txt",
        "dossier": ("abraham", "de"),
        "provenance": "archive",
        "auteur": "Karl Abraham",
        "titre": "Psychoanalytische Studien zur Charakterbildung",
        "titre_fr": "Études psychanalytiques sur la formation du caractère",
        "annee_oeuvre": 1921,      # les trois études parurent de 1921 à 1925 en revue
        "annee_edition": 1925,
        "edition": "1. Auflage (Internationale Psychoanalytische Bibliothek, Nr. XVI)",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/PsychoanalytischeStudienZurCharakterbildung_524",
        "debut_corps": "Das weite Gebiet, welches heute der psychoanalytischen",
    },
    # ---------------------------------------------------------------- SECOND AUTEUR : GUSTAVE LE BON
    # Premier texte NON allemand du corpus — et pas un choix de circonstance : Freud consacre un
    # chapitre entier de « Massenpsychologie und Ich-Analyse » (1921) à discuter ce livre. Le
    # corpus tient ainsi les DEUX côtés d'une controverse réelle, chacun dans sa langue d'origine,
    # sur les mêmes concepts (masse/foule, suggestion, meneur, contagion, prestige, imitation).
    # Symétrie de dates : 1895 est aussi l'année des « Studien über Hysterie ».
    "psychologie_des_foules": {
        "fichier": "1895_psychologie_des_foules.pg.txt",
        "dossier": ("lebon", "fr"),
        "langue": "fr",
        "auteur": "Gustave Le Bon",
        "titre": "Psychologie des foules",
        "titre_fr": "Psychologie des foules",
        "annee_oeuvre": 1895,
        "annee_edition": 1895,     # 1re édition, Félix Alcan, Paris — datation exacte
        "edition": "1re édition (Bibliothèque de philosophie contemporaine)",
        "editeur": "Félix Alcan, Paris",
        "source": "Project Gutenberg #24007 (relu par Distributed Proofreaders, scans BnF/Gallica)",
        "url": "https://www.gutenberg.org/ebooks/24007",
        "licence": ("Domaine public — Gustave Le Bon (1841-1931), œuvre libre de droits depuis "
                    "2002 (vie + 70 ans). Édition de 1895. Texte français original."),
    },
    # ------------------------------------------------------------------ SÁNDOR FERENCZI
    # Quatrième auteur traité pour lui-même (2026-07). Le plus proche de Freud pendant vingt
    # ans, et celui dont la divergence finale porte sur la TECHNIQUE, non sur la doctrine : là
    # où Rank déplace une thèse et Abraham prolonge, Ferenczi change ce que l'analyste FAIT.
    # Le corpus tient donc trois formes distinctes du rapport au maître.
    #
    # Cinq volumes, 2,6 millions de signes retenus : le deuxième corpus du projet après Freud.
    # Tous mesurés sous le seuil OCR avec une marge large — 0,00 à 0,30 % de phrases atteintes
    # contre 2,0 % admis, et zéro à quatre séquences impossibles par volume.
    #
    # TROIS VOLUMES ÉCARTÉS APRÈS MESURE, pour une raison qui n'est pas la qualité mais la
    # DUPLICATION : « Introjektion und Übertragung » (1910), « Hysterie und Pathoneurosen »
    # (1919) et « Psychoanalyse der Sexualgewohnheiten » (1925) existent en tirés à part sur
    # Internet Archive, et sont réimprimés dans les Bausteine — recouvrement mesuré de 49,6 %,
    # 56,4 % et 46,4 % en suites de huit mots. Les retenir aurait compté deux fois les mêmes
    # phrases et faussé TOUTES les densités du corpus, y compris celles des autres auteurs par
    # comparaison. Les recueils l'emportent parce qu'ils contiennent en outre tout le reste ;
    # le prix payé est une fenêtre de datation large, portée explicitement.
    "populaere_vortraege": {
        "fichier": "1922_populaere_vortraege.ia.txt",
        "dossier": ("ferenczi", "de"),
        "provenance": "archive",
        "auteur": "S\u00e1ndor Ferenczi",
        "titre": "Popul\u00e4re Vortr\u00e4ge \u00fcber Psychoanalyse",
        "titre_fr": "Conf\u00e9rences populaires sur la psychanalyse",
        # Le volume date lui-même ses pièces en note : 1908, 1909, 1910, Imago I (1912),
        # oct. 1913, congrès de Munich 1913, IZ IV (1916), Imago V (1917-19), IZ V (1919).
        # La préface, datée « Budapest, im Mai 1921 », dit que certaines remontent à 1907/08.
        "annee_oeuvre": 1907,
        "annee_edition": 1922,
        "edition": "Internationale Psychoanalytische Bibliothek, Band XII",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Z\u00fcrich",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/PopulaumlreVortraumlgeuumlberPsychoanalyse",
        # La préface est de Ferenczi (signée de sa main) : elle fait partie de son texte.
        "debut_corps": "Vorwort",
    },
    "genitaltheorie": {
        "fichier": "1924_genitaltheorie.ia.txt",
        "dossier": ("ferenczi", "de"),
        "provenance": "archive",
        "auteur": "S\u00e1ndor Ferenczi",
        "titre": "Versuch einer Genitaltheorie",
        "titre_fr": "Essai d'une th\u00e9orie g\u00e9nitale (\u00ab Thalassa \u00bb)",
        # Ouvrage INÉDIT, non un recueil : datation exacte. L'introduction retrace sa genèse
        # (idées de 1914-15, exposées à Freud en 1915 puis 1919) et est signée d'août 1923.
        "annee_oeuvre": 1924,
        "annee_edition": 1924,
        "edition": "Internationale Psychoanalytische Bibliothek, Band XV",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Z\u00fcrich",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/VersuchEinerGenitaltheorie",
        # L'œuvre la plus personnelle de Ferenczi, et la seule du corpus à faire de la biologie
        # une méthode d'interprétation. Aucun autre auteur n'écrit « amphimixis » ni « thalassal ».
        "debut_corps": "EINLEITUNG",
    },
    "bausteine_1": {
        "fichier": "1927_bausteine_1_theorie.ia.txt",
        "dossier": ("ferenczi", "de"),
        "provenance": "archive",
        "auteur": "S\u00e1ndor Ferenczi",
        "titre": "Bausteine zur Psychoanalyse. I. Band: Theorie",
        "titre_fr": "Mat\u00e9riaux pour la psychanalyse. Tome I : Th\u00e9orie",
        # La table des matières donne entre crochets le lieu et l'année de première parution de
        # chaque article, de [Jb I, 1909] à [IZ XII, 1926] : la fenêtre est LUE, non estimée.
        "annee_oeuvre": 1909,
        "annee_edition": 1927,
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Z\u00fcrich",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/BausteineITheorie",
        # BORNE CONTRE-INTUITIVE, et c'est pourquoi elle est commentée. Le « Vorwort des
        # Verlags » (p. 7-8) est de l'ÉDITEUR, pas de Ferenczi : il doit rester dehors. Le titre
        # du premier article ne peut pas servir de borne, sa première occurrence étant dans la
        # table des matières, en amont. On prend donc l'année de parution qui suit ce titre —
        # que l'OCR a lue « (7909) » pour « (1909) ». On relève ce qui est écrit, jamais ce qui
        # devrait l'être.
        "debut_corps": "(7909)",
    },
    "bausteine_2": {
        "fichier": "1927_bausteine_2_praxis.ia.txt",
        "dossier": ("ferenczi", "de"),
        "provenance": "archive",
        "auteur": "S\u00e1ndor Ferenczi",
        "titre": "Bausteine zur Psychoanalyse. II. Band: Praxis",
        "titre_fr": "Mat\u00e9riaux pour la psychanalyse. Tome II : Pratique",
        # Crochets de la table des matières : de [Psychiatr.-Neurol. Wschr. X, 1908] à
        # [IZ XII, 1927].
        "annee_oeuvre": 1908,
        "annee_edition": 1927,
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Z\u00fcrich",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/BausteineZurPsychoanalyseIiPraxis",
        # Pas de préface d'éditeur dans ce tome : le corps commence au premier article. Le titre
        # de celui-ci est coupé par un saut de ligne et figure d'abord dans la table des
        # matières ; on prend donc le premier mot du corps, que l'OCR a privé de son « k ».
        "debut_corps": "Ausdrucsverschiebung",
    },
    "bausteine_3": {
        "fichier": "1939_bausteine_3.ia.txt",
        "dossier": ("ferenczi", "de"),
        "provenance": "archive",
        "auteur": "S\u00e1ndor Ferenczi",
        "titre": "Bausteine zur Psychoanalyse. III. Band: Arbeiten aus den Jahren 1908-1933",
        "titre_fr": "Mat\u00e9riaux pour la psychanalyse. Tome III : Travaux des ann\u00e9es 1908-1933",
        # Fenêtre DÉCLARÉE PAR LE VOLUME LUI-MÊME, jusque dans son sous-titre, chaque pièce de
        # la table des matières portant son année (parfois « etwa 1909 »). Ce tome posthume
        # contient le dernier Ferenczi, celui de la « Sprachverwirrung » (1933).
        "annee_oeuvre": 1908,
        # Le volume porte 1939, non 1938 comme l'annonce la notice d'Internet Archive : c'est la
        # page de titre qui fait foi (« VERLAG HANS HUBER BERN / 1939 »).
        "annee_edition": 1939,
        "edition": "Posthume, \u00e9dit\u00e9 par Vilma Kov\u00e1cs avec I. Hermann, A. et M. B\u00e1lint",
        "editeur": "Verlag Hans Huber, Bern",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/BausteineZurPsychoananalyseIiiArbeitenAusDenJahren1908-1933",
        # La préface de ce tome est signée VILMA KOVÁCS, non Ferenczi : la borne la laisse
        # dehors.
        "debut_corps": "Psychoanalyse und Padagogik",
        # RÉSERVE PORTÉE DANS LA BASE, et non seulement en commentaire. Deux pièces de ce volume
        # ne sont pas de sa seule main : « Entwicklungsziele der Psychoanalyse » (1924),
        # co-signé avec Otto Rank, est ÉCARTÉ (voir REGIONS_ECARTEES) ; « Zur Psychoanalyse der
        # paralytischen Geistesstörung » (1922) vient d'une monographie co-signée avec Stefan
        # Hollós, dont les éditeurs n'ont retenu que la part de Ferenczi — il y cite Hollós à la
        # troisième personne, ce qui est vérifiable dans le texte. Enfin, des notes de bas de
        # page signées « (Herausgeber.) » subsistent dans le corps.
        "reserve_attribution":
            "Volume posthume. Une pi\u00e8ce co-sign\u00e9e avec Otto Rank en a \u00e9t\u00e9 retir\u00e9e, faute "
            "d'attribution \u00e9tablie. Une autre provient d'une monographie co-sign\u00e9e avec Stefan "
            "Holl\u00f3s, dont les \u00e9diteurs d\u00e9clarent n'avoir repris que la part de Ferenczi. "
            "Quelques notes de bas de page sont des \u00e9diteurs, non de l'auteur.",
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
    dossier = os.path.join(DOSSIER_SOURCES, *meta["dossier"]) if meta.get("dossier") else DOSSIER_DE
    chemin = os.path.join(dossier, meta["fichier"])
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    texte, bornage = _extraire_corps(brut, meta.get("provenance", "gutenberg"),
                                     meta.get("langue", "de"), meta)
    texte, note_fin = _retirer_paratexte_final(texte, cle)
    bornage += " ; " + note_fin
    texte, note_regions = _retirer_regions_ecartees(texte, cle)
    if note_regions:
        bornage += " ; " + note_regions
    # Le rognage aux extrémités vient EN DERNIER pour les fac-similés : entre la fin du texte et
    # le catalogue de l'éditeur s'intercalent des pages de garde numérisées, qui ne deviennent
    # les dernières lignes du volume qu'une fois le catalogue retiré. Rogner avant les aurait
    # laissées en place, et le dernier atome du « Mythus » aurait été « Pen er y ww bo: ji ».
    if meta.get("provenance") == "archive":
        from . import ocr
        texte, r_rogne = ocr.rogner_aux_extremites(texte, _vocabulaire_relu())
        bornage += " ; rognage final : %d lignes en tête, %d en queue" % (
            r_rogne["rogne_tete"], r_rogne["rogne_queue"])
    meta.update({
        "cle": cle,
        "langue": meta.get("langue", "de"),
        "auteur": meta.get("auteur", "Sigmund Freud"),
        "empreinte_fichier": hashlib.sha256(brut.encode("utf-8")).hexdigest()[:16],
        "caracteres_fichier": len(brut),
        "caracteres_oeuvre": len(texte),
        "bornage_gutenberg": bornage,
        # La licence par défaut est celle de Freud ; une œuvre d'un autre auteur porte la sienne.
        "licence": meta.get("licence", LICENCE),
        "datation": datation(meta),
    })
    return {"texte": texte, "meta": meta}


def _vocabulaire_relu():
    """Vocabulaire allemand tiré des seules sources RELUES PAR DES HUMAINS.

    Sert de référence au recollage des césures d'un fac-similé. Y verser un texte OCR
    reviendrait à faire valider les erreurs de l'OCR par elles-mêmes — d'où le filtre strict
    sur la provenance, et le calcul mémorisé (il coûte le chargement de tout le corpus).
    """
    global _VOCABULAIRE_RELU
    if _VOCABULAIRE_RELU is None:
        from . import ocr
        textes = []
        for cle, m in OEUVRES.items():
            if m.get("langue", "de") == "de" and m.get("provenance", "gutenberg") != "archive":
                textes.append(charger(cle)["texte"])
        _VOCABULAIRE_RELU = ocr.vocabulaire_de_reference(textes)
    return _VOCABULAIRE_RELU


_VOCABULAIRE_RELU = None


def _extraire_corps_archive(brut, meta):
    """Corps utile d'un FAC-SIMILÉ OCRisé → (texte, rapport chiffré).

    Trois opérations, dans cet ordre, toutes déterministes :
      1. couper les liminaires — couvertures, gardes en papier marbré, pages de titre en
         caractères ornés. C'est là que l'OCR produit son charabia (« Okto Rank », « S
         Prohesekrteke Stuclie ») ; le corps, lui, est propre. La borne est DÉCLARÉE par œuvre
         (`debut_corps`), jamais devinée ;
      2. recoller les césures de fin de ligne, que les relecteurs humains résolvent et que
         l'OCR laisse ouvertes — 305 à 5 125 par volume, contre 0 à 4 dans un texte relu ;
      3. mesurer ce qui reste, et le DIRE. Le rapport voyage avec l'œuvre.
    """
    from . import ocr
    faits = []
    borne = meta.get("debut_corps")
    if borne:
        i = brut.find(borne)
        if i < 0:
            faits.append("borne de début « %s » INTROUVABLE — texte pris entier, À VÉRIFIER"
                         % borne[:30])
        elif i > 0.30 * len(brut):
            faits.append("borne de début trouvée trop tard (%d %%) — non appliquée, À VÉRIFIER"
                         % round(100 * i / len(brut)))
        else:
            faits.append("liminaires du fac-similé retirés (%d signes)" % i)
            brut = brut[i:]
    voc = _vocabulaire_relu()
    corps, rapport = ocr.recoller_cesures(brut, voc)
    faits.append("césures recollées : %d attestées + %d par règle d'orthographe, %d laissées "
                 "(élisions « Kunst- und »)" % (rapport["cesures_recollees_attestees"],
                                                rapport["cesures_recollees_par_regle"],
                                                rapport["cesures_laissees"]))
    corps, r_blocs = ocr.retirer_blocs_illisibles(corps, voc)
    faits.append("pages de garde numérisées retirées : %d lignes sur %d (%.1f %%)"
                 % (r_blocs["lignes_retirees"], r_blocs["lignes_totales"], r_blocs["part_pct"]))
    # Les têtes courantes viennent APRÈS le retrait des blocs illisibles et AVANT la normalisation
    # des blancs : elles sont lisibles (donc le filtre précédent les garde) et doivent disparaître
    # pendant qu'elles occupent encore une ligne à elles.
    corps, r_tetes = ocr.retirer_tetes_courantes(corps)
    faits.append("têtes courantes retirées : %d (%d formes)"
                 % (r_tetes["tetes_retirees"], len(r_tetes["formes"])))
    # Certains scans sortent le texte en colonnes justifiées, d'où des suites d'espaces au milieu
    # des phrases (« Die  nachstehende  Arbeit  lag »). Aucun mot n'est touché — seule la largeur
    # des blancs change —, mais sans cela chaque citation de l'Inzest-Motiv sortirait ainsi.
    corps = re.sub(r"[ \t]{2,}", " ", corps)
    faits.append("espaces multiples du scan normalisés")
    return corps.strip(), "fac-similé OCRisé NON RELU — " + " ; ".join(faits)


def _extraire_corps(brut, provenance="gutenberg", langue="de", meta=None):
    """Retire l'en-tête/licence Gutenberg PUIS le paratexte du transcripteur.

    Si une borne manque, on le DIT dans le rapport plutôt que de laisser croire à un texte propre :
    un corpus silencieusement pollué est pire qu'un corpus dont on connaît le défaut.
    """
    if provenance == "archive":
        return _extraire_corps_archive(brut, meta or {})
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
    if langue == "fr":
        corps, note = _retirer_liminaires_fr(corps)
        notes.append(note)
        # Le transcripteur regroupe les notes de bas de page sous un libellé « NOTES: » en fin
        # de chapitre : le libellé est à lui, le contenu des notes est à l'auteur — on ne retire
        # que le libellé.
        corps, n = re.subn(r"(?m)^NOTES:[ \t]*\n", "", corps)
        notes.append("%d libellés « NOTES: » du transcripteur retirés" % n)
        return corps.strip(), "bornes Gutenberg retirées ; " + " ; ".join(notes)
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


def _retirer_regions_ecartees(corps, cle):
    """Retire du CORPS des régions dont l'attribution à l'auteur du volume n'est pas établie.

    Les deux bornes précédentes coupent aux extrémités : elles suffisent pour du paratexte
    d'éditeur, qui se trouve toujours en tête ou en queue. Elles ne peuvent rien pour un texte
    d'un autre auteur imprimé AU MILIEU d'un recueil — et le corpus en contient un.

    Ce mécanisme est la forme minimale de l'extension que `FAC_SIMILES_ECARTES` annonçait à propos
    du symposium sur les névroses de guerre : on ne cherche pas à attribuer chaque région à son
    auteur (ce serait un lexique par région, autre chantier), on RETIRE ce dont on ne peut pas
    dire qu'il est de l'auteur du volume. Retirer est décidable ; attribuer ne l'est pas ici.

    Chaque borne échoue BRUYAMMENT si elle ne se retrouve pas : une région qu'on croit écartée et
    qui reste dans le texte est pire que pas de mécanisme du tout.
    """
    regions = REGIONS_ECARTEES.get(cle)
    if not regions:
        return corps, ""
    notes = []
    for debut, fin, _motif in regions:
        i = corps.find(debut)
        if i < 0:
            raise ValueError("région à écarter introuvable dans « %s » : début « %s »"
                             % (cle, debut[:40]))
        j = corps.find(fin, i + len(debut))
        if j < 0:
            raise ValueError("région à écarter non refermée dans « %s » : fin « %s »"
                             % (cle, fin[:40]))
        notes.append("%d signes" % (j - i))
        corps = corps[:i] + corps[j:]
    return corps, "région(s) écartée(s) : " + ", ".join(notes)


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


# Premier vrai titre d'une œuvre FRANÇAISE (l'édition Alcan de 1895 ouvre sur la préface).
# Regex propre au français : leçon du corpus — un correctif (ou une langue) ne doit jamais
# déplacer le défaut vers une autre œuvre, donc jamais toucher aux regex allemandes.
_PREMIER_TITRE_FR = re.compile(r"^[ \t]*(PRÉFACE|AVANT-PROPOS|INTRODUCTION)\b", re.M)


def _retirer_liminaires_fr(corps):
    """Liminaires d'un volume français : crédit du transcripteur, faux-titre, catalogue de
    l'éditeur (« DU MÊME AUTEUR »), page de titre, dédicace — tout ce qui précède le premier
    vrai titre. Dans « Psychologie des foules », la dédicace à Th. Ribot part avec la page de
    titre : trois lignes d'hommage, pas du texte de l'ouvrage.
    """
    t = _PREMIER_TITRE_FR.search(corps)
    if not t or t.start() == 0:
        return corps, "aucun liminaire français détecté — À VÉRIFIER"
    return corps[t.start():], "liminaires retirés (%d signes, jusqu'à « %s »)" % (
        t.start(), t.group(1))


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
        meta = OEUVRES[cle]
        dossier = os.path.join(DOSSIER_SOURCES, *meta["dossier"]) if meta.get("dossier") else DOSSIER_DE
        chemin = os.path.join(dossier, meta["fichier"])
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
