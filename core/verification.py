#!/usr/bin/env python3
"""VÉRIFICATION — la mémoire des jugements portés sur les signaux « à confirmer ».

Un lexique déterministe repère où regarder ; il ne peut pas trancher qu'un auteur se corrige.
Cette couche recueille les verdicts rendus EN CONTEXTE — par un humain ou par un modèle de langage
— et les rend durables : sans elle, chaque relecture repartirait de zéro et le travail de lecture
serait perdu à chaque exécution.

Elle est volontairement SÉPARÉE du corpus : les atomes se recalculent (calcul pur), les jugements
ne se recalculent pas. Les uns vivent dans `derive/`, régénérable ; les autres dans
`verification/`, versionné et cumulatif.

Trois verdicts : « confirme » (le signal dit vrai), « rejete » (faux positif), « reclasse » (signal
réel, mais d'une autre nature). Un signal sans verdict reste « a_confirmer » — jamais promu par
défaut, jamais écarté par défaut.
"""
import json
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER = os.path.join(RACINE, "verification", "signaux_verifies.json")

VERDICTS = ("confirme", "rejete", "reclasse")


def charger():
    """Verdicts connus → {atome_id: {signal, verdict, motif, …}}. Absent = aucun jugement encore."""
    if not os.path.exists(FICHIER):
        return {"meta": {}, "verdicts": {}}
    with open(FICHIER, encoding="utf-8") as f:
        return json.load(f)


def verdict(atome_id, table=None):
    """Jugement porté sur cet atome, ou None s'il n'a pas encore été lu."""
    return (table or charger())["verdicts"].get(atome_id)


def etat(atomes, table=None):
    """Où en est la vérification — ce qui est jugé, ce qui reste, et la précision mesurée.

    Le taux de confirmation n'est pas un score de qualité : c'est l'information qui dit à quel
    point le marqueur mérite confiance, et donc combien de lecture humaine il coûte réellement.
    """
    t = table or charger()
    v = t["verdicts"]
    par_signal = {}
    for a in atomes:
        for s in a["signaux_a_confirmer"]:
            case = par_signal.setdefault(s, {"total": 0, "juges": 0, "confirmes": 0,
                                             "rejetes": 0, "reclasses": 0})
            case["total"] += 1
            j = v.get(a["id"])
            if j and j.get("signal") == s:
                case["juges"] += 1
                case[{"confirme": "confirmes", "rejete": "rejetes",
                      "reclasse": "reclasses"}[j["verdict"]]] += 1
    for case in par_signal.values():
        case["precision_mesuree"] = (round(case["confirmes"] / case["juges"], 2)
                                     if case["juges"] else None)
        case["restants"] = case["total"] - case["juges"]
    return {
        "verifie_par": t.get("meta", {}).get("verifie_par"),
        "par_signal": par_signal,
        "note": ("La précision mesurée ne vaut que pour les candidats DÉJÀ lus. Un signal non jugé "
                 "reste « à confirmer » : ni promu, ni écarté."),
    }


def confirmes(atomes, signal=None, table=None):
    """Les atomes dont le signal a été CONFIRMÉ en contexte — les seuls opposables comme faits."""
    t = table or charger()
    out = []
    for a in atomes:
        j = t["verdicts"].get(a["id"])
        if not j or j["verdict"] != "confirme":
            continue
        if signal and j.get("signal") != signal:
            continue
        out.append((a, j))
    return out


def valider(table=None):
    """Contrôle d'intégrité du registre de verdicts (appelé par les tests)."""
    t = table or charger()
    erreurs = []
    for aid, j in t["verdicts"].items():
        if j.get("verdict") not in VERDICTS:
            erreurs.append("verdict inconnu pour %s : %r" % (aid, j.get("verdict")))
        if not j.get("motif"):
            erreurs.append("verdict sans motif pour %s — un jugement doit être argumenté" % aid)
        if j.get("verdict") == "reclasse" and not j.get("vers"):
            erreurs.append("reclassement sans cible pour %s" % aid)
    return {"ok": not erreurs, "erreurs": erreurs, "juges": len(t["verdicts"])}
