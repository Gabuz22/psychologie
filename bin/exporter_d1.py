#!/usr/bin/env python3
"""EXPORT du corpus vers Cloudflare D1 — le site sert ce que Python a calculé, jamais plus.

  python bin/exporter_d1.py          →  derive/d1/corpus.sqlite (contrôle local)
                                        derive/d1/01_schema.sql
                                        derive/d1/02_donnees_NN.sql (INSERT, en tranches)

PRINCIPE. Tout le calcul — atomisation, lexique, collation, vérification, grappes — reste en
Python, déterministe et testé. Ce script ne calcule RIEN : il déverse les résultats dans un
schéma relationnel que le Worker Cloudflare interroge en lecture seule. Si un chiffre du site
diffère d'un chiffre de `bin/analyser.py`, c'est un bug d'export, jamais une divergence de
méthode.

SCHÉMA MULTI-AUTEURS DÈS LE PREMIER JOUR. L'ambition du projet est de couvrir plusieurs
auteurs et courants : `auteurs` est une table, `oeuvres.auteur_id` une clé — même si Freud
(et Otto Rank, contributeur d'un appendice) sont seuls pour l'instant. Ajouter Jung ne
changera pas le schéma.

DATATION HONNÊTE JUSQUE DANS LA BASE. Chaque atome porte sa fenêtre [annee_min, annee_max]
(via core.corpus.fenetre_datation) et sa règle en clair : le site peut donc filtrer par année
sans jamais dater un passage de l'année de l'œuvre quand il n'en a pas le droit.

Les fichiers produits vont dans derive/ : ce sont des SORTIES régénérables, jamais versionnées.
"""
import datetime
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import agents, carte, comparaison, lexique, ocr, sources, verification  # noqa: E402
from core.corpus import Corpus, fenetre_datation            # noqa: E402
from core.segmentation import replier                       # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "derive", "d1")

# Métadonnées d'auteurs — le corpus ne les contient pas (il ne connaît que les noms).
AUTEURS = {
    "Sigmund Freud": {"naissance": 1856, "mort": 1939, "courant": "psychanalyse"},
    "Otto Rank": {"naissance": 1884, "mort": 1939, "courant": "psychanalyse"},
    # Co-auteur des « Studien über Hysterie » (1895), dont il signe le cas d'Anna O. et tout le
    # chapitre théorique. Il n'est pas psychanalyste : il quitte Freud sur la question de la
    # sexualité, et défend l'état hypnoïde que celui-ci abandonnera. Le déclarer sous son propre
    # courant évite de compter sa théorie comme de la psychanalyse.
    "Josef Breuer": {"naissance": 1842, "mort": 1925, "courant": "méthode cathartique"},
    # Second auteur du corpus (2026-07), premier non-germanophone. Freud discute son livre de
    # 1895 pendant tout un chapitre de « Massenpsychologie und Ich-Analyse » (1921) : le corpus
    # tient les deux côtés de la controverse, chacun dans sa langue.
    "Gustave Le Bon": {"naissance": 1841, "mort": 1931, "courant": "psychologie des foules"},
    # Troisième auteur traité pour lui-même. Fondateur de la société de Berlin, analyste de
    # Melanie Klein et de Karen Horney, mort à quarante-huit ans sans avoir jamais rompu avec
    # Freud : le contre-cas exact de Rank, et c'est pourquoi il vient juste après lui.
    "Karl Abraham": {"naissance": 1877, "mort": 1925, "courant": "psychanalyse"},
    # Quatrième auteur traité pour lui-même. Le plus proche de Freud pendant vingt ans, et le
    # seul dont la divergence porte sur la TECHNIQUE plutôt que sur la doctrine : avec Rank qui
    # déplace une thèse et Abraham qui prolonge, le corpus tient trois formes du rapport au
    # maître — condition pour que « socle » et « écart » cessent d'être des mots.
    "S\u00e1ndor Ferenczi": {"naissance": 1873, "mort": 1933, "courant": "psychanalyse"},
    # Cinqui\u00e8me auteur trait\u00e9 pour lui-m\u00eame, et la QUATRI\u00c8ME forme du rapport au ma\u00eetre : il rompt
    # LE PREMIER (1912) et sur la doctrine, l\u00e0 o\u00f9 Rank d\u00e9place une th\u00e8se, Abraham prolonge et
    # Ferenczi diverge sur la technique. Son courant est d\u00e9clar\u00e9 \u00e0 part : apr\u00e8s la rupture il
    # fonde sa propre \u00e9cole, l'\u00ab analyse active \u00bb, qui n'est pas la psychanalyse freudienne \u2014 le
    # compter comme telle m\u00e9langerait deux doctrines dans les mesures par courant.
    "Wilhelm Stekel": {"naissance": 1868, "mort": 1940, "courant": "analyse active"},
}

