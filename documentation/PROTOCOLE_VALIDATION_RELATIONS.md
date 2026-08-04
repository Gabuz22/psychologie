# Protocole exécutable de validation des relations

**Préparation automatique exécutée ; annotation humaine non commencée.** Ce document définit ce
qu'il faudra faire avant d'affirmer qu'une couche relationnelle ajoute une information
historiquement utile. Il ne fabrique aucun jugement humain absent.

## Question historique bornée

Sur les œuvres allemandes de Freud et Stekel présentes dans l'export figé, la couche distingue-t-elle
correctement : (a) une reprise directe plausible, (b) une source tierce partagée, (c) une proximité
formulaire sans relation démontrable ? La question porte sur la **qualification de passages**, pas
sur « l'influence de Freud sur Stekel » en général.

## Choix de la paire

Le choix a été fait avant lecture du tirage, sur des critères mesurables :

| Paire | Actes | confirmés / reclassés / rejetés / discordants | paires d'œuvres | Limite principale |
|---|---:|---:|---:|---|
| Freud–Stekel | 135 | 115 / 18 / 2 / 0 | 12 | Stekel majoritairement OCR |
| Freud–Rank | 89 | 82 / 3 / 3 / 1 | 20 | Rank OCR, négatifs moins nombreux |
| Rank–Stekel | 42 | 7 / 35 / 0 / 0 | 9 | très riche en tiers, pauvre en directs |
| Freud–Abraham | 31 | 31 / 0 / 0 / 0 | 8 | presque aucun négatif interne |

Freud–Stekel offre le meilleur équilibre entre couverture, directs plausibles, sources tierces et
rejets, dans une même langue. Le choix ne repose donc pas seulement sur le nombre de résultats
favorables au moteur. Freud–Rank reste un futur test de transfert, notamment pour l'agrégat 96.

## Gel du matériau

Avant annotation, enregistrer : commit Git, SHA-256 de `corpus.sqlite`, versions
`comparaison/carte/socle`, liste exacte des œuvres et années, requête SQL de tirage, graine et date.
Le corpus, les seuils et la typologie restent immuables pendant la campagne.

Ce gel est maintenant matérialisé par `manifests/corpus_actuel.json`. L'expérience référence son
empreinte source, le SHA-256 de D1 et le commit `a35fe07`.

## Ensembles

1. **Candidats stratifiés** : 20 actes Freud–Stekel, au plus trois par cellule
   `verdict legacy × [0,30–0,49] / [0,50–0,69] / [0,70–1]`, triés par SHA-256 avec graine publiée.
2. **Sources tierces** : présentes dans les cellules `reclasse`, sans suréchantillonnage manuel.
3. **Négatifs difficiles** : 60 paires absentes des candidats v1, appariées par longueur et milieu
   de fenêtre temporelle, puis départagées par SHA-256 ; absence de candidature ≠ vérité négative.
4. **Contrôle explicite** : mentions nominales et chapitres déclarant l'autre auteur, échantillonnés
   séparément ; ils ne deviennent pas automatiquement des reprises.

`bin/preparer_experience_relations.py` produit des identifiants opaques et les items aveugles.
Verdict legacy, appartenance candidat/contrôle et sorties des baselines vivent exclusivement dans
`automatic_reference_not_gold`, séparé de `blind_items`; rien de cela n'est une vérité terrain.

## Unité et fiche d'annotation

Chaque item montre les deux passages, jusqu'à 2 atomes de contexte avant et après, œuvre, date sous
forme d'intervalle, offsets et qualité de source. Les notes bibliographiques viennent dans une
seconde phase seulement.

Champs obligatoires :

- `relation_textuelle`: `directe_plausible | source_tierce | formule_commune | aucune | indecidable` ;
- `orientation`: `a_vers_b | b_vers_a | symetrique | indecidable | non_applicable` ;
- `position`: `accord | critique | mixte | descriptive | indecidable | non_applicable` ;
- `preuve`: liste d'indices textuels/bibliographiques ;
- `certitude`: `haute | moyenne | basse` (auto-évaluation, jamais score de vérité) ;
- `commentaire` et `besoin_source_externe`.

