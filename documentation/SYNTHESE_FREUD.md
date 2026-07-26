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

**Deux œuvres majeures manquent.** *Das Ich und das Es* (1923) et *Hemmung, Symptom und Angst*
(1926) ne sont disponibles dans aucune source libre de qualité citable. Leur absence pèse
directement sur la chronologie de la seconde topique (§3).

---

*Reproduire ces mesures :* `python bin/analyser.py` (état des lieux) ·
`python bin/analyser.py trieb` (dossier d'un concept) · `python bin/analyser.py --agent signaux`
