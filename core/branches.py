#!/usr/bin/env python3
"""BRANCHES ET DÉRIVATIONS — quand un vocabulaire apparaît, quand il disparaît, et qui le reprend.

CE MODULE NE MESURE PAS CE QU'ON ATTENDAIT DE LUI, ET C'EST SON PREMIER RÉSULTAT.

La voie évidente pour cartographier les branches d'une école est de comparer la densité d'un mot
entre deux auteurs et d'appeler « divergence » un écart. Elle a été essayée ici, chiffrée, et elle
ne tient pas — après les deux contrôles que ce projet sait nécessaires, il n'en reste RIEN :

  • 35 motifs sur lesquels un auteur domine les autres d'un facteur huit ou plus ;
  • 31 le sont sur un motif de SON PROPRE lexique — vrai par construction, le motif a été écrit
    pour lui, et cela ne dit rien de sa distance aux autres ;
  • les 4 restants sont tous du même auteur, Josef Breuer, dont le corpus fait 885 atomes dans
    UNE SEULE œuvre — c'est-à-dire exactement le double artefact (petit corpus, livre unique) qui
    avait déjà fait confirmer sept fausses divergences en juillet.
  • Breuer retiré : ZÉRO.

ET LA RAISON EST PIRE QUE CE QU'ON CROYAIT — trouvé en écrivant `core/accueil.py`, après coup.
Ces quatre signatures n'ont pas SURVÉCU au premier contrôle : elles ne l'ont jamais rencontré.
Josef Breuer ne possède AUCUN motif — il est le seul auteur du corpus sans lexique propre, ses
pages étant décrites avec celui de Freud parce qu'elles sont imprimées dans un volume de Freud.
Un auteur sans motif ne peut jamais dominer sur le sien, donc le contrôle par provenance du
lexique est VIDE pour lui, structurellement. Que les quatre survivantes soient toutes de Breuer
n'était pas une coïncidence : c'était la seule chose qui pouvait arriver.
La conclusion publiée ne change pas — zéro après les deux contrôles — mais elle repose désormais
sur le bon motif, et `accueil.mesures_non_applicables` le déclare pour tout auteur futur dans ce
cas : le contrôle par provenance ne protège que les auteurs qui ont un lexique.

C'est le troisième résultat négatif du même ordre dans ce corpus, et les trois se répondent : le
signal `ecart_freud` n'a rien confirmé sur cinq candidats, l'appariement de concepts par voisinage
une divergence sur seize, la signature lexicale zéro sur trente-cinq. LA FRÉQUENCE D'UN MOT
N'ÉTABLIT JAMAIS UNE DIVERGENCE DE DOCTRINE DANS CE CORPUS. Trois méthodes différentes le disent.

L'AXE QUI FONCTIONNE EST LA CHRONOLOGIE INTERNE, et il fallait le négatif ci-dessus pour le voir.

Les quatre premières oppositions documentées du corpus (§4.1-4.4) ne reposaient pas sur un
contraste entre auteurs mais sur un déplacement DANS l'œuvre d'un seul : le vocabulaire du
traumatisme de la naissance
n'existe que dans le livre de 1924 de Rank, et nulle part avant chez lui. Cette mesure-là se
défend, parce qu'elle compare un auteur à lui-même — le lexicographe, la taille du corpus et la
langue sont constants des deux côtés.

Elle retrouve d'ailleurs, sans qu'on les lui ait données, les tournants documentés de la
psychanalyse : `es` et `ueberich` apparaissent dans « Das Ich und das Es » (1923), `todestrieb`
dans « Jenseits des Lustprinzips » (1920), `genitalitaet` dans la « Genitaltheorie » de Ferenczi
(1924) — et `hypnoid`, la théorie des états hypnoïdes empruntée à Breuer, DISPARAÎT de Freud après
les « Studien über Hysterie ».

CE QUE LA CHRONOLOGIE N'ÉTABLIT PAS, et le piège est sérieux : qu'un auteur ait CHANGÉ D'AVIS. Un
mot qui apparaît peut être un objet nouveau comme un mot nouveau pour un objet ancien. Et surtout,
un atome ne porte pas une date mais une FENÊTRE — Freud a cessé de signaler ses ajouts dès la
troisième édition, si bien qu'un vocabulaire tardif peut se trouver imprimé dans un livre ancien.
Chaque trajectoire porte donc `datation_sure`, et une trajectoire non sûre est un candidat à lire,
jamais un fait.
"""
import collections

