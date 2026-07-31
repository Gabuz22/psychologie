#!/usr/bin/env python3
"""LEXIQUE DE WILHELM STEKEL (1868-1940) — construit sur SON vocabulaire.

Stekel apporte la QUATRIÈME forme du rapport au maître, celle qui manquait au corpus. Rank déplace
une thèse et rompt ; Abraham prolonge et ne rompt jamais ; Ferenczi reste vingt ans le plus proche
et diverge sur la technique. Stekel, lui, **rompt le premier et sur la doctrine** : cofondateur
avec Freud de la Société psychologique du mercredi en 1902, il quitte la Société en 1912.

Et cette rupture est DATÉE DANS LE CORPUS, des deux côtés, avant qu'elle ait lieu :

  • en 1907, Stekel ouvre son premier livre par « Ich bekenne mich stolz als seinen Schüler,
    womit ich nicht sagen will, daß Alles, was ich ausführe, seinen Anschauungen entspricht.
    Im Gegenteil! » ;
  • en 1908, Freud préface le suivant et prend ses distances dans le même geste — « mein direkter
    Einfluß auf das vorliegende Buch … sei ein sehr geringer gewesen », « nur die Bezeichnung
    „Angsthysterie" geht auf meinen Vorschlag zurück ». Cette préface est dans le corpus, déclarée
    en `contributions` et attribuée à Freud.

Les six volumes retenus vont de 1907 à 1917 : le corpus tient donc l'avant et l'après.

SES SIGNATURES, MESURÉES contre les 1 231 000 mots des autres auteurs allemands du corpus. Le
rapport donné est celui des fréquences relatives.

  onani*         1 441 chez lui contre 295   → ×15,2   SA question, celle de la rupture de 1912
  bipolar           39 contre 2              → ×40,7   son concept théorique propre
  bisexuell        145 contre 34             → ×13,0
  heterosexuell    199 contre 51             → ×12,0
  homosexuell      883 contre 283            → ×9,7
  angsthysteri     189 contre 61             → ×9,5    le terme que Freud dit lui avoir suggéré
  angstneuros      434 contre 241            → ×5,6
  pollution        122 contre 86             → ×4,4
  verbrech         302 contre 258            → ×3,6

CE QUE LE LEXIQUE NE CONTIENT PAS, ET POURQUOI — mesuré, non supposé :

  parapathie     5 occurrences. C'est SON néologisme le plus connu (il rebaptise ainsi la névrose)
                 — mais il l'impose après 1920, et le corpus s'arrête en 1917. Le concept est
                 absent du corpus, pas de l'auteur. À reprendre si ses volumes tardifs entrent.
  aktualneurose  2 occurrences chez lui contre 35 ailleurs (rapport 0,2). C'est pourtant l'un des
                 deux points doctrinaux de la rupture de 1912 — et le corpus montre que la
                 querelle ne se lit PAS dans ce mot chez lui. Fait mesuré, contraire à l'attente.
  skopophilie    0 occurrence.  lebensangst  0 occurrence.
  zwang          rapport 0,7 — moins fréquent chez lui qu'ailleurs. Ce n'est pas sa question.
  psychosexuell  2 contre 115 (rapport 0,1).  frigiditat  4 contre 41.  masochismus  rapport 0,7.

Toutes les fréquences sont mesurées sur les six volumes retenus, 5,2 millions de signes — le
troisième corpus du projet après Freud et Ferenczi. Elles l'ont été APRÈS le retrait du bandeau
de numérisation : deux de ces volumes viennent de scans Google, et « google » y était le troisième
mot le plus caractéristique de l'auteur avant nettoyage (voir `ocr.retirer_bandeau_scan`).
"""

LANGUE = "de"

