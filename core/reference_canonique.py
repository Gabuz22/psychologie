#!/usr/bin/env python3
"""Registre déterministe des références du projet et contrôles de synchronisation.

Ce module décrit plusieurs couches qui font foi chacune dans leur périmètre. Il n'élit pas le
prototype v2 à la place de D1, ne régénère aucune donnée et ouvre l'export SQLite en lecture seule.
L'observation du site public est un instantané versionné : aucune requête réseau n'intervient dans
la génération ou la validation.
"""
import copy
import hashlib
import json
import os
import re
import sqlite3
import subprocess

from . import audit_relations


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_VERSION = "1.0.0"
DATE_VERIFICATION = "2026-08-04"
STATUTS = {
    "canonique historique", "canonique courant", "expérimental", "dérivé",
    "obsolète", "inconnu", "à décider",
}


def _absolu(relatif, racine=RACINE):
    return os.path.join(racine, *relatif.split("/"))


def _charger_json(relatif, racine=RACINE):
    with open(_absolu(relatif, racine), encoding="utf-8") as f:
        return json.load(f)


def _sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def _empreinte_artefacts(chemins, racine=RACINE):
    contenu = []
    for relatif in sorted(chemins):
        chemin = _absolu(relatif, racine)
        contenu.append({"chemin": relatif, "sha256": _sha256(chemin)})
    brut = json.dumps(contenu, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(brut).hexdigest(), contenu


def _dernier_commit(relatif):
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", relatif], cwd=RACINE,
        text=True, encoding="utf-8").strip() or "inconnu"


def _compter_tests(racine=RACINE):
    motif_python = re.compile(r"^\s*def test_", re.M)
    motif_worker = re.compile(r"^\s*(?:test|it)\s*\(", re.M)
    python, worker, fichiers_python, fichiers_worker = 0, 0, [], []
    tests = _absolu("core/tests", racine)
    for nom in sorted(os.listdir(tests)):
        if nom.startswith("test_") and nom.endswith(".py"):
            relatif = "core/tests/" + nom
            with open(_absolu(relatif, racine), encoding="utf-8") as f:
                n = len(motif_python.findall(f.read()))
            python += n
            fichiers_python.append({"chemin": relatif, "tests": n})
    worker_dir = _absolu("web/worker", racine)
    for nom in sorted(os.listdir(worker_dir)):
        if nom.endswith(".test.js"):
            relatif = "web/worker/" + nom
            with open(_absolu(relatif, racine), encoding="utf-8") as f:
                n = len(motif_worker.findall(f.read()))
            worker += n
            fichiers_worker.append({"chemin": relatif, "tests": n})
    return {
        "python": python, "worker": worker,
        "fichiers_python": fichiers_python, "fichiers_worker": fichiers_worker,
        "execution": "présence vérifiée ; exécution à consigner séparément",
    }


