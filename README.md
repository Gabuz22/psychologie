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

**Douze œuvres, 1900-1933.** Une **★** signale une datation certaine : édition d'origine, ou
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
| *Eine Teufelsneurose im 17. Jahrhundert* ★ | 1923 | 1ʳᵉ éd., 1923 | [Wikisource DE](https://de.wikisource.org/wiki/Eine_Teufelsneurose_im_siebzehnten_Jahrhundert) |
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

**18 659 atomes** sur vingt œuvres, **tous** localisables dans la source, produits sans aucun modèle
de langage : le pipeline est **entièrement déterministe** (même texte → mêmes atomes).
73 % sont qualifiés ; **15 œuvres sur 20 ont une datation certaine** rien qu'à l'échelle de
l'œuvre — quatre autres le sont phrase par phrase grâce à la collation (§ ci-dessous).

Le corpus a maigri en gagnant une œuvre : ~73 000 signes de **paratexte d'éditeur** ont été
retirés — bibliographies, catalogues de vente, colophons — dont les 56 000 du seul
*Literaturverzeichnis* de la *Traumdeutung*, qui produisaient des atomes du genre
« *#Alix.# Les rêves. Rev. Scient.* ».

**Finesse de la catégorisation** — 15 groupes conceptuels, 104 concepts, 19 sous-concepts,
11 fonctions argumentatives, 4 statuts épistémiques. En pratique le corpus présente
**4 901 combinaisons distinctes** : un profil différent toutes les 3,2 phrases en moyenne.

86 tests couvrent les invariants (recomposition, localisation, non-durcissement des propos,
séparation acquis / à confirmer, pièges du lexique allemand, déterminisme des agents).

---

## Les agents déterministes

Sept agents lisent le corpus et répondent chacun à une question. Aucun n'emploie de modèle de
langage : leurs résultats sont **reproductibles** — donc discutables, puisqu'on peut refaire le
calcul au lieu de faire confiance. Chaque sortie est **citable** jusqu'au texte allemand.

| Agent | Question |
|---|---|
| `profil` | De quoi cette œuvre parle-t-elle, et qu'est-ce qui lui est **propre** ? |
| `concept` | Que dit Freud d'un concept, sur quel ton, avec quelles citations ? |
| `cooccurrence` | Quels concepts pense-t-il **ensemble** ? |
| `courants` | Ces concepts forment-ils des **grappes** distinctes — candidats de courants ? |
| `chronologie` | La place d'un concept change-t-elle d'une œuvre à l'autre ? |
| `tension` | Où trouve-t-on des énoncés de sens opposé sur un même concept ? |
| `signaux` | Quels passages sont vérifiés, lesquels restent à lire ? |

La **collation** (`core/collation.py`) confronte une œuvre à sa première édition pour dater chaque
phrase. Elle s'appuie sur les fac-similés océrisés d'archive.org — écartés pour le corpus de
travail parce qu'illisibles pour citer, mais parfaitement suffisants ici : établir qu'un passage
*existe* est une exigence bien plus faible que le citer. Deux écarts sont neutralisés (la réforme
orthographique de 1901, et les fautes d'océrisation) et la méthode doit **prouver qu'elle sait
discriminer** — témoin négatif universel et distribution bimodale — avant de dater quoi que ce soit.

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
| `revision` | 16 | 16 | 5 | 11 | **0,31** |
| `objection` | 108 | 108 | 61 | 47 | **0,56** |
| `auto_citation` | 59 | 59 | 31 | 28 | **0,53** |

**97 signaux opposables** — dont les objections que Freud dresse contre ses propres thèses
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

L'agent `profil` retrouve la marque propre des **vingt** œuvres, sans qu'on lui ait rien dit de leur
contenu : *Die Traumdeutung* → rêve ; *Der Witz* → comique ; *Totem und Tabu* → anthropologie ;
*Massenpsychologie* → social ; *Das Unheimliche* → esthétique ; *Zur Psychopathologie* → mémoire
et actes manqués ; *Über Psychoanalyse* → conflit et cure ; *Der Dichter und das Phantasieren* →
esthétique et désir. Vingt sur vingt — y compris les œuvres les plus courtes du corpus (44 et 21
atomes), où le signal a pourtant beaucoup moins de matière pour se dégager.

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

L'agent `courants` va plus loin : il partitionne tout le graphe de concepts par maximisation
gloutonne de la modularité (Newman, 2004), déterministe — aucune grappe n'est choisie à l'avance.
Sur 96 concepts reliés, la partition atteint **0,354 de modularité** (le seuil de structure réelle
est généralement fixé à 0,30) et fait ressortir sept grappes : travail du rêve, appareil psychique,
clinique pulsionnelle, enfance et famille, psychologie sociale, esthétique, seconde topique. La
seconde topique (*Ich*/*Es*/*Über-Ich*) forme une grappe minuscule et parfaitement pure — aucun
autre concept ne s'y mêle, exactement ce qu'impose sa construction théorique. **C'est cet agent
qui porte l'objectif long terme** : si les courants postérieurs se recomposent à partir des mêmes
atomes fondateurs, un premier signe est qu'ils s'y regroupent déjà, avant même qu'aucun courant
rival n'existe. Détail dans [`documentation/SYNTHESE_FREUD.md`](documentation/SYNTHESE_FREUD.md#2-les-concepts-que-freud-pense-ensemble).

---

## Cinq choses à savoir avant d'utiliser cette base

1. **La datation est faite phrase par phrase, là où elle a pu l'être.** Freud a cessé de signaler
   ses ajouts dès la 3ᵉ édition : les couches d'écriture sont invisibles dans le texte. Quatre
   œuvres ont donc été **collationnées** avec leur première édition — chaque atome sait s'il était
   là dès l'origine ou s'il fut ajouté ensuite. Sept autres sont lues dans leur édition d'origine.
   Ne reste incertaine que *Jenseits des Lustprinzips*, où la méthode **refuse de conclure**.
2. **Un marqueur lexical ne prouve pas une révision.** Mesuré : ~3 vrais positifs sur 7. Ces
   signaux alimentent une **liste à vérifier**, jamais les faits établis.
3. **Tout terme ajouté au lexique doit être vérifié sur les formes réellement captées.**
   L'allemand compose : `traum` attrapait *Trauma*, et le correctif naïf a ensuite fait perdre
   *Traumarbeit* (le travail du rêve, 126 occurrences). L'intuition ne suffit pas — il faut
   regarder le texte. Procédure et mesures dans l'inventaire.

4. **Les jugements sont ancrés sur le TEXTE, pas sur le rang.** Les identifiants d'atomes sont
   positionnels : retirer du paratexte en amont les décale. Le registre de vérification est donc
   clé par empreinte de contenu — sans quoi 194 jugements lus à la main pointeraient dans le vide
   au premier nettoyage.
5. **Un volume n'est pas d'un seul auteur.** La 4ᵉ édition de la *Traumdeutung* contient un
   appendice d'**Otto Rank** (« *Traum und Dichtung* », « *Traum und Mythus* ») — 334 atomes, 7 %
   du volume. Chaque atome porte donc son auteur réel ; ne pas le faire mesurerait deux plumes
   pour une. Le défaut a été décelé par des passages parlant de « *der Freudschen Auffassung* »
   à la troisième personne.

**Résultats en clair : [`documentation/SYNTHESE_FREUD.md`](documentation/SYNTHESE_FREUD.md)** —
ce que le corpus dit de Freud, sans jargon technique.
Détail méthodologique : [`documentation/INVENTAIRE_ATOMES.md`](documentation/INVENTAIRE_ATOMES.md).

---

## Utilisation

```bash
python bin/atomiser.py                    # atomise tout le corpus → derive/
python bin/atomiser.py traumdeutung       # une seule œuvre

python bin/analyser.py                    # état des lieux : profils, co-occurrences, signaux
python bin/analyser.py trieb              # dossier d'un concept + chronologie + tensions
python bin/analyser.py --agent cooccurrence
python bin/analyser.py angst --json       # sortie brute, pour chaîner

python bin/rechercher.py --concept trieb --annee-max 1905      # recherche multicritère
python bin/rechercher.py --auteur "Otto Rank"                  # filtre par auteur réel
python bin/rechercher.py --groupe pulsion --csv > citations.csv  # export pour un tableur

python -m unittest discover -s core/tests -t .
```

Aucune dépendance : bibliothèque standard Python uniquement.

```
sources/freud/de/          textes de travail — jamais modifiés
sources/freud/facsimiles/  1res éditions océrisées — collation seulement, jamais citées
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

La base est complète et outillée sur **vingt** œuvres majeures — un peu plus de la moitié du
corpus des grands ouvrages de Freud identifiés comme dignes d'atomisation. Fait :

- **Corpus étendu** à vingt œuvres (1908-1933) : huit ajoutées en une passe (dont *Eine
  Kindheitserinnerung des Leonardo da Vinci*), toutes du vrai `gutenberg.org`, même exigence de
  qualité (relecture Distributed Proofreaders) que le reste. Pipeline inchangé : ajout déclaratif,
  atomisation mémorisée, agents inchangés.
- **Datation par collation** pour quatre œuvres (chaque atome sait s'il est d'origine ou ajouté) ;
  quinze autres lues dans leur édition d'origine (datation certaine à l'échelle de l'œuvre). Ne
  reste incertaine que *Jenseits des Lustprinzips* — aucun meilleur fac-similé de sa 1ʳᵉ édition
  n'existe sur archive.org (recherche faite, documentée dans `SYNTHESE_FREUD.md`) : la méthode
  refuse de conclure plutôt que dater faux.
- **Vérification faite** pour les 192 signaux du corpus actuel (dont les 9 apportés par les huit
  œuvres ajoutées) ; à reconduire sur chaque œuvre future (le registre est cumulatif, rien ne se
  rejoue).
- **Premier regroupement en grappes** (agent `courants`) sur les atomes de Freud seul — sept
  grappes, modularité 0,354. Prochaine étape naturelle : comparer avec un premier auteur non
  freudien pour voir si SES concepts recomposent ou déplacent ces grappes.
- **Corpus consultable** sans relancer un script : `bin/rechercher.py` — filtres combinables
  (concept, groupe, sous-concept, auteur, œuvre, statut, fonction, mot-clé, fenêtre d'années),
  export `--json`/`--csv`.
- **Recherche exhaustive et documentée** des œuvres restantes (`SYNTHESE_FREUD.md`, §5) : treize
  œuvres majeures — dont *Das Ich und das Es*, *Hemmung, Symptom und Angst*, les *Vorlesungen*
  de 1917, et les cinq grands cas cliniques — confirmées absentes en qualité citable de
  `gutenberg.org` comme de Wikisource DE (catalogue et API de recherche vérifiés, pas supposés).

Restent à faire :

1. **Achever le corpus freudien**, si un meilleur fac-similé ou une transcription Wikisource
   apparaît un jour pour l'un des treize textes documentés en §5 de `SYNTHESE_FREUD.md` — sinon,
   la limite est structurelle et documentée, pas une tâche en attente.
2. **Comparer les auteurs** : l'ontologie est conçue pour accueillir Jung, Klein, Lacan, afin de
   voir comment les courants se recomposent à partir des mêmes atomes fondateurs. L'agent
   `courants` est l'instrument de cette question — construit et validé sur Freud seul, prêt à
   recevoir un second auteur. C'est la prochaine étape la plus porteuse.
