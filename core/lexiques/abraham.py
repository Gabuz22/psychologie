#!/usr/bin/env python3
"""LEXIQUE DE KARL ABRAHAM (1877-1925) — construit sur SON vocabulaire.

Abraham est le contraire exact de Rank, et c'est pourquoi il vient juste après lui. Rank
s'écarte ; Abraham approfondit. Il fonde la société de Berlin, analyse Klein et Horney, et meurt
à quarante-huit ans sans avoir jamais rompu. Le corpus tient donc les deux figures de l'entourage
de Freud, condition nécessaire pour distinguer un jour, sur des mesures, un SOCLE PARTAGÉ d'une
divergence — ce qui restera l'affaire d'une couche de comparaison explicite, jamais du lexique.

Sa signature est CLINIQUE là où celle de Rank est mythologique. Mesuré par rapport à Freud :
*Patient* ×30,0, *Patienten* ×14,3, *Dementia praecox* ×110 et ×71 — la psychose est sa spécialité,
lui qui exerce à la Burghölzli avant Berlin. Et un chiffre qui dit tout du personnage : *Freuds*
×118,9. Il cite Freud à chaque page, non par déférence mais parce que sa méthode consiste à
prolonger point par point.

Sa contribution propre est une SUBDIVISION : là où Freud pose des stades oral, anal et génital,
Abraham dédouble chacun (oral de succion / oral de morsure, anal d'expulsion / anal de rétention)
et rattache chaque affection à son point de fixation. C'est le premier groupe ci-dessous, et il
n'a d'équivalent chez aucun autre auteur du corpus.

Toutes les fréquences citées sont mesurées sur les cinq œuvres (1909-1925), 1,36 million de signes.
"""

LANGUE = "de"