def _faits_d1(relatif="derive/d1/corpus.sqlite", racine=RACINE):
    chemin = os.path.abspath(_absolu(relatif, racine))
    db = sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)
    try:
        meta = {r[0]: r[1] for r in db.execute("SELECT cle, valeur FROM meta")}
        colonnes_actes = {r[1] for r in db.execute("PRAGMA table_info(carte_actes)")}
        acte96 = db.execute(
            "SELECT id, verdict, sens_lu, reclasse_vers FROM carte_actes WHERE id=96").fetchone()
        audit = audit_relations.auditer_connexion(db)
        constats = {c["code"]: c for c in audit["constats"]}
        return {
            "genere_le": meta.get("genere_le", "inconnu"),
            "schema": "d1-v1-historique",
            "versions_regles_dans_export": "inconnues",
            "comptes": {
                "atomes": db.execute("SELECT COUNT(*) FROM atomes").fetchone()[0],
                "oeuvres": db.execute("SELECT COUNT(*) FROM oeuvres").fetchone()[0],
                "auteurs": db.execute("SELECT COUNT(*) FROM auteurs").fetchone()[0],
                "qualifies": db.execute(
                    "SELECT COUNT(*) FROM atomes WHERE non_qualifie=0").fetchone()[0],
                "traductions_appliquees": db.execute(
                    "SELECT COUNT(*) FROM atomes WHERE texte_fr IS NOT NULL").fetchone()[0],
                "liens_reprise": db.execute("SELECT COUNT(*) FROM liens_reprise").fetchone()[0],
                "carte_actes": db.execute("SELECT COUNT(*) FROM carte_actes").fetchone()[0],
                "mentions": db.execute("SELECT COUNT(*) FROM mentions").fetchone()[0],
                "lectures_declarees": db.execute(
                    "SELECT COUNT(*) FROM lectures_declarees").fetchone()[0],
                "concept_liens": db.execute("SELECT COUNT(*) FROM concept_liens").fetchone()[0],
                "grappes": db.execute("SELECT COUNT(*) FROM grappes").fetchone()[0],
                "signaux": db.execute("SELECT COUNT(*) FROM signaux").fetchone()[0],
                "signaux_juges": db.execute(
                    "SELECT COUNT(*) FROM signaux WHERE verdict IS NOT NULL").fetchone()[0],
                "signaux_confirmes": db.execute(
                    "SELECT COUNT(*) FROM signaux WHERE verdict='confirme'").fetchone()[0],
            },
            "colonnes_actes_v2_absentes": not {
                "etat_validation", "verdicts_elementaires"} <= colonnes_actes,
            "acte_96": {
                "present": bool(acte96),
                "verdict_historique": acte96[1] if acte96 else None,
                "sens_lu": acte96[2] if acte96 else None,
                "reclasse_vers": acte96[3] if acte96 else None,
                "etat_interprete_sans_modifier_d1": "discordant" if acte96 and not acte96[1]
                    and acte96[2] and acte96[3] else "inconnu",
            },
            "audit_relations_ok": audit["ok"],
            "actes_non_lus": constats["actes_non_lus"]["nombre"],
            "actes_discordants": constats["actes_validation_discordante"]["nombre"],
        }
    finally:
        db.close()


def _reference(identifiant, role, chemins, commit_git, corpus_version, versions_regles,
               statut, compatibilites, incompatibilites, limites, racine=RACINE):
    empreinte, artefacts = _empreinte_artefacts(chemins, racine)
    return {
        "id": identifiant,
        "role": role,
        "artefacts": artefacts,
        "empreinte_artefacts": empreinte,
        "commit_git": commit_git,
        "version_corpus": corpus_version,
        "versions_regles": versions_regles,
        "statut": statut,
        "compatibilites": compatibilites,
        "incompatibilites": incompatibilites,
        "limites": limites,
        "verifie_le": DATE_VERIFICATION,
        "methode_verification": "empreintes SHA-256, lecture structurée et contrôles locaux",
    }


