#!/usr/bin/env python3
"""SOCLE COMMUN — ce que ces auteurs partagent RÉELLEMENT, et ce que le partage apparent recouvre.

LA QUESTION, ET POURQUOI ELLE EST PIÉGÉE. « Quel est le socle commun de la psychanalyse ? » se
laisse répondre trop facilement : on prend les concepts que tous emploient, on les compte, on
publie une liste. Le corpus a déjà mesuré ce que valent ces listes-là, et le chiffre est dans le
dépôt — l'appariement de concepts par voisinage donnait 6 % de précision sur la tâche réelle et
UNE divergence confirmée sur seize à la lecture (`documentation/APPARIEMENT_ECARTE.md`).

LA FAUTE À NE PAS REFAIRE, ET ELLE A ÉTÉ REFAITE ICI AVANT D'ÊTRE VUE. La première version de ce
module attribuait chaque lien de reprise à tous les concepts que la phrase touche : 341 motifs
ressortaient « attestés », chiffre flatteur et faux. C'est le produit croisé que `core/carte.py`
documente déjà — il fabriquait 1 366 arêtes là où il y a 354 actes, chaque phrase portant 3,5
concepts en moyenne. Une reprise établit que DEUX AUTEURS PARTAGENT CE PASSAGE ; elle n'établit
rien sur le concept que le passage mentionne au passage.

D'OÙ TROIS COUCHES QUI NE SE MULTIPLIENT JAMAIS, chacune avec sa propre unité et sa propre preuve :

  1. LE PARTAGE ATTESTÉ — l'unité est l'ACTE DE CITATION, lu et confirmé. C'est la seule couche
     qui prouve un partage de substance, et elle est PETITE. Ce qu'elle montre n'est pas un noyau
     mais une ÉTOILE : mesuré sur le corpus, 91,5 % des actes confirmés touchent Freud, et aucun
     passage du corpus n'est partagé par trois auteurs. Les disciples ne se citent presque pas
     entre eux ; ils citent le maître, séparément.

  2. LE MOT PARTAGÉ — l'unité est le MOTIF, appliqué à l'identique à tous les corpus d'une langue.
     Cette couche ne prouve aucun partage de pensée, seulement d'usage. Elle porte deux contrôles
     sans lesquels elle ment : l'ÉCART DE TAILLE entre corpus (un corpus minuscule fabrique des
     rapports spectaculaires) et la CONCENTRATION PAR ŒUVRE (sept des seize divergences déjà lues
     dans ce projet étaient des artefacts d'un livre unique, pas des traits d'auteur).

  3. LE TIERS COMMUN — ce qui RESSEMBLE à du socle et n'en est pas. Deux auteurs qui recopient la
     même page de Rosegger ou de Hebbel se ressemblent sans rien se devoir. Les 85 actes reclassés
     du corpus sont exclus du socle, et nommés : sans la lecture, chacun aurait été publié comme un
     emprunt entre auteurs du corpus.

CE QUE CE MODULE REFUSE DE DIRE, et qu'aucun de ses champs ne portera : qu'un mot partagé désigne
la même chose chez deux auteurs. C'est la thèse même du projet qu'on ne peut pas le supposer — et
la mesure qui prétendrait en décider a été construite, chiffrée, puis écartée. Un mot dont l'usage
diverge est donc rendu comme UN ENDROIT OÙ ALLER LIRE, jamais comme un écart de doctrine.
"""
import collections

SOCLE_VERSION = "1.0.0"

# Densité plancher pour qu'un motif compte comme employé par un auteur. En dessous, l'emploi
# relève de l'occurrence isolée et le rapport max/min devient le rapport de deux accidents.
PLANCHER_POUR_MILLE = 1.0

# Au-delà de ce rapport entre la densité la plus haute et la plus basse, l'usage du mot n'est plus
# comparable d'un auteur à l'autre. LE SEUIL EST FIXÉ PAR LA DISTRIBUTION MESURÉE, et il est
# volontairement lâche : la question posée ici n'est pas « ces auteurs pensent-ils la même chose »
# (indécidable) mais « ce mot se distribue-t-il assez également pour qu'on puisse au moins parler
# d'un usage commun ». Voir `documentation/SOCLE_COMMUN.md` pour la distribution complète.
ETENDUE_STABLE = 4.0

