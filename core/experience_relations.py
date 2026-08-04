#!/usr/bin/env python3
"""Préparation déterministe de l'expérience Freud–Stekel, sans vérité humaine fabriquée."""
import hashlib
import json
import re

from . import comparaison, registres_v2

EXPERIENCE_VERSION = "0.1.0-prototype"
GRAINE_NEGATIFS = "freud-stekel-negatifs-v1:2026-08-04"


def _hash(texte):
    return hashlib.sha256((GRAINE_NEGATIFS + "|" + texte).encode("utf-8")).hexdigest()


def _mots(texte):
    return comparaison.aplatir(texte).split()


def _ngrammes(texte, n=6):
    mots = _mots(texte)
    return {" ".join(mots[i:i+n]) for i in range(max(0, len(mots)-n+1))}


def mesures_baseline(texte_a, texte_b, systeme_candidat):
    ma, mb = set(_mots(texte_a)), set(_mots(texte_b))
    ga, gb = _ngrammes(texte_a), _ngrammes(texte_b)
    union = ma | mb
    court = min(len(ga), len(gb))
    replie = comparaison.aplatir(texte_a + " " + texte_b)
    return {
        "b0_noms_explicites": bool(re.search(r"\b(freud|stekel)\b", replie)),
        "b1_contenance_6grammes": round(len(ga & gb) / court, 4) if court else None,
        "b2_jaccard_lexical": round(len(ma & mb) / len(union), 4) if union else None,
        "systeme_actuel_candidat": bool(systeme_candidat),
    }


def _identifiant_aveugle(cle_stable):
    return "item:" + _hash("aveugle|" + cle_stable)[:20]


def _contexte(db, debut_id, fin_id=None, rayon=2):
    """Localise un passage et renvoie son voisinage sans aucune sortie du détecteur."""
    fin_id = fin_id or debut_id
    debut = db.execute("""
        SELECT at.oeuvre_id, at.idx, at.debut, o.cle oeuvre,
               at.annee_min, at.annee_max
        FROM atomes at JOIN oeuvres o ON o.id=at.oeuvre_id WHERE at.atome_id=?
    """, (debut_id,)).fetchone()
    fin = db.execute("""
        SELECT oeuvre_id, idx, fin FROM atomes WHERE atome_id=?
    """, (fin_id,)).fetchone()
    if debut is None or fin is None or debut["oeuvre_id"] != fin["oeuvre_id"]:
        raise ValueError("plage d'atomes introuvable ou inter-œuvres : %s..%s" %
                         (debut_id, fin_id))
    voisins = [dict(r) for r in db.execute("""
        SELECT atome_id, idx, texte FROM atomes
        WHERE oeuvre_id=? AND idx BETWEEN ? AND ? ORDER BY idx
    """, (debut["oeuvre_id"], max(0, debut["idx"] - rayon), fin["idx"] + rayon))]
    return {
        "oeuvre": debut["oeuvre"],
        "date_interval": [debut["annee_min"], debut["annee_max"]],
        "offsets": [debut["debut"], fin["fin"]],
        "context_before": [v for v in voisins if v["idx"] < debut["idx"]],
        "context_after": [v for v in voisins if v["idx"] > fin["idx"]],
    }


def _atomes_auteur(db, auteur, limite=400):
    lignes = [dict(r) for r in db.execute("""
        SELECT at.id id_sql, at.atome_id, at.texte, at.nb_mots, at.annee_min, at.annee_max,
               o.cle oeuvre, o.qualite_source
        FROM atomes at JOIN auteurs a ON a.id=at.auteur_id
        JOIN oeuvres o ON o.id=at.oeuvre_id
        WHERE a.nom=? AND at.nb_mots>=20 ORDER BY at.atome_id
    """, (auteur,))]
    return sorted(lignes, key=lambda x: _hash(x["atome_id"]))[:limite]


def negatifs_apparies(db, nombre=60):
    """Paires non candidates, appariées longueur/date, tirées sans lecture de leur contenu."""
    a = _atomes_auteur(db, "Sigmund Freud")
    b = _atomes_auteur(db, "Wilhelm Stekel")
    liens = {(r[0], r[1]) for r in db.execute("""
        SELECT atome_a, atome_b FROM liens_reprise
        UNION SELECT atome_b, atome_a FROM liens_reprise
    """)}
    utilises = set()
    out = []
    for x in a:
        candidats = [y for y in b if y["id_sql"] not in utilises and
                      (x["id_sql"], y["id_sql"]) not in liens]
        if not candidats:
            break
        y = min(candidats, key=lambda z: (
            abs(x["nb_mots"]-z["nb_mots"]),
            abs(((x["annee_min"]+x["annee_max"])/2)-((z["annee_min"]+z["annee_max"])/2)),
            _hash(x["atome_id"] + "|" + z["atome_id"])))
        utilises.add(y["id_sql"])
        out.append((x, y))
        if len(out) == nombre:
            break
    return out


