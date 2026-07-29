#!/usr/bin/env python3
"""LEXIQUE DE SÁNDOR FERENCZI (1873-1933) — construit sur SON vocabulaire.

Ferenczi complète une figure que Rank et Abraham laissaient incomplète. Rank déplace une thèse
et rompt ; Abraham prolonge et ne rompt jamais ; Ferenczi reste vingt ans le plus proche de Freud
— « mon fils paladin », « le Grand Vizir secret » — et diverge sur ce que l'analyste FAIT. Sa
querelle est TECHNIQUE, non doctrinale. Le corpus tient donc trois formes distinctes du rapport
au maître, ce qui est la condition pour qu'un jour « socle » et « écart » cessent d'être des mots.

DEUX SIGNATURES, et elles n'ont d'équivalent chez aucun autre auteur du corpus.

1. LA THÉORIE GÉNITALE (« Versuch einer Genitaltheorie », 1924). Il y explique le coït par une
   régression vers la mer, la vie intra-utérine et l'origine de la vie — l'AMPHIMIXIS des
   érotismes, mot qui est de lui. Mesuré : `amphimix` 41 occurrences chez lui, 3 dans les
   785 000 mots des autres auteurs allemands. `begattung` ×38, `genitalitat` ×42, `thalass` ×12
   contre 1. C'est le seul endroit du corpus où la biologie sert de méthode d'interprétation.

2. LA TECHNIQUE, ET SON RENVERSEMENT PAR LUI-MÊME. Il invente la « technique active »
   (injonctions et interdits, 1919-1926), puis la démolit et lui substitue la RELAXATION, la
   néocatharsis et l'« élasticité » (1927-1933). Deux groupes séparés ci-dessous, et cette
   séparation est un résultat : elle n'a de sens que parce que le même homme a soutenu les deux,
   à sept ans d'écart. Aucun autre auteur du corpus ne se contredit ainsi sur sa propre pratique.

CE LEXIQUE A ÉTÉ AUDITÉ AVANT D'ÊTRE ÉCRIT. Cent vingt-sept sous-concepts ont été proposés sur
mesure, puis passés à un contrôle adversarial dont la consigne était de les CASSER : recompter,
afficher quinze contextes, les lire un par un, chercher le mot allemand qui commence pareil et
n'a rien à voir. Résultat : 88 gardés, 30 corrigés, 9 retirés. Les corrections sont dans le code
ci-dessous ; les retraits sont documentés en fin de fichier, parce qu'une décision négative non
écrite se refait.

Toutes les fréquences citées sont mesurées sur les cinq volumes retenus (1922-1939), 2,6 millions
de signes — le deuxième corpus du projet après Freud.
"""

LANGUE = "de"