# Éditorial des grappes (résumé de documentation/COURANTS_FREUD.md). L'agent `courants` ne
# nomme pas ses grappes ni ne les commente — ceci est une couche de PRÉSENTATION, raccrochée
# par concept SIGNATURE, et l'appariement est vérifié en bijection stricte par nommer_grappes()
# ci-dessous : un glissement de partition fait ÉCHOUER l'export, il ne produit jamais un
# libellé emprunté. La citation vedette, elle, n'est pas choisie ici : elle vient de l'agent
# lui-même (AgentCourants._decrire_grappe), pour que le site ne montre jamais un texte que le
# pipeline déterministe n'a pas produit.
# PARTITION REFAITE LE 2026-07-31, à l'entrée des onze œuvres freudiennes (23 → 34). Le garde-fou
# ci-dessous a bloqué l'export, et c'est ainsi qu'il fallait le découvrir : deux grappes sans
# éditorial, une revendiquée trois fois. Ce qu'il faut retenir de ce déplacement, et qui vaut mieux
# que les libellés eux-mêmes : LA PARTITION N'EST PAS UN FAIT SUR FREUD, c'est un état de la mesure
# sur un corpus donné. Doubler le corpus l'a recomposée — trois grappes ont FUSIONNÉ, deux sont
# APPARUES. Aucune de ces quatre décisions n'a été prise par quiconque : elles sortent d'une
# maximisation de modularité sur les cooccurrences, et le lexique n'a pas bougé d'un mot.
EDITORIAL_GRAPPES = [
    ("traumarbeit", "Le rêve, l'appareil psychique, et le mot d'esprit",
     "Le mécanisme du rêve (condensation, déplacement, censure) réuni à la métapsychologie qui "
     "l'explique — conscience, investissement, décharge, excitation — et, depuis l'entrée des "
     "« Vorlesungen », au COMIQUE : le rire, la plaisanterie, l'imitation ont rejoint le rêve. "
     "Le voisinage n'est pas fortuit et Freud l'établit lui-même dès 1905 : le mot d'esprit et le "
     "rêve partagent leur technique, condensation et déplacement, et ne diffèrent que par leur "
     "destination.",
     "40 concepts, la plus grosse grappe du corpus. Sa taille est elle-même un résultat : chez "
     "Freud le rêve n'est pas un objet parmi d'autres, c'est le modèle sur lequel l'appareil "
     "psychique est pensé. Une grappe aussi large discrimine moins qu'une petite — elle dit un "
     "voisinage massif, pas une articulation fine."),
    ("dichter", "La fiction, la famille et la mort",
     "Le poète, le récit, le fantasme et le symbole, noués au roman familial — père, mère, "
     "fratrie, Œdipe, castration — et à la mort. Freud lit la fiction avec les outils de la "
     "clinique et le mythe familial comme une œuvre ; la partition les met ensemble.",
     "27 concepts. C'est un DÉPLACEMENT NET par rapport à l'état précédent : la famille "
     "appartenait à la grappe de la pulsion, elle a migré vers celle de la fiction. Les cinq "
     "volumes de la Sammlung, qui portent les grands cas cliniques racontés comme des récits, "
     "pèsent visiblement sur ce voisinage. À surveiller au prochain élargissement."),
    ("behandlung", "La clinique, la cure et la mémoire",
     "Hystérie, symptôme, transfert, suggestion, hypnose ; la conversion, la paralysie, la crise. "
     "La mémoire y figure au premier rang — souvenir, trace, oubli, après-coup, souvenir-écran : "
     "« Hysterische leiden größtentheils an Reminiscenzen », écrivent Breuer et Freud en 1895. Se "
     "souvenir n'est pas ici une faculté, c'est le traitement même.",
     "31 concepts. La grappe devait beaucoup aux « Studien über Hysterie » ; elle s'appuie "
     "désormais aussi sur les cinq cas cliniques entrés avec la Sammlung, ce qui la rend moins "
     "dépendante d'une œuvre unique. La GUERRE (« krieg ») l'a rejointe — les névroses de guerre "
     "sont traitées comme des traumatismes, non comme un fait d'histoire."),
    ("libido", "La pulsion, les instances, et la faute",
     "Libido, sexualité, stades du développement, perversion, narcissisme ; les instances — Moi, "
     "Ça, conscience morale — et le couple sadisme/masochisme avec l'agression ; la culpabilité, "
     "le remords, le châtiment, la mélancolie.",
     "34 concepts, et c'est la TRIPLE FUSION de cet élargissement : trois grappes autrefois "
     "distinctes — la pulsion, « la faute et le crime », « sadisme, masochisme, agression » — n'en "
     "font plus qu'une. Les deux petites étaient annoncées comme fragiles (192 et 178 atomes, "
     "« sensibles au moindre changement »), et elles l'étaient. Ce qui les a fondues est lisible : "
     "« Das Ich und das Es » et « Das Unbehagen in der Kultur » nouent en un seul tissu la pulsion "
     "de mort, l'agression retournée, le Sur-Moi et le sentiment de culpabilité."),
    ("totem", "Religion, anthropologie, culture et lien social",
     "Le totémisme, le tabou, le sacrifice, le dieu ; l'interdit moral, la masse et son meneur ; "
     "la culture, l'art, la science, l'institution. La névrose obsessionnelle y voisine le "
     "religieux — rapprochement que Freud pose lui-même dès 1907 dans « Zwangshandlungen und "
     "Religionsübungen » : le cérémonial du névrosé et le rite du croyant ont la même structure.",
     "22 concepts. « Das Unbehagen in der Kultur » y a fait entrer la CULTURE et l'INSTITUTION, "
     "qui manquaient à une grappe jusque-là surtout anthropologique. L'INQUIÉTANTE ÉTRANGETÉ "
     "(« unheimlich ») y figure aussi, ce qui se discute : elle relève autant de l'esthétique."),
    ("koerper", "Le corps regardé",
     "Sept concepts, et rien d'autre : l'œil, le visage, la main, la tête, la barbe, le corps, la "
     "douleur. Ce n'est pas une thèse de Freud, c'est ce qu'il DÉCRIT quand il décrit — le corps "
     "d'un patient, d'une statue, d'un tableau.",
     "GRAPPE NOUVELLE, et elle vaut surtout comme mise en garde. Elle s'est détachée de la "
     "clinique parce que le corpus élargi contient davantage de description : les cas de la "
     "Sammlung détaillent des corps, et le Moïse comme le Léonard décrivent des œuvres. Un "
     "voisinage de VOCABULAIRE DESCRIPTIF n'est pas un courant de pensée, et la partition ne sait "
     "pas faire la différence."),
    ("fehlleistung", "Les actes manqués",
     "Trois concepts : l'acte manqué, le lapsus, la méprise. Le lapsus révèle une intention "
     "contraire — c'est par là que Freud choisit de commencer son enseignement, avant même le "
     "rêve, parce que c'est le fait le plus quotidien et le moins contestable.",
     "GRAPPE NOUVELLE, et son apparition a une cause unique et vérifiable : le premier tome des "
     "« Vorlesungen » (1916) leur est ENTIÈREMENT consacré, quatre leçons sur quatre. Avant lui, "
     "ces trois concepts se dispersaient dans la Psychopathologie sans former de voisinage propre. "
     "Une grappe peut donc naître d'un seul volume — ce qu'elle mesure alors est autant un fait "
     "d'édition qu'un fait de doctrine."),
    ("malerei", "La peinture et le pacte",
     "Trois concepts seulement, tirés de deux œuvres : le Moïse de Michel-Ange et la névrose "
     "démoniaque du peintre Haizmann.",
     "CONTRE-EXEMPLE À GARDER SOUS LA MAIN, et il a SURVÉCU au doublement du corpus, ce qui le "
     "rend plus instructif encore. « teufel » et « pakt » n'ont rien à faire avec la peinture — "
     "ils y sont parce que l'unique œuvre sur le diable porte sur un peintre. Cooccurrence réelle, "
     "lien conceptuel absent."),
]


def nommer_grappes(grappes):
    """Apparie chaque grappe à son éditorial — et ÉCHOUE BRUYAMMENT si l'appariement est douteux.

    L'éditorial est raccroché par un concept SIGNATURE, ce qui est fragile : quand le lexique
    change, la partition bouge et une signature peut se retrouver dans une autre grappe, dans
    deux grappes, ou dans aucune. C'est arrivé à l'audit 4 (2026-07) — deux grappes s'étaient
    retrouvées sans nom et deux avec un nom emprunté, SANS que rien ne le signale : le site
    aurait affiché « La seconde topique » sur une grappe de dix-neuf concepts.
    Un défaut doit être visible, jamais silencieux : on exige donc une bijection stricte.
    """
    par_rang, erreurs = {}, []
    for sig, nom, description, reserve in EDITORIAL_GRAPPES:
        rangs = [i for i, g in enumerate(grappes, 1) if sig in g["concepts"]]
        if len(rangs) != 1:
            erreurs.append("signature « %s » (%s) trouvée dans %d grappe(s) : %s"
                           % (sig, nom, len(rangs), rangs or "aucune"))
            continue
        if rangs[0] in par_rang:
            erreurs.append("grappe %d revendiquée deux fois (%s / %s)"
                           % (rangs[0], par_rang[rangs[0]][0], nom))
            continue
        par_rang[rangs[0]] = (nom, description, reserve)
    for i in range(1, len(grappes) + 1):
        if i not in par_rang:
            erreurs.append("grappe %d sans éditorial — concepts : %s"
                           % (i, ", ".join(sorted(grappes[i - 1]["concepts"]))))
    if erreurs:
        raise SystemExit(
            "ÉDITORIAL DES GRAPPES DÉSYNCHRONISÉ — la partition a changé (probablement après une "
            "modification du lexique). Reprendre EDITORIAL_GRAPPES dans bin/exporter_d1.py, et "
            "régénérer documentation/COURANTS_FREUD.md, qui décrit ces mêmes grappes."
            + "".join(chr(10) + "  - " + e for e in erreurs))
    return par_rang

