#!/usr/bin/env python3
"""Migration v2 : à blanc par défaut ; application explicite dans une base séparée."""
import argparse
import json
import os
import sqlite3
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core import migration_relations_v2, registres_v2  # noqa: E402


def _charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=os.path.join(RACINE, "derive", "d1", "corpus.sqlite"))
    p.add_argument("--manifest", default=os.path.join(RACINE, "manifests", "corpus_actuel.json"))
    p.add_argument("--prototype", default=os.path.join(
        RACINE, "prototypes", "relations_v2", "registre_probatoire_freud_stekel.json"))
    p.add_argument("--report", default=os.path.join(
        RACINE, "prototypes", "relations_v2", "migration_dry_run.json"))
    action = p.add_mutually_exclusive_group()
    action.add_argument("--apply", metavar="TARGET")
    action.add_argument("--rollback", metavar="TARGET")
    args = p.parse_args()
    if args.rollback:
        if not os.path.isfile(args.rollback):
            raise FileNotFoundError("base à restaurer introuvable : %s" % args.rollback)
        db = sqlite3.connect(args.rollback)
        try:
            present = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='v2_runs'"
            ).fetchone()
            if not present:
                raise ValueError("schéma v2 absent ; rollback refusé")
            migration_relations_v2.rollback_schema(db)
        finally:
            db.close()
        print("ROLLBACK V2 APPLIQUÉ : tables historiques conservées")
        return 0
    manifest, prototype = _charger(args.manifest), _charger(args.prototype)
    source = registres_v2.charger_base(os.path.abspath(args.base))
    try:
        rapport = migration_relations_v2.rapport_a_blanc(source, prototype, manifest)
    finally:
        source.close()
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8", newline="\n") as f:
        f.write(migration_relations_v2.json_canonique(rapport))
    print("DRY-RUN : %s" % args.report)
    if args.apply:
        comptes = migration_relations_v2.appliquer(args.apply, prototype, manifest, rapport)
        print("PROTOTYPE APPLIQUÉ DANS BASE SÉPARÉE : %s" % args.apply)
        print(json.dumps(comptes, ensure_ascii=False, sort_keys=True))
    return 1 if rapport.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
