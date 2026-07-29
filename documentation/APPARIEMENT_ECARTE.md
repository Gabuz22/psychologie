# Apparier des concepts par leur voisinage : mesuré, puis écarté

**Ce document rend compte d'un échec.** Il existe pour qu'on ne recommence pas sans savoir, et
pour que ceux qui recommenceront le fassent avec les chiffres en main. Le module qui a servi à
cette mesure est conservé (`core/appariement.py`) ; **il n'alimente ni la base, ni le site.**

---

## 1. Ce qu'on cherchait, et le verrou qu'on croyait lever

Chaque auteur du corpus est décrit avec ses propres catégories. Personne ne dit donc que la
`Verdrängung` de Rank et celle de Freud sont la même chose. L'idée, la plus prometteuse depuis le
début, était de les rapprocher par leur **voisinage** : deux concepts se ressemblent si les mots
qui les entourent se ressemblent.

`core/comparaison.py` l'avait écartée en juillet 2026, pour une raison précise :

> aucun témoin positif VALIDE n'existe aujourd'hui dans la base. Le seul disponible (« un concept
> comparé à lui-même, coupé en deux moitiés ») mesure la stabilité d'échantillonnage d'une
> signature, pas la correspondance entre deux auteurs.

**Ce verrou-là a bien été levé.** La couche « usage des mots » applique un *même motif* à tous les
corpus : le couple (motif M chez A, motif M chez B) est « le même mot chez deux auteurs » — deux
corpus distincts, deux jeux de phrases distincts, une identité lexicale connue par construction.
Ce n'est plus une moitié comparée à elle-même.

Et le témoin fonctionne : **AUC 0,893**. En retirant des deux signatures le mot qui contribue le
plus, elle reste à 0,872 ; en retirant les trois premiers, 0,846. La R-précision est de **30,3 %
contre 0,3 % au hasard** — cent fois le hasard. Le signal traverse réellement deux corpus.

**Le diagnostic de juillet était donc le mauvais.** La méthode échoue, mais pour d'autres raisons,
et il fallait la construire pour les voir.

---

## 2. Pourquoi elle échoue quand même

### 2.1 Un test à 1 contre 1, un usage à 1 contre 300

Le témoin oppose 1 207 couples positifs à 986 négatifs. L'usage visé est un balayage : tous les
concepts de A contre tous ceux de B. Pour Freud ↔ Ferenczi, cela fait **69 168 comparaisons dont
221 vraies** — 0,32 %.

| seuil | paires retenues | vraies | précision | rappel |
|---|---|---|---|---|
| 95ᵉ centile du bruit (0,131) | 2 442 | 152 | **6,2 %** | 68,8 % |
| 99ᵉ centile (0,196) | 369 | 84 | **22,8 %** | 38,0 % |

Abraham ↔ Rank : 3,9 % et 15,3 %. Une vérité de terrain volontairement généreuse — toute paire
dont les deux sous-concepts appartiennent au même groupe du lexique comptée vraie — ne sauve rien :
16,9 %, 10,8 %, 15,3 %.

### 2.2 Elle ne distingue pas un mot de son synonyme, ni de son contraire

Le témoin négatif *aléatoire* est trop facile : deux mots tirés au hasard parlent trivialement
d'autre chose. Avec un négatif **difficile** — deux mots du même groupe conceptuel — la séparation
tombe de 58 % à 39 % des positifs au-dessus du seuil. Et le haut de ce « bruit » est éloquent :

| couple, réputé négatif | score |
|---|---|
| `behandlung` ↔ `kur` | 0,323 |
| `assoziation` ↔ `grundregel` | 0,316 |
| `hysterie` ↔ `neurose` | 0,300 |
| `maennlichkeit` ↔ `weiblichkeit` | 0,285 |
| `depression` ↔ `manie` | 0,281 |
| `sohn` ↔ `tochter` | 0,273 |

Les trois premiers sont des quasi-synonymes ; les trois derniers des **couples d'opposés**, qui
partagent par construction tout leur entourage. La mesure ne voit pas de différence entre « le même
mot », « son synonyme » et « son contraire ». Elle mesure une proximité de contexte, et rien de
plus.

### 2.3 Les plus hauts scores sont portés par l'autre moitié du terme

- `erogene_zone` (0,553, le plus haut du corpus) : `zone` + `zonen` portent **72 %** du score.
  C'est le substantif du terme lui-même.
- `aktivitaet` (0,540) : `passivitat` porte **88 %**.
- `anfall` (0,423) : `hysterisch*` porte 79 %. `manie` (0,437) : `depressiven` + `melancholie*`, 71 %.

Ces accords seraient les mêmes entre deux corpus psychiatriques allemands quelconques.

### 2.4 Effet de moyeu

Dans le classement Abraham ↔ Rank, le seul motif `tochter` occupe **20 des 154 premières places** :
`tochter ↔ sohn` (0,448, au-dessus de 8 des 10 vraies paires), `tochter ↔ mutter`, `tochter ↔ hass`,
`tochter ↔ liebe`. Les faux positifs de tête sont systématiques, pas dispersés — un lecteur qui
ouvre la liste par le haut tombe d'abord sur eux.

### 2.5 Le score dépend de la taille des corpus