BRANCHES_VERSION = "1.0.0"

# Sous ce nombre d'atomes, une densité d'œuvre est un accident. MESURÉ : le corpus contient une
# « œuvre » de Freud de CINQ atomes — sa préface aux « Nervöse Angstzustände » de Stekel — où une
# seule occurrence donne 200 ‰ et emporte le maximum de n'importe quel motif.
ATOMES_MINIMUM_OEUVRE = 50

# Sous ce nombre d'occurrences chez l'auteur, la trajectoire décrit du bruit.
OCCURRENCES_MINIMUM = 25

# Part des occurrences venant d'une seule œuvre au-delà de laquelle le mot est le vocabulaire d'un
# LIVRE et non d'un auteur. C'est le cas de `geburtstrauma` chez Rank — et le dire ainsi est plus
# juste que « Rank diverge », puisque le mot n'existe ni avant ni après dans son œuvre.
PART_LIVRE_UNIQUE = 0.80

# Rapport entre la densité de la seconde moitié de l'œuvre et celle de la première au-delà duquel
# on parle d'apparition (ou, inversé, de disparition).
FACTEUR_TOURNANT = 4.0


def trajectoire(motif, oeuvres):
    """La trajectoire d'un motif dans l'œuvre d'UN auteur → dict, ou None si non mesurable.

    `oeuvres` : liste de {cle, annee, atomes, porteurs} pour un seul auteur, dans n'importe quel
    ordre — la fonction les trie.

    LA COMPARAISON EST INTERNE À L'AUTEUR, et c'est ce qui la rend défendable là où le contraste
    entre auteurs échoue : le lexicographe qui a écrit le motif, la taille du corpus, la langue et
    l'orthographe sont les mêmes des deux côtés de la coupure. Il ne reste que le temps.

    Quatre classes, aucune ne nommant une intention :
      « livre_unique » — une seule œuvre porte presque tout. Le mot est le vocabulaire de ce
          livre ; l'attribuer à l'auteur serait déjà surinterpréter.
      « apparait »     — la seconde moitié de l'œuvre en porte plusieurs fois plus que la première.
      « disparait »    — l'inverse.
      « constant »     — le mot traverse l'œuvre.
    """
    utiles = sorted((o for o in oeuvres if o["atomes"] >= ATOMES_MINIMUM_OEUVRE),
                    key=lambda o: (o["annee"], o["cle"]))
    if len(utiles) < 3:
        return None
    total = sum(o["porteurs"] for o in utiles)
    if total < OCCURRENCES_MINIMUM:
        return None

    dominante = max(utiles, key=lambda o: o["porteurs"])
    part = dominante["porteurs"] / total

    # La coupure se fait sur les ŒUVRES, pas sur les années : les publications ne sont pas
    # réparties également dans le temps, et couper à mi-durée mettrait tout d'un côté.
    milieu = len(utiles) // 2
    avant, apres = utiles[:milieu], utiles[milieu:]
    d_avant = _densite(avant)
    d_apres = _densite(apres)

    # LA CONCENTRATION NE SUFFIT PAS À CLASSER, et c'est un test qui l'a montré. Un mot dont 90 %
    # des occurrences sont dans une seule œuvre est « concentré » — mais si cette œuvre est la
    # PREMIÈRE, le fait intéressant n'est pas la concentration, c'est que le mot est ensuite
    # abandonné. C'est exactement le cas de `hypnoid` chez Freud : 26 occurrences dans les
    # « Studien über Hysterie » de 1895, puis plus rien — la théorie des états hypnoïdes empruntée
    # à Breuer, qu'il cesse d'employer. L'appeler « livre unique » aurait décrit la forme et perdu
    # l'histoire.
    #
    # Trois positions, trois lectures différentes de la même concentration :
    #   première œuvre  → le vocabulaire est abandonné  (`disparait`)
    #   dernière œuvre  → il est adopté                 (`apparait`)
    #   au milieu       → il est le vocabulaire de CE livre, sans avant ni après (`livre_unique`).
    #     C'est `geburtstrauma` chez Rank : rien en 1907-1912, tout en 1924, rien en 1928.
    rang_dominante = utiles.index(dominante)
    if part >= PART_LIVRE_UNIQUE:
        classe = ("disparait" if rang_dominante == 0
                  else "apparait" if rang_dominante == len(utiles) - 1
                  else "livre_unique")
    elif d_avant == 0 or d_apres / max(d_avant, 1e-9) >= FACTEUR_TOURNANT:
        classe = "apparait"
    elif d_apres == 0 or d_avant / max(d_apres, 1e-9) >= FACTEUR_TOURNANT:
        classe = "disparait"
    else:
        classe = "constant"

    porteuses = [o for o in utiles if o["porteurs"]]
    return {
        "motif": motif,
        "classe": classe,
        "occurrences": total,
        "oeuvres_mesurees": len(utiles),
        "oeuvre_dominante": dominante["cle"],
        "annee_dominante": dominante["annee"],
        "part_dominante": round(part, 3),
        "pour_mille_avant": round(d_avant, 1),
        "pour_mille_apres": round(d_apres, 1),
        "premiere_annee": porteuses[0]["annee"] if porteuses else None,
        "derniere_annee": porteuses[-1]["annee"] if porteuses else None,
        "annee_coupure": apres[0]["annee"],
    }


