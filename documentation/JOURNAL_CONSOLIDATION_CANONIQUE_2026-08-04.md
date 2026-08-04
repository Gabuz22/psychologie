# Journal de consolidation canonique — 2026-08-04

## Cadre de travail

- Point de départ vérifié : branche `codex/fondations-relations-v2`, commit `6d750fc`, arbre de travail propre.
- Branche créée depuis cet état : `codex/consolidation-canonique-site`.
- Premier commit de consolidation : `5db3c26` (`Consolider la référence canonique du projet`).
- Aucun changement de `main`, aucun push, aucun déploiement.
- D1 a uniquement été ouvert en lecture seule (`mode=ro`) : aucune régénération du corpus, aucun recalcul de graphe ou de relation, aucune migration appliquée.
- Aucune annotation humaine Freud–Stekel n'a été lancée.

## Vérifications factuelles

- D1 gelé : 116 545 atomes, 57 œuvres, 7 auteurs, 62 fichiers/témoins, 507 liens, 354 actes, 2 899 mentions et 7 646 liens conceptuels.
- Empreinte SHA-256 de `derive/d1/corpus.sqlite` : `52f0b1f053855fc70efcbe79e7cf84ccdcfe43d06c61aa5558d3789179a9045d`.
- Acte 96 : agrégat `discordant`; aucun verdict unique n'a été fabriqué.
- Fondations v2 : 29 relations Freud–Stekel expérimentales, 80 items aveugles et 0 annotation humaine.
- Registre translexical : 96 homonymes documentés et 0 proposition d'équivalence conceptuelle.
- Site public observé le 4 août 2026 : D1 daté du 2 août 2026, 116 545 atomes, 57 œuvres, 7 auteurs, 354 actes, 938 atomes touchés (0,805 %), 25 œuvres silencieuses, 8 clusters et 607 signaux jugés. Le commit de déploiement demeure inconnu.
- Des libellés publics plus anciens (`191`, `107`, `40`, `< 0,5 %`) ont été classés comme historiques/obsolètes lorsqu'ils subsistaient dans l'interface ou la documentation.

## Changements réalisés

- Registre versionné `manifests/references_canoniques.json`, avec statuts, artefacts, commits déterminables, empreintes, compatibilités, limites et méthode de vérification.
- Générateur déterministe et contrôle non destructif dans `bin/generer_reference_canonique.py`.
- Vérificateur transversal dans `bin/verifier_synchronisation.py`.
- État statique traçable du site dans `web/site/etat-canonique.json`.
- Documentation de référence et rapport de synchronisation.
- Section de transparence légère sur le site; aucune fonctionnalité v2 non disponible n'est annoncée.
- Dix tests de non-régression et de synchronisation ajoutés.

## Exécutions et résultats

Les durées ci-dessous sont les durées terminales réellement observées. Lorsqu'une première itération n'a pas été chronométrée par le lanceur, elle est indiquée comme telle au lieu d'être estimée.

### Développement des contrôles canoniques

Commande :

```powershell
python -B -m unittest -v core.tests.test_reference_canonique
```

- Première itération : échec avant exécution des tests (`KeyError` de nommage); durée non consignée. Le nommage du registre a été corrigé.
- Deuxième itération : 8/10 réussis, 2 échecs (déclarations statiques manquantes et mutation de test trop étroite); durée non consignée. Les déclarations et le test ont été corrigés.
- Résultat final : 10/10 réussis en 6,286 s (6,974 s mesurées de bout en bout).

### Tentative groupée trop large

Commande lancée :

```powershell
python -B -m unittest -v core.tests.test_reference_canonique core.tests.test_manifeste_corpus core.tests.test_schemas_v2 core.tests.test_relations_v2 core.tests.test_registres_v2 core.tests.test_experience_relations core.tests.test_migration_relations_v2 core.tests.test_carte core.tests.test_audit_relations; node --check web/site/app.js; Push-Location web; npm.cmd test; Pop-Location
```

- Résultat : délai limite atteint à 304 s avant résultat Python exploitable; les commandes JavaScript situées après le séparateur n'ont donc pas été créditées comme exécutées.

### Contrôles ciblés séparés

```powershell
python -B -m unittest -v core.tests.test_reference_canonique core.tests.test_manifeste_corpus core.tests.test_schemas_v2 core.tests.test_relations_v2 core.tests.test_registres_v2 core.tests.test_experience_relations core.tests.test_migration_relations_v2 core.tests.test_audit_relations
```

- Résultat : 46/46 réussis en 21,557 s (22,512 s de bout en bout).

```powershell
node --check web/site/app.js
Push-Location web
npm.cmd test
Pop-Location
```

- Résultat : syntaxe JavaScript valide; 56/56 tests Worker réussis en 470,835 ms (4,528 s de bout en bout).

### Génération et synchronisation

```powershell
python -B bin/generer_reference_canonique.py
python -B bin/generer_reference_canonique.py --check
python -B bin/verifier_synchronisation.py --output documentation/RAPPORT_SYNCHRONISATION_2026-08-04.md
```

- Résultat : artefacts générés puis contrôlés conformes; rapport `CONFORME`.
- Avertissements conservés : versions des règles D1 historiques inconnues; commit du déploiement public inconnu.

### Suite Python complète

```powershell
python -B -m unittest discover -s core/tests -p 'test_*.py' --durations 30 -v
```

- Résultat : 440/440 tests réussis en 1 084,856 s (1 093,003 s de bout en bout), code terminal 0.
- Des `ResourceWarning` concernant des connexions SQLite non fermées ont été émis par des tests préexistants; ils n'ont pas causé d'échec et restent une dette technique distincte.

### Contrôle final après suite complète

```powershell
python -B bin/generer_reference_canonique.py --check
python -B bin/verifier_synchronisation.py
node --check web/site/app.js
git diff --check
```

- Résultat : registre et état du site conformes, synchronisation `CONFORME`, syntaxe valide et aucune erreur d'espacement Git.

## État de clôture

- **Canonisé techniquement** : D1 historique gelé, manifeste courant, provenance des couches, état statique du site et assertions de synchronisation.
- **Expérimental** : fondations relationnelles v2, prototype Freud–Stekel, homonymes translexicaux et migration additive non appliquée.
- **Automatiquement observé** : relations, clusters, signaux et mesures du site; aucune promotion en validation humaine.
- **Humainement validé** : aucune nouvelle donnée dans le cadre de cette consolidation.
- **Inconnu** : versions exactes des règles historiques D1 et commit du déploiement public.
- **Indécidable** : verdict unique de l'acte 96, maintenu comme agrégat discordant.
- **Restant à décider** : protocole et lancement éventuel d'une campagne humaine, politique de promotion des résultats v2 et traçabilité future du déploiement public.
