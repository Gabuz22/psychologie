#!/usr/bin/env python3
"""CARTE DES CITATIONS — les actes de citation réels entre auteurs, et rien de plus.

CE QUE CE MODULE EST, ET CE QU'IL A REMPLACÉ.

Le projet visait un graphe de concepts reliés par des liaisons pondérées multi-facteurs. Cette
ambition a été mesurée puis écartée (`documentation/APPARIEMENT_ECARTE.md`) : la similarité de
voisinage ne distingue pas un mot de son synonyme ni de son contraire, et la lecture n'a confirmé
qu'une divergence sur seize.

MAIS UNE SECONDE FAÇON D'ÉCHOUER GUETTAIT, et elle a été mesurée ici avant d'écrire une ligne.
En agrégeant les liens de reprise en arêtes CONCEPT-À-CONCEPT, on obtient 1 366 arêtes — chiffre
flatteur et faux. Chaque atome porte en moyenne 3,5 concepts (jusqu'à 13) : une seule paire de
phrases citée engendre donc par produit croisé des dizaines de « liens » entre des concepts qui
n'ont rien à voir. C'est le même défaut que l'appariement, sous une autre forme : une accumulation
combinatoire qu'on prendrait pour une structure.

L'UNITÉ RETENUE EST DONC L'ACTE DE CITATION, pas le couple de concepts. Il y en a 107 dans tout
le corpus, très inégalement répartis (53 pour Rank ↔ Freud, 1 pour Rank ↔ Ferenczi). C'est peu,
et c'est le chiffre honnête.

LES CONCEPTS SONT DU CONTEXTE, JAMAIS DES ARÊTES. Un événement dit quels concepts il touche, et
distingue ceux que les DEUX passages portent de ceux qu'un seul porte. Les premiers renseignent ;
les seconds sont précisément ce dont le produit croisé faisait des liens.

CE QUE LA CARTE N'EST PAS. Elle ne relie pas des concepts. Elle ne pondère pas une proximité
d'idées. Elle montre où, dans deux œuvres, un texte passe de l'une à l'autre — avec sa preuve,
son verdict de lecture et sa réserve.
"""
import collections

CARTE_VERSION = "1.0.0"


def evenements_de_carte(liens_par_couple, concepts_par_atome):
    """Agrège des liens de reprise DÉJÀ QUALIFIÉS en actes de citation, prêts à cartographier.

    `liens_par_couple` : {(auteur_a, auteur_b): [lien, …]} tels que produits par
        `comparaison.qualifier`, chacun portant a/b (atomes), contenance, force, sens,
        source_tierce, partages, et éventuellement verdict / sens_lu / motif_lecture.
    `concepts_par_atome` : {id_atome: {(groupe, concept), …}}

    Le POIDS d'un événement est le nombre d'atomes qu'il couvre — jamais un produit de concepts.
    Un auteur qui recopie un paragraphe de trois phrases produit un événement de poids 3, non
    trois événements ni trente arêtes.
    """
    from . import comparaison

    out = []
    for (auteur_a, auteur_b), liens in sorted(liens_par_couple.items()):
        for rang, evt in enumerate(comparaison.evenements(liens), 1):
            paires = evt["paires"]
            ca = set().union(*[concepts_par_atome.get(p["a"]["id"], set()) for p in paires]) \
                if paires else set()
            cb = set().union(*[concepts_par_atome.get(p["b"]["id"], set()) for p in paires]) \
                if paires else set()
            # LE POINT QUI ÉVITE LE PRODUIT CROISÉ. On ne rend pas « tous les concepts de A
            # fois tous ceux de B », mais trois ensembles distincts : ce que les deux passages
            # portent ENSEMBLE (par nom de concept, les groupes différant d'un lexique à l'autre),
            # et ce que chacun porte seul. Le premier renseigne ; les deux autres sont ce dont
            # une agrégation naïve aurait fabriqué des arêtes.
            noms_a = {c for _, c in ca}
            noms_b = {c for _, c in cb}
            communs = sorted(noms_a & noms_b)
            out.append({
                "auteur_a": auteur_a, "auteur_b": auteur_b, "rang": rang,
                "poids": len(paires),
                "contenance_max": evt["contenance_max"],
                "contenance_moyenne": evt["contenance_moyenne"],
                "oeuvre_a": paires[0]["a"]["oeuvre"], "oeuvre_b": paires[0]["b"]["oeuvre"],
                "id_debut_a": paires[0]["a"]["id"], "id_fin_a": paires[-1]["a"]["id"],
                "id_debut_b": paires[0]["b"]["id"], "id_fin_b": paires[-1]["b"]["id"],
                # Un événement hérite du sens et du verdict de ses paires, mais seulement s'ils
                # sont UNANIMES : deux paires du même acte qui se contrediraient signaleraient
                # une erreur de regroupement, et il vaut mieux ne rien dire que trancher.
                "force": _unanime(p["force"] for p in paires),
                "sens": _unanime(p["sens"] for p in paires),
                "sens_lu": _unanime(p.get("sens_lu") for p in paires),
                "verdict": _unanime(p.get("verdict") for p in paires),
                "reclasse_vers": _unanime(p.get("reclasse_vers") for p in paires),
                "source_tierce": any(p["source_tierce"] for p in paires),
                "concepts_communs": communs,
                "concepts_a_seul": sorted(noms_a - noms_b),
                "concepts_b_seul": sorted(noms_b - noms_a),
                "partages": _partages(paires),
                # La preuve est rendue DEUX FOIS : dans la forme repliée qui a servi à la
                # comparaison (pour qu'on puisse refaire le calcul) et telle qu'elle est imprimée
                # de chaque côté (pour qu'on puisse la vérifier dans le livre). Les deux diffèrent
                # — l'orthographe d'avant 1901 et les fautes d'OCR sont neutralisées par la
                # première et conservées par la seconde.
                "citation_a": _citation(paires, "a"),
                "citation_b": _citation(paires, "b"),
            })
    out.sort(key=lambda e: (-e["poids"], -e["contenance_max"]))
    return out


