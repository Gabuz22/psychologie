# La couverture de la comparaison — six pistes mesurées, cinq refusées

La carte des actes de citation ne touche qu'une fraction du corpus, et 22 œuvres sur 40 n'y
apparaissent dans aucun acte. Ce document répond à la question qui s'ensuit : **est-ce un défaut de
la méthode, qu'on peut réparer, ou une propriété du corpus ?**

La réponse est mesurée, et c'est la seconde. La méthode a **une** réparation, d'un dixième de point ;
elle n'a rien de plus à donner. Le reste de ce document dit comment on le sait.

Deux registres sont distingués partout : **ce que j'ai rejoué moi-même sur la base** (§ 1, § 2) et
**ce qui vient d'une mesure soumise à un contradicteur** (§ 3, § 4). Trois des cinq contradictions
ont renversé la mesure qu'elles éprouvaient — c'est pour cela qu'elles existent.

---

## 1. Deux défauts trouvés dans la couche déjà livrée, et corrigés

Ils ont été trouvés en cherchant à élargir la carte, et ils portaient sur ce qu'elle publiait déjà.

### a) La couverture était surcomptée de 14,5 % — sur la mesure même du silence

`carte.couverture` rendait `somme(poids × 2)` : un nombre de **côtés d'acte**, non d'atomes. Un
atome cité par deux actes était compté deux fois. Le corpus publiait donc :

| | publié | réel |
|---|---|---|
| atomes touchés | 284 | **248** |
| part du corpus | 0,52 % | **0,454 %** |

Le défaut portait précisément sur la seule mesure dont ce module a la charge : **dire ce que la
carte ne voit pas**. Et sa propre docstring portait déjà le bon chiffre — code et documentation se
contredisaient depuis le premier jour, sans que rien ne le signale.

Corrigé : chaque acte déclare les atomes qu'il couvre, et la couverture les compte une fois. Deux
tests le gardent, dont une contre-épreuve — pour qu'on ne remplace pas un surcompte par un
sous-compte.

Deuxième volet du même défaut : la ligne de totaux de `carte_couverture` rangeait sa couverture dans
la colonne `part_trop_courts`, qui veut dire tout autre chose, et le worker la relisait sous alias
(`part_trop_courts AS part_touchee`). Le détournement ne se lisait nulle part. Chaque mesure a
maintenant sa colonne.

### b) Deux actes sur quatre violaient la doctrine des sources tierces

`comparaison.qualifier` pose `sens = None` dès que les deux passages nomment un auteur extérieur au
corpus : chacun peut tenir sa formulation de ce tiers plutôt que de l'autre. Au niveau du lien,
c'est respecté — **0 des 4 liens à source tierce est orienté**. Au niveau de l'acte, **2 des 4
l'étaient**.

La cause est fine et vaut d'être écrite. `carte._unanime` **ignore les `None`** : il rend la valeur
si toutes les valeurs non nulles s'accordent. C'est exactement ce qu'il faut pour un verdict pas
encore lu — un `None` y signifie « pas encore d'information ». C'est faux pour le sens, où le `None`
est un **refus délibéré de conclure**. Un acte mêlant une paire à tiers et une paire sans tiers
héritait donc du sens de la seconde, et effaçait le refus de la première.

Corrigé, et testé : le tiers d'une seule paire désoriente tout l'acte.

---

## 2. L'état réel des couches — rejoué sur la base du 2026-07-30

Les « 22 œuvres muettes » sont muettes **pour la carte des actes**, pas pour la base. Toute mesure
qui annonce « les muettes tombent de 22 à N » se compare aux actes seuls et gonfle son gain.

| couche | atomes distincts | % corpus | œuvres | couples d'auteurs |
|---|---|---|---|---|
| actes de citation | 248 | 0,454 % | 18 / 40 | 6 / 15 |
| mentions nominales | 2 135 | 3,908 % | 32 / 40 | 11 / 15 |
| **union des deux** | **2 345** | **4,293 %** | **33 / 40** | 11 / 15 |
| lectures déclarées | 9 lignes | — | 4 / 40 | 4 / 15 |

