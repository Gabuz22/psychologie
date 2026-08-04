# Références canoniques du projet Psychologie

Le registre machine `manifests/references_canoniques.json` fait foi pour l'identification des
couches. Il est généré de façon déterministe à partir des artefacts locaux et se vérifie sans
réatomiser le corpus, recalculer les graphes ni interroger le réseau.

## Pourquoi plusieurs références

Une référence canonique n'est pas nécessairement « la plus récente ». D1 fait foi pour les
résultats historiques gelés ; le manifeste fait foi pour son intégrité ; v2 fait foi comme contrat
expérimental ; le site public observé fait foi seulement comme photographie datée du déploiement.
Les confondre ferait disparaître précisément l'information que la consolidation doit préserver.

| Couche | Statut | Rôle | Limite décisive |
|---|---|---|---|
| D1 du 2026-08-03 | canonique historique | atomes et résultats v1 gelés | versions historiques des règles absentes de `meta` |
| manifeste du corpus | canonique courant | fichiers, empreintes, comptes et SHA de D1 | versions de code lues a posteriori |
| règles réellement embarquées dans D1 | inconnu | provenance calculatoire historique | ne pas leur substituer le code courant |
| objets et relations v2 | expérimental | contrats JSON/SQLite additifs | non déployés, aucune validation humaine |
| prototype Freud–Stekel | expérimental | 20 candidats, 60 contrôles, 29 relations | vérité terrain absente |
| 96 homonymes translexicaux | expérimental | identités de libellé documentées | zéro équivalence conceptuelle |
| migration v2 | expérimental | dry-run sur nouvelle base | jamais appliquée à D1 |
| source du site dans le dépôt | canonique courant | interface v1 et transparence | non déployée par cette consolidation |
| site public observé | dérivé | état effectivement visible le 2026-08-04 | commit et données exactes de déploiement inconnus |
| documentation courante | canonique courant | méthode et réserves synchronisées | rapports anciens conservés comme historiques |

## Statuts scientifiques

- **Automatiquement observé** : segmentation, cooccurrence, n-grammes, densités, grappes,
  homonymes et résultats préliminaires.
- **Legacy argumenté** : verdicts de lecture présents dans `verification/`, dont la responsabilité
  ne répond pas au protocole humain indépendant v2.
- **Humainement validé** : aucun résultat v2 à ce jour.
- **Inconnu** : versions réellement utilisées pour produire le D1 historique et commit du site
  actuellement déployé.
- **Indécidable** : acte 96 au niveau agrégé ; ses verdicts élémentaires sont incompatibles et
  aucun verdict unique ne doit être fabriqué.
- **À décider** : qualification humaine des homonymes, campagne Freud–Stekel, adoption éventuelle
  du modèle v2 et référence d'un futur export.

## Commandes

```powershell
python -B bin/generer_reference_canonique.py --check
python -B bin/verifier_synchronisation.py
```

La première commande compare le registre et l'état statique du site aux artefacts présents. La
seconde vérifie en plus les déclarations du README, de la documentation et du site, puis produit un
rapport lisible. Toute erreur provoque un code retour non nul ; aucune commande ne corrige D1 ou
n'applique la migration.

## Publication

`web/site/etat-canonique.json` est un sous-ensemble généré du registre. Le site le rend dans une
section de transparence ; ce fichier n'active aucune API v2. L'observation du déploiement public est
conservée séparément dans `manifests/site_public_observe_2026-08-04.json`, afin qu'une vérification
réseau datée ne se transforme pas en dépendance non déterministe du build.
