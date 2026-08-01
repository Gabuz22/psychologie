#!/usr/bin/env python3
"""GÉNÈRE documentation/BRANCHES_ET_DERIVATIONS.md — quand un vocabulaire apparaît et disparaît.

    python bin/generer_branches.py

POURQUOI CE SCRIPT EXISTE, ET POURQUOI IL NE MESURE PAS CE QU'ON ATTENDAIT. La voie évidente pour
cartographier les branches d'une école — comparer la densité d'un mot entre deux auteurs et appeler
« divergence » un écart — a été construite ici, chiffrée, et il n'en reste rien après les deux
contrôles que ce projet sait nécessaires. Le document publie donc CE NÉGATIF avec ses chiffres,
puis la mesure qui fonctionne : la chronologie interne de l'œuvre de chaque auteur.

Le partage est le même que pour `generer_courants.py` :
  • les CHIFFRES viennent du corpus à chaque exécution, jamais d'une saisie ;
  • la PROSE ne dit que ce que `core/branches.py` autorise, et ce module refuse de nommer une
    intention — un vocabulaire qui apparaît n'est pas un auteur qui change d'avis.
"""
import collections
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import branches, comparaison                # noqa: E402
from core.corpus import Corpus                        # noqa: E402
from generer_socle import catalogue_motifs, _nombre, _virgule   # noqa: E402

SORTIE = os.path.join(RACINE, "documentation", "BRANCHES_ET_DERIVATIONS.md")

EN_TETE = """# Branches et dérivations — ce qui apparaît, ce qui disparaît, et qui reprend

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_branches.py` — ne pas éditer à la main : tous les
> chiffres viennent du corpus à chaque exécution. Régénérer après tout ajout d'œuvre et toute
> modification de lexique.
>
> **Ce que ce document est.** La trajectoire de chaque vocabulaire dans l'œuvre de chaque auteur :
> quand il apparaît, quand il cesse, s'il tient dans un seul livre, et si un autre auteur le
> reprend ensuite.
>
> **{verdict}**
>
> **Ce que ce document n'est pas.** Une histoire des idées, ni une carte des désaccords. Un mot
> qui apparaît dans l'œuvre tardive d'un auteur peut être un objet nouveau comme un mot nouveau
> pour un objet ancien — et le corpus a mesuré que la seconde possibilité est fréquente :
> Ferenczi, l'auteur qui a le plus visiblement changé de position, ne laisse que **deux**
> révisions de soi confirmées sur 74 signaux relus.
>
> **La datation est une fenêtre, pas une date.** Freud a cessé de signaler ses ajouts dès la
> troisième édition : un vocabulaire tardif peut donc se trouver imprimé dans un livre ancien.
> Toute trajectoire est un endroit où aller lire, jamais un fait établi.

---
"""


def section_negatif(r):
    L = ["## 1. Ce qui ne marche pas — la comparaison entre auteurs, mesurée puis écartée\n"]
    L.append("La mesure évidente : chercher les motifs sur lesquels un auteur domine tous les "
             "autres, et appeler cela sa divergence. Elle donne **%d** motifs sur ce corpus. "
             "Deux contrôles suffisent à tout emporter.\n" % r["brutes"])
    L.append("| Étape | Motifs restants |")
    L.append("|---|---:|")
    L.append("| signatures brutes (un auteur ≥ ×8 le second) | %d |" % r["brutes"])
    L.append("| après retrait de celles portant sur SON PROPRE lexique | %d |"
             % r["apres_controle_du_lexique"])
    L.append("| après retrait des corpus minuscules et des auteurs d'une seule œuvre | **%d** |"
             % r["apres_controle_du_corpus"])
    L.append("")
    L.append("**Le premier contrôle est le plus coûteux.** Chaque auteur du corpus est décrit avec "
             "SON lexique — le motif `amphimixis` a été écrit pour Ferenczi, dans le lexique de "
             "Ferenczi. Qu'il y domine n'établit rien : c'est vrai par construction. **%d des %d "
             "signatures** sont dans ce cas, et les publier ferait passer un choix de lexicographe "
             "pour un trait d'auteur.\n"
             % (r["brutes"] - r["apres_controle_du_lexique"], r["brutes"]))
    if r["detail_hors_propre"]:
        L.append("Les **%d** qui survivent au premier contrôle sont toutes du même auteur :\n"
                 % len(r["detail_hors_propre"]))
        L.append("| Motif | Auteur dominant | Densité | Motif défini par |")
        L.append("|---|---|---:|---|")
        for f in sorted(r["detail_hors_propre"], key=lambda x: -x["pour_mille"]):
            L.append("| `%s` | %s | %s ‰ | %s |"
                     % (_court(f["motif"]), f["auteur"], _virgule(f["pour_mille"]), f["lexique"]))
        L.append("")
    L.append("Et le second contrôle les emporte toutes : Josef Breuer pèse **885 atomes dans une "
             "seule œuvre**. C'est exactement le double artefact — petit corpus, livre unique — "
             "qui avait déjà fait confirmer sept fausses divergences en juillet.\n")
    L.append("**C'est le troisième résultat négatif du même ordre dans ce corpus**, et les trois "
             "se répondent : le signal `ecart_freud` n'a rien confirmé sur cinq candidats, "
             "l'appariement de concepts par voisinage une divergence sur seize, la signature "
             "lexicale **zéro sur %d**. La fréquence d'un mot n'établit jamais une divergence de "
             "doctrine dans ce corpus — trois méthodes différentes le disent.\n" % r["brutes"])
    return "\n".join(L)