Le score croît avec l'effectif (médiane 0,126 sous 50 porteurs, 0,297 au-delà de 500) et décroît
avec l'écart de taille entre les deux côtés. **Un « détecteur » n'utilisant QUE le rapport des
effectifs atteint déjà une AUC de 0,576.** Avec un témoin négatif apparié en taille, le seuil
strict passe de 0,196 à 0,257 et la part des positifs qui le dépassent tombe de 29,8 % à 14,3 % :
le seuil calibré naïvement est ~30 % trop permissif.

---

## 3. Le résultat qu'on croyait sauver, et qui n'a pas tenu

Restait une lecture inverse, plus modeste et doctrinalement centrale : ne pas apparier des
concepts, mais repérer **les mots partagés dont le voisinage DIVERGE** d'un auteur à l'autre. Un
score bas ne s'explique ni par la synonymie ni par l'opposition ; et la thèse fondatrice du projet
est précisément qu'un même mot peut désigner autre chose chez deux auteurs.

Après contrôle des effectifs et de l'écart de taille, 16 divergences tenaient. **Elles ont été
lues**, passage par passage, puis soumises à un contradicteur chargé de les réfuter.

| verdict après lecture | nombre |
|---|---|
| **artefact d'œuvre** — la signature décrit un livre, pas un auteur | 7 |
| **même sens, autre matière** — le piège principal | 6 |
| mot trop banal pour avoir un sens technique stable | 2 |
| **écart réel** | **1** |

Le contradicteur a **renversé 6 des 7** écarts d'abord confirmés. Deux exemples :

- `gefuehl` semblait le cas le plus fort — divergent entre *tous* les couples d'auteurs, avec 200 à
  360 porteurs de chaque côté. Réfuté : « le rapport de dépendance inverse que le lecteur décrit ne
  sépare pas deux auteurs, il sépare deux livres d'un même auteur ».
- `tier` Abraham ↔ Ferenczi avait reçu une lecture élégante : chez Abraham l'animal est *produit
  par* le travail psychique (glosé « der Totem oder Vater »), chez Ferenczi il est un organisme
  réel dont l'histoire *explique* le psychique. Réfuté : « Ferenczi détient les deux statuts à la
  fois, dans les mêmes volumes ».

Les six cas **convergents** testés en contrepoint ont tous été confirmés — `kind`, `infantil`,
`sohn`, `weiblichkeit`, `psychisch` : le noyau familial et développemental que ces auteurs
partagent vraiment. Mais c'est le résultat le moins surprenant du corpus, et le § 2.3 montre qu'il
est en partie fabriqué par le motif lui-même.

**Un cas sur seize survit à la lecture.** C'est trop peu pour publier quoi que ce soit.

---

## 4. Ce que l'exercice a rapporté

Un échec mesuré rapporte trois choses, et elles sont dans le dépôt :

1. **Un défaut de lexique, corrigé.** En lisant les voisinages du concept `tier` de Rank, on a vu
   que `\bschwan` attrapait **`schwanger`** — enceinte — 65 fois, et `schwanken` 32 fois ; que
   `\bwolf` attrapait **Wolfram von Eschenbach** 25 fois. 28 % et 46 % de captures fausses. Chez
   l'auteur dont la thèse centrale est la naissance, « enceinte » était compté comme « animal ».
   Corrigé dans `core/lexiques/rank.py`, avec les exclusions et leur mesure.

2. **Deux doublons de lexique.** `halluzination`/`halluzinatorisch` et `uebertragung`/`ubertragung`
   sélectionnent les mêmes atomes sous deux noms. `appariement.dedoublonner()` les repère — par
   l'ensemble d'atomes sélectionné, car la comparaison des chaînes de motif ne suffit pas.

3. **Un instrument de mesure réutilisable.** `Signatures.signature()` rend, pour tout couple
   (auteur, motif), les mots qui l'entourent, pondérés relativement à cet auteur-là, avec ses
   effectifs et sa concentration par œuvre. C'est utile pour *décrire* un usage. Ce qui ne tient
   pas, c'est d'en tirer un appariement.

---

## 5. À quelles conditions rouvrir le chantier

Ce n'est pas un « jamais ». C'est un « pas comme ça », et voici ce qu'il faudrait :

- **Une vérité de terrain qui ne soit pas lexicale.** Le témoin actuel valide « même mot ». Il
  faudrait des couples de concepts *attestés comme correspondants* par une source extérieure au
  corpus — un index, une concordance, une édition critique — pour calibrer sur la bonne question.
- **Plafonner la contribution d'une œuvre à une signature.** Sept des seize divergences lues
  étaient des artefacts d'œuvre unique. Une signature devrait être construite œuvre par œuvre puis
  agrégée, non tirée du corpus en vrac.
- **Neutraliser l'unité lexicale et l'antonyme.** Retirer `zone` de la signature d'`erogene`,
  `passivität` de celle d'`aktivität`. Cela suppose de savoir ce qui appartient au terme — donc
  un travail de lexique, pas de statistique.
- **Apparier les effectifs**, ou publier le score relativement à sa case (effectif × écart de
  taille), comme le fait `appariement.reference()`.

Sans ces quatre conditions, la mesure produira des listes plausibles et fausses. Le corpus a été
bâti pour ne pas en produire.
