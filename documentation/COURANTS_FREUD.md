# Les courants internes du corpus freudien — dossiers de référence par grappe

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_courants.py` — ne pas éditer à la main : les
> chiffres et les citations viennent du corpus à chaque exécution, la prose éditoriale de
> `bin/exporter_d1.py:EDITORIAL_GRAPPES` (la même source que le site). Régénérer après toute
> modification du lexique.
>
> **Ce que ce document est.** Le dossier de chacune des grappes que l'agent `courants` découpe
> dans le graphe de cooccurrence des concepts. Chaque dossier
> donne : les concepts membres, le profil chronologique par œuvre, la part **datée avec
> certitude** quand la collation le permet, une citation choisie par l'agent lui-même, et la
> réserve qui limite l'interprétation.
>
> **RÉSERVE À LIRE AVANT LES DOSSIERS. Modularité 0,288 sur 167 concepts reliés : c'est SOUS le seuil de 0,30 en deçà duquel un découpage n'est plus tenu pour la marque d'une structure réelle. Le découpage ci-dessous reste le meilleur que la méthode trouve, et il reste déterministe — mais il n'est plus adossé à une structure nette du graphe, et l'on doit s'en servir comme d'une indication de voisinage, non comme d'un partage des courants de Freud. Ce chiffre a baissé en même temps que le corpus grandissait : un graphe plus dense se découpe moins bien, ce qui est un fait sur la MESURE et non sur l'auteur.**
>
> **Ce que ce document n'est pas.** Une classification que Freud revendiquerait. Une grappe est
> un fait de cooccurrence — jamais opposable seul.
>
> Les densités sont en ‰ des atomes de l'œuvre (auteur : Sigmund Freud seul — l'appendice
> d'Otto Rank fausserait la mesure de ce que FREUD pense ensemble). Pour les œuvres
> collationnées, `origine` donne la densité recalculée sur les seuls passages retrouvés dans la
> première édition — la seule comparable d'une œuvre à l'autre sans réserve d'édition.

---

## 1. Le rêve, l'appareil psychique, et le mot d'esprit — 40 concepts, 14 639 atomes

*abfuhr, affekt, anspielung, apparat, aufmerksamkeit, besetzung, bewusstsein, deutung, energie, entstellung, erregung, halluzination, hemmung, komik, lachen, lustprinzip, nachahmung, psychisme, reiz, schlaf, tagesrest, tendenz, theorie, traum, traumarbeit, traumdeutung, traumgedanke, trauminhalt, unbewusst, verdichtung, verdraengung, verschiebung, vorbewusst, vorstellung, wachen, wiederholungszwang, witz, wunsch, wunscherfuellung, zensur.*

Le mécanisme du rêve (condensation, déplacement, censure) réuni à la métapsychologie qui l'explique — conscience, investissement, décharge, excitation — et, depuis l'entrée des « Vorlesungen », au COMIQUE : le rire, la plaisanterie, l'imitation ont rejoint le rêve. Le voisinage n'est pas fortuit et Freud l'établit lui-même dès 1905 : le mot d'esprit et le rêve partagent leur technique, condensation et déplacement, et ne diffèrent que par leur destination.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Der Witz und seine Beziehung zum Unbewußten* (1905) | 692 ‰ | 713 ‰ |
| *Die Traumdeutung* (1900) | 646 ‰ | 673 ‰ |
| *Vorlesungen zur Einführung in die Psychoanal…* (1916) | 568 ‰ | — |
| *Der Dichter und das Phantasieren* (1908) | 466 ‰ | — |
| *Traum und Telepathie* (1922) | 453 ‰ | — |
| *Über Psychoanalyse: Fünf Vorlesungen* (1910) | 440 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Mitteilungen wie die von _Pilcz_ würden hiezu stimmen, denen zufolge feste Beziehungen zwischen der Zeit des Träumens und dem Inhalt der Träume nachweisbar sind in der Weise, daß im tiefen Schlafe Eindrücke aus den ältes »
> — *Die Traumdeutung*, retrouvé dans l'édition de 1900 — daté avec certitude

**Réserve.** 40 concepts, la plus grosse grappe du corpus. Sa taille est elle-même un résultat : chez Freud le rêve n'est pas un objet parmi d'autres, c'est le modèle sur lequel l'appareil psychique est pensé. Une grappe aussi large discrimine moins qu'une petite — elle dit un voisinage massif, pas une articulation fine.

---

## 2. La fiction, la famille et la mort — 27 concepts, 11 708 atomes

*beobachtung, deckerinnerung, dichter, eltern, elternkomplex, erzaehlung, familie, geschwister, infantil, inversion, kastration, knabe_maedchen, maennlichkeit, mutter, name, oedipus, person, phantasie, pubertaet, realitaet, realitaetsprinzip, sterben, symbol, tod, todestrieb, vater, weiblichkeit.*

Le poète, le récit, le fantasme et le symbole, noués au roman familial — père, mère, fratrie, Œdipe, castration — et à la mort. Freud lit la fiction avec les outils de la clinique et le mythe familial comme une œuvre ; la partition les met ensemble.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Der Dichter und das Phantasieren* (1908) | 795 ‰ | — |
| *Eine Kindheitserinnerung aus »Dichtung und W…* (1917) | 714 ‰ | — |
| *Sammlung kleiner Schriften zur Neurosenlehre…* (1918) | 525 ‰ | — |
| *Das Motiv der Kästchenwahl* (1913) | 516 ‰ | — |
| *Drei Abhandlungen zur Sexualtheorie* (1905) | 505 ‰ | 514 ‰ |
| *Der Wahn und die Träume in W. Jensens »Gradi…* (1907) | 433 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Ich lernte erst später verstehen, daß sie mit ihm das initiale Trauma wiederholte, von dem ihre Neurose ausging, und habe seither das gleiche Verhalten bei anderen Personen gefunden, die in ihrer Kindheit sexuellen »
> — *Die Traumdeutung*, absent de l'édition de 1900 — ajouté entre 1900 et 1914

**Réserve.** 27 concepts. C'est un DÉPLACEMENT NET par rapport à l'état précédent : la famille appartenait à la grappe de la pulsion, elle a migré vers celle de la fiction. Les cinq volumes de la Sammlung, qui portent les grands cas cliniques racontés comme des récits, pèsent visiblement sur ce voisinage. À surveiller au prochain élargissement.

---

## 3. La clinique, la cure et la mémoire — 31 concepts, 11 472 atomes

*abwehr, anfall, arzt, assoziation, behandlung, conversion, erinnerung, erlebnis, forschung, gedaechtnis, hypnoid, hypnose, hysterie, krieg, lacheln, laehmung, nachtraeglichkeit, neurose, patient, projektion, psychoanalyse, spur, suggestion, symptom, trauma, uebertragung, vergessen, wahn, widerstand, zwang, zwangsneurose.*

Hystérie, symptôme, transfert, suggestion, hypnose ; la conversion, la paralysie, la crise. La mémoire y figure au premier rang — souvenir, trace, oubli, après-coup, souvenir-écran : « Hysterische leiden größtentheils an Reminiscenzen », écrivent Breuer et Freud en 1895. Se souvenir n'est pas ici une faculté, c'est le traitement même.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Sammlung kleiner Schriften zur Neurosenlehre…* (1893) | 551 ‰ | — |
| *Studien über Hysterie* (1895) | 542 ‰ | — |
| *Über Psychoanalyse: Fünf Vorlesungen* (1910) | 528 ‰ | — |
| *Vorlesungen zur Einführung in die Psychoanal…* (1917) | 432 ‰ | — |
| *Hemmung, Symptom und Angst* (1926) | 373 ‰ | — |
| *Sammlung kleiner Schriften zur Neurosenlehre…* (1905) | 350 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Es lag nun nahe, den Traum selbst wie ein Symptom zu behandeln und die für letztere ausgearbeitete Methode der Deutung auf ihn anzuwenden. (32) _Breuer_ und _Freud_, Studien über Hysterie, Wien 1895, 2. Aufl., 1909. »
> — *Die Traumdeutung*, retrouvé dans l'édition de 1900 — daté avec certitude

**Réserve.** 31 concepts. La grappe devait beaucoup aux « Studien über Hysterie » ; elle s'appuie désormais aussi sur les cinq cas cliniques entrés avec la Sammlung, ce qui la rend moins dépendante d'une œuvre unique. La GUERRE (« krieg ») l'a rejointe — les névroses de guerre sont traitées comme des traumatismes, non comme un fait d'histoire.

---

## 4. La pulsion, les instances, et la faute — 34 concepts, 8 255 atomes

*aggression, angst, autoerotismus, charakter, entwicklung, erogene_zone, es, fixierung, gewissen, ich, identifizierung, konflikt, latenzzeit, libido, masochismus, melancholie, mund, narzissmus, objekt, perversion, reaktionsbildung, regression, reue, sadismus, schuld, sexualitaet, spannung, strafe, sublimierung, trauer, trieb, ueberich, verbrechen, verleugnung.*

Libido, sexualité, stades du développement, perversion, narcissisme ; les instances — Moi, Ça, conscience morale — et le couple sadisme/masochisme avec l'agression ; la culpabilité, le remords, le châtiment, la mélancolie.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Drei Abhandlungen zur Sexualtheorie* (1905) | 601 ‰ | 651 ‰ |
| *Hemmung, Symptom und Angst* (1926) | 572 ‰ | — |
| *Eine Schwierigkeit der Psychoanalyse* (1917) | 511 ‰ | — |
| *Das Ich und das Es* (1923) | 453 ‰ | — |
| *Das Unbehagen in der Kultur* (1930) | 386 ‰ | — |
| *Vergänglichkeit* (1916) | 364 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Von zwei psychischen Bildungen, einer Affektneigung und einem Vorstellungsinhalt, die innig zusammengehören, hebt die eine, die aktuell gegeben ist, auch im Traume die andere; bald die somatisch gegebene Angst den unterd »
> — *Die Traumdeutung*, retrouvé dans l'édition de 1900 — daté avec certitude

**Réserve.** 34 concepts, et c'est la TRIPLE FUSION de cet élargissement : trois grappes autrefois distinctes — la pulsion, « la faute et le crime », « sadisme, masochisme, agression » — n'en font plus qu'une. Les deux petites étaient annoncées comme fragiles (192 et 178 atomes, « sensibles au moindre changement »), et elles l'étaient. Ce qui les a fondues est lisible : « Das Ich und das Es » et « Das Unbehagen in der Kultur » nouent en un seul tissu la pulsion de mort, l'agression retournée, le Sur-Moi et le sentiment de culpabilité.

---

## 5. Religion, anthropologie, culture et lien social — 22 concepts, 3 945 atomes

*aberglaube, allmacht, animismus, beruehrung, exogamie, fuehrer, gesellschaft, gott, institution, kultur, kunst, masse, moral, opfer, primitiv, religion, tabu, totem, unheimlich, urhorde, verbot, wissenschaft.*

Le totémisme, le tabou, le sacrifice, le dieu ; l'interdit moral, la masse et son meneur ; la culture, l'art, la science, l'institution. La névrose obsessionnelle y voisine le religieux — rapprochement que Freud pose lui-même dès 1907 dans « Zwangshandlungen und Religionsübungen » : le cérémonial du névrosé et le rite du croyant ont la même structure.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Totem und Tabu* (1913) | 542 ‰ | — |
| *Massenpsychologie und Ich-Analyse* (1921) | 423 ‰ | — |
| *Das Unheimliche* (1919) | 368 ‰ | — |
| *Zeitgemäßes über Krieg und Tod* (1915) | 312 ‰ | — |
| *Das Unbehagen in der Kultur* (1930) | 311 ‰ | — |
| *Der Moses des Michelangelo* (1914) | 198 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « So findet man den Totemismus heute bei den Völkern, die ihn noch zeigen, in den mannigfaltigsten Stadien des Verfalles, der Abbröckelung, des Überganges zu anderen sozialen und religiösen Institutionen, oder aber i »
> — *Totem und Tabu*, réimpression INCHANGÉE de 1913 (exemplaire de 1922) — texte d'origine, date certaine

**Réserve.** 22 concepts. « Das Unbehagen in der Kultur » y a fait entrer la CULTURE et l'INSTITUTION, qui manquaient à une grappe jusque-là surtout anthropologique. L'INQUIÉTANTE ÉTRANGETÉ (« unheimlich ») y figure aussi, ce qui se discute : elle relève autant de l'esthétique.

---

## 6. Le corps regardé — 7 concepts, 2 195 atomes

*auge, bart, gesicht, hand, koerper, kopf, schmerz.*

Sept concepts, et rien d'autre : l'œil, le visage, la main, la tête, la barbe, le corps, la douleur. Ce n'est pas une thèse de Freud, c'est ce qu'il DÉCRIT quand il décrit — le corps d'un patient, d'une statue, d'un tableau.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Der Moses des Michelangelo* (1914) | 318 ‰ | — |
| *Studien über Hysterie* (1895) | 168 ‰ | — |
| *Vergänglichkeit* (1916) | 136 ‰ | — |
| *Drei Abhandlungen zur Sexualtheorie* (1905) | 119 ‰ | 134 ‰ |
| *Das Unheimliche* (1919) | 86 ‰ | — |
| *Der Wahn und die Träume in W. Jensens »Gradi…* (1907) | 69 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Ich glaubte annehmen zu dürfen, dass jene ersten Schmerzen wirklich ohne psychischen Anlass als leichte rheumatische Erkrankung gekommen seien, und konnte noch erfahren, dass dies organische Leiden, das Vorbild der späte »
> — *Studien über Hysterie*, édition d'origine (1895) — date certaine

**Réserve.** GRAPPE NOUVELLE, et elle vaut surtout comme mise en garde. Elle s'est détachée de la clinique parce que le corpus élargi contient davantage de description : les cas de la Sammlung détaillent des corps, et le Moïse comme le Léonard décrivent des œuvres. Un voisinage de VOCABULAIRE DESCRIPTIF n'est pas un courant de pensée, et la partition ne sait pas faire la différence.

---

## 7. Les actes manqués — 3 concepts, 384 atomes

*fehlleistung, vergreifen, versprechen.*

Trois concepts : l'acte manqué, le lapsus, la méprise. Le lapsus révèle une intention contraire — c'est par là que Freud choisit de commencer son enseignement, avant même le rêve, parce que c'est le fait le plus quotidien et le moins contestable.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Vorlesungen zur Einführung in die Psychoanal…* (1916) | 274 ‰ | — |
| *Zur Psychopathologie des Alltagslebens* (1901) | 76 ‰ | 108 ‰ |
| *Vorlesungen zur Einführung in die Psychoanal…* (1916) | 13 ‰ | — |
| *Einige Charaktertypen aus der psychoanalytis…* (1916) | 4 ‰ | — |
| *Das Ich und das Es* (1923) | 4 ‰ | — |
| *Vorlesungen zur Einführung in die Psychoanal…* (1917) | 3 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Es liegt nicht auf meinem Wege, diese Frage zu beantworten. V. Seit den Erörterungen über das Versprechen haben wir uns begnügt, zu beweisen, dass die Fehlleistungen eine verborgene Motivierung haben, und uns mit dem Hi »
> — *Zur Psychopathologie des Alltagslebens*, absent de l'édition de 1901 — ajouté entre 1901 et 1904

**Réserve.** GRAPPE NOUVELLE, et son apparition a une cause unique et vérifiable : le premier tome des « Vorlesungen » (1916) leur est ENTIÈREMENT consacré, quatre leçons sur quatre. Avant lui, ces trois concepts se dispersaient dans la Psychopathologie sans former de voisinage propre. Une grappe peut donc naître d'un seul volume — ce qu'elle mesure alors est autant un fait d'édition qu'un fait de doctrine.

---

## 8. La peinture et le pacte — 3 concepts, 225 atomes

*malerei, pakt, teufel.*

Trois concepts seulement, tirés de deux œuvres : le Moïse de Michel-Ange et la névrose démoniaque du peintre Haizmann.

| Œuvre | Densité | Dont d'origine |
|---|---:|---:|
| *Eine Teufelsneurose im siebzehnten Jahrhunde…* (1923) | 436 ‰ | — |
| *Eine Kindheitserinnerung des Leonardo da Vin…* (1910) | 31 ‰ | — |
| *Der Moses des Michelangelo* (1914) | 14 ‰ | — |
| *Der Dichter und das Phantasieren* (1908) | 11 ‰ | — |
| *Das Motiv der Kästchenwahl* (1913) | 8 ‰ | — |
| *Das Unheimliche* (1919) | 5 ‰ | — |

Citation choisie par l'agent — le passage qui croise le plus de concepts de la grappe, à la longueur la plus proche d'une thèse théorique :

> « Es besteht also aus drei Teilen: 1. einem farbigen Titelblatt, welches die Szene der Verschreibung und die der Erlösung in der Kapelle von Mariazell darstellt; auf dem nächsten Blatt sind acht ebenfalls farbige Zeichnun »
> — *Eine Teufelsneurose im siebzehnten Jahrhundert*, édition d'origine (1923) — date certaine

**Réserve.** CONTRE-EXEMPLE À GARDER SOUS LA MAIN, et il a SURVÉCU au doublement du corpus, ce qui le rend plus instructif encore. « teufel » et « pakt » n'ont rien à faire avec la peinture — ils y sont parce que l'unique œuvre sur le diable porte sur un peintre. Cooccurrence réelle, lien conceptuel absent.

---


## Ce que les dossiers disent ensemble

1. **Les grappes ne sont pas données d'avance** : leur nombre, leur taille et leur composition
   sont mesurés, et ils BOUGENT quand l'ontologie s'affine. L'audit 4 du lexique (2026-07) a
   recomposé la partition en profondeur — la clinique s'est détachée en grappe propre, la
   différence des sexes a rejoint le roman familial, la seconde topique a cessé d'être isolée.
   Une grappe est donc un état de la mesure, pas une vérité sur Freud.
2. **Certaines grappes sont des faits de corpus autant que de pensée** : la peinture est portée
   par trois analyses d'œuvres, la masse par un seul livre. Le dire est la condition pour
   comparer un jour ces grappes à celles d'un autre auteur sans sur-interpréter.
3. **Les grappes bougent aussi dans le temps** — la mort migre de la famille vers la pulsion, le
   rêve cesse d'absorber la métapsychologie (voir `SYNTHESE_FREUD.md` §3, avec le contrôle qui
   exclut les ajouts datés par collation).

*Reproduire : `python bin/analyser.py --agent courants` · citations : `python
bin/rechercher.py --concept <nom>` · méthode et limites : `INVENTAIRE_ATOMES.md` §4.*
