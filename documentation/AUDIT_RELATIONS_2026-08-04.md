# Audit de la couche « relations » — 4 août 2026

**Statut : audit reproductible du dépôt local, branche `codex/audit-relations`.** Aucun déploiement,
aucune modification de `main`, aucune donnée de jugement inventée. La base examinée est
`derive/d1/corpus.sqlite`, générée le 3 août 2026. Les nombres ci-dessous sont des requêtes sur
cette base, pas une reprise du README.

## Conclusion exécutive

Le pipeline conserve correctement plusieurs types de faits au lieu de fabriquer un score unique :
mention nominale, lecture déclarée, reprise textuelle candidate puis relue, usage lexical et
cooccurrence. Les 507 reprises ont un verdict ; les clés étrangères, doublons et liens réflexifs
ne présentent aucune anomalie. C'est une base technique sérieuse.

La faiblesse principale est sémantique, pas algorithmique : le mot **force** désigne plusieurs
quantités incompatibles, et l'interface du « socle commun » traite parfois un même libellé dans
deux lexiques comme s'il désignait le même concept. Or 96 noms sont présents dans plusieurs
lexiques, 90 changent de groupe et 80 ont plusieurs variantes de motif. Une identité de chaîne
n'est donc pas une équivalence conceptuelle démontrée.

Un score unique de « force du lien » serait **scientifiquement indéfendable** dans l'état actuel.
Il additionnerait des unités sans commune mesure : nombre d'actes, nombre de mentions, proportion
de n-grammes, densité pour mille et cooccurrence corrigée. Le modèle recommandé est
multidimensionnel et conserve les absences, les verdicts, la provenance et la non-comparabilité.

## Photographie vérifiée

| Objet | Valeur actuelle |
|---|---:|
| atomes | 116 545 |
| volumes enregistrés | 57 |
| auteurs distincts | 7 |
| atomes qualifiés | 83 431 (71,6 %) |
| concepts | 588 |
| mentions nominales | 2 899 |
| lectures déclarées | 9 |
| candidats de reprise relus | 507 |
| actes regroupés | 354 |
| actes confirmés / reclassés / rejetés / non lus | 280 / 65 / 8 / 1 |
| actes confirmés touchant Freud | 256 / 280 (91,4 %) |
| atomes touchés par un acte | 938 (0,805 %) |
| œuvres sans acte | 25 |
| usages lexicaux | 2 944 |
| liens de cooccurrence intra-auteur | 7 646 |
| violations de clés étrangères | 0 |

Le README et plusieurs documents historiques décrivaient encore la campagne à 40 œuvres et
54 626 atomes. Ils ne doivent pas servir de référence pour la base actuelle. Les chiffres d'état
du README et les métadonnées HTML ont été corrigés ; les anciennes campagnes restent des archives
et doivent être datées comme telles lors d'une régénération documentaire.

## Chaîne source → interface

| Couche | Calcul ou décision | Stockage | Ce que cela signifie | Ce que cela ne signifie pas |
|---|---|---|---|---|
| source/atome | segmentation avec offsets | `atomes` | passage relocalisable | unité naturelle de pensée |
| mention | jeton de nom + relecture | `mentions` | nom écrit dans un passage | lecture, accord, dette |
| lecture déclarée | nom dans un titre de chapitre | `lectures_declarees` | périmètre éditorial explicite | adhésion à l'auteur lu |
| reprise | recouvrement de 6-grammes, seuil 0,30 | `liens_reprise` | candidat de proximité textuelle | influence ou emprunt |
| verdict | lecture de la paire | champs `verdict`, `reclasse_vers`, `motif_lecture` | qualification du candidat | vérité historique définitive |
| acte | agrégation de liens contigus | `carte_actes` | événement textuel regroupé | intensité de relation |
| usage | motif appliqué aux corpus de même langue | `usages` | fréquence textuelle d'une forme choisie | même sens chez deux auteurs |
| cooccurrence | vote par atome dense puis normalisation | `concept_liens` | proximité textuelle intra-auteur | proximité sémantique |
| socle | deux filtres présentés côte à côte | `socle_*` | liste exploratoire de libellés | doctrine commune |

### Les quantités appelées « force »

- `liens_reprise.contenance` est l'intersection des 6-grammes divisée par le nombre de 6-grammes
  du passage le plus court.
- `liens_reprise.force` est seulement une classe ordinale : `partielle` à partir de 0,30,
  `manifeste` à partir de 0,70. Elle n'est ni une probabilité ni une confiance.
- `carte_actes.poids` est un nombre de phrases/paires regroupées. Il ne mesure pas l'intensité.
- `concept_liens.poids` est une cooccurrence corrigée du biais des atomes denses, puis rapportée
  à une union. Elle reste intra-auteur.
- la modularité décrit une partition de graphe sur ce corpus et ce seuil ; ce n'est pas une force
  doctrinale.
- le statut `affirmé/modalisé/interrogatif/rapporté` est une force d'énonciation de la phrase,
  totalement distincte d'une relation entre auteurs.

Le terme **influence** n'est calculé nulle part, ce qui est correct. Le terme **confiance** ne doit
être utilisé que pour un protocole d'annotation ou une incertitude explicitement modélisée.

## Constats classés

### Vérifié et correct

1. Les reprises, mentions et lectures déclarées restent dans des tables séparées.
2. Les 507 reprises ont été lues ; aucune paire dupliquée, réflexive ou source tierce orientée
   n'est stockée.
