# Wilhelm Stekel — inventaire avant acquisition

Quatrième figure de l'entourage prévue au plan (Rank → Abraham → Ferenczi → **Stekel**). Ce document
établit ce qui est **utilisable**, ce qui doit être **écarté**, et ce que son entrée révélerait
rétroactivement. Aucun texte n'a encore été acquis.

Deux registres se distinguent dans ce qui suit, et il importe de ne pas les confond:
**ce qui a été mesuré sur le dépôt** (§ 1 et § 2) et **ce qui a été relevé sur le web sans être
encore éprouvé** (§ 3). Le corpus a déjà été trompé par des chiffres non rejoués — voir
[CHAPITRAGE.md § 2](CHAPITRAGE.md) — et la règle vaut ici aussi : rien n'entre sans mesure locale.

---

## 1. Ce que le corpus actuel sait déjà de lui — mesuré

**54 atomes du corpus nomment Stekel**, sans qu'on puisse afficher l'autre côté. Compté par requête
directe sur `derive/d1/corpus.sqlite` :

| auteur | œuvre | atomes |
|---|---|---:|
| Sigmund Freud | *Die Traumdeutung* | 16 |
| Karl Abraham | *Klinische Beiträge zur Psychoanalyse* | 10 |
| Otto Rank | *Das Inzest-Motiv in Dichtung und Sage* | 8 |
| Otto Rank | *Das Trauma der Geburt* | 5 |
| Sándor Ferenczi | *Bausteine II* | 4 |
| Sándor Ferenczi | *Bausteine I* | 3 |
| Otto Rank | *Die Lohengrinsage* | 2 |
| Sigmund Freud | *Das Motiv der Kästchenwahl*, *Traum und Telepathie* | 2 + 2 |
| Sigmund Freud | *Leonardo*, *Totem und Tabu* | 1 + 1 |
| **total** | | **54** |

Les quatre auteurs déjà présents le discutent. C'est le meilleur argument de son entrée, et il ne
vient pas d'une intuition sur l'histoire de la psychanalyse mais du texte du corpus.

## 2. Un défaut de configuration déjà en place — mesuré

`stekel` figure dans `NOMS_AUTEURS` de `core/lexiques/abraham.py` et de `core/lexiques/ferenczi.py`,
et **pas** dans le dict `NOMS` de `core/comparaison.py`.

Ce n'est pas un bug : `NOMS` ne contient que les auteurs **du corpus**, et un test le garantit
(`test_tous_les_auteurs_du_corpus_ont_un_jeton`). Mais la conséquence doit être écrite avant qu'on
l'oublie : le jour où Stekel entre, **son jeton devra être ajouté à `NOMS` et le pipeline rejoué sur
les quatre auteurs déjà présents**, sans quoi ces 54 atomes resteront invisibles à la couche de
comparaison. C'est exactement l'oubli qui s'est produit pour Ferenczi — entré dans le corpus sans
que son nom entre dans la table des mentions, 16,8 % des atomes et aucun auteur enregistré comme le
nommant (voir le commentaire de `comparaison.NOMS`). Le test existe pour que cela ne se répète pas
en silence ; ce paragraphe existe pour qu'on n'ait pas à découvrir le travail après coup.

---

## 3. Éditions numérisées — relevé, NON éprouvé

**Aucune transcription relue n'existe pour Stekel**, vérification négative faite sur Wikisource
allemand, Project Gutenberg allemand, zeno.org et le Deutsches Textarchiv. C'est la situation de
Rank, d'Abraham et de Ferenczi : **fac-similé océrisé ou rien**.

Les candidats relevés sur Internet Archive, par ordre de rendement attendu pour le corpus :

| # | œuvre | année | identifiant archive.org |
|---|---|---|---|
| 1 | *Die Sprache des Traumes* | 1911 | `diesprachedestr00stekgoog` |
| 2 | *Nervöse Angstzustände und ihre Behandlung* | 1908 | `b21941774` |
| 3 | *Die Ursachen der Nervosität* | 1907 | `stekel-1907-ursachen` |
| 4 | *Dichtung und Neurose* | 1909 | `DichtungUndNeurose.BausteineZurPsychologieDesKnstlersUndDes` |
| 5 | *Die Träume der Dichter* | 1912 | `bub_gb_4xM1AQAAMAAJ` |
| 6 | *Onanie und Homosexualität* | 1917 | `bub_gb_lQ4_AQAAMAAJ` |

L'ordre n'est pas chronologique, et la raison est mesurée : **c'est *Die Sprache des Traumes* que le
corpus actuel nomme le plus** — les 16 atomes de la *Traumdeutung* la discutent, Freud y saluant « la
plus riche collection de résolutions symboliques » tout en refusant sa généralisation. L'entrée de ce
volume clôt une controverse dont le corpus ne tient aujourd'hui qu'un côté.