CONCEPTS = {
    # =========================================================== SA QUESTION PROPRE : L'ONANISME
    # C'est l'un des deux points sur lesquels il rompt avec Freud en 1912, et de loin son
    # vocabulaire le plus distinctif. Un volume entier lui est consacré (1917).
    "onanie": {
        "label": "L'onanisme et ses équivalents",
        "termes": {
            # LE MOTIF EST OUVERT À GAUCHE, et c'est l'audit qui l'a imposé. Le moteur borde
            # chaque motif (`re.compile(r"\b" + m)`), de sorte que « onani » nu manquait les
            # composés où le mot n'est pas en tête : kinderonanie (7), säuglingsonanie (5),
            # notonanie (4) — des termes de Stekel, précisément ceux qui font sa question.
            # Mesuré : 1 263 atomes avant, 1 277 après. La liste portait en outre « onani »
            # DEUX FOIS, doublon inerte.
            "onanie": ["[a-z]*onani"],
            "pollution": ["pollution"],
            "abstinenz": ["abstinen", "enthaltsamkeit"],
        },
    },
    # ================================================== SA SECONDE QUESTION : L'ORIENTATION SEXUELLE
    # « Onanie und Homosexualität » (1917) porte le sous-titre « Die homosexuelle Neurose » : pour
    # lui l'homosexualité est une NÉVROSE, thèse qu'il faut lire telle qu'elle est écrite et que
    # ce corpus n'a pas à corriger. Son interlocuteur constant est Magnus Hirschfeld (87 mentions
    # contre 9 dans tout le reste du corpus), qui soutenait l'inverse.
    "geschlechtsrichtung": {
        "label": "Homosexualité, bisexualité et « inversion »",
        "termes": {
            # « homoerot » retiré : 2 occurrences, toutes deux dans une même note citant un titre
            # de Ferenczi — 0 atome propre.
            "homosexualitaet": ["homosexual", "homosexuell"],
            "heterosexualitaet": ["heterosexual", "heterosexuell"],
            # « bisexualitat » est déjà contenu dans « bisexual » : 51 occurrences comptées deux
            # fois, 0 atome gagné.
            "bisexualitaet": ["bisexual", "bisexuell"],
            # « urninde » n'attrapait RIEN : la forme imprimée dans ces volumes est « Urlinde »
            # (le féminin d'Urning chez Ulrichs). Relevée dans le texte, elle rend 9 atomes.
            "inversion": ["inversion", "invertiert", "urning", "urlinde"],
        },
    },
    # ================================================================ L'ANGOISSE COMME OBJET PROPRE
    # Son grand livre de 1908. « Angsthysterie » est le terme que Freud déclare lui avoir suggéré
    # dans sa préface — l'un des rares emprunts de vocabulaire que le corpus puisse DATER et
    # ATTRIBUER par une déclaration écrite, et non par mesure.
    "angst": {
        "label": "L'angoisse, ses états et ses crises",
        "termes": {
            "angsthysterie": ["angsthysteri"],
            "angstneurose": ["angstneuros"],
            # « angstanfalle » est déjà pris par « angstanfall » : 82 occurrences, 0 atome gagné.
            "angstanfall": ["angstanfall", "angstattack"],
            # MOTIF MORT RETIRÉ. « angstgefühl » avec tréma ne peut JAMAIS se déclencher : le
            # lexique s'applique sur `segmentation.replier`, qui supprime les diacritiques. Zéro
            # occurrence sur les 21,8 millions de signes du corpus allemand. La même faute est
            # corrigée plus bas sur `nervosität` et `schuldgefühl` — trois fois la même.
            "angstgefuehl": ["angstgefuhl"],
            # « todesgedanke » retiré : il apportait 56 des 82 atomes, dont 54 sans un seul mot
            # d'angoisse et 15 explicitement des VŒUX de mort (« Hass- und Todesgedanken »).
            # Souhaiter la mort d'un autre n'est pas la craindre pour soi.
            "todesangst": ["todesangst", "todesfurcht"],
            "herzangst": ["herzangst", "herzneuros", "herzklopfen"],
            # RÉTABLI — L'AUDIT PRÉCÉDENT L'AVAIT RETIRÉ À TORT, ET LE RETRAIT ÉTAIT MESURABLEMENT
            # FAUX. Le motif d'alors, `phobie` nu, donnait ×0,70-0,92 et on en a conclu « il en
            # parle moins que les autres, ce n'est pas son mot ». Le chiffre ne mesurait pas le
            # concept : IL MESURAIT UN MOTIF INCOMPLET. La note de retrait le disait elle-même sans
            # en tirer la conséquence — « le motif manquait ses vraies phobies à lui : topophobie
            # (10), erythrophobie (6), nosophobie (12), tandis que klaustrophob faisait 0 ».
            #
            # LA CAUSE EST STRUCTURELLE, et elle vaut pour tout le dépôt : l'allemand met la tête
            # du composé à la FIN, le moteur borde chaque motif au DÉBUT. Un mot-concept qui vit
            # surtout en second élément est donc invisible à son propre concept. C'est la même
            # cause qui faisait rater kinderonanie à `onani`, et 27 composés à `symptom`. La leçon
            # avait été apprise une fois, pour `onani`, et jamais étendue.
            # Motif complété : ×0,70 → ×1,17, 85 → 149 occurrences. La correction était le motif,
            # pas le retrait.
            #
            # DEUX GARDES, mesurées et non supposées :
            #   • `(?!os)` écarte PHOBOS et DEIPHOBOS — le fils de Priam, dans les pages de mythe.
            #   • les phobies allemandes sont ÉNUMÉRÉES et non captées par `[a-z]*angst`, qui
            #     attraperait « längst » (« depuis longtemps ») 50 fois : le repli supprime le
            #     tréma, et l'ouverture à gauche ne se décide jamais en aveugle.
            "phobie": [
                r"[a-z]*phob(?!os)",
                "platzangst", "prufungsangst", "eisenbahnangst", "brustangst", "bergangst",
                "strassenangst", "sexualangst", "prakordialangst", "bruckenangst",
            ],
        },
    },
    # ============================================================ SON CONCEPT THÉORIQUE : LA BIPOLARITÉ
    # « Alles seelische Geschehen wird von dem Gesetze der „Bipolarität" beherrscht » — c'est la
    # PREMIÈRE PHRASE de « Die Sprache des Traumes » (1911). Trente-neuf occurrences chez lui,
    # deux dans tout le reste du corpus : c'est sa thèse, et elle n'appartient qu'à lui.
    "bipolaritaet": {
        "label": "La bipolarité de la vie psychique",
        "termes": {
            # SEUL RESCAPÉ DU GROUPE, et l'audit a fait mieux que le confirmer : il a montré que
            # les deux autres étaient EMPRUNTÉS. « ambivalenz » compte 0 occurrence sur les
            # 5 222 046 signes de Stekel, contre 269 chez les autres — c'est le mot de Bleuler,
            # que Stekel cite quinze fois sans jamais reprendre son concept. Écrire ce
            # sous-concept, c'était prêter à un auteur le vocabulaire de ses contemporains.
            "bipolaritaet": ["bipolar"],
        },
    },
    # ================================================================ LE RÊVE ET SON LANGAGE
    # Sa spécialité reconnue, et le seul point où Freud le cite abondamment : « die reichste
    # Sammlung von Symbolauflösungen ». Seize atomes de la Traumdeutung le discutent.
    "traumsprache": {
        "label": "Le langage du rêve et ses symboles",
        "termes": {
            # LA GARDE ÉTAIT TROP LARGE, et c'est l'audit qui l'a montré. `traum(?!a)` écartait
            # bien `Trauma` et `traumatisch` — mais aussi 74 mots du RÊVE : Traumanalyse (39),
            # Traumarbeit (12), Traumanlaß (6). En voulant éviter un faux positif connu, on
            # perdait le vocabulaire technique de l'auteur du « Langage du rêve ». La garde
            # nomme donc maintenant ce qu'elle exclut, au lieu d'exclure une lettre :
            # +51 atomes mesurés. « traume », « traumt », « traumer » sont redondants (0 atome
            # propre) puisque le motif est un préfixe.
            "traum": [r"traum(?!at|a\b|as\b)"],
            # « symbolauflosung » attrapait 0 occurrence : c'est la formule de FREUD *sur*
            # Stekel, citée dans le commentaire de ce fichier — pas un mot de Stekel. Le piège
            # est instructif : on avait tiré un motif de l'éloge d'un tiers.
            "traumsymbol": ["traumsymbol", "symbol"],
            "traumdeutung": ["traumdeut", "traumanalys"],
            # « sprache des traumes » nu apportait 35 atomes dont 22 (63 %) sont le TITRE de son
            # propre livre — réclames de l'éditeur Bergmann, lignes de signature de cahier, notes
            # à numéro de page. Le motif exige donc maintenant un contexte de phrase.
            "traumsprache": [
                "traumsprache",
                r"in der (?:\w+ )?(?:\w+ )?sprache des traumes",
                r"sprache des traumes (?:heisst|bedeutet|benutzt|ist|zu |nicht|versteh|kennt|lehrt)",
            ],
            # « stereotyp » nu prenait 7 atomes non oniriques (stereotype Antwort, Klage, Phrase).
            # Le motif éponyme « wiederholungstraum » fait 0 occurrence : Stekel écrit
            # « stereotyper Traum ».
            "wiederholungstraum": [
                r"stereotyp(?!\w*\s+(?:antwort|klage|phrase|wort|vorstellung|frage|redensart))"],
            # « traumer » attrapait Träumerei (3), Traumerzählung (2), Traumerscheinung (2) et
            # « die „Träumerei" von Schumann ». La garde les nomme.
            "traeumer": [r"traumer(?!ei|scheinung|zahlung|kundigung|lebnis|innerung|isch)",
                         "traumende"],
        },
    },
    # ================================================================ LE ROMAN FAMILIAL
    # Il lit les rêves par la famille, et son vocabulaire le montre : 661 « Mutter », 292
    # « Bruder », 257 « Schwester ». La FRATRIE y pèse plus que chez Freud — chez Stekel, le
    # frère et la sœur sont des figures de rêve de premier plan, pas des comparses.
    "familie": {
        "label": "La famille, la fratrie et l'inceste",
        "termes": {
            "mutter": ["mutter", "mutterlich"],
            "vater": ["vater", "vaterlich"],
            "geschwister": ["bruder", "schwester", "geschwister"],
            # « madchen » RETIRÉ, et c'est le retrait le plus lourd de l'audit : 606 atomes.
            # Il déclenchait seul sur 597 d'entre eux, et la lecture y trouve 160 marqueurs
            # d'ADULTE contre 40 d'enfant — chez Stekel, « Mädchen » désigne le plus souvent une
            # jeune femme, patiente ou prostituée, non une petite fille. Le sous-concept tombe de
            # ×1,12 à ×1,00 : tout son excédent apparent venait de ce mot. Les autres motifs sont
            # des préfixes de « kind » et n'ajoutaient rien.
            "kind": ["kind", "knabe"],
            "inzest": ["inzest", "blutschande"],
            "ehe": ["ehefrau", "ehemann", "gatte", "gattin", "heirat"],
        },
    },
    # ================================================== LES SYMBOLES CONCRETS DU RÊVE
    # « Die Sprache des Traumes » est un DICTIONNAIRE de symboles : l'eau, l'escalier, la
    # chambre, la rue reviennent comme des entrées. Ces mots ne sont pas du décor, ils sont
    # l'objet même du livre — et c'est ce que Freud lui reconnaît (« die reichste Sammlung von
    # Symbolauflösungen ») tout en refusant d'en généraliser le principe.
    "traumbilder": {
        "label": "Les images concrètes du rêve",
        "termes": {
            # « see » RETIRÉ. Il coûtait 609 atomes, dont 590 sont L'ÂME : seele (255),
            # seelischen (58), seelische (38), seelenleben (35), seelenarzt (22) — contre
            # 19 vrais lacs. Dans un corpus de psychologie, un motif qui attrape « Seele » ne
            # mesure pas ce qu'il prétend, il mesure le sujet du livre.
            # `fluss` A ÉTÉ ACCUSÉ D'ATTRAPER « flüssig » (le repli confond Fluß et flüssig), ET
            # L'ACCUSATION NE TIENT PAS À LA LECTURE : sur les 26 occurrences de la famille
            # « flüssig », 21 sont le liquide lu COMME symbole onirique — « diese Gleichung nimmt
            # alle Flüssigkeiten auf: Milch, Öl, Petroleum, Tränen », « eine weisse, seifenartige
            # Flüssigkeit… als phallisches Symbol ». Dans un dictionnaire où l'eau EST l'urine et
            # le sperme, ce n'est pas du bruit, c'est le concept. Une garde `fluss(?!ig)` coûterait
            # 19 atomes légitimes pour en retirer 6. Erreurs dures réelles : 7 sur 70 (10 %), dont
            # « überflüssig » et « unbeeinflusst » coupés à la ligne par l'OCR.
            "wasser": ["wasser", "meer", "fluss", "schwimm", "ertrink"],
            # QUATRE DÉFAUTS MESURÉS, dont un motif entièrement mort. Le sous-concept perd un quart
            # de ses atomes et son rapport MONTE (×3,17 → ×3,25) : ce qui part est du bruit.
            #
            #   dachboden  0 OCCURRENCE sur 5,1 millions de signes. Ce n'est pas la faute du tréma
            #              (le mot n'en a pas) : le référent est absent du corpus. Témoins relevés
            #              — dachkammer 2, mansarde 2, dachstube 0, dachzimmer 0.
            #   keller     LE PIÈGE DU VOLUME UNIQUE, POUR LA TROISIÈME FOIS. 29 de ses 53 atomes
            #              sont dans « Die Träume der Dichter » et 18 nomment GOTTFRIED ou PAUL
            #              KELLER, les écrivains. C'est la mécanique de `rundfrage` et de
            #              `genitaltheorie` — un compte porté par un seul livre, et d'autant plus
            #              convaincant qu'il est nul chez les autres, puisque personne d'autre n'a
            #              écrit ce livre-là. Mais ce n'est PAS du paratexte : c'est un nom propre
            #              en pleine prose, que le détecteur de tête courante ne voit pas (5 %).
            #              L'ancre locative garde les vraies caves, 18 en tout.
            #   haus       175 des 344 « hause » sont l'ADVERBE (« nach Hause », « zu Hause »), et
            #              8 % seulement portent un mot du rêve : c'est de la prose clinique, « der
            #              Patient kam nach Hause ». S'y ajoute le vocabulaire domestique
            #              (hausarzt, hausfrau, haushalt) — des rôles, pas l'image d'une maison.
            #   tur        69 des 227 occurrences (30 %) sont la TOUR (turm 19, turme 7, turmen 4),
            #              le GYMNASTE (turner 7, turnen 3, turnte 3) et le TURC (turkische 3).
            #              La première correction essayée était `tur(?!m|n|k)` — la garde par lettre
            #              suivante, interdite — et elle tuait « Türklinke », une vraie poignée de
            #              porte. Remplacée par la famille morphologique positive.
            #
            # `turm` reste un VRAI symbole de Stekel (« der Turm wird häufig für den Penis
            # gebraucht ») : il ne disparaît pas du lexique, il n'appartient pas à ce groupe-ci.
            "raum": [
                r"zimmer(?!mann|maim|gesell|temperatur)",
                r"(?<!nach )(?<!zu )haus(?:e|es|er|ern|chen|erl)?\b",
                "haustor", "haustur", "hausture", "hausflur", "haussymbol",
                "wohnung",
                r"tur(?:e|en|chen)?\b",
                "turklinke", "turschnalle", "turoffnung", "turhaken", "tursymbo",
                "fenster",
                r"(?:im|in de[nmr]|in eine[nm]|aus dem|de[sm]|eine[nm]|tiefe[nr]?|lange[nr]?)\s+keller",
                "kellerstiege", "kellergewolbe", "kellerloch", "kellertraum", "kellermeister",
            ],
            # « weg » RETIRÉ, pour une raison plus profonde qu'un faux positif : il attrapait
            # « wegen » (240 fois, « à cause de »), mais surtout le repli SUPPRIME LES MAJUSCULES,
            # et l'allemand ne distingue le substantif « Weg » (le chemin, un symbole du rêve) de
            # l'adverbe « weg » (parti, au loin) que par elle. Le motif était donc indécidable par
            # construction, non seulement imprécis. Les composés sans ambiguïté sont gardés.
            "weg": ["strasse", "treppe", "stiege", "bruck", "reise", "eisenbahn"],
            # DEUX RETRAITS, ET UNE RÉSERVE DE GROUPE ÉCRITE MAIS NON APPLIQUÉE.
            #
            # L'accusation portée d'abord était que `penis`/`vagina`/`genital` seraient du
            # vocabulaire CLINIQUE mal rangé. La mesure la RÉFUTE : 73 % des `penis` et 83 % des
            # `vagina` sont dans « Die Sprache des Traumes » (base : 37 %), contre 23 % pour le
            # témoin clinique `koitus` et 31 % pour `impotenz` ; et Stekel les déclare lui-même
            # symboles — 41 énoncés « X ist ein Symbol des Penis », 10 pour vagina, 0 pour brust.
            #
            #   genital  RETIRÉ. 162 occurrences chez lui contre 1 208 au témoin → ×0,43. C'est le
            #            vocabulaire commun du champ analytique, pas le sien, et aucune sous-forme
            #            n'est récupérable (genitale ×0,63, genitalsymbol ×0,40). Même faute que
            #            `ambivalenz` : prêter à un auteur le mot de ses contemporains.
            #   brust    RETIRÉ. Seul motif du sous-concept À LA LIGNE DE BASE du corpus — 37 %
            #            dans le dictionnaire des rêves contre 37 % pour un atome quelconque. Du
            #            `brust` nu (96), 23 % seulement sont le sein ; ~40 % sont l'idiome « in
            #            der Brust », siège du sentiment (« zwei Seelen wohnen ach in meiner
            #            Brust »). S'y ajoutent `brustung` (5) = le PARAPET, et l'anatomie
            #            descriptive (brustkorb, brustgegend, brustseite). Le sens « sein » est
            #            porté par `busen` (×13,23), qui est le mot de son dictionnaire et dont il
            #            liste les symboles : balcon, terrasse, corniche, laiterie.
            #
            # RÉSERVE DE GROUPE, MESURÉE ET NON TRANCHÉE ICI. Dans un dictionnaire de symboles, un
            # mot est soit l'IMAGE, soit le SENS. Comptés sur les tournures de symbolisation, les
            # motifs de `koerperbild` sont 12 fois du côté image contre 52 du côté sens, quand les
            # images vraies du groupe (strasse, wasser, zimmer, pferd, vogel) sont 15 contre 1 :
            # « Die Stiege symbolisiert die Vagina » — l'escalier est l'image, le vagin est le
            # sens. Ce sous-concept relèverait donc de `traumsprache`, non de `traumbilder`.
            # Déplacer un sous-concept de groupe recompose les grappes et invalide l'éditorial qui
            # les décrit : la mesure est écrite ici, la décision revient à une passe qui la traite
            # avec ses conséquences.
            "koerperbild": ["vagina", "penis", "membrum", "busen"],
            # DEUX GARDES, chacune sur une famille morphologique ÉNUMÉRÉE — jamais sur la lettre
            # d'après. Contrôlé : aucune forme de chien ni de chat n'est perdue.
            #
            #   hund   attrape LE NOMBRE « cent » : hundert 9, hunderte 8, hunderten 2, hundertmal
            #          2, hunderttausende 2, hundertfache 1, hundertsten 1 — 25 occurrences sur
            #          196, et 18 atomes de Stekel étaient classés « image d'animal dans le rêve »
            #          pour la seule raison que la phrase disait « cent ». L'OCR recolle en outre
            #          des « jahr- hundert » coupés à la ligne.
            #   katze  attrape `Katzenjammer` (la gueule de bois, 7) et `Katzensteg` (5) — qui est
            #          le roman de Sudermann et, chez Stekel, une PASSERELLE analysée comme telle
            #          (« der Katzensteg ist die Vagina ») : un pont, donc, pas un animal.
            #          12 occurrences sur 45.
            #
            # Le sous-concept est par ailleurs le MIEUX FONDÉ de son groupe : enrichissement en
            # marqueurs oniriques ×2,44 contre ×1,63 pour `wasser` et ×1,65 pour `zimmer`, et le
            # chapitre XV de « Die Sprache des Traumes » s'intitule « Was die Tiere im Traume
            # bedeuten ». Sa tête courante, elle, est détruite par l'OCR (« tiero ini tniuino ») et
            # ne déclenche donc presque pas — 7 % de paratexte, sans commune mesure avec les 87 %
            # de `rundfrage`.
            "tier": ["tier", "schlange", "pferd", r"hund(?!ert)", "vogel",
                     r"katze(?!njammer|nsteg|nst\b)"],
            # UN MOTIF TROP LARGE ET UN TROP ÉTROIT — les deux mesurés, les deux corrigés.
            #
            #   grab       17 occurrences fautives sur 125. Trois choses qui ne sont pas des
            #              tombes : GRABBE (2), le poète Christian Dietrich Grabbe, cité dans
            #              « Dichtung und Neurose » parmi « Gogol, Raimund, Grabbe und Lenau » ;
            #              DER GRABEN (9), la rue de Vienne (« am Graben gehen die Dirnen
            #              spazieren ») ; et le proverbe « wer andern eine Grube gräbt » (grabt 4).
            #              Plus `grabtiere`, OCR de « Raubtiere ». La famille est donc ÉNUMÉRÉE.
            #              Contrôlé : les 28 « grabe » et 7 « graber » sont tous le substantif —
            #              zéro « ich grabe ».
            #   begrabnis  DÉFAUT INVERSE, et personne ne l'avait vu : le motif s'arrête au
            #              substantif et rate le VERBE de son propre mot. `begrab` capte 46
            #              occurrences (begraben 29, begrabnis 7, begrabnisses 2, begrabt 2…)
            #              contre 9 — toutes des inhumations. Détail révélateur : 3 des 9 actuelles
            #              ne se déclenchent que parce que l'OCR coupe « be- grabnis » à la ligne.
            #              Le motif marchait en partie par accident.
            "tod_bild": [
                "friedhof", "leiche", "sarg", "begrab",
                r"grab\b", r"grabe\b", "grabes", "grabern", r"graber\b", "grabstein",
                "grabkreuz", "grabgewolbe", "grabphantasie", "grabhugel",
            ],
        },
    },
    # ================================================================ LA NÉVROSE ET LA MORT
    # CE GROUPE EST CELUI QUI A LE PLUS APPRIS À LA MÉTHODE, et pas du tout comme on l'attendait.
    # Quatre de ses six sous-concepts affichaient un rapport < 1 — le critère qui avait servi à
    # retirer cinq sous-concepts à l'audit précédent. Aucun des quatre n'est tombé, et c'est le
    # critère qui a dû être précisé. Voir la note « LE RAPPORT < 1 » en fin de fichier.
    "neurose": {
        "label": "La névrose, le symptôme et la mort",
        "termes": {
            # GARDÉ malgré ×0,92, et le composite masque une INVERSION : `neurotik` mesure ×1,79
            # quand `neuros` fait ×0,81. Au niveau de la forme, « Neurose » au singulier vaut
            # ×1,38 contre ×0,38 au pluriel. Freud parle DES névroses, la classe ; Stekel parle DU
            # NÉVROSÉ — « Neurotiker » 288 fois, ×2,11. On ne peut pas séparer les deux sans
            # couper un mot de sa flexion. En médiane par œuvre, Stekel est 3e sur 5, AU-DESSUS de
            # Freud (215,5 contre 111,6 par million de signes).
            # Et le dénominateur était pollué par le piège du volume unique, CÔTÉ TÉMOIN : 13 % des
            # `neuros` de Freud sont « Neurosenlehre », tête courante de trois de ses volumes.
            "neurose": ["neuros", "neurotik", "neurotisch"],
            # OUVERT À GAUCHE, comme `onani` et pour la même raison — l'allemand met la tête du
            # composé à la FIN, le moteur borde au DÉBUT. Le motif nu ratait 27 occurrences de son
            # propre vocabulaire : krankheitssymptome (5), angstsymptome (3+1), hauptsymptom (2+1),
            # abwehrsymptome (2), kardinalsymptom (1+1), begleitsymptome, fettherzsymptome…
            # +23 atomes, rapport inchangé. Sans risque : en allemand, tout mot finissant par
            # « …symptom » EST un composé de Symptom.
            "symptom": ["[a-z]*symptom"],
            # GARDÉ, motif inchangé. L'emploi ORDINAIRE de « verdrängen » (chasser, évincer) a été
            # cherché de deux façons — filtre à haut rappel sur 470 occurrences, puis lecture d'un
            # échantillon de 120 formes verbales : ≤ 3,3 %, borne haute. Les deux seuls cas nets
            # sont « das elektrische Licht verdrängte das Petroleum » et un concurrent évincé.
            # Restreindre au nominal coûterait 249 atomes (−56 %) pour éviter au plus 16
            # occurrences : refusé, chiffre à l'appui.
            "verdraengung": ["verdrang"],
            # LE SOUS-CONCEPT LE PLUS MAL CONSTRUIT DU LEXIQUE, et le seul dont le défaut se lisait
            # DANS LE BANC sans qu'on le voie : deux de ses cinq motifs étaient entièrement
            # absorbés par un autre.
            #   `todes`  ⊂ `tod`    → 0 atome propre, 405 occurrences comptées deux fois
            #   `sterben` ⊂ `sterbe` → 0 atome propre, 380 occurrences comptées deux fois
            # 33 % du compte affiché était fictif. C'est le cas `bisexualitat`/`bisexual` déjà
            # corrigé plus haut, en huit fois plus gros — et il a fallu qu'un contradicteur le
            # trouve pour qu'on répare aussi le banc, qui comptait par MOTIF au lieu de par mot.
            #
            # Trois trous mesurés, comblés : `stirb` (61 occurrences de « stirbt », absent alors
            # que le lexique de Freud l'a), `sterb` qui rend en plus sterblich/sterblichkeit et
            # mesure ×4,70 — le motif le plus stekelien du sous-concept —, et la famille `toten`
            # (×2,11), 402 atomes de « die Toten » qui étaient hors champ.
            # ÉCARTÉ SUR MESURE, PAS SUR INTUITION : `tot(?!al)` entier rendrait +392 atomes mais
            # ferait tomber le sous-concept à ×1,95 (`tote` ×1,06, `totet/totung` ×0,30 — du
            # vocabulaire commun). On garde `toten`, on laisse le reste.
            #
            # RÉSERVE ÉCRITE, NON APPLIQUÉE : le nominal (`tod`, 1 017 atomes, ×2,28) NOIE le
            # verbal (`sterb`/`stirb`/`gestorben`, 560 atomes, ×3,61) — la même figure que le
            # renversement schuldgefuhl/schuldbewusstsein instruit plus bas. Le lexique de Freud
            # sépare déjà `tod` et `sterben` en deux sous-concepts. Scinder changerait la maille du
            # groupe : mesuré ici, à décider ailleurs.
            "sterben": ["sterb", "stirb", "gestorben", "tod", "toten"],
            # `freitod` RETIRÉ : 0 occurrence sur 5 222 046 signes. Le mot est POSTÉRIEUR au corpus.
            # Même faute de catégorie que `angstgefühl` et `nervosität` — un motif écrit d'intention
            # et jamais vérifié. Delta : 0 atome, 0 occurrence.
            # Le sous-concept, lui, résiste au piège du paratexte : les 122 atomes ont été lus, 3
            # sont une réclame de l'éditeur Bergmann et 3 des renvois de Stekel à SA PROPRE
            # contribution — 5 % en tout, contre 87 % pour `rundfrage`. Et « chronischer
            # Selbstmord » est son expression.
            "selbstmord": ["selbstmord", "suizid"],
            # GARDÉ malgré ×0,30 — LE CHIFFRE MESURE LA BIBLIOTHÈQUE DE FREUD, PAS LE SILENCE DE
            # STEKEL. 62 % des occurrences du témoin sont dans deux monographies de l'hystérie
            # (« Studien über Hysterie » et « Sammlung 1 ») ; sans elles, le rapport passe à ×0,54.
            # En médiane par œuvre, Stekel est 3e sur 5, au-dessus de Freud. Et son taux dans son
            # volume clinique de 1908 (135,6 par million) est dans la bande d'Abraham et de
            # Ferenczi : ce sont ses deux livres de rêve, presque la moitié de son corpus, qui
            # écrasent sa moyenne. Le retrait coûterait 118 atomes que RIEN d'autre ne rattache à
            # la névrose. Contrôlé aussi : `hysteri` ne peut pas mordre dans « angsthysterie », le
            # bordage l'en empêche — aucun double compte.
            "hysterie": ["hysteri"],
        },
    },
    # ============================================================ LE POÈTE ET LE RÊVE (ENQUÊTE)
    # « Die Träume der Dichter » (1912) est une pièce singulière : une ENQUÊTE par correspondance
    # auprès d'une quarantaine d'écrivains vivants. `rundfrage` — le mot de l'enquête — compte
    # 64 occurrences chez lui contre 1 ailleurs. Voir la réserve d'attribution portée sur ce
    # volume dans `sources.OEUVRES` : une part du texte est de la main des écrivains interrogés.
    "dichtung": {
        "label": "Le poète, la création et l'enquête",
        "termes": {
            # « dichterisch » retiré : 64 atomes, 0 propre — tous déjà pris par « dichter ».
            "dichter": ["dichter", "dichtung"],
            "phantasie": ["phantasie"],
        },
    },
    # ================================================================ LE CRIME ET LA FAUTE
    # Rapport ×3,6 sur `verbrech` et ×3,0 sur `kriminal`. Il lit le crime comme un symptôme, ce
    # qui est chez lui un prolongement direct de la clinique, non une digression sociologique.
    "verbrechen": {
        "label": "Le crime, le criminel et la faute",
        "termes": {
            "verbrechen": ["verbrech"],
            "kriminalitaet": ["kriminal", "kriminell"],
            # RENVERSEMENT MESURÉ, et le plus instructif de l'audit. « schuldgefuhl » n'est PAS
            # son mot : ×0,28 par rapport aux autres, et il est 4e sur 5 auteurs, loin derrière
            # Rank et Freud. « schuldbewusstsein » l'est : ×2,23, PREMIER des cinq — et c'est
            # bien le terme de sa thèse (« Das Schuldbewußtsein ist die hauptsächlichste Ursache
            # aller Neurosen und Psychosen »). Additionnés, les deux donnaient ×0,67 et faisaient
            # échouer le sous-concept ; séparés, l'un le porte et l'autre le noyait. (Le troisième
            # motif, « schuldgefühl » avec tréma, était mort — voir `angstgefuehl`.)
            "schuldgefuehl": ["schuldbewusstsein"],
            "laster": ["laster"],
        },
    },
    # ================================================================ LA CLINIQUE ET LE CORPS
    "klinik": {
        "label": "La clinique, le corps et la fonction sexuelle",
        "termes": {
            "impotenz": ["impotenz", "impotent"],
            "koitus": ["koitus", "coitus", "beischlaf", "geschlechtsakt"],
            # Deux motifs sur trois étaient inutiles : « nervosität » avec tréma est mort (le
            # repli supprime les diacritiques), et « nervositat » est entièrement absorbé par
            # « nervos ». Compte identique avant et après : 335 atomes.
            "nervositaet": ["nervos"],
            # « infektion » RETIRÉ : il apportait 46 des 154 atomes, et la lecture montre qu'au
            # moins 35 des 77 occurrences ne sont pas vénériennes — tuberculose, diphtérie,
            # malaria, coqueluche, peste (« Infektionskeime der Pest »), une écharde, un clou
            # planté dans un pied, la phobie des microbes. Les maladies nommées, elles, sont
            # massivement siennes : lues ×28,6, gonorrhoe ×19,7, syphilis ×6,4.
            "geschlechtskrankheit": ["gonorrho", "syphili", "lues", "tripper", "venerisch",
                                     "geschlechtskrank"],
            "schlafstoerung": ["schlaflos", "schlafstorung", "insomni"],
        },
    },
}