def _densite(oeuvres):
    atomes = sum(o["atomes"] for o in oeuvres)
    return 1000 * sum(o["porteurs"] for o in oeuvres) / atomes if atomes else 0.0


# Densité minimale pour qu'un auteur compte comme EMPLOYANT le mot, et donc comme repreneur.
# DÉFAUT MESURÉ SUR LE PREMIER DOCUMENT PRODUIT : sans ce seuil, UNE occurrence isolée chez un
# autre auteur suffisait à faire d'un vocabulaire propre un vocabulaire repris — et le corpus est
# océrisé, donc une occurrence isolée peut n'être qu'une coquille. Le document annonçait 7 rameaux
# isolés là où 36 motifs ne sont réellement employés que par un seul auteur : le résultat le plus
# intéressant de la couche était effacé par un bruit d'une occurrence.
POUR_MILLE_EMPLOI = 1.0


def reprise_posterieure(motif, par_auteur):
    """Le mot d'un auteur est-il repris par un autre APRÈS lui ? — la question « dérivation ».

    `par_auteur` : {auteur: [ {cle, annee, atomes, porteurs}, … ]}.

    C'est la seule forme de dérivation que ce corpus puisse établir, et elle est LEXICALE : un
    autre auteur emploie le mot, dans une œuvre postérieure à celle qui l'introduit. Elle
    n'établit ni emprunt, ni filiation, ni accord — deux hommes peuvent nommer la même chose sans
    se lire, et le corpus a mesuré combien cela arrive (85 actes de citation reclassés vers un
    tiers commun).

    LE RÉSULTAT UTILE EST L'ABSENCE. Un vocabulaire qu'un auteur introduit et que personne ne
    reprend est un rameau qui n'a pas pris — et le corpus en compte beaucoup plus que l'inverse.
    """
    introducteurs = []
    for auteur, oeuvres in par_auteur.items():
        porteuses = sorted((o for o in oeuvres
                            if o["porteurs"] and o["atomes"] >= ATOMES_MINIMUM_OEUVRE),
                           key=lambda o: o["annee"])
        if not porteuses:
            continue
        total_atomes = sum(o["atomes"] for o in oeuvres) or 1
        occurrences = sum(o["porteurs"] for o in oeuvres)
        pour_mille = round(1000 * occurrences / total_atomes, 1)
        # EMPLOYER un mot n'est pas l'avoir écrit une fois. Sans ce filtre, une coquille d'OCR
        # dans un corpus océrisé fait d'un vocabulaire propre un vocabulaire partagé.
        if pour_mille < POUR_MILLE_EMPLOI:
            continue
        introducteurs.append({
            "auteur": auteur,
            "premiere_annee": porteuses[0]["annee"],
            "premiere_oeuvre": porteuses[0]["cle"],
            "occurrences": occurrences,
            "pour_mille": pour_mille,
        })
    if not introducteurs:
        return None
    introducteurs.sort(key=lambda x: (x["premiere_annee"], -x["occurrences"]))
    premier = introducteurs[0]

    # Un repreneur emploie le mot dans une œuvre STRICTEMENT postérieure à la première du premier.
    # L'égalité d'année ne prouve rien — deux livres de la même année ne s'ordonnent pas, et le
    # corpus en a un cas exemplaire : le « Trauma der Geburt » de Rank et la « Genitaltheorie »
    # de Ferenczi partagent leur vocabulaire central et paraissent tous deux en 1924.
    repreneurs = [x for x in introducteurs[1:] if x["premiere_annee"] > premier["premiere_annee"]]
    simultanes = [x for x in introducteurs[1:] if x["premiere_annee"] == premier["premiere_annee"]]
    return {
        "motif": motif,
        "premier": premier["auteur"],
        "premiere_annee": premier["premiere_annee"],
        "premiere_oeuvre": premier["premiere_oeuvre"],
        "repreneurs": [x["auteur"] for x in repreneurs],
        "simultanes": [x["auteur"] for x in simultanes],
        "rameau_isole": not repreneurs and not simultanes,
        "detail": introducteurs,
    }


