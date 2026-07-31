# Wilhelm Stekel — l'intégration, et ce qu'elle a coûté

Cinquième auteur traité pour lui-même, entré le 2026-07-31. L'inventaire préalable est dans
[STEKEL_INVENTAIRE.md](STEKEL_INVENTAIRE.md) ; ce document dit ce qui s'est passé quand on l'a fait.

---

## 1. Pourquoi lui, et pourquoi maintenant

**Ce n'est pas une intuition d'histoire des idées, c'est une mesure.** 54 atomes du corpus le
nommaient déjà — 22 de Freud dont **16 dans la seule *Traumdeutung***, 15 de Rank, 10 d'Abraham,
7 de Ferenczi — sans qu'on puisse jamais montrer l'autre côté. Freud y salue « die reichste
Sammlung von Symbolauflösungen » et refuse dans le même mouvement d'en généraliser le principe.
Le corpus tenait la critique sans la thèse critiquée.

Il apporte en outre la **quatrième forme du rapport au maître**, celle qui manquait :

| | ce qu'il fait |
|---|---|
| Otto Rank | déplace une thèse, puis rompt |
| Karl Abraham | prolonge, et ne rompt jamais |
| Sándor Ferenczi | reste vingt ans le plus proche, diverge sur la **technique** |
| **Wilhelm Stekel** | **rompt le premier (1912), et sur la doctrine** |

Et cette rupture est **datée dans le corpus, des deux côtés, avant qu'elle ait lieu** :

> **Stekel, 1907** — « Und derjenige, der mir diesen Weg gezeigt hat … ist der große Seelenkenner
> Professor Sigmund Freud. Ich bekenne mich stolz als seinen Schüler, womit ich nicht sagen will,
> daß Alles, was ich ausführe, seinen Anschauungen entspricht. **Im Gegenteil!** »
>
> **Freud, 1908**, préfaçant le livre suivant — « … so scheint es doch billig, daß ich ausdrücklich
> erkläre, **mein direkter Einfluß auf das vorliegende Buch … sei ein sehr geringer gewesen**. Die
> Beobachtungen und alle Einzelheiten der Auffassung und Deutung sind sein Eigentum; **nur die
> Bezeichnung „Angsthysterie" geht auf meinen Vorschlag zurück**. »

Cette préface **entre dans le corpus par la porte de Stekel** : c'est un texte de Freud que le
corpus freudien ne contenait pas. Elle est déclarée en `contributions` et attribuée à son auteur
réel — sans quoi le corpus aurait prêté à Stekel une page où Freud parle de lui à la troisième
personne, exactement le défaut décelé jadis dans l'appendice de Rank à la *Traumdeutung*.

---

## 2. Les six volumes, et le seul écarté

Aucune transcription relue n'existe pour Stekel — ni Wikisource, ni Gutenberg allemand, ni le
Deutsches Textarchiv. C'est fac-similé océrisé ou rien, comme pour Rank, Abraham et Ferenczi.

| œuvre | année | signes | phrases atteintes |
|---|---|---:|---:|
| *Die Ursachen der Nervosität* | 1907 | 90 393 | 0,0 % |
| *Nervöse Angstzustände und ihre Behandlung* | 1908 | 1 068 884 | 0,0 % |
| *Dichtung und Neurose* | 1909 | 185 691 | 0,0 % |
| *Die Sprache des Traumes* | 1911 | 1 716 760 | 0,2 % |
| *Die Träume der Dichter* | 1912 | 824 143 | 0,1 % |
| *Onanie und Homosexualität* | 1917 | 1 355 219 | 0,0 % |

Le seuil de rejet est de 2,0 % de phrases atteintes : les six sont **au niveau des transcriptions
relues**. Total 5,24 millions de signes — le troisième corpus du projet.

**Recouvrement mesuré**, en suites de huit mots : un seul couple dépasse 2 %, *Ursachen* ×
*Angstzustände* à **8,9 %**, concentré entre 40 % et 70 % du plus petit. C'est de l'auto-reprise
entre deux livres proches — un an d'écart, même sujet —, non une réimpression : les trois volumes
de Ferenczi écartés pour duplication étaient à 46 %, 56 % et 46 %. Les deux sont donc gardés.

---

