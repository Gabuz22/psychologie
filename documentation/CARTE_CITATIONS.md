# La carte des actes de citation

> **État documentaire : photographie historique.** Les nombres de 40 œuvres, 107 actes ou 0,45 %
> décrivent une campagne antérieure. L'état courant est donné par `manifests/references_canoniques.json`
> et `documentation/REFERENCE_CANONIQUE.md` ; la méthode et les échecs décrits ici restent valides.

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

- **0,454 % du corpus** touché (248 phrases sur 54 626) — chiffre corrigé le 2026-07-30 : le code
  rendait une somme de *côtés d'acte* et annonçait 284 phrases, soit 0,52 %, en comptant deux fois
  toute phrase citée par deux actes. La docstring de `carte.couverture` portait déjà le bon chiffre.
  Voir [COUVERTURE_MESUREE.md](COUVERTURE_MESUREE.md) § 1 ;
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

**Le détecteur de chapitres a été réparé** (2026-07-29, puis achevé le 2026-07-30 — voir
[CHAPITRAGE.md](CHAPITRAGE.md)). Il était taillé sur le format de la *Traumdeutung* et laissait
20 œuvres sur 40 sans aucun chapitre — dont les cinq volumes de Ferenczi, 100 % de son corpus.
Dix-huit œuvres déclarent désormais leur propre motif : **349 sections contre 111**, atomes sans
chapitre ramenés de 46 % à **5,6 %**, et **neuf lectures déclarées contre une**. Aucun volume n'est
plus muet ; les sept œuvres sans chapitre sont de courts articles qui n'en ont pas.

Trois de ces lectures justifiaient le chantier à elles seules : « Zur Kritik der Rankschen
*Technik der Psychoanalyse* », la rupture entre Ferenczi et Rank (80 atomes), et les deux textes des
*Bausteine III* où Ferenczi rend compte de Freud — « Die Bedeutung Freuds für die Mental
Hygiene-Bewegung » (223 atomes) et « Freuds Einfluss auf die Medizin » (181). Ce sont les deux plus
longues lectures déclarées du corpus, et elles dormaient dans le seul volume que le détecteur ne
voyait pas du tout.

**Les mentions nominales sont désormais la seconde couche** (2026-07-29). Elles couvrent 11
couples sur 15 contre 6 pour les actes, et 2 135 phrases contre 248 — avec un recouvrement quasi
nul (1,7 %) : ce ne sont pas deux mesures du même fait, ce sont deux faits. Le cas Ferenczi
justifiait à lui seul le chantier : il nomme Freud dans **960** de ses phrases et ne partage un
texte avec lui que dans neuf. La carte des seuls actes le montrait comme un satellite lointain.

Elles ne sont **jamais additionnées** aux actes — un nom écrit n'est pas un texte partagé — et
tous les passages sont stockés, pas un échantillon : un compte qu'on ne peut pas aller lire ne
vaut rien. 145 des 2 899 mentions portent l'avertissement d'homographe (« Abraham » désigne aussi
le patriarche biblique, que Rank et Freud citent abondamment dans leurs travaux sur le mythe) —
et **la lecture a montré que l'avertissement était fondé : 57 de ces 145 ont été rejetées, 39 %**.

Un oubli réel a été trouvé au passage : `comparaison.NOMS` n'avait **aucun jeton pour Sándor
Ferenczi**, entré dans le corpus sans que son nom entre dans la table des mentions. Il pèse 16,8 %
des atomes, et aucun auteur ne pouvait être enregistré comme le nommant — le couple Freud ↔
Ferenczi paraissait unidirectionnel par accident de configuration. Mesuré après correction :
**80 atomes le nomment** (Freud 32, Rank 30, Abraham 18). Un test vérifie désormais que tout
auteur ayant des atomes possède un jeton, pour que l'oubli ne se reproduise pas au prochain.