def construire(racine=RACINE):
    """Construit le registre sans écrire, migrer, réatomiser ni interroger le réseau."""
    manifeste = _charger_json("manifests/corpus_actuel.json", racine)
    observation = _charger_json("manifests/site_public_observe_2026-08-04.json", racine)
    homonymes = _charger_json(
        "prototypes/relations_v2/candidats_translexicaux.json", racine)
    prototype = _charger_json(
        "prototypes/relations_v2/registre_probatoire_freud_stekel.json", racine)
    experience = _charger_json(
        "prototypes/relations_v2/experience_freud_stekel.json", racine)
    migration = _charger_json(
        "prototypes/relations_v2/migration_dry_run.json", racine)
    d1 = _faits_d1(racine=racine)
    tests = _compter_tests(racine)
    corpus_version = manifeste["versions"]["corpus_source"]
    export_sha = manifeste["reference"]["export_sha256"]

    relations_humaines = sum(
        1 for relation in prototype["relations"]
        for annotation in relation.get("annotations", [])
        if annotation.get("agent_kind") == "humain")
    equivalences = sum(len(c.get("propositions_equivalence", []))
                       for c in homonymes["candidats"])

    fondations = [
        "schemas/objets_analytiques_v2.json", "schemas/relations_v2.schema.json",
        "schemas/relations_v2.sql", "schemas/relations_v2_rollback.sql",
        "core/relations_v2.py", "documentation/SCHEMA_CANONIQUE_OBJETS_V2.md",
        "documentation/MODELE_RELATIONS_MULTIPLES_V2.md",
    ]
    docs = [
        "README.md", "documentation/REFERENCE_CANONIQUE.md",
        "documentation/PROTOCOLE_VALIDATION_RELATIONS.md",
        "documentation/ACTE_96_VERDICT_DISCORDANT.md",
    ]
    site = ["web/site/index.html", "web/site/app.js", "web/site/style.css",
            "web/worker/donnees.js"]

    references = [
        _reference(
            "d1-historique-2026-08-03", "export relationnel et textuel v1 gelé",
            ["derive/d1/corpus.sqlite"], manifeste["reference"]["commit_git"],
            corpus_version, manifeste["versions"]["enregistrees_dans_export"],
            "canonique historique",
            ["API v1", "manifeste corpus_actuel", "prototype v2 par migration additive"],
            ["ne contient aucune table v2", "versions de règles absentes de meta"],
            ["ne pas réécrire", "acte 96 stocké avec verdict NULL", "traductions pilotes"], racine),
        _reference(
            "manifeste-corpus-actuel", "gel vérifiable de D1, des sources et des registres",
            ["manifests/corpus_actuel.json"], _dernier_commit("manifests/corpus_actuel.json"),
            corpus_version, manifeste["versions"]["regles_code_lu"],
            "canonique courant", ["D1 historique au SHA-256 " + export_sha],
            ["les versions lues dans le code ne deviennent pas les versions historiques de D1"],
            ["14 alertes documentaires sont des candidats heuristiques", "scope traduction vide"],
            racine),
        _reference(
            "regles-d1-historiques", "versions réellement embarquées dans l'export historique",
            ["derive/d1/corpus.sqlite"], manifeste["reference"]["commit_git"],
            corpus_version, manifeste["versions"]["enregistrees_dans_export"],
            "inconnu", ["les résultats historiques restent lisibles et intègres"],
            ["ne pas substituer automatiquement les versions du code courant"],
            ["empreinte des sources et versions absentes de meta"], racine),
        _reference(
            "fondations-relations-v2", "contrats canoniques proposés pour objets et relations",
            fondations, _dernier_commit("schemas/relations_v2.schema.json"), corpus_version,
            {"relations_v2": "0.1.0"}, "expérimental",
            ["migration additive sur nouvelle base", "D1 conservé comme source historique"],
            ["non déployé", "aucune validation humaine produite"],
            ["proposition exécutable, pas doctrine adoptée"], racine),
        _reference(
            "prototype-freud-stekel-v1", "registre probatoire et expérience aveugle préparée",
            ["prototypes/relations_v2/registre_probatoire_freud_stekel.json",
             "prototypes/relations_v2/experience_freud_stekel.json"],
            _dernier_commit("prototypes/relations_v2/registre_probatoire_freud_stekel.json"),
            corpus_version, manifeste["versions"]["regles_code_lu"], "expérimental",
            ["20 candidats gelés", "60 contrôles", "29 relations proposées/rejetées"],
            ["ne constitue pas une vérité terrain", "ne remplace pas les 135 actes D1"],
            ["zéro annotation humaine", "précision et rappel non calculables"], racine),
        _reference(
            "homonymes-translexicaux-v1", "registre de libellés partagés entre lexiques",
            ["prototypes/relations_v2/candidats_translexicaux.json"],
            _dernier_commit("prototypes/relations_v2/candidats_translexicaux.json"),
            corpus_version, {"registre": homonymes["schema_version"]}, "expérimental",
            ["mesures lexicales D1", "schéma d'alignement v2"],
            ["aucune équivalence conceptuelle automatique"],
            ["96 homonymes non examinés humainement"], racine),
        _reference(
            "migration-v2-additive", "simulation d'import v2 sur une base séparée",
            ["schemas/relations_v2.sql", "schemas/relations_v2_rollback.sql",
             "prototypes/relations_v2/migration_dry_run.json",
             "core/migration_relations_v2.py", "bin/migrer_relations_v2.py"],
            _dernier_commit("prototypes/relations_v2/migration_dry_run.json"),
            corpus_version, {"migration": migration["schema_version"]}, "expérimental",
            ["source D1 vérifiée par SHA", "rollback limité aux tables v2"],
            ["jamais appliquée à D1", "acte 96 non convertible automatiquement"],
            ["dry-run uniquement dans le dépôt"], racine),
        _reference(
            "site-source-courant", "interface et API préparées dans le dépôt",
            site, "SELF", corpus_version, {"api": "v1", "site": "sans build"},
            "canonique courant", ["D1 v1", "état canonique statique généré"],
            ["ne rend pas les tables v2 utilisables", "n'établit aucune équivalence"],
            ["source locale non déployée par cette consolidation"], racine),
        _reference(
            "site-public-observe-2026-08-04", "instantané daté de l'état effectivement publié",
            ["manifests/site_public_observe_2026-08-04.json"], "inconnu",
            observation["api"]["version_corpus_observee"], {"api": "v1"}, "dérivé",
            ["comptes 116545/57/7 compatibles avec D1"],
            ["base publique datée du 2026-08-02", "traductions et v2 absentes"],
            ["commit de déploiement inconnu", "observation non dynamique"], racine),
        _reference(
            "documentation-courante", "explication technique et méthodologique synchronisée",
            docs, "SELF", corpus_version, manifeste["versions"]["regles_code_lu"],
            "canonique courant", ["registre canonique", "rapport de synchronisation"],
            ["les rapports datés antérieurs restent des photographies historiques"],
            ["les verdicts legacy ne sont pas une validation humaine indépendante"], racine),
    ]

    registre = {
        "schema_registre": SCHEMA_VERSION,
        "id": "psychologie-references-canoniques",
        "verifie_le": DATE_VERIFICATION,
        "methode": [
            "lecture du manifeste et des schémas versionnés",
            "ouverture SQLite en mode lecture seule",
            "vérification SHA-256 des artefacts",
            "comptage statique des tests présents",
            "comparaison à un instantané public daté et versionné",
        ],
        "semantique_statuts": {
            "canonique historique": "fait foi pour un résultat gelé, sans être le modèle courant",
            "canonique courant": "fait foi dans le dépôt pour sa couche propre",
            "expérimental": "préparé et testable, sans adoption ni validation humaine implicite",
            "dérivé": "produit à partir d'une autre couche ou observé extérieurement",
            "obsolète": "conservé pour histoire, à ne pas citer comme état courant",
            "inconnu": "information non enregistrée ou non déterminable",
            "à décider": "décision humaine ou scientifique requise",
        },
        "faits": {
            "d1": d1,
            "sources": {
                "fichiers_et_temoins": len(manifeste["fichiers"]),
                "textes_citables": sum(f["role"] == "texte_source"
                                        for f in manifeste["fichiers"]),
                "temoins_non_citables": sum(f["role"] == "temoin_collation_non_citable"
                                             for f in manifeste["fichiers"]),
            },
            "v2": {
                "statut": "expérimental",
                "relations_prototype": len(prototype["relations"]),
                "annotations_humaines_prototype": len(prototype["human_annotations"]),
                "annotations_de_type_humain_dans_relations": relations_humaines,
                "items_aveugles": len(experience["blind_items"]),
                "annotations_humaines_experience": len(experience["human_annotations"]),
                "precision_rappel": experience["automatic_preliminary_results"]["precision_rappel"],
                "homonymes_translexicaux": len(homonymes["candidats"]),
                "propositions_equivalence": equivalences,
                "migration_mode": migration["mode"],
            },
            "tests": tests,
            "site_public_observe": observation,
        },
        "references": references,
    }
    registre["validation"] = valider(registre, racine)
    return registre


