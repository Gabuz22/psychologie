# Le socle commun, mesuré — et la forme qu'il a réellement

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_socle.py` — ne pas éditer à la main : tous les
> chiffres viennent du corpus à chaque exécution, par le même chemin de calcul que la base du
> site. Régénérer après toute campagne de lecture, tout ajout d'œuvre et toute modification de
> lexique.
>
> **Ce que ce document est.** La réponse mesurée à « qu'est-ce que ces auteurs partagent ? »,
> par TROIS couches qui ne se multiplient jamais : le texte réellement partagé, le mot
> réellement commun, et ce qui ressemble à du partage sans en être.
>
> **RÉSULTAT À LIRE AVANT LES CHIFFRES. Le socle n'a pas la forme d'un noyau. 91,4 pour cent des actes de citation confirmés touchent Sigmund Freud, aucune phrase du corpus n'est partagée par trois auteurs, et les mots que les six auteurs allemands emploient au même taux sont surtout de la langue courante. Ce que ce corpus prouve, ce n'est pas une doctrine commune : c'est une étoile.**
>
> **Ce que ce document n'est pas.** Une carte des idées de la psychanalyse. Aucune couche ici ne
> nomme la nature d'un rapport — ni accord, ni dette, ni opposition. Le corpus a mesuré ce que
> valent ces qualifications : le marqueur construit pour repérer les écarts d'un disciple avec
> Freud n'a rien confirmé sur cinq candidats, les cinq passages étant des renvois d'accord.
>
> **Pourquoi trois couches séparées.** Les croiser est l'erreur que ce corpus a déjà mesurée deux
> fois. Attribuer un acte de citation à chacun des concepts que la phrase touche fabrique 1 366
> « liens » là où il y a 354 actes réels, chaque phrase portant 3,5 concepts en moyenne.
> Une reprise établit que deux auteurs partagent CE PASSAGE ; elle n'établit rien sur le concept
> que le passage mentionne au passage.

---

## 1. Le partage attesté — et il a la forme d'une étoile

La seule couche qui **prouve** un partage de substance : un texte passe d'une œuvre à une autre, et une lecture en contexte l'a confirmé. Sur les 354 actes de citation du corpus, 353 ont été lus et **280 confirmés**.

| Couple d'auteurs | Actes confirmés |
|---|---:|
| Sigmund Freud ↔ Wilhelm Stekel | 115 |
| Otto Rank ↔ Sigmund Freud | 82 |
| Karl Abraham ↔ Sigmund Freud | 31 |
| Sigmund Freud ↔ Sándor Ferenczi | 22 |
| Karl Abraham ↔ Otto Rank | 12 |
| Otto Rank ↔ Wilhelm Stekel | 7 |
| Josef Breuer ↔ Sigmund Freud | 6 |
| Sándor Ferenczi ↔ Wilhelm Stekel | 3 |
| Otto Rank ↔ Sándor Ferenczi | 1 |
| Karl Abraham ↔ Wilhelm Stekel | 1 |

**Le résultat n'était pas cherché, et c'est le principal de ce document.** 91,4 pour cent des actes confirmés touchent **Sigmund Freud** : il en reste **24** qui ne le touchent pas, sur 280. Les disciples ne se citent presque pas entre eux — ils citent le maître, séparément. Ce n'est pas un noyau commun, c'est une étoile.

| Auteur | Actes confirmés le touchant |
|---|---:|
| Sigmund Freud | 256 |
| Wilhelm Stekel | 126 |
| Otto Rank | 102 |
| Karl Abraham | 44 |
| Sándor Ferenczi | 26 |
| Josef Breuer | 6 |

### Aucun passage du corpus n'est partagé par trois auteurs

Un socle textuel se prouverait par un passage que plusieurs auteurs reprennent tous. On compte donc, pour chaque phrase touchée par un acte confirmé, le nombre d'auteurs **distincts** qui la partagent :

| Auteurs partenaires | Phrases |
|---:|---:|
| 1 | 770 |
| 2 | 10 |

La profondeur maximale est de **2**. Le passage le plus repris du corpus est donc partagé par deux auteurs, jamais trois — et il reste 10 phrases dans ce cas sur l'ensemble du corpus.

---

## 2. Le mot partagé — ce qui est stable est surtout de l'allemand courant

Le même motif appliqué à tous les corpus allemands. Cette couche ne prouve **aucun** partage de pensée, seulement d'usage : c'est la thèse fondatrice du projet qu'un même mot peut désigner autre chose chez deux auteurs, et la mesure qui prétendrait en décider a été construite puis écartée (6,2 % de précision, une divergence confirmée sur seize — voir [APPARIEMENT_ECARTE.md](APPARIEMENT_ECARTE.md)).

Les lexiques définissent **483** motifs allemands ; **460** subsistent une fois écartés ceux que deux lexiques écrivent autrement pour retenir exactement les mêmes phrases. Parmi eux, **206** sont employés par tous les auteurs allemands au-dessus de 1,0 ‰ — **44** dans un rapport resserré (≤ ×4,0), **162** dans un rapport large.

### Les mots les plus également partagés

| Motif | Écart max/min | Densités (‰) |
|---|---:|---|
| `leben|lebendig` | ×1,5 | Rank 47 · Abraham 41 · Freud 39 · Ferenczi 39 · Stekel 36 · Breuer 30 |
| `tier|schlange|pferd|hund(?!ert)|vogel|…` | ×1,5 | Rank 22 · Ferenczi 21 · Breuer 17 · Freud 17 · Stekel 16 · Abraham 15 |
| `mensch` | ×1,6 | Breuer 52 · Ferenczi 50 · Rank 49 · Abraham 46 · Freud 38 · Stekel 33 |
| `kopf` | ×1,8 | Ferenczi 9 · Breuer 8 · Stekel 7 · Abraham 6 · Rank 6 · Freud 5 |
| `auge|blick|sehen\b|licht\b|farbe|anblick` | ×1,8 | Abraham 54 · Ferenczi 38 · Rank 34 · Stekel 31 · Breuer 30 · Freud 30 |
| `hand(?:e|en|es)?\b` | ×1,9 | Rank 16 · Ferenczi 13 · Stekel 12 · Breuer 10 · Freud 9 · Abraham 8 |
| `nacht|nachts|nachte|dunkel|finster` | ×1,9 | Breuer 27 · Stekel 20 · Rank 19 · Ferenczi 18 · Freud 17 · Abraham 15 |
| `hemmung` | ×2,0 | Breuer 9 · Ferenczi 8 · Rank 7 · Abraham 6 · Freud 5 · Stekel 4 |
| `sprache|sprachlich|wort\b|worte|sprechen` | ×2,0 | Breuer 42 · Ferenczi 40 · Abraham 33 · Freud 30 · Rank 24 · Stekel 21 |
| `familie|familiar` | ×2,2 | Rank 12 · Ferenczi 8 · Abraham 7 · Freud 7 · Stekel 6 · Breuer 6 |
| `knabe|knaben|madchen|junge\b` | ×2,2 | Rank 38 · Stekel 28 · Abraham 25 · Freud 24 · Breuer 22 · Ferenczi 17 |
| `erlebnis|erlebniss` | ×2,4 | Freud 11 · Ferenczi 8 · Abraham 8 · Breuer 8 · Stekel 5 · Rank 5 |

**C'est le résultat qui refroidit.** Ce que les six auteurs emploient au même taux n'est pas la doctrine — c'est la langue : la vie, l'homme, l'œil, la main, la nuit. Le vocabulaire technique, lui, se disperse. Un socle lexical de la psychanalyse ne ressort pas de cette mesure.

### Les mots dont l'usage diverge le plus — avec leurs deux contrôles

Un écart large **n'est pas un désaccord de doctrine** : c'est un endroit où aller lire. Deux drapeaux disent d'abord s'il vaut la peine d'y aller, et chacun a été payé par une erreur déjà commise dans ce projet — sept des seize divergences lues en juillet étaient des artefacts d'un livre unique, et un « détecteur » n'utilisant que le rapport des effectifs atteint déjà une AUC de 0,576.

| Motif | Écart | Porté par | Motif défini par | Un seul livre ? | Petit corpus ? |
|---|---:|---|---|---|---|
| `sohn|sohne|sohnes` | ×88,1 | Otto Rank (96,9 ‰) | **lui-même** | **oui** (81 %) | — |
| `dichter|dichtung|dichterisch|gedicht` | ×70,3 | Otto Rank (77,3 ‰) | **lui-même** | **oui** (83 %) | — |
| `dichter|dichtung` | ×64,7 | Otto Rank (71,2 ‰) | Karl Abraham | **oui** (84 %) | — |
| `hypnos|hypnot|kathar` | ×49,9 | Josef Breuer (59,9 ‰) | Sigmund Freud | **oui** (100 %) | **oui** |
| `konig|konigin|konigs|konigstochter|kon…` | ×48,9 | Otto Rank (53,8 ‰) | **lui-même** | — | — |
| `bruder|schwester|geschwister` | ×47,0 | Otto Rank (108,0 ‰) | Wilhelm Stekel | **oui** (91 %) | — |
| `geburt|geboren|gebar|entbind` | ×46,5 | Otto Rank (51,1 ‰) | **lui-même** | — | — |
| `dichter|dichtung|poet` | ×43,9 | Otto Rank (74,6 ‰) | Sigmund Freud | **oui** (84 %) | — |
| `hysteri` | ×42,1 | Josef Breuer (197,7 ‰) | Sigmund Freud | **oui** (100 %) | **oui** |
| `mythus|mythos|mythen|mythisch|mythologi` | ×41,7 | Otto Rank (41,7 ‰) | **lui-même** | — | — |
| `erregung|erregt|reizung` | ×38,7 | Josef Breuer (127,7 ‰) | Sigmund Freud | **oui** (100 %) | **oui** |
| `behandlung|therapie|heilung|kur\b` | ×36,6 | Sándor Ferenczi (40,3 ‰) | Karl Abraham | — | — |
| `vorstellung` | ×31,6 | Josef Breuer (202,3 ‰) | Sigmund Freud | **oui** (100 %) | **oui** |
| `weib` | ×29,9 | Otto Rank (32,9 ‰) | Sigmund Freud | — | — |
| `religio|gott|kultus|ritus` | ×27,9 | Otto Rank (30,7 ‰) | Karl Abraham | — | — |

La colonne **motif défini par** est le troisième contrôle, et le plus sévère : **45 des 162 motifs dispersés** sont dominés par l'auteur dont le lexique a défini le motif. Leur écart est vrai par construction et n'établit aucune divergence — c'est le même chiffre qui vide entièrement la comparaison entre auteurs dans [BRANCHES_ET_DERIVATIONS.md](BRANCHES_ET_DERIVATIONS.md).

Sur les 162 motifs dispersés, **70** ont leur densité extrême portée à plus de 60 pour cent par une seule œuvre, et **30** ont cette densité portée par le plus petit corpus de la comparaison. Ces deux drapeaux ne filtrent rien — filtrer supposerait qu'on sait trancher, et on ne sait pas. Ils disent seulement qu'une divergence publiée sans les regarder a de bonnes chances d'être un artefact.

---

## 3. Le faux socle — ce que deux auteurs partagent sans rien se devoir

**65 actes** ont été **reclassés** par la lecture : les deux auteurs recopient la même page d'un troisième, qui n'est pas dans le corpus. Sans lecture, chacun aurait été publié comme un emprunt entre auteurs — c'est-à-dire comme du socle.

| Tiers cité par les deux | Actes |
|---|---:|
| Peter Rosegger | 10 |
| Sigmund Freud | 6 |
| Rudolf Kleinpaul | 5 |
| Friedrich Hebbel | 5 |
| Jean Paul | 5 |
| Karl Albert Scherner | 4 |
| Herbert Silberer | 3 |
| Gottfried Keller | 3 |
| Franz Grillparzer | 3 |
| Otto Rank | 2 |
| Karl Abel | 2 |
| Josef Popper-Lynkeus | 1 |
| Ernest Jones | 1 |
| Artemidoros von Daldis | 1 |
| Georg Christoph Lichtenberg | 1 |

**28 tiers distincts.** Ce que ces auteurs ont en commun ici, ce n'est pas une doctrine : c'est une bibliothèque — des poètes, des sources antiques, des psychologues d'avant la psychanalyse.

*Un auteur du corpus peut figurer dans cette liste, et ce n'est pas une anomalie : quand Rank et Stekel recopient tous deux la même page de la* Traumdeutung*, le tiers est Freud — aucun des deux ne lit l'autre, et le lien Rank ↔ Stekel qu'un calcul seul aurait publié n'existe pas.*

---

## 4. Ce que ce document ne dit pas

Ce document répond à « qu'est-ce que ces auteurs partagent ? » par TROIS mesures qui ne se multiplient jamais, parce que les multiplier est précisément l'erreur mesurée dans ce corpus : attribuer un acte de citation à chacun des concepts que la phrase touche fabrique des centaines de « liens » là où il y a quelques centaines d'actes. Le PARTAGE ATTESTÉ est la seule couche qui prouve un partage de substance, et il est petit : il ne dessine pas un noyau commun mais une étoile centrée sur Freud, et aucun passage du corpus n'est partagé par trois auteurs. Le MOT PARTAGÉ ne prouve aucun partage de pensée — seulement d'usage. Un mot dont l'usage diverge n'est PAS un désaccord de doctrine : c'est un endroit où aller lire. La mesure qui prétendrait trancher a été construite puis écartée (6 % de précision, une divergence confirmée sur seize). Le TIERS COMMUN est exclu du socle et nommé : deux auteurs qui recopient la même page d'un troisième se ressemblent sans rien se devoir. Enfin, ce que le corpus ne montre pas ne veut pas dire que rien n'a eu lieu : entre deux auteurs de langues différentes la reprise textuelle est aveugle par construction.

*Reproduire : `python bin/generer_socle.py` · les actes un par un : `python bin/analyser.py --agent lectures` · méthode et limites : `COMPARAISON_INTER_AUTEURS.md` §1 et `APPARIEMENT_ECARTE.md`.*
