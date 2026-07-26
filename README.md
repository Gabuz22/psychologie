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

**Onze œuvres, 1900-1933.** Une **★** signale une datation certaine : édition d'origine, ou
réimpression déclarée inchangée.

Deux provenances, pour une raison juridique qu'il faut connaître : le texte allemand de Freud est
libre **partout** depuis 2010 (mort en 1939 + 70 ans), mais `gutenberg.org` est une organisation
**américaine**, soumise à une règle fondée sur la date de *publication* — elle ne distribue donc
pas les œuvres tardives. Les *Neue Folge* (1933) viennent de **Wikisource allemand**, hébergé
ailleurs et sous licence libre, où elles sont légalement disponibles et relues deux fois.

| Œuvre | Original | Édition lue | Source |
|---|---|---|---|
| *Die Traumdeutung* | 1900 | 4ᵉ éd., 1914 | [#40739](https://www.gutenberg.org/ebooks/40739) |
| *Zur Psychopathologie des Alltagslebens* | 1901 | Abdruck, 1904 | [#24429](https://www.gutenberg.org/ebooks/24429) |
| *Drei Abhandlungen zur Sexualtheorie* | 1905 | 4ᵉ éd., 1920 | [#39938](https://www.gutenberg.org/ebooks/39938) |
| *Der Witz und seine Beziehung zum Unbewußten* | 1905 | 2ᵉ éd., 1912 | [#76423](https://www.gutenberg.org/ebooks/76423) |
| *Der Wahn und die Träume in Jensens »Gradiva«* ★ | 1907 | 1ʳᵉ éd., 1907 | [#35549](https://www.gutenberg.org/ebooks/35549) |
| *Über Psychoanalyse: Fünf Vorlesungen* ★ | 1910 | 2ᵉ éd., 1910 | [#20613](https://www.gutenberg.org/ebooks/20613) |
| *Totem und Tabu* ★ | 1913 | 3ᵉ éd. **inchangée**, 1922 | [#37065](https://www.gutenberg.org/ebooks/37065) |
| *Das Unheimliche* ★ | 1919 | 1ʳᵉ publication, 1919 | [#34222](https://www.gutenberg.org/ebooks/34222) |
| *Jenseits des Lustprinzips* | 1920 | 2ᵉ éd., 1921 | [#28220](https://www.gutenberg.org/ebooks/28220) |
| *Massenpsychologie und Ich-Analyse* ★ | 1921 | 1ʳᵉ éd., 1921 | [#30843](https://www.gutenberg.org/ebooks/30843) |
| *Neue Folge der Vorlesungen* ★ | 1933 | 1ʳᵉ éd., 1933 | [Wikisource DE](https://de.wikisource.org/wiki/Neue_Folge_der_Vorlesungen_zur_Einf%C3%BChrung_in_die_Psychoanalyse) |

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

**17 975 atomes** sur onze œuvres, **tous** localisables dans la source, produits sans aucun modèle
de langage : le pipeline est **entièrement déterministe** (même texte → mêmes atomes).
71 % sont qualifiés ; **6 œuvres sur 11 ont une datation certaine**.

**Finesse de la catégorisation** — 15 groupes conceptuels, 104 concepts, 19 sous-concepts,
11 fonctions argumentatives, 4 statuts épistémiques. En pratique le corpus présente
**4 901 combinaisons distinctes** : un profil différent toutes les 3,2 phrases en moyenne.

70 tests couvrent les invariants (recomposition, localisation, non-durcissement des propos,
séparation acquis / à confirmer, pièges du lexique allemand, déterminisme des agents).

---

## Les agents déterministes

Six agents lisent le corpus et répondent chacun à une question. Aucun n'emploie de modèle de
langage : leurs résultats sont **reproductibles** — donc discutables, puisqu'on peut refaire le
calcul au lieu de faire confiance. Chaque sortie est **citable** jusqu'au texte allemand.

| Agent | Question |
|---|---|
| `profil` | De quoi cette œuvre parle-t-elle, et qu'est-ce qui lui est **propre** ? |
| `concept` | Que dit Freud d'un concept, sur quel ton, avec quelles citations ? |
| `cooccurrence` | Quels concepts pense-t-il **ensemble** ? |
| `chronologie` | La place d'un concept change-t-elle d'une œuvre à l'autre ? |
| `tension` | Où trouve-t-on des énoncés de sens opposé sur un même concept ? |
| `signaux` | Quels passages sont vérifiés, lesquels restent à lire ? |

### La vérification, cumulative

Un lexique dit **où regarder** ; il ne peut pas trancher qu'un auteur se corrige. Les jugements
portés en contexte — par un humain ou un modèle de langage — sont donc consignés dans
`verification/signaux_verifies.json`, versionné et argumenté : sans cela, chaque relecture
repartirait de zéro.

Trois états, jamais mélangés : **confirmé** (opposable), **rejeté** (écarté, motif à l'appui),
**non lu** (ni promu ni écarté).

**Instruction complète** : les 178 signaux du corpus ont été lus en contexte et jugés un par un.

| Signal | Repérés | Lus | Confirmés | Rejetés | Précision mesurée |
|---|---:|---:|---:|---:|---:|
| `revision` | 15 | 15 | 5 | 9 | **0,33** |
| `objection` | 106 | 106 | 59 | 47 | **0,56** |
| `auto_citation` | 57 | 57 | 30 | 27 | **0,53** |

**94 signaux opposables** — dont les objections que Freud dresse contre ses propres thèses
(« *Es gibt nun einen Einwand, welcher die letzten Schlußfolgerungen umzustoßen droht* »), et ses
renvois datés à ses propres travaux (« *Der Schatten des Objekts ist auf das Ich gefallen, sagte
ich an anderer Stelle* » — sa formule de *Trauer und Melancholie*).

Les rejets valent autant : ils disent ce qu'un lexique ne peut pas voir. Objections appartenant à
un **personnage de roman** (Hanold chez Jensen) ou à une **histoire drôle** ; objections que Freud
adresse **à d'autres** (Frazer, Trotter, Scherner) et non à lui-même ; renvois **prospectifs**
(« *cela sera traité ailleurs* ») pris pour des auto-citations ; et de purs homonymes —
« *einwandfrei* » (irréprochable) n'a rien d'une objection, « *einwandern* » veut dire immigrer.

Trois marqueurs ont été corrigés à la source plutôt que d'annoter leur bruit : `freilich`
(concessif, 60 faux candidats), `einwandfrei`, `einwandern`.

Un **chef d'orchestre** choisit les agents selon la question : passe générale sans argument,
suite ciblée (`concept` → `chronologie` → `tension`) quand un concept est donné. Un agent en
échec est signalé et isolé — il ne fait jamais tomber le dossier.

**Ce que ça donne déjà.**

L'agent `profil` retrouve la marque propre des **dix** œuvres, sans qu'on lui ait rien dit de leur
contenu : *Die Traumdeutung* → rêve ; *Der Witz* → comique ; *Totem und Tabu* → anthropologie ;
*Massenpsychologie* → social ; *Das Unheimliche* → esthétique ; *Zur Psychopathologie* → mémoire
et actes manqués ; *Über Psychoanalyse* → conflit et cure. Dix sur dix.

L'agent `cooccurrence` retrouve les couples que tout lecteur de Freud reconnaît : *Wunsch* +
*Wunscherfüllung*, *Sadismus* + *Masochismus*, *Traumgedanke* + *Trauminhalt* (latent / manifeste),
*Tabu* + *Verbot*, *Vater* + *Mutter*, *Führer* + *Masse*. Et il fait apparaître des **ponts entre
œuvres** : *Komik* + *Lustprinzip* relie *Der Witz* (1905) au vocabulaire économique de *Jenseits*
(1920) — c'est la thèse même du livre sur le mot d'esprit, le plaisir né d'une épargne de dépense
psychique.

La chronologie retrouve l'histoire réelle des concepts. `trieb` : 5 ‰ dans la *Traumdeutung*
(1900), 141 ‰ dans les *Trois essais* (1905), 231 ‰ dans *Jenseits* (1920). Et la **seconde
topique apparaît à sa date** : `Über-Ich` est absent de tout le corpus jusqu'à 1933 (29 ‰) ;
`Es` reste sous 1 ‰ avant 1920 puis saute à 23 ‰ ; `Ich` culmine en 1921 — dans un livre qui
s'intitule précisément *Massenpsychologie und **Ich-Analyse***.

C'est cet agent qui portera l'objectif long terme : si les courants postérieurs se recomposent à
partir des mêmes atomes fondateurs, ils apparaîtront d'abord comme des grappes de concepts.

---

## Quatre choses à savoir avant d'utiliser cette base

1. **La datation est une fourchette, pas une date.** Aucune édition disponible n'est une première
   édition, et Freud a cessé de signaler ses ajouts à partir de la 3ᵉ édition. Un atome est
   « attesté *au plus tard* » dans l'édition lue.
2. **Un marqueur lexical ne prouve pas une révision.** Mesuré : ~3 vrais positifs sur 7. Ces
   signaux alimentent une **liste à vérifier**, jamais les faits établis.
3. **Tout terme ajouté au lexique doit être vérifié sur les formes réellement captées.**
   L'allemand compose : `traum` attrapait *Trauma*, et le correctif naïf a ensuite fait perdre
   *Traumarbeit* (le travail du rêve, 126 occurrences). L'intuition ne suffit pas — il faut
   regarder le texte. Procédure et mesures dans l'inventaire.

4. **Un volume n'est pas d'un seul auteur.** La 4ᵉ édition de la *Traumdeutung* contient un
   appendice d'**Otto Rank** (« *Traum und Dichtung* », « *Traum und Mythus* ») — 334 atomes, 7 %
   du volume. Chaque atome porte donc son auteur réel ; ne pas le faire mesurerait deux plumes
   pour une. Le défaut a été décelé par des passages parlant de « *der Freudschen Auffassung* »
   à la troisième personne.

Détail et mesures : [`documentation/INVENTAIRE_ATOMES.md`](documentation/INVENTAIRE_ATOMES.md).

---

## Utilisation

```bash
python bin/atomiser.py                    # atomise tout le corpus → derive/
python bin/atomiser.py traumdeutung       # une seule œuvre

python bin/analyser.py                    # état des lieux : profils, co-occurrences, signaux
python bin/analyser.py trieb              # dossier d'un concept + chronologie + tensions
python bin/analyser.py --agent cooccurrence
python bin/analyser.py angst --json       # sortie brute, pour chaîner

python -m unittest discover -s core/tests -t .
```

Aucune dépendance : bibliothèque standard Python uniquement.

```
sources/freud/de/   textes originaux — jamais modifiés
core/               segmentation · lexique · atomisation · corpus · agents
bin/                atomiser.py (produire) · analyser.py (interroger)
derive/             sorties régénérables
documentation/      inventaire empirique et méthode
```

**Ajouter une œuvre** : déposer le texte dans `sources/freud/de/`, l'inscrire dans
`core/sources.py:OEUVRES` (avec son édition réelle et son année de parution), relancer les tests.
Le lexique et les agents n'ont pas à changer — mais vérifiez les **formes réellement captées**
par tout nouveau terme ajouté (voir le point 3 ci-dessus).

---

## Suite

La base est complète et outillée sur trois textes : elle est prête à recevoir la suite de l'œuvre.
Restent à faire, dans l'ordre :

1. **Étendre le corpus** au reste de l'œuvre (~24 volumes). Le pipeline est prévu pour : ajout
   déclaratif d'une œuvre, atomisation mémorisée, agents inchangés.
2. **Dater les couches** par collation avec les premières éditions — la seule façon de lever
   l'incertitude qui pèse aujourd'hui sur toute chronologie.
3. **Vérification faite** pour les 178 signaux du corpus actuel ; à reconduire sur chaque œuvre
   ajoutée (le registre est cumulatif, rien ne se rejoue).
4. **Comparer les auteurs** : l'ontologie est conçue pour accueillir Jung, Klein, Lacan, afin de
   voir comment les courants se recomposent à partir des mêmes atomes fondateurs. L'agent
   `cooccurrence` est l'instrument de cette question.
