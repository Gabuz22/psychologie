#!/usr/bin/env python3
"""Prépare les items aveugles et baselines automatiques de l'expérience Freud–Stekel."""
import argparse
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core import experience_relations, registres_v2  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=os.path.join(RACINE, "derive", "d1", "corpus.sqlite"))
    p.add_argument("--manifest", default=os.path.join(RACINE, "manifests", "corpus_actuel.json"))
    p.add_argument("--output", default=os.path.join(
        RACINE, "prototypes", "relations_v2", "experience_freud_stekel.json"))
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    db = registres_v2.charger_base(os.path.abspath(args.base))
    try:
        contenu = experience_relations.json_canonique(experience_relations.construire(db, manifest))
    finally:
        db.close()
    if args.check:
        existant = None
        if os.path.exists(args.output):
            with open(args.output, encoding="utf-8") as f:
                existant = f.read()
        if existant != contenu:
            print("EXPÉRIENCE DÉSYNCHRONISÉE", file=sys.stderr)
            return 1
        print("EXPÉRIENCE CONFORME")
        return 0
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    print("EXPÉRIENCE ÉCRITE : %s" % args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