## 3. Un défaut de corpus trouvé en chemin : le bandeau Google

Deux de ces volumes viennent de scans Google, qui déposent **« Digitized by Google » au bas de
chaque page** — non pas en tête de fichier, mais **au milieu des phrases** coupées par le saut de
page. Mesuré : **2,2 % et 3,2 % des phrases** en portaient un.

Le défaut se voit surtout à sa conséquence. Dans la première mesure du vocabulaire distinctif de
Stekel, faite pour construire son lexique, le mot **`google` arrivait en troisième position**
(650 occurrences contre 4 dans tout le reste du corpus), devant `onanie`. Un lexique construit sur
cette mesure aurait donné à Stekel un vocabulaire signature de bibliothécaire numérique.

Le nettoyage est générique (`ocr.retirer_bandeau_scan`) et son critère est un **anachronisme**, ce
qui le rend décidable sans jamais lire le contexte : aucun texte allemand de 1907-1917 ne contient
le mot « Google ». Les vingt-huit formes que l'OCR en donne ont été relevées, non supposées —
« Digitized by Google » (217 fois) mais aussi « (iby Google » (346), « dhyGoogle », « chyGoogle »,
« DigilizeilbyGoOgle », « DiriitizedhyGoOgle ». **1 006 bandeaux retirés, zéro reste sur tout le
corpus.**

---

## 4. Son lexique, et ce qu'il ne contient pas

Construit sur SON vocabulaire, mesuré contre les 1 231 000 mots des autres auteurs allemands.
Rapports de fréquences relatives :

| motif | chez lui | ailleurs | rapport |
|---|---:|---:|---:|
| `onani*` | 1 441 | 295 | **×15,2** |
| `bipolar` | 39 | 2 | **×40,7** |
| `bisexuell` | 145 | 34 | ×13,0 |
| `heterosexuell` | 199 | 51 | ×12,0 |
| `homosexuell` | 883 | 283 | ×9,7 |
| `angsthysteri` | 189 | 61 | ×9,5 |
| `angstneuros` | 434 | 241 | ×5,6 |
| `verbrech` | 302 | 258 | ×3,6 |

`bipolar` est son concept théorique propre : « Alles seelische Geschehen wird von dem Gesetze der
„Bipolarität" beherrscht » est la **première phrase** de *Die Sprache des Traumes*.

**Ce que le lexique NE contient PAS, et pourquoi — mesuré, non supposé :**

- **`parapathie`, 5 occurrences.** C'est pourtant son néologisme le plus connu — il rebaptise ainsi
  la névrose. Mais il l'impose après 1920, et le corpus s'arrête en 1917. Le concept est absent du
  corpus, pas de l'auteur.
- **`aktualneurose`, 2 occurrences chez lui contre 35 ailleurs (rapport 0,2).** C'est l'un des deux
  points doctrinaux de la rupture de 1912 — et **le corpus montre que la querelle ne se lit pas
  dans ce mot chez lui**. Fait mesuré, contraire à l'attente.
- `skopophilie` et `lebensangst` : 0 occurrence. `zwang` : rapport 0,7, moins fréquent chez lui
  qu'ailleurs. `psychosexuell` : 2 contre 115.

**Un piège évité, le même que chez Freud :** le motif `traum` nu attrape `trauma`, `traumatisch`,
`Traumatismus`. La garde `traum(?!a)` est indispensable chez un auteur dont `traum` est le mot le
plus fréquent après les outils grammaticaux (2 098 occurrences).

---

## 5. L'audit contradictoire — fait le 2026-07-31

Onze contradicteurs ont éprouvé les 62 sous-concepts, avec pour consigne de les **casser** : les
recompter, lire vingt contextes chacun, chercher le mot allemand qui commence pareil et n'a rien à
voir. Le bilan, comparé à celui de Ferenczi :

| | Stekel | Ferenczi |
|---|---|---|
| gardés | 30 (48 %) | 88 (69 %) |
| corrigés | 19 (31 %) | 30 (24 %) |
| **retirés** | **13 (21 %)** | 9 (7 %) |

**Le taux de retrait est trois fois celui de Ferenczi.** Ce n'est pas une mesure sur Stekel, c'est
une mesure sur la façon dont ce lexique a été écrit : d'un jet, sans audit préalable. Le chiffre
est publié tel quel. Le lexique passe de 62 sous-concepts et 177 motifs à **49 et 125**.

### Les deux retraits qui valent pour toute la méthode

Les deux sous-concepts que l'en-tête du lexique citait comme **les plus propres à Stekel** sont
ceux que l'audit a tués — et pour la même raison :

- **`rundfrage`** : 56 de ses 64 occurrences (87,5 %) sont la **tête courante** de *Die Träume der
  Dichter*, imprimée en haut de chaque page. Huit usages réels.
- **`berufsneurose`** : 24 de ses 30 atomes (80 %) sont du paratexte — 18 têtes courantes,
  3 titres, 3 lignes de sommaire. **Six** usages réels.

Ils paraissaient convaincants pour une raison précise : leur compte était élevé chez lui et **nul
chez les autres**. C'est exactement la signature d'une tête courante — personne d'autre n'imprime
ce titre de chapitre en haut de ses pages. Le projet s'était déjà fait prendre à l'identique avec
`genitaltheorie` chez Ferenczi, dont 50 des 83 occurrences étaient une tête courante.

### Deux concepts qui n'étaient pas de lui

- **`ambivalenz` : 0 occurrence sur 5 222 046 signes**, contre 269 chez les autres. C'est le mot de
  **Bleuler**, que Stekel cite quinze fois sans jamais reprendre son concept.
- **`schuldgefuehl`** : renversement mesuré. « Schuldgefühl » est le mot de Rank et de Freud
  (Stekel ×0,28, 4ᵉ sur 5) ; « Schuldbewusstsein » est le sien (×2,23, **1ᵉʳ sur 5**) — et c'est
  bien le terme de sa thèse : *« Das Schuldbewußtsein ist die hauptsächlichste Ursache aller
  Neurosen und Psychosen. »* Additionnés, les deux donnaient ×0,67 et faisaient échouer le
  sous-concept ; séparés, l'un le porte et l'autre le noyait.

### Trois fautes de ma main, du même type

- **Trois motifs morts** — `angstgefühl`, `nervosität`, `schuldgefühl` : ils portent un tréma, et
  le lexique s'applique après un repli qui **supprime les diacritiques**. Zéro déclenchement
  possible, sur 21,8 millions de signes. La même faute écrite trois fois.
- **Une garde trop large** : `traum(?!a)` écartait bien `Trauma`, mais aussi 74 mots du **rêve** —
  *Traumanalyse*, *Traumarbeit*, *Traumanlaß*. En évitant un faux positif connu, on perdait le
  vocabulaire technique de l'auteur du *Langage du rêve*. La garde nomme maintenant ce qu'elle
  exclut : +51 atomes.
- **Un motif ouvert du mauvais côté** : `onani` manquait *kinderonanie*, *säuglingsonanie*,
  *notonanie*, parce que le moteur borde chaque motif à gauche.

### Deux motifs indécidables par construction

Trouvés hors audit, en mesurant moi-même les deux groupes dont les contradicteurs n'ont pas rendu :

- **`see`** (lac) coûtait 609 atomes, **dont 590 sont l'âme** : *Seele* (255), *seelisch\** (130),
  *Seelenleben* (35), *Seelenarzt* (22) — contre 19 vrais lacs. Dans un corpus de psychologie, un
  motif qui attrape « Seele » ne mesure pas ce qu'il prétend, il mesure le sujet du livre.
- **`weg`** attrapait *wegen* 240 fois. Mais le vrai problème est plus profond : le repli
  **supprime les majuscules**, et l'allemand ne distingue le substantif *Weg* (le chemin, symbole
  onirique) de l'adverbe *weg* (parti) que par elle. Le motif était indécidable, pas seulement
  imprécis.