Le recouvrement des deux couches principales est de **38 atomes** : ce ne sont pas deux mesures du
même fait, ce sont deux faits.

**Sept œuvres seulement (2 525 atomes) sont muettes dans les deux couches** — et pour celles-là
aucun élargissement n'y changera rien, parce qu'elles ne parlent pas de ce corpus :

| œuvre | atomes |
|---|---|
| *Psychologie des foules* (Le Bon) | 1 485 |
| *Eine Teufelsneurose im siebzehnten Jahrhundert* | 326 |
| *Der Moses des Michelangelo* | 283 |
| *Zeitgemäßes über Krieg und Tod* | 276 |
| *Eine Schwierigkeit der Psychoanalyse* | 90 |
| *Vergänglichkeit* | 44 |
| *Eine Kindheitserinnerung aus »Dichtung und Wahrheit«* | 21 |

Dans le *Moses*, Freud cite Lübke, Justi, Thode, Springer — pas un psychanalyste. Et
*Psychologie des foules* est le cas limite absolu : **les corpus français et allemand du projet
partagent zéro à un groupe de six mots**, et le seul partage existant est une locution courante.
Freud ↔ Le Bon ne sera **jamais** un couple d'actes, quel que soit le réglage.

---

## 3. Les six pistes, et pourquoi cinq sont refusées

Chaque piste a été mesurée par un premier examen, puis soumise à un contradicteur chargé de
**reproduire ses chiffres** et de la réfuter. Trois mesures sur cinq n'ont pas survécu.

| piste | verdict de la mesure | après contradiction |
|---|---|---|
| raccourcir le n-gramme (6 → 4) | **écarter** (par sa propre mesure) | — |
| abaisser le seuil de mots (20 → 12) | retenir avec réserve | **tient**, mais voir ci-dessous |
| renvois d'un auteur à sa propre œuvre | retenir avec réserve | **réfuté → écarté** |
| l'appareil bibliographique comme couche | retenir avec réserve | **réfuté → écarté** |
| titres d'œuvres cités | retenir avec réserve | **réfuté sur les effectifs** |
| diagnostic du silence des muettes | retenir | **tient** |

### Écartée : raccourcir le n-gramme

À 4 mots au lieu de 6 : **+0,060 point de corpus et ZÉRO couple d'auteurs nouveau**. Le bruit
ajouté n'est pas de la langue courante — le garde-fou `DOCUMENTS_MAXIMUM` ne se déclenche pas —
mais de l'**apparat bibliographique** : 27 % des nouveaux liens contre 5,6 % de rejets dans la
même bande à 6 mots. Trois titres d'ouvrage suffisent à les produire, et deux de ces faux liens ont
pour côté allemand une **page d'annonces d'éditeur**.

### Écartée après contradiction : les renvois d'un auteur à sa propre œuvre

La mesure annonçait 54,7 % de vraies auto-citations sur 64 actes. Le contradicteur a **tiré 15 actes
au hasard et les a lus** : 4 vraies sur 15, soit **26,7 %** — 73 % de bruit. La nature dominante du
bruit est instructive : Rank ne se cite pas, il **re-cite Grimm** (la Lohengrinsage, 10 actes). Un
auteur qui reprend deux fois le même conte ne se cite pas lui-même.

### Écartée après contradiction : l'appareil bibliographique

C'est la piste qui promettait le plus, et son argument était une **erreur de dénominateur**. Elle
annonçait « ×10,6 » en comparant *5,49 % du corpus porte une marque d'apparat* à *0,45 % partage un
texte avec un autre auteur* : deux faits différents. Mesuré sur une base homogène — atomes que ni
les actes ni les mentions ne portent déjà — l'apport est de **27 atomes, soit 0,049 %**, cent fois
moins que le chiffre plaidé. Sur l'axe des auteurs il est **nul** : les 281 renvois qui nomment un
confrère sont déjà tous des mentions, **zéro couple gagné**.

