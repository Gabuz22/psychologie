# Acte 96 — verdict agrégé discordant

## Localisation

- paire : Otto Rank — Sigmund Freud ;
- œuvres : `inzest_motiv` / `traumdeutung` ;
- plages : `inzest_motiv:a460–a461` / `traumdeutung:a2470–a2471` ;
- poids : 2 ; contenance maximale : 0,5 ;
- ancien champ agrégé : `verdict = NULL`.

## Cause

Les deux liens élémentaires ont été lus :

1. lien 133 : `reclasse`, vers Freud comme source commune explicitement attribuée ;
2. lien 134 : `confirme`, Rank reprenant directement la formulation freudienne.

`carte._unanime` rendait `NULL` lorsque plusieurs valeurs non nulles différaient. Le stockage et
l'audit interprétaient ensuite tout `NULL` comme « non lu ». Le calcul d'agrégation était prudent,
mais son état n'était pas assez expressif.

## Traitement

- aucun verdict n'est attribué à l'acte ;
- les deux verdicts élémentaires sont conservés dans `verdicts_elementaires` ;
- `etat_validation = discordant` ;
- `verdict` reste `NULL` pour ne pas fabriquer un consensus ;
- couverture et audit distinguent désormais `non_lu` de `discordant` ;
- dans la migration prototype, l'ancien acte 96 est conservé dans `v2_unconvertible` avec motif.

L'interface D1 actuelle n'est pas modifiée avant régénération. L'export historique reste intact.
Le prochain export dispose des deux colonnes nouvelles et du test de non-régression.