def _citation(paires, cote):
    """Le plus long passage partagé, tel qu'il est IMPRIMÉ du côté demandé.

    On cherche dans le texte enchaîné des atomes de ce côté : un acte de citation couvre plusieurs
    phrases, et le passage partagé peut chevaucher deux d'entre elles.
    """
    passages = _partages(paires)
    if not passages:
        return None
    texte = " ".join(p[cote]["texte"] for p in paires)
    for passage in passages:
        origine = retrouver_original(texte, passage)
        if origine:
            return origine
    return None


def _unanime(valeurs):
    """La valeur si toutes les paires s'accordent, None sinon. Le désaccord se tait."""
    v = {x for x in valeurs if x is not None}
    return v.pop() if len(v) == 1 else None


def _partages(paires, combien=6):
    """Les suites de mots partagées, RECOLLÉES en passages entiers — c'est la PREUVE.

    DÉFAUT MESURÉ SUR LA PREMIÈRE VERSION. Le détecteur travaille par suites de six mots et les
    rend triées par ordre ALPHABÉTIQUE ; en afficher les premières donnait douze preuves commençant
    toutes par « a » (« angst um den… », « aber nicht ohne… », « als kind seinen… »). La preuve
    montrée était donc arbitraire, et systématiquement tronquée à six mots.

    Or ces suites se CHEVAUCHENT : quand un auteur en recopie un autre sur dix-sept mots, le
    détecteur produit douze suites de six mots dont chacune partage cinq mots avec la suivante.
    Les recoller restitue le passage réel, qui est autrement plus convaincant qu'un fragment — et
    surtout qui est ce qu'un lecteur peut aller vérifier dans le texte.
    """
    grammes = []
    for p in paires:
        for g in p.get("partages", []):
            if g not in grammes:
                grammes.append(g)
    return sorted(recoller(grammes), key=lambda g: -len(g.split()))[:combien]


def retrouver_original(texte, passage_replie):
    """Le passage TEL QU'IL EST IMPRIMÉ, retrouvé à partir de sa forme repliée.

    DÉFAUT MESURÉ SUR LA PREMIÈRE VERSION. La comparaison travaille sur une forme normalisée qui
    neutralise l'orthographe d'avant 1901 et les gémination instables en OCR : « hattest » y
    devient « hatest », « Stückes » devient « stukes », « Menschen » devient « menschen » mais
    « können » devient « konen ». Publier cette forme-là comme PREUVE était doublement fautif :
    elle est illisible pour un germanophone, et surtout elle n'est pas ce qui est imprimé — donc
    invérifiable, ce qui vide la preuve de son sens.

    On réaligne donc mot à mot : chaque mot de l'atome est replié séparément, ce qui donne les
    mêmes jetons que le repliage global (les espaces protègent les frontières des substitutions),
    puis on retrouve la suite et on rend l'ORIGINAL correspondant, ponctuation comprise.

    Rend None si l'alignement échoue — mieux vaut ne rien montrer qu'un texte reconstruit.
    """
    from . import collation
    mots_origine = (texte or "").split()
    jetons, source = [], []
    for i, mot in enumerate(mots_origine):
        for j in collation.normaliser(mot).split():
            jetons.append(j)
            source.append(i)
    cible = passage_replie.split()
    if not cible or len(cible) > len(jetons):
        return None
    for depart in range(len(jetons) - len(cible) + 1):
        if jetons[depart:depart + len(cible)] == cible:
            return " ".join(mots_origine[source[depart]:source[depart + len(cible) - 1] + 1])
    return None


