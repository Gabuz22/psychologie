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

from core import agents, lexique, sources, verification     # noqa: E402
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
     "44 concepts : cette grappe a FUSIONNÉ avec celle de l'appareil psychique à l'audit 7, "
     "quand « Vorstellung » (763 occurrences) est entré dans l'ontologie et a ponté les deux. "
     "Une grappe aussi large discrimine moins qu'une petite : elle dit un voisinage massif, pas "
     "une articulation fine."),
    ("behandlung", "La clinique, le corps et la cure",
     "Hystérie, symptôme, angoisse, transfert, résistance ; la conversion, la paralysie, la "
     "douleur, l'état hypnoïde — et le corps que Freud DÉCRIT en même temps qu'il le traite. "
     "La mémoire y figure : « Hysterische leiden größtentheils an Reminiscenzen », écrivent "
     "Breuer et Freud en 1895. Se souvenir n'est pas ici une faculté, c'est le traitement même.",
     "Le corps décrit (main, œil, visage, barbe) y a été absorbé à l'audit 7, après avoir formé "
     "sa propre grappe : le vocabulaire clinique ajouté l'a rapproché du corps soigné. La grappe "
     "doit par ailleurs beaucoup à une seule œuvre — « Studien über Hysterie », 2 909 atomes."),
    ("kastration", "La famille, la différence des sexes et la mort",
     "Le roman familial (père, mère, fratrie, Œdipe) noué au complexe de castration, à "
     "l'opposition masculin/féminin, à la mort et à la culpabilité — la constellation que Freud "
     "tient pour l'origine commune du symptôme, du mythe et du lien social.",
     "La différence des sexes n'a rejoint cette grappe qu'à l'audit 4 du lexique (2026-07) : "
     "avant cela, 526 occurrences dans 17 œuvres étaient invisibles."),
    ("totem", "Religion, anthropologie, morale et lien social",
     "Le totémisme, le tabou, le sacrifice, le dieu ; l'interdit moral et la punition ; la masse "
     "et son meneur. La NÉVROSE OBSESSIONNELLE y a rejoint le religieux à l'audit 7 — voisinage "
     "que Freud pose lui-même dès 1907 dans « Zwangshandlungen und Religionsübungen » : le "
     "cérémonial du névrosé et le rite du croyant ont la même structure.",
     "Le rapprochement science/religion, quand il apparaît, est un fait de COOCCURRENCE : Freud "
     "oppose souvent les deux, et deux termes opposés dans un même énoncé voisinent autant que "
     "deux termes alliés."),
    ("libido", "La pulsion, le développement sexuel et les instances",
     "Libido, sexualité, perversion, stades du développement, destins de la pulsion "
     "(sublimation, formation réactionnelle) — et la seconde topique (Moi, Ça, Sur-Moi) avec la "
     "conscience morale.",
     "Cette grappe a changé de composition à chacun des quatre derniers audits : la seconde "
     "topique l'a rejointe, quittée, puis reprise. Une grappe est un état de la mesure, pas une "
     "vérité sur Freud. Le Sur-Moi reste sous-représenté faute de « Das Ich und das Es » (1923), "
     "absent du corpus."),
    ("dichter", "La fiction, le délire et la création",
     "Le poète, le récit, l'art, le fantasme et le délire — Freud lit la fiction avec les outils "
     "de la clinique, et le délire comme une œuvre. La grappe s'est détachée quand le corpus a "
     "gagné assez de matière clinique réelle pour que les deux se distinguent.",
     "Grappe portée par les œuvres d'analyse littéraire (Gradiva, le Dichter, le Kästchenwahl) : "
     "elle décrit autant un GENRE d'écrit de Freud qu'un domaine de sa doctrine."),
    ("malerei", "La peinture et le pacte",
     "Les analyses d'œuvres visuelles du corpus (Léonard, le Moïse de Michel-Ange, le peintre "
     "possédé de la Teufelsneurose) — et le pacte signé du sang, sujet de cette dernière.",
     "Contient l'artefact le plus instructif du découpage : « Teufel » et « pakt » n'ont rien à "
     "faire avec la peinture — ils y sont parce que l'unique œuvre sur le diable porte sur un "
     "peintre. Cooccurrence réelle, lien conceptuel absent : le contre-exemple à garder sous la "
     "main. « pakt » est de surcroît un concept mono-œuvre à ce jour."),
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
  collationnee INTEGER NOT NULL
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
  datation_regle TEXT NOT NULL
);
CREATE TABLE concepts (
  id INTEGER PRIMARY KEY,
  nom TEXT NOT NULL UNIQUE,
  groupe TEXT NOT NULL,
  n_atomes INTEGER NOT NULL DEFAULT 0
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
        cur = db.execute(
            "INSERT INTO oeuvres (cle, titre, titre_fr, langue, auteur_id, annee_oeuvre,"
            " annee_edition, edition, editeur, source, url, datation_regle, datation_precise,"
            " collationnee) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cle, src["titre"], src.get("titre_fr"), src.get("langue", "de"),
             # L'auteur du VOLUME vient du registre — plus forcément Freud depuis Le Bon.
             ids_auteur[src.get("auteur", "Sigmund Freud")],
             src["annee_oeuvre"], src["annee_edition"], src.get("edition"), src.get("editeur"),
             src.get("source"), src.get("url"), d["regle"], int(d["precise"]), int(collationnee)))
        ids_oeuvre[cle] = cur.lastrowid

    # ---- concepts (référentiel complet du lexique, même à zéro atome)
    ids_concept = {}
    for groupe, meta in lexique.CONCEPTS.items():
        for nom in meta["termes"]:
            cur = db.execute("INSERT INTO concepts (nom, groupe) VALUES (?,?)", (nom, groupe))
            ids_concept[nom] = cur.lastrowid

    # ---- atomes et jointures
    table_verdicts = verification.charger()["verdicts"]
    for a in corpus.atomes:
        ch = a["chapitre"]
        amin, amax = fenetre_datation(a)
        cur = db.execute(
            "INSERT INTO atomes (atome_id, empreinte, oeuvre_id, auteur_id, idx, texte,"
            " texte_replie, debut, fin, nb_mots, chapitre, statut, non_qualifie, couche,"
            " annee_min, annee_max, datation_regle) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["id"], a["empreinte"], ids_oeuvre[a["oeuvre"]],
             ids_auteur[a.get("auteur", "Sigmund Freud")], a["index"], a["texte"],
             replier(a["texte"]), a["debut"], a["fin"], a["nb_mots"],
             ("%s. %s" % (ch["numero"], ch["titre"])) if ch else None,
             a["statut"], int(a["non_qualifie"]), a["attestation"].get("couche"),
             amin, amax, a["attestation"]["regle"]))
        aid = cur.lastrowid
        for c in a["concepts"]:
            db.execute("INSERT OR IGNORE INTO atome_concepts VALUES (?,?)",
                       (aid, ids_concept[c["concept"]]))
            for sc in c.get("sous_concepts", []):
                db.execute("INSERT INTO atome_sous_concepts VALUES (?,?,?)",
                           (aid, ids_concept[c["concept"]], sc))
        for f in a["fonctions"]:
            db.execute("INSERT INTO fonctions VALUES (?,?)", (aid, f))
        for s in a["signaux_a_confirmer"]:
            j = table_verdicts.get(a["empreinte"])
            verdict = j["verdict"] if j and j.get("signal") == s else None
            motif = j["motif"] if j and j.get("signal") == s else None
            db.execute("INSERT INTO signaux VALUES (?,?,?,?)", (aid, s, verdict, motif))

    db.execute("UPDATE concepts SET n_atomes ="
               " (SELECT COUNT(*) FROM atome_concepts ac WHERE ac.concept_id = concepts.id)")

    # ---- grappes (agent courants — déterministe, recalculé ici pour être fidèle au lexique)
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
                       (cur.lastrowid, ids_concept[nom_c]))

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
    with open(os.path.join(dossier, "01_schema.sql"), "w", encoding="utf-8") as f:
        f.write("-- Schéma du corpus (généré par bin/exporter_d1.py — ne pas éditer)\n")
        f.write(SCHEMA.strip() + "\n")

    tables = ["auteurs", "oeuvres", "concepts", "atomes", "atome_concepts",
              "atome_sous_concepts", "fonctions", "signaux", "grappes", "grappe_concepts",
              "meta"]
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
