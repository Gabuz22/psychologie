# Psychologie — atomisation du corpus psychanalytique

Transformer l'œuvre des fondateurs de la psychologie en **données exploitables**, pour étudier
autrement ce qu'ils ont écrit : suivre un concept d'un bout à l'autre d'un livre, distinguer ce
qui est affirmé de ce qui est supposé, repérer où un auteur se corrige, comparer des œuvres.

Premier chantier : **Freud**, dans le **texte allemand original** (23 œuvres). Puis **Gustave
Le Bon**, *Psychologie des foules* (1895), en français — le livre que Freud discute pendant tout
un chapitre de *Massenpsychologie und Ich-Analyse*. Depuis le 28 juillet 2026, deux figures de
l'entourage, traitées **pour elles-mêmes** avec leurs propres catégories : **Otto Rank**
(6 œuvres, 1907-1928), celui qui s'écarte, et **Karl Abraham** (5 œuvres, 1909-1925), celui qui
approfondit sans jamais rompre.

---

## Un lexique par auteur

**Chaque auteur a ses catégories propres et se travaille séparément.** Les rapprochements entre
auteurs — socles partagés, divergences, approfondissements, contradictions — feront l'objet d'une
couche **explicite** posée par-dessus des graphes construits séparément, avec des forces de
liaison déclarées. Ils ne doivent jamais être un effet de bord du lexique.

Cette règle **renverse** celle qui prévalait au début du projet (un jeu de concepts commun, au
motif qu'on ne peut comparer qu'à travers la même grille). L'objection était réelle, mais son coût
est apparu à l'usage : mesurer Rank avec le vocabulaire de Freud, c'est ne voir de Rank que ce qui
ressemble à Freud. Son motif central — **l'enfant exposé, sauvé des eaux, qui revient tuer son
père** — n'a aucune case chez Freud et serait purement invisible.

Conséquence à ne jamais perdre de vue : **deux auteurs peuvent porter un concept de même nom sans
désigner la même chose.** `geburt` est chez Rank le traumatisme fondateur de toute angoisse ; le
mot n'a pas ce statut chez Freud. La base les tient dans des lignes distinctes (`concepts.auteur_id`),
et rien ne doit les additionner.

Le code est dans [`core/lexiques/`](core/lexiques/) — un module par auteur.

---

## Pourquoi la langue originale

Deux raisons, dans cet ordre :

1. **La citation reste vérifiable.** Un psychologue ou un psychanalyste retrouve le mot exact
   qu'a écrit l'auteur, sans passer par une traduction qui aurait déjà tranché à sa place.
2. **On évite les querelles de traduction.** *Trieb* → « pulsion » ou « instinct », *Nachträglichkeit*
   → « après-coup »… Ces choix sont contestés et varient selon les écoles ; les hériter en amont
   contaminerait toute l'analyse.

Le travail d'analyse, lui, se fait en français. Le moteur est **multilingue par construction** :
segmentation et repérage prennent la langue de l'œuvre en paramètre. Les CONCEPTS, eux,
appartiennent à chaque auteur (voir ci-dessus) : ceux de Le Bon portent des noms français
(`foule`, `meneur`, `contagion`), ceux de Freud, de Rank et d'Abraham des noms allemands. Aucune
phrase n'est jamais traduite.

---

## Corpus

**Trente-cinq œuvres, 1895-1933**, quatre auteurs, deux langues. Une **★** signale une datation
certaine : édition d'origine, ou réimpression déclarée inchangée.

**Sigmund Freud** (texte allemand, `sources/freud/de/`) :

Deux provenances, pour une raison juridique qu'il faut connaître : le texte allemand de Freud est
libre **partout** depuis 2010 (mort en 1939 + 70 ans), mais `gutenberg.org` est une organisation
**américaine**, soumise à une règle fondée sur la date de *publication* — elle ne distribue donc
pas les œuvres tardives. Les *Neue Folge* (1933) viennent de **Wikisource allemand**, hébergé
ailleurs et sous licence libre, où elles sont légalement disponibles et relues deux fois.