SCHEMA = """
DROP TABLE IF EXISTS mentions;
DROP TABLE IF EXISTS carte_couverture;
DROP TABLE IF EXISTS carte_couples;
DROP TABLE IF EXISTS carte_actes;
DROP TABLE IF EXISTS usages;
DROP TABLE IF EXISTS nominations;
DROP TABLE IF EXISTS lectures_declarees;
DROP TABLE IF EXISTS liens_reprise;
DROP TABLE IF EXISTS grappe_concepts;
DROP TABLE IF EXISTS grappes;
DROP TABLE IF EXISTS signaux;
DROP TABLE IF EXISTS fonctions;
DROP TABLE IF EXISTS atome_sous_concepts;
DROP TABLE IF EXISTS atome_concepts;
DROP TABLE IF EXISTS atomes;
DROP TABLE IF EXISTS concepts;
DROP TABLE IF EXISTS oeuvres;
DROP TABLE IF EXISTS auteurs;
DROP TABLE IF EXISTS meta;

CREATE TABLE auteurs (
  id INTEGER PRIMARY KEY,
  nom TEXT NOT NULL UNIQUE,
  naissance INTEGER,
  mort INTEGER,
  courant TEXT
);
CREATE TABLE oeuvres (
  id INTEGER PRIMARY KEY,
  cle TEXT NOT NULL UNIQUE,
  titre TEXT NOT NULL,
  titre_fr TEXT,
  langue TEXT NOT NULL DEFAULT 'de',
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
  annee_oeuvre INTEGER NOT NULL,
  annee_edition INTEGER NOT NULL,
  edition TEXT,
  editeur TEXT,
  source TEXT,
  url TEXT,
  datation_regle TEXT NOT NULL,
  datation_precise INTEGER NOT NULL,
  collationnee INTEGER NOT NULL,
  -- « relu » = transcription relue par des humains (Gutenberg, Wikisource).
  -- « ocr »  = fac-similé océrisé, NON relu : les cinq volumes d'Otto Rank, faute de toute
  --            transcription existante. La réserve voyage avec l'œuvre pour que le lecteur la
  --            voie sur chaque citation, comme la règle de datation.
  qualite_source TEXT NOT NULL DEFAULT 'relu',
  ocr_phrases_corrompues_pct REAL
);
CREATE TABLE atomes (
  id INTEGER PRIMARY KEY,
  atome_id TEXT NOT NULL UNIQUE,
  empreinte TEXT NOT NULL,
  oeuvre_id INTEGER NOT NULL REFERENCES oeuvres(id),
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
  idx INTEGER NOT NULL,
  texte TEXT NOT NULL,
  texte_replie TEXT NOT NULL,
  debut INTEGER NOT NULL,
  fin INTEGER NOT NULL,
  nb_mots INTEGER NOT NULL,
  chapitre TEXT,
  statut TEXT NOT NULL,
  non_qualifie INTEGER NOT NULL,
  couche TEXT,
  annee_min INTEGER NOT NULL,
  annee_max INTEGER NOT NULL,
  datation_regle TEXT NOT NULL,
  -- Cette phrase-ci porte une trace de corruption OCR (« sih » pour « sich », « nidit » pour
  -- « nicht »). Elle reste consultable : le lecteur sait seulement qu'il doit la vérifier sur le
  -- fac-similé avant de la publier. Marquer vaut mieux que retirer, et infiniment mieux que taire.
  ocr_suspect INTEGER NOT NULL DEFAULT 0
);
-- UN CONCEPT APPARTIENT À UN AUTEUR. L'unicité porte sur le couple (nom, auteur) et non sur le
-- nom seul : deux auteurs peuvent employer le même mot pour deux choses différentes, et le
-- corpus doit pouvoir les tenir côte à côte sans jamais les additionner.
CREATE TABLE concepts (
  id INTEGER PRIMARY KEY,
  nom TEXT NOT NULL,
  groupe TEXT NOT NULL,
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
  n_atomes INTEGER NOT NULL DEFAULT 0,
  UNIQUE (nom, auteur_id)
);
CREATE TABLE atome_concepts (
  atome_id INTEGER NOT NULL REFERENCES atomes(id),
  concept_id INTEGER NOT NULL REFERENCES concepts(id),
  PRIMARY KEY (atome_id, concept_id)
);
CREATE TABLE atome_sous_concepts (
  atome_id INTEGER NOT NULL REFERENCES atomes(id),
  concept_id INTEGER NOT NULL REFERENCES concepts(id),
  sous TEXT NOT NULL
);
CREATE TABLE fonctions (
  atome_id INTEGER NOT NULL REFERENCES atomes(id),
  fonction TEXT NOT NULL
);
-- COUCHE DE COMPARAISON INTER-AUTEURS. Elle relie des graphes construits SÉPARÉMENT et ne
-- fusionne jamais deux concepts : un lien va d'un ATOME à un ATOME, chacun gardant son auteur.
-- Aucune colonne ne nomme la NATURE du rapport (ni socle, ni emprunt, ni contradiction) : la
-- couche établit qu'un TEXTE est partagé, et laisse lire les deux passages.
CREATE TABLE liens_reprise (
  id INTEGER PRIMARY KEY,
  atome_a INTEGER NOT NULL REFERENCES atomes(id),
  atome_b INTEGER NOT NULL REFERENCES atomes(id),
  auteur_a INTEGER NOT NULL REFERENCES auteurs(id),
  auteur_b INTEGER NOT NULL REFERENCES auteurs(id),
  contenance REAL NOT NULL,
  force TEXT NOT NULL,             -- « manifeste » (≥ 0,70) ou « partielle »
  -- « a_vers_b », « b_vers_a », ou NULL quand les fenêtres de datation se chevauchent.
  -- NULL veut dire INDÉCIDABLE, jamais « pas de lien » : c'est une information sur ce que le
  -- corpus permet d'établir, pas une absence à combler.
  sens TEXT,
  -- Les deux passages nomment une source tierce (Sophocle, Shakespeare) : le partage de mots
  -- ne prouve plus un emprunt entre les deux auteurs, et le lien n'est jamais orienté.
  source_tierce INTEGER NOT NULL DEFAULT 0,
  a_verifier INTEGER NOT NULL DEFAULT 1,
  evenement INTEGER,               -- paires contiguës = un seul acte de citation
  partages TEXT,                   -- suites de mots partagées, pour surligner à l'affichage
  -- Ce que la LECTURE ajoute au calcul (registre verification/reprises_lues.json). Le détecteur
  -- s'arrête à la phrase ; le lecteur remonte de quelques atomes et trouve l'attribution
  -- (« Ich zitiere wörtlich », un appel de note). D'où deux colonnes de sens : `sens`, ce que le
  -- calcul établit à partir des seules dates, et `sens_lu`, ce que le texte déclare. La seconde
  -- ne remplace pas la première — on garde les deux pour que l'écart reste visible.
  verdict TEXT,                    -- « confirme », « rejete », « reclasse », ou NULL = non lu
  sens_lu TEXT,
  reclasse_vers TEXT,              -- source tierce commune, quand aucun des deux ne lit l'autre
  motif_lecture TEXT               -- le texte qui fonde le verdict, cité
);
CREATE TABLE lectures_declarees (
  id INTEGER PRIMARY KEY,
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
  auteur_lu_id INTEGER NOT NULL REFERENCES auteurs(id),
  oeuvre_id INTEGER NOT NULL REFERENCES oeuvres(id),
  chapitre TEXT NOT NULL,
  portee_atomes INTEGER NOT NULL,
  homographe TEXT
);
CREATE TABLE nominations (
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
  auteur_nomme_id INTEGER NOT NULL REFERENCES auteurs(id),
  atomes INTEGER NOT NULL,
  homographe TEXT,
  PRIMARY KEY (auteur_id, auteur_nomme_id)
);
-- MENTIONS NOMINALES — la SECONDE couche de la carte, et elle en est presque tout le volume :
-- 2 216 mentions sur 2 135 phrases, contre 248 phrases d'acte de citation, et 11 couples
-- d'auteurs contre 6. Le recouvrement entre les deux est quasi nul (1,7 %) : ce ne sont pas deux
-- mesures du même fait, mais deux faits différents.
--
-- ELLES NE SONT JAMAIS FUSIONNÉES AVEC LES ACTES. Un acte est un TEXTE partagé ; une mention est
-- un NOM écrit. Les additionner ferait exactement l'erreur que la carte a été bâtie pour éviter.
-- Sans cette couche, pourtant, la carte ment par omission : Ferenczi nomme Freud dans 960 de ses
-- phrases et ne partage un texte avec lui que dans 9 — la carte des seuls actes le montrerait
-- comme un satellite lointain.
--
-- CE QU'UNE MENTION N'ÉTABLIT PAS : la nature du rapport. Nommer n'est ni suivre, ni approuver,
-- ni contredire. Le corpus a déjà éprouvé ce piège — un marqueur construit pour repérer les
-- écarts d'un disciple avec Freud a donné 0 confirmé sur 5, les cinq passages étant des renvois
-- d'accord. Le passage est donc stocké en entier, pour qu'on aille lire.
CREATE TABLE mentions (
  atome_id INTEGER NOT NULL REFERENCES atomes(id),
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),         -- celui qui écrit
  auteur_nomme_id INTEGER NOT NULL REFERENCES auteurs(id),   -- celui qui est nommé
  -- Avertissement porté par la mention elle-même : « Abraham » désigne aussi le patriarche
  -- biblique, que Rank et Freud citent abondamment dans leurs travaux sur le mythe. 104 des
  -- 2 216 mentions sont dans ce cas et ne doivent pas être lues comme des renvois à Karl Abraham.
  homographe TEXT
);
-- CARTE DES ACTES DE CITATION. L'unité est l'ACTE — des paires de phrases contiguës des deux
-- côtés forment un seul acte de citation — et non le couple de concepts. Ce choix n'est pas de
-- confort : agréger les concepts de part et d'autre donnerait 1 366 « arêtes » là où il y a 107
-- actes réels, chaque phrase portant 3,5 concepts en moyenne. C'est la même accumulation
-- combinatoire qui a fait écarter l'appariement de concepts (documentation/APPARIEMENT_ECARTE.md).
CREATE TABLE carte_actes (
  id INTEGER PRIMARY KEY,
  auteur_a INTEGER NOT NULL REFERENCES auteurs(id),
  auteur_b INTEGER NOT NULL REFERENCES auteurs(id),
  oeuvre_a INTEGER NOT NULL REFERENCES oeuvres(id),
  oeuvre_b INTEGER NOT NULL REFERENCES oeuvres(id),
  poids INTEGER NOT NULL,          -- nombre de phrases couvertes ; JAMAIS un produit de concepts
  contenance_max REAL NOT NULL,
  contenance_moyenne REAL NOT NULL,
  id_debut_a TEXT NOT NULL, id_fin_a TEXT NOT NULL,
  id_debut_b TEXT NOT NULL, id_fin_b TEXT NOT NULL,
  force TEXT, sens TEXT, sens_lu TEXT, verdict TEXT, reclasse_vers TEXT,
  source_tierce INTEGER NOT NULL DEFAULT 0,
  -- La preuve est portée DEUX FOIS. `partage_replie` est la forme normalisée sur laquelle la
  -- comparaison a travaillé (orthographe d'avant 1901 neutralisée, géminations instables de
  -- l'OCR ramenées) : elle permet de refaire le calcul. `citation_a` / `citation_b` sont les
  -- passages TELS QU'ILS SONT IMPRIMÉS de chaque côté : eux seuls permettent de vérifier dans le
  -- livre. Publier la seule forme repliée était le défaut de la première version — « hattest » y
  -- devient « hatest », illisible et introuvable dans le texte.
  partage_replie TEXT,
  citation_a TEXT,
  citation_b TEXT,
  -- Les concepts sont du CONTEXTE, jamais des arêtes. Seuls ceux que les DEUX passages portent
  -- renseignent ; les deux autres colonnes sont là pour qu'on puisse constater ce qu'un produit
  -- croisé aurait fabriqué.
  concepts_communs TEXT,
  concepts_a_seul TEXT,
  concepts_b_seul TEXT
);
-- Résumé par couple d'auteurs, Y COMPRIS LES COUPLES SANS AUCUN ACTE. `silence` dit pourquoi :
-- « langues » (indétectable par construction — les corpus français et allemand du projet
-- partagent UN seul groupe de six mots, alors que Freud consacre un chapitre entier à Le Bon)
-- ou « aucun_acte ». Taire ces couples, comme le faisait la première version, présentait un
-- aveuglement de méthode comme un fait de corpus.
CREATE TABLE carte_couples (
  auteur_a INTEGER NOT NULL REFERENCES auteurs(id),
  auteur_b INTEGER NOT NULL REFERENCES auteurs(id),
  evenements INTEGER NOT NULL, atomes INTEGER NOT NULL,
  manifestes INTEGER NOT NULL, orientes INTEGER NOT NULL,
  lus INTEGER NOT NULL, confirmes INTEGER NOT NULL,
  reclasses INTEGER NOT NULL, rejetes INTEGER NOT NULL,
  source_tierce INTEGER NOT NULL,
  silence TEXT, langue_a TEXT, langue_b TEXT,
  PRIMARY KEY (auteur_a, auteur_b)
);
-- CE QUE LA CARTE NE VOIT PAS, servi avec elle. Une œuvre absente de la carte ne dit pas que son
-- auteur n'y cite personne : elle peut être hors d'atteinte. `part_trop_courts` donne la part de
-- ses phrases écartées d'office par le seuil de vingt mots de la couche de comparaison.
-- DEUX COLONNES SÉPARÉES, ET C'EST UNE CORRECTION. La ligne de totaux rangeait sa couverture
-- dans `part_trop_courts`, colonne qui veut dire tout autre chose ; le worker la relisait sous un
-- alias (« part_trop_courts AS part_touchee ») et le détournement ne se lisait nulle part. Chaque
-- mesure a désormais sa colonne, et celle qui ne s'applique pas à la ligne vaut NULL.
CREATE TABLE carte_couverture (
  oeuvre_id INTEGER REFERENCES oeuvres(id),
  cle TEXT,                        -- NULL pour la ligne de totaux
  atomes INTEGER NOT NULL,         -- œuvre muette : ses atomes ; totaux : atomes DISTINCTS touchés
  part_trop_courts REAL,           -- œuvre muette seulement
  part_touchee REAL,               -- ligne de totaux seulement
  muette INTEGER NOT NULL DEFAULT 1
);
-- USAGE DES MOTS. Un motif est appliqué à TOUS les corpus de sa langue, et on compte. C'est la
-- seule comparaison inter-auteurs de concepts que le corpus autorise : elle ne suppose à aucun
-- moment que deux auteurs veulent dire la même chose, elle mesure qui écrit quel mot.
--
-- `lexique` retient QUI a défini le motif, et cette colonne n'est pas décorative. La ligne d'un
-- auteur sur son propre motif est haute par construction — le lexique a été écrit pour lui. Ce
-- sont les lignes des AUTRES qui portent l'information, parce que personne ne les a choisies
-- pour eux. Effacer la provenance ferait passer pour neutre une mesure qui ne l'est qu'à moitié.
CREATE TABLE usages (
  sous_concept TEXT NOT NULL,
  groupe TEXT NOT NULL,
  libelle TEXT NOT NULL,
  lexique INTEGER NOT NULL REFERENCES auteurs(id),
  langue TEXT NOT NULL,
  motif TEXT NOT NULL,
  auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
  atomes INTEGER NOT NULL,
  porteurs INTEGER NOT NULL,
  pour_mille REAL NOT NULL
);
CREATE TABLE signaux (
  atome_id INTEGER NOT NULL REFERENCES atomes(id),
  signal TEXT NOT NULL,
  verdict TEXT,
  motif TEXT
);
CREATE TABLE grappes (
  id INTEGER PRIMARY KEY,
  rang INTEGER NOT NULL,
  nom TEXT NOT NULL,
  description TEXT,
  reserve TEXT,
  taille INTEGER NOT NULL,
  atomes_concernes INTEGER NOT NULL,
  citation_atome_id TEXT
);
CREATE TABLE grappe_concepts (
  grappe_id INTEGER NOT NULL REFERENCES grappes(id),
  concept_id INTEGER NOT NULL REFERENCES concepts(id)
);
CREATE TABLE meta (
  cle TEXT PRIMARY KEY,
  valeur TEXT NOT NULL
);
CREATE INDEX idx_atomes_oeuvre ON atomes(oeuvre_id);
CREATE INDEX idx_atomes_auteur ON atomes(auteur_id);
CREATE INDEX idx_atomes_statut ON atomes(statut);
CREATE INDEX idx_atomes_fenetre ON atomes(annee_min, annee_max);
CREATE INDEX idx_ac_concept ON atome_concepts(concept_id);
CREATE INDEX idx_asc_sous ON atome_sous_concepts(sous);
CREATE INDEX idx_fonctions_f ON fonctions(fonction);
CREATE INDEX idx_signaux_s ON signaux(signal);
CREATE INDEX idx_usages_sc ON usages(sous_concept);
CREATE INDEX idx_carte_poids ON carte_actes(poids DESC);
CREATE INDEX idx_mentions_couple ON mentions(auteur_id, auteur_nomme_id);
"""


