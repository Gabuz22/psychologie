#!/usr/bin/env python3
"""SOCLE PAR COUPLE — le partage entre DEUX auteurs quelconques, à seuil réglable par le lecteur.

CE QUE `core/socle.py` MESURE, ET CE QU'IL NE PEUT PAS FAIRE. Ce module répond à une question que
`core/socle.py` ne pose pas : pour DEUX auteurs précis, quels concepts ont, entre eux, un partage
assez solide — et solide comment, exactement ? `socle.partage_atteste` et `socle.mot_partage`
opèrent au niveau du corpus ENTIER (une étoile globale, une classification stable/disperse/partiel
sur tous les auteurs germanophones à la fois) ; aucun des deux ne descend au grain (auteur_a,
auteur_b, concept) qu'un lecteur qui compare Rank et Ferenczi, par exemple, voudrait pouvoir régler.

POURQUOI UN MODULE SÉPARÉ, ET PAS UNE FONCTION DE PLUS DANS `socle.py`. `test_socle.py` vérifie
mécaniquement qu'aucune fonction de ce module-là ne reçoit à la fois des données de type « actes »
et de type « motifs » — c'est le garde-fou qui empêche de refaire l'erreur déjà mesurée deux fois
dans ce corpus (le produit croisé de `core/carte.py`, l'appariement par voisinage de
`core/appariement.py`). La fonction centrale d'ici DOIT recevoir les deux à la fois, par
construction : elle croise un compte de liens vérifiés et une densité comparée pour le même couple.
L'ajouter dans `socle.py` aurait affaibli ce garde-fou pour les trois fonctions historiques ; un
module séparé le garde intact et porte SON PROPRE refus, adapté : voir les deux, ne jamais les
combiner en un champ.

D'OÙ DEUX AXES QUI NE SE FUSIONNENT JAMAIS EN UN SEUL CHIFFRE, ni entre eux, ni À L'INTÉRIEUR
D'EUX-MÊMES :

  AXE 1 — LIENS VÉRIFIÉS. Deux compteurs, jamais additionnés : `actes_confirmes` (un texte
  partagé, relu) et `mentions_confirmees` (un nom écrit, relu). Le schéma D1 le dit déjà en toutes
  lettres pour la table `mentions` : « ELLES NE SONT JAMAIS FUSIONNÉES AVEC LES ACTES. […] Les
  additionner ferait exactement l'erreur que la carte a été bâtie pour éviter. » — la preuve
  chiffrée y est aussi : Ferenczi nomme Freud dans 960 phrases, ne partage un texte avec lui que
  dans 9. Les additionner ferait passer un satellite lointain pour un proche.

  AXE 2 — DENSITÉ COMPARÉE. Le pour-mille d'usage du concept chez chacun des deux auteurs, motif
  par motif (un concept peut être défini par le lexique de l'un ET par celui de l'autre, avec des
  motifs différents — les deux restent distincts, jamais moyennés), avec le garde-fou lexicographe
  déjà établi par `socle.mot_partage` : la ligne d'un auteur sur SON PROPRE motif est haute par
  construction.

  ET LES DEUX AXES NE SE COMBINENT JAMAIS ENTRE EUX. `donnees.js:RESERVE_DOSSIER` porte déjà cette
  règle pour une autre couche du projet : « Ne jamais additionner ni moyenner ces signaux en un
  score de « force du lien » : leurs unités ne sont pas comparables, et ce serait inventer une
  mesure que le corpus ne fournit pas. » Un compte d'événements vérifiés et un pour-mille d'usage
  n'ont pas la même unité — ce module ne prétend pas les rendre comparables, il les affiche l'un à
  côté de l'autre et laisse deux seuils indépendants filtrer chacun le sien.

CE QUE CE MODULE REFUSE DE DIRE, comme `socle.py` avant lui : qu'un concept qui passe un seuil
désigne un accord, une dette ou une doctrine partagée. Un concept candidat est un endroit où deux
mesures indépendantes sont assez hautes pour être montrées — rien de plus.
"""
import collections

