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
    # Sigmund Freud — les trois recueils dont le DERNIER article est déjà au corpus. Le couper ici
    # revient à ne pas compter deux fois les mêmes phrases : c'est la mesure qui avait écarté trois
    # volumes de Ferenczi, appliquée cette fois sans perdre le reste du volume.
    #   • « Der Dichter und das Phantasieren » clôt la Zweite Folge — recouvrement mesuré 72,1 %
    #     avec l'œuvre déjà présente. L'intitulé est relevé TEL QUE L'OCR LE LIT : « Diehter ».
    "sammlung_2": "Der Diehter und das Phantasieren",
    #   • la Dritte Folge n'a pas de doublon : sa borne ne coupe que la réclame de l'éditeur.
    "sammlung_3": "VERLAG VON FRANZ DEUTICKE",
    #   • « Das Unheimliche » clôt la Fünfte Folge — recouvrement mesuré 66,3 %.
    "sammlung_5": "DAS UNHEIMLICHE",
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
    # SIGMUND FREUD, Vierte Folge (1918) — SIX TEXTES DÉJÀ AU CORPUS, retirés en UN SEUL bloc.
    #
    # Ce n'est pas une région d'un autre auteur, c'est un DOUBLON : ce volume réimprime cinq
    # textes que le corpus tient déjà de Project Gutenberg, en transcription relue. Mesuré en
    # suites de huit mots, avec la méthode qui avait écarté trois volumes de Ferenczi :
    #     kindheitserinnerung_dichtung_wahrheit  77,3 %      charaktertypen           69,8 %
    #     schwierigkeit_psychoanalyse            74,3 %      zeitgemaesses_krieg_tod  64,4 %
    #     kaestchenwahl                          62,4 %
    # (Les taux ne montent pas à 100 % parce qu'on compare un fac-similé océrisé à une
    # transcription relue : ce sont les mêmes textes, pas les mêmes graphies.)
    #
    # Les cinq se suivent SANS INTERRUPTION dans le volume, des chapitres XXVI à XXX : une seule
    # région les emporte, ce qui évite cinq paires de bornes et cinq occasions de se tromper. Elle
    # s'arrête au chapitre XXXI, l'Homme aux loups, qui lui n'est pas au corpus et doit rester.
    #
    # Les accepter aurait compté deux fois les mêmes phrases et faussé TOUTES les densités du
    # corpus — y compris celles des autres auteurs, qui se mesurent par comparaison.
    "sammlung_4": [(
        "DAS MOTIV DER KÄSTCHENWAHL",
        "AUS DER GESCHICHTE EINER INFANTILEN NEUROSE",
        "Cinq textes des chapitres XXVI à XXX sont DÉJÀ au corpus, en transcription relue de "
        "Project Gutenberg : Das Motiv der Kästchenwahl, Zeitgemäßes über Krieg und Tod, Einige "
        "Charaktertypen, Eine Schwierigkeit der Psychoanalyse, Eine Kindheitserinnerung aus "
        "„Dichtung und Wahrheit“. Recouvrement mesuré de 62,4 % à 77,3 % en suites de huit mots. "
        "La région s'arrête au chapitre XXXI (l'Homme aux loups), absent du corpus et conservé.")],
    # SIGMUND FREUD, Fünfte Folge (1922) — l'Homme aux loups, réimprimé depuis la Vierte Folge.
    # Le volume le dit LUI-MÊME en note de sommaire : ce texte fermait la « Vierte Folge » de 1918
    # et en a été retiré à la 2e édition « mit Rücksicht auf die Handlichkeit des Bandes », puis
    # repris ici. Comme le corpus lit la 1re édition de 1918, il l'a déjà — c'est le seul doublon
    # du corpus attesté par une déclaration d'éditeur plutôt que par la seule mesure.
    # WILHELM STEKEL, « Die Sprache des Traumes » (1911) — sa table des matières, qui tombe APRÈS
    # le Vorwort et non avant. La borne de début ne peut donc pas l'écarter sans emporter aussi la
    # préface, qui est du texte d'auteur. C'est un garde-fou existant du projet qui l'a signalée
    # (`test_liminaires_editeur_retires`), et non une relecture : quarante-huit lignes de titres
    # océrisés seraient entrées comme des phrases de Stekel — « XXIL Zahnträume 221 ».
    "sprache_des_traumes": [(
        "Inhaltsverzeichnis.",
        "Die Bedentang der Symbolik.",
        "Table des matières du volume, insérée entre le Vorwort de l'auteur et le premier "
        "chapitre. Quarante-huit intitulés océrisés suivis de leur numéro de page ; la borne de "
        "fin est le titre du chapitre I tel que le scan le lit (« Die Bedentang der Symbolik »), "
        "relevé et non corrigé, sans quoi il serait introuvable.")],
    # WILHELM STEKEL, « Onanie und Homosexualität » (1917) — même cas, et pire : sa table des
    # matières n'est pas une liste de titres mais un SOMMAIRE ANALYTIQUE de huit mille signes,
    # qui résume chaque paragraphe en une phrase suivie de sa page (« Alle Menschen onanieren
    # -15-. Die Neurose eine Folge der Abstinenz, nicht der Onanie -16- »). Atomisé, il aurait
    # produit des centaines de phrases assertives ressemblant à s'y méprendre à des thèses de
    # l'auteur — et il aurait faussé toutes les densités de concepts du volume, puisqu'il en
    # reprend le vocabulaire au complet.
    "onanie_homosexualitaet": [(
        "Inhaltsangabe.",
        # Borne de fin : la citation de Nietzsche qui ouvre le premier tome, prise plutôt que le
        # faux-titre « ERSTER TEIL » — celui-ci est coupé par des sauts de ligne dans le scan et
        # la recherche exacte échouait. Le garde-fou l'a dit plutôt que de laisser la région
        # ouverte, ce qui est exactement son office.
        "Unsere höchsten Weisheiten",
        "Sommaire analytique de huit mille signes, placé entre le Vorwort et le corps. Il résume "
        "chaque paragraphe du livre en une phrase suivie de sa pagination, et emploie donc tout "
        "le vocabulaire de l'ouvrage : atomisé, il aurait doublé artificiellement la densité de "
        "chaque concept du volume. La borne de fin est le faux-titre du premier tome, en "
        "capitales, qui suit immédiatement la dernière pagination du sommaire.")],
    "sammlung_5": [(
        "Der Krankheitsfall, über welchen ich hier",
        "ZUR VORGESCHICHTE DER ANALYTISCHEN TECHNIK",
        "« Aus der Geschichte einer infantilen Neurose » (1918), l'Homme aux loups, occupe la "
        "première moitié de ce volume et se trouve DÉJÀ au corpus par la Vierte Folge de 1918, "
        "que le projet lit en première édition. Le volume déclare lui-même ce déplacement en note "
        "de son sommaire.")],
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
    # WILHELM STEKEL — écarté AVANT acquisition, pour que ces titres ne soient pas reproposés le
    # jour où il entrera. Son inventaire complet est dans documentation/STEKEL_INVENTAIRE.md.
    "autobiography0000stek": (
        "The Autobiography of Wilhelm Stekel (Liveright, New York, 1950) — ÉCARTÉE POUR RAISON "
        "LÉGALE, comme Lacan. Œuvre américaine de 1950, éditée et vraisemblablement traduite par "
        "Emil A. Gutheil (mort en 1959) : la seule couche éditoriale serait protégée jusqu'en 2029, "
        "et aucun original allemand publié n'a été retrouvé. Internet Archive la classe elle-même "
        "en accès contrôlé (« Access-restricted-item »), ce qu'elle ne fait pas quand le domaine "
        "public est établi."),
    "FortschritteDerSexualwissenschaftUndPsychoanalyse": (
        "Fortschritte der Sexualwissenschaft und Psychoanalyse (1924-1931), et de même le "
        "Zentralblatt für Psychoanalyse et la Psychotherapeutische Praxis — revues DIRIGÉES par "
        "Stekel, écartées pour la même raison de STRUCTURE que le symposium des Kriegsneurosen : "
        "une publication à plusieurs voix n'a pas d'auteur de volume, et le lexique suit l'auteur "
        "du volume. Le tome IV (1931) dépasse en outre le seuil de datation appliqué à Freud."),
}