Le détecteur, lui, est bon (précision ~99 % sur 110 atomes lus). Ce qui est écarté, c'est son usage
comme argument de couverture. Deux emplois restent ouverts : un **axe corpus → monde extérieur**
(2 437 renvois désignent une source hors corpus — l'appareil savant de ces six auteurs, objet
réellement neuf), et un **drapeau** sur les actes existants.

### Réfutée sur ses effectifs : les titres d'œuvres cités

Le principe est bon — un titre traduit franchit la barrière des langues, ce qu'aucun n-gramme ne
fait. Mais deux mesures indépendantes de la même couche donnent 15 154 et 18 938 atomes touchés, et
les écarts vont en sens contraire, ce qu'un simple sur-ensemble de formes ne peut pas produire. Deux
des six identifiants publiés comme preuve ne sont pas dans la couche.

Surtout : **zéro œuvre rendue visible.** Les œuvres muettes passent de 22 à 7 par les mentions
seules ; ajouter les titres ne change rien. Les « 12 œuvres révélées » étaient déjà visibles.
*Le principe est retenu ; ses effectifs ne le sont pas. Une implémentation devra remesurer et
publier son registre de formes.*

### Retenue sous condition : abaisser le seuil de mots (20 → 12)

Le seul gain de couverture réel des six pistes : **+0,104 point** (0,454 % → 0,558 %), +12 actes,
+1 œuvre (*Versuch einer Genitaltheorie*), et **0 couple d'auteurs**. Les 48 nouveaux liens ont été
lus un par un : 30 vraies citations, 17 faux d'apparat, 1 source tierce.

Trois raisons de ne pas le livrer sans travail humain :

1. **43 % des vrais nouveaux liens sont un seul bloc** — Rank reproduisant, en le déclarant, une
   analyse de rêve d'Abraham. Ce n'est pas 13 endroits, c'est **une** citation continue. Le bénéfice
   honnête n'est pas le compte d'actes, c'est la **preuve** : le paragraphe cité redevient entier.
2. **Le seuil est aussi ce qui EXCUSE les silences.** `part_trop_courts`, publié pour chaque œuvre
   muette, passerait de 32,8 % à 13,5 % : abaisser le seuil réécrirait silencieusement la raison
   publiée du silence de 22 œuvres. La valeur du seuil devra être versionnée dans la table.
3. **Le projet lit ses nouveaux liens avant de les publier.** 5 % de résidu faux subsiste après
   filtre ; il doit être déclaré, pas absorbé.

C'est un chantier à ouvrir, pas un réglage à changer.

---

## 4. Le plafond, et la conclusion

**Le plafond absolu de la méthode, tout bruit admis** (seuil de contenance à zéro, seuil de mots à
douze) : **1,155 % du corpus et 8 couples d'auteurs sur 15.** Aucun réglage n'ouvre un seul couple
nouveau — ni la longueur du n-gramme (+0,060 pt, 0 couple), ni le seuil de mots (+0,104 pt,
0 couple), ni le seuil de contenance (+0,101 pt, 0 couple). **La dimension la plus visible de la
carte est structurellement fermée.**

Trois mesures fondent la conclusion, et aucune n'est une opinion :

1. **Les citations sont annoncées, mais le texte cité n'est pas dans le corpus.** Dans les œuvres
   muettes, ~200 atomes annoncent une citation littérale — ils nomment un auteur du corpus, ouvrent
   un guillemet, font plus de vingt mots. **Seuls 4 % partagent un n-gramme discriminant avec
   l'auteur nommé.** Abraham écrit « Als im Jahre 1916 Freuds oft zitierter Aufsatz über *Trauer und
   Melancholie* erschien… » — et *Trauer und Melancholie* n'est pas au corpus.

