# Branches et dérivations — ce qui apparaît, ce qui disparaît, et qui reprend

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_branches.py` — ne pas éditer à la main : tous les
> chiffres viennent du corpus à chaque exécution. Régénérer après tout ajout d'œuvre et toute
> modification de lexique.
>
> **Ce que ce document est.** La trajectoire de chaque vocabulaire dans l'œuvre de chaque auteur :
> quand il apparaît, quand il cesse, s'il tient dans un seul livre, et si un autre auteur le
> reprend ensuite.
>
> **RÉSULTAT À LIRE AVANT LES TABLEAUX. La comparaison de fréquence ENTRE auteurs ne donne rien : sur 35 signatures brutes, 31 portent sur le propre lexique de l'auteur — vrai par construction — et les 4 restantes viennent toutes d'un corpus de 885 atomes en une seule œuvre. Après contrôles, il n'en reste AUCUNE. C'est la chronologie interne, et elle seule, qui montre quelque chose.**
>
> **Ce que ce document n'est pas.** Une histoire des idées, ni une carte des désaccords. Un mot
> qui apparaît dans l'œuvre tardive d'un auteur peut être un objet nouveau comme un mot nouveau
> pour un objet ancien — et le corpus a mesuré que la seconde possibilité est fréquente :
> Ferenczi, l'auteur qui a le plus visiblement changé de position, ne laisse que **deux**
> révisions de soi confirmées sur 74 signaux relus.
>
> **La datation est une fenêtre, pas une date.** Freud a cessé de signaler ses ajouts dès la
> troisième édition : un vocabulaire tardif peut donc se trouver imprimé dans un livre ancien.
> Toute trajectoire est un endroit où aller lire, jamais un fait établi.

---

## 1. Ce qui ne marche pas — la comparaison entre auteurs, mesurée puis écartée

La mesure évidente : chercher les motifs sur lesquels un auteur domine tous les autres, et appeler cela sa divergence. Elle donne **35** motifs sur ce corpus. Deux contrôles suffisent à tout emporter.

| Étape | Motifs restants |
|---|---:|
| signatures brutes (un auteur ≥ ×8 le second) | 35 |
| après retrait de celles portant sur SON PROPRE lexique | 4 |
| après retrait des corpus minuscules et des auteurs d'une seule œuvre | **0** |

**Le premier contrôle est le plus coûteux.** Chaque auteur du corpus est décrit avec SON lexique — le motif `amphimixis` a été écrit pour Ferenczi, dans le lexique de Ferenczi. Qu'il y domine n'établit rien : c'est vrai par construction. **31 des 35 signatures** sont dans ce cas, et les publier ferait passer un choix de lexicographe pour un trait d'auteur.

Les **4** qui survivent au premier contrôle sont toutes du même auteur :

| Motif | Auteur dominant | Densité | Motif défini par |
|---|---|---:|---|
| `vorstellung` | Josef Breuer | 202,3 ‰ | Sigmund Freud |
| `erregung|erregt|reizung` | Josef Breuer | 127,7 ‰ | Sigmund Freud |
| `spaltung|personlichkeitsspaltung|sel…` | Josef Breuer | 38,4 ‰ | Sándor Ferenczi |
| `hypnoid` | Josef Breuer | 30,5 ‰ | Sigmund Freud |

Et le second contrôle les emporte toutes : Josef Breuer pèse **885 atomes dans une seule œuvre**. C'est exactement le double artefact — petit corpus, livre unique — qui avait déjà fait confirmer sept fausses divergences en juillet.

**C'est le troisième résultat négatif du même ordre dans ce corpus**, et les trois se répondent : le signal `ecart_freud` n'a rien confirmé sur cinq candidats, l'appariement de concepts par voisinage une divergence sur seize, la signature lexicale **zéro sur 35**. La fréquence d'un mot n'établit jamais une divergence de doctrine dans ce corpus — trois méthodes différentes le disent.

---

## 2. Ce qui marche — la chronologie interne de chaque œuvre

La comparaison porte ici sur **un auteur contre lui-même**, dans le temps. C'est ce qui la rend défendable là où le contraste entre auteurs échoue : le lexicographe qui a écrit le motif, la taille du corpus, la langue et l'orthographe sont les mêmes des deux côtés de la coupure. Il ne reste que le temps.

**1 652 trajectoires** mesurées (un motif chez un auteur ayant au moins trois œuvres d'au moins 50 atomes, et au moins 25 occurrences) :

| Classe | Motifs | Ce que cela veut dire |
|---|---:|---|
| **constant** | 1 383 | le mot traverse l'œuvre — aucun déplacement |
| **disparait** | 113 | l'inverse : le mot cesse d'être employé |
| **apparait** | 92 | la seconde moitié de l'œuvre en porte plusieurs fois plus |
| **livre_unique** | 64 | un seul livre porte presque tout, sans avant ni après |

### Les vocabulaires qui APPARAISSENT

La mesure retrouve, sans qu'on les lui ait données, les tournants documentés de la psychanalyse — ce qui est le meilleur contrôle qu'on puisse lui demander : elle ne les découvre pas, elle les rend visibles et vérifiables.

| Motif | Auteur | Œuvre dominante | Année | Part d'un livre | Avant → après |
|---|---|---|---:|---:|---|
| `orgas` | Wilhelm Stekel | onanie_homosexualitaet | 1917 | **98 %** | 0,0 → 3,7 ‰ |
| `bipolar` | Wilhelm Stekel | sprache_des_traumes | 1911 | 41 % | 0,0 → 1,2 ‰ |
| `ich-|ichs` | Otto Rank | genetische_psychologie_2 | 1928 | **85 %** | 0,0 → 5,6 ‰ |
| `introjekt` | Karl Abraham | entwicklungsgeschichte_lib | 1924 | **98 %** | 0,0 → 17,9 ‰ |
| `baum|baume` | Otto Rank | lohengrinsage | 1911 | 57 % | 0,0 → 4,5 ‰ |
| `todestrieb` | Sigmund Freud | jenseits | 1920 | 45 % | 0,0 → 3,2 ‰ |
| `uber-ich|uberich` | Sigmund Freud | neue_folge | 1933 | 32 % | 0,0 → 15,0 ‰ |
| `amphimix|amphimikt` | Sándor Ferenczi | genitaltheorie | 1924 | **83 %** | 0,0 → 5,8 ‰ |
| `inversion|invertiert|urning|urlinde` | Wilhelm Stekel | onanie_homosexualitaet | 1917 | **100 %** | 0,0 → 1,7 ‰ |
| `lamarck|haeckel|darwin|bolsche|doflein` | Sándor Ferenczi | genitaltheorie | 1924 | **83 %** | 0,0 → 4,9 ‰ |
| `analytiker|analysand|lehranalyse|leh…` | Wilhelm Stekel | onanie_homosexualitaet | 1917 | **83 %** | 0,0 → 0,9 ‰ |
| `thalass|regressionszug|regressionste…` | Sándor Ferenczi | genitaltheorie | 1924 | **81 %** | 0,0 → 5,3 ‰ |
| `(?:vom|im|ins|zum) es\b|(?<!in )(?<!…` | Sigmund Freud | ich_und_es | 1923 | 46 % | 0,1 → 11,0 ‰ |
| `mutterleib|intrauterin|embryo(?!log)…` | Wilhelm Stekel | sprache_des_traumes | 1911 | **72 %** | 0,1 → 5,1 ‰ |

*Une part en gras signale que l'œuvre dominante porte plus de 60 % des occurrences : le déplacement tient alors à un LIVRE — souvent son sujet même — et non à un tournant dans l'œuvre. Ce n'est pas un défaut à corriger, c'est une réserve à lire avec la ligne.*

### Les vocabulaires qui DISPARAISSENT

Le résultat symétrique, et le plus rare. Un mot qu'un auteur cesse d'employer est le seul indice lexical d'un abandon — mais un indice seulement : le corpus rend les passages, il ne dit pas pourquoi.

| Motif | Auteur | Œuvre dominante | Année | Part d'un livre | Avant → après |
|---|---|---|---:|---:|---|
| `hypnoid` | Sigmund Freud | studien_ueber_hysterie | 1895 | 46 % | 2,1 → 0,0 ‰ |
| `deckerinnerung` | Sigmund Freud | psychopathologie | 1901 | 38 % | 1,1 → 0,0 ‰ |
| `onanie|onanist|masturbat` | Karl Abraham | klinische_beitraege | 1907 | **100 %** | 10,7 → 0,0 ‰ |
| `paralyse\b|paralytisch|paralytik|par…` | Sigmund Freud | sammlung_1 | 1893 | 36 % | 0,9 → 0,0 ‰ |
| `ejakulation|ejaculat|samenerguss|sam…` | Karl Abraham | klinische_beitraege | 1907 | **100 %** | 13,9 → 0,0 ‰ |
| `hypochondri|hypochonder` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **80 %** | 9,0 → 0,3 ‰ |
| `bart` | Sigmund Freud | moses_michelangelo | 1914 | **61 %** | 2,5 → 0,1 ‰ |
| `anfall` | Karl Abraham | klinische_beitraege | 1907 | **98 %** | 8,1 → 0,4 ‰ |
| `witz` | Otto Rank | der_kuenstler | 1907 | **68 %** | 13,5 → 0,8 ‰ |
| `konversion|konvertier` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **72 %** | 4,3 → 0,3 ‰ |
| `tendenzios` | Sigmund Freud | witz | 1905 | **77 %** | 2,7 → 0,2 ‰ |
| `neokathar|kathar` | Sigmund Freud | studien_ueber_hysterie | 1895 | 56 % | 2,6 → 0,2 ‰ |
| `perversion|pervers` | Otto Rank | der_kuenstler | 1907 | 57 % | 25,3 → 2,0 ‰ |
| `[a-z]*phob(?!os)|platzangst|prufungs…` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **77 %** | 16,7 → 1,4 ‰ |

*Une part en gras signale que l'œuvre dominante porte plus de 60 % des occurrences : le déplacement tient alors à un LIVRE — souvent son sujet même — et non à un tournant dans l'œuvre. Ce n'est pas un défaut à corriger, c'est une réserve à lire avec la ligne.*

### Les vocabulaires D'UN SEUL LIVRE

Ni apparition ni disparition : un livre porte presque tout le mot, et rien avant ni après. Dire « cet auteur diverge » surinterprète — c'est le vocabulaire de CE livre.

| Motif | Auteur | Œuvre dominante | Année | Part d'un livre | Avant → après |
|---|---|---|---:|---:|---|
| `reue` | Otto Rank | inzest_motiv | 1912 | **97 %** | 0,0 → 2,3 ‰ |
| `uber-ich|uberich` | Sándor Ferenczi | bausteine_3 | 1908 | **100 %** | 0,0 → 6,3 ‰ |
| `kriminal|kriminell` | Otto Rank | inzest_motiv | 1912 | **96 %** | 0,0 → 2,0 ‰ |
| `conversion|konversion` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **92 %** | 3,6 → 0,0 ‰ |
| `trauma(?:s?\b|ti(?:sch|sier)|tolog` | Otto Rank | trauma_der_geburt | 1924 | **91 %** | 0,0 → 4,2 ‰ |
| `angstneuros|angstneurotik` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **95 %** | 38,4 → 0,6 ‰ |
| `verschreibung|pakt|teufelspakt|teufe…` | Sigmund Freud | teufelsneurose | 1923 | **97 %** | 0,1 → 4,4 ‰ |
| `angsthysteri` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **88 %** | 16,5 → 0,5 ‰ |
| `kunst\b|kunstler|kunstlerisch` | Karl Abraham | segantini | 1911 | **93 %** | 1,5 → 44,8 ‰ |
| `charakter(?:zug|bildung|typ|analyse|…` | Karl Abraham | charakterbildung | 1921 | **85 %** | 1,3 → 38,5 ‰ |
| `charakterzug|charakterbildung|charak…` | Karl Abraham | charakterbildung | 1921 | **84 %** | 1,3 → 35,8 ‰ |
| `angstanfall|angstattack` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **86 %** | 11,4 → 0,5 ‰ |
| `angstgefuhl` | Wilhelm Stekel | nervoese_angstzustaende | 1908 | **82 %** | 10,6 → 0,5 ‰ |
| `komik|komisch` | Sigmund Freud | witz | 1905 | **91 %** | 11,9 → 0,7 ‰ |

*Une part en gras signale que l'œuvre dominante porte plus de 60 % des occurrences : le déplacement tient alors à un LIVRE — souvent son sujet même — et non à un tournant dans l'œuvre. Ce n'est pas un défaut à corriger, c'est une réserve à lire avec la ligne.*

---

## 3. Les rameaux isolés — un vocabulaire que personne ne reprend

La seule forme de dérivation que ce corpus puisse établir est LEXICALE : un autre auteur emploie le mot, dans une œuvre postérieure à celle qui l'introduit. Elle n'établit ni emprunt, ni filiation, ni accord — deux hommes peuvent nommer la même chose sans se lire, et le corpus a mesuré combien cela arrive (65 actes de citation reclassés vers un tiers commun).

**Le résultat utile est l'absence.** Sur **467** motifs suivis, **37** ne sont employés que par un seul auteur, sans reprise ni simultanéité : des branches qui n'ont pas pris.

| Auteur | Rameaux isolés | dont sur SON PROPRE motif |
|---|---:|---:|
| Sándor Ferenczi | 27 | 26 |
| Sigmund Freud | 3 | 3 |
| Otto Rank | 3 | 2 |
| Karl Abraham | 2 | 2 |
| Wilhelm Stekel | 2 | 2 |

**La seconde colonne est indispensable.** Un auteur dont le lexique contient beaucoup de termes qui lui sont propres aura mécaniquement beaucoup de rameaux isolés : le motif a été écrit pour lui, donc personne d'autre ne le porte. Sur les 37 rameaux, **35** sont dans ce cas. Ce qui reste — **2** — est la part que la lexicographie n'explique pas, et c'est la seule qui dise quelque chose sur les auteurs.

| Motif | Introduit par | Année | Œuvre |
|---|---|---:|---|
| `verschreibung|pakt|teufelspakt|teufe…` | Sigmund Freud | 1893 | sammlung_1 |
| `statuen?\b|bildhauer|plastik|skulptu…` | Otto Rank | 1900 | traumdeutung |
| `unheimlich` | Sigmund Freud | 1900 | traumdeutung |
| `tagesrest|tagesreste` | Sigmund Freud | 1900 | traumdeutung |
| `realitatsprinzip` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `fetisch` | Karl Abraham | 1907 | klinische_beitraege |
| `begattung` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `erotism` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `organneuros|organerkrankung|organbet…` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `takt(?!i)|einfuhlung` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `katastroph|eintrock|eiszeit|sintflut` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `zuckung|zucken` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `unlustbejahung|verneinung|bejahung` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `wirklichkeitssinn|wirklichkeitsinn|r…` | Sándor Ferenczi | 1907 | populaere_vortraege |
| `laster` | Wilhelm Stekel | 1907 | ursachen_nervositaet |
| `bioanaly` | Sándor Ferenczi | 1908 | bausteine_3 |

**35 motifs apparaissent la même année chez deux auteurs**, et le corpus refuse de les ordonner : deux livres de la même année ne s'ordonnent pas. Le cas exemplaire est 1924 — le *Trauma der Geburt* de Rank et la *Genitaltheorie* de Ferenczi partagent leur vocabulaire central, et rien dans le texte ne dit qui a lu qui.

---

## 4. Ce que ce document ne dit pas

Ce document décrit des TRAJECTOIRES DE VOCABULAIRE, jamais des changements d'avis. Un mot qui apparaît dans l'œuvre tardive d'un auteur peut être un objet nouveau comme un mot nouveau pour un objet ancien — et le corpus a mesuré que la seconde possibilité est fréquente : Ferenczi, l'auteur qui a le plus visiblement changé de position, ne laisse que DEUX révisions de soi confirmées sur 74 signaux relus. Un renversement doctrinal ne laisse presque aucune trace lexicale de première personne. LA COMPARAISON ENTRE AUTEURS A ÉTÉ ESSAYÉE ET ÉCARTÉE : sur 35 motifs où un auteur domine les autres d'un facteur huit, 31 le font sur un motif de leur propre lexique — vrai par construction — et les 4 restants viennent tous d'un corpus de 885 atomes en une seule œuvre. Après contrôles, il n'en reste aucun. C'est le troisième résultat négatif du même ordre dans ce corpus, avec le signal `ecart_freud` (0 confirmé sur 5) et l'appariement de concepts par voisinage (1 sur 16). ENFIN LA DATATION : un atome ne porte pas une date mais une FENÊTRE, Freud ayant cessé de signaler ses ajouts dès la troisième édition. Un vocabulaire tardif peut donc se trouver imprimé dans un livre ancien, et une trajectoire dont `datation_sure` est faux est un endroit où aller lire, jamais un fait établi.

*Reproduire : `python bin/generer_branches.py` · le socle partagé : `SOCLE_COMMUN.md` · l'échec de l'appariement : `APPARIEMENT_ECARTE.md`.*