def etat_site(registre):
    """Sous-ensemble publiable : transparence, jamais nouvelle fonctionnalité analytique."""
    d1 = registre["faits"]["d1"]
    v2 = registre["faits"]["v2"]
    return {
        "schema": "etat-canonique-site-1.0.0",
        "source": "manifests/references_canoniques.json",
        "verifie_le": registre["verifie_le"],
        "d1": {
            "statut": "canonique historique",
            "genere_le": d1["genere_le"],
            "comptes": d1["comptes"],
            "versions_regles_dans_export": d1["versions_regles_dans_export"],
            "acte_96": d1["acte_96"],
        },
        "v2": v2,
        "tests_presents": {
            "python": registre["faits"]["tests"]["python"],
            "worker": registre["faits"]["tests"]["worker"],
            "reserve": registre["faits"]["tests"]["execution"],
        },
        "reserve": (
            "Les fondations v2 sont expérimentales et ne remplacent pas D1. Une proposition "
            "automatique n'est pas une validation humaine."
        ),
    }


def valider(registre, racine=RACINE):
    erreurs, avertissements = [], []
    for reference in registre.get("references", []):
        if reference.get("statut") not in STATUTS:
            erreurs.append({"code": "statut_inconnu", "reference": reference.get("id")})
        for artefact in reference.get("artefacts", []):
            chemin = _absolu(artefact["chemin"], racine)
            if not os.path.exists(chemin):
                erreurs.append({"code": "artefact_absent", "reference": reference["id"],
                                "chemin": artefact["chemin"]})
            elif _sha256(chemin) != artefact["sha256"]:
                erreurs.append({"code": "artefact_modifie", "reference": reference["id"],
                                "chemin": artefact["chemin"]})
    par_id = {r["id"]: r for r in registre.get("references", [])}
    if par_id.get("d1-historique-2026-08-03", {}).get("statut") != "canonique historique":
        erreurs.append({"code": "d1_non_historique"})
    for identifiant in ("fondations-relations-v2", "prototype-freud-stekel-v1",
                        "migration-v2-additive", "homonymes-translexicaux-v1"):
        if par_id.get(identifiant, {}).get("statut") != "expérimental":
            erreurs.append({"code": "v2_non_experimental", "reference": identifiant})
    v2 = registre.get("faits", {}).get("v2", {})
    if v2.get("annotations_humaines_prototype") or v2.get(
            "annotations_de_type_humain_dans_relations") or v2.get(
            "annotations_humaines_experience"):
        erreurs.append({"code": "promotion_validation_humaine"})
    if v2.get("propositions_equivalence"):
        erreurs.append({"code": "equivalence_automatique"})
    d1 = registre.get("faits", {}).get("d1", {})
    if d1.get("acte_96", {}).get("etat_interprete_sans_modifier_d1") != "discordant":
        erreurs.append({"code": "acte_96_non_discordant"})
    attendus = {"atomes": 116545, "oeuvres": 57, "auteurs": 7,
                "liens_reprise": 507, "carte_actes": 354,
                "mentions": 2899, "concept_liens": 7646, "grappes": 8}
    observes = d1.get("comptes", {})
    for cle, attendu in attendus.items():
        if observes.get(cle) != attendu:
            erreurs.append({"code": "non_regression_d1", "champ": cle,
                            "attendu": attendu, "observe": observes.get(cle)})
    if d1.get("versions_regles_dans_export") == "inconnues":
        avertissements.append({"code": "versions_d1_historiques_inconnues"})
    if registre.get("faits", {}).get("site_public_observe", {}).get(
            "deploiement", {}).get("commit_git") == "inconnu":
        avertissements.append({"code": "commit_site_public_inconnu"})
    return {"ok": not erreurs, "erreurs": erreurs, "avertissements": avertissements}