SOCLE_PAR_COUPLE_VERSION = "1.0.0"


def actes_confirmes_par_concept(evenements):
    """{(auteur_a, auteur_b) trié: Counter({concept: nombre d'actes confirmés})}.

    `evenements` : sortie de `carte.evenements_de_carte`, chaque événement portant `verdict` et
    `concepts_communs`. On compte des ACTES, jamais des atomes ni un poids : un acte qui couvre
    dix phrases ne vaut pas dix fois plus qu'un acte qui n'en couvre qu'une — mirror de
    `socle.partage_atteste`, qui compte les actes confirmés de la même façon.
    """
    out = collections.defaultdict(collections.Counter)
    for e in evenements:
        if e.get("verdict") != "confirme":
            continue
        cle = tuple(sorted((e["auteur_a"], e["auteur_b"])))
        for concept in e.get("concepts_communs") or ():
            out[cle][concept] += 1
    return out


def mentions_confirmees_par_concept(mentions_confirmees, concepts_par_atome):
    """{(auteur_a, auteur_b) trié: Counter({concept: nombre de mentions confirmées})}.

    `mentions_confirmees` : itérable de dicts {auteur, auteur_nomme, atome_id}, DÉJÀ filtrés à
    verdict confirmé par l'appelant. `concepts_par_atome` : sortie de `carte.concepts_par_atome`.

    Le concept associé à une mention est celui que l'ATOME PORTE, DANS LE LEXIQUE DE L'AUTEUR QUI
    NOMME — jamais celui de l'auteur nommé : même règle que `donnees.js:dossierExterne`
    (`m.auteur_id = c.auteur_id`). Une mention dit qu'un nom est écrit dans un contexte donné ;
    elle ne dit rien du lexique de la personne nommée.
    """
    out = collections.defaultdict(collections.Counter)
    for m in mentions_confirmees:
        cle = tuple(sorted((m["auteur"], m["auteur_nomme"])))
        for _, concept in concepts_par_atome.get(m["atome_id"], ()):
            out[cle][concept] += 1
    return out


def densites_du_concept(usages, concept, auteur_a, auteur_b):
    """Les variantes (lexique, motif) qui mesurent CE concept chez auteur_a et/ou auteur_b.

    `usages` : sortie de `comparaison.table_des_usages` (lignes plates {sous_concept, lexique,
    motif, auteur, pour_mille, …}).

    → [{"lexique", "motif", "pour_mille_a", "pour_mille_b", "lexicographe": "a"|"b"|None}, …]

    0, 1 ou 2 lignes — jamais fusionnées entre elles : deux lexiques distincts peuvent écrire le
    même NOM de concept avec des motifs regex DIFFÉRENTS, et les fusionner ferait l'erreur que
    `socle.mot_partage` évite déjà en dédoublonnant sur le VECTEUR de densités, pas sur le nom.
    """
    par_motif = {}
    for u in usages:
        if u["sous_concept"] != concept or u["auteur"] not in (auteur_a, auteur_b):
            continue
        entree = par_motif.setdefault(u["motif"], {"lexique": u["lexique"], "densites": {}})
        entree["densites"][u["auteur"]] = u["pour_mille"]
    out = []
    for motif, e in sorted(par_motif.items()):
        lexique = e["lexique"]
        out.append({
            "lexique": lexique,
            "motif": motif,
            "pour_mille_a": e["densites"].get(auteur_a),
            "pour_mille_b": e["densites"].get(auteur_b),
            "lexicographe": "a" if lexique == auteur_a else ("b" if lexique == auteur_b else None),
        })
    return out


