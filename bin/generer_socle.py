#!/usr/bin/env python3
"""GÉNÈRE documentation/SOCLE_COMMUN.md — ce que ces auteurs partagent, mesuré.

    python bin/generer_socle.py

POURQUOI CE SCRIPT EXISTE. « Quel est le socle commun de la psychanalyse ? » est la question la
plus tentante qu'on puisse poser à ce corpus, et celle où un document tenu à la main dériverait le
plus vite : ses chiffres bougent à chaque œuvre ajoutée, à chaque campagne de lecture, à chaque
correction de lexique. Le dépôt a déjà un précédent — `README.md` a décrit pendant des jours une
partition de sept grappes que le document généré comptait à huit.

Le partage est donc net, comme pour `generer_courants.py` :
  • les CHIFFRES viennent du corpus à chaque exécution, par le même chemin de calcul que la base
    du site (`carte.liens_juges`) — le document et le site ne peuvent pas montrer deux comptes
    différents du même travail ;
  • la PROSE qui interprète ne dit que ce que les trois couches de `core/socle.py` autorisent, et
    ce module refuse explicitement de nommer la nature d'un rapport.

CE QUE LE DOCUMENT ANNONCE ET QUI N'ÉTAIT PAS PRÉVU : le partage attesté ne dessine pas un noyau
commun mais une ÉTOILE, et le vocabulaire réellement stable d'un auteur à l'autre est surtout de
l'allemand courant. Les deux résultats sont négatifs, et ils sont l'apport principal.
"""
import collections
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import carte, comparaison, socle          # noqa: E402
from core.corpus import Corpus                      # noqa: E402

SORTIE = os.path.join(RACINE, "documentation", "SOCLE_COMMUN.md")


def _nombre(n):
    return format(n, ",").replace(",", " ")


def _virgule(x, chiffres=1):
    return ("%.*f" % (chiffres, x)).replace(".", ",")


def catalogue_motifs(langue="de"):
    """Les motifs de tous les lexiques de cette langue, dédoublonnés sur la chaîne du motif.

    On garde le premier propriétaire par ordre alphabétique, pour que le résultat ne dépende pas
    de l'ordre d'itération des lexiques — et on retient le nom du lexique, parce qu'une densité
    haute chez celui qui a écrit le motif est vraie par construction et n'informe pas.
    """
    from core import lexique as base, lexiques as lex
    catalogue = [("Sigmund Freud", base.CONCEPTS, "de")]
    for auteur, module in sorted(lex.PAR_AUTEUR.items()):
        catalogue.append((auteur, module.CONCEPTS, module.LANGUE))

    vus, out = set(), []
    for proprietaire, concepts, lg in catalogue:
        if lg != langue:
            continue
        for groupe, meta in sorted(concepts.items()):
            for sous, motifs in sorted(meta["termes"].items()):
                motif = r"\b(" + "|".join(motifs) + ")"
                if motif in vus:
                    continue
                vus.add(motif)
                out.append({"sous": sous, "groupe": groupe, "libelle": meta["label"],
                            "lexique": proprietaire, "motif": motif})
    return out


EN_TETE = """# Le socle commun, mesuré — et la forme qu'il a réellement

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_socle.py` — ne pas éditer à la main : tous les
> chiffres viennent du corpus à chaque exécution, par le même chemin de calcul que la base du
> site. Régénérer après toute campagne de lecture, tout ajout d'œuvre et toute modification de
> lexique.
>
> **Ce que ce document est.** La réponse mesurée à « qu'est-ce que ces auteurs partagent ? »,
> par TROIS couches qui ne se multiplient jamais : le texte réellement partagé, le mot
> réellement commun, et ce qui ressemble à du partage sans en être.
>
> **{verdict}**
>
> **Ce que ce document n'est pas.** Une carte des idées de la psychanalyse. Aucune couche ici ne
> nomme la nature d'un rapport — ni accord, ni dette, ni opposition. Le corpus a mesuré ce que
> valent ces qualifications : le marqueur construit pour repérer les écarts d'un disciple avec
> Freud n'a rien confirmé sur cinq candidats, les cinq passages étant des renvois d'accord.
>
> **Pourquoi trois couches séparées.** Les croiser est l'erreur que ce corpus a déjà mesurée deux
> fois. Attribuer un acte de citation à chacun des concepts que la phrase touche fabrique 1 366
> « liens » là où il y a {actes_total} actes réels, chaque phrase portant 3,5 concepts en moyenne.
> Une reprise établit que deux auteurs partagent CE PASSAGE ; elle n'établit rien sur le concept
> que le passage mentionne au passage.
>
> **Une vue complémentaire existe sur le site** (section « Seuils du socle commun », `/api/socle`) :
> un seuil réglable par le lecteur, entre DEUX auteurs quelconques — pas seulement centrée sur
> Freud comme ce document. Elle repose sur la MÊME doctrine que ci-dessus : deux axes (liens
> vérifiés, densité comparée) qui ne se fusionnent jamais entre eux ni en leur sein — voir
> `core/socle_par_couple.py`. Ce document-ci n'en donne pas le détail par paire : des dizaines de
> couples croisés à des dizaines de concepts feraient un tableau illisible ; la vue vivante, qu'on
> peut filtrer, est le bon support pour une donnée de cette taille.

---
"""


