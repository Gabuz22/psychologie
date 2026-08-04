# Schéma canonique des objets analytiques v2

**Statut : proposition exécutable, non doctrine adoptée.** La source machine est
`schemas/objets_analytiques_v2.json`. Chaque objet y porte définition, statut épistémique, champs
obligatoires/optionnels, identifiant, provenance, relations permises, invariants, exemple et
distinctions. Ce document explicite les frontières qui comptent le plus.

## Chaîne d'objets

| Niveau | Objets | Nature |
|---|---|---|
| documentaire | auteur, œuvre, édition | métadonnées déclarées et sourcées |
| textuel | passage source, atome, terme | traces localisables ou segmentation calculée |
| lexicographique | entrée de lexique | règle construite pour un auteur |
| interprétatif | notion, concept reconstruit, famille conceptuelle, proposition | annotation/reconstruction contestable |
| analytique | acte, assertion, relation | agrégation ou qualification explicite |
| probatoire | preuve, contre-preuve | traces mobilisées avec polarité distincte |
| procédural | annotation, validation, désaccord | responsabilité et procédure |
| calcul/provenance | résultat, règle, exécution | calcul reproductible et historique |

## Le mot « concept »

Quatre identités distinctes sont obligatoires :

1. **Terme** : forme réellement présente, avec offsets. `Traum` est une chaîne observée.
2. **Entrée de lexique** : motif et libellé écrits pour un auteur. `lexique:Rank:geburt` et
   `lexique:Freud:geburt` sont deux objets, même si le libellé coïncide.
3. **Notion** : interprétation locale portée par une annotation et des passages.
4. **Concept reconstruit** : objet transversal créé seulement après alignement explicite et
   responsabilité humaine documentée.

Une **famille conceptuelle** peut regrouper des concepts reconstruits sans fusionner leurs
identités. Les groupes actuels des lexiques et les grappes calculées ne sont pas automatiquement
des familles conceptuelles.

## Invariants principaux

- aucune identité conceptuelle déduite d'un nom, motif ou groupe identique ;
- un atome n'est ni une proposition ni une assertion par nature ;
- un acte analytique n'est pas un événement historique ;
- une mesure ne valide pas la relation qu'elle propose ;
- une annotation ne remplace pas une preuve et une validation ne remplace pas ses annotations ;
- un désaccord est conservé comme objet, jamais encodé par `NULL` ambigu ;
- toute sortie calculée réfère à une règle, une version de corpus et une exécution ;
- `inconnu`, `non_applicable`, `non_calculable` et `0` sont quatre états différents.

## Identifiants et provenance

Les identifiants positionnels d'atomes restent nécessaires pour les offsets ; les empreintes
textuelles stables portent les jugements qui doivent survivre à un déplacement. Aucun des deux ne
remplace l'autre. Les objets reconstruits utilisent un espace de noms de registre/campagne. Les
résultats calculés et relations v2 portent obligatoirement `corpus_version` et `rule_version`.

## Compatibilité

Le schéma ajoute des objets ; il ne renomme ni ne supprime D1. Une entrée `concepts` actuelle est
importable comme **entrée de lexique**, jamais automatiquement comme concept transversal. Un
`carte_actes` devient un **acte analytique** et peut proposer plusieurs relations distinctes.