### Ce que l'audit a fait au taux de qualification — et pourquoi c'est une bonne nouvelle

**Il l'a fait BAISSER** : de 52 % à 46 % sur *Ursachen der Nervosität*, de 61 % à 57 % sur
*Dichtung und Neurose*. C'est le résultat correct, et il faut le lire à l'endroit : les atomes
perdus étaient qualifiés **à tort** — par « Mädchen » désignant une femme adulte, par « Seele »
comptée comme un lac, par une tête courante répétée en haut de chaque page.

**Le taux de qualification n'est donc pas un objectif à maximiser.** Un lexique large et fautif le
fait monter ; un lexique juste peut le faire descendre. C'est la première fois que le projet le
mesure dans ce sens, et cela vaut rétroactivement pour les autres auteurs : leurs 81-84 % n'ont de
valeur que parce qu'ils ont passé le même genre d'audit.

---

## 6. Ce qui reste à faire, et qu'il faut dire

**Le taux de qualification est de 52 à 61 % selon le volume, contre 81 à 84 % pour les cinq autres
auteurs du corpus.** Le lexique de Stekel est jeune : 8 groupes, 41 sous-concepts et 5 fonctions au
départ, portés à **11 groupes, 62 sous-concepts, 177 motifs et 13 fonctions** en deux passes de
mesure — là où celui de Ferenczi compte 129 sous-concepts et celui de Freud 177, chacun après
plusieurs audits successifs.