def verifier_declarations(registre, racine=RACINE, textes=None):
    """Vérifie les déclarations courantes ; les documents historiques sont seulement étiquetés."""
    erreurs = []
    textes = textes or {}

    def lire(relatif):
        if relatif in textes:
            return textes[relatif]
        with open(_absolu(relatif, racine), encoding="utf-8") as f:
            return f.read()

    d1 = registre["faits"]["d1"]["comptes"]
    tests = registre["faits"]["tests"]
    exigences = {
        "README.md": [
            "**%s atomes**" % f"{d1['atomes']:,}".replace(",", " "),
            "%s tests Python" % tests["python"], "%s tests Worker" % tests["worker"],
            "%s signaux" % d1["signaux"], "%s actes" % d1["carte_actes"],
            "référence canonique",
        ],
        "web/site/index.html": [
            'id="transparence"', "57 volumes", "354 actes", "290 verdicts legacy confirmés",
            "96 homonymes translexicaux", "agrégat discordant",
        ],
        "web/site/app.js": ["etat-canonique.json", "rendreEtatCanonique"],
    }
    interdits = {
        "README.md": ["110 tests", "les 214 signaux du corpus actuel",
                      "Vérification faite pour les 214 signaux"],
        "web/site/index.html": ["107 actes réels", "191 confirmés", "quarante œuvres",
                                "<strong>Aucune traduction</strong>", "validées par lecture"],
        "web/worker/donnees.js": ["moins d'un demi pour cent du corpus"],
    }
    for relatif, fragments in exigences.items():
        texte = lire(relatif)
        for fragment in fragments:
            if fragment not in texte:
                erreurs.append({"code": "declaration_absente", "fichier": relatif,
                                "fragment": fragment})
    for relatif, fragments in interdits.items():
        texte = lire(relatif)
        for fragment in fragments:
            if fragment in texte:
                erreurs.append({"code": "declaration_obsolete", "fichier": relatif,
                                "fragment": fragment})
    historiques = [
        "documentation/CARTE_CITATIONS.md", "documentation/COUVERTURE_MESUREE.md",
        "documentation/POUR_LES_CHERCHEURS.md", "documentation/SYNTHESE_FREUD.md",
        "documentation/INVENTAIRE_ATOMES.md", "documentation/CHAPITRAGE.md",
        "documentation/TRADUCTION.md",
    ]
    for relatif in historiques:
        debut = lire(relatif)[:700]
        if "État documentaire : photographie historique" not in debut:
            erreurs.append({"code": "document_historique_non_signale", "fichier": relatif})
    return erreurs


