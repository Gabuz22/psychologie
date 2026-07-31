#!/usr/bin/env python3
"""DOSSIERS DE LECTURE DES REPRISES — sortir les liens NON LUS avec de quoi les juger.

  python bin/lire_reprises.py --etat                       → combien reste-t-il, par couple
  python bin/lire_reprises.py --couple "Sigmund Freud" "Wilhelm Stekel" --lot 1 --taille 30
  python bin/lire_reprises.py --tous --lot 3 --taille 25   → tous couples confondus, 3e lot

CE QUE LA LECTURE AJOUTE, ET QUE LE CALCUL NE PEUT PAS DONNER.

Le détecteur voit un partage de six mots et s'arrête à la phrase. Le lecteur remonte de quelques
atomes et trouve l'ATTRIBUTION — « Ich zitiere wörtlich », « nach Freud », un appel de note. C'est
elle qui oriente le lien, y compris quand les fenêtres de datation se chevauchent et que le calcul
doit répondre INDÉCIDABLE.

D'où la seule chose que ce dossier fait de plus qu'un affichage des deux phrases : il donne le
CONTEXTE AMONT ET AVAL de chacune. Un lien jugé sur les deux seules phrases partagées est jugé sur
moins que ce que le lecteur humain aurait sous les yeux.

L'UNITÉ EST L'ÉVÉNEMENT, PAS LA PAIRE. Un auteur qui recopie un paragraphe de trois phrases produit
trois paires ; les compter séparément gonfle le travail et, pire, le gonfle INÉGALEMENT selon les
auteurs. Le dossier groupe donc les paires contiguës et demande UN verdict par événement, qui
s'inscrit ensuite sur chacune de ses paires.

TROIS PIÈGES QUE LE DOSSIER SIGNALE AU LECTEUR, parce que le projet s'y est déjà fait prendre :
  • SOURCE TIERCE — les deux passages citent Sophocle ou Goethe : ils peuvent se ressembler sans
    rien se devoir. Verdict « reclasse », avec le tiers nommé.
  • SENS — il ne se déduit JAMAIS d'un identifiant d'atome (ils sont positionnels et dérivent :
    seize liens ont été publiés à l'envers avant qu'on le mesure). Le verdict porte `empreinte_a`,
    hachage du texte du côté a, qui ne dérive pas.
  • FENÊTRES DE DATATION — un atome porte une fenêtre, pas une date. Le dossier l'affiche : quand
    elles se chevauchent, seule l'attribution lue peut trancher, et si elle manque on n'oriente pas.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import comparaison, corpus, sources, verification    # noqa: E402

CONTEXTE = 2          # atomes de part et d'autre — assez pour trouver un « nach Freud » en amont


def _par_auteur(atomes):
    out = {}
    for a in atomes:
        out.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
    return out


def calculer(c=None):
    """Tous les liens publiables, par couple d'auteurs, avec leur verdict de lecture s'il existe."""
    c = c or corpus.Corpus()
    lus = verification.charger_reprises()
    par_auteur = _par_auteur(c.atomes)
    index = [comparaison._n_grammes_utiles(v, None) for v in par_auteur.values()]
    df = comparaison.frequences_documentaires(index)

    noms = sorted(par_auteur)
    couples = {}
    for i, x in enumerate(noms):
        for y in noms[i + 1:]:
            bruts = comparaison.reprises(par_auteur[x], par_auteur[y], df)
            retenus = [comparaison.qualifier(l) for l in bruts
                       if l["contenance"] >= comparaison.SEUIL_PUBLICATION]
            if retenus:
                for lien in retenus:
                    lien["verdict_lu"] = verification.verdict_reprise(
                        lien["a"]["empreinte"], lien["b"]["empreinte"], lus)
                couples[(x, y)] = retenus
    return c, couples


def evenements_non_lus(couples, couple=None):
    """Les ÉVÉNEMENTS dont aucune paire n'a encore reçu de verdict."""
    out = []
    for (x, y), liens in sorted(couples.items()):
        if couple and (x, y) != tuple(couple) and (y, x) != tuple(couple):
            continue
        for evt in comparaison.evenements(liens):
            if any(p.get("verdict_lu") for p in evt["paires"]):
                continue
            evt["auteur_a"], evt["auteur_b"] = x, y
            out.append(evt)
    # Les plus fortes contenances d'abord : ce sont les emprunts les plus nets, et les juger
    # d'abord donne le meilleur rendement de lecture par événement.
    out.sort(key=lambda e: (-e["contenance_max"], -e["longueur"]))
    return out


_INDEX_OEUVRE = {}


def _index(c):
    """{œuvre: [atomes triés par index]} — construit UNE fois.

    Sans cet index, `_voisins` reparcourait les 116 000 atomes du corpus à chaque appel, deux fois
    par paire. Le dossier d'un lot de trente événements demandait plusieurs minutes pour un travail
    qui est un accès par clé.
    """
    if not _INDEX_OEUVRE:
        for a in c.atomes:
            _INDEX_OEUVRE.setdefault(a["oeuvre"], []).append(a)
        for v in _INDEX_OEUVRE.values():
            v.sort(key=lambda a: a["index"])
    return _INDEX_OEUVRE