La progression, mesurée volume par volume, dit d'où venait le déficit : 26 % au premier jet,
33 % après l'ajout des fonctions rhétoriques génériques, **52 à 61 % après l'ajout des concepts
manquants** — dont `traum` lui-même, absent du premier lexique de l'auteur du *Langage du rêve*.

**Cet écart n'est pas une estimation, c'est le chiffre publié**, et il doit être lu comme tel :
sur ce corpus-là, une part plus grande des phrases n'est rattachée à aucun concept ni à aucune
fonction. Les mesures de densité sur Stekel sont donc moins comparables à celles des autres auteurs
qu'elles ne le paraissent.

Ce qui manque est nommé :

1. ~~**Un audit adversarial du lexique**~~ — **FAIT le 2026-07-31**, voir § 5.
2. ~~**Deux groupes n'ont pas reçu de verdict**~~ — **FAIT le 2026-07-31 (second passage)**, voir § 7.
3. **Les volumes d'après 1920**, qui porteraient `parapathie` et la doctrine d'après la rupture.
   La série *Störungen des Trieb- und Affektlebens* est numérisée et libre de droits.
4. **Les motifs de chapitre**, non encore relevés pour ces six volumes — d'autant plus utile que
   l'audit vient de montrer combien de têtes courantes subsistent dans ces scans.
5. ~~**`angsthysterie`**~~ — **INSTRUIT le 2026-08-01**, voir § 8. Gardé : les 43 % de paratexte
   sont réels, mais 106 usages réels subsistent et le rapport corrigé reste à ×5,7.
6. **`angstneurose` dans le même volume** : 46 atomes ouvrent par `die angstneurose.` — la tête
   courante de la partie I, exactement le même mécanisme, jamais mesuré. **Signalé, non traité.**
7. **Rien ne retire les têtes courantes page à page.** `PARATEXTE_FINAL` et `REGIONS_ECARTEES`
   coupent aux extrémités ; le milieu du volume n'a aucun traitement. C'est le défaut de fond
   derrière les points 5 et 6, et il ne se corrigera pas sous-concept par sous-concept.

---

## 8. `angsthysterie` — l'alerte de la machine, instruite

Le détecteur de concentration ajouté au § 7.5 a signalé, dans un groupe **déjà audité**, ce qui
ressemblait au piège pour la quatrième fois : `angsthysterie`, **43 % de paratexte, 88 % dans un
seul volume**. Les 184 atomes ont été lus un par un.

**Les 43 % sont RÉELS.** *Nervöse Angstzustände* est en deux parties, et la partie II a pour tête
courante verso **« ZWEITER TEIL: DIE ANGSTHYSTERIE. »**, dont l'OCR ne garde souvent que la queue,
soudée en tête d'atome : **61 atomes ouvrent littéralement par `die angsthysterie.`** suivi d'un
fragment qui ne redémarre pas — `'die angsthysterie. ursachte.'` (28 signes en tout). Les têtes
courantes recto atterrissent, elles, en plein milieu de phrase avec leur folio : `'…die frau
analyse einer angsthysterie mit obsession. 141 gestorben.'`

| | brut | corrigé du paratexte |
|---|---|---|
| atomes | 184 | **106** |
| propres | 62 | **21** |
| rapport | ×9,79 | **≈ ×5,7** |
| un seul volume | 88 % | **78 %** |

