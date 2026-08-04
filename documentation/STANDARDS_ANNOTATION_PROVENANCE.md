# Comparaison limitée avec TEI, Web Annotation, SKOS et PROV-O

Le projet conserve un schéma JSON/SQLite local. Les standards servent de vocabulaire de contrôle,
pas d'obligation XML, RDF ou JSON-LD.

| Standard | À reprendre | Inutile ici | Risque/conflit | Coût | Recommandation |
|---|---|---|---|---|---|
| [TEI P5 — Certainty, Precision, Responsibility](https://tei-c.org/release/doc/tei-p5-doc/en/html/CE.html) | responsabilité, certitude structurée, cible de l'interprétation | conversion intégrale des sources en XML TEI | double représentation des offsets et segmentation existants | moyen/fort | reprendre les champs, pas le format |
| [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/) | séparation Annotation/Body/Target, motivation, cible précise/état de ressource | protocole HTTP et JSON-LD | identifiants Web non nécessaires au prototype local | moyen | aligner les concepts de cible et motivation, sans dépendance |
| [SKOS Reference](https://www.w3.org/TR/skos-reference/) | distinguer libellés/concepts/schemes ; relations exact/close/broad/narrow/related | publication RDF immédiate | `exactMatch` est fort et transitif : dangereux pour les 96 candidats | faible conceptuellement, fort en RDF | reprendre la typologie avec validation humaine ; ne créer aucun match automatique |
| [PROV-O](https://www.w3.org/TR/prov-o/) | Entity/Activity/Agent, `wasGeneratedBy`, exécution et responsabilité | graphe RDF complet | le terme PROV « influence » est générique et ne doit pas devenir influence historique | moyen | conserver `entity/run/agent` dans SQLite ; RDF seulement si échange externe réel |

## Décisions de conception retenues dans le prototype

- TEI inspire `responsibility`, `confidence_state` et la séparation texte/interprétation.
- Web Annotation inspire `annotation`, `target`, `body/proposition` et la cible avec état/version.
- SKOS inspire la séparation `terme` / `entree_lexique` / `concept_reconstruit` et les futures
  classes d'alignement ; aucun `exactMatch` n'est émis.
- PROV-O inspire `v2_runs`, `agent_kind`, `corpus_version`, `rule_version` et l'historique.

Aucune bibliothèque ni dépendance externe n'a été ajoutée : les contraintes utiles tiennent dans
les schémas locaux et leurs tests.
