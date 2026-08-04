# Protocole exécutable de validation des relations

**Proposition, non encore lancée.** Ce document définit ce qu'il faudra faire avant d'affirmer
qu'une couche relationnelle ajoute une information historiquement utile. Il ne fabrique aucun
jugement humain absent.

## Question historique bornée

Sur les œuvres allemandes de Freud et Stekel présentes dans l'export figé, la couche distingue-t-elle
correctement : (a) une reprise directe plausible, (b) une source tierce partagée, (c) une proximité
formulaire sans relation démontrable ? La question porte sur la **qualification de passages**, pas
sur « l'influence de Freud sur Stekel » en général.

## Gel du matériau

Avant annotation, enregistrer : commit Git, SHA-256 de `corpus.sqlite`, versions
`comparaison/carte/socle`, liste exacte des œuvres et années, requête SQL de tirage, graine et date.
Le corpus, les seuils et la typologie restent immuables pendant la campagne.

## Ensembles

1. **Positifs candidats** : 60 actes Freud–Stekel stratifiés par contenance
   `[0,30–0,49]`, `[0,50–0,69]`, `[0,70–1]`, et par œuvre.
2. **Sources tierces** : tous les reclassés disponibles, complétés jusqu'à 30 si possible.
3. **Négatifs difficiles** : 60 paires sans lien, appariées par longueur, langue, période et
   vocabulaire ; inclure des fragments historiquement plausibles et des formules génériques.
4. **Contrôle explicite** : mentions nominales et chapitres déclarant l'autre auteur, échantillonnés
   séparément ; ils ne deviennent pas automatiquement des reprises.

Un script de tirage devra produire un manifeste JSONL immuable, sans verdict du pipeline visible
des annotateurs.

## Unité et fiche d'annotation

Chaque item montre les deux passages, 2 phrases de contexte de chaque côté, œuvre, date sous forme
d'intervalle, page/offset/source et, dans une seconde phase seulement, les notes bibliographiques.

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

- B0 : recherche plein texte des noms (mention explicite).
- B1 : seuil brut de contenance des 6-grammes, sans lecture.
- B2 : TF-IDF caractères ou mots, réglé uniquement sur un jeu de développement séparé.
- Système : candidats actuels + verdict/typologie, évalués sans changer le seuil sur le test.

Les chapitres déclarés sont une strate de contrôle, pas une vérité terrain pour la reprise.

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

## Format de conservation proposé

```json
{
  "campaign_id": "freud-stekel-v1",
  "item_id": "acte:12",
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