CONCEPTS = {
    # ------------------------------------------------------- SA CONTRIBUTION PROPRE
    # Le cœur d'Abraham, et ce qui reste de lui dans la psychanalyse : l'échelle des stades de
    # la libido, chacun dédoublé, avec pour chaque affection un point de fixation assignable.
    # « Versuch einer Entwicklungsgeschichte der Libido » (1924) ne parle que de cela.
    "stades": {
        "label": "Stades de la libido et points de fixation",
        "termes": {
            "libido": ["libido", "libidin"],
            # « anal » doit exclure « Analyse » et toute sa famille — sans quoi le concept
            # central d'Abraham compterait chaque occurrence du mot « analyse » du volume.
            "anal": [r"anal(?!y)", "analerotik", "analcharakter"],
            "oral": ["oral", "oralerotik", r"saug(?!lings)", "lutsch", "beissen"],
            "genital": ["genital"],
            "praegenital": ["pragenital"],
            "phallisch": ["phallisch"],
            "erogene_zone": ["erogen"],
            "fixierung": ["fixier"],
            "regression": ["regress"],
            "entwicklungsstufe": ["entwicklungsstufe", "entwicklungsphase", "organisationsstufe",
                                  "stufe\\b", "phase\\b"],
        },
    },
    # ------------------------------------------------------- LA PSYCHOSE ET L'HUMEUR
    # Le domaine qu'il a ouvert. « Ansätze zur psychoanalytischen Erforschung … des
    # manisch-depressiven Irreseins » (1912) précède de cinq ans « Trauer und Melancholie » de
    # Freud, qui s'y réfère. Dementia praecox ×110 par rapport à Freud : c'est SON terrain.
    "psychose": {
        "label": "Psychose, mélancolie, états maniaco-dépressifs",
        "termes": {
            "dementia_praecox": ["dementia", "praecox", "schizophren", "paranoi"],
            "melancholie": ["melanchol"],
            "manie": ["manisch", r"manie\b"],
            "depression": ["depress"],
            "trauer": ["trauer"],
            "objektverlust": ["objektverlust", "objektverlassen"],
            # Le mécanisme qu'il décrit et que Klein reprendra intégralement : l'objet perdu est
            # avalé, incorporé au moi. Rare en nombre (43) mais décisif en portée.
            "introjektion": ["introjekt", "inkorporat", "einverleib"],
            "ambivalenz": ["ambivalen"],
        },
    },
    # ------------------------------------------------------- LE CARACTÈRE
    # « Psychoanalytische Studien zur Charakterbildung » (1925) : Abraham fait du caractère un
    # objet à part entière, dérivé des stades. C'est de là que vient tout le vocabulaire
    # ultérieur du « caractère anal », « oral », etc.
    "caractere": {
        "label": "Formation du caractère",
        "termes": {
            "charakter": ["charakter"],
            "charakterzug": ["charakterzug", "charakterbildung", "charaktereigenschaft"],
            "sparsamkeit": ["sparsam", "geiz", "ordnungsliebe", "eigensinn", "trotz\\b"],
            "ehrgeiz": ["ehrgeiz", "eitelkeit", "groessenphantasie"],
            "neigung": ["neigung"],
        },
    },
    # ------------------------------------------------------- LA CLINIQUE
    # Ce qui domine le corpus en volume brut : Abraham part TOUJOURS de cas. Patient ×30 par
    # rapport à Freud — l'écart le plus fort de tout son vocabulaire courant.
    "clinique": {
        "label": "Le cas, le patient, la cure",
        "termes": {
            "patient": ["patient", "patientin", "kranke", "neurotiker"],
            "fall": [r"fall\b", r"falle\b", "krankengeschichte"],
            "neurose": ["neuros"],
            "hysterie": ["hysteri"],
            "zwangsneurose": ["zwangsneuros", "zwangsvorstellung"],
            "angst": ["angst", "angstlich", "phobie"],
            "symptom": ["symptom"],
            "uebertragung": ["ubertragung"],
            "widerstand": ["widerstand"],
            "behandlung": ["behandlung", "therapie", "heilung", "kur\\b"],
            # Deux objets cliniques propres à Abraham, absents de l'ontologie freudienne :
            # l'alcoolisme (45 occ., il lui consacre une étude) et le fétichisme du pied.
            "alkohol": ["alkohol", "trinker", "rausch"],
            "fetischismus": ["fetisch"],
        },
    },
    # ------------------------------------------------------- LES MÉCANISMES
    "mecanismes": {
        "label": "Mécanismes psychiques",
        "termes": {
            "verdraengung": ["verdrang"],
            "sadismus": ["sadis"],
            "masochismus": ["masochis"],
            "narzissmus": ["narziss"],
            "identifizierung": ["identifizier"],
            "projektion": ["projektion", "projizier"],
            "sublimierung": ["sublimier"],
            "phantasie": ["phantasie", "phantasier"],
        },
    },
    # ------------------------------------------------------- MYTHE ET SYMBOLE
    # « Traum und Mythus » (1909) est le Heft IV de la série où la Gradiva de Freud est le Heft I
    # et le Mythus de Rank le Heft V. Abraham y pose l'équation rêve/mythe que Rank développera.
    "mythe": {
        "label": "Rêve, mythe, symbole",
        "termes": {
            # Le piège Traum/Trauma, déjà mesuré chez Freud : discriminer sur la FAMILLE
            # morphologique attestée, jamais sur la lettre suivante. Motif repris tel quel.
            "traum": [r"traum(?!a(?:s?\b|ti(?:sch|sier)|tolog))"],
            "mythus": ["mythus", "mythos", "mythen", "mythisch", "sage\\b", "sagen\\b"],
            "symbol": ["symbol"],
            "volkerpsychologie": ["volkerpsycholog", "volkerkunde", "primitiv"],
            "religion": ["religio", "gott", "kultus", "ritus"],
            # 106 occ. : Abraham consacre une étude entière à « la force déterminante du nom »
            # (le patient qui vit son prénom comme un destin). Objet à lui, sans équivalent.
            "name": [r"namen", r"name\b", "vorname"],
        },
    },
    # ------------------------------------------------------- L'ART
    # Le « Segantini » (1911) est une monographie entière sur un peintre : Abraham y lit la
    # perte précoce de la mère dans les toiles. L'art est chez lui un matériau clinique.
    "art": {
        "label": "Art et création",
        "termes": {
            "kunst": [r"kunst\b", "kunstler", "kunstlerisch"],
            "malerei": ["malerei", "maler\\b", "gemalde", r"bild(?!ung)"],
            "dichter": ["dichter", "dichtung"],
            "schoepfung": ["schaffen", "schopfer"],
        },
    },
    # ------------------------------------------------------- L'APPAREIL PSYCHIQUE (audit 2)
    # Manquait entièrement au premier lexique, alors qu'Abraham l'emploie constamment : il
    # travaille DANS la topique de Freud, sans la discuter. C'est précisément ce qu'un lexique
    # d'auteur doit montrer — ce qu'il reprend tel quel autant que ce qu'il ajoute.
    "appareil": {
        "label": "Appareil psychique",
        "termes": {
            "unbewusst": ["unbewusst"],
            # « bewusst » nu prendrait aussi « unbewusst » : l'exclusion sépare les deux, sans
            # quoi toute mesure de l'inconscient serait doublée (même piège que chez Le Bon).
            "bewusstsein": [r"(?<!un)bewusst"],
            "vorstellung": ["vorstellung"],
            "psychisch": ["psychisch", "seelisch", "seele"],
            "erinnerung": ["erinner", "gedachtnis", "vergessen"],
            "trieb": ["trieb", "tendenz", "streben", r"drang\b"],
            "wunsch": ["wunsch", "wunsche"],
            "vorgang": ["vorgang", "prozess", "mechanismus"],
        },
    },
    # ------------------------------------------------------- AFFECTS ET PERCEPTION (audit 2)
    # 502 et 443 occurrences. Le Segantini n'était qualifié qu'à 60 % sans ces deux groupes : une
    # monographie sur un peintre parle de regard, de lumière et de couleur à chaque page, et le
    # premier lexique n'avait rien pour l'entendre.
    "affects": {
        "label": "Affects et sensibilité",
        "termes": {
            "affekt": ["affekt", "gefuhl", "stimmung", r"lust\b", "unlust"],
            "liebe": ["liebe", "liebt", "geliebt", "verliebt"],
            "hass": ["hass", "feindselig", "aggress", "grausam"],
            "schuld": ["schuld"],
            "auge": ["auge", "blick", r"sehen\b", r"licht\b", "farbe", "anblick"],
            # 107 occ. : le feu revient chez Abraham comme symbole (il consacre une étude au
            # complexe de Prométhée) et dans le Segantini, mort en montagne près d'un foyer.
            "feuer": ["feuer", "flamme", "brand\\b"],
            "sprache": ["sprache", "sprachlich", r"wort\b", "worte", "sprechen"],
        },
    },
    # ------------------------------------------------------- LA VIE, LA MORT (audit 2)
    "existence": {
        "label": "Vie, mort, maladie, corps",
        "termes": {
            "leben": ["leben", "lebendig"],
            "tod": ["tod", r"tot(?!al|em)", "sterb", "gestorben"],
            "krankheit": ["krankheit", "erkrankung", r"leiden\b"],
            "koerper": ["korper", r"organ\b", r"organe\b", "leiblich"],
            "mensch": ["mensch"],
            "person": ["person"],
            "entwicklung": ["entwicklung", "entwickel"],
        },
    },
    # ------------------------------------------------------- LA DISCIPLINE (audit 2)
    # 441 occurrences, et un signe du personnage : Abraham parle sans cesse de la psychanalyse
    # comme d'une science en construction dont il rapporte les progrès.
    "episteme": {
        "label": "La psychanalyse comme science",
        "termes": {
            "psychoanalyse": ["psychoanalyse", "psychoanalytisch"],
            "forschung": ["wissenschaft", "forschung", "theorie", "literatur"],
            "erfahrung": ["erfahrung", "beobachtung", "untersuchung"],
            "arbeit": ["arbeit"],
        },
    },
    # ------------------------------------------------------- LA FAMILLE
    "famille": {
        "label": "Père, mère, enfance",
        "termes": {
            "mutter": ["mutter"],
            "vater": ["vater"],
            "eltern": ["eltern"],
            "kind": ["kind", "kindheit", "kindlich", "infantil"],
            "geschwister": ["geschwister", "bruder", "schwester"],
            "oedipus": ["odipus"],
            "kastration": ["kastration"],
            "inzest": ["inzest"],
            "sexualitaet": ["sexual", "sexuell"],
        },
    },
}