# ------------------------------------------------------------------------------------------
FONCTIONS = [
    {
        "id": "inference",
        "label": "Inférence / conclusion",
        "marqueurs": [r"\balso\b", r"\bdaher\b", r"\bsomit\b", r"\bfolglich\b", r"\bdemnach\b",
                      r"\bmithin\b", r"\bergibt sich\b", r"\bdaraus folgt\b"],
    },
    {
        "id": "hypothese",
        "label": "Hypothèse / conjecture",
        "marqueurs": [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bdurfte\b",
                      r"\bscheint\b", r"\banzunehmen\b", r"\bwohl\b"],
    },
    {
        "id": "observation",
        "label": "Observation clinique",
        "aide": "Comme Abraham, il part d'un malade. Son corpus compte 413 occurrences de "
                "« Neurotiker » et il numérote ses cas.",
        "marqueurs": [r"\bpatient", r"\bkranke", r"\bder fall\b", r"\bfall \d", r"\bbeobachtung",
                      r"\bkrankengeschichte", r"\bein\w* \w*jahrig", r"\bmein patient\b"],
    },
    {
        "id": "enquete",
        "label": "Enquête auprès d'un tiers",
        "aide": "PROPRE À STEKEL dans ce corpus : « Die Träume der Dichter » (1912) est une "
                "enquête par correspondance auprès d'écrivains vivants, qu'il cite. Aucun autre "
                "auteur du corpus ne construit un livre ainsi. `rundfrage` : 64 occurrences "
                "chez lui, 1 dans tout le reste.",
        "marqueurs": [r"\brundfrage\b", r"\bumfrage\b", r"\bantwortet\b", r"\bschreibt mir\b",
                      r"\bteilt mir mit\b", r"\bauf meine anfrage\b", r"\bmeine frage\b"],
    },
    {
        "id": "polemique",
        "label": "Polémique et prise de distance",
        "aide": "Sa signature de ton. Le corpus tient l'avant et l'après de sa rupture de 1912 "
                "avec Freud, et sa réserve est écrite dès 1907 — « Im Gegenteil! ».",
        "marqueurs": [r"\bim gegenteil\b", r"\bich kann nicht\b", r"\bich bestreite\b",
                      r"\birrtum\b", r"\bmit unrecht\b", r"\bich widerspreche\b",
                      r"\bganz anders\b", r"\bkeineswegs\b"],
    },
    {
        "id": "methode",
        "label": "Geste de méthode",
        "marqueurs": [r"\banalyse", r"\bdeutung", r"\bmethode\b", r"\bverfahren\b",
                      r"\buntersuchung", r"\bpsychoanalyse\b", r"\bbehandlung\b", r"\btechnik\b"],
    },
    {"id": "question", "label": "Question posée", "marqueurs": [r"\?"]},
    {
        "id": "analogie",
        "label": "Analogie / comparaison",
        "marqueurs": [r"\bgleichsam\b", r"\bwie wenn\b", r"\betwa wie\b", r"\bvergleich",
                      r"\bals ob\b", r"\bahnlich wie\b", r"\bebenso wie\b"],
    },
    {
        "id": "savoir_etabli",
        "label": "Renvoi au savoir établi",
        "marqueurs": [r"\bbekanntlich\b", r"\bwir wissen\b", r"\bbekannt ist\b",
                      r"\bwie bekannt\b", r"\berfahrungsgemass\b"],
    },
    {
        "id": "revision",
        "label": "Révision de sa propre position",
        "aide": "Signal RARE et précieux, jamais tenu pour acquis : il alimente une liste à "
                "vérifier, et chaque candidat est lu en contexte avant d'être retenu.",
        "marqueurs": [r"\b(ich|wir)\b.{0,30}?\bkorrigier", r"\bberichtigen\b", r"\birrte\b",
                      r"\birrtumlich", r"\bnicht aufrechterhalten\b", r"\bfruher glaubte ich\b",
                      r"\bich habe fruher\b"],
        "fiabilite": "a_confirmer",
    },
    {
        "id": "objection",
        "label": "Objection à sa propre thèse",
        "marqueurs": [r"\beinwand(?!frei|er)", r"\beinwendung", r"\bman konnte sagen\b",
                      r"\bdagegen spricht\b", r"\bman wird einwenden\b", r"\bman wird mir\b"],
        "fiabilite": "a_confirmer",
    },
    {
        "id": "renvoi_freud",
        "label": "Renvoi à Freud",
        "aide": "CENTRAL POUR CET AUTEUR, et à ne surtout pas lire comme un accord : il est "
                "l'élève déclaré de 1907 et le rompu de 1912, et le corpus contient les deux. "
                "Un renvoi LOCALISE, il ne qualifie pas — la règle vaut ici plus qu'ailleurs.",
        "marqueurs": [
            r"\bfreud\w*\s+(auffassung|ansicht|annahme|lehre|meinung|arbeit|aufsatz|schule)\b",
            r"\b(nach|mit|gemass) freud\b", r"\bwie freud\b",
            r"\bfreud hat\b.{0,40}?\b(gezeigt|nachgewiesen|hervorgehoben|gelehrt)\b",
            r"\bprofessor freud\b", r"\bfreudsch"],
    },
    {
        "id": "rapport_tiers",
        "label": "Rapport à un tiers",
        "aide": "Hirschfeld est son contradicteur constant sur l'homosexualité : 87 mentions "
                "chez lui contre 9 dans tout le reste du corpus.",
        "marqueurs": [r"\bhirschfeld\b", r"\badler\b", r"\bjung\b", r"\bsadger\b",
                      r"\bkrafft-ebing\b", r"\bhavelock ellis\b", r"\bmoll\b", r"\bbloch\b"],
    },
]

