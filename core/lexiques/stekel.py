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
            "wasser": ["wasser", "meer", "fluss", "schwimm", "ertrink"],
            "raum": ["zimmer", "haus", "wohnung", "tur", "fenster", "keller", "dachboden"],
            # « weg » RETIRÉ, pour une raison plus profonde qu'un faux positif : il attrapait
            # « wegen » (240 fois, « à cause de »), mais surtout le repli SUPPRIME LES MAJUSCULES,
            # et l'allemand ne distingue le substantif « Weg » (le chemin, un symbole du rêve) de
            # l'adverbe « weg » (parti, au loin) que par elle. Le motif était donc indécidable par
            # construction, non seulement imprécis. Les composés sans ambiguïté sont gardés.
            "weg": ["strasse", "treppe", "stiege", "bruck", "reise", "eisenbahn"],
            "koerperbild": ["vagina", "penis", "membrum", "busen", "brust", "genital"],
            "tier": ["tier", "schlange", "pferd", "hund", "vogel", "katze"],
            "tod_bild": ["friedhof", "grab", "leiche", "sarg", "begrabnis"],
        },
    },
    # ================================================================ LA NÉVROSE ET LA MORT
    "neurose": {
        "label": "La névrose, le symptôme et la mort",
        "termes": {
            "neurose": ["neuros", "neurotik", "neurotisch"],
            "symptom": ["symptom"],
            "verdraengung": ["verdrang"],
            "sterben": ["sterben", "sterbe", "gestorben", "tod", "todes"],
            "selbstmord": ["selbstmord", "suizid", "freitod"],
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