def candidats(auteur_a, auteur_b, actes_par_concept, mentions_par_concept, usages):
    """Pour UNE paire d'auteurs, tous les concepts candidats, avec leurs deux axes séparés.

    `actes_par_concept`, `mentions_par_concept` : les Counter de CE couple, déjà extraits par
    l'appelant (`.get(tuple(sorted((auteur_a, auteur_b))), Counter())`) des sorties de
    `actes_confirmes_par_concept`/`mentions_confirmees_par_concept`.
    `usages` : sortie complète de `comparaison.table_des_usages` (filtrée en interne par concept).

    → {"auteur_a", "auteur_b", "concepts": [
         {"concept", "actes_confirmes", "mentions_confirmees", "densites"}, …
       ]}   # trié par -actes_confirmes puis nom

    UNION des trois sources, jamais leur intersection : un concept dont la densité est mesurée
    mais qui n'a encore aucun lien vérifié reste dans la liste (à 0 acte, 0 mention) — sinon
    baisser le seuil de l'axe 1 à zéro ne le ferait jamais apparaître, et un lecteur qui veut voir
    « tout ce qui est mesurable » n'y arriverait jamais.
    """
    concepts_avec_densite = {u["sous_concept"] for u in usages
                             if u["auteur"] in (auteur_a, auteur_b)}
    concepts = set(actes_par_concept) | set(mentions_par_concept) | concepts_avec_densite
    lignes = [{
        "concept": concept,
        "actes_confirmes": actes_par_concept.get(concept, 0),
        "mentions_confirmees": mentions_par_concept.get(concept, 0),
        "densites": densites_du_concept(usages, concept, auteur_a, auteur_b),
    } for concept in concepts]
    lignes.sort(key=lambda c: (-c["actes_confirmes"], c["concept"]))
    return {"auteur_a": auteur_a, "auteur_b": auteur_b, "concepts": lignes}


def toutes_les_paires(evenements, mentions_confirmees, concepts_par_atome, usages, auteurs, langues):
    """`candidats(...)` pour CHAQUE couple d'auteurs, Y COMPRIS LES COUPLES SANS CANDIDAT.

    Même discipline que `carte.couples` : un couple qu'on tait présente un aveuglement de méthode
    (deux langues différentes, la comparaison est aveugle par construction) comme un fait de
    corpus (« rien à partager »). Chaque résultat porte un `silence` :
      None              — au moins un concept candidat ;
      « langues »       — auteurs de langues différentes, indétectable par construction ;
      « aucun_candidat» — même langue, rien trouvé.
    """
    actes_par_couple = actes_confirmes_par_concept(evenements)
    mentions_par_couple = mentions_confirmees_par_concept(mentions_confirmees, concepts_par_atome)
    noms = sorted(auteurs)
    out = []
    for i, a in enumerate(noms):
        for b in noms[i + 1:]:
            cle = (a, b)
            r = candidats(a, b, actes_par_couple.get(cle, collections.Counter()),
                          mentions_par_couple.get(cle, collections.Counter()), usages)
            if r["concepts"]:
                r["silence"] = None
            elif langues.get(a) != langues.get(b):
                r["silence"] = "langues"
            else:
                r["silence"] = "aucun_candidat"
            out.append(r)
    return out


def reserve():
    """Ce que ce module refuse de dire — porté avec chaque liste qu'il produit, jamais séparé."""
    return (
        "DEUX AXES, JAMAIS FUSIONNÉS EN UN SEUL CHIFFRE. `actes_confirmes` (texte partagé, relu) "
        "et `mentions_confirmees` (nom écrit, relu) ne s'additionnent JAMAIS : un acte et une "
        "mention ne sont pas la même sorte de fait, et les additionner ferait passer un satellite "
        "lointain pour un proche — Ferenczi nomme Freud dans 960 phrases, ne partage un texte "
        "avec lui que dans 9. `densites` (l'usage comparé du mot) ne se combine avec aucun des "
        "deux comptes de l'axe 1 : un pour-mille d'usage et un compte de liens vérifiés n'ont pas "
        "la même unité, et les combiner inventerait une mesure que le corpus ne fournit pas — "
        "c'est l'erreur exacte que ce projet interdit déjà ailleurs. Aucun champ ici ne nomme la "
        "NATURE du rapport entre deux auteurs : un concept qui passe un seuil n'est ni un accord "
        "ni une dette, seulement un endroit où une mesure précise est assez haute pour être "
        "montrée. Baisser un seuil élargit une liste ; il ne change jamais un chiffre déjà "
        "affiché."
    )