2. **Ces auteurs citent par référence, pas par transcription.** Dans le même corpus :
   **248 atomes** de reprise textuelle, **2 135** de mention nominale, **~2 900** de renvoi
   bibliographique. Un rapport d'environ **onze contre un** entre *nommer / référencer* et
   *recopier*. Une carte de la reprise textuelle ne peut capter que le résidu. **Ce n'est pas un
   défaut de la carte, c'est une propriété de l'appareil savant psychanalytique — et c'est un
   résultat.**

3. **Ce qui manque, ce sont des ŒUVRES, pas des auteurs.** 27 atomes des œuvres muettes citent
   nommément un titre freudien **absent** du corpus — *Zur Einführung des Narzissmus*, *Das Ich und
   das Es*, l'*Analyse der Phobie eines fünfjährigen Knaben*, les *Bemerkungen über einen Fall von
   Zwangsneurose*, *Trauer und Melancholie* — contre 63 citant un titre présent. **Le corpus est
   incomplet aux deux tiers sur ce que ses propres auteurs citent.**

   Et ajouter un auteur ne suffit pas : les plus cités par les muettes sont hors d'atteinte du
   détecteur (Frazer 94 atomes, Jones 24, Robertson Smith 20, McDougall 15 — cités en anglais et
   **résumés en allemand**). Ajouter un jeton de nom ne démuette aucune œuvre. **Seul l'ajout d'une
   ŒUVRE peut produire un acte.**

---

## 5. Ce qui reste ouvert

- **~~Un audit de `sens` contre `sens_lu`~~ — FAIT le 2026-07-31, et c'était un défaut, pas un
  désaccord de méthode.** Les 16 contradictions n'opposaient pas deux mesures : elles publiaient
  **seize emprunts à l'envers**. Le détail est au § 6 ci-dessous, parce qu'il mérite mieux qu'une
  ligne — c'est le seul risque que le registre des reprises se donne explicitement pour mission
  d'écarter, et il s'était réalisé.
- **`SOURCES_TIERCES` ne contient ni Grimm ni Ibsen — CORRECTION, vérifiée le 2026-07-31.** Cette
  note affirmait que « le corpus porte des liens qui les citent des deux côtés ». C'était une
  confusion avec la piste `auto_citation`, rejetée : son bruit dominant était Rank RE-CITANT Grimm
  d'une œuvre à l'autre — un fait INTRA-auteur, jamais stocké dans `liens_reprise`, qui ne contient
  que des paires inter-auteurs (vérifié : `auteur_a != auteur_b` sur les 230 lignes de la table).
  Mesuré directement sur la base : **zéro** ligne de `liens_reprise` ne nomme Grimm ou Ibsen, des
  deux côtés ou d'un seul. Les deux sont pourtant bien cités dans le corpus (Grimm : 5 atomes de
  Freud, 103 de Rank, 2 de Ferenczi ; Ibsen : 2, 35, 6) — mais aucune de ces citations ne partage
  une suite de six mots avec une citation d'un AUTRE auteur, au seuil actuel. Ajouter les deux jetons
  à `SOURCES_TIERCES` aujourd'hui n'aurait donc AUCUN effet observable : ce serait une entrée sans
  cas d'usage, contraire à la règle du projet de ne rien ajouter sans nécessité mesurée. Le besoin
  ne redeviendrait réel que si le chantier du seuil de mots (ci-dessous) était mené à bien et faisait
  apparaître un lien inter-auteurs nommant l'un des deux des deux côtés — à revérifier à ce moment-là,
  pas avant.
