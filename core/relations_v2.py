#!/usr/bin/env python3
"""Contrat minimal des relations multiples et multidimensionnelles v2.

Une paire d'objets peut porter plusieurs relations simultanées. Aucune fonction de ce module ne
calcule ni ne tolère un score synthétique de relation.
"""
import json

RELATIONS_V2_VERSION = "0.1.0-prototype"

TYPES_RELATION = frozenset({
    "proximite_terminologique", "reprise_explicite", "analogie_fonctionnelle",
    "convergence_propositionnelle", "opposition_doctrinale", "transformation_possible",
    "filiation_historique_documentee", "filiation_historique_plausible_non_etablie",
    "correspondance_exploratoire", "source_tierce_partagee",
})
ETATS_VALIDATION = frozenset({
    "proposee", "candidate_automatique", "contestee", "validee_humainement",
    "rejetee", "indecidable",
})
ETATS_VALEUR = frozenset({
    "observee", "calculee", "annotee", "reconstruite", "inconnue",
    "non_applicable", "non_calculable", "contradictoire",
})
ETATS_SANS_VALEUR = frozenset({"inconnue", "non_applicable", "non_calculable"})
DIRECTIONS = frozenset({"a_vers_b", "b_vers_a", "symetrique", "indecidable", "non_applicable"})
TYPES_ALIGNEMENT = frozenset({
    "equivalence", "equivalence_partielle", "proximite", "plus_large",
    "plus_etroit", "homonymie", "opposition", "non_comparabilite", "indecidable",
})
BASES_ALIGNEMENT = frozenset({
    "libelle_identique", "definitions_comparees", "passages_compares",
    "fonctions_comparees", "annotation_experte", "source_secondaire_documentee",
})

DIMENSIONS = {
    "contenance_textuelle": ("calculee", "proportion", "[0,1]"),
    "passages_independants": ("calculee", "compte", "entier >= 0"),
    "recurrence": ("calculee", "compte", "entier >= 0"),
    "dispersion_oeuvres": ("calculee", "compte_oeuvres", "entier >= 0"),
    "localisation_temporelle": ("reconstruite", "intervalle_annees", "intervalle ou inconnu"),
    "proximite_lexicale": ("calculee", "mesure_versionnee", "dépend de la règle"),
    "explicitation": ("annotee", "classe", "explicite|implicite|indecidable"),
    "orientation": ("reconstruite", "classe", "DIRECTIONS"),
    "compatibilite_fonctionnelle": ("annotee", "classe", "compatible|incompatible|mixte"),
    "contradiction": ("annotee", "classe", "presente|absente|indecidable"),
    "qualite_provenance": ("observee", "classe", "source et édition"),
    "qualite_ocr": ("observee", "classe", "relu|ocr|suspect"),
    "dependance_traduction": ("observee", "booleen", "true|false"),
    "couverture_documentaire": ("calculee", "proportion", "[0,1] ou non_calculable"),
    "confiance_annotation": ("annotee", "classe", "auto-évaluation, jamais vérité"),
}

JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://gabuz22.github.io/psychologie/schemas/relations-v2.schema.json",
    "title": "Relation analytique multiple v2",
    "type": "object",
    "additionalProperties": True,
    "required": ["id", "type", "source", "target", "direction", "validation_state",
                 "evidence", "counterevidence", "dimensions", "annotations", "history",
                 "corpus_version", "rule_version"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "type": {"enum": sorted(TYPES_RELATION)},
        "source": {"$ref": "#/$defs/objectRef"},
        "target": {"$ref": "#/$defs/objectRef"},
        "direction": {"$ref": "#/$defs/stateValue"},
        "validation_state": {"enum": sorted(ETATS_VALIDATION)},
        "evidence": {"type": "array", "items": {"$ref": "#/$defs/evidence"}},
        "counterevidence": {"type": "array", "items": {"$ref": "#/$defs/evidence"}},
        "dimensions": {
            "type": "object",
            "propertyNames": {"enum": sorted(DIMENSIONS)},
            "additionalProperties": {"$ref": "#/$defs/dimension"},
        },
        "annotations": {"type": "array", "items": {"$ref": "#/$defs/annotation"}},
        "history": {"type": "array", "items": {"type": "object"}},
        "corpus_version": {"type": "string", "minLength": 1},
        "rule_version": {"type": "string", "minLength": 1},
    },
    "not": {"anyOf": [
        {"required": ["score"]}, {"required": ["force_globale"]},
        {"required": ["influence_score"]}, {"required": ["aggregate_score"]},
    ]},
    "$defs": {
        "objectRef": {
            "type": "object", "additionalProperties": False,
            "required": ["type", "id"],
            "properties": {"type": {"type": "string", "minLength": 1},
                           "id": {"type": "string", "minLength": 1}},
        },
        "stateValue": {
            "type": "object", "required": ["state", "value"],
            "properties": {"state": {"enum": sorted(ETATS_VALEUR)}, "value": {}},
        },
        "evidence": {
            "type": "object", "required": ["id", "target", "source", "provenance"],
            "properties": {"id": {"type": "string"}, "target": {"$ref": "#/$defs/objectRef"},
                           "source": {"type": "string"}, "excerpt": {"type": ["string", "null"]},
                           "provenance": {"type": "string"}},
        },
        "dimension": {
            "type": "object", "required": ["state", "value"],
            "properties": {"state": {"enum": sorted(ETATS_VALEUR)}, "value": {},
                           "unit": {"type": ["string", "null"]},
                           "rule": {"type": ["string", "null"]},
                           "rule_version": {"type": ["string", "null"]},
                           "limitations": {"type": ["string", "null"]}},
        },
        "annotation": {
            "type": "object", "required": ["id", "agent_kind", "agent_id", "independent",
                                             "proposition", "validation_state"],
            "properties": {"id": {"type": "string"},
                           "agent_kind": {"enum": ["humain", "automatique", "legacy_inconnu"]},
                           "agent_id": {"type": "string"}, "independent": {"type": "boolean"},
                           "proposition": {"type": "string"},
                           "validation_state": {"enum": sorted(ETATS_VALIDATION)}},
        },
    },
}

SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS v2_runs (
  id TEXT PRIMARY KEY,
  schema_version TEXT NOT NULL,
  corpus_version TEXT NOT NULL,
  rule_version TEXT NOT NULL,
  source_export_sha256 TEXT NOT NULL,
  mode TEXT NOT NULL CHECK(mode IN ('prototype','migration'))
);
CREATE TABLE IF NOT EXISTS v2_relations (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES v2_runs(id),
  type TEXT NOT NULL,
  source_type TEXT NOT NULL, source_id TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL,
  direction_state TEXT NOT NULL,
  direction_value TEXT,
  validation_state TEXT NOT NULL,
  interpretation TEXT,
  coverage_limit TEXT,
  corpus_version TEXT NOT NULL,
  rule_version TEXT NOT NULL,
  CHECK(direction_state != 'inconnue' OR direction_value IS NULL)
);
CREATE INDEX IF NOT EXISTS idx_v2_relation_pair
  ON v2_relations(source_type, source_id, target_type, target_id);