MARQUEURS_STATUT = {
    "modalise":     [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bscheint\b",
                     r"\bdurfte\b", r"\bwohl\b", r"\bmoglicherweise\b", r"\bkaum\b", r"\betwa\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"\bberichtet\b", r"\berzahlt\b", r"\bnach \w+\b", r"\bzitiert\b",
                     r"\bangeblich\b", r"\bteilt mit\b", r"\bschreibt mir\b"],
}

# Les noms qu'il cite. Hirschfeld y figure parce qu'il est son contradicteur constant sur
# l'homosexualité — 87 mentions chez lui contre 9 dans tout le reste du corpus.
NOMS_AUTEURS = ["freud", "adler", "jung", "abraham", "rank", "ferenczi", "jones", "bleuler",
                "sadger", "hirschfeld", "krafft", "moll", "bloch", "havelock", "ellis",
                "forel", "loewenfeld", "janet", "breuer"]


# --------------------------------------------------------------------------------------------
# CE QUI A ÉTÉ PROPOSÉ PUIS RETIRÉ À L'AUDIT — treize sous-concepts sur soixante-deux.
#
# Le taux de retrait est de 26 %, contre 7 % pour le lexique de Ferenczi. Ce n'est pas une mauvaise
# nouvelle sur Stekel, c'est une mesure sur la façon dont ce lexique a été écrit : d'un jet, sans
# audit préalable. Le chiffre est publié tel quel.
#
# Le motif du retrait est chaque fois une MESURE, jamais un avis. Sans cette trace, chacun de ces
# treize sera reproposé, avec les mêmes arguments et le même résultat.
#
#   ambivalenz      0 occurrence sur 5 222 046 signes, contre 269 chez les autres. C'est le mot de
#                   BLEULER, que Stekel cite quinze fois sans jamais reprendre son concept. Le
#                   sous-concept prêtait à un auteur le vocabulaire de ses contemporains.
#   gegensatzpaar   3 atomes — une par volume. Élargir à « gegensatz » donnerait 110 atomes dont
#                   43 (39 %) sont la locution « im Gegensatze zu » = « contrairement à ».
#   masturbation    ×0,50 : il en parle DEUX FOIS MOINS que les autres. Ce n'est pas son mot mais
#                   celui de ses adversaires — 5 des formes captées sont la nomenclature latine de
#                   Rohleder qu'il cite. Il écrit « onani* » 1 449 fois contre « masturbat » 34.
#   sexuelle_ersatzhandlung  5 occurrences au total, le quart du seuil ; et 3 des 5 sont des
#                   citations d'Abraham et de Freud.
#   fetischismus    ×1,12 — Abraham seul en parle plus. Les 15 atomes qui manquaient à l'appel
#                   étaient « fussfetischismus », que le bordage du moteur n'atteint pas.
#   transvestitismus  17 atomes, dont 11 dans 145 atomes consécutifs d'un volume qui en compte
#                   10 706 ; et 3 sont le titre du livre de Hirschfeld cité en note — que Stekel
#                   mentionne pour REFUSER la catégorie.
#   phobie          ×0,92 : il en parle moins que les autres. Et le motif manquait ses vraies
#                   phobies à lui — topophobie (10), erythrophobie (6), nosophobie (12) — tandis
#                   que « klaustrophob » faisait 0.
#   traumtypus      28 de ses 41 atomes (68 %) doublonnent « wiederholungstraum » ; des 15
#                   restants, 12 sont l'écho du questionnaire dans la bouche des écrivains
#                   interrogés (« Typische Träume habe ich eigentlich nicht »).
#   wunsch          3e sur 5 auteurs, ×0,91. C'est le mot de l'école, pas le sien ; et
#                   « wunschtraum » compte 1 occurrence dans tout le corpus.
#   strafbeduerfnis  le motif éponyme fait 0 occurrence chez lui (19 ailleurs) ; 12 atomes en tout,
#                   ×0,25, DERNIER des cinq auteurs. Le besoin de punition est un concept de Rank.
#   kunstwerk       ×0,78, et ×0,89 même en retirant « Der Künstler » de Rank du témoin. 31 des
#                   171 atomes désignent le MÉTIER du patient (« Ich lasse die Künstler 10 bis 15
#                   Tropfen vor dem Auftreten nehmen »), non l'œuvre d'art.
#
#   rundfrage       LE CAS FERENCZI/« GENITALTHEORIE », À L'IDENTIQUE : 56 des 64 occurrences
#                   (87,5 %) sont la tête courante et le sommaire de « Die Träume der Dichter » —
#                   « VII. Die Rundfrage. » ×10, « Die Rundfrage. » ×7. Restent 8 usages réels.
#                   Le mot était pourtant présenté comme une signature dans l'en-tête de ce
#                   fichier (« 64 occurrences chez lui contre 1 ailleurs ») : c'était un artefact
#                   typographique, et il ressemblait exactement au résultat attendu.
#   berufsneurose   PIRE ENCORE : 24 de ses 30 atomes (80 %) sont du paratexte — 18 têtes
#                   courantes, 3 titres de chapitre, 3 lignes de sommaire. Six usages réels. Et
#                   son « 0 occurrence ailleurs », qui le rendait convaincant, EST l'artefact :
#                   personne d'autre n'imprime ce titre de chapitre en haut de ses pages.
#
# Ces deux derniers valent d'être lus ensemble. Ils étaient les deux sous-concepts que l'en-tête
# de ce fichier citait comme les plus propres à Stekel, précisément parce que leur compte était
# élevé chez lui et nul ailleurs. C'est la signature d'une tête courante, pas d'un concept.