# Part des porteurs venant d'une seule œuvre au-delà de laquelle la mesure décrit un LIVRE et non
# un auteur. Reprise de `appariement.Signatures.signature`, où elle est déjà calculée sous le nom
# `concentration` — et c'est le contrôle dont l'absence a fait confirmer sept fausses divergences.
CONCENTRATION_ARTEFACT = 0.60


def partage_atteste(actes):
    """LA COUCHE FORTE — les actes de citation confirmés par lecture, et la forme qu'ils dessinent.

    `actes` : itérable de dicts portant au moins `auteur_a`, `auteur_b`, `verdict`, et les listes
    `atomes_a` / `atomes_b` (tels que rendus par `carte.evenements_de_carte`).

    LE RÉSULTAT QU'ON N'ATTENDAIT PAS, et qui est la vraie réponse à « quel est le socle » : le
    partage n'a pas la forme d'un noyau que tous auraient en commun. Il a la forme d'une ÉTOILE.
    `part_par_le_centre` mesure cette forme — c'est la part des actes confirmés qui touchent
    l'auteur le plus cité. Un socle véritable donnerait un chiffre bas et des liens denses entre
    disciples ; le corpus donne l'inverse.
    """
    par_couple = collections.Counter()
    degre = collections.Counter()
    partenaires = collections.defaultdict(set)
    for e in actes:
        if e.get("verdict") != "confirme":
            continue
        a, b = e["auteur_a"], e["auteur_b"]
        par_couple[tuple(sorted((a, b)))] += 1
        degre[a] += 1
        degre[b] += 1
        # Un passage peut être repris par plusieurs auteurs — c'est la seule façon dont un
        # « noyau commun » pourrait apparaître dans le texte. On compte donc, pour chaque atome,
        # les auteurs DISTINCTS qui le partagent.
        for x in e.get("atomes_a") or ():
            partenaires[x].add(b)
        for x in e.get("atomes_b") or ():
            partenaires[x].add(a)

    total = sum(par_couple.values())
    centre, actes_centre = (degre.most_common(1) or [(None, 0)])[0]
    profondeur = collections.Counter(len(s) for s in partenaires.values())
    return {
        "actes_confirmes": total,
        "par_couple": [{"auteurs": list(c), "actes": n}
                       for c, n in par_couple.most_common()],
        "centre": centre,
        "actes_touchant_le_centre": actes_centre,
        # 91,5 % sur le corpus au 2026-08-01. C'est LE chiffre de cette couche.
        "part_par_le_centre": round(actes_centre / total, 3) if total else None,
        "actes_sans_le_centre": total - actes_centre,
        "degre": [{"auteur": a, "actes": n} for a, n in degre.most_common()],
        # Combien de passages sont partagés par 1, 2, 3… auteurs distincts. Mesuré : aucun n'est
        # partagé par trois. Un socle textuel commun aux sept auteurs n'existe pas.
        "profondeur": dict(sorted(profondeur.items())),
        "profondeur_maximale": max(profondeur) if profondeur else 0,
        "passages_a_deux_partenaires": sorted(x for x, s in partenaires.items() if len(s) >= 2),
    }


