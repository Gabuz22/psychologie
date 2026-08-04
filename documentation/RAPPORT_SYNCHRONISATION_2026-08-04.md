# Rapport de synchronisation — 2026-08-04

**Résultat : CONFORME.**

Ce rapport contrôle des artefacts existants. Il ne régénère ni D1, ni graphe, ni relation,
et n'applique aucune migration.

## Références

| Identifiant | Statut | Commit | Empreinte |
|---|---|---|---|
| `d1-historique-2026-08-03` | canonique historique | `a35fe072d327` | `d56a404a07a05172` |
| `manifeste-corpus-actuel` | canonique courant | `17ba606af1c9` | `9c6ba32e3720ac54` |
| `regles-d1-historiques` | inconnu | `a35fe072d327` | `d56a404a07a05172` |
| `fondations-relations-v2` | expérimental | `17ba606af1c9` | `06a6c7dd37a2cbe0` |
| `prototype-freud-stekel-v1` | expérimental | `8c55e531ac3c` | `17da0db82c3e7fad` |
| `homonymes-translexicaux-v1` | expérimental | `8c55e531ac3c` | `7e9a13f618130a8b` |
| `migration-v2-additive` | expérimental | `8c55e531ac3c` | `e7b43e65ee93b8d5` |
| `site-source-courant` | canonique courant | `SELF` | `ef54679917dd872f` |
| `site-public-observe-2026-08-04` | dérivé | `inconnu` | `3ca7237c906ab5ce` |
| `documentation-courante` | canonique courant | `SELF` | `d806ba721cef1163` |

## Contrôles structurants

- D1 : 116545 atomes, 57 œuvres, 7 auteurs, 507 liens, 354 actes.
- Acte 96 : `discordant` ; aucun verdict unique fabriqué.
- V2 : `expérimental`, 0 annotation humaine dans le prototype et 0 dans l'expérience.
- Homonymes : 96 ; propositions d'équivalence : 0.
- Tests présents : 440 Python et 56 Worker ; présence distincte de l'exécution.

## Erreurs

- Aucune.

## Avertissements

- `versions_d1_historiques_inconnues`
- `commit_site_public_inconnu`

## Limites

- Le commit du déploiement public demeure inconnu.
- Les versions de règles du D1 historique ne sont pas enregistrées dans sa table `meta`.
- Les résultats v2 restent automatiques ou legacy ; aucune campagne humaine n'a commencé.