# --------------------------------------------------------------------------- FONCTIONS
# Abraham raisonne PAR CAS : il expose une observation, en tire une règle, la compare à d'autres
# cas. D'où deux fonctions propres — « observation » et « comparaison_clinique » — qui n'existent
# ni chez Freud (dont la clinique est enchâssée dans la théorie) ni chez Rank (qui compare des
# récits, pas des malades).
FONCTIONS = [
    {
        "id": "inference",
        "label": "Inférence / conclusion",
        "marqueurs": [r"\balso\b", r"\bdaher\b", r"\bsomit\b", r"\bfolglich\b", r"\bdemnach\b",
                      r"\bmithin\b", r"\bergibt sich\b", r"\bdaraus folgt\b", r"\bwir schliessen\b"],
    },
    {
        "id": "hypothese",
        "label": "Hypothèse / conjecture",
        "marqueurs": [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bdurfte\b",
                      r"\bscheint\b", r"\banzunehmen\b", r"\bnehmen wir an\b", r"\bwohl\b"],
    },
    {
        "id": "observation",
        "label": "Observation clinique",
        "aide": "LE geste d'Abraham : il part d'un malade, pas d'une thèse. Son corpus compte "
                "868 occurrences de « Patient » — trente fois plus que Freud à volume égal.",
        "marqueurs": [r"\bpatient", r"\bkranke", r"\bich beobachtete\b", r"\bder fall\b",
                      r"\bin einem falle\b", r"\bkrankengeschichte", r"\bich behandelte\b",
                      r"\bein\w* \w*jahrig", r"\bmein patient\b"],
    },
    {
        "id": "comparaison_clinique",
        "label": "Comparaison de cas",
        "aide": "Il rapproche plusieurs malades pour dégager une régularité — l'équivalent, chez "
                "lui, de l'alignement des versions d'un mythe chez Rank.",
        "marqueurs": [r"\bin allen (?:diesen )?fallen\b", r"\bin anderen fallen\b",
                      r"\bahnlich(?:e|es|en)? fall", r"\bein weiterer fall\b",
                      r"\bregelmassig\b", r"\bin der mehrzahl der falle\b", r"\bstets\b"],
    },
    {
        "id": "methode",
        "label": "Énoncé méthodologique",
        "marqueurs": [r"\banalyse", r"\bdeutung", r"\bmethode\b", r"\bverfahren\b",
                      r"\buntersuchung", r"\bauffassung\b"],
    },
    {"id": "question", "label": "Question de recherche", "marqueurs": [r"\?"]},
    {
        "id": "analogie",
        "label": "Analogie / métaphore",
        "marqueurs": [r"\bgleichsam\b", r"\bwie wenn\b", r"\betwa wie\b", r"\bvergleich",
                      r"\bals ob\b", r"\bahnlich wie\b", r"\bbeispielsweise\b"],
    },
    {
        "id": "savoir_etabli",
        "label": "Renvoi à un savoir établi",
        "marqueurs": [r"\bbekanntlich\b", r"\bwir wissen\b", r"\bbekannt ist\b", r"\bwie bekannt\b"],
    },
    # -------- SIGNAUX À CONFIRMER — jamais des faits, seulement une liste de travail.
    {
        "id": "objection",
        "label": "Objection anticipée",
        "fiabilite": "a_confirmer",
        # Même exclusion que chez Rank : « einwandfrei » est un éloge, et « Einwanderung » une
        # migration. L'exclusion porte sur « er », non sur « ern », pour couvrir le substantif.
        "marqueurs": [r"\beinwand(?!frei|er)", r"\beinwendung", r"\bman konnte sagen\b",
                      r"\bdagegen spricht\b", r"\bman wird einwenden\b"],
    },
    {
        "id": "revision",
        "label": "Révision / correction de soi",
        "fiabilite": "a_confirmer",
        "marqueurs": [r"\b(ich|wir)\b.{0,30}?\bkorrigier", r"\bberichtigen\b", r"\birrte\b",
                      r"\birrtumlich", r"\bnicht aufrechterhalten\b",
                      r"\b(fruher|damals|seinerzeit)\b.{0,70}?"
                      r"\b(geglaubt|gemeint|behauptet|angenommen|vertreten|auffassung)\b"],
    },
    {
        "id": "renvoi_freud",
        "label": "Renvoi explicite à Freud",
        # FONCTION ÉTABLIE, et le choix a été fait en connaissance de cause. La première version
        # s'appelait « appui déclaré sur Freud » et était marquée `a_confirmer` — sur le modèle
        # d'« ecart_freud » chez Rank. Elle a été REQUALIFIÉE après la leçon de ce dernier :
        # ce marqueur avait donné 0 confirmé sur 5, parce qu'un motif lexical ne peut pas décider
        # si une mention est un appui, un prolongement ou une critique.
        # La conclusion à en tirer n'est pas de multiplier les signaux invérifiables, mais de
        # nommer la fonction pour ce que le marqueur PEUT établir : la phrase invoque
        # explicitement une position de Freud. Cela, le motif le prouve. La NATURE du renvoi
        # reste une question ouverte, et le corpus ne prétend pas y répondre.
        "aide": "La phrase invoque explicitement une position de Freud. Abraham écrit « Freuds » "
                "119 fois plus souvent que Freud n'écrit son propre nom : il avance en s'adossant, "
                "et c'est mesurable. Ce que le marqueur NE dit PAS : s'il s'agit d'un appui, d'un "
                "prolongement ou d'une réserve — cela demande de lire le passage.",
        "marqueurs": [r"\bfreud\w*\s+(auffassung|ansicht|annahme|lehre|meinung|arbeit|aufsatz)\b",
                      r"\b(nach|mit|gemass) freud\b", r"\bwie freud\b",
                      r"\bfreud hat\b.{0,40}?\b(gezeigt|nachgewiesen|hervorgehoben|gelehrt)\b",
                      r"\bin ubereinstimmung mit freud\b"],
    },
]

# Auteurs qu'Abraham discute : la première génération analytique, plus les psychiatres de
# l'école de Zurich — Bleuler et Jung, dont il fut l'assistant au Burghölzli.
NOMS_AUTEURS = ["freud", "jung", "bleuler", "ferenczi", "jones", "rank", "sadger", "stekel",
                "kraepelin", "riklin", "maeder", "silberer", "hitschmann", "reik", "simmel",
                "eitingon", "roheim", "storfer"]

MARQUEURS_STATUT = {
    "modalise":     [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bscheint\b",
                     r"\bdurfte\b", r"\bwohl\b", r"\bmoglicherweise\b", r"\bkaum\b", r"\betwa\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"\bberichtet\b", r"\berzahlt\b", r"\bnach \w+\b", r"\bzitiert\b",
                     r"\bangeblich\b", r"\bteilt mit\b"],
}
