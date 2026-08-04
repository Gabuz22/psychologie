#!/usr/bin/env python3
"""Génère le registre translexical et le prototype probatoire sans jugement nouveau."""
import argparse
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core import registres_v2  # noqa: E402


def _ecrire(chemin, objet):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(registres_v2.json_canonique(objet))


def _lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=os.path.join(RACINE, "derive", "d1", "corpus.sqlite"))
    p.add_argument("--manifest", default=os.path.join(RACINE, "manifests", "corpus_actuel.json"))
    p.add_argument("--output-dir", default=os.path.join(RACINE, "prototypes", "relations_v2"))
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    db = registres_v2.charger_base(os.path.abspath(args.base))
    try:
        objets = {
            "candidats_translexicaux.json": registres_v2.registre_translexical(db),
            "registre_probatoire_freud_stekel.json": registres_v2.prototype_probatoire(
                db, manifest["versions"]["corpus_source"],
                "comparaison:%s|carte:%s" % (
                    manifest["versions"]["regles_code_lu"]["comparaison"],
                    manifest["versions"]["regles_code_lu"]["carte"])),
        }
    finally:
        db.close()
    if args.check:
        erreurs = []
        for nom, objet in objets.items():
            chemin = os.path.join(args.output_dir, nom)
            attendu = registres_v2.json_canonique(objet)
            if not os.path.exists(chemin) or _lire(chemin) != attendu:
                erreurs.append(nom)
        if erreurs:
            print("REGISTRES DÉSYNCHRONISÉS : " + ", ".join(erreurs), file=sys.stderr)
            return 1
        print("REGISTRES CONFORMES")
        return 0
    for nom, objet in objets.items():
        _ecrire(os.path.join(args.output_dir, nom), objet)
        print("ÉCRIT : %s" % os.path.join(args.output_dir, nom))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