CREATE TABLE IF NOT EXISTS v2_evidence (
  id TEXT NOT NULL,
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  polarity TEXT NOT NULL CHECK(polarity IN ('favorable','defavorable')),
  target_type TEXT NOT NULL, target_id TEXT NOT NULL,
  source TEXT NOT NULL,
  excerpt TEXT,
  provenance TEXT NOT NULL,
  PRIMARY KEY (relation_id, id)
);
CREATE TABLE IF NOT EXISTS v2_dimensions (
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  name TEXT NOT NULL,
  state TEXT NOT NULL,
  value_json TEXT,
  unit TEXT,
  rule TEXT,
  rule_version TEXT,
  limitations TEXT,
  PRIMARY KEY (relation_id, name)
);
CREATE TABLE IF NOT EXISTS v2_annotations (
  id TEXT PRIMARY KEY,
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  agent_kind TEXT NOT NULL CHECK(agent_kind IN ('humain','automatique','legacy_inconnu')),
  agent_id TEXT NOT NULL,
  independent INTEGER NOT NULL,
  proposition TEXT NOT NULL,
  validation_state TEXT NOT NULL,
  confidence_state TEXT NOT NULL,
  confidence_value TEXT,
  guide_version TEXT
);
CREATE TABLE IF NOT EXISTS v2_history (
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  ordinal INTEGER NOT NULL,
  action TEXT NOT NULL,
  actor TEXT NOT NULL,
  detail TEXT,
  PRIMARY KEY (relation_id, ordinal)
);
CREATE TABLE IF NOT EXISTS v2_legacy_metrics (
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  name TEXT NOT NULL,
  value_json TEXT,
  original_rule TEXT NOT NULL,
  original_rule_version TEXT NOT NULL,
  canonical INTEGER NOT NULL DEFAULT 0 CHECK(canonical=0),
  caveat TEXT NOT NULL,
  PRIMARY KEY (relation_id, name)
);
CREATE TABLE IF NOT EXISTS v2_unconvertible (
  source_table TEXT NOT NULL,
  source_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  PRIMARY KEY (source_table, source_id)
);
"""

SQL_ROLLBACK = """
DROP TABLE IF EXISTS v2_unconvertible;
DROP TABLE IF EXISTS v2_legacy_metrics;
DROP TABLE IF EXISTS v2_history;
DROP TABLE IF EXISTS v2_annotations;
DROP TABLE IF EXISTS v2_dimensions;
DROP TABLE IF EXISTS v2_evidence;
DROP INDEX IF EXISTS idx_v2_relation_pair;
DROP TABLE IF EXISTS v2_relations;
DROP TABLE IF EXISTS v2_runs;
"""


def etat_validation_agrege(verdicts):
    """Qualifie l'agrégation sans transformer un désaccord en absence de lecture."""
    valeurs = list(verdicts)
    lus = {v for v in valeurs if v is not None}
    if not lus:
        return "non_lu"
    if len(lus) > 1:
        return "discordant"
    if any(v is None for v in valeurs):
        return "partiellement_lu"
    return "unanime"


def dimension(state, value=None, unit=None, rule=None, rule_version=None, limitations=None):
    d = {"state": state, "value": value, "unit": unit, "rule": rule,
         "rule_version": rule_version, "limitations": limitations}
    return d


def valider_dimension(nom, d):
    erreurs = []
    if nom not in DIMENSIONS:
        erreurs.append("dimension inconnue : %s" % nom)
    etat = d.get("state")
    if etat not in ETATS_VALEUR:
        erreurs.append("état de dimension inconnu : %r" % etat)
    if etat in ETATS_SANS_VALEUR and d.get("value") is not None:
        erreurs.append("%s ne doit pas coder %s par une valeur" % (nom, etat))
    if etat not in ETATS_SANS_VALEUR and "value" not in d:
        erreurs.append("%s : valeur absente" % nom)
    if etat == "calculee" and (not d.get("rule") or not d.get("rule_version")):
        erreurs.append("%s : calcul sans règle versionnée" % nom)
    return erreurs


