# Licence des données — CC BY 4.0

Les **données dérivées** de ce projet sont mises à disposition sous
**Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Texte intégral : <https://creativecommons.org/licenses/by/4.0/legalcode.fr>
Résumé lisible : <https://creativecommons.org/licenses/by/4.0/deed.fr>
Identifiant SPDX : `CC-BY-4.0`

---

## Ce qui est couvert

Tout ce que le pipeline **produit**, et non ce qu'il lit :

- `derive/` — les atomes et leurs attributs (position, fonction, statut épistémique, concepts,
  fenêtre de datation), les liens de reprise, les actes de citation, les mentions nominales, les
  lectures déclarées, les grappes, les tables d'usage, et l'export SQL de la base ;
- `verification/` — les registres de jugements portés à la main sur les signaux et les reprises,
  clés par empreinte de phrase ;
- les **lexiques de concepts** de `core/lexiques/` en tant que *contenu savant* — le découpage en
  groupes, le choix des concepts et de leurs motifs. Le fichier Python qui les porte est aussi du
  code, et reste donc également disponible sous MIT : prenez celle des deux qui convient à votre
  usage.

## Ce qui n'est pas couvert

- **Le code** (`core/`, `bin/`, `web/`, les tests) : licence MIT, voir [`LICENSE`](LICENSE).
- **Les textes sources** (`sources/`) : **domaine public**. Ils ne sont pas concédés par ce dépôt
  et n'ont pas à l'être. Chaque œuvre déclare son édition, son éditeur, son année et son
  fac-similé dans `core/sources.py`.

---

## Ce que l'attribution demande, concrètement

Citer la source lors de toute réutilisation, y compris pour une figure dans un article. La forme
recommandée est dans [`CITATION.cff`](CITATION.cff) ; en une ligne :

> Uzan, Gabriel. *Psychologie — atomisation déterministe du corpus psychanalytique du domaine
> public*, 2026. https://github.com/Gabuz22/psychologie — données sous CC BY 4.0.

CC BY 4.0 n'impose **pas** de partager vos propres travaux dérivés sous la même licence. Vous
pouvez adapter, filtrer, recouper avec d'autres corpus, et publier le résultat comme vous
l'entendez, à condition de dire d'où viennent les données et si vous les avez modifiées.

---

## Deux demandes qui ne sont pas des conditions

Elles n'ont aucune force juridique, et elles tiennent à ce que ce corpus prétend être.

1. **Si vous citez un chiffre de ce corpus, citez sa version.** Le dépôt bouge, et les mesures avec
   lui — la couverture de la carte a été corrigée de 0,52 % à 0,454 % le 2026-07-30, parce qu'elle
   comptait des côtés d'acte pour des atomes. Une mesure sans version n'est pas vérifiable.

2. **Si vous reprenez une mesure, reprenez aussi sa réserve.** Chaque couche de ce projet est
   publiée avec ce qu'elle n'établit pas : une mention nominale ne dit ni accord ni désaccord, un
   acte de citation ne dit pas une influence, et la carte est aveugle par construction entre deux
   auteurs de langues différentes. Ces réserves sont dans
   [`documentation/`](documentation/) — notamment `CARTE_CITATIONS.md`, `COUVERTURE_MESUREE.md` et
   `APPARIEMENT_ECARTE.md`, qui conserve une méthode mesurée puis écartée. Les séparer des chiffres
   qu'elles accompagnent leur ferait dire ce que le corpus refuse de dire.
