# Ce que le corpus dit de Freud

> **Ce document n'est pas une interprétation.** Tout ce qui suit est produit par des agents
> déterministes — aucun modèle de langage n'intervient dans les mesures. On peut refaire chaque
> calcul (`python bin/analyser.py`) et remonter de n'importe quel chiffre jusqu'à la phrase
> allemande qui le fonde. Là où une lecture humaine a été nécessaire, elle est signalée comme telle.
>
> Corpus : **23 œuvres, 1895-1933, 21 928 atomes** (une phrase = un atome).

---

## 1. Chaque livre reconnu par sa marque propre

L'agent `profil` compare chaque œuvre au reste du corpus et retient ce qui y est **sur-représenté**
— non pas ce qui domine, mais ce qui distingue. Il ne sait rien du contenu des livres : il ne voit
que des atomes catégorisés.

| Œuvre | Atomes | Ce qui la distingue |
|---|---:|---|
| *Die Traumdeutung* (1900) | 5 996 | **rêve**, désir, topique, mémoire |
| *Studien über Hysterie* (1895) | 2 909 | **conflit**, cure, mémoire, topique |
| *Neue Folge der Vorlesungen zur Einführung in…* (1933) | 2 119 | **topique**, rêve, pulsion, épistémè |
| *Der Witz und seine Beziehung zum Unbewußten* (1905) | 2 076 | **comique**, rêve, économie |
| *Totem und Tabu* (1913) | 1 588 | **anthropologie**, morale, famille, mort |
| *Zur Psychopathologie des Alltagslebens* (1901) | 1 051 | **mémoire**, actes manqués, cure, topique |
| *Drei Abhandlungen zur Sexualtheorie* (1905) | 843 | **pulsion**, développement, conflit, économie |
| *Der Wahn und die Träume in W. Jensens »Gradi…* (1907) | 756 | **rêve**, conflit, esthétique, mémoire |
| *Massenpsychologie und Ich-Analyse* (1921) | 699 | **social**, pulsion, topique, cure |
| *Eine Kindheitserinnerung des Leonardo da Vinci* (1910) | 670 | **développement**, famille, esthétique, corps |
| *Jenseits des Lustprinzips* (1920) | 545 | **pulsion**, topique, économie, mort |
| *Über Psychoanalyse: Fünf Vorlesungen* (1910) | 467 | **conflit**, cure, topique, développement |
| *Das Unheimliche* (1919) | 421 | **esthétique**, corps, développement, actes manqués |
| *Eine Teufelsneurose im siebzehnten Jahrhundert* (1923) | 337 | **anthropologie**, esthétique, famille, conflit |
| *Traum und Telepathie* (1922) | 287 | **rêve**, famille, développement, désir |
| *Der Moses des Michelangelo* (1914) | 283 | **corps**, esthétique, économie |
| *Zeitgemäßes über Krieg und Tod* (1915) | 278 | **social**, mort, anthropologie, morale |
| *Einige Charaktertypen aus der psychoanalytis…* (1916) | 233 | **morale**, développement, désir, famille |
| *Das Motiv der Kästchenwahl* (1913) | 127 | **mort**, famille, désir, esthétique |
| *Eine Schwierigkeit der Psychoanalyse* (1917) | 90 | **topique**, pulsion, cure, conflit |
| *Der Dichter und das Phantasieren* (1908) | 88 | **esthétique**, désir, développement, topique |
| *Vergänglichkeit* (1916) | 44 | **mort**, esthétique, social, économie |
| *Eine Kindheitserinnerung aus »Dichtung und W…* (1917) | 21 | **famille**, développement, épistémè, rêve |

