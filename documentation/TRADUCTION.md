# Traduire depuis l'allemand — ce qu'un seul mot français doit porter

> **État documentaire : photographie historique.** Les analyses lexicales restent utiles, mais le
> pilote actuel contient 11 146 empreintes et son `meta.scope` est vide : aucune couverture totale
> ne doit être déduite de ce document.

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_traduction.py` — ne pas éditer à la main : la charge
> et la contamination sont recalculées sur le corpus à chaque exécution. Régénérer après tout
> ajout d'œuvre.
>
> **Ce que ce document est.** Pour chaque terme canonique allemand, la mesure de ce qu'un mot
> français unique doit couvrir : le nombre de formes distinctes de la famille, la part qui vit
> à l'intérieur d'un composé, et les faux amis que le radical attrape.
>
> **RÉSULTAT À LIRE AVANT LES TABLEAUX. Aucun de ces mots n'est un mot : *Lust* demande **79 formes allemandes distinctes** pour couvrir 90 % de ses emplois, et une recherche par radical sur *Lust* ramasse **11,1 % de faux amis** — c'est-à-dire du texte qui n'a rien à voir avec le terme. Traduire par un mot unique est une décision, pas une évidence. Un terme est pire encore et ne figure dans aucun de ces deux classements : *Ich*, dont le radical est déclaré INUTILISABLE — ses chiffres mesureraient l'échec de la méthode, pas le mot. Voir §2.**
>
> **Ce que ce document n'est PAS, et c'est le point le plus important.** Il ne juge aucune
> traduction. Décider que « pulsion » rend bien *Trieb* demande une compétence de traducteur et
> une histoire des traductions ; ce corpus n'a ni l'une ni l'autre. La colonne **français
> courant** est une donnée EXTÉRIEURE, donnée pour être confrontée, jamais validée.
>
> **Le corpus n'a qu'une ancre bilingue** : Gustave Le Bon, 1 485 atomes, 1895 — et il n'est
> pas psychanalyste. Le seul énoncé solide qu'on puisse en tirer sur une traduction est un
> **refus** de correspondance, pas une validation. Ils sont en §3.

---

## 1. La charge de traduction — l'allemand compose, le français juxtapose

Un terme canonique n'apparaît presque jamais seul. La **charge** est le nombre de formes allemandes distinctes qu'il faut couvrir pour atteindre 90 % des occurrences : c'est ce qu'un mot français unique doit porter.

| Terme | Français courant | Formes | Occurrences | **Charge** | Radical interne |
|---|---|---:|---:|---:|---:|
| *Ich* ⚠ | moi | 2 761 | 107 369 | (902) | 72 % |
| *Lust* | plaisir | 158 | 3 144 | **79** | 41 % |
| *Trieb* | pulsion | 146 | 3 692 | **66** | 36 % |
| *Traum* | rêve | 304 | 18 739 | **46** | 7 % |
| *Angst* | angoisse | 129 | 5 756 | **38** | 8 % |
| *Besetzung* | investissement | 25 | 514 | **14** | 53 % |
| *Verdrängung* | refoulement | 47 | 3 280 | **9** | 4 % |
| *Übertragung* | transfert | 19 | 748 | **5** | 6 % |

⚠ *Radical déclaré inutilisable : la charge entre parenthèses mesure l'échec de la recherche par radical, pas le terme. Voir §2.*

**Les deux extrêmes disent la même chose sous deux formes.** *Verdrängung* est le terme le plus propre du corpus — le radical ouvre presque toujours le mot, la famille est courte, et « refoulement » tient sans réserve. *Besetzung* est l'inverse : plus de la moitié de ses occurrences sont dans un composé (Objektbesetzung, Gegenbesetzung, Überbesetzung), et le mot français doit survivre à la composition — ce qu'il fait mal.

---

## 2. Les faux amis — mesurés, déclarés, jamais devinés

Chercher un terme par son radical attrape des mots qui n'ont rien à voir. C'est le défaut que le lexique du projet a déjà payé : `\bschwan` attrapait **`schwanger`** — enceinte — 65 fois chez l'auteur dont la thèse centrale est la naissance, soit 28 % de captures fausses. Les faux amis sont donc DÉCLARÉS et comptés.

| Terme | Ce que le radical attrape en trop | Occurrences | Contamination |
|---|---|---:|---:|
| *Lust* | `verlust`, `lustig`, `geluste`, `lustigen` | 394 | **11,1 %** |
| *Angst* | `langst`, `unlangst` | 373 | **6,1 %** |
| *Trieb* | `ubertriebene`, `ubertriebenen`, `ubertrieben`, `betrieb` | 208 | **5,3 %** |
| *Traum* | `trauma`, `traumatischen`, `traumatische`, `geburtstraumas` | 868 | **4,4 %** |
| *Übertragung* | `gedankenubertragung` | 16 | **2,1 %** |

Deux termes n'ont **aucun** faux ami mesuré : *Verdrängung*, *Besetzung*. Quand un terme se comporte ainsi, la charge de traduction est celle de la composition seule.

### Le cas qui montre la limite de la méthode

Le radical `ich` est **inutilisable**, et il est le seul du tableau à être déclaré tel. Douze faux amis suffisent à en écarter **40,4 %** — `sich`, `nicht`, `mich`, `nichts`, `vielleicht` — et il en resterait des centaines : ce chiffre est un plancher, pas un total. C'est pourquoi il ne figure dans aucun classement de ce document : il mesurerait l'échec de la recherche par radical, pas le terme *Ich*.

Le lexique du projet ne s'y risque pas — `lexique._RE_ICH_MOI` cherche « das Ich », « Ich-Ideal », « Ichs », « des Ichs », jamais le radical nu. Certains termes ne se cherchent pas par leur radical du tout, et aucune mesure de charge ne le dirait : il faut le savoir avant de mesurer.

---

## 3. Terme par terme — et les refus

### *Angst* → « angoisse »

129 formes, 5 756 occurrences, charge **38**. Formes principales : `angst` (2 706), `angstneurose` (651), `angsthysterie` (210), `angstzustande` (140), `angstlich` (97), `angstanfall` (85), `angstliche` (75), `angstlichkeit` (75).

Composés où le radical n'ouvre pas le mot : `kastrationsangst` (65), `todesangst` (50), `platzangst` (42), `realangst` (41), `gewissensangst` (26), `urangst` (25).

**Note.** « Angst » se rend tantôt par « angoisse », tantôt par « peur », et le corpus ne peut pas trancher entre les deux — il peut seulement montrer les contextes. Le faux ami `längst` (« depuis longtemps ») n'a aucun rapport avec le terme et n'est séparé de lui par aucune frontière de mot : seule une déclaration explicite l'écarte.

### *Besetzung* → « investissement »

25 formes, 514 occurrences, charge **14**. Formes principales : `besetzung` (156), `besetzungen` (49), `objektbesetzungen` (49), `objektbesetzung` (46), `gegenbesetzung` (42), `libidobesetzung` (34), `besetzungsenergie` (20), `uberbesetzung` (18).

Composés où le radical n'ouvre pas le mot : `objektbesetzungen` (49), `objektbesetzung` (46), `gegenbesetzung` (42), `libidobesetzung` (34), `uberbesetzung` (18), `energiebesetzung` (14).

**Note.** CAS INVERSE ET LE PLUS INSTRUCTIF : c'est le terme dont la plus grande part des emplois a le radical À L'INTÉRIEUR d'un composé (Objektbesetzung, Gegenbesetzung, Libidobesetzung, Überbesetzung) — voir la colonne « radical interne ». Le mot français doit donc survivre à la composition, ce qu'il fait mal : « contre-investissement » passe, « investissement d'objet » s'alourdit.

### *Ich* → « moi »

2 761 formes, 107 369 occurrences, charge **902**. Formes principales : `ich` (28 922), `naturlich` (977), `namlich` (905), `endlich` (822), `wahrscheinlich` (732), `plotzlich` (725), `ahnlich` (706), `schliesslich` (688).

Composés où le radical n'ouvre pas le mot : `naturlich` (977), `namlich` (905), `endlich` (822), `wahrscheinlich` (732), `plotzlich` (725), `ahnlich` (706).

**Note.** LE RADICAL EST INUTILISABLE : la contamination mesurée dans le tableau ci-dessus est un PLANCHER, obtenu en ne déclarant que douze faux amis là où il y en a des centaines. Le lexique du projet ne s'y risque pas — `lexique._RE_ICH_MOI` cherche « das Ich », « Ich-Ideal », « Ichs », « des Ichs ». C'est le cas qui montre que la charge de traduction n'est pas seulement lexicale : certains termes ne se cherchent pas par leur radical du tout.

### *Lust* → « plaisir »

158 formes, 3 144 occurrences, charge **79**. Formes principales : `lust` (966), `unlust` (234), `schaulust` (88), `lustprinzip` (80), `lustprinzips` (80), `lustgewinn` (71), `vorlust` (70), `lustvolle` (51).

Composés où le radical n'ouvre pas le mot : `unlust` (234), `schaulust` (88), `vorlust` (70), `wollust` (47), `illustrieren` (39), `illustration` (39).

**Note.** `Verlust` est LA PERTE, exactement le contraire du plaisir, et le radical l'attrape. `Unlust` en revanche appartient bien à la famille — c'est le déplaisir freudien, second terme du couple Lust/Unlust.

### *Traum* → « rêve »

304 formes, 18 739 occurrences, charge **46**. Formes principales : `traum` (4 996), `traume` (3 993), `traumes` (1 609), `traumen` (1 233), `traumdeutung` (570), `traumgedanken` (532), `traumer` (511), `traumarbeit` (351).

Composés où le radical n'ouvre pas le mot : `getraumt` (253), `tagtraume` (71), `angsttraum` (64), `angsttraume` (58), `tagtraumen` (34), `tagtraum` (33).

**Note.** LE FAUX AMI LE PLUS COÛTEUX DU CORPUS : chercher `traum` attrape `Trauma`, c'est-à-dire que le rêve avale le traumatisme — et donc tout le vocabulaire du livre de 1924 de Rank. Chez Le Bon, « rêve » est métaphorique (« les rêves de nos pères ») et `MOTIFS_FR` refuse de le rattacher à `Traum`.

### *Trieb* → « pulsion »

146 formes, 3 692 occurrences, charge **66**. Formes principales : `triebe` (585), `trieb` (421), `trieben` (170), `triebregungen` (160), `triebes` (121), `getrieben` (113), `triebleben` (113), `sexualtrieb` (106).

Composés où le radical n'ouvre pas le mot : `getrieben` (113), `sexualtrieb` (106), `sexualtriebes` (93), `sexualtriebe` (90), `antrieb` (61), `geschlechtstriebes` (61).

**Note.** « Instinkt » et « Trieb » sont deux mots distincts en allemand, et Le Bon écrit « instinct » en 1895 sans rien devoir à Freud : `lexique.MOTIFS_FR` REFUSE explicitement de les apparier. Les formes verbales de `treiben` (getrieben, Antrieb) sont laissées dans la famille — elles sont de la même racine, et les retirer serait trancher une question de morphologie que le corpus ne pose pas.

### *Verdrängung* → « refoulement »

47 formes, 3 280 occurrences, charge **9**. Formes principales : `verdrangung` (1 398), `verdrangten` (624), `verdrangte` (324), `verdrangt` (243), `verdrangungen` (111), `verdrangter` (93), `verdrangen` (79), `sexualverdrangung` (52).

Composés où le radical n'ouvre pas le mot : `sexualverdrangung` (52), `urverdrangung` (36), `triebverdrangung` (12), `unverdrangten` (5), `partialverdrangung` (5), `unverdrangt` (4).

**Note.** Le terme le plus PROPRE du corpus : le radical ouvre presque toujours le mot, la famille est courte, et aucun faux ami n'a été trouvé. Quand un terme se comporte ainsi, la charge de traduction est faible et le mot français unique tient sans réserve particulière.

### *Übertragung* → « transfert »

19 formes, 748 occurrences, charge **5**. Formes principales : `ubertragung` (556), `ubertragungsneurosen` (54), `ubertragungen` (34), `gegenubertragung` (16), `ubertragungsliebe` (15), `sexualubertragung` (12), `ubertragungsneurose` (10), `ubertragungs` (7).

Composés où le radical n'ouvre pas le mot : `gegenubertragung` (16), `sexualubertragung` (12), `liebesubertragung` (7), `affektubertragung` (6), `vaterubertragung` (3).

**Note.** `Gedankenübertragung` est la TRANSMISSION DE PENSÉE — la télépathie, sujet réel chez Freud et Ferenczi — et non le transfert analytique. Le composé est déclaré faux ami parce que le français emploie deux mots là où l'allemand en emploie un.

### Les correspondances REFUSÉES

Un refus argumenté est le seul énoncé qu'un corpus de 1 485 atomes français puisse produire sur une traduction — et il vaut mieux qu'une correspondance plausible. Ceux-ci vivent dans `lexique.MOTIFS_FR` et gouvernent réellement la mesure : le concept correspondant n'est pas mesuré sur le texte français, il reste non qualifié plutôt qu'approximé.

| Français | ≠ Allemand | Pourquoi |
|---|---|---|
| « instinct » | *Trieb* | La distinction Trieb/Instinkt est un débat de traduction connu, et « l'instinct des foules » de Le Bon en 1895 n'est pas la pulsion freudienne. |
| « rêve » | *Traum* | Chez Le Bon le mot est métaphorique (« les rêves de nos pères »), jamais l'objet théorique de la Traumdeutung. |
| « illusion » | *Wahn* | Le délire n'est pas l'illusion. Le chapitre « Les illusions » de Le Bon traite des croyances collectives, pas de la psychose. |
| « état » | *Staat* | Replié sans majuscule, « l'État » se confond avec « l'état mental » — l'ambiguïté est créée par le pliage, pas par la langue. |

---

## 4. Ce que ce document ne dit pas

Ce document NE JUGE AUCUNE TRADUCTION. Décider que « pulsion » rend bien Trieb demande une compétence de traducteur et une histoire des traductions ; le corpus n'a ni l'une ni l'autre. La colonne « français courant » est une donnée EXTÉRIEURE au corpus, donnée pour être confrontée et non validée. Ce qui est mesuré, c'est la CHARGE : le nombre de formes allemandes distinctes qu'un mot français unique doit couvrir, l'allemand composant là où le français juxtapose. Les FAUX AMIS sont déclarés et comptés, jamais détectés : chercher un terme par son radical attrape `Verlust` pour `Lust`, `längst` pour `Angst`, `Trauma` pour `Traum` — et pour `ich`, 40,4 % des occurrences sont `sich`, `nicht`, `mich`. C'est le même défaut que `\bschwan` attrapant `schwanger` dans le lexique de Rank, mesuré à 28 % de captures fausses. Enfin, LE CORPUS N'A QU'UNE ANCRE BILINGUE — Gustave Le Bon, 1 485 atomes, 1895, et il n'est pas psychanalyste. Les seuls énoncés solides qu'on puisse en tirer sont des REFUS de correspondance, pas des validations.

*Reproduire : `python bin/generer_traduction.py` · la table des motifs français : `core/lexique.py:MOTIFS_FR` · l'usage comparé des mots : `SOCLE_COMMUN.md` §2.*
