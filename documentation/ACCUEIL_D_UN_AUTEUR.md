# Accueillir un huitième auteur — le contrat, et ce qu'il ne promet pas

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_accueil.py` — ne pas éditer à la main : l'état des
> auteurs présents est recalculé sur le corpus à chaque exécution. Régénérer après toute entrée
> d'auteur ou d'œuvre.
>
> **Ce que ce document est.** La liste des points à déclarer pour qu'un auteur entre dans le
> corpus sans rien casser, et l'état vérifié des **7** auteurs déjà présents.
>
> **ÉTAT : les 7 auteurs du corpus satisfont le contrat, et un seul porte une réserve — décrit avec le lexique d'un autre, ce qui rend certaines mesures inapplicables. Voir §3.**
>
> **Ce que ce contrat ne promet PAS.** Que l'auteur entré soit *comparable* aux autres. Il sera
> décrit, cité, daté, et ses reprises textuelles seront trouvées. Mais s'il écrit dans une autre
> langue, la reprise textuelle est aveugle par construction — les corpus français et allemand du
> projet partagent UN seul groupe de six mots. Et s'il n'a pas de lexique propre, il est décrit
> avec celui d'un autre : on ne voit alors de lui que ce qui ressemble à cet autre.

---

## 1. Les points à déclarer

Chacun a été payé au moins une fois. La colonne **si on l'oublie** n'est pas une précaution de style : c'est ce qui est réellement arrivé, ou ce que le code fait réellement.

| Point | Où | Obligatoire | Si on l'oublie |
|---|---|---|---|
| **oeuvres** | `core/sources.py : OEUVRES` | oui | l'auteur n'existe pas — il n'a aucun atome |
| **jeton_de_nom** | `core/comparaison.py : NOMS` | oui | aucun auteur ne peut être enregistré comme le nommant — il paraît isolé, et ce silence se lit comme un fait de corpus (mesuré sur Ferenczi : 16,8 % des atomes, 80 mentions invisibles) |
| **biographie** | `bin/exporter_d1.py : AUTEURS` | oui | l'export échoue à la clé manquante — panne bruyante, donc sans danger |
| **lexique** | `core/lexiques/__init__.py : PAR_AUTEUR` | non — mais réserve | il est décrit avec le lexique de Freud, donc on ne voit de lui que ce qui ressemble à Freud — et plusieurs mesures cessent d'avoir un sens pour lui (voir `mesures_non_applicables`) |
| **langue** | `core/comparaison.py : langues_par_auteur` | oui | un auteur à cheval sur deux langues rend None, et aucune densité n'est mesurée sur lui : le silence vaut mieux qu'un zéro faux, mais il est alors déclaré |

**Un seul point ne se déclare pas** : la *langue*, dérivée des œuvres de l'auteur. La distinction n'est pas cosmétique — offrir un endroit où déclarer la langue serait offrir un endroit où se tromper : une œuvre française rangée sous un auteur annoncé germanophone passerait sans bruit. Il n'y a rien à écrire, seulement à vérifier qu'elle est résoluble.

---

## 2. L'état des auteurs présents, vérifié

Le contrôle porte sur les auteurs **ayant des atomes**, jamais sur les registres : un nom déclaré sans œuvre n'est pas un problème, un auteur qui écrit sans être déclaré en est un. C'est le sens exact de l'oubli de Ferenczi, et l'inverse ne s'est jamais produit.

| Auteur | Atomes | Langue | Lexique propre | Conforme |
|---|---:|---|---|---|
| Wilhelm Stekel | 42 260 | de | oui | oui |
| Sigmund Freud | 40 276 | de | oui | oui |
| Otto Rank | 14 938 | de | oui | oui |
| Sándor Ferenczi | 9 158 | de | oui | oui |
| Karl Abraham | 7 543 | de | oui | oui |
| Gustave Le Bon | 1 485 | fr | oui | oui |
| Josef Breuer | 885 | de | **non** | oui |

---

## 3. L'exception, et ce qu'elle invalide

**Josef Breuer** est décrit avec le lexique de Freud, et c'est le seul cas. Ce n'est pas un manquement : ses pages sont imprimées dans un volume de Freud, et les catégories sont celles de l'auteur du volume — décision documentée dans `core/atomisation.py`. Mais la CONSÉQUENCE ne l'était pas, et elle a fait passer un artefact pour un résultat.

| Mesure qui cesse d'avoir un sens | Pourquoi |
|---|---|
| signature lexicale (branches, §1) | le contrôle par provenance du motif est VIDE pour lui — ne possédant aucun motif, il ne peut jamais dominer sur le sien. Toute signature qu'il produit passe le contrôle sans être éprouvée par lui. |
| densité de ses concepts propres (usages) | aucun motif n'a été écrit pour lui : on ne voit de lui que ce qui ressemble à l'auteur dont on emprunte le lexique. |

**Le cas mesuré.** La couche des branches écarte une signature lexicale quand le motif vient du PROPRE lexique de l'auteur qui domine — contrôle qui élimine 31 des 35 signatures du corpus. Les 4 restantes étaient toutes de Breuer, et l'on a d'abord écrit qu'elles *survivaient* à ce contrôle. C'est faux : ne possédant aucun motif, il ne peut jamais dominer sur le sien, donc le contrôle est **vide pour lui**. Elles ne survivaient pas, elles ne le rencontraient pas. Le résultat publié ne change pas — zéro signature après les deux contrôles — mais il repose désormais sur le bon motif.

---

## 4. Le défaut qui attendait le huitième auteur

Le dépôt écrit **quarante fois** `atome.get("auteur", "Sigmund Freud")`, dans vingt et un
fichiers. Ce défaut n'est **jamais** nécessaire : `core/atomisation.py` pose le champ `auteur` sur
chaque atome qu'il produit. Il ne peut donc se déclencher que si quelque chose est cassé — et ce
jour-là, il n'annonce rien : il attribue le texte à Freud, et la mesure fausse traverse toutes les
couches en silence.

C'est le mode de panne exact qui a rendu Ferenczi invisible : entré avec **16,8 %** des atomes du
corpus et sans jeton de nom, aucun auteur ne pouvait être enregistré comme le nommant, et le
couple Freud ↔ Ferenczi paraissait unidirectionnel — un accident de configuration présenté comme
un fait de texte.

`accueil.auteur_de()` échoue au lieu de deviner, et un test l'appelle sur les **116 545** atomes du
corpus sans qu'il lève une seule fois. Le défaut est donc prouvé mort : il ne protège rien, il ne
peut que mentir. C'est la même règle que le corpus applique déjà à la datation (INDÉCIDABLE plutôt
qu'une date devinée) et aux langues (non mesurable plutôt qu'un zéro faux).

---

## 5. Ce que ce contrat ne dit pas

Ce contrat garantit l'ACCUEIL d'un auteur, jamais sa COMPARABILITÉ. Un auteur entré selon ces règles sera décrit, cité, daté, et ses reprises textuelles seront trouvées. Mais s'il écrit dans une autre langue, la reprise textuelle est aveugle par construction — les corpus français et allemand du projet partagent UN seul groupe de six mots. Et s'il n'a pas de lexique propre, il est décrit avec celui d'un autre : on ne voit alors de lui que ce qui ressemble à cet autre, et certaines mesures cessent d'avoir un sens pour lui sans que rien ne le signale. LE CONTRAT NE SE VÉRIFIE PAS TOUT SEUL : il est éprouvé par un test sur les auteurs réellement présents dans le corpus. Un nom déclaré sans œuvre n'est pas un problème ; un auteur qui écrit sans être déclaré en est un, et c'est arrivé — Ferenczi est entré avec 16,8 % des atomes du corpus et sans jeton de nom, si bien qu'aucun auteur ne pouvait être enregistré comme le nommant.

*Reproduire : `python bin/generer_accueil.py` · la règle du lexique par auteur : `core/lexiques/__init__.py` · ce que la comparaison entre auteurs ne donne pas : `BRANCHES_ET_DERIVATIONS.md` §1.*