**Verdict : GARDE.** Ce n'est pas `keller`. La concentration est **légitime** — c'est le livre de
Stekel sur l'angoisse —, 23 atomes réels vivent hors de ce volume, et le rapport corrigé reste très
au-dessus de 1. Aucun motif de remplacement n'est possible, et c'est mesuré : la tête courante *est*
le mot lui-même. Le seul motif propre à 100 % (`angsthysterien|angsthysterik|angsthysterisch`)
tombe à 27 atomes et perd **75 % des usages réels**. Le remède serait pire que le mal.

Détail qui tranche : **la tête courante ne dit jamais que le singulier.** Les 22 `angsthysterien`,
4 `angsthysteriker` et 1 `angsthysterische` sont à 100 % de l'usage réel.

Note historique, vérifiée au passage : la déclaration de Freud — « nur die Bezeichnung
„Angsthysterie" geht auf meinen Vorschlag zurück » — est dans la préface, correctement attribuée à
**Freud** par l'atomiseur. Elle ne pèse donc pas dans les 184 atomes de Stekel et survit intacte à
toute décision prise ici.

### Le détecteur passe sa première épreuve en solo

C'est le premier cas qu'il signale **seul**, sans qu'un lecteur l'ait vu d'abord. Mesuré contre la
lecture des 184 atomes :

| | |
|---|---|
| précision | **95 %** (76 justes sur 80 signalés) |
| rappel | **97 %** (76 sur 78 vrais paratextes) |
| annoncé 43 % / réel 42 % | l'écart « plancher » se vérifie, et il est minuscule ici |

**Et il ne faut pas durcir le seuil**, contrairement à ce qu'on pouvait craindre. Les 4 faux
positifs viennent bien de la règle du nombre nu appliquée à un livre clinique plein de nombres
légitimes (« eine 32 Jahre alte … Patientin »). Mais cette même règle attrape **15 vrais paratextes
qu'elle seule peut voir** — les têtes courantes recto, qui atterrissent en plein milieu de phrase et
qu'aucune règle d'ouverture ne détecte. La durcir sacrifierait 15 prises justes pour éviter 3
fausses.