def mot_partage(mesures, lexique_par_motif=None):
    """LA COUCHE FAIBLE — les mots que tous emploient, avec les deux contrôles qui l'empêchent
    de mentir.

    `mesures` : itérable de dicts tels que rendus par `comparaison.densite_comparee`, chacun
    portant `motif` et `auteurs` (liste de {auteur, pour_mille, par_oeuvre, …}).

    Trois classes, et AUCUNE ne nomme une nature :
      • « stable »    — tous l'emploient, dans un rapport resserré. C'est le plus près d'un socle
                        lexical que la mesure puisse aller. Résultat mesuré, et il refroidit : ce
                        qui est stable est surtout de l'allemand courant (`leben`, `mensch`,
                        `auge`, `hand`), pas de la doctrine.
      • « disperse »  — tous l'emploient, mais le rapport est large. CE N'EST PAS UN ÉCART DE
                        DOCTRINE. C'est un endroit où aller lire, et les deux contrôles disent
                        d'abord s'il vaut la peine d'être lu.
      • « partiel »   — au moins un auteur ne l'emploie pas au-dessus du plancher : le mot n'est
                        pas commun, et sa comparaison n'a pas lieu d'être.

    LES DEUX CONTRÔLES, chacun payé par une erreur déjà commise dans ce projet :
      `porte_par_une_oeuvre` — la densité extrême vient d'un seul livre (Breuer et l'hystérie, Rank
          et le traumatisme de la naissance). La mesure décrit alors une ŒUVRE, pas un auteur.
      `extremum_petit_corpus` — l'auteur qui porte l'extremum a le plus petit corpus. Un
          « détecteur » n'utilisant QUE le rapport des effectifs atteint déjà une AUC de 0,576 :
          sans ce drapeau, on publierait une différence de volume pour une différence d'usage.
    """
    out = []
    for m in mesures:
        lignes = [a for a in m["auteurs"] if a.get("pour_mille") is not None]
        if len(lignes) < 2:
            continue
        employent = [a for a in lignes if a["pour_mille"] >= PLANCHER_POUR_MILLE]
        haut = max(lignes, key=lambda a: a["pour_mille"])
        bas = min(lignes, key=lambda a: a["pour_mille"])

        if len(employent) < len(lignes):
            classe, etendue = "partiel", None
        else:
            etendue = round(haut["pour_mille"] / bas["pour_mille"], 1)
            classe = "stable" if etendue <= ETENDUE_STABLE else "disperse"

        concentration = _concentration(haut)
        # Le plus petit corpus de la mesure, pour dire si l'extremum est porté par lui.
        petit = min(lignes, key=lambda a: a["atomes"])
        # QUI A DÉFINI LE MOTIF — colonne porteuse, pas décorative. La ligne d'un auteur sur son
        # propre motif est haute par construction : le lexique a été écrit pour lui. Sans cette
        # information, on lit « Rank domine sur `dichter` » comme un fait d'auteur alors que
        # `dichter` peut venir du lexique de Rank. C'est la règle que `table_des_usages` énonce
        # déjà, et l'omettre ici la contredirait.
        lexique = (lexique_par_motif or {}).get(m["motif"])
        out.append({
            "motif": m["motif"],
            "classe": classe,
            "etendue": etendue,
            "lexique": lexique,
            "haut_est_le_lexicographe": lexique is not None and lexique == haut["auteur"],
            "auteurs_employant": len(employent),
            "auteurs_mesures": len(lignes),
            "haut": haut["auteur"], "pour_mille_haut": haut["pour_mille"],
            "bas": bas["auteur"], "pour_mille_bas": bas["pour_mille"],
            "concentration_haut": concentration,
            "porte_par_une_oeuvre": (concentration is not None
                                     and concentration >= CONCENTRATION_ARTEFACT),
            "extremum_petit_corpus": haut["auteur"] == petit["auteur"],
            "densites": {a["auteur"]: a["pour_mille"] for a in lignes},
        })
    # DÉDOUBLONNAGE SUR CE QUE LE MOTIF SÉLECTIONNE, jamais sur sa chaîne. Deux lexiques écrivent
    # le même concept différemment — `leben|lebendig` chez l'un, `leben|lebendig|lebens` chez
    # l'autre — et les deux chaînes retiennent exactement les mêmes phrases. Comparer les chaînes
    # ne les rapproche pas ; comparer leur VECTEUR DE DENSITÉS le fait, et sans coût. Sans cela le
    # haut du classement montrait trois fois « dichter » sous trois écritures, occupant les places
    # d'autres mots. C'est le même défaut que `appariement.dedoublonner` corrige par les atomes.
    #
    # LE VECTEUR EST UN PROXY DE L'ENSEMBLE D'ATOMES, pas l'ensemble lui-même : deux motifs
    # différents pourraient donner par coïncidence les mêmes densités chez les six auteurs. Le
    # risque est faible (six valeurs au dixième près) et le coût de la vraie mesure est un second
    # parcours du corpus par motif ; si le classement laissait un jour tomber un mot légitime,
    # c'est ici qu'il faudrait passer aux ensembles d'atomes.
    vus, uniques = set(), []
    for x in sorted(out, key=lambda x: (len(x["motif"]), x["motif"])):
        cle = tuple(sorted(x["densites"].items()))
        if cle in vus:
            continue
        vus.add(cle)
        uniques.append(x)
    uniques.sort(key=lambda x: (x["classe"], -(x["etendue"] or 0)))
    return uniques


