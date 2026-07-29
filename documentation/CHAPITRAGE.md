# Le chapitrage, et pourquoi il fallait le réparer

Un chapitre n'est pas un ornement de navigation. C'est ce qui porte la **lecture déclarée** —
quand un chapitre annonce dans son titre qu'il traite d'un autre auteur, c'est l'édition elle-même
qui déclare la lecture. `core/comparaison.py` la désigne comme « le lien le plus fort du corpus, et
le seul qui traverse la barrière des langues ».

Or la base n'en comptait **qu'une seule**. Ce n'était pas un fait de corpus.

---

## 1. Le défaut

Le détecteur unique était taillé sur une seule mise en page :

```python
_CHAPITRE = re.compile(r"^[ \t]*([IVX]{1,5})\.[ \t]*\n\s*\n[ \t]*(\S[^\n]{3,90})", re.M)
```

Chiffre romain **suivi d'un point**, seul sur sa ligne, puis une ligne vide, puis le titre. C'est
le format de *Die Traumdeutung*, et de presque rien d'autre. Mesuré :

| | avant | première passe | après reprise |
|---|---|---|---|
| œuvres sans aucun chapitre | **20 sur 40** | 9 | **7 sur 40** |
| sections dans le corpus | 111 | 295 | **349** |
| atomes sans chapitre | 46 % | 13 % | **5,6 %** (3 052 sur 54 626) |
| lectures déclarées | **1** | 7 | **9** |

Ferenczi était à **100 %** aveugle — ses cinq volumes, 9 158 atomes. Il numérote sans point et
compose ses titres en capitales : le point de rupture est là.

---

## 2. Un motif par œuvre, pas un détecteur universel

Il n'y a pas de détecteur universel, parce que chaque fac-similé a sa propre mise en page. Le
projet déclare déjà ses bornes œuvre par œuvre — `debut_corps`, `PARATEXTE_FINAL`,
`REGIONS_ECARTEES` — et le chapitrage suit la même règle : `sources.MOTIFS_CHAPITRE`, **dix-huit**
œuvres, chaque motif **relevé dans le texte**, éprouvé contre ses faux positifs, puis **rejoué**
avant d'être inscrit.

| œuvre | avant | après |
|---|---|---|
| **`bausteine_3` (Ferenczi)** | 0 | **51** |
| `bausteine_2` (Ferenczi) | 0 | **36** |
| `klinische_beitraege` (Abraham) | 6 | **28** |
| `inzest_motiv` (Rank) | 7 | **23** |
| `bausteine_1`, `populaere_vortraege` (Ferenczi) | 0 | **17** |
| `mythus_geburt_helden`, `traum_und_mythus` | 0-1 | **12** |
| `trauma_der_geburt`, `genitaltheorie`, `witz` | 0 | **10-11** |
| `neue_folge`, `genetische_psychologie_2` | 0 | **6-7** |
| `entwicklungsgeschichte_libido`, `segantini`, `der_kuenstler` | 0-3 | 2-5 |
| **`charakterbildung` (Abraham)** | 0 | **3** — les trois études, aucune de plus |

**Contrat du motif** : groupes nommés `t` (titre) et `n` (numéro) s'ils existent ; sinon un groupe
unique vaut titre, et à partir de deux le premier vaut numéro et les suivants composent le titre.

### La règle que je me suis imposée, et qui a servi

Un relevé automatisé a proposé 24 motifs en annonçant 283 sections et 9 titres nommant un autre
auteur. **En les rejouant moi-même, j'ai obtenu 140 et 3** — et trois œuvres qui *reculaient*, dont
une tombant à zéro. Une partie de l'écart était prosaïque (de la prose collée après l'expression
régulière, un motif n'étant qu'un renvoi à un autre), mais la leçon vaut d'être écrite : **aucun
motif n'entre sans avoir été rejoué, et sans faire au moins aussi bien que le détecteur commun.**
Sept motifs ont été écartés à ce titre, et un huitième faute d'expression exploitable.

---

## 3. Le second blocage, invisible jusqu'à la mesure

Le chapitrage réparé, les lectures déclarées restaient à **une**. Le blocage était ailleurs :

```python
_INTITULE_COMPLET = re.compile(r"[.!?»]\s*$")
```

Ce filtre exigeait qu'un titre **se termine par une ponctuation**. C'était une parade légitime au
défaut du détecteur commun : quand une œuvre n'a pas d'intitulé de section, celui-ci prend la
première *phrase* du chapitre, tronquée à 90 signes — et « II. Ich knüpfe nun an meine früheren
Bemerkungen an, … die Breuer'sche Meth » passait pour un chapitre que Freud consacrerait à Breuer.

Mais les titres de Ferenczi n'ont pas de point final. Le filtre écartait donc des lectures bien
réelles, dont sa **rupture avec Rank**.

La correction n'est pas de supprimer le filtre — le risque qu'il couvre est réel — mais de le
**restreindre au détecteur commun**. Chaque repère porte désormais son origine : `declare: True`
quand il vient d'un motif propre à l'œuvre (relevé, éprouvé, rejoué), et seul le détecteur
générique reste suspect.

---

## 4. Ce que le corpus voit maintenant