CONCEPTS = {
    # ==================================================== SA CONTRIBUTION PROPRE (1) : LE GÉNITAL
    # Le cœur de la « Genitaltheorie ». Ferenczi y soutient que l'acte sexuel réunit les
    # érotismes partiels — urétral, anal, génital — en une seule décharge : l'AMPHIMIXIS.
    # Le mot n'existe que chez lui, et il n'a survécu nulle part ailleurs.
    "genitalite": {
        "label": "L'amphimixis des érotismes et la fonction génitale",
        "termes": {
            "amphimixis": ["amphimix", "amphimikt"],
            "erotismen": ["erotism"],
            # « genitaltheorie » est EXCLU : c'est le titre du livre, pas un concept. L'audit a
            # mesuré que 50 de ses 83 occurrences étaient la tête courante imprimée en haut de
            # chaque page paire — un artefact typographique qui ressemblait exactement au
            # résultat attendu. (Ces têtes sont désormais retirées en amont, mais l'exclusion
            # reste : un auteur qui cite le titre de son livre ne mobilise pas un concept.)
            "genitalitaet": ["genitalitat", "genitalprimat", "genitalfunktion", "genitalisier"],
            "genitalorgan": ["genitalien", "genitalorgan", "genitalzone", "genitalgegend",
                             "genitalsekret", "genitalsymbolik", "genitalerotik"],
            "genital": [r"genital(?!theorie)"],
            "begattung": ["begattung"],
            "koitus": ["koitus", "coitus", "geschlechtsakt", "beischlaf", "kohabitation",
                       "sexualakt", "paarung", "koitier", "kopulation"],
            "ejakulation": ["ejakulation", "ejaculat", "samenerguss", "samenentleerung", "sperma"],
            # Le motif nu « samen » a été essayé puis écarté : il attrape « zusammen ».
            "erektion_friktion": ["erektion", "erektil", "friktion", "immissio", "reibung"],
            "orgasmus": ["orgas"],
            "urethro_anal": ["urethral", "analerotik", "urethro"],
        },
    },
    # ==================================================== SA CONTRIBUTION PROPRE (2) : THALASSA
    # La thèse la plus étrange du corpus, et la plus assumée : le coït est une tentative de
    # retour au ventre maternel, lui-même souvenir de l'océan que la vie a quitté quand les mers
    # se sont asséchées. D'où une CATASTROPHE géologique au fondement d'une théorie psychique.
    #
    # Rapprochement que la mesure impose et que le lexique ne tranche pas : `mutterleib` pèse
    # 11,0 ‰ chez Ferenczi contre 8,4 ‰ chez Rank — et le « Trauma der Geburt » de Rank paraît
    # la MÊME ANNÉE que la « Genitaltheorie ». Deux hommes, deux livres, un vocabulaire commun,
    # 1924. Le corpus le montre ; il ne dit pas ce qu'il faut en conclure.
    "thalassa": {
        "label": "La régression thalassale : mer, ventre maternel, catastrophe",
        "termes": {
            "thalassal": ["thalass", "regressionszug", "regressionstend", "regressionstrieb",
                          "regressionsziel", "regressionsneigung", "regressionsbestrebung",
                          "regressionsweg", "mutterleibsregression", "mutterleibregression",
                          "meeresregression"],
            "regression": ["regress"],
            # « embryo » exclut « embryologie » : la discipline n'est pas l'organisme.
            "mutterleib": ["mutterleib", "intrauterin", r"embryo(?!log)", "fotus", "fotal",
                           "plazenta", "amnion", "fruchtwasser", "keimzelle", "befruchtung"],
            # Exclusions relevées à la lecture des contextes : le cochon d'Inde, la conduite
            # d'eau, le baleinier, la femme du pêcheur. Toutes mesurées, aucune supposée.
            "meer_wasser": [r"meer(?!schwein)", "seewasser", r"wasser(?!leitung)",
                            r"fisch(?!bein|blase|genuss|gericht|ersfrau)"],
            "katastrophe": ["katastroph", "eintrock", "eiszeit", "sintflut"],
            # « tier » exclut « tieren » conjugué et « tierung » (les suffixes de dérivation
            # française passés en allemand savant : « Konzentrierung »).
            "tierreihe": [r"tier(?!t|ung)", "amphib", "molch", "lurch", "reptil", "wasserbewohn",
                          "landbewohn", "landtier", "kiemen", r"parasit(?!ophobie)"],
            "schlaf": [r"schlaf(?!zimmer)"],
        },
    },
    # La MÉTHODE que ces deux thèses supposent, et que Ferenczi nomme : éclairer le psychique par
    # le biologique et réciproquement. C'est l'UTRAQUISME — cinq occurrences seulement, mais le
    # mot désigne le geste qui organise tout le livre de 1924, et il est retenu pour cela.
    "bioanalyse": {
        "label": "La bioanalyse et l'utraquisme : la méthode",
        "termes": {
            "bioanalyse": ["bioanaly"],
            "utraquismus": ["utraquis"],
            "phylogenese": ["phylogen", "ontogen", "biogenetisch", "stammesgeschicht",
                            "coenogenetisch"],
            "naturwissenschaft": ["naturwissenschaft", "biolog", "zoolog", "embryolog"],
            # Les savants qu'il convoque ne sont pas des psychanalystes : c'est le signe même de
            # sa méthode. Lamarck et Haeckel y pèsent plus que Jung.
            "naturforscher": ["lamarck", "haeckel", "darwin", "bolsche", "doflein"],
            "organismus": ["organism"],
        },
    },
    # ==================================================== LA TECHNIQUE, PREMIÈRE MANIÈRE
    # 1919-1926. L'analyste prescrit et interdit pour forcer la matière à venir. Ferenczi l'a
    # inventée, défendue devant les congrès, puis abandonnée — voir le groupe suivant.
    "technique_active": {
        "label": "La technique active : injonctions, frustration, forçage (1919-1926)",
        "termes": {
            "aktivitaet": ["aktivitat", "aktive[nrs]? tech", "aktive[nrs]? therapie",
                           "aktive[nrs]? eingr", "aktive[nrs]? massnahm", "aktive[nrs]? verfahr"],
            # « Gebot » doit exclure « zu Gebote stehen » (être à disposition), tournure courante
            # qui n'a rien d'une injonction : le regard arrière et le regard avant ont été posés
            # après lecture des contextes, pas devinés.
            "gebot_verbot": [r"(?<!zu )gebot(?:e|es|s)?\b(?!\s*ste|[’'])", "verbot"],
            "versagung": ["versagung", "gewahrung"],
            "forcierte_phantasie": [r"forcierte[nrs]? phantasi", "assoziationsfreiheit"],
            "eingriff": ["massnahme", "vorschrift", "kunstgriff"],
            "indikation": ["indikation"],
            "nacherziehung": ["nacherziehung"],
        },
    },
    # ==================================================== LA TECHNIQUE, SECONDE MANIÈRE
    # 1927-1933. Le contraire exact : on relâche au lieu de contraindre, on écoute au lieu de
    # prescrire, l'analyste s'admet faillible. C'est le Ferenczi que Freud désavouera.
    #
    # DEUX GROUPES POUR UN MÊME OBJET, ET C'EST VOULU. Les fusionner ferait disparaître le seul
    # renversement documenté du corpus : un auteur qui abandonne SA PROPRE technique.
    "relaxation": {
        "label": "Relaxation, néocatharsis, élasticité, tact : le tournant de 1927-1933",
        "termes": {
            "relaxation": ["relaxation", "entspannung", "nachgiebig"],
            "neokatharsis": ["neokathar", "kathar"],
            "elastizitaet": ["elastizitat", "elastisch"],
            # « takt » exclut « taktisch », « Taktik » : la tactique n'est pas le tact.
            "takt": [r"takt(?!i)", "einfuhlung"],
            "aufrichtigkeit": ["aufrichtigkeit"],
        },
    },
    # Le dispositif lui-même, commun aux deux manières. C'est le groupe le plus lourd du lexique
    # (`patient` 2 112 occurrences) : Ferenczi écrit depuis le fauteuil, comme Abraham depuis le
    # chevet — mais Abraham rapporte des CAS, Ferenczi décrit une RELATION à deux.
    "cure": {
        "label": "Le dispositif de la cure et ses deux personnes",
        "termes": {
            "technik": ["technik", "technisch", "verfahren"],
            # « kur » exclut kurz, Kurve, Kurs, Kurbel, kurtisan ; « heil » exclut heilig et le
            # mot nu « Heil ». Sans ces exclusions le concept central de la cure comptait aussi
            # « kurz » (bref), qui est partout.
            "kur": [r"kur(?!z|v|s|b|t)", "behandlung", "therap", r"heil(?!ig|\b)"],
            "analytiker": ["analytiker", "analysand", "lehranalyse", "lehrgang"],
            "patient": ["patient", "kranke", "arzt"],
            "grundregel": ["grundregel", r"regel(?!ma|re|lo|wi|un|-)", "assoziation", "einfall"],
            "deutung": ["deutung"],
            "widerstand": [r"widerstand(?!sfahig)"],
            "analysenstunde": ["analysenstunde", r"stunde(?!nlang|nplan|n-)", "honorar",
                               "chaiselongue", "sofa"],
            "beendigung": ["beendig"],
        },
    },
    # ==================================================== LE SENS DE LA RÉALITÉ
    # « Entwicklungsstufen des Wirklichkeitssinnes » (1913) : comment l'enfant passe de la
    # toute-puissance hallucinatoire à l'acceptation du réel. `wirklichkeitssinn` ne compte que
    # 3 occurrences dans tout le reste du corpus allemand contre 41 chez lui.
    "wirklichkeitssinn": {
        "label": "Les stades du sens de la réalité et l'omnipotence",
        "termes": {
            "wirklichkeitssinn": ["wirklichkeitssinn", "wirklichkeitsinn", "realitatssinn"],
            "allmacht": ["allmacht"],
            # « geste » borné, « gebarde » excluant « gebardet » (se comporter). Le motif
            # « zauber » a été retiré à l'audit : il tirait le concept vers le folklore.
            "magische_geste": [r"geste[ns]?\b", r"gebarde(?!t)", "magi"],
            "halluzinatorisch": ["halluzin"],
            "realitatsprinzip": ["realitatsprinzip", "wirklichkeitsprinzip", "lustprinzip",
                                 "realitatsprufung"],
            "unlustbejahung": ["unlustbejahung", "verneinung", "bejahung"],
            # Les motifs nus « stufe », « phase », « stadium » ont été RETIRÉS à l'audit : ils
            # attrapaient toute périodisation, y compris celles qui n'ont rien de génétique.
            "entwicklungsstufe": ["entwicklungsstufe", "entwicklungsperiode",
                                  "realitatsentwicklung", "ichentwicklung"],
            "animismus": ["animis"],
            "anpassung": ["anpass"],
        },
    },
    # « Introjektion und Übertragung » (1910) — l'article qui donne son nom à un concept que
    # Karl Abraham reprendra et que Melanie Klein bâtira. Le mot est chez Abraham aussi : ce
    # n'est pas une raison de l'exclure d'ici. Chaque auteur garde SES catégories, et un mot
    # partagé garde le sens que SON corpus lui donne — la couche de comparaison est ailleurs.
    "introjektion": {
        "label": "Introjection, projection, identification et symbole",
        "termes": {
            # « einverleib » (incorporer) a été retiré à l'audit : c'est le concept d'Abraham,
            # et chez Ferenczi il désigne l'ingestion au sens propre dans une majorité de cas.
            "introjektion": ["introjekt"],
            "projektion": ["projektion", "projizier"],
            "identifizierung": ["identifizier"],
            "symbol": ["symbol"],
            "verschiebung": ["verschiebung"],
        },
    },
    "uebertragung": {
        "label": "Le transfert, la suggestion et l'hypnose",
        "termes": {
            "ubertragung": ["ubertragung"],
            # Quinze occurrences, et pourtant retenu : Ferenczi est le premier à faire du
            # contre-transfert un objet technique, et le mot n'apparaît qu'une fois dans tout
            # le reste du corpus allemand. Rareté n'est pas insignifiance quand l'écart est tel.
            "gegenubertragung": ["gegenubertragung"],
            "suggestion": ["suggestion", "suggestiv"],
            "hypnose": ["hypnose", "hypnot"],
            "objektliebe": ["objektliebe", "ubertragungsliebe"],
        },
    },
    # ==================================================== SA CLINIQUE
    # Le terrain qu'il a ouvert : la maladie ORGANIQUE prise dans la libido. « Pathonévrose » est
    # son mot (48 occurrences chez lui, 8 ailleurs) ; il désigne la névrose qui se greffe sur une
    # lésion réelle. C'est le pendant clinique exact de sa bioanalyse.
    "pathoneuroses": {
        "label": "Pathonévroses, névroses d'organe et névroses actuelles",
        "termes": {
            "pathoneurose": ["pathoneuros"],
            "organneurose": ["organneuros", "organerkrankung", "organbetatigung"],
            "organ": [r"organ\b", r"organe\b", r"organen\b", r"organs\b", r"organes\b",
                      "organteil", "organgefuhl", "organlibido"],
            "hypochondrie": ["hypochondri", "hypochonder"],
            "paralysie_generale": [r"paralyse\b", "paralytisch", "paralytik", r"paralysis\b"],
            "materialisation": ["materialisation", "materialisier"],
            "konversion": ["konversion", "konvertier"],
            "neurasthenie": ["neurasthen", "aktualneuros"],
            "impotenz": ["impotenz", r"potenz\b", "potenzstorung", "potenzverkurzung"],
            "onanie": ["onanie", "onanist", "masturbat"],
            "passagere_symptome": ["passagere", "symptombildung"],
            "autotomie": ["autotomie"],
        },
    },
    # « Psychoanalytische Betrachtungen über den Tic » (1921) : `tic` compte 236 occurrences chez
    # lui contre 30 dans tout le reste du corpus. L'audit a vérifié que le motif n'attrape aucun
    # autre mot allemand — la crainte était fondée, la mesure l'a levée.
    "tic": {
        "label": "Tic, stéréotypie et décharge motrice",
        "termes": {
            "tic": [r"tic\b", r"tics\b", "tique"],
            "tiqueur": ["tiqueur"],
            "zuckung": ["zuckung", "zucken"],
            "stereotypie": ["stereotyp"],
            "katatonie": ["katato"],
            "epilepsie": ["epilep"],
            "anfall": ["anfall", "konvulsion", "chorea"],
            "krampf": ["krampf"],
            "lahmung": ["lahmung", "gelahmt"],
            "zwangshandlung": ["zwangshandlung", "zwangsneuros"],
        },
    },
    "kriegsneurosen": {
        "label": "Névroses de guerre et commotion",
        "termes": {
            "kriegsneurose": ["kriegsneuros", "kriegsneurotiker", "kriegshysteri"],
            "granate": ["granat"],
        },
    },
    # ==================================================== LE DERNIER FERENCZI
    # 1932-1933 : le traumatisme réel, le clivage, l'enfant à qui l'adulte impose sa langue.
    # C'est le Ferenczi que la psychanalyse mettra cinquante ans à relire.
    #
    # AVERTISSEMENT PORTÉ DANS LE LEXIQUE LUI-MÊME. Ce dernier Ferenczi tient, dans le corpus,
    # à quelques pages : le « Journal clinique » n'a paru qu'en 1985 et n'est pas dans le domaine
    # public. Le mot « Sprachverwirrung » a d'ailleurs été RETIRÉ à l'audit — six occurrences,
    # dont une seule dans le corps du texte. Ce que ce groupe décrit est donc réel mais MINCE,
    # et une densité calculée dessus dira surtout que le corpus s'arrête là.
    "trauma": {
        "label": "Traumatisme, commotion et clivage de la personnalité",
        "termes": {
            # Les exclusions écartent Traumarbeit, Traumanalyse, Traumauffassung, Traumabends —
            # c'est-à-dire le RÊVE (« Traum »), qui n'a rien à voir avec le traumatisme et qui
            # aurait multiplié le concept par trois.
            "trauma": [r"trauma(?!rbeit|nalyse|uffassung|bends)", "urtrauma", "sexualtrauma"],
            "erschutterung": ["erschutterung", "erschutterte"],
            "schock": ["schock", r"schreck(?!lich)"],
            "spaltung": ["spaltung", "personlichkeitsspaltung", "selbstspaltung", "abgespalten",
                         "fragmentierung", "atomisier"],
            "bewusstseinsverlust": ["trance", "bewusstlos", "ohnmacht", "dammerzustand"],
            "wiederholung": ["wiederholung", "abreagier"],
        },
    },
    "enfant_adulte": {
        "label": "L'enfant et l'adulte — tendresse, passion, éducation",
        "termes": {
            "kind": ["kind"],
            "erwachsene": ["erwachsene"],
            "zartlichkeit": ["zartlich"],
            "leidenschaft": ["leidenschaft"],
            "erziehung": ["erziehung", "padagog"],
            # « schuler » a été retiré à l'audit : il attrapait « Schülerin », « Schulerfahrung »
            # et surtout le contexte scolaire ordinaire, sans rapport avec la relation d'emprise.
            "lehrer": ["lehrer"],
            "autoritat": ["autoritat", "gehorsam", "trotzig", "trotzes"],
            "strafe": ["strafe", "bestraf", "drohung"],
            "saugling": ["saugling", "neugeboren", "wiegenkind"],
            "vertrauen": ["vertrauen", "aufrichtigkeit", "hypokrisie"],
        },
    },
    # ==================================================== LE FONDS ANALYTIQUE QU'IL PARTAGE
    # LES CINQ GROUPES CI-DESSOUS ONT ÉTÉ AJOUTÉS APRÈS MESURE, ET L'OUBLI QU'ILS RÉPARENT MÉRITE
    # D'ÊTRE DIT. Le lexique s'était d'abord limité à ce que Ferenczi a d'INHABITUEL — génitalité,
    # thalassa, technique, trauma. Résultat mesuré : 58 % de ses atomes qualifiés, contre 78 à
    # 82 % pour les autres auteurs. Quarante-deux pour cent de son œuvre était muette, non parce
    # qu'elle ne dit rien, mais parce qu'elle parle d'inconscient, de refoulement, de rêve et de
    # névrose — c'est-à-dire de ce qu'un psychanalyste écrit tous les jours.
    #
    # LA RÈGLE DU PROJET N'EST PAS « CHAQUE AUTEUR N'A QUE CE QUI LE DISTINGUE ». Elle est : chaque
    # auteur est décrit avec SES catégories, définies sur SON texte. Un concept partagé reste un
    # concept de lui, avec les motifs et les fréquences mesurés chez lui. Ne retenir que sa
    # singularité reviendrait à ne le décrire que par contraste avec les autres — exactement
    # l'erreur symétrique de celle que le lexique par auteur voulait éviter.
    #
    # Gain mesuré : 2 370 atomes muets sur 3 834, soit une qualification portée de 58 % à 84 %.
    "episteme": {
        "label": "La psychanalyse comme science",
        "termes": {
            "psychoanalyse": ["psychoanaly", "analytisch"],
            "wissenschaft": ["wissenschaft", "forschung", "theorie", "literatur", "hypothese"],
            "erfahrung": ["erfahrung", "beobacht", "untersuchung", "experiment"],
        },
    },
    "appareil": {
        "label": "Conscient, inconscient, refoulement",
        "termes": {
            "unbewusst": ["unbewusst", "vorbewusst", "bewusstsein", "bewusste"],
            "verdraengung": ["verdrang", "zensur", "abwehr"],
            # LE MOI, JAMAIS LE PRONOM. « ich » et « es » sont « je » et « cela » en allemand
            # ordinaire — 3 553 atomes de Ferenczi les contiennent. La restriction est reprise
            # telle quelle du lexique de Freud, où ce piège a déjà été mesuré et documenté.
            "ich_instanz": [r"das ich\b", r"ichs\b", "ichideal", "uberich", "ich-ideal",
                            r"das es\b"],
            "gedaechtnis": ["erinnerung", "gedachtnis", "vergessen", "amnesie"],
        },
    },
    "sexualitaet": {
        "label": "Sexualité, libido, perversion, narcissisme",
        "termes": {
            "sexualitaet": ["sexual", "sexuell", "geschlechtlich"],
            # SON TERRAIN PROPRE, et il avait été manqué : « Zur Nosologie der männlichen
            # Homosexualität (Homoerotik) » est de lui, et `homoerotik` compte 77 occurrences
            # chez lui contre 3 dans tout le reste du corpus allemand — le rapport le plus élevé
            # de son vocabulaire après « amphimixis ». Il forge « homoérotisme » pour distinguer
            # l'orientation du désir de l'acte.
            "homoerotik": ["homoerot", "homosexual", "heteroerot", "invers"],
            "perversion": ["pervers", "fetisch", "sadis", "masochis", "exhibition", "voyeur"],
            "libido": ["libido", "libidin"],
            "narzissmus": ["narziss", "autoerot"],
        },
    },
    "famille": {
        "label": "Père, mère, fratrie, Œdipe",
        "termes": {
            "vater": ["vater"],
            "mutter": ["mutter"],
            "eltern": ["eltern"],
            "geschwister": ["geschwister", "bruder", "schwester"],
            "oedipus": ["odipus", "oedipus", "inzest", "kastration"],
        },
    },
    "clinique_commune": {
        "label": "Rêve, angoisse, névrose, caractère",
        "termes": {
            # « traum » exclut « trauma » et sa famille : le rêve n'est pas le traumatisme, et
            # sans cette exclusion les deux concepts se confondraient chez l'auteur même qui
            # tient le plus aux deux.
            "traum": [r"traum(?!a)", "traumdeut", "traumarbeit", "tagtraum"],
            "angst": ["angst", "phobie", "furcht"],
            "hysterie": ["hysteri"],
            "neurose": ["neuros", "neurotiker", "neurotisch"],
            "charakter": ["charakter"],
            "zwang": ["wiederholungszwang", "zwang"],
            "witz": ["witz", "komisch", "humor"],
            "religion": ["religio", "gott", "aberglaub", "magisch", "totem"],
        },
    },
}


