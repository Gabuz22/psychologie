# Comparer des auteurs sans les confondre

Chaque auteur du corpus est décrit avec **ses propres catégories** (`core/lexiques/`). C'est une
règle d'architecture, pas une commodité : rien, dans les données, ne dit spontanément que la
`Verdrängung` de Rank et celle de Freud sont la même chose — ni qu'elles ne le sont pas. Un
lexique commun trancherait cette question par décret, avant toute mesure.

Le prix à payer est qu'aucune comparaison n'est donnée d'avance. Ce document décrit comment le
corpus en produit quand même, et à quelles conditions.

---

## 1. Ce que la couche établit, et ce qu'elle refuse d'établir

Quatre mesures, retenues parce que chacune se vérifie à l'œil sur le texte.

| Mesure | Ce qu'elle prouve | Ce qu'elle ne prouve pas |
|---|---|---|
| **Reprise textuelle** | deux passages partagent des suites de six mots | qu'ils partagent une thèse |
| **Mention nominale** | un auteur écrit le nom d'un autre | qu'il le suit, l'approuve ou le conteste |
| **Lecture déclarée** | un chapitre annonce dans son *titre* qu'il traite d'un autre auteur | ce qu'il en dit |
| **Usage d'un mot** | un motif se distribue ainsi entre les corpus | que les auteurs veulent dire la même chose |

Aucune colonne de la base ne nomme la **nature** d'un rapport. Vous ne trouverez ni « socle », ni
« emprunt », ni « contradiction » : ces mots désignent une intention que la mesure ne voit pas.

Le corpus a déjà éprouvé ce piège. Un marqueur avait été construit pour repérer les écarts d'un
disciple avec Freud ; lecture faite, il donnait **0 confirmé sur 5** — les cinq passages étaient
des renvois d'accord. Le marqueur a été requalifié en « renvoi explicite à Freud », qui est ce
qu'il prouve réellement.

---

## 2. Le problème de la comparaison de concepts, et sa solution

Comparer la densité du concept « Œdipe » de Rank à celui de Freud est suspect : les deux motifs
viennent de lexiques **différents**, écrits séparément. L'écart pourrait donc venir des
lexicographes plutôt que des auteurs. Aucun témoin ne permet de trancher — le seul disponible
(« un concept comparé à lui-même, coupé en deux moitiés ») mesure la stabilité d'un échantillon,
pas la correspondance entre deux auteurs.

**La sortie est de changer de question.** On ne demande plus « ces deux concepts sont-ils
équivalents ? » (indécidable) mais « comment ce mot exact se distribue-t-il ? » (mesurable). Un
seul motif, appliqué à tous les corpus de sa langue, et on compte.

Le test décisif porte sur un cas où les deux mesures existent :

| | motif propre à chacun | motif **unique** |
|---|---|---|
| Sigmund Freud | 3,6 ‰ | 3,2 ‰ |
| Otto Rank | 20,6 ‰ | 21,6 ‰ |

**L'écart persiste** quand le lexicographe disparaît. Il vient donc des auteurs. C'est ce qui rend
la comparaison de vocabulaire défendable — et c'est protégé par un test
(`test_l_ecart_mesure_ne_vient_pas_du_lexicographe`) dont la chute signifierait que la comparaison
redevient indéfendable.

Deux réserves qui ne s'effacent jamais :

- La colonne **`lexique`** dit qui a défini le motif. La ligne de cet auteur est haute par
  construction — le motif a été écrit pour lui. Ce sont les **autres** lignes qui informent.
- La langue du motif est **déclarée**, jamais devinée. Un motif allemand ne dit rien d'un texte
  français : la case est vide, et « non mesurable » n'est pas « zéro ».

---

## 3. Ce que la lecture ajoute au calcul

> **Les chiffres de cette section décrivent la campagne de juillet, sur un corpus à cinq auteurs
> (132 liens).** L'entrée de Stekel et des onze œuvres de Freud a porté le corpus à **511 liens /
> 358 événements**, et une seconde campagne a eu lieu le 2026-07-31 : voir **§ 6**. Les
> enseignements de méthode ci-dessous restent valables ; les comptes, non.

