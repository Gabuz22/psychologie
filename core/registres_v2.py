#!/usr/bin/env python3
"""Générateurs déterministes des registres exploratoires v2."""
import collections
import hashlib
import json
import sqlite3

from . import relations_v2

REGISTRES_V2_VERSION = "0.1.0-prototype"
GRAINE_EXPERIENCE = "freud-stekel-v1:2026-08-04"


def _rang(stable_id, graine=GRAINE_EXPERIENCE):
    return hashlib.sha256((graine + "|" + str(stable_id)).encode("utf-8")).hexdigest()


def registre_translexical(db):
    """Les libellés présents dans plusieurs lexiques, sans alignement sémantique implicite."""
    db.row_factory = sqlite3.Row
    noms = [r[0] for r in db.execute("""
        SELECT nom FROM concepts GROUP BY nom HAVING COUNT(DISTINCT auteur_id)>1 ORDER BY nom
    """)]
    candidats = []
    for nom in noms:
        entrees = []
        for c in db.execute("""
            SELECT c.id, c.nom, c.groupe, c.n_atomes, a.id auteur_id, a.nom auteur
            FROM concepts c JOIN auteurs a ON a.id=c.auteur_id
            WHERE c.nom=? ORDER BY a.nom, c.id
        """, (nom,)):
            passages = [dict(r) for r in db.execute("""
                SELECT at.atome_id, o.cle oeuvre, substr(at.texte,1,240) extrait
                FROM atome_concepts ac JOIN atomes at ON at.id=ac.atome_id
                JOIN oeuvres o ON o.id=at.oeuvre_id
                WHERE ac.concept_id=? ORDER BY o.cle, at.idx LIMIT 3
            """, (c["id"],))]
            usages = [dict(r) for r in db.execute("""
                SELECT al.nom auteur_mesure, u.langue, u.motif, u.porteurs, u.pour_mille,
                       lx.nom lexicographe
                FROM usages u JOIN auteurs al ON al.id=u.auteur_id
                JOIN auteurs lx ON lx.id=u.lexique
                WHERE u.sous_concept=? AND u.lexique=?
                ORDER BY al.nom, u.motif
            """, (nom, c["auteur_id"]))]
            entrees.append({
                "concept_entry_id": c["id"], "auteur_id": c["auteur_id"],
                "auteur": c["auteur"], "forme_observee": c["nom"], "groupe": c["groupe"],
                "atomes": c["n_atomes"],
                "definition": {"statut": "non_documente", "valeur": None},
                "passages_disponibles": passages,
                "resultats_lexicaux": usages,
            })
        groupes = sorted({e["groupe"] for e in entrees})
        motifs = sorted({u["motif"] for e in entrees for u in e["resultats_lexicaux"]})
        candidats.append({
            "id": "translexical:" + nom,
            "forme_observee": nom,
            "lexiques_concernes": [e["auteur"] for e in entrees],
            "auteurs_concernes": [e["auteur"] for e in entrees],
            "entrees": entrees,
            "divergences_automatiques": {
                "groupes_distincts": groupes,
                "nombre_groupes": len(groupes),
                "nombre_motifs_distincts": len(motifs),
                "motifs_distincts": motifs,
            },
            "propositions_equivalence": [],
            "statut_automatique": "identite_terminologique_seulement",
            "statut_humain": "homonymie_non_examinee",
            "raison": ("libellé identique dans plusieurs lexiques ; aucune identité conceptuelle "
                       "n'est déduite du nom, du groupe ou du motif"),
        })
    return {
        "schema_version": REGISTRES_V2_VERSION,
        "type": "candidats_translexicaux",
        "nombre": len(candidats),
        "statuts_autorises": [
            "homonymie_non_examinee", "identite_terminologique_seulement",
            "equivalence_candidate", "equivalence_partielle_candidate",
            "opposition_ou_incompatibilite_candidate", "non_comparabilite", "rejet",
            "indecidable", "valide_humainement",
        ],
        "candidats": candidats,
    }


def _bande(contenance):
    if contenance < 0.50:
        return "0.30-0.49"
    if contenance < 0.70:
        return "0.50-0.69"
    return "0.70-1.00"


def echantillon_actes(db, auteur_a="Sigmund Freud", auteur_b="Wilhelm Stekel", par_strate=3):
    """Tirage sans préférence positive : verdict × bande, rang par hash d'une graine publiée."""
    db.row_factory = sqlite3.Row
    lignes = [dict(r) for r in db.execute("""
        SELECT ca.*, aa.nom nom_a, ab.nom nom_b, oa.cle cle_a, ob.cle cle_b,
               oa.qualite_source qualite_a, ob.qualite_source qualite_b,
               oa.langue langue_a, ob.langue langue_b,
               oa.annee_oeuvre annee_a, ob.annee_oeuvre annee_b
        FROM carte_actes ca JOIN auteurs aa ON aa.id=ca.auteur_a
        JOIN auteurs ab ON ab.id=ca.auteur_b
        JOIN oeuvres oa ON oa.id=ca.oeuvre_a JOIN oeuvres ob ON ob.id=ca.oeuvre_b
        WHERE (aa.nom=? AND ab.nom=?) OR (aa.nom=? AND ab.nom=?)
        ORDER BY ca.id
    """, (auteur_a, auteur_b, auteur_b, auteur_a))]
    strates = collections.defaultdict(list)
    for r in lignes:
        strate = "%s:%s" % (r["verdict"] or "sans_verdict", _bande(r["contenance_max"]))
        strates[strate].append(r)
    choisis = []
    for strate in sorted(strates):
        candidats = sorted(strates[strate], key=lambda r: _rang(r["id"]))
        for r in candidats[:par_strate]:
            r["strate"] = strate
            r["rang_deterministe"] = _rang(r["id"])
            choisis.append(r)
    return sorted(choisis, key=lambda r: r["id"]), {
        "graine": GRAINE_EXPERIENCE,
        "methode": "stratification verdict × bande de contenance ; tri SHA-256 ; n par strate",
        "par_strate": par_strate,
        "population": len(lignes),
        "strates_population": {k: len(v) for k, v in sorted(strates.items())},
        "selection": len(choisis),
    }


