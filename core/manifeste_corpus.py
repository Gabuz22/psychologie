#!/usr/bin/env python3
"""Gel déterministe du corpus et contrôles de cohérence associés.

Le manifeste décrit un export existant ; il ne réatomise pas les textes et ne complète aucune
métadonnée absente. Les chemins sont relatifs, les listes triées et aucun horodatage mural n'est
ajouté : deux générations sur le même état produisent exactement les mêmes octets JSON.
"""
import hashlib
import json
import os
import re
import sqlite3
import subprocess

from . import (atomisation, carte, collation, comparaison, lexique, lexiques,
               socle_par_couple, sources)

MANIFESTE_SCHEMA_VERSION = "1.0.0"
EXPORT_SCHEMA_VERSION = "d1-v1"
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def _relatif(chemin):
    return os.path.relpath(chemin, RACINE).replace(os.sep, "/")


def _hash_json(valeur):
    brut = json.dumps(valeur, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(brut).hexdigest()


def _inconnu(raison):
    return {"statut": "inconnu", "valeur": None, "raison": raison}


def _git_revision(reference):
    return subprocess.check_output(
        ["git", "rev-parse", "--verify", reference], cwd=RACINE,
        text=True, encoding="utf-8").strip()


def fichiers_sources():
    """Entrées textuelles citées et témoins de collation, avec empreinte complète."""
    entrees = []
    references = set()
    for cle, meta in sorted(sources.OEUVRES.items()):
        dossier = (os.path.join(sources.DOSSIER_SOURCES, *meta["dossier"])
                   if meta.get("dossier") else sources.DOSSIER_DE)
        chemin = os.path.join(dossier, meta["fichier"])
        references.add(os.path.normcase(os.path.abspath(chemin)))
        entrees.append({
            "role": "texte_source",
            "oeuvre": cle,
            "chemin": _relatif(chemin),
            "present": os.path.exists(chemin),
            "octets": os.path.getsize(chemin) if os.path.exists(chemin) else None,
            "sha256": _sha256(chemin) if os.path.exists(chemin) else None,
        })
    for cle, meta in sorted(collation.FACSIMILES.items()):
        chemin = os.path.join(collation.DOSSIER_FAC, meta["fichier"])
        references.add(os.path.normcase(os.path.abspath(chemin)))
        entrees.append({
            "role": "temoin_collation_non_citable",
            "oeuvre": cle,
            "chemin": _relatif(chemin),
            "present": os.path.exists(chemin),
            "octets": os.path.getsize(chemin) if os.path.exists(chemin) else None,
            "sha256": _sha256(chemin) if os.path.exists(chemin) else None,
        })
    tous = set()
    for dossier, _sous, noms in os.walk(sources.DOSSIER_SOURCES):
        for nom in noms:
            if nom.lower().endswith(".txt"):
                tous.add(os.path.normcase(os.path.abspath(os.path.join(dossier, nom))))
    return entrees, sorted(_relatif(p) for p in tous - references)


def empreinte_sources(fichiers=None):
    """Version du corpus source : rôles, œuvres, chemins et contenus, jamais l'heure courante."""
    fichiers = fichiers if fichiers is not None else fichiers_sources()[0]
    return _hash_json([
        {k: f[k] for k in ("role", "oeuvre", "chemin", "sha256")} for f in fichiers])


def divergences_documentaires(compte_atomes, compte_oeuvres):
    """Repère des déclarations numériques possiblement périmées, sans les réécrire.

    C'est volontairement un détecteur de candidats : un document historique ou un sous-corpus
    peut légitimement porter un autre nombre. La décision reste humaine.
    """
    chemins = [os.path.join(RACINE, "README.md")]
    dossier = os.path.join(RACINE, "documentation")
    chemins.extend(os.path.join(dossier, n) for n in sorted(os.listdir(dossier))
                    if n.endswith(".md"))
    motifs = [
        ("atomes", re.compile(r"(?<!\d)(\d{1,3}(?:[ .\u00a0]\d{3})+)\s+atomes", re.I),
         compte_atomes),
        ("oeuvres", re.compile(r"(?<!\d)(\d+)\s+[œo]uvres", re.I), compte_oeuvres),
    ]
    out = []
    for chemin in chemins:
        if not os.path.exists(chemin):
            continue
        with open(chemin, encoding="utf-8") as f:
            for numero, ligne in enumerate(f, 1):
                # Les tableaux d'inventaire par auteur ne déclarent pas nécessairement le total.
                if not any(m in ligne.lower() for m in ("corpus", "état actuel", "sur ")):
                    continue
                for mesure, motif, attendu in motifs:
                    for match in motif.finditer(ligne):
                        trouve = int(re.sub(r"\D", "", match.group(1)))
                        if trouve != attendu:
                            out.append({
                                "fichier": _relatif(chemin), "ligne": numero,
                                "mesure": mesure, "trouve": trouve, "attendu": attendu,
                                "contexte": ligne.strip()[:240],
                                "statut": "a_verifier_humainement",
                            })
    return out


def _meta(db):
    return {r[0]: r[1] for r in db.execute("SELECT cle, valeur FROM meta")}


def construire(chemin_sqlite, reference_git="HEAD"):
    """Construit le manifeste en mémoire à partir de D1 et des registres versionnés."""
    chemin_sqlite = os.path.abspath(chemin_sqlite)
    db = sqlite3.connect("file:%s?mode=ro" % chemin_sqlite, uri=True)
    db.row_factory = sqlite3.Row
    try:
        meta = _meta(db)
        fichiers, orphelins = fichiers_sources()
        auteurs = []
        for r in db.execute("""
            SELECT au.id, au.nom,
                   (SELECT COUNT(*) FROM atomes at WHERE at.auteur_id=au.id) atomes,
                   (SELECT COUNT(*) FROM oeuvres o WHERE o.auteur_id=au.id) volumes,
                   (SELECT COUNT(*) FROM concepts c WHERE c.auteur_id=au.id) concepts,
                   (SELECT COUNT(*) FROM atomes at WHERE at.auteur_id=au.id
                    AND at.texte_fr IS NOT NULL) traductions,
                   (SELECT COUNT(*) FROM atomes at WHERE at.auteur_id=au.id
                    AND at.ocr_suspect=1) ocr_suspects
            FROM auteurs au ORDER BY au.id
        """):
            entree = dict(r)
            entree["lexique_propre"] = lexiques.connu(r["nom"])
            if not entree["lexique_propre"]:
                entree["avertissement_lexique"] = "non_documente_comme_lexique_propre"
            auteurs.append(entree)

        source_par_oeuvre = {f["oeuvre"]: f for f in fichiers if f["role"] == "texte_source"}
        oeuvres = []
        for r in db.execute("""
            SELECT o.id, o.cle, o.titre, o.langue, a.nom auteur, o.annee_oeuvre,
                   o.annee_edition, o.edition, o.editeur, o.source, o.url,
                   o.qualite_source, o.ocr_phrases_corrompues_pct,
                   COUNT(at.id) atomes,
                   SUM(CASE WHEN at.non_qualifie = 0 THEN 1 ELSE 0 END) qualifies,
                   SUM(CASE WHEN at.texte_fr IS NOT NULL THEN 1 ELSE 0 END) traductions,
                   SUM(CASE WHEN at.ocr_suspect = 1 THEN 1 ELSE 0 END) ocr_suspects
            FROM oeuvres o JOIN auteurs a ON a.id=o.auteur_id
            LEFT JOIN atomes at ON at.oeuvre_id=o.id
            GROUP BY o.id ORDER BY o.cle
        """):
            e = dict(r)
            f = source_par_oeuvre.get(r["cle"])
            e["fichier_source"] = f["chemin"] if f else None
            e["sha256_source"] = f["sha256"] if f else None
            e["couverture_relations"] = dict(db.execute(
                "SELECT muette, part_trop_courts, part_touchee FROM carte_couverture "
                "WHERE oeuvre_id=?", (r["id"],)).fetchone() or {})
            oeuvres.append(e)

        total_atomes = db.execute("SELECT COUNT(*) FROM atomes").fetchone()[0]
        total_oeuvres = db.execute("SELECT COUNT(*) FROM oeuvres").fetchone()[0]
        version_sources = empreinte_sources(fichiers)
        reg_fichiers = [
            "verification/signaux_verifies.json", "verification/reprises_lues.json",
            "verification/mentions_lues.json", "traductions/citations_fr.json",
        ]
        registres = []
        for relatif in reg_fichiers:
            chemin = os.path.join(RACINE, *relatif.split("/"))
            with open(chemin, encoding="utf-8") as f:
                contenu = json.load(f)
            cle_collection = "traductions" if relatif.startswith("traductions/") else "verdicts"
            registres.append({
                "chemin": relatif, "sha256": _sha256(chemin),
                "entrees": len(contenu.get(cle_collection, {})),
                "meta": contenu.get("meta", {}),
            })
        traitements = {
            table: db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
            for table in ("mentions", "lectures_declarees", "liens_reprise", "carte_actes",
                          "usages", "socle_liens", "socle_densites", "concept_liens")
        }
        versions_export = {}
        for cle in ("version_schema_export", "version_atomisation", "version_lexique",
                    "version_collation", "version_comparaison", "version_carte",
                    "version_socle_par_couple", "empreinte_sources"):
            versions_export[cle] = (meta[cle] if cle in meta else
                                    _inconnu("champ absent de cet export historique"))
        docs = divergences_documentaires(total_atomes, total_oeuvres)
        manifeste = {
            "schema_manifeste": MANIFESTE_SCHEMA_VERSION,
            "reference": {
                "commit_git": _git_revision(reference_git),
                "reference_demandee": reference_git,
                "export": _relatif(chemin_sqlite),
                "export_sha256": _sha256(chemin_sqlite),
                "export_genere_le": meta.get("genere_le", "inconnu"),
            },
            "versions": {
                "corpus_source": version_sources,
                "schema_export_attendu": EXPORT_SCHEMA_VERSION,
                "enregistrees_dans_export": versions_export,
                "regles_code_lu": {
                    "atomisation": atomisation.ATOMISATION_VERSION,
                    "lexique": lexique.LEXIQUE_VERSION,
                    "collation": collation.COLLATION_VERSION,
                    "comparaison": comparaison.COMPARAISON_VERSION,
                    "carte": carte.CARTE_VERSION,
                    "socle_par_couple": socle_par_couple.SOCLE_PAR_COUPLE_VERSION,
                },
            },
            "comptes": {
                "auteurs": len(auteurs), "oeuvres": total_oeuvres, "atomes": total_atomes,
                "qualifies": db.execute(
                    "SELECT COUNT(*) FROM atomes WHERE non_qualifie=0").fetchone()[0],
                "traductions_appliquees": db.execute(
                    "SELECT COUNT(*) FROM atomes WHERE texte_fr IS NOT NULL").fetchone()[0],
            },
            "auteurs": auteurs,
            "oeuvres": oeuvres,
            "fichiers": fichiers,
            "registres": registres,
            "traitements_derives": traitements,
            "avertissements": {
                "fichiers_txt_orphelins": orphelins,
                "divergences_documentaires_candidates": docs,
                "traduction": ("scope_non_documente" if not registres[-1]["meta"].get("scope")
                                else None),
            },
        }
        manifeste["validation"] = valider(manifeste, db, meta)
        return manifeste
    finally:
        db.close()


def valider(manifeste, db=None, meta=None):
    """Contrôles mécaniques ; les divergences documentaires restent des avertissements."""
    erreurs, avertissements = [], []
    auteurs_attendus = set()
    for m in sources.OEUVRES.values():
        auteurs_attendus.add(m.get("auteur", "Sigmund Freud"))
        auteurs_attendus.update(c["auteur"] for c in m.get("contributions", []))
    auteurs_observes = {a["nom"] for a in manifeste["auteurs"]}
    if auteurs_attendus != auteurs_observes:
        erreurs.append({"code": "auteurs_ecart", "attendus": sorted(auteurs_attendus),
                        "observes": sorted(auteurs_observes)})
    oeuvres_attendues = set(sources.OEUVRES)
    oeuvres_observees = {o["cle"] for o in manifeste["oeuvres"]}
    if oeuvres_attendues != oeuvres_observees:
        erreurs.append({"code": "oeuvres_ecart", "manquantes": sorted(oeuvres_attendues-oeuvres_observees),
                        "inattendues": sorted(oeuvres_observees-oeuvres_attendues)})
    absents = [f["chemin"] for f in manifeste["fichiers"] if not f["present"]]
    if absents:
        erreurs.append({"code": "fichiers_absents", "fichiers": absents})
    orphelins = manifeste["avertissements"]["fichiers_txt_orphelins"]
    if orphelins:
        avertissements.append({"code": "fichiers_orphelins", "fichiers": orphelins})
    if sum(a["atomes"] for a in manifeste["auteurs"]) != manifeste["comptes"]["atomes"]:
        erreurs.append({"code": "compte_auteurs_incoherent"})
    if sum(o["atomes"] for o in manifeste["oeuvres"]) != manifeste["comptes"]["atomes"]:
        erreurs.append({"code": "compte_oeuvres_incoherent"})
    if db is not None:
        nuls = db.execute("SELECT COUNT(*) FROM atomes WHERE atome_id IS NULL OR atome_id='' ").fetchone()[0]
        doublons = db.execute("SELECT COUNT(*) FROM (SELECT atome_id FROM atomes GROUP BY atome_id "
                              "HAVING COUNT(*)>1)").fetchone()[0]
        if nuls or doublons:
            erreurs.append({"code": "identifiants_atomes", "manquants": nuls, "doublons": doublons})
        for cle in ("atomes", "oeuvres"):
            if meta and cle in meta and int(meta[cle]) != manifeste["comptes"][cle]:
                erreurs.append({"code": "meta_compte_incoherent", "champ": cle,
                                "meta": int(meta[cle]), "observe": manifeste["comptes"][cle]})
        empreinte_export = (meta or {}).get("empreinte_sources")
        if empreinte_export is None:
            avertissements.append({"code": "version_sources_export_inconnue",
                                    "raison": "ancien export sans empreinte_sources"})
        elif empreinte_export != manifeste["versions"]["corpus_source"]:
            erreurs.append({"code": "export_autre_corpus", "export": empreinte_export,
                            "sources": manifeste["versions"]["corpus_source"]})
    docs = manifeste["avertissements"]["divergences_documentaires_candidates"]
    if docs:
        avertissements.append({"code": "documentation_numerique_a_verifier", "nombre": len(docs)})
    return {"ok": not erreurs, "erreurs": erreurs, "avertissements": avertissements}


def json_canonique(manifeste):
    return json.dumps(manifeste, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