def recoller(grammes):
    """Recolle des n-grammes qui se chevauchent en passages maximaux.

    Deux suites s'enchaînent si la fin de l'une est le début de l'autre à un mot près. On part de
    celles que rien ne précède, pour ne pas couper un passage en son milieu.
    """
    if not grammes:
        return []
    mots = {g: g.split() for g in grammes}
    n = len(next(iter(mots.values())))
    if n < 2:
        return sorted(grammes)
    suivant, precede = {}, set()
    for g, mg in mots.items():
        for h, mh in mots.items():
            if g != h and mg[1:] == mh[:-1]:
                suivant[g] = h
                precede.add(h)
                break
    passages, vus = [], set()
    for depart in sorted(g for g in mots if g not in precede):
        if depart in vus:
            continue
        chaine, courant = list(mots[depart]), depart
        vus.add(courant)
        while courant in suivant and suivant[courant] not in vus:
            courant = suivant[courant]
            vus.add(courant)
            chaine.append(mots[courant][-1])
        passages.append(" ".join(chaine))
    # Les suites prises dans un cycle (rare : une formule répétée) n'ont pas de départ ; on les
    # rend telles quelles plutôt que de les perdre.
    passages.extend(sorted(g for g in mots if g not in vus))
    return passages


def couples(evenements, auteurs, langues):
    """Résumé par couple d'auteurs — Y COMPRIS LES COUPLES SANS AUCUN ACTE.

    DÉFAUT MESURÉ SUR LA PREMIÈRE VERSION, et c'est le plus grave qu'elle ait porté. Le résumé
    était construit à partir des seuls événements : un couple sans acte ne produisait pas une ligne
    à zéro, il n'existait pas. Neuf couples sur quinze disparaissaient ainsi sans un mot.

    Or cinq de ces neuf sont de LANGUES DIFFÉRENTES, et pour ceux-là la détection est
    mathématiquement impossible : les corpus français et allemand du projet partagent UN SEUL
    n-gramme de six mots sur 41 172 et 1 348 514. Pendant ce temps, Freud consacre à Le Bon un
    chapitre entier de 105 atomes et le nomme dans 31 phrases. Taire ce couple, c'est présenter un
    aveuglement de méthode comme un fait de corpus — l'erreur exacte que ce projet refuse.

    Chaque couple porte donc désormais son `silence` :
      None            — il y a des actes ;
      « langues »     — indétectable par construction, aucune conclusion possible ;
      « aucun_acte »  — même langue, détection possible, rien trouvé. Cela reste une information
                        faible : le détecteur ne voit qu'un texte recopié, pas une lecture.
    """
    par = collections.OrderedDict()
    noms = sorted(auteurs)
    for i, a in enumerate(noms):
        for b in noms[i + 1:]:
            memes_langues = langues.get(a) == langues.get(b)
            par[(a, b)] = {
                "evenements": 0, "atomes": 0, "manifestes": 0, "orientes": 0,
                "lus": 0, "confirmes": 0, "reclasses": 0, "rejetes": 0, "source_tierce": 0,
                "silence": None if memes_langues else "langues",
                "langue_a": langues.get(a), "langue_b": langues.get(b),
            }
    for e in evenements:
        c = par.get((e["auteur_a"], e["auteur_b"]))
        if c is None:
            continue
        c["evenements"] += 1
        c["atomes"] += e["poids"]
        c["manifestes"] += 1 if e["force"] == "manifeste" else 0
        c["orientes"] += 1 if (e["sens"] or e["sens_lu"]) else 0
        c["source_tierce"] += 1 if e["source_tierce"] else 0
        if e["verdict"]:
            c["lus"] += 1
            c[{"confirme": "confirmes", "reclasse": "reclasses",
               "rejete": "rejetes"}[e["verdict"]]] += 1
    for c in par.values():
        if c["evenements"]:
            c["silence"] = None
        elif c["silence"] != "langues":
            c["silence"] = "aucun_acte"
    return [{"auteur_a": a, "auteur_b": b, **v} for (a, b), v in par.items()]


