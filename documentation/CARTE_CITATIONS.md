# La carte des actes de citation

Elle montre une seule chose : **les endroits où un texte passe d'une œuvre à une autre**. Pas des
concepts reliés, pas des affinités d'idées — des passages recopiés, avec les deux versions telles
qu'elles sont imprimées.

Elle est née de deux échecs, et sa forme est entièrement dictée par eux.

---

## 1. Ce qu'elle remplace

L'ambition d'origine était un graphe de concepts reliés par des liaisons pondérées
multi-facteurs. Elle a été construite, mesurée, puis écartée — le détail est dans
[APPARIEMENT_ECARTE.md](APPARIEMENT_ECARTE.md) : la similarité de voisinage ne distingue pas un
mot de son synonyme ni de son contraire, sa précision sur la tâche réelle est de 6 %, et la
lecture des divergences n'en a confirmé qu'une sur seize.

**Un second échec guettait ici même**, et il a été mesuré avant d'écrire une ligne. En agrégeant
les liens de reprise en arêtes concept-à-concept, on obtient un chiffre flatteur :

| ce qu'une agrégation naïve annonce | ce qu'il y a réellement |
|---|---|
| 1 366 arêtes concept-à-concept | **107 actes de citation** |
| 2 590 « liens » par produit croisé | 190 concepts portés des deux côtés |

L'écart vient d'un fait simple : **chaque phrase porte 3,5 concepts en moyenne** (jusqu'à 13). Une
seule paire de phrases citée engendre donc, par produit croisé, des dizaines de « liens » entre
des concepts qui n'ont rien à voir. C'est la même accumulation combinatoire que dans le premier
échec, sous une autre forme.

**D'où l'unité retenue : l'acte de citation.** Des phrases contiguës des deux côtés forment un
seul acte — un auteur qui recopie un paragraphe de trois phrases produit un acte de poids 3, non
trois liens ni trente arêtes.

---

## 2. Ce qu'un acte porte

- **son poids** : le nombre de phrases couvertes, jamais un produit de concepts ;
- **sa preuve, deux fois** : la forme repliée sur laquelle la comparaison a travaillé (pour
  refaire le calcul) et le passage **tel qu'il est imprimé de chaque côté** (pour vérifier dans le
  livre) ;
- **son sens**, quand il est établi — et la carte dit lequel des deux parle : celui que les dates
  imposent, ou celui qu'une attribution écrite déclare ;
- **son verdict de lecture** : confirmé, reclassé vers un tiers, rejeté, ou pas encore relu ;
- **ses concepts**, comme contexte, séparés en trois — portés par les deux passages, par A seul,
  par B seul. Seuls les premiers sont présentés comme informatifs ; les deux autres sont là pour
  qu'on puisse constater ce que le produit croisé aurait fabriqué.

### La preuve a été corrigée deux fois

**Premier défaut : elle était arbitraire.** Le détecteur travaille par suites de six mots et les
rendait triées par ordre alphabétique ; les douze premières preuves affichées commençaient toutes
par « a » — « angst um den… », « aber nicht ohne… », « als kind seinen… ». Or ces suites se
chevauchent : quand un auteur en recopie un autre sur dix-sept mots, le détecteur produit douze
fragments partageant chacun cinq mots avec le suivant. Les recoller restitue le passage réel :
**21 mots en médiane, jusqu'à 54**.

**Second défaut : elle n'était pas dans le livre.** La comparaison travaille sur une forme
normalisée qui neutralise l'orthographe d'avant 1901 et les géminations instables de l'OCR —
« hattest » y devient « hatest », « Stückes » devient « stukes ». Publier cette forme comme preuve
était doublement fautif : illisible pour un germanophone, et introuvable dans le texte imprimé,
donc invérifiable. Chaque acte porte désormais son passage réaligné mot à mot sur l'original,
ponctuation et majuscules comprises. **107 actes sur 107** y parviennent.

Ce que la confrontation donne, sur le cas d'Anna O. recopié par Freud quinze ans après Breuer :

> **Breuer, 1895** — « Sie **gerieth** in einen Zustand von Wachträumen und sah, wie von der Wand
> her eine schwarze Schlange sich dem Kranken näherte, um ihn zu **beissen**. »
>
> **Freud, 1910** — « Sie **geriet** in einen Zustand von Wachträumen und sah, wie von der Wand
> her eine schwarze Schlange sich dem Kranken näherte, um ihn zu **beißen**. »

La réforme orthographique de 1901 est visible entre les deux. C'est cela qu'une forme repliée
faisait disparaître.

---

## 3. Ce que la carte ne voit pas — servi avec elle

C'est le défaut le plus grave qu'ait porté la première version, et il était d'omission. Le résumé
par couple d'auteurs était bâti sur les seuls actes trouvés : **un couple sans acte ne produisait
pas une ligne à zéro, il n'existait pas.** Neuf couples sur quinze disparaissaient sans un mot.

