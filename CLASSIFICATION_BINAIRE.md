# Agents binaires de Psychologie

L'adaptateur est `core/classification_binaire.py`. Il genere le registre directement depuis les
lexiques d'auteur existants : aucune seconde taxonomie n'est maintenue a la main.

Commandes depuis la racine `Psychologie` :

```text
python bin/classifier_binaire.py registry
python bin/classifier_binaire.py classify traumdeutung --limit-per-work 100
python bin/classifier_binaire.py progress
python bin/classifier_binaire.py resume --limit 100
python bin/classifier_binaire.py verify --limit 100
```

Sans `--limit-per-work`, `classify` traite toutes les phrases des oeuvres demandees. Le
verificateur ne recalcule que les atomes termines dont le registre effectif n'est plus courant ;
`--force` permet une relecture explicite meme sans changement de version.

Le perimetre taxonomique est l'auteur du volume, conformement a l'atomisation canonique. Une
contribution de Breuer dans un volume freudien garde son auteur reel en metadonnee, mais utilise
le lexique Freud du volume.