def couverture(evenements, atomes, oeuvres):
    """CE QUE LA CARTE NE VOIT PAS — rendu avec elle, jamais relégué en note.

    Mesuré : les actes touchent 248 atomes sur 54 626, soit 0,45 % du corpus, et 22 œuvres sur 40
    n'y apparaissent JAMAIS. Un lecteur qui ouvre la carte sur « Totem und Tabu » et n'y trouve
    rien doit pouvoir distinguer « Freud n'y cite personne » de « cette œuvre est hors d'atteinte ».

    S'y ajoute un plafond dur, jamais annoncé jusqu'ici : `comparaison.MOTS_MINIMUM` écarte de
    toute comparaison les atomes de moins de vingt mots — 32,8 % du corpus, et jusqu'à 47,6 % chez
    Karl Abraham. Une œuvre peut donc être « muette » pour cette seule raison.
    """
    from . import comparaison
    touches = set()
    for e in evenements:
        touches.add(e["oeuvre_a"])
        touches.add(e["oeuvre_b"])
    atomes_touches = sum(e["poids"] * 2 for e in evenements)
    par_oeuvre = collections.Counter(a["oeuvre"] for a in atomes)
    courts = collections.Counter(a["oeuvre"] for a in atomes
                                 if a.get("nb_mots", 0) < comparaison.MOTS_MINIMUM)
    muettes = []
    for cle, n in sorted(par_oeuvre.items()):
        if cle in touches:
            continue
        meta = oeuvres.get(cle, {})
        muettes.append({
            "oeuvre": cle, "titre": meta.get("titre", cle),
            "auteur": meta.get("auteur", "Sigmund Freud"), "atomes": n,
            "part_trop_courts": round(courts.get(cle, 0) / max(n, 1), 3),
        })
    total = sum(par_oeuvre.values())
    return {
        "atomes_corpus": total,
        "atomes_touches": atomes_touches,
        "part_touchee": round(atomes_touches / max(total, 1), 5),
        "oeuvres_corpus": len(par_oeuvre),
        "oeuvres_muettes": len(muettes),
        "muettes": sorted(muettes, key=lambda m: -m["atomes"]),
        "atomes_trop_courts": sum(courts.values()),
        "part_trop_courte": round(sum(courts.values()) / max(total, 1), 3),
        "mots_minimum": comparaison.MOTS_MINIMUM,
        "actes_non_lus": sum(1 for e in evenements if not e["verdict"]),
        "actes": len(evenements),
    }


def reserve():
    """Ce que la carte ne dit pas — porté avec elle, jamais dans un coin de documentation."""
    return (
        "Cette carte montre des ACTES DE CITATION : des endroits où un texte passe d'une œuvre "
        "à une autre, établis par le partage de suites de six mots et vérifiés par lecture. "
        "Elle ne relie pas des CONCEPTS et ne pondère aucune proximité d'idées — un graphe de "
        "concepts a été tenté, mesuré, puis écarté (voir la documentation). "
        "Le poids d'un acte est le nombre de phrases qu'il couvre, jamais un produit de "
        "concepts : agréger les concepts de part et d'autre donnerait 1 366 « liens » là où il y "
        "a 107 actes réels, chaque phrase portant 3,5 concepts en moyenne. "
        "Les concepts affichés sont du CONTEXTE ; seuls ceux que les deux passages portent "
        "ensemble renseignent. "
        "SURTOUT : ce que la carte ne montre pas ne veut PAS dire que rien n'a eu lieu. Elle "
        "touche 0,45 % du corpus, 22 œuvres sur 40 n'y apparaissent jamais, et un tiers des "
        "phrases sont trop courtes pour être comparables. Entre deux auteurs de langues "
        "différentes elle est aveugle par construction : les corpus français et allemand du "
        "projet partagent UN seul groupe de six mots, alors même que Freud consacre à Le Bon un "
        "chapitre entier. Chaque couple sans acte porte donc la raison de son silence."
    )
