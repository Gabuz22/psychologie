# Clôture de l'audit relationnel et fondations v2 — 4 août 2026

**Branche : `codex/fondations-relations-v2`.** Cette mission part de l'audit `a35fe07` et ne le
rejoue pas. Elle ferme ses manques techniques sans recalcul général, sans validation humaine
inventée, sans migration des données historiques et sans déploiement.

## Table de clôture

| Livrable | Statut après le premier audit | Vérifié ici | Statut actuel | Raison et fichier |
|---|---|---:|---|---|
| cartographie source → extraction → jugement → export → UI | terminé | oui | terminé | chaîne et limites détaillées dans `AUDIT_RELATIONS_2026-08-04.md` |
| inventaire de « force », confiance, influence et notions voisines | terminé | oui | terminé | significations incompatibles inventoriées ; aucune influence calculée |
| failles priorisées | terminé | oui | terminé | criticité et décisions séparées dans l'audit |
| protocole expérimental | partiel | oui | terminé pour préparation | tirage, contrôles, baselines et critères exécutables ; annotations humaines encore absentes par définition |
| migration réversible | partiel (SQL indicatif) | oui | prototype terminé | dry-run, base séparée, refus de seconde application, rollback et tests |
| décisions réservées à Gabriel/spécialiste | terminé | oui | terminé | liste consolidée ci-dessous |
| cinq travaux suivants par valeur/coût | absent | oui | terminé | classement ci-dessous |
| manifeste reproductible | absent | oui | terminé | `manifests/corpus_actuel.json` + générateur/validateur |
| schéma canonique des objets | absent | oui | terminé au stade prototype | JSON machine + document explicatif ; doctrine non adoptée définitivement |
| relations multiples/multidimensionnelles | partiel | oui | prototype terminé | JSON Schema, SQLite, validation et exemples simultanés |
| registre des 96 noms | absent | oui | terminé comme candidats | zéro équivalence et zéro validation humaine |
| acte sans verdict | partiel | oui | terminé | identifié comme agrégat discordant, pas comme non lu |
| registre probatoire | absent | oui | prototype terminé | 20 actes tirés, 29 relations, supprimable sans toucher D1 |
| comparaison TEI/W3C/SKOS/PROV-O | absent | oui | terminé | comparaison limitée, aucune dépendance ajoutée |
| recalcul général v2 | hors périmètre | oui | absent volontairement | interdit par la mission |

## Validation technique de la suite existante

Commande :

```powershell
& '<python 3.12 explicite>' -m unittest discover -s core/tests -p 'test_*.py' --durations 30 -v
```

Résultat initial complet : **395 tests réussis en 758,779 s**, aucun ignoré ni échoué. La limite
de dix minutes de la mission précédente interrompait un calcul encore actif. Elle ne cachait ni
réseau, ni deadlock, ni fuite : cinq tests globaux totalisent l'essentiel du temps.

Résultat final après ajout des fondations : **430 tests réussis en 623,785 s**, aucun ignoré ni
échoué. Les 35 tests ajoutés couvrent manifeste, schémas, relations multiples, agrégation
discordante, registre, expérience aveugle et migration. La suite web passe également **56/56** en
0,251 s avec `npm.cmd test`.

| Test | Durée |
|---|---:|
| cooccurrence Abraham, corpus complet | 327,473 s |
| absence de reprise Le Bon, comparaisons globales | 89,905 s |
| ancrage des verdicts de reprise sur le corpus | 81,735 s |
| orientation des reprises réelles | 78,107 s |
| tension : refus de conclure automatiquement | 58,553 s |

Le cache d'atomisation fonctionne ; segmenter ces cinq tests en processus distincts serait plus
lent. La commande complète dans un processus unique est donc le chemin de validation de référence.
Les 38 tests v2/carte/audit ciblés passent aussi. Deux premières invocations de ciblage étaient
invalides (nom de classe inexistant, puis répertoire Python incorrect) ; elles ont été corrigées et
ne correspondent pas à des échecs du code. Aucun test du dépôt n'est resté non exécuté. Les
annotations humaines et la régénération générale de D1 restent volontairement hors périmètre.

