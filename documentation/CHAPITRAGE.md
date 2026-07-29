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

| | avant | après |
|---|---|---|
| œuvres sans aucun chapitre | **20 sur 40** | 9 sur 40 |
| sections dans le corpus | 111 | **295** |
| atomes sans chapitre | 46 % | **13 %** |
| lectures déclarées | **1** | **7** |

Ferenczi était à **100 %** aveugle — ses cinq volumes, 9 158 atomes. Il numérote sans point et
compose ses titres en capitales : le point de rupture est là.

---

## 2. Un motif par œuvre, pas un détecteur universel

Il n'y a pas de détecteur universel, parce que chaque fac-similé a sa propre mise en page. Le
projet déclare déjà ses bornes œuvre par œuvre — `debut_corps`, `PARATEXTE_FINAL`,
`REGIONS_ECARTEES` — et le chapitrage suit la même règle : `sources.MOTIFS_CHAPITRE`, seize
œuvres, chaque motif **relevé dans le texte**, éprouvé contre ses faux positifs, puis **rejoué**
avant d'être inscrit.

| œuvre | avant | après |
|---|---|---|
| `bausteine_2` (Ferenczi) | 0 | **36** |
| `klinische_beitraege` (Abraham) | 6 | **28** |
| `inzest_motiv` (Rank) | 7 | **23** |
| `bausteine_1`, `populaere_vortraege` (Ferenczi) | 0 | **17** |
| `mythus_geburt_helden`, `traum_und_mythus` | 0-1 | **12** |
| `trauma_der_geburt`, `genitaltheorie`, `witz` | 0 | **10-11** |
| `neue_folge`, `genetische_psychologie_2` | 0 | **6-7** |
| `entwicklungsgeschichte_libido`, `segantini`, `der_kuenstler` | 0-3 | 2-5 |

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
| Sándor Ferenczi lit Sigmund Freud | *Über Aktual- und Psychoneurosen im Lichte der Freudschen Forschungen* | 219 atomes |
| Sigmund Freud lit Gustave Le Bon | *II. Le Bon's Schilderung der Massenseele* | 105 |
| **Sándor Ferenczi lit Otto Rank** | ***Zur Kritik der Rankschen « Technik der Psychoanalyse »*** | **80** |
| Sándor Ferenczi lit Sigmund Freud | *Zum 70. Geburtstage Sigmund Freuds* | 50 |
| Sándor Ferenczi lit Sigmund Freud | *Die wissenschaftliche Bedeutung von Freuds « Drei Abhandlungen »* | 27 ×2 |
| Karl Abraham lit Sándor Ferenczi | *Bemerkungen zu Ferenczis Mitteilung über « Sonntagsneurosen »* | 21 |

La troisième ligne est celle qui justifiait tout le chantier : la critique par Ferenczi de la
technique de Rank, c'est-à-dire leur rupture, avec ses 80 atomes localisés. Elle était dans le
corpus depuis l'entrée de Ferenczi ; le détecteur ne pouvait pas la voir.

*(Les deux entrées à 27 atomes ne sont pas un doublon : le même article de Ferenczi figure dans
deux volumes, les* Populäre Vorträge *et les* Bausteine I.*)*

---

## 5. Ce qui reste

Neuf œuvres n'ont toujours aucun chapitre. Pour la plupart, c'est un fait et non un défaut : ce
sont de courts articles sans sections (`vergaenglichkeit`, 44 atomes ; `dichter_phantasieren`, 88).
Deux cas méritent d'être repris :

- **`bausteine_3`** (Ferenczi, 3 627 atomes) — le relevé n'a pas produit de motif exploitable, et
  c'est le plus gros volume encore muet ;
- **`charakterbildung`** (Abraham) — un motif a été trouvé mais ne captait que 2 articles sur 3.

Un dernier détail cosmétique assumé : deux titres portent leur année en tête de clé de chapitre
(« 1927. Zur Kritik der Rankschen… »), parce que le motif de ces volumes capte la ligne de datation
comme numéro. C'est laid et informatif — la date de première parution est une donnée utile — et
cela ne change rien à la détection.