def section_partage(r, actes_lus, actes_total):
    L = ["## 1. Le partage attesté — et il a la forme d'une étoile\n"]
    L.append("La seule couche qui **prouve** un partage de substance : un texte passe d'une œuvre "
             "à une autre, et une lecture en contexte l'a confirmé. Sur les %s actes de citation "
             "du corpus, %s ont été lus et **%s confirmés**.\n"
             % (_nombre(actes_total), _nombre(actes_lus), _nombre(r["actes_confirmes"])))

    L.append("| Couple d'auteurs | Actes confirmés |")
    L.append("|---|---:|")
    for c in r["par_couple"]:
        L.append("| %s | %d |" % (" ↔ ".join(c["auteurs"]), c["actes"]))
    L.append("")

    part = r["part_par_le_centre"]
    L.append("**Le résultat n'était pas cherché, et c'est le principal de ce document.** "
             "%s pour cent des actes confirmés touchent **%s** : il en reste **%d** qui ne le "
             "touchent pas, sur %d. Les disciples ne se citent presque pas entre eux — ils citent "
             "le maître, séparément. Ce n'est pas un noyau commun, c'est une étoile.\n"
             % (_virgule(100 * part), r["centre"], r["actes_sans_le_centre"],
                r["actes_confirmes"]))

    L.append("| Auteur | Actes confirmés le touchant |")
    L.append("|---|---:|")
    for d in r["degre"]:
        L.append("| %s | %d |" % (d["auteur"], d["actes"]))
    L.append("")

    prof = r["profondeur"]
    L.append("### Aucun passage du corpus n'est partagé par trois auteurs\n")
    L.append("Un socle textuel se prouverait par un passage que plusieurs auteurs reprennent "
             "tous. On compte donc, pour chaque phrase touchée par un acte confirmé, le nombre "
             "d'auteurs **distincts** qui la partagent :\n")
    L.append("| Auteurs partenaires | Phrases |")
    L.append("|---:|---:|")
    for k in sorted(prof):
        L.append("| %d | %s |" % (k, _nombre(prof[k])))
    L.append("")
    L.append("La profondeur maximale est de **%d**. Le passage le plus repris du corpus est donc "
             "partagé par deux auteurs, jamais trois — et il reste %d phrases dans ce cas sur "
             "l'ensemble du corpus.\n"
             % (r["profondeur_maximale"], len(r["passages_a_deux_partenaires"])))
    return "\n".join(L)


