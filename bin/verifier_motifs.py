#!/usr/bin/env python3
"""CONTRÔLE MÉCANIQUE DES MOTIFS — trois défauts qui ne demandent aucun jugement.

  python bin/verifier_motifs.py              → les cinq lexiques
  python bin/verifier_motifs.py "Otto Rank"

Le banc `eprouver_sous_concept.py` demande une LECTURE : il montre ce qu'un motif ramène, et c'est
un humain qui dit si c'est le bon objet. Cet outil-ci ne demande rien à personne. Il cherche trois
défauts qui sont des ERREURS D'ÉCRITURE, vraies ou fausses sans discussion possible :

  MOTIF MORT       zéro occurrence dans TOUT le corpus. Le motif ne peut rien capter, jamais.
                   Cause la plus fréquente dans ce dépôt : un tréma. Le lexique s'applique après un
                   repli qui SUPPRIME les diacritiques, donc « angstgefühl » ne peut pas se
                   déclencher. Cette faute a été écrite trois fois dans le seul lexique de Stekel
                   (angstgefühl, nervosität, schuldgefühl), plus `dachboden` et `freitod` qui sont
                   morts pour une autre raison : le mot est absent du corpus.

  MOTIF ABSORBÉ    le motif n'apporte AUCUN atome que les autres motifs de son sous-concept
                   n'apportent déjà. Il gonfle le compte d'occurrences sans rien qualifier de plus.
                   C'est le défaut le plus coûteux trouvé à ce jour : dans `sterben`, « todes » est
                   contenu dans « tod » et « sterben » dans « sterbe » — 785 occurrences comptées
                   DEUX FOIS, soit 33 % du compte affiché du sous-concept, et le doublon se lisait
                   dans la colonne « formes » sans que personne le voie, tous les chiffres y étant
                   exactement le double du réel. Le même défaut avait déjà été trouvé à la main sur
                   « bisexualitat » ⊂ « bisexual » (51 occurrences, 0 atome gagné).

  DOUBLON EXACT    deux motifs identiques dans la même liste. Inerte, mais c'est le signe qu'une
                   liste a été écrite deux fois ; « onani » y figurait en double.

CE QUE L'OUTIL NE DIT PAS : qu'un motif absorbé doive être retiré. Un motif redondant POUR LES
ATOMES peut rester utile s'il documente une forme attestée — mais alors il faut le savoir, et le
compte d'occurrences doit être lu en sachant qu'il double. L'outil donne le fait ; la décision se
prend en le voyant.

RAPPEL DE MOTEUR, sans quoi cet outil mesurerait autre chose que le lexique : les motifs sont
compilés `re.compile(r"\\b" + motif)` — bordés À GAUCHE seulement — et appliqués sur
`segmentation.replier`, qui supprime diacritiques ET majuscules.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import atomisation, lexique, sources         # noqa: E402
from core.segmentation import replier                  # noqa: E402


def corpus_replie():
    """{auteur: [textes repliés]} — une seule atomisation pour tout le contrôle."""
    out = collections.defaultdict(list)
    for cle in sources.OEUVRES:
        for a in atomisation.atomiser(cle)["atomes"]:
            out[a.get("auteur", "Sigmund Freud")].append(replier(a["texte"]))
    return out


def controler(auteur, textes_par_auteur):
    """→ liste de défauts, chacun établi par un compte et non par un avis."""
    table = lexique.pour_auteur(auteur)
    langue = table.LANGUE
    # Un motif est « mort » s'il ne capte rien NULLE PART dans sa langue — pas seulement chez son
    # auteur. Un motif qui ne capte rien chez lui mais capte ailleurs est un autre problème (ce
    # n'est pas son mot), que le banc traite par le rapport.
    corpus_langue = []
    for autre, textes in textes_par_auteur.items():
        if lexique.pour_auteur(autre).LANGUE == langue:
            corpus_langue.extend(textes)
    miens = textes_par_auteur.get(auteur, [])

    defauts = []
    for groupe, meta in table.CONCEPTS.items():
        for sous, motifs in meta["termes"].items():
            vus = collections.Counter(motifs)
            for m, k in vus.items():
                if k > 1:
                    defauts.append(("DOUBLON EXACT", groupe, sous, m,
                                    "écrit %d fois dans la même liste" % k))

            compiles = {m: re.compile(r"\b" + m) for m in dict.fromkeys(motifs)}

            # Atomes captés par chaque motif, chez cet auteur.
            atomes_par_motif = {}
            for m, r in compiles.items():
                atomes_par_motif[m] = {i for i, t in enumerate(miens) if r.search(t)}

            for m, r in compiles.items():
                partout = sum(1 for t in corpus_langue if r.search(t))
                if partout == 0:
                    defauts.append(("MOTIF MORT", groupe, sous, m,
                                    "0 atome dans tout le corpus %s" % langue))
                    continue
                autres = set()
                for m2, s2 in atomes_par_motif.items():
                    if m2 != m:
                        autres |= s2
                propre = atomes_par_motif[m] - autres
                if atomes_par_motif[m] and not propre:
                    absorbeurs = [m2 for m2, s2 in atomes_par_motif.items()
                                  if m2 != m and (atomes_par_motif[m] & s2)]
                    defauts.append(("MOTIF ABSORBÉ", groupe, sous, m,
                                    "%d atomes, 0 propre — déjà pris par %s"
                                    % (len(atomes_par_motif[m]), ", ".join(sorted(absorbeurs)[:3]))))
                elif not atomes_par_motif[m]:
                    defauts.append(("MUET CHEZ LUI", groupe, sous, m,
                                    "0 atome chez cet auteur, %d ailleurs en %s" % (partout, langue)))
    return defauts


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("auteur", nargs="?")
    args = p.parse_args()

    textes = corpus_replie()
    auteurs = [args.auteur] if args.auteur else sorted(
        {m.get("auteur", "Sigmund Freud") for m in sources.OEUVRES.values()})

    total = collections.Counter()
    for auteur in auteurs:
        if auteur not in textes:
            continue
        defauts = controler(auteur, textes)
        table = lexique.pour_auteur(auteur)
        n_motifs = sum(len(v) for meta in table.CONCEPTS.values() for v in meta["termes"].values())
        print("=" * 100)
        print("%s — %d motifs, %d défaut(s)" % (auteur, n_motifs, len(defauts)))
        print("=" * 100)
        for genre, groupe, sous, motif, detail in sorted(defauts):
            total[genre] += 1
            print("  %-14s %-22s %-24s %-24s %s"
                  % (genre, groupe + "/", sous, repr(motif), detail))
        if not defauts:
            print("  aucun défaut mécanique.")
        print()

    print("=" * 100)
    print("TOTAL :", ", ".join("%s %d" % (g, k) for g, k in total.most_common()) or "aucun défaut")


if __name__ == "__main__":
    main()
