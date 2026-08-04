# Modèle de relations multiples et multidimensionnelles v2

## Principe

La clé logique n'est pas `(A, B)` mais `(relation_id, type, A, B, règle, version)`. Deux relations
sur la même paire ne s'écrasent donc jamais. Une proximité terminologique et une opposition
doctrinale peuvent toutes deux être fortes ; elles ne s'annulent pas et ne se moyennent pas.

Le contrat exécutable se trouve dans `core/relations_v2.py`, le JSON Schema dans
`schemas/relations_v2.schema.json` et SQLite dans `schemas/relations_v2.sql`.

## Composantes séparées

1. `type` : nature de la relation proposée ;
2. `evidence` : passages favorables ;
3. `counterevidence` : passages défavorables ;
4. `dimensions` : mesures ou états, chacun avec règle et limites ;
5. `annotations` : qualifications indépendantes, jamais écrasées ;
6. `validation_state` : procédure, pas moyenne des dimensions ;
7. `interpretation` : lecture scientifique facultative et responsable ;
8. `coverage_limit` : ce que la méthode ne pouvait pas observer.

Les types incluent notamment proximité terminologique, reprise explicite, analogie fonctionnelle,
convergence propositionnelle, opposition doctrinale, transformation possible, filiation
documentée, filiation plausible non établie, correspondance exploratoire et source tierce partagée.
**Influence** n'est pas un raccourci de cooccurrence, succession ou ressemblance : elle exige une
relation de filiation historique et ses propres preuves.

## Dimensions

| Dimension | Domaine | Statut honnête actuel | Données nécessaires | Limite |
|---|---|---|---|---|
| contenance textuelle | `[0,1]` | calculable | deux textes, n-grammes, règle | pas une probabilité |
| passages indépendants | entier | non calculable actuellement | segmentation de dépendance/citation | `poids` compte des paires contiguës |
| récurrence | entier | calculable selon unité déclarée | actes ou paires distincts | dépend de l'unité choisie |
| dispersion entre œuvres | entier/proportion | calculable | regroupement par œuvres | corpus incomplet |
| stabilité/localisation temporelle | intervalles | partiellement reconstruisible | dates/collation | éditions augmentées |
| proximité lexicale | mesure versionnée | calculable | textes, langue, règle | sens non garanti |
| explicitation | classes | annotation requise | contexte et guide | pas déductible du score |
| orientation | classe | date calculée + lecture possible | fenêtres et attribution | chevauchements/tiers |
| compatibilité fonctionnelle | classe | non automatique | propositions annotées | cooccurrence insuffisante |
| contradiction | classe | non automatique | propositions et polarité | négation/mention ne suffisent pas |
| qualité de provenance | classe | observée | édition/source/offsets | granularité œuvre/passage |
| qualité OCR | relu/OCR/suspect | observée | provenance + drapeau phrase | absence de drapeau ≠ texte parfait |
| dépendance à traduction | booléen/état | observée | chemin de calcul | traduction pilote incomplète |
| couverture documentaire | `[0,1]` ou état | calculable par méthode | population éligible | pas couverture historique totale |
| confiance d'annotation | classe déclarée | inconnue pour legacy | annotateur et guide | auto-évaluation, pas vérité |

Chaque dimension porte `state` parmi `observee`, `calculee`, `annotee`, `reconstruite`, `inconnue`,
`non_applicable`, `non_calculable`, `contradictoire`. Les trois états sans valeur refusent une
valeur numérique, ce qui empêche de coder l'inconnu par zéro.

## Exemple simultané

Dans le prototype, un acte reclassé Freud–Stekel produit :

- une `correspondance_exploratoire`, soutenue par le recouvrement textuel mais fragilisée par
  l'attribution tierce ;
- une `source_tierce_partagee`, proposée à partir du motif de reclassement legacy.

Les deux relations partagent la paire d'objets, pas leur identité. Leur orientation, leurs preuves,
leur validation et leurs dimensions restent séparées. L'annotation legacy est marquée
`legacy_inconnu`, jamais `humain`.

## Anciennes forces

`force = partielle|manifeste` est conservée dans `v2_legacy_metrics` avec `canonical = 0`, sa règle
de seuil et l'avertissement « ni confiance, ni intensité, ni score canonique ». La migration ne la
renomme pas, ne la moyenne pas et ne l'efface pas.