# MOTIFS DE CHAPITRE, DÉCLARÉS ŒUVRE PAR ŒUVRE.
#
# `atomisation._CHAPITRE` exige un chiffre romain SUIVI D'UN POINT, seul sur sa ligne, puis une
# ligne vide. C'est la mise en page de « Die Traumdeutung » et de presque rien d'autre : mesuré,
# 20 œuvres sur 40 n'avaient AUCUN chapitre — 36 % du corpus, dont les cinq volumes de Ferenczi,
# qui numérote sans point et compose ses titres en capitales.
#
# La conséquence était en cascade et invisible : la LECTURE DÉCLARÉE — qu'un chapitre annonce dans
# son titre qu'il traite d'un autre auteur — ne comptait qu'UNE ligne dans toute la base, alors
# que `core/comparaison.py` la désigne comme « le lien le plus fort du corpus, et le seul qui
# traverse la barrière des langues ». Ce n'était pas un fait de corpus mais un aveuglement.
#
# ON NE CHERCHE PAS DE DÉTECTEUR UNIVERSEL : il n'y en a pas. Chaque fac-similé a sa mise en page,
# et le projet déclare déjà ses bornes œuvre par œuvre. Chaque motif ci-dessous a été relevé dans
# le texte, éprouvé contre ses faux positifs, puis REJOUÉ avant d'être inscrit — ceux qui
# reculaient par rapport au détecteur commun ont été écartés.
#
# Contrat : groupes nommés `t` (titre) et `n` (numéro) s'ils existent ; sinon un groupe unique
# vaut titre, et à partir de deux le premier vaut numéro et les suivants composent le titre.
MOTIFS_CHAPITRE = {
    # bausteine_1 : 17 sections (contre 0) — dont 2 titre(s) nommant un autre auteur :
    #   Die wissenschaftliche Bedeutung von Freuds „Drei Abhandlungen zur Sexualtheorie“
    #   Zum 70. Geburtstage Sigmund Freuds Fine Begrüßung
    'bausteine_1': '^(?:[ \\t]*(?:[|\\\\/¦][ \\t]*){0,2}\\n){2,}(?P<t>[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?(?![^\\n]*[a-zäöüß][“”’»\\"]?[.!?][ \\t“”’\\"»]*[^\\s“”’»])[A-ZÄÖÜÉ„/][A-Za-zÄÖÜäöüß](?:[^\\n]{0,98}?(?:[^\\s.,;:!?)\\]\\d—–][“”»’]?[!*¹]?|-)|[^\\n]{0,90}\\([^\\n]{1,40}[A-Za-zÄÖÜäöü]\\))[ \\t]*\\.?[ \\t]*\\n(?:[ \\t]*(?:[|\\\\/¦][ \\t]*){0,2}\\n){0,6}(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?(?![^\\n]*[a-zäöüß][“”’»\\"]?[.!?][ \\t“”’\\"»]*[^\\s“”’»])[A-Za-zÄÖÜäöü„][A-Za-zÄÖÜäöüß](?:[^\\n]{0,98}?(?:[^\\s.,;:!?)\\]\\d—–][“”»’]?[!*¹]?|-)|[^\\n]{0,90}\\([^\\n]{1,40}[A-Za-zÄÖÜäöü]\\))[ \\t]*\\.?[ \\t]*\\n(?:[ \\t]*(?:[|\\\\/¦][ \\t]*){0,2}\\n){0,6}){0,3})(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?\\((?P<s>[^()\\n]{3,140})\\)[ \\t]*\\n(?:[ \\t]*\\n)*)?(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?\\((?P<n>[^()\\n]{3,140})\\)[ \\t]*\\.?[ \\t]*\\n|(?=[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?\\(?(?:Vortrag|Festvortrag|Vorgetragen|Nach einem|Gehalten|Diese Zeilen|Mit diesem|Aus Anla|Antwort auf|Erschienen)[^\\n]{0,130}[^.\\s][ \\t]*\\n))',
    # bausteine_2 : 36 sections (contre 0) — dont 1 titre(s) nommant un autre auteur :
    #   Zur Kritik der Rankschen „Technik der   Psychoanalyse”
    'bausteine_2': '^(?:[ \\t]*(?:[|\\\\/¦][ \\t]*){0,2}\\n){2,}(?P<t>[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?(?![^\\n]*[a-zäöüß][“”’»\\"]?[.!?][ \\t“”’\\"»]*[^\\s“”’»])[A-ZÄÖÜÉ„/][A-Za-zÄÖÜäöüß](?:[^\\n]{0,98}?(?:[^\\s.,;:!?)\\]\\d—–][“”»’]?[!*¹]?|-)|[^\\n]{0,90}\\([^\\n]{1,40}[A-Za-zÄÖÜäöü]\\))[ \\t]*\\.?[ \\t]*\\n(?:[ \\t]*(?:[|\\\\/¦][ \\t]*){0,2}\\n){0,6}(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?(?![^\\n]*[a-zäöüß][“”’»\\"]?[.!?][ \\t“”’\\"»]*[^\\s“”’»])[A-Za-zÄÖÜäöü„][A-Za-zÄÖÜäöüß](?:[^\\n]{0,98}?(?:[^\\s.,;:!?)\\]\\d—–][“”»’]?[!*¹]?|-)|[^\\n]{0,90}\\([^\\n]{1,40}[A-Za-zÄÖÜäöü]\\))[ \\t]*\\.?[ \\t]*\\n(?:[ \\t]*(?:[|\\\\/¦][ \\t]*){0,2}\\n){0,6}){0,3})(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?\\((?P<s>[^()\\n]{3,140})\\)[ \\t]*\\n(?:[ \\t]*\\n)*)?(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?\\((?P<n>[^()\\n]{3,140})\\)[ \\t]*\\.?[ \\t]*\\n|(?=[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?:[iı][ \\t]+)?\\(?(?:Vortrag|Festvortrag|Vorgetragen|Nach einem|Gehalten|Diese Zeilen|Mit diesem|Aus Anla|Antwort auf|Erschienen)[^\\n]{0,130}[^.\\s][ \\t]*\\n))',
    # bausteine_3 : 51 sections (contre 0) — dont 2 titre(s) nommant un autre auteur :
    #   Die Bedeutung Freuds für die Mental Hygiene-Bewegung Aus Anlass de la Vollendung… (1926)
    #   Freuds Einfluss auf die Medizin (1933)
    #
    # LE VOLUME LE PLUS GROS ET LE PLUS MAL SCANNÉ (3 627 atomes, aucun chapitre jusqu'ici). Deux
    # terminaisons, toutes deux RELEVÉES dans le volume, parce que sa mise en page change en route :
    #   • les pièces anciennes portent leur année seule sur une ligne, sous le titre — « (1908) »,
    #     « (etwa 1909) ». C'est la table des matières du volume qui donne la vérité de terrain
    #     (« Originalarbeiten aus den Jahren 1908—1933 ») ;
    #   • les pièces tardives (1926-1933) n'ont plus d'année mais la mention de la séance où elles
    #     furent lues. Le mot commun à TOUTES ces mentions est « gehalten » (ou « Vorgetragen am »).
    #     Le seul mot « Vortrag » ne suffisait pas : il revient au fil des phrases (« meines
    #     Vortrages den Eindruck… »), et faisait entrer deux amorces de corps de texte comme titres.
    #
    # Ce qui écarte les TÊTES COURANTES sans avoir à les nommer : aucune n'est suivie d'une ligne
    # d'année ni d'une mention de séance. Le signal de mise en page seul (lignes vides + ligne
    # courte) en ramassait vingt-six, dont « Die Bedeutung Freuds… 303 » trois fois — et un motif
    # déclaré contourne le filtre de ponctuation de `comparaison._INTITULE_COMPLET`, donc chaque
    # tête courante retenue aurait fabriqué une fausse lecture déclarée.
    'bausteine_3': '(?:^[ \\t]*\\n){2,}(?:[ \\t]*[^\\n]{1,8}[ \\t]*\\n(?:[ \\t]*\\n)+)?[ \\t]*(?P<t>(?=[^\\n]*[A-Za-zÄÖÜäöüß]{3})(?![^\\n]*\\bS\\.[ \\t]*\\d)[A-ZÄÖÜ„][^\\n]{2,58}?(?:[ \\t]*\\n[ \\t]*(?=[^\\n]*[A-Za-zÄÖÜäöüß]{2})[^\\n\\d\\s][^\\n]{1,58}?){0,3}(?:(?:[ \\t]*\\n){2,3}[ \\t]*(?=[^\\n]*[A-Za-zÄÖÜäöüß]{2})[^\\n\\d\\s][^\\n]{1,58}?)?)[ \\t]*\\n(?:[ \\t]*\\n)*(?:[ \\t]*[^\\n]{1,8}[ \\t]*\\n(?:[ \\t]*\\n)+)?[ \\t]*(?:\\((?P<n>(?:etwa[ \\t]*)?1[89]\\d\\d(?:[ \\t]*[—–-]+[ \\t]*\\d{2,4})?)\\)[^\\n]{0,12}|(?:[^\\n]*\\bgehalten|Vorgetragen[ \\t]+am)[^\\n]*)[ \\t]*$',
    # charakterbildung : 3 sections (contre 0) — les trois études du volume, aucune de plus.
    # La branche `\\A` est là pour la PREMIÈRE étude : son chiffre romain occupe une ligne d'un seul
    # signe, que le retrait des blocs illisibles du fac-similé emporte avec le bruit de scan. Sans
    # elle, une étude sur trois restait sans titre — c'est le défaut qui avait fait écarter ce motif
    # au premier passage, et il ne venait pas du motif mais de la borne `debut_corps`, qui tombait
    # APRÈS le titre de la première étude (voir son commentaire dans le registre).
    'charakterbildung': '(?:(?:^[ \\t]*\\n){2,}[ \\t]*(?P<n>[IVX]{1,3})[ \\t]*\\n(?:[ \\t]*\\n)*|\\A)[ \\t]*(?P<t>(?=[^\\n]*[A-Za-zÄÖÜäöüß]{3})[A-ZÄÖÜ„][^\\n]{4,64}?(?:[ \\t]*\\n[ \\t]*(?=[^\\n]*[A-Za-zÄÖÜäöüß]{3})[^\\n\\d\\s][^\\n]{2,64}?)?)[\'’!*]{0,2}[ \\t]*\\n(?:[ \\t]*\\n){2,}',
    # der_kuenstler : 2 sections (contre 0)
    'der_kuenstler': '\\n[ \\t]*\\n[ \\t]*([A-ZÄÖÜ][A-Za-zÄÖÜäöüß]{2,20}(?:[ \\t]+[A-Za-zÄÖÜäöüß]{2,20}){1,4})\\.[ \\t]*\\n[ \\t]*\\n',
    # entwicklungsgeschichte_libido : 5 sections (contre 0)
    'entwicklungsgeschichte_libido': '(?:^[ \\t]*\\n){2}[ \\t]*([IVXL]{1,6})[ \\t]*\\n(?:[ \\t]*\\n)*[ \\t]*([A-ZÄÖÜ][^\\n]{4,70})[ \\t]*\\n(?:(?:[ \\t]*\\n){0,2}[ \\t]*((?=[^\\n]*[A-Za-zÄÖÜäöüß]{3})[^\\n\\W\\d][^\\n]{2,70})[ \\t]*\\n)?[ \\t]*\\n',
    # genetische_psychologie_2 : 6 sections (contre 0)
    'genetische_psychologie_2': '\\n[ \\t]*\\n[ \\t]*([A-ZÄÖÜ][a-zäöüß]{3,20}(?:[ \\t]+[a-zäöüßA-ZÄÖÜ][a-zäöüßA-ZÄÖÜ]{1,20}){1,3})(?:\\.[ \\t]*\\n[ \\t]*\\n|[ \\t]*\\n(?:[ \\t]*\\n)+[ \\t]*[„\\"“])',
    # genitaltheorie : 10 sections (contre 0)
    'genitaltheorie': '^[ \\t]*\\n(?:[ \\t]*\\n)*[ \\t]*(?P<n>[IVXilvun]{1,5})\\.?[ \\t]*\\n(?:[ \\t]*\\n)*[ \\t]*(?:[|\\\\/¦][ \\t]*)?(?P<t>[A-ZÄÖÜ][A-ZÄÖÜẞ \\t.’-]{8,70}[ \\t]*\\n(?:[ \\t]*(?:[|\\\\/¦][ \\t]*)?[A-ZÄÖÜ„“”][A-ZÄÖÜẞ„“” \\t.:’-]{2,70}[ \\t]*\\n)?)',
    # inzest_motiv : 23 sections (contre 7)
    'inzest_motiv': '\\n[ \\t]*\\n[ \\t]*((?=[^\\n]*[IVXLHYNivxlhyn])[IVXLHYNivxlhyn]{1,6})\\.?[ \\t]*\\n(?:[ \\t]*\\n)*[ \\t]*((?=[^\\n]*[a-zäöüß]{3})[A-ZÄÖÜ][^\\n:]{4,85})[ \\t]*\\n',
    # klinische_beitraege : 28 sections (contre 6) — dont 1 titre(s) nommant un autre auteur :
    #   Bemerkungen zu Ferenczis Mitteilung über „Sonntagsneurosen“'.
    'klinische_beitraege': '(?:^[ \\t]*\\n){7,}(?:[ \\t]*[^\\W\\d]{1,3}[ \\t]*\\n(?:[ \\t]*\\n)+)?([A-ZÄÖÜ][^\\n]{6,52}?(?:(?:[ \\t]*\\n){1,3}[ \\t]*(?:[^\\W\\d\\n]|[„«»“\\"])[^\\n]{2,52}?){1,3}|[A-ZÄÖÜ][^\\n]{6,92}?)[.?,][^\\w\\n]{0,4}\\n[ \\t]*\\n',
    # lohengrinsage : 7 sections (contre 4)
    'lohengrinsage': '\\n[ \\t]*\\n[ \\t]*([IVXLUilvxu|]{1,5})\\.?[ \\t]*\\n(?:[ \\t]*\\n)*[ \\t]*(?:(?=[^\\n]{40,})[A-ZÄÖÜ]|([A-ZÄÖÜ][^\\n]{4,60})\\.[ \\t]*\\n[ \\t]*\\n)',
    # mythus_geburt_helden : 12 sections (contre 0)
    'mythus_geburt_helden': '\\n[ \\t]*\\n[ \\t]*[^\\w\\n]{0,3}[ \\t]*([A-ZÄÖÜ][a-zäöüß]{2,15})\\.[^\\w\\n]{0,4}[ \\t]*\\n(?:[ \\t]*\\n)*[ \\t]*(?=[^\\n]{40,})[^\\n]*[a-zäöüß]',
    # neue_folge : 7 sections (contre 0)
    'neue_folge': '(?m)^[ \\t]*([^\\na-zäöüß]{4,80}?)[ \\t]*\\n[ \\t]*\\n[ \\t]*([IVXLC]{2,8})\\.[ \\t]*VORLESUNG\\.?[ \\t]*$',
    # populaere_vortraege : 17 sections (contre 0) — dont 2 titre(s) nommant un autre auteur :
    #   Über Aktual- und Psychoneurosen im Lichte der Freudschen Forschungen und über die Psycho
    #   Die wissenschaftliche Bedeutung von Freuds „Drei Abhandlungen zur Sexualtheorie“ *
    'populaere_vortraege': '^(?:[ \\t]*\\n){2,}(?P<t>[ \\t]*(?=[^\\n]*[a-zäöüß]{3})(?![^\\n]*[a-zäöüß][“”’»\\"]?[.!?][ \\t“”’\\"»]*[^\\s“”’»])(?![^\\n]*[—–])[A-ZÄÖÜ„][^\\n]{4,84}?[^\\s.,;:!?)\\d—–-][“”»*®’]{0,3}[ \\t]*\\n(?:[ \\t]*(?![^\\n]*[a-zäöüß][“”’»\\"]?[.!?][ \\t“”’\\"»]*[^\\s“”’»])(?![^\\n]*[—–])[^\\s\\d([][^\\n]{2,84}?[^\\s.,;:!?)\\d—–-][“”»*®’]{0,3}[ \\t]*\\n){0,2})(?:[ \\t]*\\n){2,}',
    # segantini : 4 sections (contre 3)
    'segantini': '(?:^[ \\t]*\\n){2}[ \\t]*(AV|[IVXL]{1,6})\\.[ \\t]*\\n[ \\t]*\\n',
    # traum_und_mythus : 12 sections (contre 1)
    'traum_und_mythus': '(?:^[ \\t]*\\n){2}[ \\t]*(Vill|[IVXL]{1,6})\\.[ \\t]+(\\S[^\\n]{3,110})[ \\t]*\\n(?:[ \\t]*([A-ZÄÖÜa-zäöüß][^\\n]{2,90})[ \\t]*\\n)?[ \\t]*\\n(?=(?:[ \\t]*\\n)*[ \\t]*[^\\n]{45,})',
    # trauma_der_geburt : 11 sections (contre 0)
    'trauma_der_geburt': '\\n[ \\t]*\\n[ \\t]*([A-ZÄÖÜ][a-zäöüß]{2,12}[ \\t]+[a-zäöüßA-ZÄÖÜ]{4,20}[ \\t]+[A-ZÄÖÜ][a-zäöüß]{4,20})[^\\w\\n]{0,3}[ \\t]*\\n[ \\t]*\\n',
    # witz : 10 sections (contre 0)
    'witz': '(?m)(?<=\\n\\n\\n\\n)^[ \\t]*([A-C]|[IVXLC]{1,6})\\.[ \\t]+(\\S[^\\n]{2,88}?)[ \\t]*$(?=\\n\\n\\n)',
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

    # ------------------------------------------------------- ONZE ŒUVRES ENTRÉES LE 2026-07-30
    # UNE CONCLUSION PÉRIMÉE, RENVERSÉE PAR LA MESURE. Le § 5 de documentation/SYNTHESE_FREUD.md
    # déclarait treize œuvres majeures « hors d'atteinte en qualité citable, vérifié par recherche
    # systématique ». La recherche était bonne, mais elle ne portait que sur gutenberg.org et
    # Wikisource DE — à une époque où le projet n'acceptait aucun fac-similé océrisé. Il en accepte
    # seize depuis (tout Rank, tout Abraham, tout Ferenczi), avec un seuil de qualité mesuré. La
    # conclusion tenait donc à une contrainte qui n'existait plus, et personne ne l'avait rejouée.
    #
    # CE QUE LE CORPUS RÉCLAMAIT LUI-MÊME, mesuré : 27 atomes des œuvres muettes citent nommément
    # un titre freudien ABSENT, contre 63 citant un titre présent — le corpus était incomplet aux
    # deux tiers sur ce que ses propres auteurs citent (voir documentation/COUVERTURE_MESUREE.md).
    #
    # Qualité mesurée par ocr.corruption(), seuil à 2,0 % de phrases atteintes : ces onze sont
    # entre 0,0 et 0,1 %, c'est-à-dire au niveau des transcriptions relues. Une douzième candidate
    # a été écartée par ce seuil — voir « Die Zukunft einer Illusion » dans FAC_SIMILES_ECARTES.
    "vorlesungen_1": {
        "fichier": "1916_vorlesungen_1.ia.txt",
        "provenance": "archive",
        "titre": "Vorlesungen zur Einführung in die Psychoanalyse. Erster Teil: Die Fehlleistungen",
        "titre_fr": "Conférences d'introduction à la psychanalyse. Première partie : les actes manqués",
        "annee_oeuvre": 1916,
        "annee_edition": 1916,     # 1re édition, datation EXACTE
        "edition": "1. Auflage, Erster Teil (Vorlesung I–IV)",
        "editeur": "Hugo Heller & Cie., Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/freud-1916-vorlesungen_a",
        # LA 1re ÉDITION PARUT EN TROIS VOLUMES, en 1916, 1916 et 1917 : on les prend tels quels
        # plutôt que la refonte en un volume de 1918, pourtant elle aussi disponible et propre.
        # La raison est la DATATION — trois volumes datés séparément donnent trois fenêtres
        # exactes là où le volume unique n'en donnerait qu'une, plus large d'un à deux ans. C'est
        # la règle que le projet applique déjà partout : l'édition la plus ancienne l'emporte.
        "debut_corps": "Ich weiß nicht, wieviel die einzelnen von Ihnen",
    },
    "vorlesungen_2": {
        "fichier": "1916_vorlesungen_2.ia.txt",
        "provenance": "archive",
        "titre": "Vorlesungen zur Einführung in die Psychoanalyse. Zweiter Teil: Der Traum",
        "titre_fr": "Conférences d'introduction à la psychanalyse. Deuxième partie : le rêve",
        "annee_oeuvre": 1916,
        "annee_edition": 1916,
        "edition": "1. Auflage, Zweiter Teil (Vorlesung V–XV)",
        "editeur": "Hugo Heller & Cie., Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/freud1916vorlesungen_traum",
        "debut_corps": "Eines Tages machte man die Entdeckung",
    },
    "vorlesungen_3": {
        "fichier": "1917_vorlesungen_3.ia.txt",
        "provenance": "archive",
        "titre": "Vorlesungen zur Einführung in die Psychoanalyse. Dritter Teil: Allgemeine Neurosenlehre",
        "titre_fr": "Conférences d'introduction à la psychanalyse. Troisième partie : théorie générale des névroses",
        "annee_oeuvre": 1917,
        "annee_edition": 1917,
        "edition": "1. Auflage, Dritter Teil (Vorlesung XVI–XXVIII)",
        "editeur": "Hugo Heller & Cie., Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/freud-1917-vorlesungen-c-neurosen",
        # Ce tome porte la préface de Freud à l'ensemble des trois : elle est GARDÉE, c'est du texte
        # d'auteur, et elle date elle-même les deux semestres de cours (1915/6 et 1916/7).
        "debut_corps": "Was ich hier als „Einführung in die Psychoanalyse“",
    },
    "ich_und_es": {
        "fichier": "1923_ich_und_es.ia.txt",
        "provenance": "archive",
        "titre": "Das Ich und das Es",
        "titre_fr": "Le Moi et le Ça",
        "annee_oeuvre": 1923,
        "annee_edition": 1923,
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/Freud_1923_Das_Ich_und_das_Es_k",
        # L'ABSENCE QUI PESAIT LE PLUS. La chronologie des concepts du corpus (voir § 3 de
        # SYNTHESE_FREUD.md) mesurait l'apparition de la seconde topique sans disposer du texte
        # qui la pose.
        "debut_corps": "Die Unterscheidung des Psychischen in Bewußtes und Unbewußtes",
    },
    "hemmung_symptom_angst": {
        "fichier": "1926_hemmung_symptom_angst.ia.txt",
        "provenance": "archive",
        "titre": "Hemmung, Symptom und Angst",
        "titre_fr": "Inhibition, symptôme et angoisse",
        "annee_oeuvre": 1926,
        "annee_edition": 1926,
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/Freud_1926_Hemmung_Symptom_und_Angst_k",
        "debut_corps": "Unser Sprachgebrauch läßt uns in der Beschreibung pathologischer",
    },
    "unbehagen_kultur": {
        "fichier": "1930_unbehagen_kultur.ia.txt",
        "provenance": "archive",
        "titre": "Das Unbehagen in der Kultur",
        "titre_fr": "Le Malaise dans la civilisation",
        "annee_oeuvre": 1930,
        "annee_edition": 1930,
        "edition": "1. Auflage (1.–12. Tausend)",
        "editeur": "Internationaler Psychoanalytischer Verlag, Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/DasUnbehagenInDerKultur",
        # L'ŒUVRE LA PLUS TARDIVE DU CORPUS, et elle passe de justesse : le projet applique à
        # Freud le seuil américain de 1931 (voir LICENCE). Une réimpression de 1931 aurait été
        # écartée pour cette seule raison, à texte identique.
        "debut_corps": "Man kann sich des Eindrucks nicht erwehren",
    },
    "sammlung_1": {
        "fichier": "1906_sammlung_1.ia.txt",
        "provenance": "archive",
        "titre": "Sammlung kleiner Schriften zur Neurosenlehre aus den Jahren 1893–1906",
        "titre_fr": "Recueil de petits écrits sur la théorie des névroses, 1893-1906",
        "annee_oeuvre": 1893,      # le volume déclare sa fenêtre dans son propre titre
        "annee_edition": 1906,
        "edition": "1. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/sksn1",
        "debut_corps": "Mit J. M. Charcot, den nach einem glücklichen",
    },
    "sammlung_2": {
        "fichier": "1909_sammlung_2.ia.txt",
        "provenance": "archive",
        "titre": "Sammlung kleiner Schriften zur Neurosenlehre. Zweite Folge",
        "titre_fr": "Recueil de petits écrits sur la théorie des névroses, deuxième série",
        "annee_oeuvre": 1905,
        "annee_edition": 1909,
        "edition": "1. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/sksn2",
        # Il ouvre sur le cas Dora, dont c'est ici la première reprise en volume.
        "debut_corps": "Es war sicherlich mißlich, daß ich Forschungsergebnisse",
    },
    "sammlung_3": {
        "fichier": "1913_sammlung_3.ia.txt",
        "provenance": "archive",
        "titre": "Sammlung kleiner Schriften zur Neurosenlehre. Dritte Folge",
        "titre_fr": "Recueil de petits écrits sur la théorie des névroses, troisième série",
        "annee_oeuvre": 1909,
        "annee_edition": 1913,
        "edition": "1. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/sksn3",
        # LE VOLUME LE PLUS RENTABLE DE LA SÉRIE, et le seul qui n'ait AUCUN recouvrement avec le
        # corpus : il porte trois des cinq grands cas cliniques — le petit Hans, l'Homme aux rats
        # et Schreber. Les deux premiers sont cités nommément par des œuvres muettes du corpus.
        "debut_corps": "Die auf den folgenden Blättern darzustellende",
    },
    "sammlung_4": {
        "fichier": "1918_sammlung_4.ia.txt",
        "provenance": "archive",
        "titre": "Sammlung kleiner Schriften zur Neurosenlehre. Vierte Folge",
        "titre_fr": "Recueil de petits écrits sur la théorie des névroses, quatrième série",
        "annee_oeuvre": 1913,
        "annee_edition": 1918,
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/sksn4",
        # LE VOLUME QUE LE CORPUS RÉCLAMAIT LE PLUS FORT : il porte « Zur Einführung des
        # Narzissmus » (1914) et « Trauer und Melancholie » (1917), tous deux cités nommément et
        # absents — Abraham écrit « Als im Jahre 1916 Freuds oft zitierter Aufsatz über „Trauer
        # und Melancholie“ erschien… » —, plus les trois écrits métapsychologiques de 1915 et
        # l'Homme aux loups. Il réimprime aussi CINQ textes déjà au corpus, retirés en région
        # écartée (voir REGIONS_ECARTEES) : les compter deux fois fausserait toutes les densités.
        "debut_corps": "Wenn ich im Nachstehenden Beiträge zur Geschichte",
    },
    "sammlung_5": {
        "fichier": "1922_sammlung_5.ia.txt",
        "provenance": "archive",
        "titre": "Sammlung kleiner Schriften zur Neurosenlehre. Fünfte Folge",
        "titre_fr": "Recueil de petits écrits sur la théorie des névroses, cinquième série",
        "annee_oeuvre": 1918,
        "annee_edition": 1922,
        "edition": "1. Auflage",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Internet Archive — fac-similé OCRisé, NON relu",
        "url": "https://archive.org/details/sksn5",
        # DEUX RÉGIONS ÉCARTÉES, et la première l'est sur la foi du volume LUI-MÊME : sa note de
        # sommaire explique que l'Homme aux loups, qui fermait la « Vierte Folge » de 1918, en a
        # été retiré à la 2e édition « mit Rücksicht auf die Handlichkeit des Bandes » et repris
        # ici. Comme le corpus lit la 1re édition de 1918, ce texte y est déjà. La seconde région
        # est « Das Unheimliche », que le corpus tient de Gutenberg, relu.
        #
        # « Das Unheimliche » FERME le volume : la borne de paratexte final suffit pour lui.
        # L'Homme aux loups, lui, occupe la PREMIÈRE MOITIÉ — et c'est le garde-fou qui l'a dit :
        # une borne de début posée à 51 % du volume est refusée d'office (le seuil est à 30 %),
        # parce qu'une borne aussi tardive est presque toujours une erreur de relevé. Ici elle ne
        # l'était pas, mais la règle a raison de ne pas en juger : ce doublon-là est une RÉGION,
        # et il est déclaré comme tel dans REGIONS_ECARTEES.
        "debut_corps": "Der Krankheitsfall, über welchen ich hier",
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
        # LA BORNE TOMBAIT APRÈS LE TITRE DE LA PREMIÈRE ÉTUDE. Elle visait la première phrase du
        # corps (« Das weite Gebiet, welches heute der psychoanalytischen ») et laissait donc dehors
        # « I / Ergänzungen zur Lehre vom Analcharakter » — une étude sur trois entrait au corpus
        # sans titre, et le chapitrage de ce volume avait été écarté pour cette raison, qui ne
        # venait pas de son motif. La borne porte maintenant le titre lui-même. Elle inclut le
        # chiffre romain et l'appel de note (« Analcharakter' ») pour rester UNIQUE : le titre nu
        # revient seize fois dans le volume, en tête courante de page.
        "debut_corps": "I \nErgänzungen zur Lehre vom Analcharakter'",
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
    # (Les licences propres aux autres auteurs sont posées plus bas, à `charger` : voir LICENCES.)
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

    # ------------------------------------------------------------------ WILHELM STEKEL
    # CINQUI\u00c8ME AUTEUR trait\u00e9 pour lui-m\u00eame (2026-07-31), et la QUATRI\u00c8ME forme du rapport au
    # ma\u00eetre \u2014 celle qui manquait. Rank d\u00e9place une th\u00e8se et rompt ; Abraham prolonge et ne rompt
    # jamais ; Ferenczi reste vingt ans le plus proche et diverge sur la technique. Stekel, lui,
    # rompt LE PREMIER et sur la doctrine : cofondateur avec Freud de la Soci\u00e9t\u00e9 psychologique du
    # mercredi en 1902, il quitte la Soci\u00e9t\u00e9 en 1912 sur les n\u00e9vroses actuelles et l'onanisme.
    #
    # CE QUI L'A FAIT ENTRER N'EST PAS UNE INTUITION D'HISTOIRE MAIS UNE MESURE : 54 atomes du
    # corpus le nommaient d\u00e9j\u00e0 \u2014 22 de Freud dont 16 dans la seule Traumdeutung, 15 de Rank, 10
    # d'Abraham, 7 de Ferenczi \u2014 sans qu'on puisse montrer l'autre c\u00f4t\u00e9. L'inventaire complet est
    # dans documentation/STEKEL_INVENTAIRE.md.
    #
    # D'O\u00d9 L'ORDRE D'ACQUISITION, QUI N'EST PAS CHRONOLOGIQUE : \u00ab Die Sprache des Traumes \u00bb vient
    # en t\u00eate parce que c'est le volume que le corpus nomme le plus. Freud y salue \u00ab la plus riche
    # collection de r\u00e9solutions symboliques \u00bb tout en refusant sa g\u00e9n\u00e9ralisation ; le corpus ne
    # tenait qu'un c\u00f4t\u00e9 de cette controverse.
    #
    # Qualit\u00e9 mesur\u00e9e par ocr.corruption(), seuil \u00e0 2,0 % de phrases atteintes : les six volumes
    # sont entre 0,0 et 0,2 %. Aucune transcription relue n'existe pour Stekel \u2014 ni Wikisource, ni
    # Gutenberg allemand, ni le Deutsches Textarchiv : c'est fac-simil\u00e9 oc\u00e9ris\u00e9 ou rien, comme
    # pour Rank, Abraham et Ferenczi.
    "ursachen_nervositaet": {
        "fichier": "1907_ursachen_nervositaet.ia.txt",
        "dossier": ("stekel", "de"),
        "provenance": "archive",
        "auteur": "Wilhelm Stekel",
        "titre": "Die Ursachen der Nervosit\u00e4t. Neue Ansichten \u00fcber deren Entstehung und Verh\u00fctung",
        "titre_fr": "Les causes de la nervosit\u00e9",
        "annee_oeuvre": 1907,
        "annee_edition": 1907,     # 1re \u00e9dition \u2014 datation exacte
        "edition": "1. Auflage (Hygienische Zeitfragen, Heft 1)",
        "editeur": "Paul Knepler, Wien",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/stekel-1907-ursachen",
        # SON PREMIER LIVRE, et il ouvre sur une d\u00e9claration d'all\u00e9geance qui date la relation
        # avant la rupture : \u00ab Und derjenige, der mir diesen Weg gezeigt hat \u2026 ist der gro\u00dfe
        # Seelenkenner Professor Sigmund Freud. Ich bekenne mich stolz als seinen Sch\u00fcler, womit
        # ich nicht sagen will, da\u00df Alles, was ich ausf\u00fchre, seinen Anschauungen entspricht. \u00bb
        # La r\u00e9serve est d\u00e9j\u00e0 l\u00e0, cinq ans avant la rupture \u2014 c'est le genre de fait que ce
        # corpus existe pour rendre localisable.
        "debut_corps": "Es wird heutzutage so viel \u00fcber",
    },
    "nervoese_angstzustaende": {
        "fichier": "1908_nervoese_angstzustaende.ia.txt",
        "dossier": ("stekel", "de"),
        "provenance": "archive",
        "auteur": "Wilhelm Stekel",
        "titre": "Nerv\u00f6se Angstzust\u00e4nde und ihre Behandlung",
        "titre_fr": "Les \u00e9tats d'angoisse nerveux et leur traitement",
        "annee_oeuvre": 1908,
        "annee_edition": 1908,
        "edition": "1. Auflage",
        "editeur": "Urban & Schwarzenberg, Berlin/Wien",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/b21941774",
        # CE VOLUME PORTE UNE PR\u00c9FACE DE FREUD, sign\u00e9e \u00ab Wien, im M\u00e4rz 1908. Prof. Freud. \u00bb et
        # retir\u00e9e \u00e0 la 3e \u00e9dition de 1921. C'est un texte de Freud ABSENT du corpus freudien, et
        # il entre ici par la porte de Stekel \u2014 d\u00e9clar\u00e9 en `contributions`, donc attribu\u00e9 \u00e0 son
        # auteur r\u00e9el. Sans cette d\u00e9claration, le corpus aurait pr\u00eat\u00e9 \u00e0 Stekel une page o\u00f9 Freud
        # \u00e9crit \u00ab Herr Dr. W. Stekel, einer der ersten Kollegen, die ich in die Kenntnis der
        # Psychoanalyse einf\u00fchren konnte \u00bb \u2014 c'est-\u00e0-dire o\u00f9 il parle de lui \u00e0 la troisi\u00e8me
        # personne. C'est exactement le d\u00e9faut qui avait \u00e9t\u00e9 d\u00e9cel\u00e9 dans la Traumdeutung, o\u00f9
        # l'appendice de Rank parlait de \u00ab der Freudschen Auffassung \u00bb.
        #
        # La page vaut d'\u00eatre lue pour elle-m\u00eame : Freud y prend ses distances autant qu'il
        # patronne \u2014 \u00ab mein direkter Einflu\u00df auf das vorliegende Buch \u2026 sei ein sehr geringer
        # gewesen \u00bb, \u00ab nur die Bezeichnung \u201eAngsthysterie" geht auf meinen Vorschlag zur\u00fcck \u00bb.
        # Quatre ans avant la rupture, la r\u00e9serve est d\u00e9j\u00e0 \u00e9crite, des deux c\u00f4t\u00e9s (voir aussi
        # \u00ab ursachen_nervositaet \u00bb, o\u00f9 Stekel \u00e9crit la sienne).
        "debut_corps": "Meine seit dem Jahre 1893 fortgesetzten Untersuchungen",
        "contributions": [{
            "auteur": "Sigmund Freud",
            "debut": "Meine seit dem Jahre 1893 fortgesetzten Untersuchungen",
            # Borne de fin relev\u00e9e TELLE QUE L'OCR LA LIT \u2014 \u00ab Inhaltsverzeichnis \u00bb y devient
            # \u00ab IiilialtsYerzeichnis \u00bb. La corriger la rendrait introuvable.
            "fin": "IiilialtsYerzeichnis",
        }],
    },
    "dichtung_und_neurose": {
        "fichier": "1909_dichtung_und_neurose.ia.txt",
        "dossier": ("stekel", "de"),
        "provenance": "archive",
        "auteur": "Wilhelm Stekel",
        "titre": "Dichtung und Neurose. Bausteine zur Psychologie des K\u00fcnstlers und des Kunstwerkes",
        "titre_fr": "Po\u00e9sie et n\u00e9vrose",
        "annee_oeuvre": 1909,
        "annee_edition": 1909,
        "edition": "1. Auflage (Grenzfragen des Nerven- und Seelenlebens, Heft 68)",
        "editeur": "J. F. Bergmann, Wiesbaden",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu",
        "url": "https://archive.org/details/DichtungUndNeurose.BausteineZurPsychologieDesKnstlersUndDes",
        # Le volume s'ouvre sur quatre pages de R\u00c9CLAME D'\u00c9DITEUR \u2014 recensions d'autres titres de
        # la collection, sign\u00e9es d'autres auteurs. La borne les laisse dehors : atomis\u00e9es, elles
        # auraient pr\u00eat\u00e9 \u00e0 Stekel des phrases de Kreuser et de K\u00f6tscher.
        "debut_corps": "Die nachfolgenden, stellenweise aphoristischen Ausf\u00fchrungen",
    },
    "sprache_des_traumes": {
        "fichier": "1911_sprache_des_traumes.ia.txt",
        "dossier": ("stekel", "de"),
        "provenance": "archive",
        "auteur": "Wilhelm Stekel",
        "titre": "Die Sprache des Traumes",
        "titre_fr": "Le langage du r\u00eave",
        "annee_oeuvre": 1911,
        "annee_edition": 1911,
        "edition": "1. Auflage",
        "editeur": "J. F. Bergmann, Wiesbaden",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu (scan Google)",
        "url": "https://archive.org/details/diesprachedestr00stekgoog",
        # LE VOLUME QUE LE CORPUS R\u00c9CLAMAIT LE PLUS FORT : seize atomes de la seule \u00ab Traumdeutung \u00bb
        # le discutent. Freud y salue \u00ab die reichste Sammlung von Symbolaufl\u00f6sungen \u00bb et refuse
        # dans le m\u00eame mouvement d'en g\u00e9n\u00e9raliser le principe \u2014 \u00ab der allgemeine Satz Stekels vor
        # der Anerkennung einer gr\u00f6\u00dferen Mannigfaltigkeit zur\u00fcckzutreten hat \u00bb. Le corpus tenait
        # la critique sans la th\u00e8se critiqu\u00e9e.
        #
        # Le scan porte en t\u00eate plusieurs pages d'avertissement Google EN ANGLAIS : la borne les
        # laisse dehors, sans quoi le corpus attribuerait \u00e0 Stekel de la prose juridique anglaise.
        "debut_corps": "Alles seelische Geschehen wird von dem Gesetze",
    },
    "traeume_der_dichter": {
        "fichier": "1912_traeume_der_dichter.ia.txt",
        "dossier": ("stekel", "de"),
        "provenance": "archive",
        "auteur": "Wilhelm Stekel",
        "titre": "Die Tr\u00e4ume der Dichter",
        "titre_fr": "Les r\u00eaves des po\u00e8tes",
        "annee_oeuvre": 1912,
        "annee_edition": 1912,
        "edition": "1. Auflage",
        "editeur": "J. F. Bergmann, Wiesbaden",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu (scan Google)",
        "url": "https://archive.org/details/bub_gb_4xM1AQAAMAAJ",
        # L'ANN\u00c9E DE LA RUPTURE. Le volume est en outre une pi\u00e8ce singuli\u00e8re du corpus : une
        # ENQU\u00caTE, o\u00f9 Stekel interroge une quarantaine d'\u00e9crivains vivants sur leurs r\u00eaves
        # (Hauptmann, Strindberg, Rosegger, Karl May\u2026). Une part du texte est donc de leur main,
        # cit\u00e9e par lui \u2014 la table des mati\u00e8res le dit. Le lexique suit l'auteur du volume, et
        # cette part-l\u00e0 n'est pas s\u00e9par\u00e9e : r\u00e9serve port\u00e9e dans les m\u00e9tadonn\u00e9es ci-dessous.
        "debut_corps": "In N\u00fcrnberg auf der alten Burg wird ein tiefer Brunnen",
        "reserve_attribution":
            "Ce volume est une ENQU\u00caTE : Stekel y reproduit les r\u00e9ponses d'une quarantaine "
            "d'\u00e9crivains vivants sur leurs propres r\u00eaves. Ces passages sont de leur main, cit\u00e9s "
            "par lui, et ne sont PAS s\u00e9par\u00e9s dans l'atomisation \u2014 le lexique suit l'auteur du "
            "volume. Toute mesure de vocabulaire sur ce volume en h\u00e9rite.",
    },
    "onanie_homosexualitaet": {
        "fichier": "1917_onanie_homosexualitaet.ia.txt",
        "dossier": ("stekel", "de"),
        "provenance": "archive",
        "auteur": "Wilhelm Stekel",
        "titre": "Onanie und Homosexualit\u00e4t (Die homosexuelle Neurose)",
        "titre_fr": "Onanisme et homosexualit\u00e9 (la n\u00e9vrose homosexuelle)",
        "annee_oeuvre": 1917,
        "annee_edition": 1917,
        "edition": "1. Auflage (St\u00f6rungen des Trieb- und Affektlebens, II)",
        "editeur": "Urban & Schwarzenberg, Berlin/Wien",
        "source": "Internet Archive \u2014 fac-simil\u00e9 OCRis\u00e9, NON relu (scan Google)",
        "url": "https://archive.org/details/bub_gb_lQ4_AQAAMAAJ",
        # APR\u00c8S LA RUPTURE, et sur le sujet m\u00eame qui l'a caus\u00e9e : l'onanisme est l'un des deux
        # points de d\u00e9saccord de 1912. C'est le seul volume du corpus qui prenne cette question
        # pour objet principal.
        "debut_corps": "Schon vor dem Ausbruch des Weltkrieges war die Fortsetzung",
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

# Licence par AUTEUR, pour ceux dont la date de mort diffère de celle de Freud. Le calcul est le
# même partout — vie + 70 ans en Allemagne/Autriche, et parution avant 1931 pour la règle
# américaine — mais l'année d'entrée dans le domaine public change, et la dire est le minimum
# qu'on doive à qui voudra réutiliser ce corpus.
LICENCES = {
    "Otto Rank": ("Domaine public — Otto Rank (1884-1939), œuvre libre de droits depuis 2010 "
                  "(vie + 70 ans). Éditions utilisées antérieures à 1931. Texte allemand original."),
    "Karl Abraham": ("Domaine public — Karl Abraham (1877-1925), œuvre libre de droits depuis 1996 "
                     "(vie + 70 ans). Texte allemand original."),
    "Sándor Ferenczi": ("Domaine public — Sándor Ferenczi (1873-1933), œuvre libre de droits "
                        "depuis 2004 (vie + 70 ans). Texte allemand original."),
    "Josef Breuer": ("Domaine public — Josef Breuer (1842-1925), œuvre libre de droits depuis 1996 "
                     "(vie + 70 ans). Texte allemand original."),
    "Wilhelm Stekel": ("Domaine public — Wilhelm Stekel (1868-1940), œuvre libre de droits depuis "
                       "2011 (vie + 70 ans). Éditions utilisées de 1907 à 1917, antérieures à 1931. "
                       "Texte allemand original. ÉCARTÉS et déclarés : son autobiographie de 1950, "
                       "œuvre américaine dont la couche éditoriale est protégée, et les revues "
                       "qu'il dirigeait, qui sont des publications à plusieurs voix."),
}


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
    if cle in MOTIFS_CHAPITRE:
        meta["motif_chapitre"] = MOTIFS_CHAPITRE[cle]
    meta.update({
        "cle": cle,
        "langue": meta.get("langue", "de"),
        "auteur": meta.get("auteur", "Sigmund Freud"),
        "empreinte_fichier": hashlib.sha256(brut.encode("utf-8")).hexdigest()[:16],
        "caracteres_fichier": len(brut),
        "caracteres_oeuvre": len(texte),
        "bornage_gutenberg": bornage,
        # La licence par défaut est celle de Freud ; une œuvre d'un autre auteur porte la sienne.
        # La licence déclarée sur l'œuvre l'emporte ; sinon celle de son AUTEUR ; sinon celle de
        # Freud, qui est le cas par défaut et le plus fréquent. Avant cette table, tout le corpus
        # non freudien portait la licence de Freud — des dates fausses sur des auteurs morts en
        # 1925, 1933 et 1940.
        "licence": meta.get("licence",
                            LICENCES.get(meta.get("auteur", "Sigmund Freud"), LICENCE)),
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


def _trouver_souple(texte, borne):
    """Position d'une borne, EN IGNORANT la largeur des blancs. -1 si absente.

    Une borne est un repère de TEXTE ; elle ne doit pas échouer sur la mise en page d'un scan.
    Or les fac-similés justifiés sortent « Ich  weiß  nicht,  wieviel  die \\neinzelnen  von  Ihnen »
    — doubles espaces et retour à la ligne au milieu de la phrase. Six bornes sur onze ont été
    déclarées introuvables pour cette seule raison, alors que leur texte était bien là.

    On cherche donc mot à mot, chaque intervalle valant n'importe quelle suite de blancs. La
    recherche exacte reste possible par construction : un seul espace correspond aussi à `\\s+`.
    """
    if not borne:
        return -1
    i = texte.find(borne)
    if i >= 0:
        return i
    m = re.search(r"\s+".join(re.escape(mot) for mot in borne.split()), texte)
    return m.start() if m else -1


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
        i = _trouver_souple(brut, borne)
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
    # Le bandeau de numérisation vient APRÈS les têtes courantes : il n'occupe pas une ligne à lui
    # mais s'insère au milieu des phrases coupées par le saut de page, et le retirer les recolle.
    corps, r_bandeau = ocr.retirer_bandeau_scan(corps)
    faits.append("bandeaux de numérisation retirés : %d" % r_bandeau["bandeaux_retires"])
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