**Vingt-trois sur vingt-trois.** Ce n'est pas un résultat sur Freud — c'est un contrôle de
validité : une ontologie qui se tromperait de catégories ne retrouverait pas ces identités, y
compris sur des textes de quelques dizaines d'atomes (*Vergänglichkeit*, *Kindheitserinnerung aus
»Dichtung und Wahrheit«*) où le signal a beaucoup moins de matière pour se dégager. Les deux
œuvres entrées au corpus le dernier jour le confirment à l'aveugle : *Einige Charaktertypen*
reçoit « **morale** » — son sujet est le criminel par sentiment de culpabilité — et *Das Motiv
der Kästchenwahl* reçoit « **mort** », qui est exactement sa thèse : le troisième coffret est la
déesse de la mort. Et *Studien über Hysterie*, entré ensuite, reçoit « **conflit**, cure,
mémoire » — les trois mots qui résument ce livre : l'hystérie, la cure cathartique, et les
réminiscences dont les malades souffrent.

Deux observations méritent d'être notées, parce qu'elles ne se lisent pas dans les titres :

- ***Totem und Tabu*** et ***Massenpsychologie*** partagent la même seconde marque : **famille**.
  Le lien social et la horde primitive sont pensés par Freud avec le vocabulaire du roman familial.
- ***Gradiva*** croise **rêve**, **esthétique** et **conflit** : c'est bien une analyse de rêves
  menée sur une œuvre de fiction.

---

## 2. Les concepts que Freud pense ensemble

L'agent `cooccurrence` mesure la force du lien entre deux concepts (indice de Jaccard : nombre
d'atomes où ils apparaissent ensemble, rapporté aux atomes où l'un ou l'autre paraît). L'indice est
préféré au comptage brut, qui ne ferait que remonter les concepts les plus fréquents.

| Couple | Force | Atomes communs |
|---|---:|---:|
| *Masochismus* + *Sadismus* | 0,270 | 17 |
| *Wunsch* + *Wunscherfüllung* | 0,244 | 154 |
| *Sexualität* + *Trieb* | 0,178 | 169 |
| *Bewußtsein* + *Unbewußt* | 0,148 | 136 |
| *Neurose* + *Symptom* | 0,140 | 90 |
| *Traumgedanke* + *Trauminhalt* | 0,135 | 71 |
| *Tabu* + *Verbot* | 0,119 | 37 |
| *Mutter* + *Vater* | 0,115 | 80 |
| ***Komik* + *Lustprinzip*** | **0,110** | **77** |
| *Apparat* + *Psychisme* | 0,101 | 155 |
| *Es* + *Ich* | 0,098 | 21 |

Ces couples sont ceux que tout lecteur de Freud reconnaît — sadisme et masochisme toujours traités
ensemble, contenu manifeste et pensées latentes, tabou et interdit, le couple parental.

**Le plus intéressant est le neuvième.** *Komik* + *Lustprinzip* relie *Der Witz* (1905) au
vocabulaire économique de *Jenseits* (1920) : c'est la thèse même du livre sur le mot d'esprit —
le plaisir naît d'une **épargne de dépense psychique**. Un pont entre deux œuvres séparées de
quinze ans, trouvé sans qu'on l'ait cherché.

C'est ce type de regroupement qui servira la question de fond du projet : si les courants
postérieurs se recomposent à partir des mêmes atomes fondateurs, ils apparaîtront d'abord comme
des grappes.

### Les paires deviennent sept grappes

L'agent `courants` va plus loin que les paires : il PARTITIONNE tout le graphe de concepts par
maximisation gloutonne de la modularité (Newman, 2004), un algorithme déterministe — aucune
grappe n'est choisie à l'avance, ni leur nombre ni leur taille. Sur 151 concepts suffisamment
reliés, la partition atteint une **modularité de 0,373** — au-dessus du seuil de 0,30 généralement
retenu comme signe d'une vraie structure plutôt que d'un artefact du graphe (Newman & Girvan,
2004). Sept grappes en ressortent :

| Grappe | Concepts (extrait) | Atomes |
|---|---|---:|
| Le rêve, l'appareil psychique et la représentation | *Traum, Verdichtung, Bewußtsein, Besetzung, Vorstellung* | 8 969 |
| La clinique, le corps et la cure | *Hysterie, Conversion, Schmerz, Erinnerung, Hand, Auge* | 4 783 |
| La famille, la différence des sexes et la mort | *Vater, Mutter, Ödipus, Kastration, Schuld, Tod* | 3 774 |
| Religion, anthropologie, morale et lien social | *Totem, Tabu, Gott, Moral, Masse, Zwangsneurose* | 3 338 |
| La pulsion, le développement sexuel et les instances | *Trieb, Libido, Ich, Es, Über-Ich, Gewissen* | 2 570 |
| La fiction, le délire et la création | *Dichter, Erzählung, Phantasie, Wahn, Kunst* | 1 298 |
| La peinture et le pacte | *Malerei, Teufel, Pakt* | 201 |