Or cinq de ces neuf sont de **langues différentes**, et pour ceux-là la détection est
mathématiquement impossible : les corpus français et allemand du projet partagent **un seul**
groupe de six mots sur 41 172 et 1 348 514. Pendant ce temps, Freud consacre à Le Bon un chapitre
entier de 105 atomes et le nomme dans 31 phrases. Taire ce couple, c'était présenter un
aveuglement de méthode comme un fait de corpus.

Chaque couple porte donc la **raison de son silence** :

| silence | ce qu'il veut dire |
|---|---|
| *(aucun)* | il y a des actes |
| `langues` | indétectable par construction — aucune conclusion possible |
| `aucun_acte` | même langue, détection possible, rien trouvé — information faible |

Et la couverture est affichée **avant** les actes, non après :

- **0,45 % du corpus** touché (248 phrases sur 54 626) ;
- **22 œuvres sur 40 n'y apparaissent jamais** — dont *Totem und Tabu*, *Massenpsychologie und
  Ich-Analyse*, les *Neue Folge*, toute la *Genitaltheorie*, et les 3 627 atomes des *Bausteine III* ;
- **un tiers des phrases sont trop courtes** pour être comparables (le détecteur écarte d'office
  celles de moins de vingt mots — jusqu'à 45 % du corpus chez Abraham) ;
- **39 % des actes ne sont pas encore relus.**

Chaque œuvre muette est listée avec sa part de phrases trop courtes : c'est parfois toute
l'explication de son silence.

---

## 4. Ce que la carte contient

| couple | actes | phrases | relus | confirmés |
|---|---|---|---|---|
| Otto Rank ↔ Sigmund Freud | 53 | 68 | 33 | 31 |
| Karl Abraham ↔ Otto Rank | 19 | 22 | 11 | 4 |
| Karl Abraham ↔ Sigmund Freud | 18 | 28 | 9 | 9 |
| Josef Breuer ↔ Sigmund Freud | 9 | 14 | 6 | 3 |
| Sigmund Freud ↔ Sándor Ferenczi | 7 | 8 | 6 | 5 |
| Otto Rank ↔ Sándor Ferenczi | 1 | 2 | 0 | 0 |

Le déséquilibre est réel, et il ne doit pas se lire comme une histoire. Rank et Ferenczi ont
co-signé un livre en 1924 — dont une partie a d'ailleurs été **retirée du corpus** faute
d'attribution établie, les éditeurs posthumes l'ayant attribuée à Ferenczi sur le souvenir de sa
veuve (voir `REGIONS_ECARTEES` dans `core/sources.py`). Un seul acte de citation entre eux ne dit
donc rien de leur rapport ; il dit ce que ce corpus, réduit à ces volumes-là, permet de voir.

---

## 5. Un défaut trouvé en chemin, et corrigé

L'audit de cette carte a révélé un oubli dans une autre couche : `comparaison.NOMS` ne contenait
**aucun jeton pour Sándor Ferenczi**, entré dans le corpus sans que son nom entre dans la table
des mentions. Il pèse 16,8 % des atomes, et aucun auteur ne pouvait être enregistré comme le
nommant — le couple Freud ↔ Ferenczi paraissait unidirectionnel, ce qui était un accident de
configuration présenté comme un fait de texte. Mesuré après correction : **80 atomes le nomment**
(Freud 32, Rank 30, Abraham 18).

---

## 6. Ce qui reste ouvert

**Le détecteur de chapitres ne voit pas Ferenczi.** `lectures_declarees` ne compte qu'**une seule
ligne** dans toute la base, alors que la couche de comparaison désigne la lecture déclarée comme
« le lien le plus fort du corpus, et le seul qui traverse la barrière des langues ». Ce n'est pas
un fait de corpus mais un défaut de détecteur, à deux étages : le repérage de chapitre est taillé
sur le format de la *Traumdeutung*, 46 % des atomes n'ont aucun chapitre, et **les cinq volumes de
Ferenczi en ont zéro** — 100 % de son corpus. L'audit a relevé dans les sources brutes au moins
cinq sections de Ferenczi consacrées à un autre auteur, dont « Zur Kritik der Rankschen *Technik
der Psychoanalyse* » : leur rupture, 81 atomes consécutifs portant 12 mentions de Rank. C'est un
chantier à part entière.

**Les mentions nominales sont la moitié manquante.** Elles couvrent 11 couples sur 15 contre 6
pour les actes, et 2 136 atomes contre 248 — avec un recouvrement quasi nul (1,7 %). Le cas
Ferenczi est parlant : 9 phrases d'acte contre 1 090 de mention, soit 1 pour 121. Une carte qui
n'affiche que les actes le montre comme un satellite lointain de Freud, alors qu'il le nomme dans
une phrase sur dix de son œuvre. Les y intégrer sans les confondre avec des actes — ce sont des
liens auteur-à-auteur, pas des passages partagés — est l'étape suivante la plus utile.