Les deux améliorations utiles sont ailleurs, et elles sont notées plutôt que faites : tolérer la
déformation OCR dans les ouvertures répétées (distance d'édition sur les deux premiers mots), et
accepter le chiffre romain comme folio.

---

## 7. Le second passage — les deux groupes manquants, 2026-07-31

Sept contradicteurs sur les douze sous-concepts de `traumbilder` et `neurose`. **Aucun groupe n'est
tombé ; le lexique passe de 49 à 50 sous-concepts et de 125 à 155 motifs.** Mais ce passage a
rapporté davantage en méthode qu'en verdicts, et sur trois points il a corrigé le premier audit.

### 7.1 Ce que les motifs ramenaient vraiment

| sous-concept | verdict | le chiffre |
|---|---|---|
| `raum` | corrige, **−390 atomes** | `dachboden` = **0 occurrence** ; `keller` = 55 % dans *Die Träume der Dichter*, 18 atomes nommant **Gottfried ou Paul Keller, les écrivains** ; `haus` = 175 « nach/zu Hause » adverbiaux sur 344 ; `tur` = 69 occurrences de *Turm*, *Turner*, *Türke* sur 227 |
| `koerperbild` | corrige, −289 | `genital` ×0,43 (vocabulaire du champ) ; `brust` à la ligne de base, dont `Brüstung` = le parapet et ~40 % d'idiome « in der Brust », siège du sentiment |
| `tier` | corrige, −36 | `hund` attrape **`hundert`**, le nombre (25 occ.) ; `katze` attrape *Katzenjammer* et *Katzensteg* (12 sur 45) |
| `tod_bild` | corrige, **+17** | `grab` attrape **Grabbe le poète**, **der Graben la rue de Vienne** et le proverbe « wer andern eine Grube gräbt » ; à l'inverse `begrabnis` ratait `begraben` — 46 occurrences contre 9 |
| `sterben` | corrige, **+284** | **deux motifs sur cinq à zéro atome** : `todes` ⊂ `tod`, `sterben` ⊂ `sterbe` — 33 % du compte affiché était fictif |
| `symptom` | corrige, +23 | le bordage à gauche ratait 27 composés (*krankheitssymptome*, *angstsymptome*, *hauptsymptom*…) |
| `selbstmord` | garde | `freitod` = 0 occurrence, mot **postérieur au corpus** |
| `wasser`, `weg`, `neurose`, `hysterie`, `verdraengung` | **gardés** | voir 7.3 |

Le rapport de `raum` **monte** en perdant un quart de ses atomes (×3,18 → ×3,23) et celui de
`koerperbild` passe de ×1,65 à **×4,30** : ce qui part est du bruit, et c'est la meilleure preuve
qu'on puisse en donner.

**Qualification : 54,0 % → 53,7 %.** Plate. Retraits et vocabulaire récupéré se compensent.

### 7.2 Deux hypothèses de départ RÉFUTÉES par la lecture

Elles avaient été fournies aux contradicteurs comme des pistes ; les mesurer était le travail.

- **`fluss` attraperait « flüssig »** — faux. Sur les 26 occurrences de la famille, **21 sont le
  liquide lu comme symbole onirique** : « diese Gleichung nimmt alle Flüssigkeiten auf: Milch, Öl,
  Petroleum, Tränen », « eine weisse, seifenartige Flüssigkeit … als phallisches Symbol ». Dans un
  dictionnaire où l'eau EST l'urine et le sperme, ce n'est pas du bruit, c'est le concept. Une
  garde aurait coûté 19 atomes légitimes pour en retirer 6.
- **`penis`/`vagina` seraient de la clinique mal rangée** — faux. 73 % et 83 % sont dans *Die
  Sprache des Traumes* (base : 37 %), contre 23 % pour le témoin clinique `koitus` ; et Stekel les
  déclare lui-même symboles **41 fois**.

Une réserve mesurée mais **non appliquée** est écrite dans le lexique : sur les tournures de
symbolisation, `koerperbild` est 12 fois du côté de l'IMAGE contre 52 du côté du SENS, quand les
images vraies du groupe sont 15 contre 1 — « Die Stiege symbolisiert die Vagina ». Ce sous-concept
relèverait de `traumsprache`. Déplacer recompose les grappes : mesuré ici, à décider ailleurs.

### 7.3 Le premier audit s'était trompé de règle, et deux retraits sont infondés

Quatre des six sous-concepts de `neurose` affichaient un rapport < 1 — le critère qui avait servi à
retirer cinq sous-concepts. **Aucun des quatre n'est tombé.** Appliqué mécaniquement, ce critère
retirerait `neurose` et `hysterie` du lexique de l'homme qui sous-titre un livre *Die homosexuelle
Neurose*. Les huit cas ont été repris (voir la note « LE RAPPORT < 1 » dans `core/lexiques/stekel.py`) :

- **`phobie` a été retiré à tort** : le ×0,70 mesurait un **motif incomplet**, pas le concept. Ses
  phobies propres — `nosophob` 12 contre **0** au témoin, `platzangst` ×12,3 — étaient hors
  d'atteinte du bordage. Motif complété : **×1,42**. Rétabli.
- **`wunsch` a été retiré sur le seul rapport**, sans terme rival : infondé par la règle même.
- **`hysterie` ×0,30 mesure la bibliothèque de Freud** : 62 % de ses occurrences sont dans deux
  monographies de l'hystérie ; sans elles, ×0,54. En médiane par œuvre, Stekel est 3ᵉ sur 5,
  **au-dessus de Freud**.
- **Le piège du volume unique joue aussi sur le DÉNOMINATEUR** : 13 % des `neuros` de Freud sont
  *Neurosenlehre*, tête courante de trois de ses volumes.

**Règle retenue** : un rapport < 1 ne condamne que si (1) le motif couvre déjà la famille attestée,
**et** (2) il existe un rival *intra-corpus* dominant. Sans les deux, il se publie comme une mesure,
jamais comme un verdict.

### 7.4 La rupture de 1912 : la belle histoire est refusée

`verdraengung` ×0,54 et `symptom` ×0,39 semblaient dire que Stekel s'écarte de l'appareil freudien.
**C'est d'abord un artefact de composition** : 48,4 % de son corpus allemand sont ses deux livres de
rêve, où *tout* le registre clinique s'effondre ensemble (`verdrang` ×0,15, `symptom` ×0,11,
`hysteri` ×0,08) pendant que `traum` monte à ×3,03 — et le même effet se lit chez Freud, dont la
*Traumdeutung* est à 56,5 `verdrang`/Mc contre 212,6 dans ses *Sammlungen*. **Corrigé du genre**, sur
ses seuls volumes cliniques : `verdraengung` ×0,90, `symptom` ×0,65.