| qui lit qui | chapitre | portée |
|---|---|---|
| **Sándor Ferenczi lit Sigmund Freud** | ***Die Bedeutung Freuds für die Mental Hygiene-Bewegung*** (1926) | **223 atomes** |
| Sándor Ferenczi lit Sigmund Freud | *Über Aktual- und Psychoneurosen im Lichte der Freudschen Forschungen* | 219 |
| **Sándor Ferenczi lit Sigmund Freud** | ***Freuds Einfluss auf die Medizin*** (1933) | **181** |
| Sigmund Freud lit Gustave Le Bon | *II. Le Bon's Schilderung der Massenseele* | 105 |
| **Sándor Ferenczi lit Otto Rank** | ***Zur Kritik der Rankschen « Technik der Psychoanalyse »*** | **80** |
| Sándor Ferenczi lit Sigmund Freud | *Zum 70. Geburtstage Sigmund Freuds* | 50 |
| Sándor Ferenczi lit Sigmund Freud | *Die wissenschaftliche Bedeutung von Freuds « Drei Abhandlungen »* | 27 ×2 |
| Karl Abraham lit Sándor Ferenczi | *Bemerkungen zu Ferenczis Mitteilung über « Sonntagsneurosen »* | 21 |

La ligne de la rupture est celle qui justifiait le chantier : la critique par Ferenczi de la
technique de Rank, avec ses 80 atomes localisés. Elle était dans le corpus depuis l'entrée de
Ferenczi ; le détecteur ne pouvait pas la voir.

Les deux plus longues lectures du corpus sont venues avec la reprise du chantier : ce sont les deux
textes des *Bausteine III* où Ferenczi rend compte de Freud, 404 atomes à eux deux. Le volume était
resté entièrement muet.

*(Les deux entrées à 27 atomes ne sont pas un doublon : le même article de Ferenczi figure dans
deux volumes, les* Populäre Vorträge *et les* Bausteine I.*)*

---

## 5. La reprise des deux derniers trous

Deux œuvres restaient, et les deux ont été reprises le 2026-07-30. Elles ont eu chacune leur
surprise, et la seconde vaut plus que le motif qu'elle a produit.

### `bausteine_3` — une mise en page qui change en cours de volume

3 627 atomes, le plus gros volume du corpus, et zéro chapitre. Le premier passage n'avait « pas
trouvé de motif exploitable » ; en réalité il y en avait **deux**, parce que le recueil posthume
juxtapose des pièces de vingt-cinq années :

- les pièces anciennes portent **leur année seule sur une ligne**, sous le titre — `(1908)`,
  `(etwa 1909)`. La table des matières du volume donne la vérité de terrain, jusque dans son
  intitulé : « Originalarbeiten aus den Jahren 1908—1933 » ;
- les pièces de 1926-1933 n'ont plus d'année mais **la mention de la séance** où elles furent lues.

Le mot qui revient dans toutes ces mentions est `gehalten`. Le seul mot `Vortrag` ne suffisait pas —
il revient au fil des phrases (« meines Vortrages den Eindruck… »), et faisait entrer deux amorces
de corps de texte comme si c'étaient des titres. **51 sections**, dont les deux textes où Ferenczi
rend compte de Freud.

Ce qui a été **écarté**, et pourquoi : le signal de mise en page seul — lignes vides, ligne courte,
lignes vides — donne 106 sections, mais **26 sont des têtes courantes**, dont « Die Bedeutung
Freuds … 303 » trois fois. L'enjeu n'est pas cosmétique : un motif déclaré contourne le filtre de
ponctuation de `comparaison._INTITULE_COMPLET`, donc chaque tête courante retenue **fabriquerait une
fausse lecture déclarée**, répétée autant de fois que la page. Aucune tête courante n'est suivie
d'une ligne d'année ni d'une mention de séance : c'est ce qui les écarte, sans avoir à les nommer.

### `charakterbildung` — le défaut n'était pas dans le motif

Le motif captait 2 études sur 3, et il avait été écarté pour cette raison. Elle était fausse. La
cause était la **borne de début du corps** : `debut_corps` visait la première phrase
(« Das weite Gebiet, welches heute der psychoanalytischen ») et laissait dehors le titre de la
première étude, « I / Ergänzungen zur Lehre vom Analcharakter ». Une étude sur trois entrait au
corpus **sans titre, quel que soit le motif**.

La borne porte maintenant le titre. Elle inclut le chiffre romain et l'appel de note
(`Analcharakter'`) pour rester unique : le titre nu revient seize fois dans le volume, en tête
courante de page. Et le motif a dû apprendre à lire un premier titre dont le chiffre romain — une
ligne d'un seul signe — est emporté avec le bruit de scan par le retrait des blocs illisibles.
**3 sections sur 3.**

La leçon est la même que celle du § 3 : quand une mesure ne bouge pas après une correction, la cause
est ailleurs, et la chercher vaut mieux que raffiner ce qu'on vient de corriger.

---

## 6. Ce qui reste

Sept œuvres n'ont aucun chapitre, et pour toutes c'est désormais **un fait, non un défaut** : ce
sont de courts articles sans sections — `vergaenglichkeit` (44 atomes), `dichter_phantasieren` (88),
`schwierigkeit_psychoanalyse` (90), `kaestchenwahl`, `moses_michelangelo`, `teufelsneurose`,
`traum_telepathie`, `zeitgemaesses_krieg_tod`. Aucun volume n'est plus muet.

Un détail cosmétique assumé : quelques titres portent leur année en tête de clé de chapitre
(« 1927. Zur Kritik der Rankschen… », « 1933. Freuds Einfluss auf die Medizin »), parce que le motif
de ces volumes capte la ligne de datation comme numéro. C'est laid et informatif — la date de
première parution est une donnée utile — et cela ne change rien à la détection.

Deux titres de `bausteine_3` gardent une cicatrice de scan (« Liöbesult über die Rolle des er 5 »,
« Stigmata EB »), et un épigraphe latin de Lessing y passe pour un titre. Trois lignes sur 51, dont
aucune ne nomme un auteur du corpus : elles ne peuvent donc pas fabriquer de fausse lecture
déclarée, et c'est la seule propriété qui compte ici.
