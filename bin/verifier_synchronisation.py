#!/usr/bin/env python3
"""Vérifie dépôt, D1, registre, documentation et site sans rien corriger automatiquement."""
import argparse
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core.reference_canonique import (  # noqa: E402
    _charger_json, rapport_markdown, verifier_registre_existant)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--output")
    args = p.parse_args()
    verification = verifier_registre_existant()
    registre = _charger_json("manifests/references_canoniques.json")
    if args.json:
        contenu = json.dumps(verification, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    else:
        contenu = rapport_markdown(registre, verification)
    if args.output:
        chemin = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(contenu)
        print("RAPPORT ÉCRIT : %s" % chemin)
    else:
        print(contenu, end="")
    return 0 if verification["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