132 liens de reprise sont calculés. 63 tombaient entre 0,30 et 0,70 de contenance — assez pour
être publiés, pas assez pour être évidents. **38 ont été relus en contexte**, chacun avec les
atomes qui l'entourent des deux côtés.

Le détecteur s'arrête à la phrase. Le lecteur remonte de quelques atomes et trouve l'attribution
que la phrase seule ne porte pas : *« Ich zitiere wörtlich (Drei Abhandlungen zur Sexualtheorie,
Seite 37) »*, un guillemet ouvrant, un appel de note.

| Verdict | Nombre |
|---|---|
| confirmé | 31 |
| reclassé (les deux citent un **tiers**) | 5 |
| rejeté | 1 |
| non lu (échec réseau, à reprendre) | 25 |

*(Un trente-huitième verdict a été rendu puis **désancré** : le retrait des têtes courantes —
voir le README — a renuméroté les atomes de « Traum und Mythus », et le couple exact qu'il
jugeait n'existe plus tel quel. Il est conservé dans le registre sous `desancres`, avec son
motif, plutôt que supprimé : un travail de lecture effacé en silence se refait.)*

### Le résultat qui valide la règle de datation

Le calcul oriente un lien uniquement quand les fenêtres de datation des deux passages sont
disjointes ; sinon il répond **INDÉCIDABLE**, et ce refus est une information sur ce que le corpus
permet, pas un trou à combler.

Confrontation des deux sources sur les 32 liens orientés par la lecture :

| calculé | lu | nombre |
|---|---|---|
| `a_vers_b` | `a_vers_b` | 3 |
| `b_vers_a` | `b_vers_a` | 26 |
| INDÉCIDABLE | tranché par le texte | 3 |

**Vingt-neuf accords, zéro contradiction.** La règle par les dates ne s'est jamais trompée sur ce
qu'elle a osé affirmer, et son silence a été levé trois fois par la lecture. Les deux colonnes
sont conservées séparément (`sens` et `sens_lu`) pour que l'écart reste visible.

### Le cas que seul un lecteur pouvait voir

Cinq liens ont été **reclassés** : aucun des deux auteurs ne lit l'autre, tous deux copient la
même page d'un tiers. Quatre fois, ce tiers est *Die Traumdeutung* — Abraham l'annonce (*« Ich
zitiere den folgenden Passus wörtlich nach Freud »*, note « Traumdeutung, Seite 180 f. ») et Rank
aussi (*« heißt es in der Traumdeutung weiter »*, référence « l. c., S. 182 »). Le calcul voyait
deux auteurs qui se ressemblent ; ils ne se devaient rien.

Le cinquième cas est plus retors : les deux passages appartiennent au **même volume**, les
*Studien über Hysterie*, dont la « Vorläufige Mitteilung » de 1893 est réimprimée en tête. Le
corpus se rapprochait de lui-même.

Le lien **rejeté** l'a été parce que les quatre suites partagées étaient les mots d'un **titre
d'article**, et que l'un des deux atomes n'était pas une phrase mais un fragment d'apparat agrégé
par l'OCR.

---

## 4. Trois oppositions connues, passées à la mesure

On ne cherche pas ici à prouver une opposition. On regarde ce que le texte montre — et on note
aussi ce qu'il ne montre pas, car un désaccord d'idées ne laisse pas forcément de trace lexicale.

### 4.1 La rupture d'Otto Rank (1924)

*Das Trauma der Geburt* est le livre qui lui coûtera sa place. Sa thèse : l'angoisse vient de la
naissance, non du père.

Le vocabulaire de cette thèse est **strictement localisé** :

| œuvre de Rank | année | `geburtstrauma` | `mutterleib` |
|---|---|---|---|
| Der Künstler | 1907 | 0,0 ‰ | 0,0 ‰ |
| Der Mythus von der Geburt des Helden | 1909 | 0,0 ‰ | 3,0 ‰ |
| Die Lohengrinsage | 1911 | 0,0 ‰ | 14,1 ‰ |
| Das Inzest-Motiv | 1912 | 0,0 ‰ | 0,7 ‰ |
| **Das Trauma der Geburt** | **1924** | **121,6 ‰** | **70,3 ‰** |
| Genetische Psychologie II | 1928 | 0,0 ‰ | 0,0 ‰ |

