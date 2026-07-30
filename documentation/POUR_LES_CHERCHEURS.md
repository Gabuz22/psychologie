# Pour les chercheurs

Cette page répond à une question précise : **quelqu'un qui a déjà accès à PEP-Web, aux
*Gesammelte Werke* numérisés et au Deutsches Textarchiv a-t-il une raison d'ouvrir celui-ci ?**

La réponse honnête est *oui pour quatre choses, non pour tout le reste* — et le reste est plus
grand. Cette page dit les quatre, puis dit le reste.

---

## 1. Ce que ce corpus fait et que les autres ne font pas

### a) L'unité est la phrase, et elle porte son statut épistémique

Une recherche plein texte répond à « où Freud écrit-il *Trieb* ? ». Elle ne répond pas à
« où Freud **soutient**-il quelque chose de *Trieb*, plutôt que de l'envisager, de le mettre en
question ou de rapporter l'opinion d'un autre ? ». Ici chaque phrase porte l'un de quatre statuts —
**affirmé, modalisé, interrogatif, rapporté** — attribué par un repérage déterministe, et une
fonction rhétorique.

Ce n'est pas un raffinement d'affichage. C'est ce qui permet de poser la question inverse de celle
que permet un moteur de recherche : non pas « qu'a-t-il dit sur X », mais « **de quoi s'est-il
porté garant** ». Le projet s'interdit de durcir ce que l'auteur a modalisé, et le vérifie par des
tests.

### b) La datation est une fenêtre, pas une année

Freud a cessé de signaler ses ajouts à partir de la 3ᵉ édition de la *Traumdeutung*. Citer
« Freud, 1900 » pour une phrase entrée dans le texte en 1914 est une erreur courante, et
silencieuse. Ici **chaque atome porte une fenêtre de datation** ; quatre œuvres sont collationnées
phrase à phrase avec leur première édition, ce qui resserre la fenêtre là où c'est possible et la
laisse ouverte là où ça ne l'est pas.

Le corpus refuse donc de fournir la donnée fausse qui serait la plus commode.

### c) Chaque auteur est décrit avec ses propres catégories

Rank n'est pas mesuré avec la grille de Freud. C'est une décision coûteuse — elle interdit
d'additionner les concepts entre auteurs — et elle est prise pour une raison précise : le motif
central de Rank, *l'enfant exposé sauvé des eaux qui revient tuer son père*, n'a **aucune case**
chez Freud. Le mesurer avec le vocabulaire freudien ne montrerait de lui que ce qui ressemble à
Freud, et l'appellerait « analyse de Rank ».

Conséquence conservée explicitement dans la base : `geburt` chez Rank est le traumatisme fondateur
de toute angoisse ; le mot n'a pas ce statut chez Freud. Deux lignes distinctes, jamais sommées.

### d) Les comparaisons entre auteurs sont des faits de texte, montrés en entier

Trois couches, posées **séparément** et **jamais additionnées**, parce que ce sont trois faits de
nature différente :

| couche | ce qu'elle mesure | ce qu'elle ne dit pas |
|---|---|---|
| **actes de citation** | deux passages partagent des suites de six mots, attestées | ni accord, ni influence |
| **mentions nominales** | un auteur écrit le nom d'un autre | nommer n'est ni suivre, ni approuver, ni contredire |
| **lectures déclarées** | un titre de chapitre annonce qu'il traite d'un autre auteur | rien de plus que ce que l'édition déclare |

Les actes de citation sont donnés avec **les deux passages tels qu'ils sont imprimés**, orthographe
d'époque comprise. Sur le cas d'Anna O. recopié par Freud quinze ans après Breuer, la réforme
orthographique de 1901 est visible entre les deux versions (`gerieth`/`geriet`,
`beissen`/`beißen`) : c'est un fait philologique que la comparaison, qui travaille sur une forme
normalisée, faisait disparaître — et qui a été rétabli exprès pour que la citation soit
**retrouvable dans le livre**.

---

## 2. Ce que ce corpus publie et que presque personne ne publie

Ses **résultats négatifs**, mesurés, avec la méthode qui a échoué.