## Annotateurs

Deux annotateurs compétents travaillent indépendamment et à l'aveugle du verdict automatique.
Un troisième arbitre traite les désaccords sans écraser les deux réponses originales. Chaque
fichier porte identifiant pseudonyme, rôle, date, version du guide et déclaration d'indépendance.

## Baselines

- B0 : présence plein texte de `Freud|Stekel` dans les extraits.
- B1 : contenance brute des 6-grammes, seuil 0,30, sans lecture.
- B2 : Jaccard lexical des formes repliées, baseline simple sans apprentissage.
- Système : candidats actuels + verdict/typologie, évalués sans changer le seuil sur le test.

Les chapitres déclarés sont une strate de contrôle, pas une vérité terrain pour la reprise.

Une baseline TF-IDF reste possible dans une seconde phase, uniquement avec développement/test
séparés ; elle n'est pas nécessaire pour commencer et aucune dépendance n'a été ajoutée.

## Métriques prédéfinies

- accord brut et matrice de confusion ;
- Cohen κ pour deux annotateurs sur la classe nominale, avec intervalle bootstrap ;
- Krippendorff α si plus de deux annotations ou données manquantes ;
- précision, rappel et F1 par classe, macro-F1, avec intervalles bootstrap par œuvre ;
- taux de faux « directs » parmi les sources tierces ;
- couverture par œuvre et par période ;
- analyse qualitative obligatoire de tous les faux positifs à contenance ≥ 0,70 et faux négatifs
  explicitement nommés.

La position (`accord/critique`) n'est évaluée que sur les items où une relation textuelle a été
jugée ; elle ne doit pas contaminer la détection.

## Critères de valeur ajoutée

La couche sera dite utile seulement si, sur le test gelé :

1. sa précision sur `directe_plausible` dépasse B1 d'au moins 10 points avec intervalle compatible
   avec un gain positif ;
2. elle réduit d'au moins moitié les sources tierces classées directes ;
3. elle ne perd pas plus de 5 points de rappel par rapport à la meilleure baseline ;
4. κ ou α atteint au moins 0,67, sinon le guide doit être révisé et la campagne répétée ;
5. les résultats sont publiés par strate, y compris les négatifs et indécidables.

Si ces critères échouent, le résultat est conservé comme négatif : le système reste un outil de
repérage, sans revendication de qualification historique.

## Résultats automatiques préliminaires

Sur 80 items préparés :

- B0 noms explicites : 2 items ;
- B1 contenance ≥ 0,30 : 20 items, exactement les candidats stratifiés ;
- médiane B2 Jaccard lexical : 0,0784 ;
- précision, rappel, F1 et matrice de confusion : **non calculables** avant annotation humaine.

Ces chiffres décrivent les sorties automatiques, pas leur justesse historique. Ils sont conservés
dans `prototypes/relations_v2/experience_freud_stekel.json`, y compris les 60 non-candidats.

## Commandes reproductibles

```powershell
python bin/generer_manifeste_corpus.py --check
python bin/generer_registres_v2.py --check
python bin/preparer_experience_relations.py --check
python bin/migrer_relations_v2.py
```

La dernière commande est un dry-run. Une application exige `--apply <nouvelle-base.sqlite>` et
refuse une cible existante.

## Format de conservation proposé

```json
{
  "campaign_id": "freud-stekel-v1",
  "item_id": "item:4c1b7262fdf4cf0ac9ec",
  "annotator_id": "A02",
  "guide_version": "1.0.0",
  "independent": true,
  "relation_textuelle": "source_tierce",
  "orientation": "non_applicable",
  "position": "non_applicable",
  "certitude": "haute",
  "preuve": ["attribution bibliographique à Rosegger"],
  "timestamp": "ISO-8601"
}
```

Les annotations brutes sont append-only. Une table de consensus référence leurs identifiants ;
elle ne les remplace jamais.
