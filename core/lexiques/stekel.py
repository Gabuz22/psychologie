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
            # Le motif nu couvre onanie, onanieren, onaniert, onanist, onanistisch. Les deux
            # graphies fautives sont relevées dans le texte, non supposées : l'OCR des scans
            # Google rend « Onanie » en « Öonanie » (26 fois) et « Önanie » (34).
            "onanie": ["onani", "oonani", "onani"],
            "masturbation": ["masturbat"],
            "pollution": ["pollution"],
            "abstinenz": ["abstinen", "enthaltsamkeit"],
            "sexuelle_ersatzhandlung": ["ersatzbefriedigung", "surrogat"],
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
            "homosexualitaet": ["homosexual", "homosexuell", "homoerot"],
            "heterosexualitaet": ["heterosexual", "heterosexuell"],
            "bisexualitaet": ["bisexual", "bisexuell", "bisexualitat"],
            "inversion": ["inversion", "invertiert", "urning", "urninde"],
            "fetischismus": ["fetischis", "fetischist"],
            "transvestitismus": ["transvestit"],
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
            "angstanfall": ["angstanfall", "angstanfalle", "angstattack"],
            "angstgefuehl": ["angstgefuhl", "angstgefühl"],
            "phobie": ["phobie", "phobisch", "agoraphob", "klaustrophob", "platzangst"],
            "todesangst": ["todesangst", "todesgedanke", "todesfurcht"],
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
            "bipolaritaet": ["bipolar"],
            "ambivalenz": ["ambivalen"],
            "gegensatzpaar": ["gegensatzpaar", "gegensatzlich"],
        },
    },
    # ================================================================ LE RÊVE ET SON LANGAGE
    # Sa spécialité reconnue, et le seul point où Freud le cite abondamment : « die reichste
    # Sammlung von Symbolauflösungen ». Seize atomes de la Traumdeutung le discutent.
    "traumsprache": {
        "label": "Le langage du rêve et ses symboles",
        "termes": {
            # Le motif nu est INDISPENSABLE — c'est le mot le plus fréquent de son corpus après
            # les outils grammaticaux (2 098 occurrences). La garde `(?!a)` est obligatoire :
            # sans elle, `traum` attrape `trauma`, `traumatisch`, `Traumatismus`, qui relèvent
            # d'une tout autre question. Le piège est le même que `traum`/`Trauma` déjà
            # documenté dans le lexique de Freud.
            "traum": [r"traum(?!a)", r"traume", r"traumt", r"traumer"],
            "traumsymbol": ["traumsymbol", "symbolauflosung", "symbolik", "symbolisch", "symbol"],
            "traumdeutung": ["traumdeut", "traumanalys"],
            "traumsprache": ["traumsprache", "sprache des traumes"],
            "traumtypus": ["typischer traum", "typische traume", "stereotype traum"],
            "wiederholungstraum": ["wiederholungstraum", "stereotyp"],
            "wunsch": ["wunsch", "wunsche", "wunschtraum", "wunscherfullung"],
            "traeumer": ["traumer", "traumende"],
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
            "kind": ["kind", "kinder", "kindheit", "kindlich", "knabe", "madchen"],
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
            "wasser": ["wasser", "meer", "fluss", "see", "schwimm", "ertrink"],
            "raum": ["zimmer", "haus", "wohnung", "tur", "fenster", "keller", "dachboden"],
            "weg": ["strasse", "weg", "treppe", "stiege", "bruck", "reise", "eisenbahn"],
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
            "rundfrage": ["rundfrage", "umfrage"],
            "dichter": ["dichter", "dichtung", "dichterisch"],
            "kunstwerk": ["kunstwerk", "kunstler"],
            "phantasie": ["phantasie", "phantasier"],
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
            "schuldgefuehl": ["schuldgefuhl", "schuldgefühl", "schuldbewusstsein"],
            "strafbeduerfnis": ["strafbedurfnis", "bestrafung", "suhne"],
            "laster": ["laster"],
        },
    },
    # ================================================================ LA CLINIQUE ET LE CORPS
    "klinik": {
        "label": "La clinique, le corps et la fonction sexuelle",
        "termes": {
            "impotenz": ["impotenz", "impotent"],
            "koitus": ["koitus", "coitus", "beischlaf", "geschlechtsakt"],
            "nervositaet": ["nervositat", "nervosität", "nervos"],
            "berufsneurose": ["berufsneuros"],
            "geschlechtskrankheit": ["gonorrho", "syphilis", "lues", "infektion"],
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