**Et il n'y a pas de cassure en 1912** : la courbe décroît de façon monotone dès 1907 (417 → 212 →
132 par million de signes), soit −68 % **cinq ans avant** la rupture.

Reste un fait qui n'est pas du bruit : de clinique à clinique (1908 → 1917), `verdrang` −57 %,
`symptom` −85 %, **et le nom « Freud » lui-même −57 %**, pendant que `sexual` tient (+8 %) et que
son vocabulaire propre apparaît (`bipolar` 0 → ×62,2). La direction est compatible avec une
divergence doctrinale — mais **le corpus ne contient qu'un seul volume post-rupture, sur un seul
sujet** : sujet et date sont inséparables. On ne conclut pas.

### 7.5 Trois défauts du BANC, trouvés par les contradicteurs

Le banc (`bin/eprouver_sous_concept.py`) a été écrit pour cet audit ; il en est ressorti corrigé
trois fois, ce qui vaut d'être écrit puisque ses chiffres ont servi à juger.

1. **La colonne « propres » ne mesurait pas ce qu'elle annonçait.** Elle lisait une clé
   `sous_concepts` **qui n'existe pas** sur un atome (les vraies clés sont `groupe` et `concept`) ;
   le `.get()` rendait sa valeur par défaut et la colonne comptait « atomes sans fonction ».
   Surestimation **×2,3** (`neurose` : 747 affichés, 307 réels). Cela vaut rétroactivement pour le
   premier audit, qui condamnait `madchen` en citant « 606 atomes, **597 propres** ».
2. **Les occurrences étaient comptées par MOTIF, non par mot.** Quand deux motifs d'un même
   sous-concept se recouvrent, le même mot comptait double — et le doublon se lisait dans la
   colonne « formes » sans qu'on le voie, tous les chiffres y étant exactement le double du réel.
3. **Le détecteur de paratexte est un plancher, jamais un plafond.** Il exige trois ouvertures
   identiques ; or l'OCR massacre les têtes courantes — « Todessymbolik » apparaît en **43
   orthographes distinctes**. Le banc en signale 2 sur ~23.

Un quatrième point n'est pas un défaut mais un ajout : après le cas `keller`, le banc mesure la
**répartition par volume**. C'est la forme *générale* du piège qui a pris le projet trois fois
(`genitaltheorie`, `rundfrage`/`berufsneurose`, `keller`) — un compte porté par un seul livre, et
d'autant plus convaincant qu'il est nul chez les autres, puisque personne d'autre n'a écrit ce
livre-là. `keller` n'était pas du paratexte : c'était un nom propre en pleine prose, invisible au
détecteur de tête courante. C'est cette mesure qui a ensuite trouvé `angsthysterie`.

### 7.6 L'angle mort du moteur, jamais généralisé

L'allemand met la tête du composé à la **fin** ; le moteur borde chaque motif au **début**. Un
mot-concept qui vit surtout en second élément est donc **invisible à son propre concept**. Trois
manifestations indépendantes dans ce seul audit : `phobie` (topophobie, erythrophobie, nosophobie),
`symptom` (27 composés), et les phobies composées `brustangst`/`eisenbahnangst`/`strassenangst`,
que le groupe `angst` ne pouvait pas voir.

La leçon avait été apprise **une fois**, pour `onani` → `[a-z]*onani`, et jamais étendue : c'était
le seul motif ouvert à gauche des cinq lexiques du dépôt. Elle ne peut pas l'être en aveugle —
`[a-z]*tier` attrape *konstatieren*, `[a-z]*angst` attrape **`längst`** (50 occurrences). L'ouverture
se justifie motif par motif, sur les composés attestés.
