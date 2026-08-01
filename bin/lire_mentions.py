#!/usr/bin/env python3
"""DOSSIERS DE LECTURE DES MENTIONS — sortir les mentions NON LUES avec de quoi les juger.

  python bin/lire_mentions.py --etat                       → combien reste-t-il, par couple
  python bin/lire_mentions.py --lot 1 --taille 180          → tous couples confondus, 1er lot
  python bin/lire_mentions.py --couple "Sándor Ferenczi" "Sigmund Freud" --lot 1 --taille 180

CE QU'UNE MENTION N'ÉTABLIT PAS, ET QUE LA LECTURE NE DOIT PAS COMBLER : la nature du rapport.
Nommer n'est ni suivre, ni approuver, ni contredire — voir `core/comparaison.mentions`. Le travail
de lecture n'est donc PAS de décider si Ferenczi est d'accord avec Freud quand il le nomme : c'est
de vérifier que le nom désigne bien le collègue, et pas autre chose.

TROIS FAUX POSITIFS CONNUS, à chercher activement :
  • L'HOMOGRAPHE — « Abraham » est aussi le patriarche biblique (déclaré dans
    `comparaison.HOMOGRAPHES`, 145 mentions le portent). Le champ `homographe` du dossier signale
    le RISQUE, mesuré ; il ne dit pas le verdict — c'est à la lecture de trancher, mention par
    mention.
  • L'APPAREIL BIBLIOGRAPHIQUE — un titre de recueil, une notice, une liste d'ouvrages où le nom
    apparaît sans qu'aucune phrase ne le nomme activement.
  • LA CITATION D'UN TIERS — l'auteur reproduit un passage d'un troisième texte qui, lui, nomme le
    collègue ; ce n'est alors pas L'AUTEUR DE L'ATOME qui nomme, mais le texte qu'il recopie. Le
    contexte amont/aval (guillemets, appel de note) tranche, comme pour les reprises.

LE VERDICT NE SE SUBSTITUE JAMAIS AU FAIT DE TEXTE : la mention reste ce qu'elle est (un nom
écrit) ; le verdict dit seulement si CE nom, ICI, désigne bien le collègue nommé et si c'est
l'auteur de l'atome qui le nomme.
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import comparaison, corpus, verification    # noqa: E402

CONTEXTE = 2          # atomes de part et d'autre — assez pour trouver un guillemet ou un appel de note

_INDEX_OEUVRE = {}


def _index(c):
    if not _INDEX_OEUVRE:
        for a in c.atomes:
            _INDEX_OEUVRE.setdefault(a["oeuvre"], []).append(a)
        for v in _INDEX_OEUVRE.values():
            v.sort(key=lambda a: a["index"])
    return _INDEX_OEUVRE


def _voisins(c, atome, n=CONTEXTE):
    meme = _index(c).get(atome["oeuvre"], [])
    pos = next((i for i, a in enumerate(meme) if a["id"] == atome["id"]), None)
    if pos is None:
        return [], []
    return (meme[max(0, pos - n):pos], meme[pos + 1:pos + 1 + n])


def calculer(c=None):
    """Toutes les mentions du corpus, groupées par couple (auteur, auteur_nomme)."""
    c = c or corpus.Corpus()
    par_auteur = {}
    for a in c.atomes:
        par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)

    par_couple = collections.defaultdict(list)
    for auteur, atomes in par_auteur.items():
        for m in comparaison.mentions(atomes, auteur):
            par_couple[(auteur, m["auteur_nomme"])].append(m)
    return c, par_couple


def non_lues(c, par_couple, lus, couple=None):
    """Les mentions dont l'atome (× auteur_nomme) n'a pas encore de verdict."""
    out = []
    for (auteur, nomme), ms in sorted(par_couple.items()):
        if couple and (auteur, nomme) != tuple(couple):
            continue
        for m in ms:
            cle = verification.cle_mention(m["atome"]["empreinte"], nomme, m["atome"]["oeuvre"])
            if verification.verdict_mention(cle, lus) is None:
                out.append((auteur, nomme, m))
    return out


def dossier(c, auteur, nomme, m):
    at = m["atome"]
    amont, aval = _voisins(c, at)
    meta = c.oeuvres[at["oeuvre"]]
    return {
        "auteur": auteur,
        "auteur_nomme": nomme,
        "homographe": m["homographe"],
        "id": at["id"],
        "empreinte": at["empreinte"],
        "oeuvre_slug": at["oeuvre"],
        "oeuvre": meta["oeuvre"],
        "annee_oeuvre": meta["annee_oeuvre"],
        "edition_lue": "%s (%s)" % (meta["edition_lue"], meta["annee_edition"]),
        "chapitre": (at["chapitre"] or {}).get("titre"),
        "amont": [x["texte"] for x in amont],
        "texte": at["texte"],
        "aval": [x["texte"] for x in aval],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--etat", action="store_true")
    p.add_argument("--couple", nargs=2)
    p.add_argument("--lot", type=int, default=1)
    p.add_argument("--taille", type=int, default=180)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    c, par_couple = calculer()
    lus = verification.charger_mentions()

    if args.etat:
        total = restant = 0
        print("%-20s %-20s %7s %10s" % ("auteur", "auteur nommé", "total", "non lues"))
        for (auteur, nomme), ms in sorted(par_couple.items(), key=lambda kv: -len(kv[1])):
            nl = len(non_lues(c, {(auteur, nomme): ms}, lus))
            total += len(ms)
            restant += nl
            print("%-20s %-20s %7d %10d" % (auteur, nomme, len(ms), nl))
        print("\n%d mentions, %d non lues" % (total, restant))
        return

    items = non_lues(c, par_couple, lus, args.couple)
    debut = (args.lot - 1) * args.taille
    lot = items[debut:debut + args.taille]
    if not lot:
        print("lot vide — %d mentions non lues au total" % len(items))
        return

    dossiers = [dossier(c, auteur, nomme, m) for auteur, nomme, m in lot]
    if args.json:
        print(json.dumps(dossiers, ensure_ascii=False, indent=1))
        return

    print("LOT %d — %d mentions sur %d non lues" % (args.lot, len(lot), len(items)))
    for n, d in enumerate(dossiers, debut + 1):
        print("\n" + "=" * 98)
        print("MENTION %d — %s nomme %s%s"
              % (n, d["auteur"], d["auteur_nomme"],
                 "  [HOMOGRAPHE CONNU]" if d["homographe"] else ""))
        print("  %s — %s (%s), éd. %s" % (d["id"], d["oeuvre"], d["annee_oeuvre"], d["edition_lue"]))
        for t in d["amont"]:
            print("      … %s" % t[:200].replace("\n", " "))
        print("      >>> %s" % d["texte"][:400].replace("\n", " "))
        for t in d["aval"]:
            print("      … %s" % t[:200].replace("\n", " "))


if __name__ == "__main__":
    main()