def valider_relation(relation):
    erreurs = []
    requis = ("id", "type", "source", "target", "direction", "validation_state",
              "evidence", "counterevidence", "dimensions", "annotations", "history",
              "corpus_version", "rule_version")
    for cle in requis:
        if cle not in relation:
            erreurs.append("champ obligatoire absent : %s" % cle)
    if erreurs:
        return erreurs
    interdits = {"score", "force_globale", "influence_score", "aggregate_score"} & set(relation)
    if interdits:
        erreurs.append("score synthétique interdit : %s" % ", ".join(sorted(interdits)))
    if relation["type"] not in TYPES_RELATION:
        erreurs.append("type de relation inconnu : %s" % relation["type"])
    if relation["validation_state"] not in ETATS_VALIDATION:
        erreurs.append("statut de validation inconnu")
    for cote in ("source", "target"):
        if not relation[cote].get("type") or not relation[cote].get("id"):
            erreurs.append("objet %s incomplet" % cote)
    direction = relation["direction"]
    if direction.get("state") not in ETATS_VALEUR:
        erreurs.append("état de direction inconnu")
    if direction.get("state") in ETATS_SANS_VALEUR:
        if direction.get("value") is not None:
            erreurs.append("direction inconnue/non applicable avec valeur")
    elif direction.get("value") not in DIRECTIONS:
        erreurs.append("valeur de direction inconnue")
    if not relation["corpus_version"] or not relation["rule_version"]:
        erreurs.append("versions du corpus et des règles obligatoires")
    preuves = list(relation["evidence"]) + list(relation["counterevidence"])
    ids_preuves = [p.get("id") for p in preuves]
    if any(not i for i in ids_preuves) or len(ids_preuves) != len(set(ids_preuves)):
        erreurs.append("preuves sans identifiant ou dupliquées")
    ids_annotations = [a.get("id") for a in relation["annotations"]]
    if any(not i for i in ids_annotations) or len(ids_annotations) != len(set(ids_annotations)):
        erreurs.append("annotations sans identifiant ou dupliquées")
    for nom, d in relation["dimensions"].items():
        erreurs.extend(valider_dimension(nom, d))
    if relation["type"] == "filiation_historique_documentee" and not relation["evidence"]:
        erreurs.append("filiation documentée sans preuve propre")
    if relation["type"] in {"convergence_propositionnelle", "opposition_doctrinale"}:
        if relation["validation_state"] == "validee_humainement" and not any(
                a.get("agent_kind") == "humain" for a in relation["annotations"]):
            erreurs.append("validation humaine annoncée sans annotation humaine")
    return erreurs


def valider_alignement_conceptuel(alignement):
    """Refuse qu'une identité de libellé soit promue en identité conceptuelle.

    Cette validation porte sur une proposition d'alignement, pas sur les candidats
    translexicaux. Un candidat peut donc rester documenté sans recevoir d'alignement.
    """
    erreurs = []
    requis = ("id", "source_entry_id", "target_entry_id", "relation",
              "bases", "validation_state", "annotations")
    for cle in requis:
        if cle not in alignement:
            erreurs.append("champ obligatoire absent : %s" % cle)
    if erreurs:
        return erreurs
    if alignement["source_entry_id"] == alignement["target_entry_id"]:
        erreurs.append("un alignement doit relier deux entrées distinctes")
    if alignement["relation"] not in TYPES_ALIGNEMENT:
        erreurs.append("type d'alignement inconnu")
    bases = set(alignement["bases"])
    if not bases or not bases <= BASES_ALIGNEMENT:
        erreurs.append("base d'alignement absente ou inconnue")
    relations_semantiques = {
        "equivalence", "equivalence_partielle", "proximite", "plus_large",
        "plus_etroit", "opposition",
    }
    if alignement["relation"] in relations_semantiques and bases <= {"libelle_identique"}:
        erreurs.append("un libellé identique ne suffit pas à un alignement conceptuel")
    if alignement["validation_state"] not in ETATS_VALIDATION:
        erreurs.append("statut de validation inconnu")
    if alignement["validation_state"] == "validee_humainement" and not any(
            a.get("agent_kind") == "humain" for a in alignement["annotations"]):
        erreurs.append("validation humaine annoncée sans annotation humaine")
    return erreurs


def json_canonique(valeur):
    return json.dumps(valeur, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