- [`APPARIEMENT_ECARTE.md`](APPARIEMENT_ECARTE.md) — un appariement de concepts inter-auteurs par
  similarité de voisinage a été construit, calibré, puis **écarté** : précision de 6,2 % sur la
  tâche réelle, incapacité à distinguer un mot de son synonyme ou de son contraire, et 1 seule
  « divergence » confirmée sur 16 après lecture. Les quatre conditions qu'il faudrait remplir pour
  y revenir sont écrites.
- [`CARTE_CITATIONS.md`](CARTE_CITATIONS.md) — agréger les concepts de part et d'autre des liens de
  reprise produirait **1 366 « arêtes »** là où il y a **107 actes de citation** réels, parce que
  chaque phrase porte 3,5 concepts en moyenne. Le chiffre flatteur a été mesuré avant d'être refusé.
- L'attribution nominale a été essayée comme **critère de tri** des reprises : le taux est plat,
  40 % dans la bande haute comme dans la bande basse, parce que les notes bibliographiques nomment
  les auteurs autant que les vraies citations. Elle reste affichée, jamais utilisée pour trier.

Pour un lecteur méthodologiste, c'est probablement la partie la plus utile du dépôt : elle dit ce
qui, dans ce genre de travail, produit des chiffres impressionnants et faux.

Dans le même esprit, la couverture des mesures est affichée **avant** les résultats, avec la raison
de chaque silence — y compris « indétectable par construction » pour les couples d'auteurs de
langues différentes, où les corpus français et allemand du projet partagent exactement **un** groupe
de six mots.

---

## 3. Ce que ce corpus n'est pas

À lire avant de l'utiliser, et sans indulgence :

- **Ce n'est pas une bibliothèque.** Quarante œuvres, 1895-1939. Pas de correspondance, pas de
  notes de cas, pas de revues, pas de littérature secondaire. PEP-Web indexe plusieurs ordres de
  grandeur de plus.
- **Il n'y a aucune traduction.** Allemand et français seulement, par choix — la citation reste
  vérifiable, et les querelles de traduction (*Trieb* → pulsion ou instinct ?) ne sont pas héritées
  en amont. Le prix est réel : le corpus est fermé à qui ne lit pas ces deux langues.
- **Il n'y a pas d'apparat critique.** Ni notes d'éditeur, ni variantes, ni index de noms établi par
  un spécialiste. La collation phrase à phrase ne couvre que quatre œuvres.
- **La moitié du corpus est un fac-similé océrisé non relu.** Rank, Abraham et Ferenczi n'ont pas
  de transcription humaine disponible. La qualité est mesurée œuvre par œuvre, les défauts
  réparables sont réparés, et les phrases douteuses portent un avertissement — mais il reste des
  mots faux dans le texte, et certains titres de chapitre gardent leurs cicatrices de scan.
- **La couverture de la couche de comparaison est très faible.** Les actes de citation touchent
  0,5 % des phrases ; 22 œuvres sur 40 n'apparaissent dans aucun acte. Une partie s'explique
  (langue, phrases trop courtes, OCR), une autre est un fait de corpus : ces auteurs citent
  abondamment des gens qui n'y sont pas encore.
- **Les lexiques de concepts n'ont pas été relus par un psychanalyste.** Ils ont été audités —
  sept passes pour Freud, une par auteur ensuite — mais en interne. C'est la limite la plus sérieuse
  pour un usage savant, et elle ne se lève pas par du code.

---

## 4. Vérifier une affirmation de ce corpus en dix minutes

C'est le seul argument qui compte, alors voici la marche à suivre exacte.

Prenons l'acte de citation le plus net : **Freud recopiant en 1910 la description d'Anna O. écrite
par Breuer en 1895.**

1. Ouvrir la page « Carte des citations » du site et filtrer sur le couple Breuer ↔ Freud.
2. L'acte affiche les **deux passages tels qu'imprimés**, avec leur identifiant d'atome, leur œuvre
   et leur poids en nombre de phrases.
3. Le registre des sources (`core/sources.py`) donne, pour chaque œuvre, l'**URL du fac-similé** et
   l'édition exacte utilisée. Ouvrir le fac-similé, chercher la phrase : elle y est, avec son
   orthographe.
4. Pour refaire le calcul plutôt que de le croire :

```bash
python -m unittest discover -s core/tests -t .
```

puis

```bash
python bin/atomiser.py
```