# --------------------------------------------------------------------------- FONCTIONS
# Ferenczi ne raisonne ni comme Freud (qui construit une théorie) ni comme Abraham (qui rapporte
# des cas) ni comme Rank (qui aligne des versions d'un mythe). Il ESSAIE quelque chose sur un
# patient, dit ce que ça donne, et revient sur ce qu'il a dit. Deux fonctions lui sont propres :
# l'essai technique et l'analogie biologique.
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
                      r"\bscheint\b", r"\banzunehmen\b", r"\bnehmen wir an\b", r"\bwohl\b"],
    },
    {
        "id": "essai_technique",
        "label": "Essai technique rapporté",
        "aide": "LE geste de Ferenczi : il modifie sa manière de conduire la cure et rapporte ce "
                "que la modification produit. Ni un cas clinique (Abraham) ni une thèse (Freud) — "
                "une EXPÉRIENCE sur le dispositif, dont il est lui-même l'instrument.",
        "marqueurs": [r"\bich versuchte\b", r"\bich forderte\b", r"\bich verbot\b",
                      r"\bich liess\b", r"\bversuchsweise\b", r"\bich ordnete an\b",
                      r"\bin einem falle versuchte\b", r"\bich habe.{0,30}?\bversucht\b",
                      r"\bdie aktive technik\b", r"\bmeine technik\b"],
    },
    {
        "id": "analogie_biologique",
        "label": "Analogie biologique (utraquisme)",
        "aide": "Il éclaire le psychique par le vivant et réciproquement — c'est ce qu'il nomme "
                "UTRAQUISME, et c'est la méthode de la « Genitaltheorie » entière. Le marqueur "
                "établit qu'une comparaison au vivant est faite ; il ne dit pas si elle vaut.",
        "marqueurs": [r"\bwie beim tier", r"\bin der tierreihe\b", r"\bbiologisch\b",
                      r"\bphylogenetisch\b", r"\bstammesgeschichtlich\b",
                      r"\bbei den amphibien\b", r"\bwie der organismus\b", r"\butraquis"],
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
        "id": "revision",
        "label": "Révision / correction de soi",
        "fiabilite": "a_confirmer",
        "aide": "LE SIGNAL LE PLUS ATTENDU DE CET AUTEUR, et c'est pourquoi il reste « à "
                "confirmer » plutôt que promu. Ferenczi a soutenu la technique active puis l'a "
                "abandonnée pour son contraire : s'il existe dans ce corpus un auteur qui se "
                "corrige, c'est lui. Raison de plus pour ne rien affirmer sans avoir lu — chez "
                "Rank, un marqueur du même genre a donné 0 confirmé sur 5.",
        "marqueurs": [r"\b(ich|wir)\b.{0,30}?\bkorrigier", r"\bberichtigen\b", r"\birrte\b",
                      r"\birrtumlich", r"\bnicht aufrechterhalten\b", r"\bubertrieben\b",
                      r"\b(fruher|damals|seinerzeit)\b.{0,70}?"
                      r"\b(geglaubt|gemeint|behauptet|angenommen|vertreten|auffassung)\b"],
    },
    {
        "id": "objection",
        "label": "Objection anticipée",
        "fiabilite": "a_confirmer",
        "marqueurs": [r"\beinwand(?!frei|er)", r"\beinwendung", r"\bman konnte sagen\b",
                      r"\bdagegen spricht\b", r"\bman wird einwenden\b"],
    },
    {
        "id": "renvoi_freud",
        "label": "Renvoi explicite à Freud",
        "aide": "La phrase invoque explicitement une position de Freud. Fonction ÉTABLIE, sur le "
                "modèle d'Abraham : le motif prouve que la phrase s'adosse à Freud, il ne dit "
                "pas si c'est pour l'appuyer, le prolonger ou s'en écarter — et chez Ferenczi, "
                "les trois arrivent.",
        "marqueurs": [r"\bfreud\w*\s+(auffassung|ansicht|annahme|lehre|meinung|arbeit|aufsatz)\b",
                      r"\b(nach|mit|gemass) freud\b", r"\bwie freud\b",
                      r"\bfreud hat\b.{0,40}?\b(gezeigt|nachgewiesen|hervorgehoben|gelehrt)\b",
                      r"\bin ubereinstimmung mit freud\b"],
    },
]

