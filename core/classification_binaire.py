#!/usr/bin/env python3
"""Adaptateur Psychologie vers le moteur commun d'agents binaires.

Une categorie conceptuelle reste strictement rattachee au lexique de son auteur. Les fonctions
argumentatives et statuts ont un agent global, mais celui-ci applique les regles du lexique du
volume. Les signaux ``a_confirmer`` sont acceptes en ``candidate_review``, jamais comme acquis.
"""
from __future__ import annotations

from functools import lru_cache
import os
import sys
from typing import Any, Dict, Iterable, Mapping, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _WORKSPACE not in sys.path:
    sys.path.insert(0, _WORKSPACE)

from classification_commune import (  # noqa: E402
    AgentRegistry, Atom, BinaryCategoryAgent, ClassificationOrchestrator,
    ClassificationStore, MatchOutcome, OldestFirstVerifier,
)
from classification_commune.model import stable_hash  # noqa: E402

from . import atomisation, lexique, lexiques  # noqa: E402

PROJECT_ID = "psychologie"
REGISTRY_VERSION = "1.0.0"
DEFAULT_DATABASE = os.path.abspath(os.path.join(_HERE, "..", "derive", "classification_binaire.sqlite"))
FREUD = "Sigmund Freud"


def _authors():
    return [FREUD] + sorted(lexiques.PAR_AUTEUR)


def _scope_known(scope: str) -> bool:
    return scope in set(_authors())


@lru_cache(maxsize=16384)
def _analysis(text: str, scope: str):
    concepts = lexique.concepts_de(text, scope)
    functions = frozenset(lexique.fonctions_de(text, scope))
    return {
        "concepts": frozenset((item["groupe"], item["concept"]) for item in concepts),
        "groups": frozenset(item["groupe"] for item in concepts),
        "functions": functions,
        "status": lexique.statut_de(text, scope),
    }


def _concept_matcher(scope: str, group_id: str, concept_id: str):
    def match(atom: Atom):
        accepted = (group_id, concept_id) in _analysis(atom.text, scope)["concepts"]
        evidence = ({"scope": scope, "group": group_id, "concept": concept_id},) if accepted else ()
        return MatchOutcome.yes("concept_marker", evidence) if accepted else MatchOutcome.no()
    return match


def _group_matcher(scope: str, group_id: str):
    def match(atom: Atom):
        accepted = group_id in _analysis(atom.text, scope)["groups"]
        concepts = sorted(c for g, c in _analysis(atom.text, scope)["concepts"] if g == group_id)
        return MatchOutcome.yes("group_has_concept", ({"concepts": concepts},)) if accepted \
            else MatchOutcome.no()
    return match


def _function_matcher(function_id: str):
    def match(atom: Atom):
        scope = atom.taxonomy_scope
        accepted = function_id in _analysis(atom.text, scope)["functions"]
        reliability = lexique._compilee(scope)["fiabilite"].get(function_id, "etablie")
        if not accepted:
            return MatchOutcome.no()
        state = "candidate_review" if reliability == "a_confirmer" else "auto_validated"
        return MatchOutcome.yes("function_marker", ({"scope": scope, "reliability": reliability},), state)
    return match


def _status_matcher(status_id: str):
    def match(atom: Atom):
        actual = _analysis(atom.text, atom.taxonomy_scope)["status"]
        if actual == status_id:
            return MatchOutcome.yes("most_cautious_status", ({"status": actual},))
        return MatchOutcome.no("another_status_selected", ({"selected": actual},))
    return match


