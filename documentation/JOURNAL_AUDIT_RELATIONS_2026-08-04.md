# Journal de travail — audit relations, 4 août 2026

## Réalisé

- création de la branche locale `codex/audit-relations` depuis `main` propre ;
- lecture du README, de tous les Markdown à la racine de `documentation/`, de l'historique récent,
  des modules relationnels, de l'export D1 et des routes/présentations concernées ;
- inventaire SQL de l'export courant et recomptage indépendant des auteurs, œuvres, atomes,
  verdicts, couples, usages, concepts, doublons et clés étrangères ;
- échantillon adversarial de reprises fortes, faibles, tierces, interlingues et homonymes ;
- ajout d'un audit SQLite en lecture seule et de tests unitaires ;
- garde-fou à la frontière de `Corpus` contre auteur absent, identifiant absent et doublon ;
- ajout des versions de règles aux prochains exports ;
- correction des chiffres courants et de plusieurs formulations d'interface ;
- rédaction du rapport, du protocole expérimental et d'un schéma v2 compatible.

## Non modifié délibérément

- aucun verdict de reprise ou de mention ;
- aucune traduction ni prétention de couverture ;
- aucun seuil de détection ;
- aucun alignement entre concepts homonymes ;
- aucune décision sur les prêts interlingues ou Breuer sans lexique ;
- aucun déploiement, push, PR ou changement de `main`.

## Décisions attendues

1. Valider ou refuser une table d'alignement conceptuel revue humainement.
2. Définir la comparabilité des motifs identiques entre langues.
3. Définir si les densités sont applicables à un auteur sans lexique propre.
4. Nommer deux annotateurs et un arbitre pour la campagne Freud–Stekel.
5. Déclarer le périmètre exact de la traduction pilote.

## Validation

- suite Python complète initiale : 262 tests indiqués comme réussis avant expiration de la limite
  de 10 minutes ; aucun échec imprimé, mais absence de résultat terminal, donc suite **incomplète** ;
- tests Python ciblés des nouveaux garde-fous et de l'auditeur : 9/9 réussis ;
- contrôle du contrat sur les 116 545 atomes réels : 1/1 réussi (300,9 s) ;
- compilation des quatre modules Python modifiés/ajoutés : réussie ;
- tests Worker explicitement ciblés : 56/56 réussis ;
- audit de la base réelle : structure valide, 0 clé étrangère invalide, 0 doublon de reprise,
  0 reprise réflexive, 0 source tierce orientée ; alertes conservées sur 1 acte non lu,
  96 homonymes inter-lexiques et les versions absentes de l'export historique.
