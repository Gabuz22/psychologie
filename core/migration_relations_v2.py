#!/usr/bin/env python3
"""Migration prototype, additive et réversible, vers le registre relationnel v2."""
import json
import os
import sqlite3

from . import relations_v2


def _actes_sources(prototype):
    return sorted({int(r["legacy"]["id"]) for r in prototype["relations"]
                   if r.get("legacy", {}).get("table") == "carte_actes"})


def rapport_a_blanc(source_db, prototype, manifest):
    """Décrit exactement ce qui serait ajouté ; aucune écriture n'est effectuée."""
    source_db.row_factory = sqlite3.Row
    ids = _actes_sources(prototype)
    presents = 0
    if ids:
        marques = ",".join("?" for _ in ids)
        presents = source_db.execute(
            "SELECT COUNT(*) FROM carte_actes WHERE id IN (%s)" % marques, ids).fetchone()[0]
    non_convertibles = []
    for r in source_db.execute("""
        SELECT id, verdict, sens_lu, reclasse_vers, citation_a, citation_b
        FROM carte_actes WHERE verdict IS NULL ORDER BY id
    """):
        etat = ("discordant_agrege" if r["sens_lu"] and r["reclasse_vers"]
                else "sans_lecture_documentee")
        non_convertibles.append({
            "source_table": "carte_actes", "source_id": str(r["id"]),
            "reason": etat + " : ne pas fabriquer un verdict canonique",
            "payload": dict(r),
        })
    relations = prototype["relations"]
    rapport = {
        "schema_version": relations_v2.RELATIONS_V2_VERSION,
        "mode": "dry_run",
        "source": {
            "export": manifest["reference"]["export"],
            "export_sha256": manifest["reference"]["export_sha256"],
            "corpus_version": manifest["versions"]["corpus_source"],
            "actes_selectionnes": len(ids),
            "actes_retrouves": presents,
        },
        "would_create": {
            "relations": len(relations),
            "evidence": sum(len(r["evidence"]) + len(r["counterevidence"]) for r in relations),
            "annotations": sum(len(r["annotations"]) for r in relations),
            "dimensions": sum(len(r["dimensions"]) for r in relations),
            "legacy_metrics": sum(1 for r in relations if r.get("legacy", {}).get("force") is not None),
            "unconvertible": len(non_convertibles),
        },
        "would_modify_historical_rows": 0,
        "would_delete_historical_rows": 0,
        "unconvertible": non_convertibles,
        "rollback": "DROP uniquement des tables v2 ; aucune table historique n'est touchée",
        "idempotence": "refus si la cible existe déjà",
    }
    if presents != len(ids):
        rapport["error"] = "échantillon et export source désynchronisés"
    return rapport


def _value_json(value):
    return None if value is None else json.dumps(value, ensure_ascii=False, sort_keys=True)


def appliquer(chemin_cible, prototype, manifest, rapport):
    """Crée une base v2 séparée. Refuse toute cible existante, même vide."""
    if os.path.exists(chemin_cible):
        raise FileExistsError("cible déjà existante ; seconde migration refusée : %s" % chemin_cible)
    if rapport.get("error"):
        raise ValueError(rapport["error"])
    os.makedirs(os.path.dirname(os.path.abspath(chemin_cible)), exist_ok=True)
    db = sqlite3.connect(chemin_cible)
    try:
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript(relations_v2.SQL_SCHEMA)
        run_id = "prototype:freud-stekel:v1"
        rule_version = prototype["relations"][0]["rule_version"]
        db.execute("INSERT INTO v2_runs VALUES (?,?,?,?,?,?)", (
            run_id, relations_v2.RELATIONS_V2_VERSION,
            manifest["versions"]["corpus_source"], rule_version,
            manifest["reference"]["export_sha256"], "prototype"))
        for r in prototype["relations"]:
            d = r["direction"]
            db.execute("INSERT INTO v2_relations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                r["id"], run_id, r["type"], r["source"]["type"], r["source"]["id"],
                r["target"]["type"], r["target"]["id"], d["state"], d.get("value"),
                r["validation_state"], r.get("interpretation"), r.get("coverage_limit"),
                r["corpus_version"], r["rule_version"]))
            for polarity, preuves in (("favorable", r["evidence"]),
                                      ("defavorable", r["counterevidence"])):
                for p in preuves:
                    cible = p.get("target") or {}
                    db.execute("INSERT INTO v2_evidence VALUES (?,?,?,?,?,?,?,?)", (
                        p["id"], r["id"], polarity, cible.get("type", "inconnu"),
                        cible.get("id", str(cible)), p.get("source", "inconnu"),
                        p.get("excerpt"), p.get("provenance", "inconnu")))
            for nom, dim in r["dimensions"].items():
                db.execute("INSERT INTO v2_dimensions VALUES (?,?,?,?,?,?,?,?)", (
                    r["id"], nom, dim["state"], _value_json(dim.get("value")), dim.get("unit"),
                    dim.get("rule"), dim.get("rule_version"), dim.get("limitations")))
            for a in r["annotations"]:
                db.execute("INSERT INTO v2_annotations VALUES (?,?,?,?,?,?,?,?,?,?)", (
                    a["id"] + ":" + r["id"], r["id"], a["agent_kind"], a["agent_id"],
                    int(a["independent"]), a["proposition"], a["validation_state"],
                    a["confidence_state"], a.get("confidence_value"), a.get("guide_version")))
            for h in r["history"]:
                db.execute("INSERT INTO v2_history VALUES (?,?,?,?,?)", (
                    r["id"], h["ordinal"], h["action"], h["actor"], h.get("detail")))
            if r.get("legacy", {}).get("force") is not None:
                db.execute("INSERT INTO v2_legacy_metrics VALUES (?,?,?,?,?,?,?)", (
                    r["id"], "force_classe", _value_json(r["legacy"]["force"]),
                    "seuil de contenance textuelle", r["rule_version"], 0,
                    "donnée historique ; ni confiance, ni intensité, ni score canonique"))
        for u in rapport["unconvertible"]:
            db.execute("INSERT INTO v2_unconvertible VALUES (?,?,?,?)", (
                u["source_table"], u["source_id"], u["reason"],
                json.dumps(u["payload"], ensure_ascii=False, sort_keys=True)))
        db.commit()
        return {t: db.execute("SELECT COUNT(*) FROM " + t).fetchone()[0] for t in (
            "v2_relations", "v2_evidence", "v2_annotations", "v2_dimensions",
            "v2_legacy_metrics", "v2_unconvertible")}
    except Exception:
        db.rollback()
        db.close()
        if os.path.exists(chemin_cible):
            os.unlink(chemin_cible)
        raise
    finally:
        if db:
            db.close()


def rollback_schema(db):
    """Retire seulement le prototype v2 ; les tables sans préfixe v2 restent intactes."""
    db.executescript(relations_v2.SQL_ROLLBACK)
    db.commit()


def json_canonique(objet):
    return json.dumps(objet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