Chez Freud, `geburtstrauma` porte **un** atome sur 20 617. Chez Abraham, aucun.

**Mais le résultat qu'on n'attendait pas** est ailleurs. Si Rank avait remplacé l'Œdipe par la
naissance, l'Œdipe devrait s'effacer de ce livre. Il n'en est rien : `odipus` y pèse **19,1 ‰**,
contre 21,6 ‰ sur l'ensemble de son œuvre — l'écart est dans le bruit. Le texte de 1924 ne montre
pas un abandon, il montre une **addition**.

Ce que la mesure établit : un vocabulaire neuf, concentré sur un seul livre, qui n'existe chez
aucun autre auteur du corpus. Ce qu'elle n'établit pas : que Rank contredit Freud. Pour cela il
faut lire les 159 passages — la base les rend.

### 4.2 Freud contre Le Bon

La seule controverse du corpus qui traverse deux langues, et la mieux documentée : un chapitre
entier de *Massenpsychologie und Ich-Analyse* (1921) s'intitule « II. Le Bon's Schilderung der
Massenseele ». C'est une **lecture déclarée** — le lien le plus fort du corpus, et le seul qu'une
reprise de mots ne pourrait pas trouver, Freud lisant Le Bon en traduction.

Le désaccord a une forme lexicale, et elle est nette. « Suggestion » existe dans les deux langues,
donc se compare à travers elles :

| | `suggestion` | `libido` |
|---|---|---|
| Gustave Le Bon | **38,4 ‰** | **0,0 ‰** |
| Josef Breuer | 18,1 ‰ | 0,0 ‰ |
| Sándor Ferenczi | 13,0 ‰ | 27,6 ‰ |
| Sigmund Freud | 3,9 ‰ | 9,1 ‰ |
| Karl Abraham | 0,8 ‰ | 36,5 ‰ |
| Otto Rank | 0,1 ‰ | 8,4 ‰ |

Le mot qui porte toute l'explication chez l'un est absent chez l'autre, et réciproquement. C'est
exactement ce que Freud annonce faire — remplacer la suggestion par la libido. Ici, la mesure
**concorde** avec ce que l'auteur déclare de son propre geste, ce qui est le meilleur usage
qu'on puisse en faire : elle ne découvre pas la controverse, elle la rend visible et vérifiable.

Le 18,1 ‰ de Breuer n'était pas cherché. Il date l'autre côté de la même histoire : en 1895, la
suggestion est encore le vocabulaire de la cure.

### 4.3 Le contre-cas : Abraham, qui ne rompt pas

Abraham est le contraire exact de Rank — il approfondit là où l'autre s'écarte, et meurt sans
avoir rompu. La mesure le montre par un chiffre inattendu : `libido` pèse **36,5 ‰** chez lui
contre **9,1 ‰** chez Freud. Le disciple emploie le terme central du maître **quatre fois plus
souvent que le maître**. Ferenczi, qui ne rompt pas non plus, est à 27,6 ‰ — même position.

Un usage de mot ne mesure ni une allégeance ni une orthodoxie. Mais il indique où regarder, et
c'est tout ce qu'on lui demande.

### 4.4 Deux hommes, deux livres, une même année

Ferenczi entre dans le corpus en juillet 2026, et la première chose que la mesure signale n'était
pas cherchée. Son *Versuch einer Genitaltheorie* et le *Trauma der Geburt* de Rank paraissent la
**même année, 1924**, et ils partagent leur vocabulaire central :

| | `mutterleib` (ventre maternel) |
|---|---|
| Sándor Ferenczi | **11,0 ‰** |
| Otto Rank | 8,4 ‰ |
| Karl Abraham | 0,8 ‰ |
| Sigmund Freud | 0,7 ‰ |

