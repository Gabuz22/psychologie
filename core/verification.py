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


def cle(atome):
    """Clé d'un atome dans le registre : son EMPREINTE, jamais son rang.

    Les identifiants positionnels (« oeuvre:aN ») se décalent dès qu'on retire du paratexte en
    amont — le nettoyage des blocs de notes Wikisource, intercalés dans les Neue Folge, a suffi à
    faire pointer 30 jugements dans le vide. Un verdict porte sur une PHRASE : il doit la suivre.
    """
    return atome["empreinte"] if isinstance(atome, dict) else atome


def verdict(atome, table=None):
    """Jugement porté sur cet atome, ou None s'il n'a pas encore été lu."""
    return (table or charger())["verdicts"].get(cle(atome))


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
            j = v.get(cle(a))
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
        j = t["verdicts"].get(cle(a))
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


# ------------------------------------------------------------------------------------------
# REGISTRE DES REPRISES LUES — même doctrine, autre unité.
#
# Le registre ci-dessus juge un ATOME. Une reprise est un COUPLE d'atomes : le jugement ne porte
# ni sur l'un ni sur l'autre, mais sur le rapport entre les deux. Il lui faut donc sa propre clé
# — le couple d'empreintes — et son propre fichier.
#
# Ce que la lecture ajoute que le calcul ne peut pas donner : le détecteur voit un partage de
# mots et s'arrête à la phrase ; le lecteur remonte de quelques atomes et trouve l'attribution
# (« Ich zitiere wörtlich », « nach Freud », un appel de note). C'est cette attribution qui
# oriente le lien, y compris quand les fenêtres de datation se chevauchent et que le calcul doit
# répondre INDÉCIDABLE.
#
# Quatrième verdict, propre à cette unité : « reclasse » avec une cible qui n'est ni A ni B. Deux
# auteurs citant le même passage d'un TIERS se ressemblent sans rien se devoir. Le calcul ne le
# voit pas ; la lecture, oui.
FICHIER_REPRISES = os.path.join(RACINE, "verification", "reprises_lues.json")


def charger_reprises():
    if not os.path.exists(FICHIER_REPRISES):
        return {"meta": {}, "verdicts": {}}
    with open(FICHIER_REPRISES, encoding="utf-8") as f:
        return json.load(f)


def cle_reprise(emp_a, emp_b):
    """Clé d'un couple : les deux empreintes TRIÉES, pour que l'ordre de lecture ne compte pas."""
    return "|".join(sorted((emp_a, emp_b)))


def verdict_reprise(emp_a, emp_b, table=None):
    return (table or charger_reprises())["verdicts"].get(cle_reprise(emp_a, emp_b))


def valider_reprises(table=None):
    t = table or charger_reprises()
    erreurs = []
    for k, j in t["verdicts"].items():
        if j.get("verdict") not in VERDICTS:
            erreurs.append("verdict inconnu pour %s : %r" % (k, j.get("verdict")))
        if not j.get("motif"):
            erreurs.append("verdict sans motif pour %s — un jugement doit être argumenté" % k)
        if j.get("verdict") == "reclasse" and not j.get("vers"):
            erreurs.append("reclassement sans cible pour %s" % k)
        if j.get("sens_lu") not in (None, "a_vers_b", "b_vers_a"):
            erreurs.append("sens illisible pour %s : %r" % (k, j.get("sens_lu")))
        # `sens_lu` est relatif à l'ordre (a, b) DÉCLARÉ dans le verdict, que la clé triée perd.
        # Sans les identifiants d'origine, on ne saurait plus à qui « a » renvoie.
        if j.get("sens_lu") and not (j.get("id_a") and j.get("id_b")):
            erreurs.append("sens donné sans id_a/id_b pour %s — le sens deviendrait ambigu" % k)
        # ET SURTOUT : sans `empreinte_a`, l'ordre est INDEVINABLE. Les identifiants ci-dessus
        # sont positionnels et dérivent au moindre changement de paratexte ; s'y fier a fait
        # publier seize emprunts à l'envers avant que la mesure ne le montre. L'empreinte est le
        # hachage du texte du côté a : elle ne dérive pas, et elle tranche sans rien déduire.
        if j.get("sens_lu") and not j.get("empreinte_a"):
            erreurs.append("sens donné sans empreinte_a pour %s — l'ordre (a, b) serait retrouvé "
                           "par des identifiants positionnels, qui dérivent" % k)
        if j.get("empreinte_a") and j["empreinte_a"] not in k.split("|"):
            erreurs.append("empreinte_a de %s n'est pas l'un des deux côtés du couple" % k)
    return {"ok": not erreurs, "erreurs": erreurs, "juges": len(t["verdicts"])}