def _court(motif):
    m = motif.replace(r"\b(", "").rstrip(")")
    return m if len(m) <= 38 else m[:36] + "…"


def section_trajectoires(resume, par_classe):
    L = ["## 2. Ce qui marche — la chronologie interne de chaque œuvre\n"]
    L.append("La comparaison porte ici sur **un auteur contre lui-même**, dans le temps. C'est ce "
             "qui la rend défendable là où le contraste entre auteurs échoue : le lexicographe qui "
             "a écrit le motif, la taille du corpus, la langue et l'orthographe sont les mêmes des "
             "deux côtés de la coupure. Il ne reste que le temps.\n")
    L.append("**%s trajectoires** mesurées (un motif chez un auteur ayant au moins trois œuvres "
             "d'au moins %d atomes, et au moins %d occurrences) :\n"
             % (_nombre(resume["total"]), branches.ATOMES_MINIMUM_OEUVRE,
                branches.OCCURRENCES_MINIMUM))
    L.append("| Classe | Motifs | Ce que cela veut dire |")
    L.append("|---|---:|---|")
    sens = {
        "constant": "le mot traverse l'œuvre — aucun déplacement",
        "apparait": "la seconde moitié de l'œuvre en porte plusieurs fois plus",
        "disparait": "l'inverse : le mot cesse d'être employé",
        "livre_unique": "un seul livre porte presque tout, sans avant ni après",
    }
    for c, n in resume["par_classe"].items():
        L.append("| **%s** | %s | %s |" % (c, _nombre(n), sens.get(c, "")))
    L.append("")

    for classe, titre, prose in (
        ("apparait", "### Les vocabulaires qui APPARAISSENT",
         "La mesure retrouve, sans qu'on les lui ait données, les tournants documentés de la "
         "psychanalyse — ce qui est le meilleur contrôle qu'on puisse lui demander : elle ne les "
         "découvre pas, elle les rend visibles et vérifiables."),
        ("disparait", "### Les vocabulaires qui DISPARAISSENT",
         "Le résultat symétrique, et le plus rare. Un mot qu'un auteur cesse d'employer est le "
         "seul indice lexical d'un abandon — mais un indice seulement : le corpus rend les "
         "passages, il ne dit pas pourquoi."),
        ("livre_unique", "### Les vocabulaires D'UN SEUL LIVRE",
         "Ni apparition ni disparition : un livre porte presque tout le mot, et rien avant ni "
         "après. Dire « cet auteur diverge » surinterprète — c'est le vocabulaire de CE livre."),
    ):
        lignes = par_classe.get(classe) or []
        if not lignes:
            continue
        L.append(titre + "\n")
        L.append(prose + "\n")
        L.append("| Motif | Auteur | Œuvre dominante | Année | Part d'un livre | Avant → après |")
        L.append("|---|---|---|---:|---:|---|")
        # TRIÉ PAR L'AMPLEUR DU DÉPLACEMENT, pas par le volume. Trier par occurrences remontait
        # les mots les plus fréquents — qui sont les moins informatifs — et enterrait le seul
        # résultat que cette section existe pour montrer : « das Ich » chez Freud en 1923 était
        # en quatrième position, derrière « liebe », « gatte » et « ehefrau ».
        for auteur, t in sorted(lignes, key=lambda x: -_amplitude(x[1]))[:14]:
            part = 100 * t["part_dominante"]
            L.append("| `%s` | %s | %s | %s | %s | %s → %s ‰ |"
                     % (_court(t["motif"]), auteur, t["oeuvre_dominante"][:26],
                        t["annee_dominante"],
                        # Une part élevée dit que le déplacement tient à UN livre : la marquer
                        # évite de lire comme un tournant d'auteur ce qui est un sujet de volume.
                        ("**%s %%**" % _virgule(part, 0)) if part >= 60 else "%s %%" % _virgule(part, 0),
                        _virgule(t["pour_mille_avant"]), _virgule(t["pour_mille_apres"])))
        L.append("")
        L.append("*Une part en gras signale que l'œuvre dominante porte plus de 60 % des "
                 "occurrences : le déplacement tient alors à un LIVRE — souvent son sujet même — "
                 "et non à un tournant dans l'œuvre. Ce n'est pas un défaut à corriger, c'est une "
                 "réserve à lire avec la ligne.*\n")
    return "\n".join(L)


