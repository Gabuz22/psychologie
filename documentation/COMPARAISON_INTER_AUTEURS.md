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

## 4. Cinq oppositions connues, passées à la mesure

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

### 4.5 Stekel contre Ferenczi — trouvé par le croisement, pas par la lecture large

Les quatre cas ci-dessus avaient été repérés à la main, par lecture large du corpus, avant que
`core/divergences.py` (§ 7) ne systématise leur recette commune. Sur les 98 candidats que ce
croisement a produits, un seul a livré un **désaccord nommé et textuellement confirmé** — le
premier trouvé par ce mécanisme plutôt que par une lecture préalable.

Dans *Onanie und Homosexualität* (1917), Stekel conteste en son nom propre une thèse de Ferenczi
sur la nosologie de l'homosexualité masculine, en citant l'article visé :

> « Ich kann die Behauptung von Ferenczi ("Zur Nosologie der männlichen Homosexualität") … nicht
> bestätigen. » (« Je ne peux pas confirmer l'affirmation de Ferenczi… »)

La phrase renvoie à un cas précis (« der auf S. 283 berichtete Fall Nr. 62 ») : ce n'est pas une
réserve générale mais une objection clinique argumentée, sur un point de doctrine nommé. Le même
chapitre attribue par ailleurs à Freud, sans réserve, la thèse du refoulement homosexuel comme
origine de la paranoïa — Stekel ne conteste donc pas la psychanalyse en bloc, il conteste
Ferenczi précisément.

Une réserve, mesurée plutôt que passée sous silence : le dossier ne permet pas d'établir avec
certitude que cette dispute se trouve dans le même ouvrage que le pic lexical de 1917 qui a
signalé le candidat (l'attribution de Freud, elle, porte un repère de chapitre — « XIX. Hebbels
Träume » — qui la situe probablement ailleurs, dans un livre distinct sur l'interprétation des
rêves). Mais le sujet de la dispute (la nosologie de l'homosexualité masculine) colle exactement
à celui d'*Onanie und Homosexualität*, ce qui rend la co-localisation plausible sans être prouvée
par ce seul dossier.

Sur 98 candidats croisant un lien vérifié et une trajectoire réelle, **un seul** a donné cette
sorte de désaccord nommé — un taux de succès comparable à celui du seul autre témoin positif du
corpus sur ce genre de question (l'appariement de concepts, 1 confirmé sur 16). Ce n'est pas rien,
et ce n'est pas beaucoup : voir § 7 pour ce que les 84 autres candidats confirmés montrent à la
place.

---

---

## 5. Ce qui reste ouvert

- ~~Des événements de reprise n'ont pas été lus.~~ **INSTRUCTION COMPLÈTE le 2026-08-01 : les
  354 événements du corpus ont été lus en contexte.** Voir § 6. (Le chiffre annoncé ici auparavant
  — « 25 sur 63 » — datait d'un corpus à cinq auteurs ; l'entrée de Stekel et les onze œuvres de
  Freud l'avaient porté à 358, dont 4 ont disparu avec le catalogue d'éditeur retiré du corpus.)
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

## 6. La lecture des reprises — instruction complète, 2026-08-01

**Les 354 événements de reprise du corpus ont été lus en contexte : 232 confirmés, 56 reclassés,
9 rejetés.**

### Le taux de rejet n'est pas uniforme — et c'est le résultat le plus utile

Les lots sont triés par **contenance décroissante**, et lus dans cet ordre. Le résultat par bande :

| lots | contenance | confirmés | reclassés | **rejetés** |
|---|---|---|---|---|
| 1–5 (les plus fortes) | 1,00 → 0,60 | 129 | 21 | **0** |
| 6–9 | 0,60 → 0,45 | 87 | 32 | **1** |
| 10 (la queue) | 0,45 → 0,30 | 16 | 3 | **8** |

**Huit des neuf rejets tombent dans le dernier lot.** Les 250 premiers événements ne contiennent
aucun faux positif mécanique — non par indulgence, mais parce que ce sont des citations littérales
*signées* : guillemet ouvert dans l'atome amont, pagination dans l'aval (« (Traumdeutung S. 179.) »,
« (Freud: Kl. Schr., II, S. 173) »). **Un taux de rejet global ne veut donc rien dire ici ; il faut
le lire par bande**, et c'est un argument pour le seuil de publication de 0,30 plutôt que contre lui.

### La NATURE des liens change avec la contenance

C'est la découverte de structure de cette campagne, et elle n'était pas prévue. En haut de la
distribution, les liens sont des citations **internes** au corpus : un analyste en cite un autre.
En bas, **un tiers deviennent des citations d'un TIERS extérieur** — poètes, sources antiques,
psychologues d'avant la psychanalyse — que deux auteurs recopient sans se lire.

La liste des tiers s'est allongée de treize noms : **Grillparzer, Scherner** (parfois via Volkelt),
**Silberer, Karl Abel, Jean Paul, Lenau, Artemidoros von Daldis, Tolstoï, Stendhal, Paul Heyse**,
aux côtés de Rosegger, Gottfried Keller, Hebbel, Lichtenberg, Goethe, Jones, Kleinpaul et
Popper-Lynkeus. Sans lecture, chacun aurait été publié comme un emprunt **entre auteurs du corpus**.

La preuve est presque toujours une **divergence de leçon**, qui interdit la copie de l'un sur
l'autre : Freud lit « das Gefühl hatte » et « die Syrier » là où Stekel lit « das Gesicht hatte »
et « die Tyrier » (Artémidore) ; Rank a « diese Leidenschaft in vollem Maße », Stekel « diese
Leidenschaft **nicht** in vollem Maße » (Grillparzer).

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

### Un défaut du CORPUS, trouvé par la lecture et non par un contrôle

Quatre rejets du dernier lot avaient la même cause, et elle n'était pas dans la couche des
reprises : **les « atomes » appariés n'étaient pas du texte d'auteur mais le catalogue de
l'éditeur relié en fin de volume.** Le lecteur l'a reconnu à son contenu — des titres avec leurs
prix, une annonce d'abonnement à *Imago* (« M 15.— = K 18.— pro Jahrgang ») — et a noté qu'ils
« polluent probablement d'autres lots ». Vérifié : ils le faisaient.

*Das Ich und das Es* portait **115 atomes de catalogue sur 559, soit 21 % du volume** ; les
*Vorlesungen II*, 34. Ces deux œuvres étaient les seules, avec quelques autres, à ne déclarer
**aucune** borne dans `sources.PARATEXTE_FINAL` — et rien ne le signalait : la fonction répond
« pas de paratexte final déclaré » sans distinguer *ce volume n'en a pas* de *personne n'a
regardé*. Vingt-deux œuvres en déclarent une ; l'absence n'était pas une décision, c'était un trou.

Les bornes sont posées, 148 atomes de réclame quittent le corpus, et les deux volumes s'achèvent
maintenant sur leur vraie dernière phrase — pour *Das Ich und das Es*, « … doch dabei die Rolle
des Eros zu unterschätzen. »

Les quatre verdicts correspondants perdent leur ancre. Ils sont **conservés dans `desancres`**
avec leur motif, comme les six précédents : un travail de lecture effacé en silence se refait. Ici
la désancrage est même le bon résultat — *le lien n'existe plus parce qu'il n'aurait jamais dû
exister*.

### Deux preuves d'antériorité qui ne doivent rien aux dates

Le cas le plus solide de la campagne ne s'appuie sur aucune datation. Stekel (1917) cite les *Drei
Abhandlungen* avec des **leçons d'édition antérieures** à celle que le corpus lit (4ᵉ éd., 1920) :
« scheint **mit dem Einsetzen der Latenzperiode** zu schwinden » là où l'édition lue porte « scheint
nach kurzer Zeit zu schwinden » ; et « *Alle* meine Patientinnen » contre « *Viele* meiner ». La
variante prouve qu'il copie une impression plus ancienne — l'apparente antériorité de Stekel sur
« son » Freud est un pur artefact d'édition, et **Freud a atténué après coup**.

---

## 7. Chercher la divergence elle-même — un mécanisme de candidats, pas un quatrième détecteur

> **Les chiffres et lectures de cette section datent de la campagne du 2026-08-02, sur le corpus à
> sept auteurs germanophones.** Comme pour § 3, ce sont des comptes figés au moment de la lecture,
> pas une donnée maintenue : le compte de 98 candidats est rejouable (`python
> bin/generer_candidats_divergences.py`), mais le détail des deux lectures indépendantes par
> candidat ne l'est pas — il est conservé hors dépôt (voir plus bas).

Le § 5 gardait un résultat négatif : un renversement doctrinal aussi net que celui de Ferenczi « ne
laisse presque aucune trace lexicale de première personne ». Trois tentatives avaient déjà buté sur
la même question sous d'autres formes — un marqueur d'écart (0 confirmé sur 5), l'appariement de
concepts par voisinage (1 sur 16, [APPARIEMENT_ECARTE.md](APPARIEMENT_ECARTE.md)), une signature
lexicale inter-auteurs (0 sur 35 après contrôle du lexicographe). Toutes les trois demandaient à un
CALCUL de trancher la nature d'un rapport. `core/divergences.py` ne le demande plus : il croise deux
faits déjà mesurés séparément — un vocabulaire qui **apparaît** ou **disparaît** vraiment chez un
auteur (`core/branches.trajectoire`) et un lien **vérifié** (acte de citation confirmé, mention
confirmée) qui le rattache à un autre auteur sur ce même concept — et désigne seulement où lire,
comme un seuil de contenance désigne une reprise à vérifier sans en préjuger le verdict.

Sur le corpus complet, ce croisement produit **98 candidats** (55 apparitions, 43 disparitions,
répartis sur les cinq auteurs germanophones). Tous ont été lus, par un lecteur puis par un second
qui n'a vu que les mêmes pièces — jamais le jugement du premier avant d'avoir relu par lui-même :

| étape | nombre |
|---|---|
| candidats croisés | 98 |
| jugés « rien de spécifique au-delà du chiffre » dès la première lecture | 5 |
| jugés notables en première lecture | 93 |
| **infirmés** à la relecture indépendante (le lien vérifié ne porte pas sur ce concept, ou les passages sont un artefact — sommaire, récit sans travail conceptuel, thème attendu) | 8 |
| **confirmés** par les deux lectures | 85 |

Trois lectures se sont perdues en route (une panne d'agent a renvoyé un texte de test au lieu d'une
lecture) ; dans les trois cas le second lecteur l'a signalé explicitement et a fourni, lui, une
lecture réelle des mêmes pièces — conservée comme le jugement qui compte, y compris pour le candidat
`mutterleib` de Ferenczi cité plus bas (§ 4.4). Un travail de lecture ne se corrige pas en silence :
ceci est la même règle que les verdicts désancrés du § 6, ici appliquée à la campagne elle-même
plutôt qu'au corpus.

### Ce que les 85 candidats confirmés montrent, une fois lus

**Un seul des 85 montre un désaccord nommé et textuellement confirmé** — le cas Stekel contre
Ferenczi sur la nosologie de l'homosexualité masculine, ajouté au § 4 comme cinquième opposition
(§ 4.5), le premier trouvé par ce mécanisme plutôt que par une lecture large. Les **84 autres**
n'en montrent pas. Ce n'est pas un artefact de méthode : nombre d'entre eux sont des convergences
solidement établies, citation à l'appui — le croisement n'a donc rien d'un filtre qui n'aurait
laissé passer que du vide. Il désigne fidèlement des endroits où deux auteurs se lisent vraiment
sur un concept précis ; le plus souvent, la lecture aboutit à une adoption, une extension, ou
l'absence de rapport démontrable — mais pas toujours à une opposition, comme le § 4.5 le montre.
C'est un QUATRIÈME résultat, obtenu par une méthode entièrement différente des trois détecteurs
déjà écartés, qui converge largement avec eux tout en nuançant leur zéro absolu : sur ce corpus,
la divergence intellectuelle laisse une trace lexicale de ce genre **rarement** (1 candidat sur
98, un taux du même ordre que le seul autre témoin positif du corpus, l'appariement à 1 sur 16) —
mais pas jamais.

**Le patron le plus fréquent** est celui d'un lien réel qui ne porte pas sur le concept mesuré. Le
« tabu » de Freud (*Totem und Tabu*, 1913) en est l'exemple le plus net : le mot s'y concentre à
75,6 %, et trois liens vérifiés existent bien — vers Le Bon, Ferenczi, Abraham — mais aucun des
trois ne porte sur le tabou lui-même ; l'un renvoie à un autre essai du même livre, l'autre à un
travail de Ferenczi sur le sens de la réalité, le troisième se réduit à un renvoi bibliographique
vide. C'est un utile négatif de contrôle : le livre qui, cinq ans plus tard, donnera le cas le
mieux documenté du corpus (§ 4.2, Freud contre Le Bon) ne montre, sur son PROPRE concept-titre,
aucun dialogue vérifiable — la trace que laisse un vrai désaccord n'est visiblement pas la
concentration lexicale d'un terme, mais autre chose, comme le mot qui bascule d'une langue à
l'autre en § 4.2.

**Le second patron, presque aussi fréquent, est la convergence documentée** — et le plus riche
concentre, sans surprise, autour du § 4.3 déjà écrit (« Abraham, qui ne rompt pas »). Son
*Entwicklungsgeschichte der Libido* (1924) revient sur sept concepts de ce lot
(`introjektion`, `melancholie`, `trauer`, `entwicklungsstufe`, `ambivalenz`, `regression`,
`entwicklung`) et à chaque fois le texte, pas seulement le chiffre, crédite Freud nommément :
« Er tat den entscheidenden Schritt zur Aufdeckung des melancholischen Mechanismus » pour
l'introjection dans la mélancolie, un renvoi exprès à l'essai « Trauer und Melancholie », la
formule « vollauf bestätigt » (pleinement confirmé) pour dire ce que l'observation clinique
d'Abraham ajoute à la théorie freudienne — jamais une réserve. La même figure se répète sur
*Charakterbildung* (1921) : « Freuds erste Beschreibung des analen Charakters besagte… eine
Sparsamkeit », l'étude entière se présentant comme le prolongement d'un article de Freud de 1908
qu'elle nomme. Sept ans plus tôt, cinq ans plus tard — c'est la même posture, mesurée maintenant
avec des citations plutôt qu'avec la seule densité de `libido` qu'utilisait déjà le § 4.3.

**Rank, à l'inverse, éclaire son propre § 4.1 — mais un seul des candidats porte vraiment sur
*Das Trauma der Geburt*.** `libido` (en recul après 1924, 44 % des usages concentrés dans ce
livre) montre la « Libido » de Rank régresser jusqu'à un « stade intra-utérin » qui n'appartient
qu'à lui ; le seul rattachement explicite et assumé, sur ce candidat, va non pas vers Freud mais
vers Ferenczi — Rank rapproche sa propre « Urtendenz der Libido » de la « Regression zur
Protopsyche » que Ferenczi décrit dans *Hysterie und Pathoneurosen* (1919), « in einem ähnlichen
Sinne wie hier ». Ce que le § 4.1 avait déjà vu dans les chiffres — une **addition**, pas un
abandon de l'Œdipe — se confirme ici dans le texte même : sur ce mot précis, Rank construit sa
thèse de 1924 en dialogue ponctuel avec Ferenczi, sans jamais répondre à Freud.

Les deux autres candidats de Rank retenus sur ce lot (`traum`, `widerstand`) datent en réalité
d'AVANT 1924 et n'ont pas de rapport avec *Trauma der Geburt* — un rappel utile que la classe
« disparaît » d'une trajectoire désigne un recul après un pic, pas nécessairement un recul après
1924. `traum` culmine dans *Das Inzest-Motiv* (1912), sur un rapprochement poète/rêve/folie
(Dilthey, Heyse, Aristote) sans rapport avec les auteurs liés ; `widerstand` culmine dans *Der
Künstler* (1907), où les « Widerstände » externes et internes viennent de l'appareil pulsionnel
personnel de Rank, avec un seul écho explicite à la « psychische Zensur » freudienne — un
emprunt de vocabulaire assumé, pas une réponse. Les deux confirment, chacun à sa date, le même
diagnostic que `libido` : un vocabulaire d'abord personnel, jamais construit contre Freud.

**Un troisième candidat resserre le § 4.4** (« deux hommes, deux livres, une même année »). Chez
Ferenczi, `mutterleib` se concentre à 61–64 % dans sa *Genitaltheorie* (Thalassa, 1924) — et le
texte porte, en note, une citation explicite et non ambiguë : « Siehe Rank: Der Mythus von der
Geburt des Helden » (1909), insérée exactement dans le passage sur la symbolique du retour au
ventre maternel (eau, natation, vol). Le § 4.4 notait que la couche de reprise textuelle ne
trouvait que deux passages partagés entre les deux hommes ; celui-ci est un troisième point d'appui,
et il est nommé par Ferenczi lui-même, pas seulement mesuré.

### Douze autres lectures, en bref

| auteur | concept | œuvre dominante | ce que montre la lecture |
|---|---|---|---|
| Karl Abraham | `hysterie`, `neurose` | Klinische Beiträge (1907) | citation quasi verbatim de Freud, thèse reprise sans contestation |
| Karl Abraham | `charakter` | Charakterbildung (1921) | prolongement assumé de « Charakter und Analerotik » (Freud, 1908) |
| Karl Abraham | `alkohol` | Klinische Beiträge (1907) | pulsions partielles freudiennes appliquées à un objet clinique que Freud n'a pas traité |
| Sándor Ferenczi | `begattung` | Genitaltheorie (1924) | reprend le constat clinique d'Abraham (ejaculatio praecox) par analogie |
| Sándor Ferenczi | `erotismen` | Genitaltheorie (1924) | prolongement assumé des « Autoerotismen » freudiens des *Drei Abhandlungen* |
| Sándor Ferenczi | `regression` | Bausteine 3 | attribue à Freud, verbatim, le « caractère régressif des symptômes névrotiques » |
| Sándor Ferenczi | `materialisation` | Bausteine 3 | concept élaboré par Ferenczi seul, étendu du symptôme hystérique à l'expression affective normale |
| Otto Rank | `kastration` (×2) | Das Inzest-Motiv (1912) | chapitre de synthèse créditant nommément Freud, Ferenczi et Stekel — jamais une contestation |
| Otto Rank | `unterwelt` | Lohengrinsage (1911) | usage mythologique-comparatiste porté par le sujet du livre, pas un enjeu théorique autonome |
| Wilhelm Stekel | `bisexualitaet` | Onanie und Homosexualität (1917) | crédite Fliess, Hirschfeld, Krafft-Ebing — aucun des trois auteurs du corpus liés n'est en cause ici |
| Sigmund Freud | `deckerinnerung` | Zur Psychopathologie des Alltagslebens (1901) | histoire autonome du concept ; le lien vérifié à Rank porte sur un point voisin, pas sur ce terme |
| Sigmund Freud | `trauminhalt` | Traumdeutung | renvoi ciblé et substantiel à des travaux réels de Rank, mise à distance critique de Stekel |

Les 51 autres candidats confirmés (sur les 84 qui ne sont ni le cas Stekel/Ferenczi du § 4.5 ni
déjà cités ci-dessus) suivent la même distribution — convergence documentée ou lien réel mais
topiquement étranger au concept mesuré — sans qu'aucun n'ajoute une figure nouvelle à celles
ci-dessus. Le détail complet (passages, preuves de lien, les deux lectures indépendantes)
est conservé hors dépôt ; `core/divergences.py` documente la méthode et sa validation, et
`core/divergences.reserve()` porte, avec toute liste de candidats qu'il produit, le rappel qu'une
liste de ce genre ne contient aucun verdict.

**Ce que ce chantier change, et ce qu'il ne change pas.** Il ajoute une cinquième opposition
vérifiée au § 4 (§ 4.5, Stekel contre Ferenczi) — la première trouvée par un mécanisme systématique
plutôt que par une lecture large du corpus, ce qui répond directement à la question posée en tête
de cette section. Il confirme aussi, à un niveau de détail que les trois détecteurs écartés
n'avaient jamais atteint, le résultat du § 5 sur Ferenczi : sur 98 candidats construits
spécifiquement pour repérer où un dialogue inter-auteurs POURRAIT laisser une trace lexicale, un
seul en montre une de désaccord. La divergence, dans ce corpus, se lit — le § 4 le prouve, cinq
fois maintenant — mais elle ne se détecte que rarement par le seul vocabulaire qui bouge, quelle
que soit la sophistication du croisement qui le mesure ; l'écrasante majorité de ce que ce
vocabulaire donne à lire, une fois vérifié, est une convergence.