def verifier_registre_existant(relatif="manifests/references_canoniques.json", racine=RACINE):
    existant = _charger_json(relatif, racine)
    erreurs = list(valider(existant, racine)["erreurs"])
    erreurs.extend(verifier_declarations(existant, racine))
    attendu = construire(racine)
    if json_canonique(existant) != json_canonique(attendu):
        erreurs.append({"code": "registre_desynchronise", "fichier": relatif})
    etat_attendu = json_canonique(etat_site(attendu))
    with open(_absolu("web/site/etat-canonique.json", racine), encoding="utf-8") as f:
        if f.read() != etat_attendu:
            erreurs.append({"code": "etat_site_desynchronise",
                            "fichier": "web/site/etat-canonique.json"})
    return {"ok": not erreurs, "erreurs": erreurs,
            "avertissements": attendu["validation"]["avertissements"]}


def rapport_markdown(registre, verification):
    etat = "CONFORME" if verification["ok"] else "DÉSYNCHRONISÉ"
    lignes = [
        "# Rapport de synchronisation — %s" % registre["verifie_le"], "",
        "**Résultat : %s.**" % etat, "",
        "Ce rapport contrôle des artefacts existants. Il ne régénère ni D1, ni graphe, ni relation,",
        "et n'applique aucune migration.", "", "## Références", "",
        "| Identifiant | Statut | Commit | Empreinte |",
        "|---|---|---|---|",
    ]
    for r in registre["references"]:
        lignes.append("| `%s` | %s | `%s` | `%s` |" % (
            r["id"], r["statut"], r["commit_git"][:12], r["empreinte_artefacts"][:16]))
    d1 = registre["faits"]["d1"]
    v2 = registre["faits"]["v2"]
    t = registre["faits"]["tests"]
    lignes += [
        "", "## Contrôles structurants", "",
        "- D1 : %s atomes, %s œuvres, %s auteurs, %s liens, %s actes." % (
            d1["comptes"]["atomes"], d1["comptes"]["oeuvres"], d1["comptes"]["auteurs"],
            d1["comptes"]["liens_reprise"], d1["comptes"]["carte_actes"]),
        "- Acte 96 : `%s` ; aucun verdict unique fabriqué." %
        d1["acte_96"]["etat_interprete_sans_modifier_d1"],
        "- V2 : `%s`, %s annotation humaine dans le prototype et %s dans l'expérience." % (
            v2["statut"], v2["annotations_humaines_prototype"],
            v2["annotations_humaines_experience"]),
        "- Homonymes : %s ; propositions d'équivalence : %s." % (
            v2["homonymes_translexicaux"], v2["propositions_equivalence"]),
        "- Tests présents : %s Python et %s Worker ; présence distincte de l'exécution." % (
            t["python"], t["worker"]), "",
        "## Erreurs", "",
    ]
    if verification["erreurs"]:
        lignes.extend("- `%s` — %s" % (e["code"], json.dumps(e, ensure_ascii=False,
                                                              sort_keys=True))
                      for e in verification["erreurs"])
    else:
        lignes.append("- Aucune.")
    lignes += ["", "## Avertissements", ""]
    if verification["avertissements"]:
        lignes.extend("- `%s`" % a["code"] for a in verification["avertissements"])
    else:
        lignes.append("- Aucun.")
    lignes += ["", "## Limites", "",
               "- Le commit du déploiement public demeure inconnu.",
               "- Les versions de règles du D1 historique ne sont pas enregistrées dans sa table `meta`.",
               "- Les résultats v2 restent automatiques ou legacy ; aucune campagne humaine n'a commencé.",
               ""]
    return "\n".join(lignes)


def json_canonique(valeur):
    return json.dumps(valeur, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def copie_avec_artefact_absent(registre, chemin="absent/factice.json"):
    """Aide de test : ne modifie jamais le registre reçu."""
    copie = copy.deepcopy(registre)
    copie["references"][0]["artefacts"].append({"chemin": chemin, "sha256": "0" * 64})
    return copie
