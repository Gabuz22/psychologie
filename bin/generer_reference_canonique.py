#!/usr/bin/env python3
"""Génère ou vérifie le registre canonique et l'état de transparence du site."""
import argparse
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core.reference_canonique import construire, etat_site, json_canonique  # noqa: E402


def _traiter(chemin, contenu, check):
    if check:
        if not os.path.exists(chemin):
            print("ABSENT : %s" % chemin, file=sys.stderr)
            return False
        with open(chemin, encoding="utf-8") as f:
            if f.read() != contenu:
                print("DÉSYNCHRONISÉ : %s" % chemin, file=sys.stderr)
                return False
        print("CONFORME : %s" % chemin)
        return True
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    print("ÉCRIT : %s" % chemin)
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=os.path.join(
        RACINE, "manifests", "references_canoniques.json"))
    p.add_argument("--site-output", default=os.path.join(
        RACINE, "web", "site", "etat-canonique.json"))
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    registre = construire()
    if not registre["validation"]["ok"]:
        for erreur in registre["validation"]["erreurs"]:
            print("ERREUR : %s" % erreur, file=sys.stderr)
        return 1
    ok1 = _traiter(args.output, json_canonique(registre), args.check)
    ok2 = _traiter(args.site_output, json_canonique(etat_site(registre)), args.check)
    return 0 if ok1 and ok2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
