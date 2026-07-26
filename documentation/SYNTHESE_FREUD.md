# Ce que le corpus dit de Freud

> **Ce document n'est pas une interprétation.** Tout ce qui suit est produit par des agents
> déterministes — aucun modèle de langage n'intervient dans les mesures. On peut refaire chaque
> calcul (`python bin/analyser.py`) et remonter de n'importe quel chiffre jusqu'à la phrase
> allemande qui le fonde. Là où une lecture humaine a été nécessaire, elle est signalée comme telle.
>
> Corpus : **12 œuvres, 1900-1933, 16 898 atomes** (une phrase = un atome).

---

## 1. Chaque livre reconnu par sa marque propre

L'agent `profil` compare chaque œuvre au reste du corpus et retient ce qui y est **sur-représenté**
— non pas ce qui domine, mais ce qui distingue. Il ne sait rien du contenu des livres : il ne voit
que des atomes catégorisés.

| Œuvre | Atomes | Ce qui la distingue |
|---|---:|---|
| *Die Traumdeutung* (1900) | 5 996 | **rêve**, désir |
| *Neue Folge der Vorlesungen* (1933) | 2 119 | **topique**, famille, cure |
| *Der Witz…* (1905) | 2 076 | **comique**, économie |
| *Totem und Tabu* (1913) | 1 588 | **anthropologie**, famille |
| *Zur Psychopathologie…* (1901) | 1 051 | **mémoire**, actes manqués |
| *Drei Abhandlungen…* (1905) | 843 | **pulsion**, développement |
| *Gradiva* (1907) | 756 | rêve, **esthétique**, conflit |
| *Massenpsychologie…* (1921) | 699 | **social**, famille |
| *Jenseits des Lustprinzips* (1920) | 545 | **pulsion**, topique, économie |
| *Über Psychoanalyse* (1910) | 467 | **conflit**, cure |
| *Das Unheimliche* (1919) | 421 | **esthétique** |
| *Eine Teufelsneurose…* (1923) | 337 | **famille**, conflit |

**Douze sur douze.** Ce n'est pas un résultat sur Freud — c'est un contrôle de validité : une
ontologie qui se tromperait de catégories ne retrouverait pas ces identités.

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

---

## 3. La chronologie des concepts

L'agent `chronologie` mesure la densité d'un concept par œuvre (en ‰ des atomes). Il **ne date
jamais un énoncé** : il compare des volumes, en rappelant que cinq d'entre eux sont lus dans une
édition postérieure dont les couches d'ajout sont indiscernables (voir §5).

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

| Instance | Avant 1920 | 1920-21 | 1933 |
|---|---:|---:|---:|
| *Ich* (le Moi) | 2-17 ‰ | 28-49 ‰ | 35 ‰ |
| *Es* (le Ça) | < 1 ‰ | ~4 ‰ | **23 ‰** |
| *Über-Ich* (le Surmoi) | **absent** | **absent** | **29 ‰** |

Le Ça et le Surmoi n'existent pas dans le vocabulaire de Freud avant les années 1920 — le corpus
le retrouve seul. Le pic du Moi en 1921 tombe sur un livre intitulé *Massenpsychologie und
**Ich-Analyse***.

> **Réserve.** *Das Ich und das Es* (1923), où ces instances sont introduites, **ne figure pas au
> corpus** : aucune source libre n'en propose une transcription de qualité citable — Wikisource ne
> l'a pas transcrit, et l'édition disponible ailleurs est celle de S. Fischer 1975, dont l'appareil
> éditorial est protégé. Même constat pour *Hemmung, Symptom und Angst* (1926). La marche entre
> 1921 et 1933 est donc plus abrupte ici qu'elle ne le fut dans l'œuvre.

---

## 4. Ce que Freud dit de lui-même

Un lexique déterministe peut **repérer** un passage où un auteur se corrige, s'objecte ou se cite ;
il ne peut pas **établir** qu'il le fait. Les 183 candidats du corpus ont donc été lus en contexte
et jugés un par un.

| Signal | Repérés | Confirmés | Précision |
|---|---:|---:|---:|
| Objection contre sa propre thèse | 108 | 61 | 0,56 |
| Renvoi à son propre travail | 59 | 31 | 0,53 |
| Révision de soi | 16 | 5 | 0,31 |

**97 passages opposables.** Quelques-uns méritent d'être lus :

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

**Ce que les rejets apprennent.** Les 86 candidats écartés disent ce qu'un lexique ne peut pas
voir : objections appartenant à un **personnage de roman** (Hanold chez Jensen) ou à une **histoire
drôle** ; objections que Freud adresse **à d'autres** (Frazer, Trotter, Scherner) et non à lui-même ;
renvois **prospectifs** (« cela sera traité ailleurs ») pris pour des auto-citations ; et de purs
homonymes — *einwandfrei* (irréprochable) n'a rien d'une objection, *einwandern* veut dire immigrer.

---

## 5. Ce que ce document ne dit pas

Cinq limites, toutes mesurées, aucune supposée.

**La datation est une fourchette pour cinq œuvres sur douze.** Freud a cessé de signaler ses ajouts
dès la 3ᵉ édition : les couches d'écriture sont indiscernables. Un atome est « attesté au plus tard »
dans l'édition lue. Sept œuvres échappent à cette réserve (éditions d'origine, ou réimpression
déclarée inchangée pour *Totem und Tabu*).

**Un volume n'est pas d'un seul auteur.** La 4ᵉ édition de la *Traumdeutung* contient un appendice
d'**Otto Rank** — 334 atomes. Chaque atome porte son auteur réel ; sans cela, une mesure d'auteur
mélangerait deux plumes.

**Une co-occurrence n'est pas une thèse.** Que deux concepts voisinent souvent indique où regarder,
pas ce que Freud en dit. La lecture reste nécessaire.

**Une chronologie de densité n'est pas une histoire des idées.** Elle mesure la place d'un mot,
pas l'évolution d'une pensée. Un concept peut être présent sans être nommé.

**Deux œuvres majeures manquent.** *Das Ich und das Es* (1923) et *Hemmung, Symptom und Angst*
(1926) ne sont disponibles dans aucune source libre de qualité citable. Leur absence pèse
directement sur la chronologie de la seconde topique (§3).

---

*Reproduire ces mesures :* `python bin/analyser.py` (état des lieux) ·
`python bin/analyser.py trieb` (dossier d'un concept) · `python bin/analyser.py --agent signaux`