def signature_apres_controles(lignes_usages, lexique_par_motif, corpus_par_auteur,
                              facteur=8.0, porteurs_minimum=10):
    """LE NÉGATIF, CALCULÉ ET CONSERVÉ — parce qu'un résultat négatif non écrit se refait.

    `lignes_usages` : {motif: {auteur: (pour_mille, porteurs)}}
    `lexique_par_motif` : {motif: auteur qui a défini le motif}
    `corpus_par_auteur` : {auteur: (nb_atomes, nb_oeuvres)}

    Rend le décompte des signatures à chaque étape du filtrage, pour qu'on voie où elles tombent.
    Une signature ne survit que si le motif vient du lexique d'un AUTRE auteur (sans quoi elle est
    vraie par construction) et si l'auteur qui domine n'est ni le plus petit corpus ni un auteur
    d'une seule œuvre (sans quoi c'est le double artefact déjà mesuré).
    """
    brutes, hors_propre, survivantes = [], [], []
    petit = min(corpus_par_auteur, key=lambda a: corpus_par_auteur[a][0])
    for motif, densites in lignes_usages.items():
        ordonne = sorted(densites.items(), key=lambda kv: -kv[1][0])
        if len(ordonne) < 2:
            continue
        (haut, (pm_haut, porteurs)), (_, (pm_second, _)) = ordonne[0], ordonne[1]
        if porteurs < porteurs_minimum or pm_haut < facteur * max(pm_second, 0.05):
            continue
        fiche = {"motif": motif, "auteur": haut, "pour_mille": pm_haut,
                 "pour_mille_second": pm_second, "lexique": lexique_par_motif.get(motif)}
        brutes.append(fiche)
        if lexique_par_motif.get(motif) == haut:
            continue                       # le motif a été écrit pour lui : rien n'est établi
        hors_propre.append(fiche)
        atomes, oeuvres = corpus_par_auteur.get(haut, (0, 0))
        if haut == petit or oeuvres <= 1:
            continue                       # petit corpus ou livre unique : artefact déjà mesuré
        survivantes.append(fiche)
    return {
        "brutes": len(brutes),
        "apres_controle_du_lexique": len(hors_propre),
        "apres_controle_du_corpus": len(survivantes),
        "survivantes": survivantes,
        "ecartees_par_le_lexique": [f["motif"] for f in brutes if f not in hors_propre],
        "detail_hors_propre": hors_propre,
    }