def build_registry() -> AgentRegistry:
    agents = []
    function_defs: Dict[str, Mapping[str, Any]] = {}
    order = 0
    for scope in _authors():
        table = lexique.pour_auteur(scope)
        scope_slug = _slug(scope)
        for group_id, group in sorted(table.CONCEPTS.items()):
            order += 1
            agents.append(BinaryCategoryAgent(
                "psy.%s.group.%s" % (scope_slug, group_id),
                "%s+%s" % (REGISTRY_VERSION, lexique.LEXIQUE_VERSION),
                stable_hash({"scope": scope, "group": group_id, "terms": group["termes"]}),
                _group_matcher(scope, group_id), label=group.get("label", group_id), order=order,
                applicable=lambda atom, expected=scope: atom.taxonomy_scope == expected,
                metadata={"kind": "concept_group", "scope": scope, "native_id": group_id},
            ))
            for concept_id, terms in sorted(group["termes"].items()):
                order += 1
                agents.append(BinaryCategoryAgent(
                    "psy.%s.concept.%s.%s" % (scope_slug, group_id, concept_id),
                    "%s+%s" % (REGISTRY_VERSION, lexique.LEXIQUE_VERSION),
                    stable_hash({"scope": scope, "group": group_id,
                                 "concept": concept_id, "terms": terms}),
                    _concept_matcher(scope, group_id, concept_id), label=concept_id, order=order,
                    applicable=lambda atom, expected=scope: atom.taxonomy_scope == expected,
                    metadata={"kind": "concept", "scope": scope, "group": group_id,
                              "native_id": concept_id},
                ))
        for definition in table.FONCTIONS:
            function_defs.setdefault(definition["id"], definition)

    # Une seule categorie de fonction/statut, mais des regles selectionnees selon le lexique du volume.
    all_function_rules = {
        scope: [{k: value for k, value in item.items() if k in ("id", "marqueurs", "fiabilite")}
                for item in lexique.pour_auteur(scope).FONCTIONS]
        for scope in _authors()
    }
    for function_id, definition in sorted(function_defs.items()):
        order += 1
        agents.append(BinaryCategoryAgent(
            "psy.function.%s" % function_id,
            "%s+%s" % (REGISTRY_VERSION, lexique.LEXIQUE_VERSION),
            stable_hash({"function": function_id, "all_scopes": all_function_rules}),
            _function_matcher(function_id), label=definition.get("label", function_id), order=order,
            applicable=lambda atom: _scope_known(atom.taxonomy_scope),
            metadata={"kind": "function", "native_id": function_id},
        ))
    for status_id in lexique.STATUTS:
        order += 1
        rules = {scope: lexique.pour_auteur(scope).MARQUEURS_STATUT for scope in _authors()}
        agents.append(BinaryCategoryAgent(
            "psy.status.%s" % status_id,
            "%s+%s" % (REGISTRY_VERSION, lexique.LEXIQUE_VERSION),
            stable_hash({"status": status_id, "all_scopes": rules}),
            _status_matcher(status_id), label=status_id, order=order,
            applicable=lambda atom: _scope_known(atom.taxonomy_scope),
            metadata={"kind": "status", "native_id": status_id},
        ))
    return AgentRegistry(agents, namespace="psy", version=REGISTRY_VERSION)


def _slug(value: str) -> str:
    import re
    import unicodedata
    folded = "".join(c for c in unicodedata.normalize("NFD", value.lower())
                     if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", folded).strip("_")


def atom_from_existing(item: Mapping[str, Any], volume_meta: Mapping[str, Any]) -> Atom:
    year = volume_meta.get("annee_oeuvre") or volume_meta.get("annee_edition")
    created = "%04d-01-01T00:00:00+00:00" % int(year) if year else None
    scope = str(volume_meta.get("auteur") or FREUD)
    return Atom(
        project_id=PROJECT_ID, atom_id=str(item["id"]), text=str(item.get("texte", "")),
        source_id=str(volume_meta.get("cle") or item.get("oeuvre", "")),
        source_created_at=created, source_order=int(item.get("index", 0)), taxonomy_scope=scope,
        metadata={
            "text_fingerprint_legacy": item.get("empreinte"),
            "actual_author": item.get("auteur", scope),
            "chapter": item.get("chapitre"),
            "source_start": item.get("debut"),
            "source_end": item.get("fin"),
        },
    )


def components(database_path: Optional[str] = None):
    store = ClassificationStore(database_path or DEFAULT_DATABASE)
    orchestrator = ClassificationOrchestrator(build_registry(), store)
    verifier = OldestFirstVerifier(orchestrator, PROJECT_ID)
    return orchestrator, verifier


def classify_works(work_keys: Iterable[str], *, database_path: Optional[str] = None,
                   limit_per_work: Optional[int] = None):
    orchestrator, _ = components(database_path)
    reports = []
    for key in work_keys:
        result = atomisation.atomiser(key)
        items = result["atomes"][:limit_per_work] if limit_per_work is not None else result["atomes"]
        batch = orchestrator.classify_many(atom_from_existing(item, result["meta"]) for item in items)
        reports.append({"work": key, **batch})
    return {"works": reports, "progress": orchestrator.progress(PROJECT_ID)}