Chez Rank, la densité est concentrée sur un seul livre (70,5 ‰ dans le *Trauma*, 0 à 14 ‰
ailleurs). Chez Ferenczi, elle est portée par la *Genitaltheorie*, où le retour au ventre
maternel n'est pas l'origine de l'angoisse mais celle du **coït**. Deux thèses différentes, un
lexique commun, la même année, et les deux hommes se brouilleront avec Freud dans la décennie.

La mesure établit le partage de vocabulaire. Elle n'établit ni influence, ni convergence, ni
rivalité — la couche de reprise textuelle ne trouve d'ailleurs que **deux** passages partagés
entre eux. Ce qu'elle fait, c'est désigner un endroit où il faut aller lire.

Le reste de sa signature n'a d'équivalent chez personne : `amphimixis`, mot qu'il forge, compte
41 occurrences chez lui contre 3 dans les 785 000 mots des autres corpus allemands ; `homoerotik`
77 contre 3 ; `thalass` 12 contre 1. Et un chiffre qui dit sa place : `gegenübertragung`, 15
occurrences chez lui, **une** dans tout le reste du corpus.

---

---

## 5. Ce qui reste ouvert

- **147 événements de reprise sur 358 n'ont pas été lus.** Ils gardent `a_verifier = 1` : non lus,
  pas rejetés. (Le chiffre annoncé ici auparavant — « 25 sur 63 » — datait d'un corpus à cinq
  auteurs ; l'entrée de Stekel et les onze œuvres de Freud l'ont porté à 358 événements.)

  **211 ont été lus le 2026-07-31** : voir § 6.
- Les empreintes de contenu résistent aux **déplacements** d'atomes, pas aux changements de
  **segmentation**. Une resegmentation désancre les verdicts ; un test
  (`test_les_verdicts_lus_portent_bien_sur_des_couples_du_corpus`) le signale au lieu de laisser
  la perte passer inaperçue.
- **Un résultat négatif qu'il faut garder.** Ferenczi est l'auteur qui a le plus visiblement
  changé d'avis : il invente la technique active (1919-1926) puis lui substitue son contraire
  (1927-1933). Les 74 signaux relus à son arrivée ont pourtant donné **deux** révisions de soi
  confirmées, toutes deux ayant survécu à un contrôle adversarial. Vingt-neuf candidats ont été
  **reclassés** — le plus souvent en objections d'un tiers rapportées, ou en corrections
  attribuées à un autre (Jung, un patient, la science en général) — et vingt et un rejetés.
  Autrement dit : un renversement doctrinal aussi net que celui-là ne laisse presque **aucune
  trace lexicale de première personne**. Un auteur qui change d'avis ne l'écrit pas ; il écrit
  autre chose. C'est une limite du repérage par marqueur, mesurée plutôt que supposée.
- Le rapprochement de concepts **par similarité de voisinage** a été construit, mesuré, puis
  écarté — voir [APPARIEMENT_ECARTE.md](APPARIEMENT_ECARTE.md), et les quatre conditions qu'il
  faudrait remplir pour rouvrir le chantier.

  **Cette ligne a porté une affirmation fausse pendant deux jours**, et le cas mérite d'être gardé
  parce qu'il a réellement trompé un lecteur. Elle disait : « n'est toujours pas fondable : aucun
  témoin positif valide n'existe dans la base ». C'était vrai le 28 juillet ; le verrou a été levé
  le lendemain — la couche « usage des mots » donne un témoin inter-auteurs qui fonctionne
  (AUC 0,893). Le commit qui l'a levé a écrit `APPARIEMENT_ECARTE.md` et l'en-tête de
  `core/comparaison.py`, tous deux exacts, **sans toucher à cette phrase-ci**. Un document tenu à
  la main ne se met pas à jour parce qu'un autre document le contredit : la règle déjà écrite pour
  `COURANTS_FREUD.md` (un texte qui décrit des données calculées doit être généré) vaut aussi pour
  une section « ce qui reste ouvert », qui est la première chose que lit celui qui reprend.

---

## 6. La lecture des reprises — 2026-07-31

