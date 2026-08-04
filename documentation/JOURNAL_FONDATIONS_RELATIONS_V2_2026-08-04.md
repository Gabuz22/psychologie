# Journal — fondations relationnelles v2, 4 août 2026

## Point de départ

- branche source propre `codex/audit-relations`, commits `5e3d93b` et `a35fe07` ;
- nouvelle branche `codex/fondations-relations-v2` ;
- aucun push, déploiement ou changement de `main`.

## Vérifications et observations

- relecture intégrale des quatre documents de l'audit et de l'auditeur CLI ;
- relecture des registres, schémas D1, sources, atomisation, comparaison, carte, socle et tests ;
- suite Python initiale : 395/395, 758,779 s ;
- suite Python finale : 430/430, 623,785 s ; suite web : 56/56, 0,251 s ;
- audit D1 : 0 reprise non lue, 1 agrégat discordant, 96 candidats translexicaux ;
- acte 96 localisé et relié à ses deux verdicts élémentaires ;
- standards officiels TEI/W3C examinés sans nouvelle dépendance.

## Produits

- manifeste déterministe, générateur et validation de désynchronisation ;
- schéma canonique machine de 22 types d'objet ;
- JSON Schema et SQLite des relations multiples ;
- registre déterministe des 96 libellés ;
- registre probatoire Freud–Stekel ;
- expérience de 80 items aveugles, références et trois baselines automatiques séparées ;
- migration à blanc, additive dans une base séparée, idempotence par refus et rollback ;
- documentation de clôture, modèle, acte 96 et comparaison de standards.

## Correctifs certains

- les futurs exports enregistrent schéma, atomisation, lexique, collation, comparaison, carte,
  socle et empreinte du corpus source ;
- `NULL` agrégé n'est plus assimilé automatiquement à « non lu » ;
- les verdicts élémentaires discordants voyagent avec l'acte ;
- l'ancien champ `force` est conservé comme métrique legacy non canonique.

## Abstentions

- aucune équivalence parmi les 96 noms ;
- aucune annotation humaine ;
- aucune conclusion de précision/rappel ;
- aucune influence historique ;
- aucune migration générale ni régénération D1 ;
- aucun choix langue/Breuer/traduction à la place de Gabriel.

## Commandes de validation finales

```powershell
& '<python 3.12 explicite>' -m unittest discover -s core/tests -p 'test_*.py' --durations 30 -v
npm.cmd test  # depuis web/
python bin/generer_manifeste_corpus.py --check
python bin/generer_registres_v2.py --check
python bin/preparer_experience_relations.py --check
python bin/migrer_relations_v2.py
python bin/auditer_relations.py --json
```

Résultats : 430 tests Python et 56 tests web réussis ; trois artefacts déterministes conformes ;
migration restée en dry-run ; audit D1 `ok` avec 0 acte non lu, 1 agrégat discordant, 96 homonymes
et 3 versions absentes dans l'export historique. Les 38 tests ciblés v2/carte/audit passent. Deux
sélecteurs de test initialement mal formés ont été corrigés avant cette validation ; aucun échec
fonctionnel ne subsiste. Aucun test automatisé du dépôt n'est omis. La campagne humaine et la
régénération générale de D1 ne sont pas des tests exécutés, conformément au périmètre.
