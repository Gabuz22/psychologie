# Psychologie — atomisation du corpus psychanalytique

Transformer l'œuvre des fondateurs de la psychologie en **données exploitables**, pour étudier
autrement ce qu'ils ont écrit : suivre un concept d'un bout à l'autre d'un livre, distinguer ce
qui est affirmé de ce qui est supposé, repérer où un auteur se corrige, comparer des œuvres.

Première étape : **Freud**, dans le **texte allemand original**.

---

## Pourquoi l'allemand

Deux raisons, dans cet ordre :

1. **La citation reste vérifiable.** Un psychologue ou un psychanalyste retrouve le mot exact
   qu'a écrit Freud, sans passer par une traduction qui aurait déjà tranché à sa place.
2. **On évite les querelles de traduction.** *Trieb* → « pulsion » ou « instinct », *Nachträglichkeit*
   → « après-coup »… Ces choix sont contestés et varient selon les écoles ; les hériter en amont
   contaminerait toute l'analyse.

Le travail d'analyse, lui, se fait en français. La traduction des concepts viendra comme une
**couche séparée**, posée sur des atomes qui, eux, restent en allemand.

---

## Corpus

Trois œuvres, choisies pour couvrir 20 ans d'évolution théorique :

| Œuvre | Original | Édition lue | Source |
|---|---|---|---|
| *Die Traumdeutung* | 1900 | 4ᵉ éd., 1914 | [Gutenberg #40739](https://www.gutenberg.org/ebooks/40739) |
| *Drei Abhandlungen zur Sexualtheorie* | 1905 | 4ᵉ éd., 1920 | [Gutenberg #39938](https://www.gutenberg.org/ebooks/39938) |
| *Jenseits des Lustprinzips* | 1920 | 2ᵉ éd., 1921 | [Gutenberg #28220](https://www.gutenberg.org/ebooks/28220) |

**Domaine public** — Freud (1856-1939) est libre de droits depuis 2010 (vie + 70 ans) ; les
éditions utilisées sont antérieures à 1931.

**Pourquoi Gutenberg plutôt qu'un scan.** Les fac-similés d'archive.org ont été testés : l'OCR
comporte 2 716 caractères parasites et plus de 2 000 jetons corrompus (`Patielitin` pour
*Patientin*, `Kealen` pour *Realen*, `Eeibc` pour *Reihe*). Suffisant pour segmenter, **inutilisable
pour citer** — ce qui aurait ruiné la raison même de travailler sur l'original. Les éditions
Gutenberg sont relues par des humains (Distributed Proofreaders), orthographe d'origine conservée
et corrections signalées. Les scans restent référencés comme **fac-similés de contrôle**.

---

## Ce qu'est un atome

Une **phrase**, plus tout ce qui permet de la situer, de la qualifier et de la **retrouver dans la
source**.

```json
{
  "id": "traumdeutung:a3184",
  "texte": "Ich habe also in diesem Traume bereits an zwei Personen Rache genommen.",
  "debut": 612430, "fin": 612501,
  "chapitre": {"numero": "II", "titre": "Die Methode der Traumdeutung."},
  "fonctions": ["inference"],
  "signaux_a_confirmer": [],
  "statut": "affirme",
  "concepts": [{"groupe": "reve", "concept": "traum"}],
  "attestation": {"regle": "attesté au plus tard dans l'édition 1914 ; première apparition inconnue dans [1900, 1914]"}
}
```

Trois couches cumulables : **fonction** (ce que la phrase fait), **statut** (avec quelle force elle
l'affirme), **concepts** (de quoi elle parle). Un atome peut relever de plusieurs groupes à la fois.

---

## État actuel

**8 602 atomes** sur trois œuvres, tous localisables dans la source, produits sans aucun modèle de
langage : le pipeline est **entièrement déterministe** (même texte → mêmes atomes).

| Œuvre | Atomes | Localisation | Qualifiés | À confirmer |
|---|---:|---|---:|---:|
| *Die Traumdeutung* | 7 198 | 100 % | 62 % | 100 |
| *Drei Abhandlungen* | 837 | 100 % | 70 % | 9 |
| *Jenseits des Lustprinzips* | 567 | 100 % | 65 % | 7 |

38 tests couvrent les invariants (recomposition, localisation, non-durcissement des propos,
séparation acquis / à confirmer).

---

## Trois choses à savoir avant d'utiliser cette base

1. **La datation est une fourchette, pas une date.** Aucune édition disponible n'est une première
   édition, et Freud a cessé de signaler ses ajouts à partir de la 3ᵉ édition. Un atome est
   « attesté *au plus tard* » dans l'édition lue.
2. **Un marqueur lexical ne prouve pas une révision.** Mesuré : ~3 vrais positifs sur 7. Ces
   signaux alimentent une **liste à vérifier**, jamais les faits établis.
3. **Tout terme ajouté au lexique doit être vérifié sur les formes réellement captées.**
   L'allemand compose : `traum` attrapait *Trauma*, et le correctif naïf a ensuite fait perdre
   *Traumarbeit* (le travail du rêve, 126 occurrences). L'intuition ne suffit pas — il faut
   regarder le texte. Procédure et mesures dans l'inventaire.

Détail et mesures : [`documentation/INVENTAIRE_ATOMES.md`](documentation/INVENTAIRE_ATOMES.md).

---

## Utilisation

```bash
python bin/atomiser.py                    # atomise tout le corpus → derive/
python bin/atomiser.py traumdeutung       # une seule œuvre
python -m unittest discover -s core/tests -t .
```

Aucune dépendance : bibliothèque standard Python uniquement.

```
sources/freud/de/   textes originaux — jamais modifiés
core/               pipeline déterministe (segmentation, lexique, atomisation)
derive/             sorties régénérables
documentation/      inventaire empirique et méthode
```

---

## Suite

La méthode est prouvée sur trois textes. Restent à faire, dans l'ordre :

1. **Étendre le corpus** au reste de l'œuvre (~24 volumes).
2. **Dater les couches** par collation avec les premières éditions.
3. **Vérifier les signaux** repérés (révisions, objections) — c'est là qu'un modèle de langage
   apporte ce qu'un lexique ne peut pas.
4. **Comparer les auteurs** : l'ontologie est conçue pour accueillir Jung, Klein, Lacan, afin de
   voir comment les courants se recomposent à partir des mêmes atomes fondateurs.