| Œuvre | Original | Édition lue | Source |
|---|---|---|---|
| *Studien über Hysterie* (avec Josef Breuer) ★ | 1895 | 1. Auflage, 1895 | [Wikisource DE](https://de.wikisource.org/wiki/Studien_über_Hysterie) |
| *Die Traumdeutung* | 1900 | 4. Auflage, 1914 | [#40739](https://www.gutenberg.org/ebooks/40739) |
| *Zur Psychopathologie des Alltagslebens* | 1901 | Durchgesehener Abdruck, 1904 | [#24429](https://www.gutenberg.org/ebooks/24429) |
| *Drei Abhandlungen zur Sexualtheorie* | 1905 | 4. Auflage, 1920 | [#39938](https://www.gutenberg.org/ebooks/39938) |
| *Der Witz und seine Beziehung zum Unbewußten* | 1905 | 2. Auflage, 1912 | [#76423](https://www.gutenberg.org/ebooks/76423) |
| *Der Wahn und die Träume in W. Jensens »Gradiva«* ★ | 1907 | 1. Auflage (Schriften zur angewandten Seelenkunde, erstes Heft), 1907 | [#35549](https://www.gutenberg.org/ebooks/35549) |
| *Der Dichter und das Phantasieren* ★ | 1908 | 1. Auflage (Neue Revue, Bd. I, 1907/08), 1908 | [#28863](https://www.gutenberg.org/ebooks/28863) |
| *Über Psychoanalyse: Fünf Vorlesungen* ★ | 1910 | 2. Auflage, 1910 | [#20613](https://www.gutenberg.org/ebooks/20613) |
| *Eine Kindheitserinnerung des Leonardo da Vinci* ★ | 1910 | 1. Auflage (Schriften zur angewandten Seelenkunde, VII. Heft), 1910 | [#75455](https://www.gutenberg.org/ebooks/75455) |
| *Totem und Tabu* ★ | 1913 | 3., unveränderte Auflage, 1922 | [#37065](https://www.gutenberg.org/ebooks/37065) |
| *Das Motiv der Kästchenwahl* ★ | 1913 | 1. Auflage (Imago, Bd. II, Heft 3), 1913 | [#24017](https://www.gutenberg.org/ebooks/24017) |
| *Der Moses des Michelangelo* ★ | 1914 | 1. Auflage (Imago, Bd. III), 1914 | [#30762](https://www.gutenberg.org/ebooks/30762) |
| *Zeitgemäßes über Krieg und Tod* ★ | 1915 | 1. Auflage (Imago, Bd. IV), 1915 | [#29941](https://www.gutenberg.org/ebooks/29941) |
| *Vergänglichkeit* ★ | 1916 | 1. Auflage (« Das Land Goethes 1914-1916 », recueil du Berliner Goethebund), 1916 | [#29514](https://www.gutenberg.org/ebooks/29514) |
| *Einige Charaktertypen aus der psychoanalytischen Arbeit* ★ | 1916 | 1. Auflage (Imago, Bd. IV), 1916 | [#29101](https://www.gutenberg.org/ebooks/29101) |
| *Eine Schwierigkeit der Psychoanalyse* ★ | 1917 | 1. Auflage (Imago, Bd. V), 1917 | [#29097](https://www.gutenberg.org/ebooks/29097) |
| *Eine Kindheitserinnerung aus »Dichtung und Wahrheit«* ★ | 1917 | 1. Auflage (Imago, Bd. V), 1917 | [#29946](https://www.gutenberg.org/ebooks/29946) |
| *Das Unheimliche* ★ | 1919 | 1re publication (Imago, Bd. V), 1919 | [#34222](https://www.gutenberg.org/ebooks/34222) |
| *Jenseits des Lustprinzips* | 1920 | 2. durchgesehene Auflage, 1921 | [#28220](https://www.gutenberg.org/ebooks/28220) |
| *Massenpsychologie und Ich-Analyse* ★ | 1921 | 1. Auflage, 1921 | [#30843](https://www.gutenberg.org/ebooks/30843) |
| *Traum und Telepathie* ★ | 1922 | 1. Auflage (Imago, Bd. VIII), 1922 | [#31560](https://www.gutenberg.org/ebooks/31560) |
| *Eine Teufelsneurose im siebzehnten Jahrhundert* ★ | 1923 | 1. Auflage (Imago, Bd. IX), 1923 | [Wikisource DE](https://de.wikisource.org/wiki/Eine_Teufelsneurose_im_siebzehnten_Jahrhundert) |
| *Neue Folge der Vorlesungen zur Einführung in die Psychoanalyse* ★ | 1933 | 1. Auflage, 1933 | [Wikisource DE](https://de.wikisource.org/wiki/Neue_Folge_der_Vorlesungen_zur_Einführung_in_die_Psychoanalyse) |

**Gustave Le Bon** (texte français, `sources/lebon/fr/`) :

| Œuvre | Original | Édition lue | Source |
|---|---|---|---|
| *Psychologie des foules* ★ | 1895 | 1re édition, Félix Alcan, Paris, 1895 | [#24007](https://www.gutenberg.org/ebooks/24007) (scans BnF/Gallica) |

**Otto Rank** (texte allemand, `sources/rank/de/`) — **toutes en premières éditions**, situation
plus favorable que pour Freud, dont la plupart des textes sont lus dans une édition tardive :

| Œuvre | Original | Édition lue | Source |
|---|---|---|---|
| *Der Künstler* ★ | 1907 | 1. Auflage, Hugo Heller, Wien | [archive.org](https://archive.org/details/derknstleranstz00rankgoog) |
| *Der Mythus von der Geburt des Helden* ★ | 1909 | 1. Auflage (Schriften zur angewandten Seelenkunde, V) | [archive.org](https://archive.org/details/SzaS_5_Rank_1909_Mythus_von_der_Geburt_des_Helden) |
| *Die Lohengrinsage* ★ | 1911 | 1. Auflage (id., XIII) | [archive.org](https://archive.org/details/SzaS_13_Rank_1911_Die_Lohengrinsage) |
| *Das Inzest-Motiv in Dichtung und Sage* ★ | 1912 | 1. Auflage | [archive.org](https://archive.org/details/dasinzestmotivin00rank) |
| *Das Trauma der Geburt* ★ | 1924 | 1. Auflage | [archive.org](https://archive.org/details/DasTraumaDerGeburtUndSeineBedeutungFrDiePsychoanalyse) |
| *Grundzüge einer Genetischen Psychologie, II* ★ | 1928 | 1. Auflage | [archive.org](https://archive.org/details/Rank_1928_Genetische_Psychologie_II_k) |

**Karl Abraham** (texte allemand, `sources/abraham/de/`) — ses fac-similés sont les meilleurs du
corpus : 0,05 à 0,54 ‰ de caractères parasites, soit *au niveau ou sous* les textes relus :

| Œuvre | Original | Édition lue | Source |
|---|---|---|---|
| *Traum und Mythus* ★ | 1909 | 1. Auflage (Schriften zur angewandten Seelenkunde, IV) | [archive.org](https://archive.org/details/TraumUndMythus.EineStudieZurVoumllkerpsychologie) |
| *Giovanni Segantini* ★ | 1911 | 1. Auflage (id., XI) | [archive.org](https://archive.org/details/SzaS_11_Abraham_1911_Segantini) |
| *Klinische Beiträge zur Psychoanalyse* | 1907-1920 | 1. Auflage, 1921 | [archive.org](https://archive.org/details/KlinischeBeitraumlgeZurPsychoanalyse) |
| *Versuch einer Entwicklungsgeschichte der Libido* ★ | 1924 | 1. Auflage | [archive.org](https://archive.org/details/VersuchEinerEntwicklungsgeschichteDerLibidoAufGrundDerPsychoanalyse) |
| *Psychoanalytische Studien zur Charakterbildung* | 1921-1925 | 1. Auflage, 1925 | [archive.org](https://archive.org/details/PsychoanalytischeStudienZurCharakterbildung_524) |

*Zur Psychoanalyse der Kriegsneurosen* (1919) est écarté pour une raison de **structure**, non de
qualité : c'est un symposium à cinq voix (Freud, Ferenczi, Abraham, Simmel, Jones). Le lexique
suivant l'auteur du volume, un volume à cinq auteurs n'en a pas — il faudrait un lexique par
région. À reprendre quand Ferenczi entrera : ce volume les concerne tous les deux.

### Les œuvres de Rank sont des FAC-SIMILÉS OCRISÉS, non relus

Le projet avait d'abord **refusé** l'OCR : pour Freud, Gutenberg offrait une transcription relue
par des humains, et prendre un scan aurait dégradé le texte sans contrepartie. Le refus portait sur
un **arbitrage**, pas sur l'OCR en soi. Pour Rank — comme pour Abraham, Ferenczi, Stekel — aucune
transcription relue n'existe, ni sur Gutenberg ni sur Wikisource. Le choix réel est **« OCR ou
rien »**, et renoncer laisserait le corpus définitivement monopolaire.

La doctrine ne bouge pas : **une limite se mesure et s'affiche.** [`core/ocr.py`](core/ocr.py)
mesure la qualité de chaque scan dans les mêmes unités que les textes relus, répare les défauts
déterministes, et **marque** ce qui reste douteux.

| Mesure | Textes relus (étalon) | Rank après traitement |
|---|---|---|
| caractères parasites | 0,45 – 1,23 ‰ | 0,10 – 1,35 ‰ |
| césures non résolues | 0 – 4 | 0 – 17 (toutes des élisions légitimes, « Kunst- und ») |
| phrases corrompues | — | 0,0 – 1,1 % |

**Trois volumes ont été ÉCARTÉS** sur cette mesure, et le dépôt garde leur chiffre
(`sources.FAC_SIMILES_ECARTES`) : *Die Don Juan-Gestalt* (1924) — le « ch » lu « di », 30 des 92
*nicht* écrits *nidit* —, *Der Doppelgänger* (1925) — le « ch » réduit à « h », **7,1 % des
phrases atteintes**, soit un atome sur quatorze — et *Eine Neurosenanalyse in Träumen* (1924),
à 2,6 %, cas limite : c'est pour ceux-là qu'un seuil existe, sinon chaque volume douteux se
discuterait au cas par cas et finirait par entrer. Ce second défaut était invisible au premier
contrôle, écrit pour le premier : il n'a été trouvé **qu'en lisant le texte**.

Les 47 atomes où une trace de corruption subsiste portent un marqueur `ocr_suspect`, visible sur
le site et dans l'API. Ils restent consultables — le lecteur sait seulement qu'il doit vérifier la
citation sur le fac-similé avant de la publier.

Le choix n'est pas décoratif : 1895 est aussi l'année des *Studien über Hysterie*, et les
mécanismes que Le Bon prête à la foule — *contagion*, *prestige*, *imitation* — ont chacun leur
trace comptée chez Freud (*Ansteckung* ×11, *Prestige* ×8 — mot français qu'il conserve tel
quel —, *Nachahmung* ×4 dans *Massenpsychologie*). La controverse est **mesurable des deux côtés**.

**Domaine public** — Freud (1856-1939) est libre de droits depuis 2010, Le Bon (1841-1931)
depuis 2002 (vie + 70 ans) ; les éditions utilisées sont antérieures à 1931.

**Quatre textes de Gutenberg sont volontairement ÉCARTÉS** : les essais de *Totem und Tabu*
publiés séparément dans *Imago* ([#37066](https://www.gutenberg.org/ebooks/37066),
[#37069](https://www.gutenberg.org/ebooks/37069), [#37070](https://www.gutenberg.org/ebooks/37070),
[#37071](https://www.gutenberg.org/ebooks/37071)) sont les chapitres du volume déjà présent —
vérifié par comparaison de fragments, huit sur huit retrouvés mot pour mot. Les ajouter compterait
deux fois les mêmes phrases. La liste est tenue dans `core/sources.py:DOUBLONS_ECARTES` : une
décision négative doit être traçable, sinon elle sera refaite.

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

**45 588 atomes** sur trente-cinq œuvres, quatre auteurs et deux langues, **82 % qualifiés**, **tous**
localisables dans la source, produits sans aucun modèle de langage : le pipeline est **entièrement déterministe**
(même texte → mêmes atomes). **29 œuvres sur 35 ont une datation certaine** à l'échelle de
l'œuvre — quatre autres le sont phrase par phrase grâce à la collation (§ ci-dessous).

| Auteur | Atomes | Qualifiés |
|---|---|---|
| Sigmund Freud | 20 617 | 81 % |
| Otto Rank | 14 990 | 83 % |
| Karl Abraham | 7 611 | 84 % |
| Gustave Le Bon | 1 485 | 84 % |
| Josef Breuer (dans les *Studien*) | 885 | 81 % |

**Le passage au lexique par auteur s'est mesuré.** Le Bon était qualifié à **57 %** tant qu'on le
décrivait avec des identifiants freudiens francisés ; il l'est à **75 %** depuis qu'il a ses
propres catégories (`foule`, `meneur`, `contagion`, `âme`, `révolution`…), sans qu'une seule
ligne du moteur ait changé. Ce n'était donc pas un lexique « jeune » qu'il fallait étoffer :
c'était la grille d'un autre auteur qui ne pouvait pas le voir.

Le corpus a maigri en gagnant une œuvre : ~73 000 signes de **paratexte d'éditeur** ont été
retirés — bibliographies, catalogues de vente, colophons — dont les 56 000 du seul
*Literaturverzeichnis* de la *Traumdeutung*, qui produisaient des atomes du genre
« *#Alix.# Les rêves. Rev. Scient.* ».

**Finesse de la catégorisation** — 19 groupes conceptuels, 171 concepts, 19 sous-concepts,
11 fonctions argumentatives, 4 statuts épistémiques. En pratique le corpus présente
**4 901 combinaisons distinctes** : un profil différent toutes les 3,2 phrases en moyenne.

110 tests couvrent les invariants (recomposition, localisation, non-durcissement des propos,
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

**Instruction complète** : les 214 signaux du corpus ont été lus en contexte et jugés un par un
— dont 22 devenus visibles quand la normalisation des blancs a réparé les marqueurs coupés par
un retour à la ligne (ils dormaient là depuis le début, deux révisions doctrinales parmi eux).

| Signal | Repérés | Lus | Confirmés | Précision mesurée |
|---|---:|---:|---:|---:|
| `revision` | 24 | 24 | 7 | **0,29** |
| `objection` | 111 | 111 | 64 | **0,58** |
| `auto_citation` | 79 | 79 | 38 | **0,48** |

**109 signaux opposables** — dont les objections que Freud dresse contre ses propres thèses
(« *Es gibt nun einen Einwand, welcher die letzten Schlußfolgerungen umzustoßen droht* »), ses
renvois datés à ses propres travaux (« *Der Schatten des Objekts ist auf das Ich gefallen, sagte
ich an anderer Stelle* » — sa formule de *Trauer und Melancholie*), et la correction de sa thèse
sur le « non » : « *…wonach also die frühere Behauptung zu korrigieren ist, daß der Traum das
Nein nicht auszudrücken vermag* » (*Die Traumdeutung*).

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
`Es` est à **zéro atome réel avant 1923** — les 19 détections antérieures, lues une à une lors
de la validation qualitative, étaient toutes le pronom allemand dans une relative, et un test
verrouille désormais ce zéro — puis saute à 21 ‰ en 1933 ; `Ich` culmine en 1921, dans un livre
qui s'intitule précisément *Massenpsychologie und **Ich-Analyse***.

L'agent `courants` va plus loin : il partitionne tout le graphe de concepts par maximisation
gloutonne de la modularité (Newman, 2004), déterministe — aucune grappe n'est choisie à l'avance.
Sur 151 concepts reliés, la partition atteint **0,373 de modularité** (le seuil de structure
réelle est généralement fixé à 0,30) et fait ressortir sept grappes — dont « la famille, la
différence des sexes et la mort », la plus freudienne du lot, et « la clinique », qui s'est
détachée en grappe propre à l'audit 4 du lexique. Chaque grappe a été **validée en lisant**
des atomes-croisements ; les artefacts sont dits (le *Teufel* rejoint la peinture parce que
l'unique cas sur le diable porte sur un peintre). Le dossier complet de chacune est
[`documentation/COURANTS_FREUD.md`](documentation/COURANTS_FREUD.md), **régénéré** par
`bin/generer_courants.py` — un document qui décrit des données calculées ne peut pas rester
juste s'il est tenu à la main. Partitionné séparément, le corpus
1900-1913 contre 1914-1933 montre **trois recompositions datables** — la mort quitte la famille
pour la pulsion, le rêve cesse d'absorber la métapsychologie, la seconde topique naît comme
grappe accolée aux figures parentales. **C'est cet agent qui porte l'objectif long terme** : si
les courants postérieurs se recomposent à partir des mêmes atomes fondateurs, un premier signe
est qu'ils s'y regroupent déjà. Détail dans
[`documentation/SYNTHESE_FREUD.md`](documentation/SYNTHESE_FREUD.md#2-les-concepts-que-freud-pense-ensemble).

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
**Dossiers de référence par grappe : [`documentation/COURANTS_FREUD.md`](documentation/COURANTS_FREUD.md)**
— chronologie, citations validées et réserves pour chacun des huit courants internes.
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

**Le site — [psychologie.guzan99.workers.dev](https://psychologie.guzan99.workers.dev)**
(`web/`) expose le corpus en ligne : recherche multicritère, dossier complet de chaque grappe
(éditorial, citation vedette choisie par l'agent, densité par œuvre), chronologie d'un concept
visualisée, **« Freud sur lui-même »** (les 109 objections, auto-citations et révisions
confirmées, chacune avec le motif du jugement porté en contexte), lecture séquentielle d'une
œuvre, export de citation académique. Cloudflare Worker
+ D1, frontend statique sans framework — le Worker ne calcule rien : il sert en lecture seule
ce que `bin/exporter_d1.py` a déversé du pipeline Python (atomes, concepts, grappes, verdicts,
fenêtres de datation). Mise à jour du site après un changement de corpus : `web/deployer.sh`
(un seul script, rejouable). Déploiement pas à pas : [`web/DEPLOIEMENT.md`](web/DEPLOIEMENT.md).

**Le corpus comme outil pour une IA** — deux façades, une seule logique de requête
(`worker/donnees.js`) et une seule liste d'outils (`worker/outils.js`) :
- **Assistant du site** (section « Assistant ») — répond en langage naturel, mais le LLM ne
  sert QU'À choisir quels outils appeler et mettre leurs résultats en prose. Surtout, chaque
  réponse subit une **vérification déterministe** (`web/worker/verification.js`, 14 tests) :
  citations allemandes, densités en ‰ et identifiants d'atomes sont confrontés aux données
  réellement retournées — **sans aucun modèle de langage dans ce contrôle**. Un écart renvoie
  le modèle à ses sources pour correction ; ce qui résiste est affiché en clair plutôt que tu,
  comme les signaux « à confirmer » du corpus. Nécessite une clé Groq (gratuite) posée en
  secret Cloudflare — voir `web/DEPLOIEMENT.md`.
- **Serveur MCP** (`/mcp`) — un chercheur branche son propre assistant (Claude Desktop, Claude
  Code…) directement sur le corpus, sans passer par le site : `claude mcp add --transport http
  corpus-freud https://psychologie.guzan99.workers.dev/mcp`.

```
sources/freud/de/          textes de travail — jamais modifiés
sources/freud/facsimiles/  1res éditions océrisées — collation seulement, jamais citées
core/               segmentation · lexique · atomisation · corpus · agents
bin/                atomiser.py · analyser.py · rechercher.py · exporter_d1.py
web/                site Cloudflare : worker (API D1) + site (statique) + DEPLOIEMENT.md
derive/             sorties régénérables (dont derive/d1/, les dumps pour D1)
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
- **Vérification faite** pour les 214 signaux du corpus actuel (dont les 9 apportés par les huit
  œuvres ajoutées et les 22 que cachaient des marqueurs coupés par des retours à la ligne) ; à
  reconduire sur chaque œuvre future (le registre est cumulatif, rien ne se rejoue).
- **Premier regroupement en grappes** (agent `courants`) sur les atomes de Freud seul — sept
  grappes, modularité 0,373. Prochaine étape naturelle : comparer avec un premier auteur non
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