**Contrôle de sens intégré** (pas seulement mesuré une fois, mais rejoué à chaque test) : *Ich*,
*Es* et *Über-Ich* — la seconde topique, trois concepts inséparables par construction théorique —
tombent TOUJOURS dans la même grappe. *Wunsch* et *Wunscherfüllung*, *Masochismus* et *Sadismus*
aussi. Si l'algorithme les avait dispersés, la partition n'aurait mesuré aucune structure réelle.

**Ces grappes BOUGENT quand l'ontologie s'affine — et c'est un résultat, pas un défaut.**
L'audit 4 du lexique (2026-07) a ajouté 22 concepts, dont la différence des sexes et le
vocabulaire de la cure : la partition s'est recomposée en profondeur (modularité 0,361 → 0,372,
donc une structure un peu plus nette). La clinique s'est détachée en grappe propre au lieu
d'être diluée dans la pulsion ; la différence des sexes a rejoint le roman familial ; la seconde
topique, jusque-là isolée, s'est rattachée au développement sexuel. Une grappe est un état de la
mesure, jamais une vérité sur Freud — le dossier complet de chacune, régénéré à chaque
changement, est dans [`COURANTS_FREUD.md`](COURANTS_FREUD.md).

**Et elles peuvent aussi se CONSOLIDER — ce qui est une limite, pas un progrès.** L'audit 7 a
fait passer la partition de neuf grappes à sept : le rêve a fusionné avec l'appareil psychique,
la clinique a absorbé le corps décrit. En cause, « Vorstellung » (763 occurrences), concept si
transversal qu'il ponte des ensembles jusque-là distincts. La modularité reste bonne (0,373)
mais la grappe de tête compte désormais **44 concepts sur 168** : elle dit un voisinage massif,
non une articulation fine. Plus l'ontologie s'enrichit de termes très connectés, moins la
partition discrimine — à surveiller, et à dire.

**L'entrée du texte FONDATEUR a déplacé la mémoire.** « Studien über Hysterie » (1895) rejoint
le corpus comme son œuvre la plus ancienne — et 2 909 atomes de matière clinique réelle
suffisent à faire migrer *Erinnerung*, *Gedächtnis*, *Vergessen* et *Spur* hors de la grappe du
rêve, où ils vivaient depuis l'origine, vers celle de la CURE. La partition retrouve ainsi la
phrase la plus célèbre du livre : « *Hysterische leiden größtentheils an Reminiscenzen* » — les
hystériques souffrent surtout de réminiscences. Se souvenir n'y est pas une faculté de
l'esprit : c'est le traitement lui-même. Dans le même mouvement, la fiction et le délire se
détachent en grappe propre — le corpus a désormais assez de clinique réelle pour que l'analyse
d'un roman ne se confonde plus avec celle d'un malade.

### Le germe de la rupture est dans le livre fondateur — et il se mesure

L'audit 7 a fait entrer dans l'ontologie l'**état hypnoïde** (*hypnoider Zustand*), non pour
enrichir le lexique mais pour rendre un DÉSACCORD mesurable : c'est la thèse de Breuer, que
Freud abandonnera. Sans le concept, une théorie que le corpus contient pourtant resterait
invisible.

Le résultat demande une nuance que le comptage brut aurait manquée. En valeur absolue, Freud
emploie le terme presque autant que Breuer (26 contre 27 dans le volume) — mais Breuer n'a écrit
que 886 atomes contre 2 023 :

| Auteur | Atomes portant « hypnoïde » | Densité dans SA part |
|---|---:|---:|
| Josef Breuer | 27 | **30,5 ‰** |
| Sigmund Freud | 26 | 12,9 ‰ |