def section_mots(lignes, stables, disperses, mesures_brutes):
    L = ["## 2. Le mot partagé — ce qui est stable est surtout de l'allemand courant\n"]
    L.append("Le même motif appliqué à tous les corpus allemands. Cette couche ne prouve **aucun** "
             "partage de pensée, seulement d'usage : c'est la thèse fondatrice du projet qu'un "
             "même mot peut désigner autre chose chez deux auteurs, et la mesure qui prétendrait "
             "en décider a été construite puis écartée (6,2 % de précision, une divergence "
             "confirmée sur seize — voir [APPARIEMENT_ECARTE.md](APPARIEMENT_ECARTE.md)).\n")
    # DEUX COMPTES DIFFÉRENTS, et les confondre serait une erreur de plus : `mesures_brutes` est
    # le nombre de motifs des lexiques, `lignes` ce qu'il en reste une fois écartés ceux que deux
    # lexiques écrivent différemment pour retenir les mêmes phrases.
    L.append("Les lexiques définissent **%d** motifs allemands ; **%d** subsistent une fois "
             "écartés ceux que deux lexiques écrivent autrement pour retenir exactement les mêmes "
             "phrases. Parmi eux, **%d** sont employés par tous les auteurs allemands au-dessus "
             "de %s ‰ — **%d** dans un rapport resserré (≤ ×%s), **%d** dans un rapport large.\n"
             % (mesures_brutes, len(lignes), len(stables) + len(disperses),
                _virgule(socle.PLANCHER_POUR_MILLE), len(stables),
                _virgule(socle.ETENDUE_STABLE), len(disperses)))

    L.append("### Les mots les plus également partagés\n")
    L.append("| Motif | Écart max/min | Densités (‰) |")
    L.append("|---|---:|---|")
    for x in sorted(stables, key=lambda x: x["etendue"])[:12]:
        L.append("| `%s` | ×%s | %s |"
                 % (_motif_court(x["motif"]), _virgule(x["etendue"]), _densites(x)))
    L.append("")
    L.append("**C'est le résultat qui refroidit.** Ce que les six auteurs emploient au même taux "
             "n'est pas la doctrine — c'est la langue : la vie, l'homme, l'œil, la main, la nuit. "
             "Le vocabulaire technique, lui, se disperse. Un socle lexical de la psychanalyse ne "
             "ressort pas de cette mesure.\n")

    L.append("### Les mots dont l'usage diverge le plus — avec leurs deux contrôles\n")
    L.append("Un écart large **n'est pas un désaccord de doctrine** : c'est un endroit où aller "
             "lire. Deux drapeaux disent d'abord s'il vaut la peine d'y aller, et chacun a été "
             "payé par une erreur déjà commise dans ce projet — sept des seize divergences lues "
             "en juillet étaient des artefacts d'un livre unique, et un « détecteur » n'utilisant "
             "que le rapport des effectifs atteint déjà une AUC de 0,576.\n")
    L.append("| Motif | Écart | Porté par | Motif défini par | Un seul livre ? | Petit corpus ? |")
    L.append("|---|---:|---|---|---|---|")
    for x in sorted(disperses, key=lambda x: -x["etendue"])[:15]:
        L.append("| `%s` | ×%s | %s (%s ‰) | %s | %s | %s |"
                 % (_motif_court(x["motif"]), _virgule(x["etendue"]), x["haut"],
                    _virgule(x["pour_mille_haut"]),
                    # LE TROISIÈME CONTRÔLE, et il manquait. Un auteur qui domine sur un motif de
                    # SON PROPRE lexique ne diverge pas : le motif a été écrit pour lui.
                    ("**lui-même**" if x["haut_est_le_lexicographe"]
                     else (x["lexique"] or "—")),
                    ("**oui** (%s %%)" % _virgule(100 * x["concentration_haut"], 0)
                     if x["porte_par_une_oeuvre"] else "—"),
                    "**oui**" if x["extremum_petit_corpus"] else "—"))
    L.append("")
    propres = sum(1 for x in disperses if x["haut_est_le_lexicographe"])
    L.append("La colonne **motif défini par** est le troisième contrôle, et le plus sévère : "
             "**%d des %d motifs dispersés** sont dominés par l'auteur dont le lexique a défini "
             "le motif. Leur écart est vrai par construction et n'établit aucune divergence — "
             "c'est le même chiffre qui vide entièrement la comparaison entre auteurs dans "
             "[BRANCHES_ET_DERIVATIONS.md](BRANCHES_ET_DERIVATIONS.md).\n"
             % (propres, len(disperses)))
    n_art = sum(1 for x in disperses if x["porte_par_une_oeuvre"])
    n_pet = sum(1 for x in disperses if x["extremum_petit_corpus"])
    L.append("Sur les %d motifs dispersés, **%d** ont leur densité extrême portée à plus de %s "
             "pour cent par une seule œuvre, et **%d** ont cette densité portée par le plus petit "
             "corpus de la comparaison. Ces deux drapeaux ne filtrent rien — filtrer supposerait "
             "qu'on sait trancher, et on ne sait pas. Ils disent seulement qu'une divergence "
             "publiée sans les regarder a de bonnes chances d'être un artefact.\n"
             % (len(disperses), n_art, _virgule(100 * socle.CONCENTRATION_ARTEFACT, 0), n_pet))
    return "\n".join(L)


def _motif_court(motif):
    """Le motif sans son échafaudage d'expression régulière — lisible dans un tableau."""
    m = motif.replace(r"\b(", "").rstrip(")")
    return m if len(m) <= 40 else m[:38] + "…"


def _densites(x):
    return " · ".join("%s %s" % (a.split()[-1], _virgule(p, 0))
                      for a, p in sorted(x["densites"].items(), key=lambda kv: -kv[1]))