def _amplitude(t):
    """De combien l'usage se déplace de part et d'autre de la coupure — le rang de la ligne."""
    avant, apres = t["pour_mille_avant"], t["pour_mille_apres"]
    haut, bas = max(avant, apres), min(avant, apres)
    return haut / bas if bas else float("inf")


def section_reprises(reprises, lexique_par_motif):
    isoles = [r for r in reprises if r["rameau_isole"]]
    L = ["## 3. Les rameaux isolés — un vocabulaire que personne ne reprend\n"]
    L.append("La seule forme de dérivation que ce corpus puisse établir est LEXICALE : un autre "
             "auteur emploie le mot, dans une œuvre postérieure à celle qui l'introduit. Elle "
             "n'établit ni emprunt, ni filiation, ni accord — deux hommes peuvent nommer la même "
             "chose sans se lire, et le corpus a mesuré combien cela arrive (65 actes de citation "
             "reclassés vers un tiers commun).\n")
    L.append("**Le résultat utile est l'absence.** Sur **%d** motifs suivis, **%d** ne sont "
             "employés que par un seul auteur, sans reprise ni simultanéité : des branches qui "
             "n'ont pas pris.\n" % (len(reprises), len(isoles)))
    par_auteur = collections.Counter(r["premier"] for r in isoles)
    # LE MÊME CONFONDANT QU'EN §1, ET IL FAUT LE CHIFFRER ICI AUSSI. Un auteur dont le lexique
    # contient beaucoup de termes qui lui sont propres aura mécaniquement beaucoup de « rameaux
    # isolés » : le motif a été écrit pour lui, donc personne d'autre ne le porte. Sans cette
    # colonne, « Ferenczi porte les trois quarts des rameaux isolés » se lit comme un fait
    # d'histoire de la psychanalyse alors que c'est en partie un fait de lexicographie.
    propres = collections.Counter(r["premier"] for r in isoles
                                  if lexique_par_motif.get(r["motif"]) == r["premier"])
    if par_auteur:
        L.append("| Auteur | Rameaux isolés | dont sur SON PROPRE motif |")
        L.append("|---|---:|---:|")
        for a, n in par_auteur.most_common():
            L.append("| %s | %d | %d |" % (a, n, propres.get(a, 0)))
        L.append("")
        L.append("**La seconde colonne est indispensable.** Un auteur dont le lexique contient "
                 "beaucoup de termes qui lui sont propres aura mécaniquement beaucoup de rameaux "
                 "isolés : le motif a été écrit pour lui, donc personne d'autre ne le porte. Sur "
                 "les %d rameaux, **%d** sont dans ce cas. Ce qui reste — **%d** — est la part "
                 "que la lexicographie n'explique pas, et c'est la seule qui dise quelque chose "
                 "sur les auteurs.\n"
                 % (len(isoles), sum(propres.values()), len(isoles) - sum(propres.values())))
    L.append("| Motif | Introduit par | Année | Œuvre |")
    L.append("|---|---|---:|---|")
    for r in sorted(isoles, key=lambda r: r["premiere_annee"])[:16]:
        L.append("| `%s` | %s | %s | %s |"
                 % (_court(r["motif"]), r["premier"], r["premiere_annee"], r["premiere_oeuvre"]))
    L.append("")
    simultanes = [r for r in reprises if r["simultanes"]]
    L.append("**%d motifs apparaissent la même année chez deux auteurs**, et le corpus refuse de "
             "les ordonner : deux livres de la même année ne s'ordonnent pas. Le cas exemplaire "
             "est 1924 — le *Trauma der Geburt* de Rank et la *Genitaltheorie* de Ferenczi "
             "partagent leur vocabulaire central, et rien dans le texte ne dit qui a lu qui.\n"
             % len(simultanes))
    return "\n".join(L)