**150 événements lus, 129 confirmés, 21 reclassés, 0 rejeté.** Avec les 61 déjà lus, le registre
compte **211 événements instruits sur 358**.

### Zéro rejet, et ce n'est pas de l'indulgence

Les lots sont triés par **contenance décroissante** : ces 150 événements sont les plus fortes
reprises du corpus, et presque toutes sont des citations littérales *signées* — guillemet ouvert
dans l'atome amont, pagination dans l'aval (« (Traumdeutung S. 179.) », « (Freud: Kl. Schr., II,
S. 173) », « (a. a. O. S. 84) »). Les rejeter pour atteindre un quota aurait été l'erreur
symétrique de celle que ce registre combat. **Les faux positifs, s'il y en a, sont dans les bandes
basses — non lues.** C'est pourquoi le taux de rejet de cette campagne ne doit pas être extrapolé.

### Une dizaine de sens publiés à l'envers, tous par le même artefact

L'essai de Freud *Über einen besonderen Typus der Objektwahl beim Manne* paraît au *Jahrbuch* II en
**1910**, mais il est lu dans la *Sammlung kleiner Schriften, Vierte Folge* de **1918** : sa fenêtre
de datation est donc [1913, 1918], et le calcul en déduisait que Rank (*Lohengrinsage*, 1911) était
**la source de Freud**. Rank écrit lui-même, en note de bas de page, ce que le calcul ne pouvait pas
voir :

> « Die folgenden Ausführungen sind fast wörtlich der grundlegenden Arbeit Freuds
> (Jb., II, S. 394 ff.) entnommen. »

et référence ailleurs « (Freud, Jb., II, S. 392, 4) ». C'est le même piège que les seize emprunts
retournés de juillet, sous une autre forme : là c'était un identifiant positionnel qui dérivait,
ici c'est une **date d'édition qui n'est pas une date d'écriture**. La parade est la même — la
lecture prime sur le calcul, et l'ancrage se fait sur l'empreinte du texte.

### 21 reclassements : des tiers que le corpus ne contient pas

| tiers | événements | ce qui le prouve |
|---|---|---|
| **Peter Rosegger**, *Waldheimat* | 5 | le récit du *Schneidergeselle*, que Freud et Stekel impriment tous deux ; la *Traumdeutung* crédite Frau Dr. M. Hilferding de l'avoir apporté à la discussion |
| **Gottfried Keller**, *Traumbuch* | 2 | Rank et Stekel transcrivent le même rêve de serpent la même année 1912 ; variantes « Taburett »/« Tabouret », « Wir lachten auf »/« Wir lachten auch » — deux dépouillements indépendants |
| **Friedrich Hebbel**, *Tagebücher* | 2 | Rank date l'entrée de 1834, Stekel de 1837 |
| **Rudolf Kleinpaul** | 2 | Rank et Stekel, tous deux en 1911, donnent des pages différentes (112 f. / 113) |
| **Ernest Jones** | 1 | « entnehme ich … einer Arbeit von E. Jones » / « das Jones (S. 296 f.) … mitteilt » |
| Lichtenberg, Goethe, Popper-Lynkeus, Abraham, Rank lui-même | 9 | attributions nominales explicites |

Sans la lecture, chacun de ces liens aurait été publié comme un emprunt **entre deux auteurs du
corpus**. C'est précisément ce que la contrainte fondatrice interdit : un lien qui ne se déroule pas
jusqu'à deux passages lus côte à côte n'existe pas.

### Deux preuves d'antériorité qui ne doivent rien aux dates

Le cas le plus solide de la campagne ne s'appuie sur aucune datation. Stekel (1917) cite les *Drei
Abhandlungen* avec des **leçons d'édition antérieures** à celle que le corpus lit (4ᵉ éd., 1920) :
« scheint **mit dem Einsetzen der Latenzperiode** zu schwinden » là où l'édition lue porte « scheint
nach kurzer Zeit zu schwinden ». La variante prouve qu'il copie une impression plus ancienne —
l'apparente antériorité de Stekel sur « son » Freud est un pur artefact d'édition.
