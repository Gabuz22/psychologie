# Les défauts qu'aucune lecture ne trouve

Ce dépôt fait relire ses lexiques par des contradicteurs, et ça marche : treize audits successifs
ont retiré des sous-concepts entiers, corrigé des motifs, mesuré des plafonds. Mais **une classe de
défauts échappe complètement à la lecture**, parce qu'elle est invisible à l'œil : le motif *a l'air
juste*. Il ne lève aucune erreur. Il ne capte simplement rien, ou il compte deux fois.

Ce document rend compte du premier passage mécanique sur les cinq lexiques (2026-08-01,
`bin/verifier_motifs.py`) : **162 défauts**, dont un qui vivait dans le dépôt depuis des mois.

---

## 1. Le `\b` mangé — trois motifs de Freud morts en silence

```python
"realitaet":      ["realitat", "real\b",  "reale", ...]        # AVANT
"knabe_maedchen": ["knabe", "knaben", "madchen", "bube\b", "junge\b"]
```

`"real\b"` en Python **n'est pas** « real + frontière de mot ». Dans une chaîne non brute, `\b` est
le caractère **BACKSPACE** (0x08). Aucun texte allemand n'en contient : ces trois motifs ne
pouvaient rien capter, jamais.

| motif | ce qu'il rend une fois réparé |
|---|---|
| `junge\b` | **116 atomes** |
| `real\b` | **49 atomes** |
| `bube\b` | **0** — le mot est absent du corpus allemand de Freud |

Le sous-concept touché est `knabe_maedchen`, qui porte la **différence des sexes** — ajoutée à
l'audit 8 comme « le plus gros manque du corpus ». Les deux mots allemands courants pour « garçon »
après *Knabe* y étaient morts.

**Pourquoi huit audits ne l'ont pas vue** : la faute ne produit ni exception, ni avertissement, ni
comportement bizarre. Le fichier se lit normalement. Le seul symptôme est un compte plus bas que
prévu — et personne n'avait de « prévu » à comparer.

`bube` est retiré, mais **après réparation et mesure**, pas par principe : c'est en le faisant
marcher qu'on apprend que le mot n'est pas là. Même chose pour `namensvergessen` (Freud écrit
*Namenvergessen*, sans le -s- de liaison).

**Garde posée** : `test_aucun_motif_ne_contient_de_caractere_de_controle`.

---

## 2. Le diacritique — la même faute pour la cinquième fois

Le lexique s'applique **après** `segmentation.replier`, qui supprime les diacritiques. Un motif
portant « ä », « ö », « ü » ou « ß » ne peut jamais se déclencher.

Documentée trois fois dans le lexique de Stekel (`angstgefühl`, `nervosität`, `schuldgefühl`), elle
était aussi chez Freud : `abergläubisch`. Elle y avait survécu pour une raison instructive — la
forme repliée correcte (`aberglaubisch`) était juste à côté dans la même liste, si bien que le
sous-concept fonctionnait et que rien ne signalait le motif mort.

**Garde posée** : `test_aucun_motif_ne_porte_de_diacritique`.

---

## 3. Le motif absorbé — 129 cas, et le plus coûteux valait 33 %

Un motif qui n'apporte **aucun atome** que les autres motifs de son sous-concept n'apportent déjà.
Il ne qualifie rien de plus, mais il **gonfle le compte d'occurrences**, puisque le même mot est
compté une fois par motif qui le touche.

Le cas qui a fait construire cet outil : dans `sterben` (Stekel), `todes` ⊂ `tod` et `sterben` ⊂
`sterbe` — **785 occurrences comptées deux fois, 33 % du compte affiché du sous-concept**. Le
doublon se lisait dans la colonne « formes » du banc sans que personne le voie : tous les chiffres
y étaient exactement le double du réel.

Répartition du premier passage :

| lexique | motifs | absorbés |
|---|---|---|
| Freud | ~900 | 23 |
| Ferenczi | 356 | 10 |
| Stekel | 155 | 8 |
| Rank, Abraham, Le Bon | — | le reste |

**Tous ne sont pas à retirer.** `unbewusste` ⊂ `unbewusst` documente une forme attestée et ne coûte
qu'une ligne ; `sexuelle` ⊂ `sexuell` idem. Ce que l'outil établit, c'est que **le compte
d'occurrences de ces sous-concepts double sur ces formes** — et cela doit être su quand on lit un
rapport de fréquence. Le banc, lui, a été corrigé pour compter par POSITION et non par motif.

---

## 4. Le motif muet chez son auteur — 13 cas

Le motif fonctionne, mais rend zéro atome **chez l'auteur dont c'est le lexique**, alors qu'il en
rend ailleurs. Ce n'est pas une faute d'écriture : c'est un fait sur l'auteur, et il est intéressant
comme tel. `uberich` fait 0 chez Ferenczi contre 63 ailleurs ; `insomni` fait 0 chez Stekel.

L'outil les signale sans les condamner — un lexique d'auteur peut légitimement prévoir une forme
que l'auteur n'emploie pas, si elle est attestée dans son champ.

---

## 5. Ce que cette classe de défauts dit de la méthode

Les treize audits contradictoires du dépôt ont porté sur **ce que les motifs ramènent** — la règle
d'or, « on ne juge jamais un motif sur son intention, toujours sur la liste de ce qu'il capte ».
C'est la bonne règle, et elle a trouvé beaucoup.

Mais elle a un angle mort exact : **un motif qui ne ramène RIEN ne montre rien à juger.** Il ne
produit aucune liste, donc aucune liste suspecte. Il disparaît du champ de la lecture.

D'où la division du travail qui s'impose :

| | trouve | ne trouve pas |
|---|---|---|
| **lecture contradictoire** | ce qu'un motif capte à tort | ce qu'un motif ne capte pas du tout |
| **contrôle mécanique** | motif mort, absorbé, doublon | si le mot capté est le bon objet |

Les deux sont nécessaires, et aucun ne remplace l'autre.