def construire(chemin_sqlite):
    """Construit la base SQLite complète depuis le corpus. Rend la connexion (pour le dump)."""
    if os.path.exists(chemin_sqlite):
        os.remove(chemin_sqlite)
    db = sqlite3.connect(chemin_sqlite)
    db.executescript(SCHEMA)

    corpus = Corpus()

    # ---- auteurs
    ids_auteur = {}
    noms = sorted({a.get("auteur", "Sigmund Freud") for a in corpus.atomes})
    for nom in noms:
        m = AUTEURS.get(nom, {})
        cur = db.execute("INSERT INTO auteurs (nom, naissance, mort, courant) VALUES (?,?,?,?)",
                         (nom, m.get("naissance"), m.get("mort"), m.get("courant")))
        ids_auteur[nom] = cur.lastrowid

    # ---- œuvres
    ids_oeuvre = {}
    for cle, meta in sorted(corpus.oeuvres.items(), key=lambda x: x[1]["annee_oeuvre"]):
        src = sources.OEUVRES[cle]
        d = sources.datation(src)
        collationnee = any(a["attestation"].get("couche") for a in corpus.par_oeuvre(cle))
        ocrise = src.get("provenance") == "archive"
        corruption = (ocr.corruption(sources.charger(cle)["texte"])["taux_phrases_pct"]
                      if ocrise else None)
        cur = db.execute(
            "INSERT INTO oeuvres (cle, titre, titre_fr, langue, auteur_id, annee_oeuvre,"
            " annee_edition, edition, editeur, source, url, datation_regle, datation_precise,"
            " collationnee, qualite_source, ocr_phrases_corrompues_pct)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cle, src["titre"], src.get("titre_fr"), src.get("langue", "de"),
             # L'auteur du VOLUME vient du registre — plus forcément Freud depuis Le Bon.
             ids_auteur[src.get("auteur", "Sigmund Freud")],
             src["annee_oeuvre"], src["annee_edition"], src.get("edition"), src.get("editeur"),
             src.get("source"), src.get("url"), d["regle"], int(d["precise"]), int(collationnee),
             "ocr" if ocrise else "relu", corruption))
        ids_oeuvre[cle] = cur.lastrowid

    # ---- concepts : UN RÉFÉRENTIEL PAR AUTEUR, jamais un référentiel commun.
    # La clé est le COUPLE (auteur, concept), et c'est essentiel : deux auteurs peuvent porter un
    # concept de même nom sans désigner la même chose. `geburt` est chez Rank le traumatisme
    # d'origine de toute angoisse ; le mot n'a pas ce statut chez Freud. Les confondre dans une
    # seule ligne ferait additionner deux notions distinctes à la première requête venue.
    # On n'enregistre le référentiel que des auteurs qui SIGNENT UN VOLUME. Un contributeur
    # (Breuer dans les « Studien », Rank dans la « Traumdeutung ») voit ses pages décrites avec
    # les catégories du livre qui les contient : lui créer un référentiel propre produirait 171
    # concepts orphelins, à zéro atome, que rien ne viendrait jamais remplir.
    ids_concept = {}
    for nom_auteur in sorted({m.get("auteur", "Sigmund Freud") for m in sources.OEUVRES.values()}):
        table = lexique.pour_auteur(nom_auteur)
        for groupe, meta in table.CONCEPTS.items():
            for nom in meta["termes"]:
                if (nom_auteur, nom) in ids_concept:
                    continue
                cur = db.execute("INSERT INTO concepts (nom, groupe, auteur_id) VALUES (?,?,?)",
                                 (nom, groupe, ids_auteur[nom_auteur]))
                ids_concept[(nom_auteur, nom)] = cur.lastrowid

    # ---- atomes et jointures
    table_verdicts = verification.charger()["verdicts"]
    for a in corpus.atomes:
        ch = a["chapitre"]
        amin, amax = fenetre_datation(a)
        cur = db.execute(
            "INSERT INTO atomes (atome_id, empreinte, oeuvre_id, auteur_id, idx, texte,"
            " texte_replie, debut, fin, nb_mots, chapitre, statut, non_qualifie, couche,"
            " annee_min, annee_max, datation_regle, ocr_suspect)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["id"], a["empreinte"], ids_oeuvre[a["oeuvre"]],
             ids_auteur[a.get("auteur", "Sigmund Freud")], a["index"], a["texte"],
             replier(a["texte"]), a["debut"], a["fin"], a["nb_mots"],
             ("%s. %s" % (ch["numero"], ch["titre"])) if ch else None,
             a["statut"], int(a["non_qualifie"]), a["attestation"].get("couche"),
             amin, amax, a["attestation"]["regle"], int(a.get("ocr_suspect", False))))
        aid = cur.lastrowid
        # Les concepts d'un atome sont ceux du lexique de l'AUTEUR DU VOLUME — le même que celui
        # avec lequel l'atomisation les a trouvés (voir atomisation._atomiser). Une contribution
        # insérée dans le livre d'un autre garde donc les catégories de ce livre.
        auteur_lexique = sources.OEUVRES[a["oeuvre"]].get("auteur", "Sigmund Freud")
        for c in a["concepts"]:
            cid = ids_concept[(auteur_lexique, c["concept"])]
            db.execute("INSERT OR IGNORE INTO atome_concepts VALUES (?,?)", (aid, cid))
            for sc in c.get("sous_concepts", []):
                db.execute("INSERT INTO atome_sous_concepts VALUES (?,?,?)", (aid, cid, sc))
        for f in a["fonctions"]:
            db.execute("INSERT INTO fonctions VALUES (?,?)", (aid, f))
        for s in a["signaux_a_confirmer"]:
            j = table_verdicts.get(a["empreinte"])
            verdict = j["verdict"] if j and j.get("signal") == s else None
            motif = j["motif"] if j and j.get("signal") == s else None
            db.execute("INSERT INTO signaux VALUES (?,?,?,?)", (aid, s, verdict, motif))

    db.execute("UPDATE concepts SET n_atomes ="
               " (SELECT COUNT(*) FROM atome_concepts ac WHERE ac.concept_id = concepts.id)")

    # ---- couche de comparaison inter-auteurs (agents `reprises` et `lectures`)
    # Recalculée ici comme les grappes : le site ne sert jamais qu'un résultat produit par le
    # pipeline déterministe. Les identifiants d'atome sont retrouvés par leur clé textuelle.
    ids_atome = dict(db.execute("SELECT atome_id, id FROM atomes").fetchall())

    # On passe par le module et non par la fiche de l'agent : celle-ci plafonne son extrait à
    # quarante liens par couple, ce qui convient à une réponse d'API mais tronquerait la base —
    # 104 liens enregistrés au lieu de 132 lors du premier essai. Une troncature silencieuse est
    # exactement ce que ce projet refuse : la base doit contenir tout ce que le calcul a produit.
    lus = verification.charger_reprises()
    par_auteur_atomes = {}
    for a in corpus.atomes:
        par_auteur_atomes.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
    index_ng = [comparaison._n_grammes_utiles(v, None) for v in par_auteur_atomes.values()]
    df_ng = comparaison.frequences_documentaires(index_ng)

    noms_auteurs = sorted(par_auteur_atomes)
    liens_carte = {}
    for i, x in enumerate(noms_auteurs):
        for y in noms_auteurs[i + 1:]:
            bruts = comparaison.reprises(par_auteur_atomes[x], par_auteur_atomes[y], df_ng)
            retenus = [comparaison.qualifier(l) for l in bruts
                       if l["contenance"] >= comparaison.SEUIL_PUBLICATION]
            if not retenus:
                continue
            # Les paires contiguës des deux côtés forment un seul ACTE de citation : c'est lui
            # qu'on compte, sans quoi celui qui cite par longs blocs paraîtrait le plus lié.
            # Chaque lien reçoit son verdict de lecture AVANT tout usage : la table des liens et
            # la carte doivent voir exactement la même chose, sans quoi le site montrerait deux
            # comptes différents du même travail.
            for lien in retenus:
                # Le verdict est retrouvé par EMPREINTES, jamais par identifiants d'atome :
                # ceux-ci se décalent à la moindre correction de paratexte en amont.
                j = verification.verdict_reprise(
                    lien["a"]["empreinte"], lien["b"]["empreinte"], lus) or {}
                sens_lu = j.get("sens_lu")
                # Le verdict a été rendu sur un couple ORDONNÉ (id_a, id_b) que la clé triée a
                # perdu. Si le calcul présente le couple dans l'autre ordre, le sens lu doit être
                # retourné — sans quoi on publierait l'emprunt à l'envers.
                #
                # LE RETOURNEMENT SE DÉCIDE SUR L'EMPREINTE, JAMAIS SUR UN IDENTIFIANT POSITIONNEL.
                #
                # La version précédente comparait `id_a` à `lien["a"]["id"]` — et le commentaire
                # deux lignes plus haut dit lui-même pourquoi c'est faux : « ceux-ci se décalent à
                # la moindre correction de paratexte en amont ». Ils se sont décalés. Le test
                # devenait vrai sans qu'aucun ordre n'ait changé, et retournait le sens d'un lien
                # parfaitement correct. Mesuré à la correction : sur 56 liens portant un sens lu,
                # 40 avaient l'identifiant intact et 16 avaient DÉRIVÉ — ces 16 étaient publiés
                # À L'ENVERS, et aucun ne relevait d'un vrai changement d'ordre. Le cas le plus
                # net : Abraham citant Freud en toutes lettres (« Ich zitiere den folgenden Passus
                # wörtlich nach Freud », Traum und Mythus 1909 contre Traumdeutung 1900) était
                # publié comme Freud citant Abraham — neuf ans avant que le texte d'Abraham existe.
                #
                # Le registre porte maintenant `empreinte_a`, le hachage du TEXTE du côté a. Il ne
                # dérive pas, et il tranche sans rien déduire. On a préféré cela à une comparaison
                # par ŒUVRE, qui aurait marché pour 53 couples sur 56 mais serait restée ambiguë
                # sur les volumes CO-ÉCRITS : trois reprises du corpus mettent en regard deux
                # atomes des mêmes « Studien über Hysterie », l'un de Breuer, l'autre de Freud.
                if sens_lu:
                    ancre = j.get("empreinte_a")
                    if not ancre:
                        raise SystemExit(
                            "SENS LU SANS ANCRAGE — le verdict %s porte un sens mais pas "
                            "d'`empreinte_a`. Sans elle, l'ordre (a, b) sur lequel le sens a été "
                            "rendu est indevinable, et publier l'emprunt à l'envers est le seul "
                            "risque que ce registre a pour mission d'écarter."
                            % verification.cle_reprise(lien["a"]["empreinte"],
                                                       lien["b"]["empreinte"]))
                    if ancre != lien["a"]["empreinte"]:
                        sens_lu = "b_vers_a" if sens_lu == "a_vers_b" else "a_vers_b"
                lien["verdict"] = j.get("verdict")
                lien["sens_lu"] = sens_lu
                lien["reclasse_vers"] = j.get("vers")
                lien["motif_lecture"] = j.get("motif")
                lien["_juge"] = bool(j)
            liens_carte[(x, y)] = retenus

            for rang, evt in enumerate(comparaison.evenements(retenus), 1):
                for lien in evt["paires"]:
                    ida = ids_atome.get(lien["a"]["id"])
                    idb = ids_atome.get(lien["b"]["id"])
                    if ida is None or idb is None:
                        continue
                    sens_lu = lien["sens_lu"]
                    db.execute(
                        "INSERT INTO liens_reprise (atome_a, atome_b, auteur_a, auteur_b,"
                        " contenance, force, sens, source_tierce, a_verifier, evenement, partages,"
                        " verdict, sens_lu, reclasse_vers, motif_lecture)"
                        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (ida, idb, ids_auteur[x], ids_auteur[y], lien["contenance"],
                         lien["force"], lien["sens"], int(lien["source_tierce"]),
                         int(lien["a_verifier"] and not lien["_juge"]), rang,
                         " | ".join(lien["partages"][:6]),
                         lien["verdict"], sens_lu, lien["reclasse_vers"],
                         lien["motif_lecture"]))

    # ---- carte des actes de citation
    # Elle ne recalcule RIEN : elle regroupe les mêmes liens en actes, et y ajoute ce que la
    # table des liens ne peut pas porter — le passage recollé, sa forme imprimée des deux côtés,
    # les concepts communs, et surtout les couples SANS acte avec la raison de leur silence.
    concepts_par_atome = {}
    for a in corpus.atomes:
        cs = {(x["groupe"], x["concept"]) for x in a.get("concepts", [])}
        if cs:
            concepts_par_atome[a["id"]] = cs
    actes = carte.evenements_de_carte(liens_carte, concepts_par_atome)
    for e in actes:
        db.execute(
            "INSERT INTO carte_actes (auteur_a, auteur_b, oeuvre_a, oeuvre_b, poids,"
            " contenance_max, contenance_moyenne, id_debut_a, id_fin_a, id_debut_b, id_fin_b,"
            " force, sens, sens_lu, verdict, reclasse_vers, source_tierce, partage_replie,"
            " citation_a, citation_b, concepts_communs, concepts_a_seul, concepts_b_seul)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (ids_auteur[e["auteur_a"]], ids_auteur[e["auteur_b"]],
             ids_oeuvre[e["oeuvre_a"]], ids_oeuvre[e["oeuvre_b"]], e["poids"],
             e["contenance_max"], e["contenance_moyenne"],
             e["id_debut_a"], e["id_fin_a"], e["id_debut_b"], e["id_fin_b"],
             e["force"], e["sens"], e["sens_lu"], e["verdict"], e["reclasse_vers"],
             int(e["source_tierce"]), " | ".join(e["partages"][:3]),
             e["citation_a"], e["citation_b"],
             ", ".join(e["concepts_communs"]), ", ".join(e["concepts_a_seul"]),
             ", ".join(e["concepts_b_seul"])))

    langues_carte = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)
    for c in carte.couples(actes, par_auteur_atomes.keys(), langues_carte):
        db.execute(
            "INSERT INTO carte_couples VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (ids_auteur[c["auteur_a"]], ids_auteur[c["auteur_b"]], c["evenements"], c["atomes"],
             c["manifestes"], c["orientes"], c["lus"], c["confirmes"], c["reclasses"],
             c["rejetes"], c["source_tierce"], c["silence"], c["langue_a"], c["langue_b"]))

    cov = carte.couverture(actes, corpus.atomes, corpus.oeuvres)
    for m in cov["muettes"]:
        db.execute("INSERT INTO carte_couverture VALUES (?,?,?,?,NULL,1)",
                   (ids_oeuvre[m["oeuvre"]], m["oeuvre"], m["atomes"], m["part_trop_courts"]))
    # Ligne de totaux, sans œuvre : c'est elle qui porte ce que la carte ne voit pas du tout.
    # `atomes` y compte des atomes DISTINCTS — c'était une somme de côtés d'acte, qui comptait
    # deux fois tout atome cité par deux actes et gonflait la couverture de 14,5 %.
    db.execute("INSERT INTO carte_couverture VALUES (NULL,NULL,?,NULL,?,0)",
               (cov["atomes_touches"], cov["part_touchee"]))

    # ---- usage des mots : chaque sous-concept de chaque lexique, mesuré sur tous les corpus
    # Déduite des ATOMES : une table bâtie sur les œuvres ignorerait Josef Breuer, qui est
    # auteur de passages sans être auteur d'un volume — et le mesurerait en français.
    langues_auteur = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)
    for u in comparaison.table_des_usages(par_auteur_atomes, langues_auteur):
        db.execute("INSERT INTO usages VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (u["sous_concept"], u["groupe"], u["libelle"], ids_auteur[u["lexique"]],
                    u["langue"], u["motif"], ids_auteur[u["auteur"]], u["atomes"],
                    u["porteurs"], u["pour_mille"]))

    lec = agents.AGENTS["lectures"].executer(corpus)
    for c in lec["chapitres_declares"]:
        db.execute(
            "INSERT INTO lectures_declarees (auteur_id, auteur_lu_id, oeuvre_id, chapitre,"
            " portee_atomes, homographe) VALUES (?,?,?,?,?,?)",
            (ids_auteur[c["auteur"]], ids_auteur[c["auteur_lu"]], ids_oeuvre[c["oeuvre"]],
             c["chapitre"], c["portee_atomes"], c["homographe"]))
    for n in lec["nominations"]:
        db.execute("INSERT INTO nominations VALUES (?,?,?,?)",
                   (ids_auteur[n["auteur"]], ids_auteur[n["auteur_nomme"]],
                    n["atomes"], n["homographe"]))

    # Les PASSAGES des mentions, un par un. La table `nominations` ci-dessus ne porte que des
    # comptes ; sans les passages, un lecteur ne peut pas vérifier une seule de ces 2 216
    # affirmations — et la doctrine du projet est qu'un chiffre non vérifiable ne vaut rien.
    for auteur, atomes in sorted(par_auteur_atomes.items()):
        for m in comparaison.mentions(atomes, auteur):
            aid = ids_atome.get(m["atome"]["id"])
            if aid is None:
                continue
            db.execute("INSERT INTO mentions VALUES (?,?,?,?)",
                       (aid, ids_auteur[auteur], ids_auteur[m["auteur_nomme"]], m["homographe"]))

    # ---- grappes (agent courants — déterministe, recalculé ici pour être fidèle au lexique)
    # Elles sont calculées sur les atomes de SIGMUND FREUD seul, et le resteront tant que la
    # couche de comparaison inter-auteurs n'existe pas. Ce n'est pas un oubli : une partition
    # calculée sur deux lexiques distincts mêlerait des concepts qui ne se répondent pas, et le
    # résultat n'aurait aucun sens interprétable. Chaque auteur aura ses propres courants le jour
    # où on les calculera séparément — c'est le travail suivant, explicitement déclaré.
    r = agents.AGENTS["courants"].executer(corpus)
    editorial = nommer_grappes(r["grappes"])      # échoue bruyamment si l'appariement a glissé
    for rang, g in enumerate(r["grappes"], 1):
        nom, description, reserve = editorial[rang]
        citation_id = g["citation"]["id"] if g.get("citation") else None
        cur = db.execute(
            "INSERT INTO grappes (rang, nom, description, reserve, taille, atomes_concernes,"
            " citation_atome_id) VALUES (?,?,?,?,?,?,?)",
            (rang, nom, description, reserve, g["taille"], g["atomes_concernes"], citation_id))
        for nom_c in g["concepts"]:
            db.execute("INSERT INTO grappe_concepts VALUES (?,?)",
                       (cur.lastrowid, ids_concept[("Sigmund Freud", nom_c)]))

    # ---- méta
    resume = corpus.resume()
    for cle, valeur in {
        "genere_le": datetime.date.today().isoformat(),
        "oeuvres": resume["oeuvres"], "atomes": resume["atomes"],
        "qualifies": resume["qualifies"], "signaux": resume["a_confirmer"],
        "modularite_grappes": r["modularite"],
        "licence": sources.LICENCE,
        "avertissement_datation": (
            "Un atome n'est jamais daté de l'année de l'œuvre : il porte une fenêtre "
            "[annee_min, annee_max]. Quatre œuvres sont collationnées avec leur première "
            "édition (couche origine/ajout) ; les autres portent la fenêtre de leur édition."),
    }.items():
        db.execute("INSERT INTO meta VALUES (?,?)", (cle, str(valeur)))

    db.commit()
    return db