def construire(db, manifest):
    db.row_factory = __import__("sqlite3").Row
    actes, tirage = registres_v2.echantillon_actes(db)
    aveugles, reference = [], {}
    for a in actes:
        cle = "candidate:acte:%s" % a["id"]
        iid = _identifiant_aveugle(cle)
        texte_a, texte_b = a["citation_a"] or "", a["citation_b"] or ""
        aveugles.append({
            "item_id": iid,
            "source": dict({"id": a["id_debut_a"], "id_fin": a["id_fin_a"],
                            "texte": texte_a, "qualite": a["qualite_a"]},
                           **_contexte(db, a["id_debut_a"], a["id_fin_a"])),
            "target": dict({"id": a["id_debut_b"], "id_fin": a["id_fin_b"],
                            "texte": texte_b, "qualite": a["qualite_b"]},
                           **_contexte(db, a["id_debut_b"], a["id_fin_b"])),
        })
        reference[iid] = {
            "nature": "verdict_legacy_non_gold", "verdict": a["verdict"],
            "strate": a["strate"], "acte_v1": a["id"],
            "baselines": mesures_baseline(texte_a, texte_b, True),
        }
    for n, (a, b) in enumerate(negatifs_apparies(db), 1):
        cle = "controle_non_candidat:%03d" % n
        iid = _identifiant_aveugle(cle)
        aveugles.append({
            "item_id": iid,
            "source": dict({"id": a["atome_id"], "id_fin": a["atome_id"],
                            "texte": a["texte"], "qualite": a["qualite_source"]},
                           **_contexte(db, a["atome_id"])),
            "target": dict({"id": b["atome_id"], "id_fin": b["atome_id"],
                            "texte": b["texte"], "qualite": b["qualite_source"]},
                           **_contexte(db, b["atome_id"])),
        })
        reference[iid] = {
            "nature": "controle_construit_non_gold", "verdict": None,
            "raison": "paire absente des candidats v1",
            "baselines": mesures_baseline(a["texte"], b["texte"], False),
        }
    aveugles.sort(key=lambda x: _hash(x["item_id"]))
    valeurs = [reference[i["item_id"]]["baselines"] for i in aveugles]
    auto = {
        "items": len(aveugles), "candidats_v1": len(actes),
        "controles_non_candidats": len(aveugles)-len(actes),
        "b0_noms_explicites": sum(v["b0_noms_explicites"] for v in valeurs),
        "b1_au_seuil_030": sum((v["b1_contenance_6grammes"] or 0) >= 0.30 for v in valeurs),
        "b2_jaccard_median": sorted(v["b2_jaccard_lexical"] for v in valeurs)[len(valeurs)//2],
        "precision_rappel": "non_calculables_sans_annotations_humaines",
    }
    return {
        "schema_version": EXPERIENCE_VERSION,
        "status": "automatique_preliminaire_sans_verite_humaine",
        "question": ("La couche distingue-t-elle une reprise directe plausible, une source tierce "
                     "partagée et une proximité formulaire sans relation démontrable ?"),
        "pair": ["Sigmund Freud", "Wilhelm Stekel"],
        "freeze": {"corpus_version": manifest["versions"]["corpus_source"],
                   "export_sha256": manifest["reference"]["export_sha256"],
                   "commit": manifest["reference"]["commit_git"],
                   "rule_versions": manifest["versions"]["regles_code_lu"]},
        "categories_predefined": ["directe_plausible", "source_tierce", "formule_commune",
                                  "aucune", "indecidable"],
        "candidate_sampling": tirage,
        "negative_sampling": {"graine": GRAINE_NEGATIFS, "nombre": len(aveugles)-len(actes),
                              "matching": ["nb_mots", "milieu_fenetre_date", "rang_sha256"]},
        "blind_items": aveugles,
        "automatic_reference_not_gold": reference,
        "automatic_preliminary_results": auto,
        "human_annotations": [],
    }


def json_canonique(objet):
    return json.dumps(objet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
