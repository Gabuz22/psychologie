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

## 5. Ce qui reste à faire, et qu'il faut dire

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

Ce qui manque est nommé, et c'est un chantier à part entière — le même que ceux qui ont suivi
l'entrée de Rank (« audit du lexique, comme les sept audits de Freud ») et celle d'Abraham :

1. **Un audit adversarial du lexique**, sur le modèle de celui de Ferenczi : proposer les
   sous-concepts, puis les faire casser — recompter, afficher quinze contextes, chercher le mot
   allemand qui commence pareil et n'a rien à voir. Pour Ferenczi : 127 proposés, 88 gardés,
   30 corrigés, 9 retirés.
2. **Les volumes d'après 1920**, qui porteraient `parapathie` et la doctrine d'après la rupture.
   La série *Störungen des Trieb- und Affektlebens* est numérisée et libre de droits.
3. **Les motifs de chapitre**, non encore relevés pour ces six volumes.