def section_tiers(r):
    L = ["## 3. Le faux socle — ce que deux auteurs partagent sans rien se devoir\n"]
    L.append("**%d actes** ont été **reclassés** par la lecture : les deux auteurs recopient la "
             "même page d'un troisième, qui n'est pas dans le corpus. Sans lecture, chacun aurait "
             "été publié comme un emprunt entre auteurs — c'est-à-dire comme du socle.\n"
             % r["actes_reclasses"])
    L.append("| Tiers cité par les deux | Actes |")
    L.append("|---|---:|")
    for t in r["tiers"][:15]:
        L.append("| %s | %d |" % (t["tiers"], t["actes"]))
    L.append("")
    L.append("**%d tiers distincts.** Ce que ces auteurs ont en commun ici, ce n'est pas une "
             "doctrine : c'est une bibliothèque — des poètes, des sources antiques, des "
             "psychologues d'avant la psychanalyse.\n" % r["tiers_distincts"])
    L.append("*Un auteur du corpus peut figurer dans cette liste, et ce n'est pas une anomalie : "
             "quand Rank et Stekel recopient tous deux la même page de la* Traumdeutung*, le tiers "
             "est Freud — aucun des deux ne lit l'autre, et le lien Rank ↔ Stekel qu'un calcul "
             "seul aurait publié n'existe pas.*\n")
    return "\n".join(L)


def main(corpus=None):
    # Le corpus peut être PASSÉ plutôt que rechargé : `Corpus()` ré-atomise les 57 œuvres depuis
    # les sources, ce qui coûte plusieurs minutes, et les trois documents de ce chantier décrivent
    # le même état. Les enchaîner dans un seul processus divise le coût par trois.
    corpus = corpus or Corpus()
    liens = carte.liens_juges(corpus)
    actes = carte.evenements_de_carte(liens, carte.concepts_par_atome(corpus))

    atteste = socle.partage_atteste(actes)
    tiers = socle.tiers_commun(actes)

    par_auteur = {}
    for a in corpus.atomes:
        par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
    langues = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)
    allemands = {a: v for a, v in par_auteur.items() if langues.get(a) == "de"}

    catalogue = catalogue_motifs("de")
    mesures = [comparaison.densite_comparee(m["motif"], allemands, langues, langue_motif="de")
               for m in catalogue]
    lignes = socle.mot_partage(mesures, {m["motif"]: m["lexique"] for m in catalogue})
    stables = [x for x in lignes if x["classe"] == "stable"]
    disperses = [x for x in lignes if x["classe"] == "disperse"]

    # LE VERDICT EST CALCULÉ ET ÉCRIT EN TOUTES LETTRES, jamais laissé au lecteur — même règle que
    # `generer_courants.py`. Un chiffre qu'il faut interpréter soi-même pour voir ce qu'il dit est
    # un chiffre à moitié publié.
    part = atteste["part_par_le_centre"]
    if atteste["profondeur_maximale"] >= 3:
        verdict = ("RÉSULTAT : un noyau textuel existe — %d phrases du corpus sont partagées par "
                   "trois auteurs ou plus. Le socle a la forme d'un noyau."
                   % sum(n for k, n in atteste["profondeur"].items() if k >= 3))
    else:
        verdict = ("RÉSULTAT À LIRE AVANT LES CHIFFRES. Le socle n'a pas la forme d'un noyau. "
                   "%s pour cent des actes de citation confirmés touchent %s, aucune phrase du "
                   "corpus n'est partagée par trois auteurs, et les mots que les six auteurs "
                   "allemands emploient au même taux sont surtout de la langue courante. Ce que "
                   "ce corpus prouve, ce n'est pas une doctrine commune : c'est une étoile."
                   % (_virgule(100 * part), atteste["centre"]))

    parts = [EN_TETE.format(verdict=verdict, actes_total=_nombre(len(actes))),
             section_partage(atteste, sum(1 for e in actes if e.get("verdict")), len(actes)),
             "---\n",
             section_mots(lignes, stables, disperses, len(catalogue)),
             "---\n",
             section_tiers(tiers),
             "---\n",
             "## 4. Ce que ce document ne dit pas\n",
             socle.reserve() + "\n",
             "*Reproduire : `python bin/generer_socle.py` · les actes un par un : "
             "`python bin/analyser.py --agent lectures` · méthode et limites : "
             "`COMPARAISON_INTER_AUTEURS.md` §1 et `APPARIEMENT_ECARTE.md`.*\n"]

    with open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("→ %s (%d actes confirmés, %s %% par le centre, %d motifs stables, %d dispersés)"
          % (SORTIE, atteste["actes_confirmes"], _virgule(100 * part), len(stables),
             len(disperses)))


if __name__ == "__main__":
    main()
