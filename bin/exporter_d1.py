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

from core import agents, comparaison, lexique, ocr, sources, verification  # noqa: E402
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
}

# Éditorial des grappes (résumé de documentation/COURANTS_FREUD.md). L'agent `courants` ne
# nomme pas ses grappes ni ne les commente — ceci est une couche de PRÉSENTATION, raccrochée
# par concept SIGNATURE, et l'appariement est vérifié en bijection stricte par nommer_grappes()
# ci-dessous : un glissement de partition fait ÉCHOUER l'export, il ne produit jamais un
# libellé emprunté. La citation vedette, elle, n'est pas choisie ici : elle vient de l'agent
# lui-même (AgentCourants._decrire_grappe), pour que le site ne montre jamais un texte que le
# pipeline déterministe n'a pas produit.
EDITORIAL_GRAPPES = [
    ("traumarbeit", "Le rêve, l'appareil psychique et la représentation",
     "Le mécanisme du rêve (condensation, déplacement, censure) réuni à la métapsychologie qui "
     "l'explique — conscient, préconscient, inconscient, investissement, décharge — et à la "
     "REPRÉSENTATION, qui les relie. C'est la plus grosse grappe du corpus, et sa taille est "
     "elle-même un résultat : chez Freud, le rêve n'est pas un objet parmi d'autres, c'est le "
     "modèle sur lequel l'appareil psychique est pensé.",
     "49 concepts. L'APRÈS-COUP (« nachtraeglichkeit ») l'a rejointe à l'audit 8, ce qui est "
     "cohérent : un souvenir qui ne prend son sens que rétroactivement relève du même appareil "
     "que le rêve. Une grappe aussi large discrimine moins qu'une petite — elle dit un voisinage "
     "massif, pas une articulation fine."),
    ("libido", "La pulsion, la famille et le développement sexuel",
     "Libido, sexualité, stades du développement, perversion, narcissisme — noués au roman "
     "familial (père, mère, fratrie, Œdipe, castration) et aux instances (Moi, Ça, Sur-Moi). "
     "L'OBJET y figure depuis l'audit 8, et sa place n'est pas indifférente : c'est autour de lui "
     "que se recomposera, chez Abraham puis chez Klein, toute la théorie des relations d'objet.",
     "42 concepts. Cette grappe a FUSIONNÉ à l'audit 8 avec celle de la famille, que « objekt » "
     "et « knabe_maedchen » ont pontée — l'enfant sexué et l'objet du désir appartiennent au même "
     "voisinage. Une partition est un état de la mesure, pas une vérité sur Freud."),
    ("behandlung", "La clinique, le corps et la cure",
     "Hystérie, symptôme, angoisse, transfert, résistance ; la conversion, la paralysie, la "
     "douleur, l'état hypnoïde — et le corps que Freud DÉCRIT en même temps qu'il le traite. "
     "La mémoire y figure : « Hysterische leiden größtentheils an Reminiscenzen », écrivent "
     "Breuer et Freud en 1895. Se souvenir n'est pas ici une faculté, c'est le traitement même.",
     "La grappe doit beaucoup à une seule œuvre — « Studien über Hysterie », près de 3 000 atomes. "
     "Le CARACTÈRE l'a rejointe : chez Freud il se décrit au chevet du malade, non en théorie."),
    ("totem", "Religion, anthropologie, morale et lien social",
     "Le totémisme, le tabou, le sacrifice, le dieu ; l'interdit moral et la punition ; la masse "
     "et son meneur. La névrose obsessionnelle y voisine le religieux — rapprochement que Freud "
     "pose lui-même dès 1907 dans « Zwangshandlungen und Religionsübungen » : le cérémonial du "
     "névrosé et le rite du croyant ont la même structure.",
     "La TOUTE-PUISSANCE DES PENSÉES (« allmacht ») y est entrée à l'audit 8, à sa place exacte : "
     "Freud en fait le ressort commun de la magie, de l'animisme et de l'obsession."),
    ("dichter", "La fiction, le délire et la réalité",
     "Le poète, le récit, l'art, le fantasme et le délire — Freud lit la fiction avec les outils "
     "de la clinique, et le délire comme une œuvre. La RÉALITÉ y a rejoint le délire à l'audit 8, "
     "et le voisinage est parlant : ce qui définit le délire, c'est son rapport à elle.",
     "Grappe portée par les œuvres d'analyse littéraire (Gradiva, le Dichter, le Kästchenwahl) : "
     "elle décrit autant un GENRE d'écrit de Freud qu'un domaine de sa doctrine."),
    ("malerei", "La peinture et le pacte",
     "Trois concepts seulement, tirés de deux œuvres : le Léonard, le Moïse de Michel-Ange et la "
     "névrose démoniaque du peintre Haizmann.",
     "CONTRE-EXEMPLE À GARDER SOUS LA MAIN. « teufel » et « pakt » n'ont rien à faire avec la "
     "peinture — ils y sont parce que l'unique œuvre sur le diable porte sur un peintre. "
     "Cooccurrence réelle, lien conceptuel absent. « pakt » est de surcroît mono-œuvre."),
    ("verbrechen", "La faute et le crime",
     "Deux concepts : la culpabilité et le crime. Ils se sont détachés à l'audit 8, quand la "
     "morale et la punition sont parties vers la grappe religieuse — ce qui isole la faute "
     "SUBJECTIVE de l'interdit collectif qui la sanctionne.",
     "Grappe minuscule (192 atomes) : une séparation nette à ce niveau de finesse tient autant "
     "à la rareté des deux termes qu'à leur autonomie conceptuelle. À surveiller."),
    ("sadismus", "Sadisme, masochisme, agression",
     "Le couple sadisme/masochisme et l'agression, détachés en grappe propre à l'audit 8. C'est "
     "le voisinage le plus serré du corpus — Freud ne nomme presque jamais l'un sans l'autre.",
     "Grappe de trois concepts et 178 atomes. Son autonomie est un fait de mesure robuste "
     "(le couple ressort de l'agent `cooccurrence` depuis les toutes premières versions), mais "
     "sa petite taille la rend sensible au moindre changement de lexique."),
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
  partages TEXT                    -- suites de mots partagées, pour surligner à l'affichage
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
    par_auteur_atomes = {}
    for a in corpus.atomes:
        par_auteur_atomes.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
    index_ng = [comparaison._n_grammes_utiles(v, None) for v in par_auteur_atomes.values()]
    df_ng = comparaison.frequences_documentaires(index_ng)

    noms_auteurs = sorted(par_auteur_atomes)
    for i, x in enumerate(noms_auteurs):
        for y in noms_auteurs[i + 1:]:
            bruts = comparaison.reprises(par_auteur_atomes[x], par_auteur_atomes[y], df_ng)
            retenus = [comparaison.qualifier(l) for l in bruts
                       if l["contenance"] >= comparaison.SEUIL_PUBLICATION]
            if not retenus:
                continue
            # Les paires contiguës des deux côtés forment un seul ACTE de citation : c'est lui
            # qu'on compte, sans quoi celui qui cite par longs blocs paraîtrait le plus lié.
            for rang, evt in enumerate(comparaison.evenements(retenus), 1):
                for lien in evt["paires"]:
                    ida = ids_atome.get(lien["a"]["id"])
                    idb = ids_atome.get(lien["b"]["id"])
                    if ida is None or idb is None:
                        continue
                    db.execute(
                        "INSERT INTO liens_reprise (atome_a, atome_b, auteur_a, auteur_b,"
                        " contenance, force, sens, source_tierce, a_verifier, evenement, partages)"
                        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (ida, idb, ids_auteur[x], ids_auteur[y], lien["contenance"],
                         lien["force"], lien["sens"], int(lien["source_tierce"]),
                         int(lien["a_verifier"]), rang, " | ".join(lien["partages"][:6])))

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
              "liens_reprise", "lectures_declarees", "nominations", "meta"]
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