## Gel produit

Le manifeste fixe l'export du 3 août 2026, SHA-256
`52f0d2372bf2858169fdec56733520be1d906c1384f6a1fa3924ca2ea4a9045d`, au commit de référence
`a35fe072d32798964731bab5128ff71dc9c9480a`.

- 116 545 atomes, 57 œuvres/volumes, 7 auteurs ;
- 62 entrées textuelles empreintées : 57 sources citées et 5 témoins de collation non citables ;
- aucun fichier `.txt` orphelin ;
- comptes par auteur et œuvre cohérents ;
- 11 198 traductions appliquées dans D1, distinctes des 11 146 entrées du registre ;
- 14 déclarations numériques documentaires candidates à relecture humaine ;
- version source de l'ancien export : **inconnue**, parce que le champ n'existait pas ;
- futurs exports : versions de schéma/règles et empreinte source obligatoires.

## Résultats automatiquement observés

- 96 libellés apparaissent dans plusieurs lexiques ; ils restent 96 candidats non examinés.
- L'acte 96 agrège un verdict `reclasse` et un verdict `confirme` : état `discordant`.
- La paire Freud–Stekel contient 135 actes : 115 confirmés, 18 reclassés, 2 rejetés.
- Le tirage expérimental contient 20 candidats et 60 contrôles non candidats.
- Baselines préliminaires : 2/80 items portent un nom explicite dans les extraits ; 20/80 passent
  le seuil de contenance 0,30 ; médiane du Jaccard lexical 0,0784.
- Précision et rappel : **non calculables sans annotations humaines**.

## Implémenté, proposé et non validé

### Implémenté

- manifeste déterministe et détection de désynchronisation ;
- schéma relationnel JSON/SQLite et contraintes anti-score ;
- registre translexical, registre probatoire et expérience automatique ;
- migration à blanc/additive/rollback ;
- état agrégé `discordant` et conservation des verdicts élémentaires ;
- tests sur inconnue ≠ zéro, preuve + contre-preuve, annotations divergentes et ancien score.

### Seulement proposé

- le vocabulaire canonique des objets et types de relation ;
- toute équivalence conceptuelle ;
- toute interprétation de convergence, opposition ou filiation ;
- l'adoption de conventions inspirées de TEI, Web Annotation, SKOS ou PROV-O.

### Humainement validé

Rien de nouveau dans cette mission. Les verdicts historiques sont importables uniquement comme
`legacy_inconnu` : leur auteur/méthode n'est pas documenté au niveau de chaque jugement.

## Cinq travaux suivants — valeur scientifique / coût

| Rang | Travail | Valeur | Coût | Dépendance |
|---:|---|---|---|---|
| 1 | double annotation indépendante des 80 items Freud–Stekel | très forte | moyen | deux spécialistes + guide gelé |
| 2 | examen stratifié de 24 des 96 libellés translexicaux | très forte | moyen/fort | décision sur qualification des annotateurs |
| 3 | régénérer D1 avec versions/empreinte et comparer le manifeste | forte | moyen | aucun choix doctrinal |
| 4 | décider langue/prêts lexicaux et statut de Breuer, puis corriger le socle | forte | moyen | décision Gabriel/spécialiste |
| 5 | réduire le coût du test de cooccurrence sans changer sa population | moyenne | moyen | profilage, test d'équivalence strict |

## Décisions restant à Gabriel ou à une personne compétente

1. Autoriser ou refuser des comparaisons interlingues sur liste blanche (`prestige`).
2. Déclarer si une densité est applicable à Breuer sans lexique propre.
3. Définir qui peut valider un alignement conceptuel et selon quel guide.
4. Choisir le statut éditorial des verdicts historiques sans annotateur individuel.
5. Nommer deux annotateurs indépendants et un arbitre pour Freud–Stekel.
6. Déclarer le périmètre et le statut de la traduction pilote.
7. Adopter ou non le vocabulaire v2 proposé ; le prototype fonctionne sans cette adoption.

Tout le travail technique indépendant de ces décisions est achevé. Aucun choix ci-dessus n'a été
tranché implicitement dans les données.