La lecture des passages confirme que l'écart n'est pas seulement de fréquence, mais de position.
Breuer POSE la thèse :

> « *Grundlage und Bedingung der Hysterie ist die Existenz von hypnoiden Zuständen.* »

Freud, dans le même volume, la DÉPLACE déjà :

> « *Ich kann den Verdacht nicht unterdrücken, dass Hypnoid- und Abwehrhysterie irgendwo an
> ihrer Wurzel zusammentreffen, und dass dabei **die Abwehr das Primäre ist**.* »

Le livre qui les réunit contient donc, mesurablement, ce qui les séparera : là où Breuer fonde
l'hystérie sur un état de conscience, Freud fait de la **défense** le fait premier. C'est le seul
endroit du corpus où deux auteurs sont en désaccord — et c'est l'attribution par auteur, posée
pour éviter un contresens, qui permet de le voir.

**L'audit 6 (2026-07) a produit le déplacement le plus parlant.** En faisant entrer la
CONSCIENCE MORALE dans l'ontologie (*Gewissen*, *Schuld*, *Strafe*, absents jusque-là), la
seconde topique a quitté la pulsion pour rejoindre **la masse et le meneur**. Ce n'est pas un
hasard de calcul : c'est la thèse de *Massenpsychologie und Ich-Analyse* (1921) — l'idéal du moi
se forme par identification au meneur, et c'est de là que procède la conscience. Le Moi, le Ça,
le Sur-Moi, la masse, le chef et la conscience morale forment désormais une seule grappe de dix
concepts. La partition a retrouvé seule un lien que Freud met vingt ans à établir.

**L'audit 5 (2026-07) a fait apparaître une grappe que personne n'avait cherchée : le corps
DÉCRIT.** En ajoutant à l'ontologie les parties du corps concrètes — la main, l'œil, le visage,
la barbe, la tête —, la partition les a regroupées d'elle-même en une grappe distincte
(modularité 0,372 → **0,382**). Ce découpage n'était pas prévisible : il sépare le corps
*regardé* du corps *pensé*. « Körper », le somatique abstrait, est resté dans la grappe de
l'appareil psychique ; « Mundzone », la zone érogène orale, dans celle de la sexualité ; seuls
les organes que Freud DÉCRIT en regardant une œuvre — la main du Moïse, les yeux arrachés de
l'homme au sable, le sourire de Monna Lisa — se sont rassemblés. La grappe mesure donc un
**geste** de Freud (décrire ce qu'il voit), pas une doctrine.

Le contrôle le plus net est ailleurs : avant l'audit 5, l'agent `profil` attribuait au
*Moses des Michelangelo* la marque « **économie** » — un contresens manifeste sur une analyse
de sculpture, faute de vocabulaire pour la décrire. Sa marque est désormais « **corps** », et
son taux d'atomes non qualifiés est passé de **43 % à 28 %**. Une ontologie trouée ne se
contente pas de manquer des choses : elle en dit de fausses.

### Validation qualitative — les grappes lues, pas seulement comptées

Chaque grappe a été validée en lisant des atomes-croisements (portant au moins deux concepts de
la grappe À LA FOIS), répartis sur plusieurs œuvres. Ce que la lecture confirme, et ce qu'elle
nuance :

- **« Père, religion, mort » est la grappe la plus freudienne du lot.** Sa cohérence n'est pas un
  artefact de comptage : c'est le geste théorique même de *Totem und Tabu* (la religion et la
  société dérivées du meurtre du père) et de la *Teufelsneurose* (le Diable en substitut du père
  mort). Lu en croisement : « *Eine der Reaktionen auf den **Vatermord** war doch die Einrichtung
  der totemistischen **Exogamie*** » (*Massenpsychologie*).
- **« Souvenir et création » est portée par les œuvres sur l'art** : le souvenir d'enfance comme
  matière de l'œuvre est la thèse du *Léonard* et du *Dichter und das Phantasieren*. La grappe
  réunit ce que Freud lie explicitement.