*Nervöse Angstzustände* (1908) porte une particularité : **une préface signée de Freud**
(« Wien, im März 1908, Prof. Freud »), retirée à la 3ᵉ édition de 1921. C'est un texte de Freud
absent du corpus, qui entrerait par le mécanisme `contributions` déjà éprouvé pour l'appendice de
Rank dans la *Traumdeutung* et pour les régions de Breuer dans les *Studien*.

### Ce qui n'est PAS établi et doit l'être avant tout chargement

- **La qualité OCR n'est mesurée pour aucun de ces six volumes.** Le seul signal disponible est
  qualitatif (« umlauts mal reconnus » sur un échantillon de 1908). Le taux de base observé chez Rank
  est de **deux volumes écartés sur neuf** pour corruption ; il faut s'attendre à ce qu'un ou deux
  de ces six échouent au seuil de 2 % de phrases atteintes. `core/ocr.py` tranchera, pas une
  impression de lecture.
- Les bornes (`debut_corps`, `PARATEXTE_FINAL`) et un motif de chapitre par volume restent à relever
  dans le texte, un par un, comme pour les dix-huit œuvres déjà déclarées.

---

## 4. Le droit

Stekel est mort le **25 juin 1940** à Londres. Ses œuvres allemandes sont dans le domaine public en
Allemagne et en Autriche depuis 2011 (vie + 70 ans), et toute sa production monographique allemande
est antérieure à 1931 — le seuil que le projet applique déjà à Freud.

Deux ensembles doivent être **écartés**, et pour deux motifs différents :

| écarté | motif |
|---|---|
| ***The Autobiography of Wilhelm Stekel*** (Liveright, New York, 1950) | Œuvre américaine de 1950, éditée et vraisemblablement traduite par Emil A. Gutheil (mort en 1959) : la couche éditoriale seule serait protégée jusqu'en 2029. Aucun original allemand publié n'a été retrouvé. Internet Archive la classe elle-même en `Access-restricted-item` — l'accès contrôlé est le signe qu'elle n'a pas établi le domaine public. **Même traitement que Lacan : écartée jusqu'à preuve du contraire.** |
| *Fortschritte der Sexualwissenschaft*, *Zentralblatt für Psychoanalyse*, *Psychotherapeutische Praxis* — les revues qu'il dirige | Obstacle de **structure**, non de droit : ce sont des publications à plusieurs voix, et le lexique du projet suit l'auteur du volume. Même raison qui a fait écarter le symposium *Zur Psychoanalyse der Kriegsneurosen* (voir `FAC_SIMILES_ECARTES`). |
| les traductions anglaises | Doctrine du projet : le texte original seulement. Elles portent en outre une couche de droits de traducteur distincte. |

Ces exclusions sont déclarées dans `sources.FAC_SIMILES_ECARTES` pour qu'elles ne soient pas
reproposées.

---

## 5. Le coût, à l'échelle des trois auteurs déjà intégrés

| poste | référence observée | pour Stekel |
|---|---|---|
| lexique propre | Rank 396 lignes, Abraham 336, Ferenczi 526 | ~350-500 — deux registres presque absents du corpus : la symbolique onirique systématique, et le catalogue des troubles sexuels |
| tests dédiés | 174 à 348 lignes | ~200-350 |
| motifs de chapitre | un par volume, relevé et rejoué | 5 à 6 |
| volume de texte | Rank 3,8 Mo / 7 œuvres | ~5-7 Mo pour les six titres |
| audit du lexique | 5 à 7 passes par auteur | à reproduire |
| **reprise rétroactive** | — | ajouter son jeton à `comparaison.NOMS` et **rejouer** Freud, Rank, Abraham, Ferenczi (voir § 2) |

---

## 6. Ce qui reste à décider

L'acquisition suppose de **télécharger** six fac-similés dans `sources/stekel/de/`. Le dossier légal
est net et le rendement est mesuré ; la décision de télécharger, elle, appartient à l'auteur du
dépôt et n'a pas été prise en écrivant ce document.

Un point d'histoire qui rend cet auteur intéressant pour la suite du projet, et qu'il faut noter sans
le faire dire au corpus : Stekel cofonde avec Freud la Société psychologique du mercredi en 1902 et
rompt en 1912, sur les névroses actuelles et sur l'onanisme. Le corpus tiendrait alors **quatre
formes du rapport au maître** — Rank déplace une thèse et rompt, Abraham prolonge et ne rompt pas,
Ferenczi diverge sur la technique, Stekel rompt le premier et sur la doctrine. Mais c'est une
hypothèse d'histoire des idées, pas une mesure : le corpus devra la contredire s'il le peut.