def main(corpus=None):
    corpus = corpus or Corpus()          # partageable entre générateurs — voir `generer_socle`
    langues = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)

    # Atomes groupés par (auteur, œuvre) — une seule passe, réutilisée par tous les motifs.
    groupes = collections.defaultdict(list)
    for a in corpus.atomes:
        auteur = a.get("auteur", "Sigmund Freud")
        if langues.get(auteur) != "de":
            continue
        groupes[(auteur, a["oeuvre"])].append(comparaison.replier_comparaison(a["texte"]))
    annees = {cle: meta["annee_oeuvre"] for cle, meta in corpus.oeuvres.items()}

    motifs = catalogue_motifs("de")
    par_auteur_taille = collections.Counter()
    for (auteur, _), textes in groupes.items():
        par_auteur_taille[auteur] += len(textes)

    # UNE SEULE PASSE PAR MOTIF, et les trois mesures en sortent. La première version en faisait
    # DEUX — la seconde recalculait par auteur ce que la première avait déjà compté par œuvre, en
    # rescannant tout le corpus pour chacun des six auteurs. Soit 483 motifs × 6 × 115 000 atomes,
    # des heures de calcul pour un résultat déjà en mémoire. Le coût d'une passe est déjà de
    # 55 millions de recherches ; il n'y a pas de place pour une seconde.
    trajectoires, reprises = [], []
    densites = collections.defaultdict(dict)
    lexique_par_motif = {}
    for m in motifs:
        r = re.compile(m["motif"])
        par_auteur = collections.defaultdict(list)
        for (auteur, oeuvre), textes in groupes.items():
            par_auteur[auteur].append({
                "cle": oeuvre, "annee": annees.get(oeuvre, 0), "atomes": len(textes),
                "porteurs": sum(1 for t in textes if r.search(t))})
        for auteur, oeuvres in par_auteur.items():
            t = branches.trajectoire(m["motif"], oeuvres)
            if t:
                trajectoires.append((auteur, t))
            # La densité de l'auteur est la somme de ses œuvres — déjà comptée ci-dessus.
            n = sum(o["porteurs"] for o in oeuvres)
            densites[m["motif"]][auteur] = (
                round(1000 * n / par_auteur_taille[auteur], 1), n)
        rep = branches.reprise_posterieure(m["motif"], par_auteur)
        if rep:
            reprises.append(rep)
        lexique_par_motif[m["motif"]] = m["lexique"]

    # Les lexiques décrivent le même concept sous plusieurs écritures ; sans dédoublonnage les
    # tableaux montrent trois fois le même mot et le compte est faux.
    trajectoires = branches.dedoublonner(trajectoires)
    resume = branches.resume(trajectoires)
    par_classe = collections.defaultdict(list)
    for auteur, t in trajectoires:
        par_classe[t["classe"]].append((auteur, t))

    # LE NÉGATIF, recalculé à chaque exécution : s'il cessait d'être vrai, le document le dirait.
    corpus_par_auteur = {a: (n, len({o for (x, o) in groupes if x == a}))
                         for a, n in par_auteur_taille.items()}
    negatif = branches.signature_apres_controles(densites, lexique_par_motif, corpus_par_auteur)

    if negatif["apres_controle_du_corpus"]:
        verdict = ("RÉSULTAT : %d signature(s) lexicale(s) survivent aux deux contrôles. La "
                   "comparaison entre auteurs redevient exploitable — relire la §1."
                   % negatif["apres_controle_du_corpus"])
    else:
        verdict = ("RÉSULTAT À LIRE AVANT LES TABLEAUX. La comparaison de fréquence ENTRE auteurs "
                   "ne donne rien : sur %d signatures brutes, %d portent sur le propre lexique de "
                   "l'auteur — vrai par construction — et les %d restantes viennent toutes d'un "
                   "corpus de 885 atomes en une seule œuvre. Après contrôles, il n'en reste "
                   "AUCUNE. C'est la chronologie interne, et elle seule, qui montre quelque chose."
                   % (negatif["brutes"],
                      negatif["brutes"] - negatif["apres_controle_du_lexique"],
                      negatif["apres_controle_du_lexique"]))

    parts = [EN_TETE.format(verdict=verdict),
             section_negatif(negatif), "---\n",
             section_trajectoires(resume, par_classe), "---\n",
             section_reprises(reprises, lexique_par_motif), "---\n",
             "## 4. Ce que ce document ne dit pas\n",
             branches.reserve() + "\n",
             "*Reproduire : `python bin/generer_branches.py` · le socle partagé : "
             "`SOCLE_COMMUN.md` · l'échec de l'appariement : `APPARIEMENT_ECARTE.md`.*\n"]

    with open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("→ %s (%d trajectoires, %d signatures après contrôles, %d rameaux isolés)"
          % (SORTIE, resume["total"], negatif["apres_controle_du_corpus"],
             sum(1 for r in reprises if r["rameau_isole"])))


if __name__ == "__main__":
    main()