3. Les événements reclassés conservent leur destination tierce et le motif de lecture.
4. Le buisson des concepts est intra-auteur et corrige le biais des phrases riches en concepts.
5. Les axes du socle ne sont pas additionnés en un score composite.

### Défauts certains corrigés

1. **Attribution silencieuse à Freud.** Une quarantaine de chemins utilisaient historiquement
   `atome.get("auteur", "Sigmund Freud")`. La fonction sûre existait mais le test du corpus réel
   ne prouvait pas l'échec sur entrée cassée. `Corpus` valide désormais auteur, identifiant et
   unicité avant toute indexation ; des tests injectent les trois pannes.
2. **Provenance de règles absente.** Les prochains exports portent les versions de comparaison,
   de carte et de socle dans `meta`.
3. **Libellés d'interface trop forts.** « force graduée », « ne dépend d'aucun lexique » et
   « deux mesures indépendantes jugent » ont été remplacés par les opérations réellement faites.
4. **État courant périmé.** README, description HTML et proportion freudienne ont été remis en
   cohérence avec la base du 3 août.

### Probable ou trompeur — décision scientifique nécessaire

1. **Homonymie conceptuelle.** `carte.concepts_communs` intersecte des noms. `angst`, `traum`,
   `hysterie`, `religion`, etc. changent de groupe selon le lexique. Les appeler « communs » sans
   table d'équivalence validée est trompeur.
2. **Densités interlingues.** La langue est stockée dans `usages`, mais la clé logique de
   `densites_du_concept` est le seul motif. Le prêt exact `prestige` peut donc rapprocher Le Bon
   et un auteur allemand alors que les autres formes interlingues restent non mesurables. Il faut
   décider si ces prêts sont autorisés par une liste explicite ou toujours séparés par langue.
3. **Export incomplet du socle.** L'API et `candidats()` promettent l'union des axes, mais
   l'export écrit les densités seulement pour les concepts déjà présents dans l'axe des liens.
   Exemple : Freud–Ferenczi offre 372 concepts de densité dans `usages`, mais 169 seulement dans
   `socle_densites`. Corriger mécaniquement sans décider du lexique propre de Breuer et de la
   comparabilité interlingue déplacerait le problème ; la migration v2 doit trancher d'abord.
4. **Jugement non attribuable.** Les registres portent verdict et motif, mais pas toujours
   annotateur, date, méthode/modèle, indépendance ni version de preuve. Il est impossible de
   calculer honnêtement un accord inter-annotateurs rétrospectif.
5. **Traduction pilote sans périmètre déclaré.** `citations_fr.json.meta.scope` est vide ; le
   garde-fou de complétude ne protège donc aucun auteur. Il faut déclarer `pilot`, `incomplete`,
   cible et version de traduction, sans prétendre que les 11 146 entrées couvrent le corpus.

## Échantillon adversarial

Ces cas sont à conserver dans une campagne humaine, avec contexte étendu et source affichée.

| Cas | Donnée | Pourquoi il résiste à un score unique | Statut actuel |
|---|---|---|---|
| très fort | acte 1, Rank `lohengrinsage` → Freud `sammlung_4`, contenance 1, poids 6 | identité longue et orientation plausible | confirmé |
| fort mais tiers | acte 12, Freud–Stekel, contenance 1, poids 4, texte de Rosegger | le meilleur score brut n'est pas une relation directe | reclassé |
| tiers partagé | actes 45–46, Rank–Stekel, Kleinpaul | source commune, pas reprise mutuelle | reclassés |
| frontière | acte 351, Rank–Freud, contenance 0,30, poids 1 | fragment générique, validation dépend du contexte | confirmé |
| OCR/graphie | acte 354, Freud–Stekel, `spät/spat`, contenance 0,30 | tolérance utile mais risque de faux positif | confirmé |
| lecture sans mots partagés | Freud lit Le Bon, chapitre de `massenpsychologie`, 105 atomes | lien éditorial fort malgré langues différentes | lecture déclarée |
| plausible mais absent | couple sans reprise après rupture ou dans une œuvre muette | absence de détection ≠ absence historique | négatif à annoter |
| homonyme | `traum` dans cinq lexiques et cinq groupes | même chaîne, catégories différentes | à décider |

Les cas reclassés montrent empiriquement que `contenance = 1` n'est pas une probabilité de lien.
Les cas au seuil montrent inversement qu'une faible contenance n'invalide pas automatiquement un
lien. La relecture et la typologie sont indispensables.

## Priorités

### Critique

- Ne pas publier de score composite de « force du lien ».
- Introduire des identités conceptuelles propres à chaque lexique et une table d'alignement revue.
- Versionner toute nouvelle campagne d'annotation avec annotateurs indépendants.

### Important

- Migrer le socle vers l'union réellement exportée, après décision langue/lexique.
- Exposer dans l'API le type de preuve, la règle/version, le verdict et la réserve.
- Marquer tous les documents générés par date, commit et empreinte de base.

### Souhaitable

- Remplacer les derniers usages de l'auteur par défaut dans les chemins non couverts par `Corpus`.
- Ajouter une page « état de la mesure » issue directement de `meta` plutôt que des nombres HTML.
- Versionner le périmètre et le statut des traductions.

## Reproduction

```powershell
& '<python explicite>' bin/auditer_relations.py
& '<python explicite>' bin/auditer_relations.py --json
node --test worker/*.test.js
```

L'auditeur ouvre SQLite en lecture seule. Une alerte méthodologique n'est pas transformée en
erreur de structure : cette distinction évite qu'un test automatique prétende résoudre une
question d'interprétation.