# --------------------------------------------------------------------------------------------
# LE RAPPORT < 1 : CE QU'IL CONDAMNE, ET CE QU'IL NE CONDAMNE PAS.
#
# Le second audit (2026-07-31) a éprouvé les deux groupes que le premier n'avait pas instruits, et
# il en est ressorti une correction de MÉTHODE plus importante qu'aucun de ses verdicts.
#
# Le premier audit avait retiré cinq sous-concepts sur le seul rapport de fréquence, au nom d'une
# règle juste — « le lexique d'un auteur ne doit pas lui prêter le vocabulaire de ses
# contemporains ». Appliquée mécaniquement, cette règle retirerait `neurose` (×0,92) et `hysterie`
# (×0,30) du lexique de l'homme qui sous-titre un livre « Die homosexuelle Neurose » et dont la
# thèse est « Das Schuldbewußtsein ist die hauptsächlichste Ursache aller Neurosen und Psychosen ».
#
# Les huit cas ont été repris, et trois configurations distinctes apparaissent :
#
#   1. RIVAL INTRA-CORPUS DOMINANT → le retrait est FONDÉ. Le lexique prête à l'auteur le mot d'un
#      autre À LA PLACE du sien.
#        masturbation ×0,50 — il écrit « onani* » 1 566 fois contre « masturbat » 31 (50:1)
#        schuldgefuehl ×0,26 — « Schuldbewusstsein » est son terme (×1,94), et les additionner
#                              faisait échouer les deux
#
#   2. PAS DE RIVAL → le rapport dit seulement que le mot est COMMUN AU CHAMP. Ce n'est pas un
#      motif de retrait : un lexique qui retire tout le vocabulaire commun ne décrit plus un
#      auteur, il décrit son écart au champ.
#        neurose ×0,92, hysterie ×0,30 — gardés
#        wunsch ×0,91 — RETIRÉ À TORT au premier audit, aucun rival mesuré
#
#   3. MOTIF INCOMPLET → le rapport ne mesure pas le concept mais la couverture du motif. Il faut
#      avoir vérifié que le motif couvre la famille attestée AVANT d'invoquer un rapport.
#        phobie ×0,70 → ×1,17 une fois les composés atteints. RÉTABLI, voir le groupe `angst`.
#
#   Et un cas qui ne rentre dans aucune des trois, qu'il faut nommer pour ne pas le confondre
#   avec le premier : RIVAL HORS CORPUS. `parapathie`, le néologisme par lequel Stekel rebaptise
#   la névrose, compte 4 occurrences — il l'annonce en 1917 (« den NEUEN Ausdrücken Paraphilie,
#   Parapathie, Paralogie ») et ne l'impose qu'après 1920, quand le corpus s'arrête. Un rival que
#   l'auteur n'a pas encore forgé ne peut condamner aucun mot.
#
# RÈGLE RETENUE : un rapport < 1 ne condamne que si (1) le motif couvre déjà la famille
# morphologique attestée chez l'auteur, ET (2) il existe un terme rival INTRA-CORPUS désignant la
# même chose, de rapport > 1, dont le compte chez l'auteur DOMINE celui du sous-concept accusé.
# Sans les deux, le rapport se publie comme une mesure, jamais comme un verdict.
#
# TROIS AUTRES CHOSES QUE CE RAPPORT NE MESURE PAS, toutes rencontrées ici :
#   • la BIBLIOTHÈQUE DU TÉMOIN — 62 % des « hysteri » de Freud sont dans ses deux monographies de
#     l'hystérie ; sans elles le rapport de Stekel passe de ×0,30 à ×0,54 ;
#   • le PARATEXTE DU TÉMOIN — 13 % des « neuros » de Freud sont « Neurosenlehre », tête courante
#     de trois de ses volumes : le piège du volume unique joue aussi sur le DÉNOMINATEUR ;
#   • la COMPOSITION DU CORPUS — 48 % du corpus allemand de Stekel sont ses deux livres de rêve,
#     où TOUT le registre clinique s'effondre ensemble (verdrang ×0,15, symptom ×0,11, hysteri
#     ×0,08, sexual ×0,20) pendant que `traum` monte à ×3,03. Corrigé du genre, sur ses seuls
#     volumes cliniques, `verdraengung` remonte de ×0,54 à ×0,90 et `symptom` de ×0,39 à ×0,65.
#     C'est le genre du livre, pas la doctrine de l'auteur.
