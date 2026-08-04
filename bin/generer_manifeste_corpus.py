#!/usr/bin/env python3
"""Génère ou vérifie le gel déterministe du corpus actuel."""
import argparse
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core.manifeste_corpus import construire, json_canonique  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=os.path.join(RACINE, "derive", "d1", "corpus.sqlite"))
    p.add_argument("--output", default=os.path.join(RACINE, "manifests", "corpus_actuel.json"))
    p.add_argument("--reference-git", default="a35fe07")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    contenu = json_canonique(construire(args.base, args.reference_git))
    if args.check:
        if not os.path.exists(args.output):
            print("MANIFESTE ABSENT : %s" % args.output, file=sys.stderr)
            return 1
        with open(args.output, encoding="utf-8") as f:
            existant = f.read()
        if existant != contenu:
            print("MANIFESTE DÉSYNCHRONISÉ : régénérer %s" % args.output, file=sys.stderr)
            return 1
        print("MANIFESTE CONFORME : %s" % args.output)
        return 0
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    print("MANIFESTE ÉCRIT : %s" % args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
