#!/usr/bin/env python3
"""Audit structurel en lecture seule de la couche relationnelle exportée."""
import argparse
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core.audit_relations import auditer_fichier  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base", nargs="?", default=os.path.join(RACINE, "derive", "d1", "corpus.sqlite"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rapport = auditer_fichier(os.path.abspath(args.base))
    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
    else:
        print("AUDIT RELATIONS — %s" % ("structure valide" if rapport["ok"] else "ERREURS"))
        for ligne in rapport["inventaire"]:
            print("  %-20s %7d  %s" % (ligne["table"], ligne["lignes"], ligne["sens"]))
        for constat in rapport["constats"]:
            print("  [%s] %s (%d): %s" % (constat["severite"].upper(), constat["code"],
                                           constat["nombre"], constat["message"]))
    return 0 if rapport["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