def _sql_litteral(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def dumper_sql(db, dossier, taille_tranche=3_500_000):
    """Écrit 01_schema.sql + 02_donnees_NN.sql (tranches ≤ ~3,5 Mo pour `wrangler d1 execute`).

    Les INSERT sont groupés (40 lignes par ordre) : D1 exécute un fichier comme une suite
    d'ordres SQL, et 18 000 INSERT unitaires seraient inutilement lents à charger.
    """
    # Le schéma doit rester REJOUABLE sur une base déjà peuplée : chaque CREATE a son DROP.
    # Sans cela, un rechargement échoue à mi-parcours et laisse la base distante dans un état
    # mixte — c'est arrivé lors de l'ajout des tables de comparaison, dont les DROP manquaient.
    import re as _re
    crees = set(_re.findall(r"CREATE TABLE (\w+)", SCHEMA))
    supprimes = set(_re.findall(r"DROP TABLE IF EXISTS (\w+);", SCHEMA))
    if crees - supprimes:
        raise SystemExit(
            "SCHÉMA NON REJOUABLE — ces tables sont créées sans être supprimées d'abord : %s.\n"
            "Un rechargement sur une base déjà peuplée échouerait à mi-parcours et la laisserait "
            "incomplète. Ajouter le DROP correspondant en tête de SCHEMA." % ", ".join(sorted(crees - supprimes)))

    with open(os.path.join(dossier, "01_schema.sql"), "w", encoding="utf-8") as f:
        f.write("-- Schéma du corpus (généré par bin/exporter_d1.py — ne pas éditer)\n")
        f.write(SCHEMA.strip() + "\n")

    # ORDRE DE CHARGEMENT : les tables référencées d'abord, puisque D1 applique les clés
    # étrangères. L'ordre doit donc rester explicite ; en revanche, l'OUBLI d'une table ne doit
    # plus jamais être possible en silence.
    #
    # DÉFAUT RÉEL, corrigé ici : cette liste était figée, et l'ajout des trois tables de la
    # couche de comparaison ne l'a pas mise à jour. Le résultat était le pire qui soit — la base
    # locale contenait 132 liens, la base distante zéro, et RIEN ne le signalait : le site
    # affichait une section vide, ce qui se lit comme « le corpus n'a rien trouvé » alors que le
    # calcul avait abouti. D'où le contrôle ci-dessous, qui compare la liste au schéma réel et
    # fait ÉCHOUER l'export plutôt que de produire une base incomplète.
    tables = ["auteurs", "oeuvres", "concepts", "atomes", "atome_concepts",
              "atome_sous_concepts", "fonctions", "signaux", "grappes", "grappe_concepts",
              "liens_reprise", "lectures_declarees", "nominations", "usages",
              "mentions", "carte_actes", "carte_couples", "carte_couverture",
              "meta"]
    reelles = {r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    oubliees = reelles - set(tables)
    if oubliees:
        raise SystemExit(
            "TABLE(S) ABSENTE(S) DE L'EXPORT : %s.\n"
            "Elles existent dans le schéma mais ne seraient pas versées dans la base distante — "
            "le site les afficherait vides, sans qu'aucune erreur ne le signale. Ajouter chaque "
            "table à `tables` dans bin/exporter_d1.py, à sa place dans l'ordre des dépendances."
            % ", ".join(sorted(oubliees)))
    numero, tampon, taille = 1, [], 0
    chemins = []

    def flusher():
        nonlocal numero, tampon, taille
        if not tampon:
            return
        chemin = os.path.join(dossier, "02_donnees_%02d.sql" % numero)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(tampon) + "\n")
        chemins.append(chemin)
        numero, tampon, taille = numero + 1, [], 0

    for table in tables:
        colonnes = [c[1] for c in db.execute("PRAGMA table_info(%s)" % table)]
        lignes = db.execute("SELECT %s FROM %s" % (", ".join(colonnes), table)).fetchall()
        for i in range(0, len(lignes), 40):
            valeurs = ",\n".join("(" + ", ".join(_sql_litteral(v) for v in ligne) + ")"
                                 for ligne in lignes[i:i + 40])
            ordre = "INSERT INTO %s (%s) VALUES\n%s;" % (table, ", ".join(colonnes), valeurs)
            tampon.append(ordre)
            taille += len(ordre)
            if taille >= taille_tranche:
                flusher()
    flusher()
    return chemins


def main():
    os.makedirs(SORTIE, exist_ok=True)
    chemin_sqlite = os.path.join(SORTIE, "corpus.sqlite")
    print("construction de la base depuis le corpus…")
    db = construire(chemin_sqlite)
    print("dump SQL…")
    chemins = dumper_sql(db, SORTIE)
    n_atomes = db.execute("SELECT COUNT(*) FROM atomes").fetchone()[0]
    n_liens = db.execute("SELECT COUNT(*) FROM atome_concepts").fetchone()[0]
    db.close()
    print("→ %s (%d atomes, %d liens concept)" % (chemin_sqlite, n_atomes, n_liens))
    for c in [os.path.join(SORTIE, "01_schema.sql")] + chemins:
        print("→ %s (%.1f Mo)" % (c, os.path.getsize(c) / 1e6))


if __name__ == "__main__":
    main()