def dedoublonner(trajectoires):
    """Écarte les trajectoires que DEUX MOTIFS DIFFÉRENTS décrivent à l'identique.

    DÉFAUT MESURÉ SUR LE PREMIER DOCUMENT PRODUIT. Plusieurs lexiques écrivent le même concept
    autrement — `identifizier`, `identifizierung|identifizier`, `identifizierung|identifiziert` —
    et les trois retiennent les mêmes phrases. Les tableaux montraient alors trois fois le même
    mot, occupant les places d'autres : sur quatorze lignes d'apparition, trois disaient
    « identifizier » et trois « traum ». Ce n'est pas un défaut d'affichage, c'est un compte faux.

    Deux trajectoires sont tenues pour la même quand elles portent sur le même auteur, la même
    œuvre dominante et les mêmes densités de part et d'autre de la coupure. On garde le motif le
    plus court, pour que le choix ne dépende pas de l'ordre d'itération des lexiques.
    """
    vus, uniques = set(), []
    for auteur, t in sorted(trajectoires, key=lambda x: (len(x[1]["motif"]), x[1]["motif"])):
        cle = (auteur, t["oeuvre_dominante"], t["part_dominante"],
               t["pour_mille_avant"], t["pour_mille_apres"], t["occurrences"])
        if cle in vus:
            continue
        vus.add(cle)
        uniques.append((auteur, t))
    return uniques


def resume(trajectoires):
    """Combien de motifs dans chaque classe, par auteur — la carte des branches, en un tableau."""
    par_classe = collections.Counter()
    par_auteur = collections.defaultdict(collections.Counter)
    for auteur, t in trajectoires:
        par_classe[t["classe"]] += 1
        par_auteur[auteur][t["classe"]] += 1
    return {
        "total": sum(par_classe.values()),
        "par_classe": dict(par_classe.most_common()),
        "par_auteur": {a: dict(c.most_common()) for a, c in sorted(par_auteur.items())},
    }


def reserve():
    """Ce que les branches ne disent pas — porté avec elles."""
    return (
        "Ce document décrit des TRAJECTOIRES DE VOCABULAIRE, jamais des changements d'avis. Un mot "
        "qui apparaît dans l'œuvre tardive d'un auteur peut être un objet nouveau comme un mot "
        "nouveau pour un objet ancien — et le corpus a mesuré que la seconde possibilité est "
        "fréquente : Ferenczi, l'auteur qui a le plus visiblement changé de position, ne laisse "
        "que DEUX révisions de soi confirmées sur 74 signaux relus. Un renversement doctrinal ne "
        "laisse presque aucune trace lexicale de première personne. "
        "LA COMPARAISON ENTRE AUTEURS A ÉTÉ ESSAYÉE ET ÉCARTÉE : sur 35 motifs où un auteur domine "
        "les autres d'un facteur huit, 31 le font sur un motif de leur propre lexique — vrai par "
        "construction — et les 4 restants viennent tous d'un corpus de 885 atomes en une seule "
        "œuvre. Après contrôles, il n'en reste aucun. C'est le troisième résultat négatif du même "
        "ordre dans ce corpus, avec le signal `ecart_freud` (0 confirmé sur 5) et l'appariement de "
        "concepts par voisinage (1 sur 16). "
        "ENFIN LA DATATION : un atome ne porte pas une date mais une FENÊTRE, Freud ayant cessé de "
        "signaler ses ajouts dès la troisième édition. Un vocabulaire tardif peut donc se trouver "
        "imprimé dans un livre ancien, et une trajectoire dont `datation_sure` est faux est un "
        "endroit où aller lire, jamais un fait établi."
    )