def _preuve(acte, cote):
    return {
        "id": "preuve:acte:%s:%s" % (acte["id"], cote),
        "target": {"type": "plage_atomes", "id": "%s..%s" % (
            acte["id_debut_" + cote], acte["id_fin_" + cote])},
        "source": acte["cle_" + cote],
        "excerpt": acte["citation_" + cote],
        "provenance": acte["qualite_" + cote],
    }


def relations_prototypes(actes, corpus_version, rule_version):
    """Relations proposées sur le tirage ; les verdicts legacy ne deviennent pas humains."""
    relations = []
    for a in actes:
        base_id = "prototype:acte:%s" % a["id"]
        verdict = a["verdict"]
        type_relation = ("reprise_explicite" if verdict == "confirme"
                         else "correspondance_exploratoire")
        etat = "rejetee" if verdict == "rejete" else "proposee"
        annotation = {
            "id": "annotation:legacy:acte:%s" % a["id"],
            "agent_kind": "legacy_inconnu", "agent_id": "unknown",
            "independent": False, "proposition": verdict or "discordant",
            "validation_state": "indecidable" if verdict is None else etat,
            "confidence_state": "inconnue", "confidence_value": None,
            "guide_version": None,
        }
        contre = []
        if verdict in ("reclasse", "rejete") and a.get("reclasse_vers"):
            contre.append({
                "id": "contrepreuve:acte:%s" % a["id"],
                "target": {"type": "acte_v1", "id": str(a["id"])},
                "source": "verification/reprises_lues.json",
                "excerpt": a.get("reclasse_vers"),
                "provenance": "legacy_inconnu",
            })
        direction = ({"state": "reconstruite", "value": a["sens"]}
                     if a.get("sens") else {"state": "inconnue", "value": None})
        relation = {
            "id": base_id, "type": type_relation,
            "source": {"type": "plage_atomes", "id": "%s..%s" %
                       (a["id_debut_a"], a["id_fin_a"])},
            "target": {"type": "plage_atomes", "id": "%s..%s" %
                       (a["id_debut_b"], a["id_fin_b"])},
            "direction": direction,
            "period": {"state": "reconstruite", "value": [a["annee_a"], a["annee_b"]]},
            "validation_state": etat,
            "evidence": [_preuve(a, "a"), _preuve(a, "b")],
            "counterevidence": contre,
            "dimensions": {
                "contenance_textuelle": relations_v2.dimension(
                    "calculee", a["contenance_max"], "proportion",
                    "intersection n-grammes / côté court", rule_version,
                    "maximum de l'acte, pas probabilité"),
                "recurrence": relations_v2.dimension(
                    "calculee", a["poids"], "paires_de_phrases",
                    "agrégation contiguë carte", rule_version,
                    "ne démontre pas des passages indépendants"),
                "passages_independants": relations_v2.dimension(
                    "non_calculable", limitations="contiguïté et dépendance non annotées"),
                "qualite_provenance": relations_v2.dimension(
                    "observee", [a["qualite_a"], a["qualite_b"]], "classe_source"),
                "qualite_ocr": relations_v2.dimension(
                    "observee", [a["qualite_a"], a["qualite_b"]], "classe_source"),
                "dependance_traduction": relations_v2.dimension("observee", False, "booleen"),
                "confiance_annotation": relations_v2.dimension(
                    "inconnue", limitations="annotateur et méthode legacy non documentés"),
            },
            "annotations": [annotation],
            "interpretation": None,
            "coverage_limit": "détecteur de reprises sur textes de même langue, seuil 20 mots",
            "history": [{"ordinal": 1, "action": "importe_prototype",
                         "actor": "bin/generer_registres_v2.py"}],
            "corpus_version": corpus_version, "rule_version": rule_version,
            "legacy": {"table": "carte_actes", "id": a["id"], "force": a["force"],
                       "force_canonical": False, "strate": a["strate"]},
        }
        erreurs = relations_v2.valider_relation(relation)
        if erreurs:
            raise ValueError("relation %s invalide : %s" % (relation["id"], erreurs))
        relations.append(relation)
        if verdict == "reclasse":
            tierce = dict(relation)
            tierce.update({
                "id": base_id + ":source_tierce",
                "type": "source_tierce_partagee",
                "direction": {"state": "non_applicable", "value": None},
                "validation_state": "proposee",
                "evidence": contre or relation["evidence"],
                "counterevidence": [],
                "interpretation": "cible du reclassement legacy, provenance d'annotateur inconnue",
            })
            if relations_v2.valider_relation(tierce):
                raise ValueError("relation tierce invalide")
            relations.append(tierce)
    return relations


def prototype_probatoire(db, corpus_version, rule_version):
    actes, tirage = echantillon_actes(db)
    relations = relations_prototypes(actes, corpus_version, rule_version)
    return {
        "schema_version": relations_v2.RELATIONS_V2_VERSION,
        "status": "prototype_automatique_non_valide_humainement",
        "pair": ["Sigmund Freud", "Wilhelm Stekel"],
        "tirage": tirage,
        "relations": relations,
        "human_annotations": [],
        "warning": "aucune proposition ou annotation legacy n'est présentée comme validation humaine",
    }


def charger_base(chemin):
    return sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)


def json_canonique(objet):
    return json.dumps(objet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