- **Le chantier du seuil de mots** (§ 3), avec ses 48 liens à lire et son filtre à déclarer.
- **~~Six ou sept œuvres allemandes du domaine public que ce corpus cite et ne contient pas~~ —
  FAIT le 2026-07-31 : onze sont entrées** (voir l'en-tête de `core/sources.py`). C'était bien
  l'ajout au meilleur rendement : les actes de citation sont passés de 107 à 175.

---

## 6. Seize emprunts publiés à l'envers — le défaut, et comment il a tenu

Ce paragraphe est le plus important du document, parce que le défaut portait exactement sur ce que
le projet met le plus en avant : **qui cite qui**.

### Ce qui était publié

Un acte de citation porte deux orientations, et le site les distingue : `sens`, établi par les
**dates** quand les fenêtres de datation sont disjointes, et `sens_lu`, ce que le **texte déclare**
lui-même (« Ich zitiere den folgenden Passus wörtlich nach Freud »). Sur 46 actes où les deux
étaient remplis, **16 se contredisaient**. On pouvait croire à une divergence intéressante entre
deux méthodes. C'était un bug, et `sens` avait raison partout.

Le cas le plus net : **Abraham citant Freud** en toutes lettres — *Traum und Mythus* (1909) reprend
mot à mot un passage de la *Traumdeutung* (1900), en l'annonçant et en donnant la page. Le corpus
publiait **Freud citant Abraham**, neuf ans avant que le texte d'Abraham existe.

### Pourquoi

La clé d'un verdict de lecture est faite des deux empreintes **triées**, pour que le même couple lu
dans un sens ou dans l'autre retrouve son jugement. Ce tri fait perdre l'ordre (a, b) sur lequel
« a_vers_b » a été rendu. L'export le retrouvait en comparant l'identifiant stocké `id_a` à
l'identifiant courant du côté a.

Or ces identifiants sont **positionnels** (`traumdeutung:a2476`) et dérivent dès qu'on retire du
paratexte en amont. C'est la raison même pour laquelle ce registre est clé par empreinte — et le
commentaire du code le disait, deux lignes au-dessus de la ligne fautive :

> `# Le verdict est retrouvé par EMPREINTES, jamais par identifiants d'atome :`
> `# ceux-ci se décalent à la moindre correction de paratexte en amont.`

Puis, juste en dessous : `if sens_lu and j.get("id_a") != lien["a"]["id"]`. Le code énonçait la
règle et l'enfreignait dans le même souffle.

Les corrections de chapitrage et l'entrée des onze œuvres ont fait dériver les numéros. Mesuré :
sur 56 liens portant un sens lu, **40 avaient l'identifiant intact et 16 avaient dérivé** — et ces
16 déclenchaient un retournement qui n'avait aucune raison d'être. Aucun ne relevait d'un vrai
changement d'ordre : le retournement, dans l'état actuel du corpus, n'était **jamais** nécessaire.

### Ce qui a été fait, et une fausse correction écartée

Le registre porte maintenant **`empreinte_a`**, le hachage du texte du côté a. Il ne dérive pas, et
il tranche sans rien déduire. Les 56 verdicts existants ont été ancrés en une passe, aucun cas
ambigu. `valider_reprises` refuse désormais un sens sans ancrage, et l'export s'arrête plutôt que
de publier une orientation qu'il ne saurait pas justifier.

**Une première correction avait été écrite, puis écartée par son propre test.** Elle comparait les
**œuvres** plutôt que les identifiants complets — l'œuvre ne dérivant pas — en supposant que les
deux côtés d'une reprise appartiennent toujours à des œuvres différentes, puisqu'ils appartiennent
à des auteurs différents. Le test écrit pour la protéger a mesuré le contraire : **trois reprises
du corpus mettent en regard deux atomes du même volume**, les *Studien über Hysterie* de 1895, dont
Breuer et Freud sont co-auteurs. La supposition était fausse, et c'est le test qui l'a dit avant que
le correctif ne parte. Le fait est conservé comme garde-fou dans `test_verification.py`.

Après correction : **0 contradiction** sur 48 liens et 45 actes.