def _voisins(c, atome, n=CONTEXTE):
    """Les atomes qui entourent celui-ci DANS LA MÊME ŒUVRE — là où se trouve l'attribution."""
    meme = _index(c).get(atome["oeuvre"], [])
    pos = next((i for i, a in enumerate(meme) if a["id"] == atome["id"]), None)
    if pos is None:
        return [], []
    return (meme[max(0, pos - n):pos], meme[pos + 1:pos + 1 + n])


def dossier(c, evt):
    """Tout ce qu'il faut pour juger UN événement, sans avoir à ouvrir autre chose."""
    paires = []
    for p in evt["paires"]:
        fiche = {}
        for cote in ("a", "b"):
            at = p[cote]
            amont, aval = _voisins(c, at)
            meta = c.oeuvres[at["oeuvre"]]
            fiche[cote] = {
                "id": at["id"],
                "empreinte": at["empreinte"],
                "auteur": at.get("auteur", "Sigmund Freud"),
                "oeuvre": meta["oeuvre"],
                "annee_oeuvre": meta["annee_oeuvre"],
                "edition_lue": "%s (%s)" % (meta["edition_lue"], meta["annee_edition"]),
                "fenetre_datation": list(corpus.fenetre_datation(at)),
                "chapitre": (at["chapitre"] or {}).get("titre"),
                "amont": [x["texte"] for x in amont],
                "texte": at["texte"],
                "aval": [x["texte"] for x in aval],
            }
        fiche["contenance"] = p["contenance"]
        fiche["partages"] = p["partages"]
        fiche["source_tierce"] = p["source_tierce"]
        fiche["sens_calcule"] = p["sens"]
        paires.append(fiche)
    return {
        "auteurs": [evt["auteur_a"], evt["auteur_b"]],
        "longueur": evt["longueur"],
        "contenance_max": evt["contenance_max"],
        "paires": paires,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--etat", action="store_true")
    p.add_argument("--couple", nargs=2)
    p.add_argument("--tous", action="store_true")
    p.add_argument("--lot", type=int, default=1)
    p.add_argument("--taille", type=int, default=25)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    c, couples = calculer()

    if args.etat:
        total = lus = 0
        print("%-26s %-26s %7s %7s %7s" % ("auteur A", "auteur B", "liens", "évén.", "non lus"))
        for (x, y), liens in sorted(couples.items()):
            evts = comparaison.evenements(liens)
            nl = sum(1 for e in evts if not any(p.get("verdict_lu") for p in e["paires"]))
            total += len(evts)
            lus += len(evts) - nl
            print("%-26s %-26s %7d %7d %7d" % (x, y, len(liens), len(evts), nl))
        print("\n%d événements, %d lus, %d NON LUS" % (total, lus, total - lus))
        return

    evts = evenements_non_lus(couples, args.couple)
    debut = (args.lot - 1) * args.taille
    lot = evts[debut:debut + args.taille]
    if not lot:
        print("lot vide — %d événements non lus au total" % len(evts))
        return

    dossiers = [dossier(c, e) for e in lot]
    if args.json:
        print(json.dumps(dossiers, ensure_ascii=False, indent=1))
        return

    print("LOT %d — %d événements sur %d non lus" % (args.lot, len(lot), len(evts)))
    for n, d in enumerate(dossiers, debut + 1):
        print("\n" + "=" * 98)
        print("ÉVÉNEMENT %d — %s ↔ %s — %d paire(s), contenance max %.2f"
              % (n, d["auteurs"][0], d["auteurs"][1], d["longueur"], d["contenance_max"]))
        for k, pr in enumerate(d["paires"], 1):
            print("-" * 98)
            print("  paire %d — contenance %.2f — source tierce : %s — sens calculé : %s"
                  % (k, pr["contenance"], pr["source_tierce"], pr["sens_calcule"]))
            for cote in ("a", "b"):
                f = pr[cote]
                print("  [%s] %s — %s (%s), éd. %s — fenêtre %s"
                      % (cote.upper(), f["auteur"], f["oeuvre"], f["annee_oeuvre"],
                         f["edition_lue"], f["fenetre_datation"]))
                print("      id=%s  empreinte=%s  chapitre=%r"
                      % (f["id"], f["empreinte"], f["chapitre"]))
                for t in f["amont"]:
                    print("      … %s" % t[:200].replace("\n", " "))
                print("      >>> %s" % f["texte"][:700].replace("\n", " "))
                for t in f["aval"]:
                    print("      … %s" % t[:200].replace("\n", " "))
            print("      partagés : %s" % ", ".join(pr["partages"][:6]))


if __name__ == "__main__":
    main()