Le corpus se reconstruit à l'identique — aucun modèle de langage n'intervient, aucun tirage
aléatoire. Si un chiffre de ce dépôt ne se reproduit pas chez vous, c'est un défaut, et il est
recevable comme tel.

La même vérification s'applique aux mesures qu'on n'aime pas : le détail de ce que la carte **ne
voit pas** est servi avec elle, œuvre par œuvre, avec la part de phrases trop courtes pour être
comparables.

---

## 5. Ce qui manque pour que ce corpus soit vraiment citable

Il y avait trois obstacles, aucun technique. **Le premier est levé**, les deux autres demandent une
démarche que le dépôt ne peut pas faire à la place de son auteur.

### a) La licence — posée le 2026-07-30 ✅

Le dépôt ne portait **aucun fichier `LICENSE`**, et en droit d'auteur l'absence de licence ne
signifie pas « libre » mais « tous droits réservés » : personne ne pouvait légalement réutiliser le
code, redistribuer les données, ni les inclure dans un article avec ses figures.

Trois matières, trois régimes, parce que les confondre serait une erreur juridique :

| quoi | licence | effet |
|---|---|---|
| le code — `core/`, `bin/`, `web/`, les tests | **MIT** ([`LICENSE`](../LICENSE)) | réutilisable partout, y compris dans un logiciel fermé, avec attribution |
| les données dérivées — `derive/`, `verification/` | **CC-BY-4.0** ([`LICENSE-DONNEES.md`](../LICENSE-DONNEES.md)) | citables, redistribuables et adaptables, avec attribution ; vos propres travaux dérivés restent libres de leur licence |
| les textes sources — `sources/` | **domaine public** | rien à concéder ; la provenance est déclarée œuvre par œuvre dans `core/sources.py` |

Deux demandes accompagnent la licence des données sans avoir force de condition : **citer la
version** avec le chiffre (le dépôt bouge, et ses mesures avec lui — la couverture de la carte est
passée de 0,52 % à 0,454 % le 2026-07-30, parce qu'elle comptait des côtés d'acte pour des atomes),
et **reprendre la réserve avec la mesure**. Les séparer ferait dire aux chiffres ce que le corpus
refuse de dire.

### b) Il n'y a pas de DOI, donc pas de cible de citation stable

Un article qui s'appuie sur ce corpus ne peut aujourd'hui pointer que vers une branche `main` qui
changera sous lui. Un archivage **Zenodo** du dépôt délivre un DOI et une copie figée par version,
et reprend automatiquement les métadonnées de [`CITATION.cff`](../CITATION.cff). L'opération demande
un compte Zenodo relié au compte GitHub — elle ne peut donc pas être faite depuis le dépôt.

Un **ORCID** (gratuit) rendrait de plus l'attribution stable en cas d'homonymie. Les deux champs
sont préparés et commentés dans `CITATION.cff`.

### c) Aucun spécialiste du domaine n'a relu les lexiques

C'est ce qui séparerait « un corpus rigoureux » de « un corpus dont les catégories sont défendables
devant la discipline ». Le découpage en 19 groupes conceptuels et les lexiques par auteur sont des
décisions savantes, prises hors de la discipline. Une relecture par un psychanalyste ou un historien
de la psychanalyse — même partielle, même sur un seul auteur — vaudrait plus que n'importe quelle
mesure supplémentaire.

Ce qu'on peut offrir en échange à un relecteur, et qui est rare : **tout est rejouable, et toute
objection portant sur une phrase précise peut être vérifiée puis corrigée dans le même après-midi.**

---

## 6. Comment citer

Les métadonnées sont dans [`CITATION.cff`](../CITATION.cff) (GitHub affiche un bouton
« Cite this repository »). En attendant un DOI, la forme la plus honnête mentionne la version et la
date, puisque le dépôt bouge :

> Uzan, Gabriel. *Psychologie — atomisation déterministe du corpus psychanalytique du domaine
> public*, version 0.9, 2026. https://github.com/Gabuz22/psychologie

Et, pour une affirmation précise, citez **l'atome** : son identifiant est stable — c'est une
empreinte de la phrase elle-même, et non sa position dans le volume, précisément pour qu'un
jugement porté sur une phrase lui reste attaché quand le paratexte du volume change autour.
