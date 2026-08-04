#!/usr/bin/env python3
"""Contrôles structurels, reproductibles et non interprétatifs des relations D1.

Ce module ne décide ni d'une influence ni d'un accord. Il vérifie uniquement que les objets
stockés respectent le contrat technique nécessaire avant toute lecture scientifique.
"""
import collections
import sqlite3


COUCHES = collections.OrderedDict([
    ("mentions", "nom explicite détecté puis relu ; ne prouve ni lecture ni influence"),
    ("lectures_declarees", "lecture déclarée par un titre de chapitre ; portée locale"),
    ("liens_reprise", "recouvrement textuel candidat, direction datée si elle est décidable"),
    ("carte_actes", "regroupement de liens relus ; poids = nombre de phrases, pas intensité"),
    ("usages", "densité d'un motif lexical, relative à un lexique et une langue"),
    ("socle_liens", "compteurs séparés d'actes et de mentions confirmés"),
    ("socle_densites", "densités lexicales séparées ; aucune fusion avec les liens"),
    ("concept_liens", "cooccurrence intra-auteur corrigée de la densité des atomes"),
])


def _tables(db):
    return {r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def _compter(db, sql):
    return db.execute(sql).fetchone()[0]


def auditer_connexion(db):
    """Rend un rapport sérialisable. Les erreurs sont mécaniques, les alertes méthodologiques."""
    tables = _tables(db)
    constats = []

    def ajouter(code, severite, nombre, message):
        constats.append({"code": code, "severite": severite, "nombre": nombre,
                         "message": message})

    violations = list(db.execute("PRAGMA foreign_key_check"))
    ajouter("cles_etrangeres", "erreur" if violations else "ok", len(violations),
            "violations de clés étrangères")

    if "atomes" in tables:
        n = _compter(db, "SELECT COUNT(*) FROM (SELECT atome_id FROM atomes "
                         "GROUP BY atome_id HAVING COUNT(*) > 1)")
        ajouter("atomes_dupliques", "erreur" if n else "ok", n,
                "identifiants textuels d'atomes dupliqués")

    if "liens_reprise" in tables:
        n = _compter(db, "SELECT COUNT(*) FROM liens_reprise WHERE atome_a = atome_b")
        ajouter("reprises_reflexives", "erreur" if n else "ok", n,
                "reprises reliant un atome à lui-même")
        n = _compter(db, "SELECT COUNT(*) FROM (SELECT atome_a, atome_b FROM liens_reprise "
                         "GROUP BY atome_a, atome_b HAVING COUNT(*) > 1)")
        ajouter("reprises_dupliquees", "erreur" if n else "ok", n,
                "paires de reprise dupliquées")
        n = _compter(db, "SELECT COUNT(*) FROM liens_reprise "
                         "WHERE source_tierce = 1 AND sens IS NOT NULL")
        ajouter("tierce_orientee", "erreur" if n else "ok", n,
                "sources tierces auxquelles une direction a été attribuée")
        n = _compter(db, "SELECT COUNT(*) FROM liens_reprise WHERE verdict IS NULL")
        ajouter("reprises_non_lues", "alerte" if n else "ok", n,
                "candidats de reprise sans verdict de lecture")

    if "carte_actes" in tables:
        colonnes = {r[1] for r in db.execute("PRAGMA table_info(carte_actes)")}
        if "etat_validation" in colonnes:
            non_lus = _compter(db, "SELECT COUNT(*) FROM carte_actes "
                               "WHERE etat_validation='non_lu'")
            discordants = _compter(db, "SELECT COUNT(*) FROM carte_actes "
                                   "WHERE etat_validation='discordant'")
        else:
            # Compatibilité avec l'export du 2026-08-03 : l'acte 96 a un verdict NULL mais porte
            # à la fois `sens_lu` et `reclasse_vers`, traces de deux verdicts élémentaires
            # contradictoires. Ce n'est pas une absence de lecture.
            if {"sens_lu", "reclasse_vers"} <= colonnes:
                discordants = _compter(db, "SELECT COUNT(*) FROM carte_actes WHERE verdict IS NULL "
                                       "AND sens_lu IS NOT NULL AND reclasse_vers IS NOT NULL")
            else:
                discordants = 0
            non_lus = _compter(db, "SELECT COUNT(*) FROM carte_actes WHERE verdict IS NULL") - discordants
        ajouter("actes_non_lus", "alerte" if non_lus else "ok", non_lus,
                "actes réellement sans lecture élémentaire")
        ajouter("actes_validation_discordante", "alerte" if discordants else "ok", discordants,
                "actes agrégeant plusieurs verdicts élémentaires incompatibles")

    if "concepts" in tables:
        n = _compter(db, "SELECT COUNT(*) FROM (SELECT nom FROM concepts "
                         "GROUP BY nom HAVING COUNT(DISTINCT auteur_id) > 1)")
        ajouter("concepts_homonymes", "alerte" if n else "ok", n,
                "noms de concepts présents dans plusieurs lexiques ; l'identité du nom ne "
                "démontre pas l'équivalence conceptuelle")

    attendues = {"version_comparaison", "version_carte", "version_socle_par_couple"}
    if "meta" in tables:
        presentes = {r[0] for r in db.execute("SELECT cle FROM meta")}
        manquantes = sorted(attendues - presentes)
        ajouter("versions_regles", "alerte" if manquantes else "ok", len(manquantes),
                "versions de règles absentes : " + (", ".join(manquantes) or "aucune"))

    inventaire = []
    for table, sens in COUCHES.items():
        if table in tables:
            inventaire.append({"table": table, "lignes": _compter(db, "SELECT COUNT(*) FROM " + table),
                               "sens": sens})
    return {
        "ok": not any(c["severite"] == "erreur" for c in constats),
        "inventaire": inventaire,
        "constats": constats,
    }


def auditer_fichier(chemin):
    """Ouvre une base en lecture seule : l'audit ne peut donc pas la corriger en silence."""
    db = sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)
    try:
        return auditer_connexion(db)
    finally:
        db.close()