- **Une grappe est en partie un artefact de composition du corpus, et il faut le dire** :
  « peinture » accueille *Teufel* uniquement parce que l'unique œuvre du corpus sur le diable
  (la *Teufelsneurose*) porte sur un **peintre**. La cooccurrence est réelle dans le texte, mais
  elle reflète le hasard biographique d'un cas, pas un lien conceptuel — le genre de nuance
  qu'aucune modularité ne peut voir et que seule la lecture apporte.
- **La validation a débusqué un défaut de données** : les atomes du concept *Es* antérieurs à
  1923, lus un par un, étaient TOUS le pronom allemand dans une relative (« *ein Spielzeug, über
  das es sich geärgert hatte* » — le jouet contre lequel IL s'était fâché), pas le Ça. Motif
  corrigé, chronologie assainie (voir §3), verrou de test posé.

**Ce que ces grappes ne sont pas** : des courants postérieurs. Freud n'a jamais rangé sa propre
œuvre ainsi ; c'est une lecture rétrospective de la cooccurrence de ses mots, pas une
classification qu'il revendique. Une grappe computée est un candidat de lecture — validé ici,
mais jamais opposable seul.

**Le dossier complet de chaque grappe** — chronologie par œuvre, part datée d'origine,
citations validées, réserves — est dans [`COURANTS_FREUD.md`](COURANTS_FREUD.md).

---

## 3. La chronologie des concepts

L'agent `chronologie` mesure la densité d'un concept par œuvre (en ‰ des atomes).

**Quatre œuvres sont désormais COLLATIONNÉES** : chacune a été confrontée à sa première édition,
phrase par phrase, ce qui dit pour chaque passage s'il était là dès l'origine ou s'il fut ajouté
plus tard. Pour celles-là, la datation n'est plus une fourchette mais un fait.

| Œuvre | Éd. lue | Retrouvé dans la 1ʳᵉ éd. | Ajouté après |
|---|---|---:|---:|
| *Die Traumdeutung* | 4ᵉ, 1914 | 4 484 | **1 268** |
| *Der Witz* | 2ᵉ, 1912 | 1 987 | 17 |
| *Drei Abhandlungen* | 4ᵉ, 1920 | 600 | **226** |
| *Zur Psychopathologie* | 1904 | 398 | **609** |

*Zur Psychopathologie* a plus que doublé entre l'article de revue de 1901 et le livre de 1904.
*Der Witz* n'a pratiquement pas bougé entre 1905 et 1912.

### Le symbolisme onirique n'était pas là en 1900

C'est le résultat que la collation seule permet, et il change une lecture courante.

| *Symbol* dans la *Traumdeutung* | |
|---|---:|
| Densité dans l'édition lue (1914) | 26 ‰ |
| Densité **réellement de 1900** | **9 ‰** |
| Passages ajoutés après | **81 sur 121** |

Les deux tiers de ce que la *Traumdeutung* dit du symbolisme ont été **greffés après coup**. Sans
collation, on prêterait à Freud une théorie du symbole qu'il n'avait pas encore en 1900.

Le plus probant : **Freud le dit lui-même**, dans un passage que la collation classe justement
en « ajout » —

> « *Durch eigene Erfahrung wie durch die Arbeiten von W. Stekel und anderen habe ich **seither**
> den Umfang und die Bedeutung der Symbolik im Traume…* »
> (« …j'ai reconnu **depuis lors** l'étendue et l'importance du symbolisme onirique »)

La méthode a détecté l'ajout ; la phrase détectée le confirme.

### La pulsion envahit la pensée de Freud

| Œuvre | *Trieb* |
|---|---:|
| *Die Traumdeutung* (1900) | 5 ‰ |
| *Drei Abhandlungen* (1905) | 141 ‰ |
| *Über Psychoanalyse* (1910) | 66 ‰ |
| *Totem und Tabu* (1913) | 20 ‰ |
| ***Jenseits des Lustprinzips* (1920)** | **231 ‰** |
| *Massenpsychologie* (1921) | 63 ‰ |
| *Neue Folge* (1933) | 58 ‰ |

### La seconde topique apparaît à sa date

| Instance | Avant 1923 | 1933 |
|---|---:|---:|
| *Ich* (le Moi) | 2-49 ‰ | 35 ‰ |
| *Es* (le Ça) | **0 — zéro atome réel** | **21 ‰** |
| *Über-Ich* (le Surmoi) | **absent** | **29 ‰** |

Le Ça et le Surmoi n'existent **pas du tout** dans le vocabulaire de Freud avant les années
1920 — le corpus le retrouve seul, et plus nettement encore depuis la validation qualitative :
les 19 détections antérieures du *Es*, lues une à une, étaient toutes le **pronom** allemand
dans une relative (« *ein Spielzeug, über das es sich geärgert hatte* »), jamais l'instance.
Le motif a été corrigé et un test verrouille désormais ce zéro : si un motif futur réinvente
une préhistoire au Ça, il casse. Le pic du Moi en 1921 tombe sur un livre intitulé
*Massenpsychologie und **Ich-Analyse***.

> **Réserve.** *Das Ich und das Es* (1923), où ces instances sont introduites, **ne figure pas au
> corpus** : aucune source libre n'en propose une transcription de qualité citable — Wikisource ne
> l'a pas transcrit, et l'édition disponible ailleurs est celle de S. Fischer 1975, dont l'appareil
> éditorial est protégé. Même constat pour *Hemmung, Symptom und Angst* (1926). La marche entre
> 1921 et 1933 est donc plus abrupte ici qu'elle ne le fut dans l'œuvre.

### Les grappes se recomposent au milieu de l'œuvre

Si les grappes de concepts mesurent quelque chose de réel, elles doivent BOUGER avec la pensée.
Test : partitionner séparément les œuvres de **1900-1913** (9 œuvres, 13 535 atomes) et de
**1914-1933** (11 œuvres, 5 124 atomes). Contrôle de rigueur : la moitié précoce a aussi été
recalculée en **excluant les 2 120 atomes que la collation date comme ajouts tardifs** — le
résultat tient dans les deux cas (modularité 0,368 avec, 0,381 sans).

Trois recompositions, chacune datable et lisible :

1. **La mort change de camp.** En 1900-1913, *Tod*, *Trauer* et *Sterben* voyagent avec la
   **famille** (*Vater, Mutter, Eltern*) et la religion — la mort est celle des proches, objet
   de deuil et de rêves de mort. En 1914-1933, *Tod* et *Todestrieb* rejoignent la grappe
   **pulsion-biologie** (*Trieb, Libido, Narzißmus, Aggression*). C'est exactement le geste de
   *Jenseits des Lustprinzips* (1920) — la mort cesse d'être un événement familial pour devenir
   un principe pulsionnel — rendu visible par la seule cooccurrence.

2. **Le rêve dégonfle, la métapsychologie s'autonomise.** En 1900-1913, la grappe du rêve est
   un monstre de 26-30 concepts qui absorbe l'appareil psychique entier (*Bewußtsein, Besetzung,
   Energie, Ich*…) : le rêve est le laboratoire de toute la théorie. En 1914-1933, le rêve
   redevient une grappe modeste et l'appareil psychique forme sa propre grappe : la
   métapsychologie n'a plus besoin du rêve pour se dire.

3. **La seconde topique naît comme grappe.** Inexistante avant (le *Ich* précoce vit DANS la
   grappe du rêve), elle émerge en 1914-1933 comme grappe propre — accolée à *Eltern* et
   *Geschwister* : le corpus retrouve seul que le Surmoi est « l'héritier du complexe parental ».

La modularité monte de 0,37-0,38 à **0,51** entre les deux moitiés : la pensée tardive est plus
compartimentée. **Réserve de composition** : la moitié tardive est faite d'essais courts et
spécialisés (11 œuvres, 5 124 atomes) là où la précoce contient trois monuments généralistes —
une part de la compartimentation vient du format des œuvres, pas seulement de la pensée. Les
trois migrations ci-dessus, elles, ne dépendent pas de ce biais : chacune est un déplacement de
concepts PRÉSENTS des deux côtés.

---

## 4. Ce que Freud dit de lui-même

Un lexique déterministe peut **repérer** un passage où un auteur se corrige, s'objecte ou se cite ;
il ne peut pas **établir** qu'il le fait. Les 234 candidats du corpus ont donc été lus en contexte
et jugés un par un — les 183 d'origine, puis les 9 apportés par les huit œuvres ajoutées, puis
**22 devenus visibles quand la normalisation des blancs a réparé les marqueurs coupés par un
retour à la ligne** (le registre compte 225 verdicts : il est cumulatif et garde ceux dont le
marqueur a depuis été retiré du lexique).

| Signal | Repérés | Confirmés | Précision |
|---|---:|---:|---:|
| Objection contre sa propre thèse | 119 | 69 | 0,58 |
| Renvoi à son propre travail | 90 | 39 | 0,44 |
| Révision de soi | 25 | 7 | 0,28 |

**115 passages opposables.** Les 22 candidats cachés par les retours à la ligne contenaient
**deux révisions doctrinales majeures** qui dormaient là depuis le début du projet :

> « *…wonach also die frühere Behauptung zu korrigieren ist, daß der Traum das Nein nicht
> auszudrücken vermag.* »
> — *Die Traumdeutung*. Devant un contre-exemple (un rêve qui ne parvient pas à se former),
> Freud **corrige sa thèse** que le rêve ne sait pas dire non : l'échec du rêve EST un « non ».

> « *Ich möchte darum die obige Behauptung einschränken und korrigieren: an der Leiche des
> erschlagenen Feindes wird der Urmensch triumphiert haben…* »
> — *Zeitgemäßes über Krieg und Tod*. Il **restreint explicitement** son affirmation : l'homme
> primitif ne méditait pas la mort devant le cadavre de l'ennemi — seulement devant ses proches.

Quelques autres méritent d'être lus :

> « *Ich hatte damals die (später als unrichtig erkannte) Meinung, daß meine Aufgabe sich darin
> erschöpfe, den Kranken den verborgenen Sinn ihrer Symptome mitzuteilen…* »
> — *Die Traumdeutung*. Freud déclare qu'une position sienne fut **ensuite reconnue fausse** : il
> croyait qu'il suffisait de communiquer au malade le sens caché de ses symptômes.

> « *…wenn es doch nicht an allen Stellen gelungen ist, den früheren Text auf das Niveau unserer
> heutigen Einsichten zu heben…* »
> — Préface à la 3ᵉ édition. **Freud confirme lui-même** que les couches d'écriture coexistent dans
> le texte que nous lisons : c'est exactement la limite de datation posée au §5.

> « *Es gibt nun einen Einwand, welcher die letzten Schlußfolgerungen umzustoßen droht.* »
> — Il annonce une objection qui menace ses propres conclusions, avant de l'exposer et d'y répondre.

> « *Ich habe einmal behauptet, daß solche Kindheitsszenen »Denkerinnerungen« sind, die zu einer
> späteren Zeit herausgesucht, zusammengestellt, und dabei nicht selten verfälscht werden.* »
> — *Traum und Telepathie* (1922). Renvoi explicite à sa propre théorie des **souvenirs-écrans**
> (« *Über Deckerinnerungen* », 1899) — une œuvre que le corpus ne contient pas encore, mais dont
> la trace reste lisible dans celle-ci.

**Ce que les rejets apprennent.** Les 119 candidats écartés disent ce qu'un lexique ne peut pas
voir : objections appartenant à un **personnage de roman** (Hanold chez Jensen) ou à une **histoire
drôle** ; objections que Freud adresse **à d'autres** (Frazer, Trotter, Scherner) et non à lui-même ;
renvois **prospectifs** (« cela sera traité ailleurs ») pris pour des auto-citations ; de purs
homonymes — *einwandfrei* (irréprochable) n'a rien d'une objection, *einwandern* veut dire
immigrer ; et jusqu'au marqueur pris **au sens propre** : « *ein Verzicht an anderer Stelle* »
désigne un renoncement ailleurs dans l'économie psychique, pas un renvoi bibliographique.

---

## 5. Ce que ce document ne dit pas

Cinq limites, toutes mesurées, aucune supposée.

**La datation reste une fourchette pour une seule œuvre.** Sept œuvres sont lues dans leur édition
d'origine (ou une réimpression déclarée inchangée) ; quatre ont été collationnées phrase par
phrase. Ne demeure incertain que *Jenseits des Lustprinzips* — dont l'océrisation du fac-similé
s'est révélée trop dégradée pour distinguer « absent » de « présent mais illisible ». **La méthode
refuse alors de conclure** plutôt que de produire une date fausse ; l'écart n'y est que d'un an.

*Recherche d'un meilleur témoin, faite et documentée plutôt que supposée* : archive.org ne
recense qu'un seul scan de la 1ʳᵉ édition (1920) — celui déjà utilisé. Un autre exemplaire
(« jenseitsdeslust00freugoog », scan Google/Michigan) a d'abord semblé prometteur — sa
couverture y grimpe à 0,82 contre 0,49 — mais son texte s'est révélé être la **2ᵉ édition
(1921)**, la même que celle déjà lue dans le corpus : l'adopter aurait comparé le texte à
lui-même et daté faussement « 1920 » ce qui n'est qu'un doublon de 1921. Tous les autres
exemplaires trouvés sont soit des éditions encore plus tardives (3ᵉ éd. 1923, *Gesammelte
Werke* 1925/1940), soit des traductions (hongrois, néerlandais, grec, japonais) — aucun n'est
un second témoin recevable de 1920. Le fac-similé actuel ne dispose pas non plus d'une couche
ABBYY à confiance par mot qui permettrait de filtrer les passages douteux. La réserve tient
donc jusqu'à ce qu'un meilleur exemplaire physique soit numérisé.

**Un volume n'est pas d'un seul auteur.** La 4ᵉ édition de la *Traumdeutung* contient un appendice
d'**Otto Rank** — 334 atomes. Chaque atome porte son auteur réel ; sans cela, une mesure d'auteur
mélangerait deux plumes.

**Une co-occurrence n'est pas une thèse.** Que deux concepts voisinent souvent indique où regarder,
pas ce que Freud en dit. La lecture reste nécessaire.

**Une chronologie de densité n'est pas une histoire des idées.** Elle mesure la place d'un mot,
pas l'évolution d'une pensée. Un concept peut être présent sans être nommé.

**Treize œuvres majeures manquent — recherche faite, pas supposée.** Huit œuvres ont rejoint le
corpus (1908-1922, dont *Eine Kindheitserinnerung des Leonardo da Vinci*), toutes issues du vrai
`gutenberg.org` (allemand, relu par Distributed Proofreaders — même exigence que le reste).
Treize autres restent hors d'atteinte en qualité citable, vérifié par recherche systématique
plutôt que supposé : ni `gutenberg.org` (dont le catalogue complet a été passé en revue — seules
des traductions anglaises y figurent pour ces titres), ni Wikisource DE (dont l'API de recherche
ne renvoie aucune page hébergée pour aucun des treize, seulement des entrées bibliographiques
pointant vers des scans bruts d'archive.org) ne les proposent transcrits. Sept œuvres
théoriques majeures — *Vorlesungen zur Einführung* (1917), *Das Ich und das Es* (1923),
*Hemmung, Symptom und Angst* (1926), *Zur Geschichte der psychoanalytischen Bewegung* (1914),
*Die Zukunft einer Illusion* (1927), *Das Unbehagen in der Kultur* (1930), *Der Mann Moses*
(1939), *Abriss der Psychoanalyse* (1940) — et cinq grands cas cliniques (Dora, le petit Hans,
l'Homme aux rats, Schreber, l'Homme aux loups). L'absence des deux premières pèse directement
sur la chronologie de la seconde topique (§3). *Der Mann Moses* et *Abriss* ont une raison
supplémentaire : publiés en 1939/1940, ils ne sont pas encore libres de droits aux États-Unis
(règle de 95 ans après publication), où `gutenberg.org` est hébergé — seul Wikisource DE
pourrait les proposer légalement, s'il les transcrivait un jour.

---

*Reproduire ces mesures :* `python bin/analyser.py` (état des lieux) ·
`python bin/analyser.py trieb` (dossier d'un concept) · `python bin/analyser.py --agent signaux`