# Ceux que Ferenczi discute : la première génération analytique, ses coauteurs hongrois (Hollós,
# Hermann, Bálint, Róheim), et les naturalistes que sa bioanalyse convoque.
NOMS_AUTEURS = ["freud", "abraham", "rank", "jung", "jones", "bleuler", "stekel", "sadger",
                "hollos", "hermann", "balint", "roheim", "reik", "simmel", "eitingon",
                "groddeck", "reich", "klein", "lamarck", "haeckel", "darwin", "bolsche"]

MARQUEURS_STATUT = {
    "modalise":     [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bscheint\b",
                     r"\bdurfte\b", r"\bwohl\b", r"\bmoglicherweise\b", r"\bkaum\b", r"\betwa\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"\bberichtet\b", r"\berzahlt\b", r"\bnach \w+\b", r"\bzitiert\b",
                     r"\bangeblich\b", r"\bteilt mit\b"],
}


# --------------------------------------------------------------------------------------------
# CE QUI A ÉTÉ PROPOSÉ PUIS RETIRÉ À L'AUDIT — neuf sous-concepts.
#
# Trace obligatoire : sans elle, chacun de ces neuf sera reproposé, avec les mêmes arguments et
# le même résultat. Le motif du retrait est chaque fois une MESURE, jamais un avis.
#
#   sprachverwirrung   6 occurrences, dont UNE SEULE dans le corps du texte — les autres sont
#                      la table des matières et des renvois. L'article de 1933 qui porte ce titre
#                      est bien dans le volume, mais son vocabulaire propre n'y est pas.
#   kinderanalyse      22 occurrences, dont 17 de paratexte (titres, sommaire, index). Il en
#                      reste 5 : sous le seuil.
#   parallele          50 occurrences, mais la moitié est de l'allemand ordinaire (« parallel
#                      dazu », « parallele Erscheinung ») sans rapport avec le parallélisme
#                      bio-psychique que le concept prétendait nommer.
#   hilflosigkeit      21 occurrences, atteintes seulement en additionnant `hilflos` et
#                      `todesangst`, deux notions étrangères l'une à l'autre. Le seuil n'était
#                      franchi que par la somme.
#   trance             6 occurrences, toutes authentiques — et retiré quand même : trop peu pour
#                      fonder un concept, et déjà couvert par `bewusstseinsverlust`.
#   rente              19 occurrences, mais le motif `entschadigung` (indemnisation) attrapait
#                      des emplois économiques ordinaires. Le concept aurait mesuré autre chose
#                      que la névrose de rente qu'il visait.
#   frigiditat         16 occurrences dont 10 par `anasthesi`, qui attrape l'anesthésie
#                      chirurgicale.
#   onychophagie       6 occurrences. Ce sont des exemples cliniques, pas un concept.
#   krankheitsnarzissmus  11 occurrences, dont trois lignes d'index.