def _concentration(ligne):
    """Part des porteurs venant de l'œuvre dominante, ou None si le détail manque."""
    par_oeuvre = ligne.get("par_oeuvre") or []
    porteurs = sum(o.get("porteurs", 0) for o in par_oeuvre)
    if not porteurs:
        return None
    return round(max(o.get("porteurs", 0) for o in par_oeuvre) / porteurs, 3)


def tiers_commun(actes):
    """LE FAUX SOCLE — ce qui ressemble à un partage et n'en est pas, avec le tiers nommé.

    Un acte « reclasse » dit : ces deux auteurs recopient la même page d'un TROISIÈME, qui n'est
    pas dans le corpus. Sans la lecture, chacun de ces actes aurait été publié comme un emprunt
    entre auteurs du corpus — c'est-à-dire comme du socle. Ils sont donc exclus, et la liste des
    tiers est rendue avec, parce qu'elle est le résultat : ce que ces auteurs ont vraiment en
    commun, ici, c'est une bibliothèque, pas une doctrine.
    """
    par_tiers = collections.Counter()
    par_couple = collections.Counter()
    for e in actes:
        if e.get("verdict") != "reclasse":
            continue
        par_tiers[_nom_court(e.get("reclasse_vers"))] += 1
        par_couple[tuple(sorted((e["auteur_a"], e["auteur_b"])))] += 1
    return {
        "actes_reclasses": sum(par_tiers.values()),
        "tiers": [{"tiers": t, "actes": n} for t, n in par_tiers.most_common()],
        "tiers_distincts": len(par_tiers),
        "par_couple": [{"auteurs": list(c), "actes": n} for c, n in par_couple.most_common()],
    }


def _nom_court(vers):
    """Le nom du tiers, sans sa référence bibliographique.

    Les verdicts de lecture citent souvent l'ouvrage entier (« Peter Rosegger (Waldheimat, Bd. II,
    "Fremd gemacht") »). Compter ces chaînes telles quelles éclate un même tiers en cinq entrées et
    fait paraître la bibliothèque commune plus large qu'elle n'est — mesuré : 52 « tiers » distincts
    pour une petite vingtaine de noms réels. On coupe donc à la première parenthèse ou virgule.
    """
    if not vers:
        return "(non renseigné)"
    for sep in ("(", ",", " — ", " – ", "«"):
        i = vers.find(sep)
        if i > 0:
            vers = vers[:i]
    return vers.strip(" «»\"'") or "(non renseigné)"


def reserve():
    """Ce que le socle ne dit pas — porté avec lui, jamais relégué en note."""
    return (
        "Ce document répond à « qu'est-ce que ces auteurs partagent ? » par TROIS mesures qui ne "
        "se multiplient jamais, parce que les multiplier est précisément l'erreur mesurée dans ce "
        "corpus : attribuer un acte de citation à chacun des concepts que la phrase touche "
        "fabrique des centaines de « liens » là où il y a quelques centaines d'actes. "
        "Le PARTAGE ATTESTÉ est la seule couche qui prouve un partage de substance, et il est "
        "petit : il ne dessine pas un noyau commun mais une étoile centrée sur Freud, et aucun "
        "passage du corpus n'est partagé par trois auteurs. "
        "Le MOT PARTAGÉ ne prouve aucun partage de pensée — seulement d'usage. Un mot dont l'usage "
        "diverge n'est PAS un désaccord de doctrine : c'est un endroit où aller lire. La mesure "
        "qui prétendrait trancher a été construite puis écartée (6 % de précision, une divergence "
        "confirmée sur seize). "
        "Le TIERS COMMUN est exclu du socle et nommé : deux auteurs qui recopient la même page "
        "d'un troisième se ressemblent sans rien se devoir. "
        "Enfin, ce que le corpus ne montre pas ne veut pas dire que rien n'a eu lieu : entre deux "
        "auteurs de langues différentes la reprise textuelle est aveugle par construction."
    )
