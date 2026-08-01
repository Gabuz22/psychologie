#!/usr/bin/env python3
"""LEXIQUE — la taxonomie du corpus psychanalytique : fonction, statut épistémique, concepts.

DÉRIVÉ EMPIRIQUEMENT, pas deviné. Chaque famille de marqueurs ci-dessous a été relevée en lisant
des passages réels de « Die Traumdeutung » (chap. I, II, IV, V, VII) puis COMPTÉE sur le texte
intégral (13 125 phrases). Les fréquences mesurées figurent en commentaire : elles disent ce sur
quoi on peut s'appuyer, et ce qui est rare (donc précieux, mais jamais présenté comme exhaustif).

Trois couches indépendantes et cumulables (multigroupe : un atome peut porter plusieurs valeurs) :

  1. FONCTION  — ce que la phrase FAIT dans l'argumentation (thèse, objection, révision…).
                 Chaque fonction porte une FIABILITÉ mesurée sur le texte réel :
                   « etablie »     → le marqueur suffit, la qualification est tenue pour acquise ;
                   « a_confirmer » → le marqueur ne fait que SIGNALER un candidat ; l'atome part
                                     dans une liste à vérifier, jamais dans les faits établis.
                 Pourquoi : « révision » a été mesurée à ~3 vrais positifs sur 7 détections
                 (« nunmehr » narratif, « korrigieren » d'un rêve ou d'un défaut physique…).
                 Un lexique déterministe ne peut pas ÉTABLIR seul qu'un auteur se corrige — il
                 peut seulement dire où regarder. Doctrine reprise du corpus AXA : ce qui n'est
                 pas prouvé est listé comme « à vérifier », jamais présenté comme un fait.
  2. STATUT    — avec quelle force elle l'affirme (doctrine reprise du projet AXA :
                 affirmé > modalisé > interrogatif > rapporté ; on ne durcit JAMAIS un propos).
  3. CONCEPTS  — de quoi elle parle, dans l'ontologie psychanalytique.

L'ontologie de concepts est volontairement ORGANISÉE PAR GROUPES et non à plat : l'objectif à
terme est de voir comment les courants postérieurs (Jung, Klein, Lacan…) se recomposent à partir
des mêmes atomes. Ajouter un auteur = ajouter des concepts et des groupes, sans toucher au moteur.

Tout est en forme REPLIÉE (minuscules, sans diacritiques, ß→ss) et cherché en frontière de mot :
l'orthographe de 1900 (« Unbewußte », « Bewusstsein », « Verdrängung ») est ainsi couverte sans
dépendre des variantes ß/ss.
"""
import re

from .segmentation import replier, replier_esszett

LEXIQUE_VERSION = "1.1.0"      # 1.1.0 : lexique multilingue (tables françaises) + concepts de la controverse Le Bon/Freud

# --------------------------------------------------------------------------- 1. FONCTION
# (occurrences mesurées sur Die Traumdeutung, 4e éd. — indicatives, jamais un quota)
FONCTIONS = [
    {
        "id": "inference",
        "label": "Inférence / conclusion",
        "aide": "Freud tire une conséquence de ce qui précède.",
        "mesure_traumdeutung": 342,
        "marqueurs": [r"\balso\b", r"\bdaher\b", r"\bsomit\b", r"\bfolglich\b", r"\bdemnach\b",
                      r"\bmithin\b", r"\bergibt sich\b", r"\bwir schliessen\b", r"\bdaraus folgt\b"],
    },
    {
        "id": "hypothese",
        "label": "Hypothèse / conjecture",
        "aide": "Proposition avancée sans être affirmée — le conditionnel de la recherche.",
        "mesure_traumdeutung": 301,
        "marqueurs": [r"\bvielleicht\b", r"\bwahrscheinlich\w*\b", r"\bvermutlich\b", r"\bduerfte\b",
                      r"\bscheint\b", r"\bes ist moeglich\b", r"\bich vermute\b", r"\banzunehmen\b",
                      r"\bnehmen wir an\b", r"\bwenn wir annehmen\b"],
    },
    {
        "id": "methode",
        "label": "Énoncé méthodologique",
        "aide": "Description du procédé analytique lui-même (analyse, déchiffrement, technique).",
        "mesure_traumdeutung": 496,
        "marqueurs": [r"\banalyse", r"\bdeutung", r"\bverfahrens?\b", r"\bmethoden?\b", r"\btechniken?\b",
                      r"\bzerlegt\b", r"\bzerlegung\b", r"\bauflosung\b"],
    },
    {
        "id": "question",
        "label": "Question de recherche / auto-interrogation",
        "aide": "Freud s'interroge lui-même pour relancer l'enquête — moteur d'avancée du texte.",
        "mesure_traumdeutung": 236,
        "marqueurs": [r"\?"],
    },
    {
        "id": "analogie",
        "label": "Analogie / métaphore",
        "aide": "Comparaison illustrative (la mouche qu'on chasse, l'appareil optique…).",
        "mesure_traumdeutung": 123,
        "marqueurs": [r"\bgleichsam\b", r"\bwie wenn\b", r"\betwa wie\b", r"\bvergleich",
                      r"\bbeispielsweise\b", r"\bals ob\b", r"\bahnlich wie\b"],
    },
    {
        "id": "association",
        "label": "Association libre rapportée",
        "aide": "« Einfall » : ce qui vient à l'esprit — la donnée brute de la méthode.",
        "mesure_traumdeutung": 39,
        "marqueurs": [r"\beinfall", r"\bfallt mir\b", r"\beinfiel\b", r"\bfiel mir ein\b",
                      r"\bassoziation"],
    },
    {
        "id": "savoir_etabli",
        "label": "Renvoi à un savoir établi",
        "aide": "« bekanntlich », « wir wissen » : posé comme acquis, donc non redémontré.",
        "mesure_traumdeutung": 29,
        "marqueurs": [r"\bbekanntlich\b", r"\bwir wissen\b", r"\bbekannt ist\b", r"\bwie bekannt\b"],
    },
    {
        "id": "objection",
        "label": "Objection anticipée",
        "aide": "Freud met en scène une contre-objection AVANT d'y répondre. Rare, très informatif.",
        "fiabilite": "a_confirmer",
        "mesure_traumdeutung": 27,
        # « freilich » a été RETIRÉ après lecture : c'est un adverbe concessif (« certes », « il est
        # vrai que »), pas une objection mise en scène. Il produisait 60 candidats sur 177, dont
        # aucun des dix lus n'était une contre-objection — et dans « Gradiva » il apparaissait
        # jusque dans les dialogues cités du roman. Même défaut que « nicht mehr » pour la
        # révision : un mot fréquent et vague noie le signal rare et précis.
        # Deux homonymies écartées, découvertes en lisant les candidats un par un :
        #   • « einwandfrei » = irréprochable, sans défaut — un tout autre mot (11 occurrences,
        #     dont « eine einwandfreie Deutung », qui est un ÉLOGE, pas une objection) ;
        #   • « einwandern » = immigrer — dans Totem und Tabu, les âmes qui « migrent » dans
        #     d'autres personnes se retrouvaient comptées comme objections.
        "marqueurs": [r"\beinwand(?!frei|ern)", r"\beinwendung", r"\beinwenden\b",
                      r"\bman koennte sagen\b", r"\bman kann einwenden\b",
                      r"\bdagegen spricht\b", r"\bdagegen laesst sich\b"],
    },
    {
        "id": "revision",
        "label": "Révision / correction de soi",
        "aide": "SIGNAL D'ÉVOLUTION THÉORIQUE : Freud corrige ou nuance sa propre position antérieure.",
        "fiabilite": "a_confirmer",
        "mesure_traumdeutung": 37,
        # PRÉCISION AVANT RAPPEL — vérifié sur le texte réel. Un premier jeu de marqueurs incluait
        # « nicht mehr » : il produisait 62 détections sur 99, presque toutes fausses (« le rêveur
        # ne se souvenait plus », « cet auteur ne défend plus sa thèse », « le livre n'est plus
        # ignoré »). C'est une simple négation de continuité, pas une révision. Sur LE signal
        # central du projet, un faux positif silencieux vaut pire que rien : on exige donc soit une
        # formule explicite de correction, soit un adverbe de temps passé ACCOMPAGNÉ d'un verbe
        # d'assertion (c'est le couple qui fait la révision, pas l'adverbe seul).
        # « korrigieren » nu est également trop large : dans le texte réel il désigne aussi bien le
        # rêve qui corrige une perception, une patiente qui corrige un défaut physique, ou un mot
        # rectifié au réveil (« später korrigiert: Angorakatze »). On exige donc que la correction
        # porte sur un ÉNONCÉ ANTÉRIEUR (behauptung, annahme, meinung, text…) ou sur Freud lui-même.
        "marqueurs": [
            r"\b(behauptung|annahme|meinung|ansicht|auffassung|darstellung|text|lehre|satz)\b"
            r".{0,50}?\bkorrigier",
            r"\bkorrigier\w*\b.{0,50}?\b(behauptung|annahme|meinung|ansicht|auffassung|fruhere)\b",
            r"\b(ich|wir)\b.{0,30}?\bkorrigier",
            r"\bberichtigen\b", r"\bzuruecknehmen\b", r"\birrte\b", r"\birrtuemlich",
            r"\bals unrichtig\b", r"\bnicht aufrechterhalten\b", r"\bich muss gestehen\b",
            r"\b(fruher|damals|einst|seinerzeit)\b.{0,70}?"
            r"\b(geglaubt|gemeint|behauptet|angenommen|vertreten|meinung|ansicht|auffassung)\b",
            r"\b(geglaubt|gemeint|behauptet|angenommen|vertreten|meinung|ansicht)\b.{0,40}?"
            r"\b(fruher|damals|einst|seinerzeit)\b",
            r"\bnunmehr\b",
        ],
    },
    {
        "id": "auto_citation",
        "label": "Renvoi à son propre travail",
        "aide": "SIGNAL DE COHÉRENCE : rappel explicite d'une thèse déjà posée (traçable, vérifiable).",
        "fiabilite": "a_confirmer",
        "mesure_traumdeutung": 10,
        # L'allemand rejette le participe en FIN de proposition : entre « wir haben » et
        # « bezeichnet » il peut y avoir toute une subordonnée. Le motif doit donc tolérer un écart
        # large (non gourmand, borné pour rester en frontière de phrase).
        "marqueurs": [r"\bwir haben\b.{0,90}?\b(gesehen|gesagt|erfahren|bezeichnet|behauptet|gehoert)\b",
                      r"\bich habe\b.{0,90}?\b(gezeigt|behauptet|ausgefuehrt|dargelegt|erwahnt)\b",
                      r"\bwie oben\b", r"\bfrueher erwahnt\b", r"\ban anderer stelle\b"],
    },
    {
        "id": "rapport_tiers",
        "label": "Rapport d'un tiers (littérature)",
        "aide": "Observation attribuée à un autre auteur — dialogue avec la littérature savante.",
        "mesure_traumdeutung": None,   # détecté par NOMS_AUTEURS, pas par marqueur lexical
        "marqueurs": [r"\bnach \w+s (ansicht|meinung)\b", r"\bberichtet(?:e|en)?\b", r"\bzitiert(?:e|en)?\b",
                      r"\bbehauptet \w+, dass\b"],
    },
]

# Auteurs cités dans la littérature onirique du chapitre I (repérés dans le texte réel).
# Sert la fonction « rapport_tiers » : une phrase qui les nomme rapporte un propos extérieur.
NOMS_AUTEURS = ["maury", "spitta", "hildebrandt", "strumpell", "wundt", "delboeuf", "scherner",
                "volkelt", "binz", "burdach", "jessen", "radestock", "vaschide", "weygandt",
                "fechner", "robert", "hervey", "benini", "giessler", "purkinje", "schleiermacher"]

# --------------------------------------------------------------------------- 2. STATUT ÉPISTÉMIQUE
# Doctrine AXA transposée : on n'affirme jamais plus fort que le texte. « affirme » est le défaut,
# mais toute marque de doute, d'interrogation ou d'attribution le DÉCLASSE (le plus prudent gagne).
STATUTS = ["affirme", "modalise", "interrogatif", "rapporte"]

# FLEXION ALLEMANDE — correctif SÉLECTIF (2026-07-28), et surtout pas global.
# Constat : « Wahrscheinlicher ist eine solche Verteilung » recevait le statut « affirmé ».
# Un énoncé modalisé durci en affirmation, c'est-à-dire exactement ce que la doctrine interdit.
# La cause est le «  » final, que la déclinaison allemande fait échouer.
#
# MAIS le retirer partout aurait été pire, et la mesure l'a montré : « etwa » (à peu près)
# deviendrait « etwas » (quelque chose) — 717 fausses modalisations à lui seul ; « als ob »
# deviendrait « als Objekt » ; « wohl » attraperait « Wohlgefallen » et « Wohlbefinden ».
# Le «  » final PROTÈGE dans ces cas-là ; il ne gêne que là où la flexion est régulière.
# On a donc étendu huit marqueurs, un par un, chacun vérifié par comptage — et laissé les autres.
MARQUEURS_STATUT = {
    "modalise":     [r"\bvielleicht\b", r"\bwahrscheinlich\w*\b", r"\bvermutlich\b", r"\bscheint\b",
                     r"\bduerfte\b", r"\bwohl\b", r"\bmoeglicherweise\b", r"\betwa\b", r"\bkaum\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"\bberichtet(?:e|en)?\b", r"\berzahlt(?:e|en)?\b", r"\bnach \w+\b", r"\bzitiert(?:e|en)?\b",
                     r"\bsoll \w+ haben\b", r"\bangeblich\w*\b"],
}

# --------------------------------------------------------------------- 2 bis. TABLES FRANÇAISES
# L'entrée de Le Bon (1895) rend le lexique MULTILINGUE : les identifiants (fonctions, statuts,
# concepts) sont neutres et communs ; seuls les MOTIFS dépendent de la langue. Règle d'honnêteté :
# une fonction ou un concept SANS motifs français n'est simplement PAS mesuré dans un texte
# français — il apparaît alors dans les non-qualifiés, visibles, plutôt que d'être « traduit »
# par des marqueurs approximatifs qui produiraient des faux positifs silencieux.
# Tous les motifs sont en forme REPLIÉE (minuscules, sans accents) : « peut-être » → « peut-etre ».

MARQUEURS_FONCTIONS_FR = {
    "inference":     [r"\bdonc\b", r"\bpar consequent\b", r"\bdes lors\b", r"\bil en resulte\b",
                      r"\bil s'ensuit\b", r"\bc'est pourquoi\b", r"\bpar suite\b",
                      r"\bon peut conclure\b", r"\bnous pouvons conclure\b"],
    "hypothese":     [r"\bpeut-etre\b", r"\bprobablement\b", r"\bvraisemblablement\b",
                      r"\bsans doute\b", r"\bil semble\b", r"\bil est possible\b",
                      r"\bsupposons\b", r"\bsi l'on admet\b", r"\bon peut supposer\b"],
    # « procédé » est ÉCARTÉ : replié, il devient « procede » et se confond avec le verbe
    # « procède » (« ces sentiments procèdent de… »), fréquent chez Le Bon dans un tout autre sens.
    "methode":       [r"\bmethodes?\b", r"\banalyse", r"\bexamen\b", r"\bclassification\b"],
    "question":      [r"\?"],
    "analogie":      [r"\bcomme si\b", r"\bsemblables? a\b", r"\bpareils? a\b", r"\bcomparable",
                      r"\bde meme que\b", r"\bpar exemple\b", r"\ba la facon de\b", r"\banalog"],
    "savoir_etabli": [r"\bon sait que\b", r"\bchacun sait\b", r"\bnul n'ignore\b",
                      r"\bil est bien connu\b", r"\bcomme on le sait\b", r"\bnous savons\b"],
    "objection":     [r"\bon objectera\b", r"\bon pourrait objecter\b", r"\bl'objection\b",
                      r"\bon dira que\b", r"\bon repondra\b"],
    "auto_citation": [r"\bnous avons vu\b", r"\bnous avons dit\b", r"\bnous l'avons (?:vu|dit|montre)\b",
                      r"\bj'ai montre\b", r"\bcomme je l'ai (?:dit|montre)\b", r"\bdit plus haut\b",
                      r"\bavons montre\b"],
    # « cite » est ÉCARTÉ : replié, « la cité » (Fustel de Coulanges a écrit « La Cité antique »,
    # discuté par Le Bon) devient « la cite » et se compterait comme citation. De même « rapporte »
    # exclut « se rapporte à » (= concerner), très fréquent dans la prose de 1895.
    "rapport_tiers": [r"\bd'apres \w+", r"\bselon \w+", r"(?<!se )\brapporte\b", r"\braconte\b",
                      r"\becrivait\b", r"\becrit que\b"],
    # SANS équivalent français assumé : « association » (l'Einfall est un terme technique de la
    # cure, absent chez Le Bon) et « revision » (le signal central du projet exige des formules
    # explicites de correction de soi ; aucune n'est attestée chez Le Bon — plutôt aucun marqueur
    # que des marqueurs faibles sur LE signal où un faux positif vaut pire que rien).
}

MARQUEURS_STATUT_FR = {
    "modalise":     [r"\bpeut-etre\b", r"\bprobablement\b", r"\bsans doute\b", r"\bsemble",
                     r"\bparait\b", r"\bvraisemblablement\b", r"\ba peine\b", r"\bpourrait\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"(?<!se )\brapporte\b", r"\braconte\b", r"\bd'apres \w+", r"\bselon \w+",
                     r"\bpretend", r"\bdit-on\b", r"\bparait-il\b"],
}

# Auteurs que Le Bon discute nommément (repérés dans le texte réel de 1895) — même rôle que
# NOMS_AUTEURS pour la littérature onirique : nommer l'un d'eux = rapporter un propos extérieur.
NOMS_AUTEURS_FR = ["taine", "tocqueville", "spencer", "tarde", "ribot", "fustel de coulanges"]

# --------------------------------------------------------------------------- 3. CONCEPTS
# Ontologie psychanalytique par GROUPES. Extensible : ajouter Jung/Klein/Lacan = ajouter des
# entrées, jamais toucher au moteur. Termes en forme repliée (ß→ss, sans diacritiques).
#
# ACCUEIL D'AUTRES AUTEURS (structure posée avant d'en avoir besoin, tant que l'ontologie freudienne
# est encore malléable — la refaire après coup coûterait bien plus cher).
#
# Le pari du projet est qu'un courant postérieur ne s'invente pas de toutes pièces : il RECOMPOSE
# des atomes déjà là, en déplaçant les accents. La comparaison n'a donc de sens que si les auteurs
# partagent le MÊME jeu de concepts — sinon on ne mesurerait que la différence des grilles de
# lecture. D'où la règle : un concept propre à un auteur est ajouté au groupe EXISTANT qui lui
# correspond, avec le champ `auteurs` ; il n'ouvre un groupe neuf que si aucun ne peut l'accueillir.
#
#   « archetyp » (Jung)            → groupe `topique`      (une instance de plus, pas un ailleurs)
#   « position_depressive » (Klein) → groupe `developpement`
#   « objet_partiel » (Klein)      → groupe `famille` ou `pulsion` selon l'usage attesté
#   « objet_petit_a » (Lacan)      → groupe `desir`
#
# `auteurs` absent = concept commun, cherché chez tout le monde (c'est le cas de tout le lexique
# freudien actuel). `auteurs: ["jung"]` = cherché seulement dans les œuvres de cet auteur, ce qui
# évite de compter chez Freud un mot qu'il n'employait pas.
#
# La langue reste l'ALLEMAND pour Jung et Klein (qui écrivent en allemand), et demandera un
# lexique français pour Lacan — d'où le champ `langue` prévu dans le registre des œuvres.
CONCEPTS = {
    "reve": {
        "label": "Rêve et travail du rêve",
        "termes": {
            # PIÈGE MAJEUR (vérifié sur le texte, deux fois plutôt qu'une).
            #
            # 1) « traum » nu capte aussi « Trauma », « traumatisch » : deux notions distinctes,
            #    et la confusion tombait au pire endroit — « Jenseits des Lustprinzips » argumente
            #    à partir de la névrose TRAUMATIQUE pour poser la compulsion de répétition
            #    (24 des 38 atomes « rêve » de ce livre parlaient en fait de trauma).
            #
            # 2) Mais exclure bêtement « traum » suivi d'un « a » est PIRE : l'allemand compose,
            #    et « Traumarbeit » (le travail du rêve, 126 occurrences !), « Traumanalyse »,
            #    « Traumangst », « Traumätiologie » sont des mots du RÊVE qui commencent par
            #    « trauma… ». La première version de ce correctif les avait tous perdus.
            #
            # On discrimine donc sur la FAMILLE MORPHOLOGIQUE réelle de Trauma — c'est-à-dire
            # « trauma » terminé (Trauma/Traumas) ou suivi de ses seuls dérivés attestés
            # (traumatisch, traumatisier-, traumatolog-) — et jamais sur la lettre suivante.
            "traum": [r"traum(?!a(?:s?\b|ti(?:sch|sier)|tolog))"],
            "traumdeutung": ["traumdeutung"],
            "traumarbeit": ["traumarbeit"],
            "traumgedanke": ["traumgedanke", "traumgedanken"],
            # « manifeste » / « latente » nus retirés : adjectifs courants, qui peuvent qualifier
            # tout autre chose qu'un contenu de rêve. Les vrais emplois techniques (« manifester
            # Trauminhalt », « latente Traumgedanken ») restent captés par les termes composés.
            "trauminhalt": ["trauminhalt"],
            "verdichtung": ["verdichtung"],
            "verschiebung": ["verschiebung"],
            "entstellung": ["entstellung", "traumentstellung"],
            "symbol": ["symbol", "symbolik", "symbolisch"],
            "tagesrest": ["tagesrest", "tagesreste"],
            # Le sommeil est la CONDITION du rêve, et le grand absent de la première version du
            # lexique : 416 occurrences ignorées dans un livre sur les rêves. « (?!rock|zimmer) »
            # écarte les emplois non psychiques (robe de chambre, chambre à coucher).
            "schlaf": [r"schlaf(?!rock|zimmer)", "einschlaf", "schlummer"],
            "wachen": ["wachzustand", "wachleben", "erwachen", "wachend"],
        },
    },
    "topique": {
        "label": "Appareil psychique (lieux et instances)",
        "termes": {
            "unbewusst": ["unbewusst", "unbewusste", "unbewussten", "unbewusstes"],
            "vorbewusst": ["vorbewusst", "vorbewusste", "vorbewussten"],
            "bewusstsein": ["bewusstsein", "bewusst"],
            "zensur": ["zensur"],
            # LA REPRÉSENTATION — 763 occurrences, et pourtant absente de l'ontologie jusqu'à
            # l'audit 7. C'est le terme central du refoulement : ce qui est refoulé n'est pas un
            # affect ni un souvenir en général, mais « eine unverträgliche Vorstellung ». Le
            # motif ne prend que le SUBSTANTIF et ses composés (Vorstellungsinhalt,
            # Vorstellungskreis) — jamais le verbe « sich etwas vorstellen » (s'imaginer).
            "vorstellung": ["vorstellung"],
            "ich": ["ich-", "ichs"],          # « Ich » nu est trop ambigu (pronom) — voir note ci-dessous
            # « es » est le pronom « il/cela » en allemand : impossible à capter nu sans tout
            # ramasser. On ne le prend donc qu'après un déterminant, là où il désigne l'instance
            # (« das Es », « vom Es »). Comme pour « Ich », mieux vaut manquer que sur-détecter.
            #
            # DÉCELÉ PAR LA VALIDATION QUALITATIVE DES GRAPPES (2026-07) : « déterminant + es »
            # capte aussi les RELATIVES — « ein Spielzeug, über das es sich geärgert hatte »
            # (das = le jouet, es = l'enfant). Lus un par un, les 19 atomes antérieurs à 1923
            # étaient TOUS de ce type : le Ça n'existait pas encore, chaque détection était du
            # bruit — et faussait la chronologie de la seconde topique. Le discriminant est
            # mécanique : une relative est toujours PRÉCÉDÉE d'une préposition (« in dem es »,
            # « bei dem es », « über das es ») ; le Ça topique jamais (« das Es kennt », « im
            # Es » — les formes contractées, elles, ne peuvent pas ouvrir une relative).
            # Trois formes pronominales à écarter, toutes lues dans le corpus : la relative à
            # préposition (« über das es sich geärgert hatte »), la relative après virgule
            # (« das System, das es bezeichnet ») et le participe où « es » est objet (« dem es
            # modifizierenden Realitätsprinzip » — le principe de réalité qui LE modifie).
            # Le Ça topique ne se présente jamais ainsi.
            "es": [r"(?:vom|im|ins|zum) es\b",
                   r"(?<!in )(?<!bei )(?<!mit )(?<!von )(?<!zu )(?<!an )(?<!auf )(?<!aus )"
                   r"(?<!nach )(?<!uber )(?<!unter )(?<!vor )(?<!durch )(?<!fur )(?<!um )"
                   r"(?<!gegen )(?<!hinter )(?<!neben )(?<!zwischen )(?<!wahrend )(?<!, )"
                   r"(?:das|dem|des) es\b(?! \w+enden\b)"],
            # PIÈGE DE TRANSLITTÉRATION, resté invisible jusqu'à l'arrivée des « Neue Folge » :
            # ces termes étaient écrits « ueber-ich », comme si le ü devenait « ue ». Or le
            # repliement SUPPRIME les diacritiques : « Über-Ich » donne « uber-ich ». Résultat,
            # le SURMOI — l'une des trois instances de la seconde topique — n'était détecté nulle
            # part dans le corpus (48 mentions manquées dans les seules Neue Folge).
            # Les deux graphies sont gardées : le corpus mélange « Über-Ich » et « Überich ».
            "ueberich": ["uber-ich", "uberich"],
            # L'« appareil psychique » est le modèle central du chapitre VII — il manquait.
            "apparat": ["apparat", "instanz", "system"],
            # AUDIT 8 — 1 212 occurrences de « Person »/« Persönlichkeit », dont la
            # « Persönlichkeitsspaltung » et « die Person des Arztes ». Absent jusqu'ici parce
            # que le mot passe pour ordinaire ; il ne l'est pas chez un auteur qui décrit des
            # personnes en tant que telles.
            "person": ["person", "personlichkeit", "personen"],
            "psychisme": ["seelisch", "seele", "psychisch", "psyche"],
        },
    },
    # NOUVEAU GROUPE — le point de vue ÉCONOMIQUE (quantités d'énergie), distinct de la topique
    # (les lieux) et de la dynamique (les conflits). C'est la grille que Freud superpose aux deux
    # autres, et elle porte l'argument de « Jenseits » : 193 « Erregung » et 53 « Besetzung »
    # étaient jusqu'ici invisibles.
    "economie": {
        "label": "Économie psychique (énergie, quantités)",
        "termes": {
            "erregung": ["erregung", "erregt", "reizung"],
            # Les composés sont ÉNUMÉRÉS, jamais captés par un joker : même prudence que pour
            # « trieb ». Décelé par un test de l'audit 4 — « Aufmerksamkeitsbesetzung » n'était
            # pas vu, la frontière de mot excluant tout composé où « besetzung » est en second.
            # Liste relevée sur le texte, pas devinée (les 10 formes attestées ≥ 2 occurrences).
            "besetzung": ["besetzung", "besetzt",
                          r"(?:gegen|objekt|uber|hemmungs|energie|aufmerksamkeits|libido|probe|"
                          r"ziel|erinnerungs|bewusstseins|mehr)besetzung"],
            "spannung": ["spannung"],
            "abfuhr": ["abfuhr", "entladung"],
            "energie": ["energie", "quantitat", "intensitat"],
            "reiz": ["reizschutz", "reizmenge"],
            # L'affect est une QUANTITÉ chez Freud (Affektbetrag) : sa place est ici.
            # (?!ion) écarte « Affektion » — l'affection au sens MÉDICAL (nervöse Affektion,
            # 14 occurrences), qui n'est pas l'affect.
            "affekt": [r"affekt(?!ion)"],
            # L'ATTENTION — audit 4 (2026-07). Grandeur ÉCONOMIQUE chez Freud, pas
            # psychologie de sens commun : « Aufmerksamkeitsbesetzung » (investissement
            # d'attention) est le terme technique, d'où sa place dans ce groupe.
            "aufmerksamkeit": ["aufmerksamkeit"],
        },
    },
    # NOUVEAU GROUPE — mémoire et oubli : 266 « Erinnerung » ignorées, alors que le souvenir
    # d'enfance et le refoulement du souvenir sont la matière première de la méthode.
    "memoire": {
        "label": "Mémoire, souvenir, oubli",
        "termes": {
            "erinnerung": ["erinnerung", "erinnert", "erinnern"],
            # L'ÉVÉNEMENT VÉCU (240 occ.) — chez Freud ce n'est pas un mot ordinaire : c'est ce
            # qui, n'ayant pas été « abréagi », revient comme symptôme.
            "erlebnis": ["erlebnis", "erlebniss"],
            "gedaechtnis": ["gedachtnis"],
            "vergessen": ["vergessen", "vergesslichkeit"],
            # AUDIT 8 — L'APRÈS-COUP (51 occ.). Concept majeur : un événement ne prend son sens
            # traumatique que rétroactivement. Toute une lecture de Freud (Lacan, Laplanche) part
            # de là, et le mot n'avait aucune case.
            "nachtraeglichkeit": ["nachtraglich", "nachtraglichkeit"],
            "deckerinnerung": ["deckerinnerung"],
            "spur": ["erinnerungsspur", "gedachtnisspur"],
            # LE NOM PROPRE — matière privilégiée de l'oubli chez Freud : « Zur Psychopathologie
            # des Alltagslebens » s'ouvre sur « Das Vergessen von Eigennamen ». Le concept
            # « namenvergessen » ne captait que le mot composé (19 occurrences) ; le nom
            # lui-même, 459 fois dans le corpus, n'existait pas dans l'ontologie.
            # Borné : « namentlich » (à savoir) n'est pas un nom propre.
            "name": [r"namen?s?\b", r"eigennamen?\b", r"vornamen?\b"],
        },
    },
    "pulsion": {
        "label": "Pulsion, libido, sexualité",
        "termes": {
            # « trieb » nu ne voit pas les composés : l'allemand soude (Sexual-trieb, Todes-trieb),
            # et la frontière de mot est en tête. Sans les composés attestés, les sous-concepts de
            # « trieb » ne se déclenchaient jamais. On les énumère plutôt que d'employer un joker
            # (`\w*trieb` attraperait « Betrieb », « getrieben ») — même prudence que Traum/Trauma.
            "trieb": ["trieb",
                      r"(?:sexual|todes|ich|partial|lebens|schau|selbsterhaltungs|destruktions|"
                      r"aggressions|eros)trieb"],
            "libido": ["libido"],
            "sexualitaet": ["sexualitat", "sexuell", "sexuelle", "sexualtrieb"],
            # (?!ig) écarte « lustig » (amusant), qui n'a rien à voir avec le plaisir freudien.
            "lustprinzip": ["lustprinzip", r"lust(?!ig)"],
            # Le PRINCIPE de réalité figurait au lexique, mais pas la réalité elle-même :
            # 159 « Realität » et 649 « wirklich » passaient au travers.
            # MOTIF MORT CORRIGÉ (2026-08-01) — `"real\b"` était écrit en chaîne NON BRUTE, donc
            # Python y lisait « real » + un caractère BACKSPACE (0x08), pas une frontière de mot.
            # Aucun texte allemand ne contient ce caractère : le motif ne pouvait rien capter, et
            # « real » employé seul — 49 atomes — passait au travers. La faute est invisible à la
            # lecture du fichier, la chaîne paraissant correcte. Voir `bin/verifier_motifs.py`.
            "realitaet": ["realitat", r"real\b", "reale", "wirklichkeit", "wirklich"],
            "realitaetsprinzip": ["realitatsprinzip"],
            "todestrieb": ["todestrieb"],
            "wiederholungszwang": ["wiederholungszwang"],
            "narzissmus": ["narzissmus", "narzisstisch"],
            # Les « aberrations sexuelles » sont le premier des Trois essais : 219 occurrences
            # d'inversion et de perversion étaient hors ontologie.
            "inversion": ["inversion", "invertiert", "invertierte"],
            "perversion": ["perversion", "pervers"],
            "sadismus": ["sadismus", "sadist"],
            "masochismus": ["masochis"],
            "autoerotismus": ["autoerot"],
            # AUDIT 8 (2026-07-28) — L'OBJET, absent après SEPT audits successifs, alors qu'il
            # est l'un des concepts les plus lourds de la psychanalyse : 596 occurrences, dont
            # 92 « Sexualobjekt » et 52 « Objektwahl ». C'est de lui que sortira toute la théorie
            # des relations d'objet, chez Abraham puis chez Klein.
            # Comment il a échappé si longtemps : aucun audit ne l'a cherché, parce que le mot
            # « Objekt » ne SONNE pas comme un terme technique — il ressemble à un mot ordinaire.
            # Les sept audits précédents balayaient le vocabulaire des atomes NON QUALIFIÉS, et
            # « Objekt » apparaît presque toujours dans des phrases par ailleurs qualifiées : il
            # était donc invisible à cette méthode. Leçon : le scan des non-qualifiés trouve les
            # DOMAINES absents, pas les concepts isolés noyés dans du texte déjà reconnu.
            "objekt": ["objekt", "sexualobjekt", "liebesobjekt", "objektwahl", "objektbeziehung",
                       "objektliebe", "objektverlust"],
            "erogene_zone": ["erogen"],
            # L'agression — « Zorn » est LE sujet du « Moses des Michelangelo » (la colère que la
            # statue retient), « Wut » sa variante ; « aggress » couvre Aggression, aggressiv et
            # le composé Aggressionstrieb déjà énuméré sous « trieb ».
            "aggression": ["aggress", "zorn", "wut"],
            # LA DIFFÉRENCE DES SEXES — audit 4 (2026-07). Le plus gros manque du corpus :
            # 526 occurrences dans 17 œuvres, et une conférence entière des « Neue Folge »
            # s'intitule « Die Weiblichkeit ». Rien n'en était capté.
            # « weib » couvre Weib/Weibes/Weibe (la femme, forme d'époque) ET weiblich/
            # Weiblichkeit — aucun mot allemand ne commence par « weib » sans parler de la femme.
            "weiblichkeit": ["weib"],
            # « mannlich » et NON « mann » nu : ce dernier ramasserait « der Mann » (l'homme, la
            # personne) partout, alors que le concept est la masculinité COMME QUALITÉ, celle que
            # Freud oppose à la féminité. Même prudence que « ich » réservé au moi.
            "maennlichkeit": ["mannlich"],
        },
    },
    # NOUVEAU GROUPE (audit 5) — LE CORPS ET SES EXPRESSIONS. « koerper » ne connaissait que
    # l'abstrait (somatisch, leiblich) et vivait dans « pulsion ». Or trois œuvres du corpus
    # sont des analyses de corps CONCRETS, et leur vocabulaire restait invisible : la main, la
    # barbe et les Tables du *Moses des Michelangelo* (43 % de non-qualifiés, le pire du
    # corpus), les yeux de *Das Unheimliche* — l'homme au sable arrache les yeux, que Freud
    # lit comme équivalent de la castration —, le sourire de *Monna Lisa* dans le *Leonardo*.
    # Le corps n'est pas une pulsion : il méritait son groupe.
    "corps": {
        "label": "Corps, organes, expression",
        "termes": {
            "koerper": ["korper", "somatisch", "organisch", "leiblich"],
            # LA DOULEUR (409 occ.) — le symptôme hystérique par excellence : les douleurs de
            # jambe d'Elisabeth v. R. occupent tout un cas des « Studien über Hysterie ».
            "schmerz": ["schmerz"],
            # Les symptômes de conversion, dans la graphie médicale de 1895 (« Contractur »,
            # avec c). Le corps qui parle à la place du souvenir.
            "laehmung": ["lahmung", r"[ck]ontra[ck]tur", "anasthesie", "anaesthesie"],
            # Exclut « Augenblick » (l'instant, 41 occ.) et « augenfällig » (manifeste, 20) ;
            # garde les composés bien oculaires, dont « Augenangst » — l'angoisse pour ses yeux,
            # que Freud lit dans « Das Unheimliche » comme équivalent de l'angoisse de castration.
            "auge": [r"auge(?!nblick|nfallig|nschein)"],
            # Borné : « handeln », « Handlung », « behandeln » pèsent 300+ occurrences et ne
            # parlent pas de la main. Le motif nu aurait triplé le concept avec du bruit.
            "hand": [r"hand(?:e|en|es)?\b"],
            "kopf": ["kopf"],
            "bart": ["bart"],
            # (?!lich) écarte « mündlich » (verbal, oral au sens de « parlé ») ; les composés
            # gardés sont bien corporels, dont « Mundzone » — la zone érogène orale des
            # « Drei Abhandlungen ».
            "mund": [r"mund(?!lich)"],
            # (?!spunkt) écarte « Gesichtspunkt » (le point de vue, 71 occ. sur 166).
            "gesicht": [r"gesicht(?!spunkt)"],
            # Le sourire, distinct du rire (« lachen », groupe comique) : Freud l'analyse comme
            # mimique — celle de Monna Lisa (37 occ. sur 49) comme celle du mot d'esprit.
            "lacheln": ["lachel"],
        },
    },
    # NOUVEAU GROUPE (audit 6) — LA CONSCIENCE MORALE. Registre entier absent de l'ontologie,
    # découvert en atomisant « Einige Charaktertypen aus der psychoanalytischen Arbeit » (1916),
    # dont la troisième partie s'intitule « Verbrecher aus Schuldbewußtsein ». L'omission était
    # de taille : Freud définit le Sur-Moi comme l'héritier de la conscience morale, et fait de
    # la culpabilité le ressort du totémisme comme de la névrose obsessionnelle.
    "morale": {
        "label": "Conscience morale, culpabilité, punition",
        "termes": {
            "schuld": ["schuld"],
            # PIÈGE MAJEUR : « gewissen » est aussi l'adjectif « gewiß » (certain) décliné —
            # « einer gewissen Regel » compte à lui seul 108 occurrences, contre ~65 pour le
            # substantif. Le repliement supprimant la majuscule qui les sépare en allemand, on
            # ne retient que les formes SÛRES : le génitif et les composés (Gewissensangst,
            # Gewissensvorwürfe), l'adjectif dérivé, et le substantif précédé d'un déterminant
            # neutre — jamais « einer/einen/einem gewissen », qui ne peut pas être le nom.
            # Mieux vaut manquer que sur-détecter, comme pour « ich » et « es ».
            "gewissen": [r"gewissens\w*", r"gewissenhaft",
                         r"(?<=das )gewissen\b", r"(?<=dem )gewissen\b",
                         r"(?<=sein )gewissen\b", r"(?<=ihr )gewissen\b",
                         r"(?<=mein )gewissen\b", r"(?<=kein )gewissen\b"],
            "strafe": ["straf"],
            "moral": ["moral"],
            "verbrechen": ["verbrech"],
            "reue": ["reue"],
        },
    },
    "conflit": {
        "label": "Conflit, défense, symptôme",
        "termes": {
            "verdraengung": ["verdrangung", "verdrangt", "verdrangen"],
            "widerstand": ["widerstand", "widerstande"],
            # LA CONVERSION (78 occ.) — le mécanisme même de l'hystérie selon Freud : la somme
            # d'excitation inconciliable est transposée dans le corporel. Graphie latine
            # « Conversion » dans tout le corpus.
            "conversion": ["conversion", "konversion"],
            # L'INHIBITION (144 occ.) — assez centrale pour donner son titre à « Hemmung,
            # Symptom und Angst » (1926), œuvre que le corpus ne peut pas encore atteindre.
            "hemmung": ["hemmung"],
            "anfall": ["anfall"],
            # LA CONTRAINTE, au-delà de la seule névrose obsessionnelle : Zwangsvorstellung,
            # Zwangshandlung, Wiederholungszwang. Recoupe « zwangsneurose », plus spécifique —
            # recoupement voulu, comme « trieb » et « todestrieb ».
            "zwang": ["zwang"],
            # L'ÉTAT HYPNOÏDE (64 occ.) — thèse de BREUER, que Freud abandonnera. Le concept
            # existe pour rendre ce désaccord MESURABLE : sans lui, la théorie que Freud rejette
            # resterait invisible dans un corpus qui contient pourtant le texte où elle est
            # défendue (« Studien über Hysterie », chapitre III, signé Breuer).
            "hypnoid": ["hypnoid"],
            "symptom": ["symptom", "symptome"],
            # « neurotiker » (le névrosé, 95 occ.) et « nervös » (40) manquaient depuis
            # l'origine — la maladie était captée, jamais le malade. Défaut révélé par un test
            # de l'audit 6, pas par une relecture du lexique : une phrase d'exemple attendait
            # « neurose » sur « quält den Neurotiker » et ne l'a pas trouvé.
            "neurose": ["neurose", "neurotisch", "neurotik", "nervos",
                        "hysterie", "hysterisch", "zwangsneurose"],
            # Les COMPOSÉS en -angst sont ÉNUMÉRÉS, jamais pris par un joker : « längst »
            # (depuis longtemps, 79 occ.) et « unlängst » (récemment, 16) finissent eux aussi
            # par « angst » et n'ont rien d'anxieux. Défaut décelé par un test de l'audit 6 —
            # « Gewissensangst » n'était pas reconnu comme de l'angoisse. Même correctif que
            # pour « trieb » et « besetzung » : la frontière de mot exclut tout composé, donc
            # on relève ceux qui existent réellement dans le texte.
            "angst": ["angst", "angstlich",
                      r"(?:real|kastrations|kinder|gewissens|augen|traum|beruhrungs|todes|"
                      r"versuchungs|platz|massen|neurosen)angst"],
            "abwehr": ["abwehr"],
            "konflikt": ["konflikt"],
            # LES DEUX GRANDES NÉVROSES, distinguées — audit 4 (2026-07). « neurose » les captait
            # déjà toutes deux (voir son motif) mais les confondait : impossible de demander ce que
            # Freud dit de l'hystérie SANS l'obsession, alors que leur distinction est fondatrice.
            # Elles restent AUSSI sous « neurose » — l'hystérie EST une névrose, le multigroupe
            # est fait pour ça.
            "hysterie": ["hysteri"],
            # « zwangs- » et non « zwang » nu : le second ramasserait la contrainte au sens
            # ordinaire (66 occ.), et surtout il chevaucherait « wiederholungszwang », concept
            # distinct du groupe pulsion. Les composés cliniques suffisent et sont sans ambiguïté :
            # Zwangsneurose, Zwangsvorstellung, Zwangshandlung, Zwangskranke, Zwangsverbot.
            "zwangsneurose": ["zwangs"],
            # LES DÉFENSES AUTRES QUE LE REFOULEMENT — audit 4. Le groupe ne connaissait que
            # « abwehr » (générique) et « verdrangung » : sublimation, projection et déni étaient
            # hors ontologie, alors que la sublimation est ce par quoi Freud explique la culture
            # et l'œuvre d'art (Leonardo), et la projection ce par quoi il explique la paranoïa
            # et l'animisme (Totem und Tabu).
            "sublimierung": ["sublimier"],
            "projektion": ["projektion", "projizier"],
            "verleugnung": ["verleugn"],
            "reaktionsbildung": ["reaktionsbildung"],
            "introjektion": ["introjekt"],
            "isolierung": ["isolierung"],
            "wahn": ["wahn", "wahnsinn", "paranoi"],
            # L'HALLUCINATION manquait entièrement à l'ontologie (67 occurrences) — alors que la
            # « halluzinatorische Wunscherfüllung » du nourrisson est le modèle même du rêve au
            # chapitre VII de la Traumdeutung.
            "halluzination": ["halluzin"],
            # Concept À PART ENTIÈRE, et non un parasite du rêve (voir la note sur « traum ») :
            # la névrose traumatique et la névrose de guerre sont le point d'appui empirique de
            # « Jenseits des Lustprinzips » pour poser la compulsion de répétition.
            # Motif STRICTEMENT symétrique de celui de « traum » : seuls Trauma/Traumas et les
            # dérivés attestés comptent — surtout pas « Traumarbeit » ni « Traumanalyse », qui
            # sont des composés du rêve (l'erreur inverse, mesurée à 163 faux positifs sur 165).
            "trauma": [r"trauma(?:s?\b|ti(?:sch|sier)|tolog)"],
        },
    },
    "desir": {
        "label": "Désir et accomplissement",
        "termes": {
            "wunsch": ["wunsch", "wunsche", "wunsches", "wunschen"],
            "wunscherfuellung": ["wunscherfullung"],
            "regression": ["regression", "regressiv"],
            "fixierung": ["fixierung", "fixiert"],
        },
    },
    "developpement": {
        "label": "Développement et enfance",
        "termes": {
            "infantil": ["infantil", "infantile", "kindheit", "kindlich", "kind"],
            "oedipus": ["oedipus", "odipus"],
            "elternkomplex": ["elternkomplex", "komplex"],
            "latenzzeit": ["latenzzeit", "latenzperiode"],
            "pubertaet": ["pubertat"],
            "entwicklung": ["entwicklung", "entwicklungsstufe"],
            # LE CARACTÈRE, restreint à ses composés UNIVOQUES. « Charakter » nu est ambigu en
            # allemand — le caractère d'une personne, mais aussi la nature d'une chose : « die
            # Charaktere des Traumlebens » (les propriétés de la vie onirique) n'a rien de
            # caractérologique. Sur 513 occurrences du radical, la part psychanalytique n'est
            # pas séparable mécaniquement ; on ne prend donc que les 35 composés qui ne peuvent
            # rien désigner d'autre. Concept volontairement étroit et exact plutôt que large et
            # faux — même arbitrage que pour « gewissen ».
            "charakter": [r"charakter(?:zug|bildung|typ|analyse|eigenschaft|entwicklung|anlage)"],
            # LE COMPLEXE DE CASTRATION — audit 4 (2026-07). Pièce centrale de la théorie du
            # développement, articulée à l'Œdipe, et totalement absente de l'ontologie : 116
            # occurrences dans 7 œuvres. « phallisch » y est joint parce que c'est le nom du
            # stade que ce complexe conclut.
            # AUDIT 8 — 508 occurrences. Le lexique portait « männlich »/« weiblich » (l'attribut)
            # mais pas l'enfant SEXUÉ, alors que toute la théorie du développement repose sur la
            # différence des trajets du garçon et de la fille.
            # DEUX MOTIFS MORTS CORRIGÉS (2026-08-01), ET C'EST LE SOUS-CONCEPT QUI POUVAIT LE MOINS
            # SE LE PERMETTRE : il porte la différence des sexes, ajoutée à l'audit 8 comme « le plus
            # gros manque du corpus ». « bube\b » et « junge\b » étaient écrits en chaîne NON BRUTE :
            # Python y lisait « bube » et « junge » suivis d'un caractère BACKSPACE (0x08), jamais
            # d'une frontière de mot. Les deux mots allemands courants pour « garçon », après Knabe,
            # ne pouvaient donc rien capter — 116 atomes de « Junge » perdus.
            # `bube` est RETIRÉ, mais après mesure et non par principe : une fois le motif réparé,
            # il rend ZÉRO atome — le mot est absent du corpus allemand de Freud. Le fait est écrit
            # ici pour qu'on ne le repropose pas.
            "knabe_maedchen": ["knabe", "knaben", "madchen", r"junge\b"],
            "kastration": ["kastration", "penisneid", "phallisch", "phallus"],
        },
    },
    # NOUVEAU GROUPE — les FIGURES du roman familial. « oedipus » ne captait que le mot (3 atomes) ;
    # la substance du complexe est ailleurs : 232 « Vater », 163 « Mutter », 147 frères et sœurs.
    # Groupe distinct à dessein : c'est sur lui que se recomposeront les courants postérieurs
    # (relations d'objet chez Klein, fonction paternelle chez Lacan) — l'objectif à terme du projet.
    "famille": {
        "label": "Figures familiales et roman familial",
        "termes": {
            # (?!land|stadt) écarte « Vaterland » / « Vaterstadt », qui ne sont pas le père.
            "vater": [r"vater(?!land|stadt)", "vaterlich"],
            "mutter": [r"mutter(?!mal)", "mutterlich"],
            "eltern": ["eltern"],
            "geschwister": ["geschwister", "bruder", "schwester"],
            "familie": ["familie", "familiar"],
        },
    },
    # ----------------------------------------------------------------------------------------
    # GROUPES OUVERTS PAR L'EXTENSION DU CORPUS (2e vague : 7 œuvres ajoutées, 1901-1921).
    # Freud ne parle pas que de rêve et de sexualité : il écrit aussi sur la société primitive,
    # le mot d'esprit, la foule, l'art. Sans ces groupes, « Das Unheimliche » n'était qualifié
    # qu'à 39 %, « Totem und Tabu » à 50 % — non parce que ces textes seraient hors psychanalyse,
    # mais parce que l'ontologie était taillée sur trois livres seulement.
    # ----------------------------------------------------------------------------------------
    "anthropologie": {
        "label": "Anthropologie : totémisme, tabou, sacrifice",
        "termes": {
            "totem": ["totem"],
            "tabu": ["tabu"],
            "exogamie": ["exogamie", "inzest"],
            "opfer": ["opfer"],
            # « verbiet » couvre les formes conjuguées (verbietet, verbieten) — trou décelé par
            # les tests de l'audit 2026-07, pas par intuition.
            "verbot": ["verbot", "verboten", "verbiet"],
            # AUDIT 8 — « Allmacht der Gedanken » (42 occ.), que Freud pose dans Totem und Tabu
            # comme le ressort commun de la magie, de l'animisme et de la névrose obsessionnelle.
            "allmacht": ["allmacht", "allmachtig"],
            "animismus": ["animismus", "animistisch", "magie", "zauber"],
            "urhorde": ["urhorde", "urvater", "urzeit"],
            "primitiv": ["primitiv", "wilde", "wilden", "volker", "urmensch"],
            "beruehrung": ["beruhrung", "beruhrungsangst"],
            # RELIGION — « Totem und Tabu » fonde la religion sur le père, la « Teufelsneurose »
            # lit le Diable en substitut paternel, les essais de guerre parlent de l'au-delà.
            # Ce vocabulaire restait entièrement hors ontologie.
            "religion": ["religio"],
            # (?!ing) écarte « Göttingen » — la ville universitaire, pas le divin.
            "gott": [r"gott(?!ing)"],
            # « teufl » attrape « teuflisch » — le e du radical tombe dans l'adjectif.
            "teufel": ["teufel", "teufl"],
            # LE PACTE avec le diable — l'engagement ÉCRIT et signé du sang, sujet même de la
            # « Teufelsneurose » (52 occurrences de « Verschreibung », toutes dans cette œuvre).
            # À NE PAS CONFONDRE avec « verschreiben » (le lapsus calami, groupe acte_manque) :
            # le motif « verschreiben » ne capte pas « Verschreibung », les deux cohabitent sans
            # se recouvrir. Concept mono-œuvre à ce jour — le signaler plutôt que le taire ; il
            # se peuplera si d'autres textes de démonologie rejoignent le corpus.
            "pakt": ["verschreibung", "pakt", "teufelspakt", "teufelsverschreibung"],
        },
    },
    "comique": {
        "label": "Mot d'esprit, comique, rire",
        "termes": {
            "witz": ["witz"],
            "komik": ["komik", "komisch"],
            "lachen": ["lachen", "lacherlich"],
            "anspielung": ["anspielung", "wortspiel", "doppelsinn"],
            "tendenz": ["tendenzios"],
        },
    },
    "social": {
        "label": "Masse, lien social, autorité",
        "termes": {
            # « § » = ce terme se juge sur le texte où le ß est CONSERVÉ. Sans cela, « in hohem
            # Maße » (mesure) se repliait en « masse » et rejoignait la psychologie des foules.
            "masse": ["§masse", "§massen"],
            "fuehrer": ["fuhrer"],
            "suggestion": ["suggestion", "suggestiv"],
            "identifizierung": ["identifizierung", "identifiziert"],
            "panik": ["panik"],
            "institution": ["kirche", "heer", "armee"],
            # CULTURE, GUERRE, ÉTAT — le vocabulaire des essais de 1915-1916 (« Zeitgemäßes über
            # Krieg und Tod », « Vergänglichkeit ») était invisible : 44 % de non-qualifiés.
            "kultur": ["kultur"],
            # « kriegen » = « recevoir » (familier, présent dans les Witze cités) : on ne prend
            # que les formes nominales, les composés en kriegs- et « Krieger » — jamais le verbe.
            "krieg": [r"krieg(?:e?s|e)?\b", r"kriegs[a-z]", "krieger"],
            "staat": ["staat"],
            # « gesellschaft » couvre aussi vergesellschaftet/Gesellschaftsordnung.
            "gesellschaft": ["gesellschaft", "vergesellschaft"],
            # LA CONTROVERSE LE BON / FREUD, mesurable des deux côtés. Freud consacre un chapitre
            # entier de « Massenpsychologie und Ich-Analyse » (1921) à discuter Le Bon (1895) ; les
            # trois mécanismes que Le Bon donne à la foule ont chacun leur trace dans les deux
            # langues, comptée sur les corpus réels : Ansteckung (11 occ. chez Freud) / contagion,
            # Prestige (8 occ. — Freud garde le mot français tel quel) / prestige, Nachahmung
            # (4 occ.) / imitation. Les motifs français sont dans MOTIFS_FR.
            "ansteckung": ["ansteckung"],
            "prestige": ["prestige"],
            "nachahmung": ["nachahmung"],
        },
    },
    # NOUVEAU GROUPE — mort, deuil, perte. Les essais de guerre (1915-1916) et la Teufelsneurose
    # (la mélancolie du peintre après la mort de son père) parlaient dans le vide : « Trauer »,
    # « Tod », « Vergänglichkeit » n'existaient nulle part dans l'ontologie — alors que « Trauer
    # und Melancholie » est un pivot de l'œuvre, que Freud cite lui-même (voir la vérification
    # des auto-citations : « Der Schatten des Objekts ist auf das Ich gefallen »).
    "mort": {
        "label": "Mort, deuil, perte",
        "termes": {
            # \btod couvre Tod/Todes- et recoupe « todestrieb » (groupe pulsion) : un énoncé sur
            # la pulsion de mort parle AUSSI de la mort — recoupement voulu, pas un accident.
            "tod": ["tod"],
            "sterben": ["sterb", "stirb", "gestorben", "unsterblich"],
            "trauer": ["trauer"],
            "melancholie": ["melanchol"],
            "verganglichkeit": ["verganglich"],
        },
    },
    "esthetique": {
        "label": "Art, fiction, inquiétante étrangeté",
        "termes": {
            "unheimlich": ["unheimlich"],
            # « Dichter » (le poète, l'écrivain) — Freud dialogue constamment avec la littérature.
            # Homographe du comparatif « dichter » (plus dense), très rare ici : écart assumé.
            "dichter": ["dichter", "dichtung", "poet"],
            "phantasie": ["phantasie", "phantasier"],
            # « kunstwerk » seul manquait 128 « Künstler » ; mais PAS de \bkunst nu, qui prendrait
            # « künstlich » (artificiel, 24 occurrences — les « foules artificielles » de la
            # Massenpsychologie n'ont rien d'esthétique).
            "kunst": ["kunstwerk", "asthetik", "asthetisch", "kunstler", r"kunst\b", r"kunste\b"],
            # PEINTURE ET SCULPTURE — le Léonard (44 % de non-qualifiés) et le Moses (61 %) sont
            # des analyses d'œuvres VISUELLES ; le lexique ne connaissait que la littérature.
            # « gemal » couvre gemalt/Gemälde — et ne peut pas attraper « Gemahl » (époux),
            # qui s'écrit avec un h.
            "malerei": ["maler", "gemal", "bildnis"],
            # « statuen?\b » exact — « statue » nu attrapait « statuerunt » dans une citation latine.
            "statue": [r"statuen?\b", "bildhauer", "plastik", "skulptur", "standbild"],
            # « schonheit » est sans risque ; « schön » nu se replierait en « schon » (déjà).
            "schoenheit": ["schonheit"],
            "erzaehlung": ["erzahlung", "roman", "novelle"],
        },
    },
    "acte_manque": {
        "label": "Actes manqués et psychopathologie du quotidien",
        "termes": {
            "fehlleistung": ["fehlleistung", "fehlhandlung"],
            # « Versprechen » est ambigu en allemand (promesse / lapsus) ; dans ce corpus, c'est
            # le lapsus qui domine — le livre entier porte sur « Vergessen, Versprechen,
            # Vergreifen ». Ambiguïté connue et acceptée, signalée ici plutôt que masquée.
            "versprechen": ["versprechen", "verlesen", "verschreiben"],
            "vergreifen": ["vergreifen", "vergriff"],
            # `namensvergessen` (avec le -s- de liaison) fait 0 atome : Freud écrit
            # « Namenvergessen ». Retiré après mesure, comme `bube` plus haut.
            "namenvergessen": ["namenvergessen"],
            # LE TRÉMA, ENCORE. `abergläubisch` ne peut PAS se déclencher : le lexique s'applique
            # après un repli qui SUPPRIME les diacritiques. La faute est documentée trois fois dans
            # le lexique de Stekel (angstgefühl, nervosität, schuldgefühl) et elle était ici aussi,
            # à côté de la forme repliée correcte qui la rendait inoffensive — d'où sa survie.
            "aberglaube": ["aberglaube", "aberglaubisch"],
        },
    },
    "cure": {
        "label": "Cure et relation analytique",
        "termes": {
            "uebertragung": ["ubertragung"],
            "psychoanalyse": ["psychoanalyse", "psychoanalytisch"],
            "patient": ["patient", "patientin", "kranke", "kranken"],
            "assoziation": ["assoziation", "einfall", "einfalle"],
            # LE VOCABULAIRE ORDINAIRE DE LA CURE — audit 4 (2026-07). Le groupe connaissait le
            # transfert et l'association libre, mais pas le traitement lui-même ni le médecin :
            # 417 occurrences dans 18 œuvres passaient à travers.
            "behandlung": ["behandlung", "therapie", "therapeut", "heilung"],
            "arzt": ["arzt"],
            # « deutung » NU, et c'est un piège majeur : sans la frontière de mot (posée
            # automatiquement devant chaque motif), il ramasserait « BEdeutung » (signification,
            # 375 occ.) — un tout autre mot. La frontière écarte aussi « TRAUMdeutung », qui a
            # son propre concept dans le groupe « reve ». Restent 323 occurrences de
            # l'interprétation COMME ACTE, cœur de la méthode.
            "deutung": ["deutung"],
            # L'HYPNOSE ET LA CATHARSIS — la technique que Freud a pratiquée puis abandonnée.
            # Absente de l'ontologie alors qu'elle est le repoussoir constant de la méthode
            # analytique, et l'objet d'un chapitre entier de « Massenpsychologie ».
            "hypnose": ["hypnos", "hypnot", "kathar"],
        },
    },
    # NOUVEAU GROUPE — LE DISCOURS DE LA SCIENCE. Ce n'est pas de la théorie psychanalytique
    # mais le MÉTA-DISCOURS de Freud sur son propre travail : est-ce une science, qu'est-ce qui
    # y fait preuve, qu'est-ce qui s'y observe. 847 occurrences dans la quasi-totalité des
    # œuvres, entièrement hors ontologie jusqu'ici — et c'est précisément la matière qui
    # intéresse un projet dont l'objet est la rigueur épistémique.
    # Le groupe est nommé et étiqueté pour qu'on ne le confonde jamais avec un concept freudien :
    # taguer « Beobachtung » dit que l'atome PARLE d'observation, pas que Freud observe.
    "episteme": {
        "label": "Discours de la science : statut, méthode, preuve",
        "termes": {
            "wissenschaft": ["wissenschaft"],
            "forschung": ["forschung", "erforsch"],
            "beobachtung": ["beobachtung", "beobachtet"],
            # La frontière de mot écarte « SexualTHEORIE », « LibidoTHEORIE », « TraumTHEORIE » :
            # ces composés parlent d'une théorie PARTICULIÈRE, pas du fait d'en avoir une.
            "theorie": ["theorie"],
        },
    },
}

# --------------------------------------------------------------------------- 3bis. SOUS-CONCEPTS
# TROISIÈME NIVEAU (groupe → concept → sous-concept), posé UNIQUEMENT là où le texte fait une
# distinction réelle et mesurable. Sans lui, tous les atomes de « trieb » tombaient dans le même
# tiroir, que Freud parle de pulsion sexuelle (98 occurrences) ou de pulsion de mort (20) — deux
# thèses que 15 ans et un revirement théorique séparent. C'est exactement la finesse qui manquait.
#
# Le sous-concept est ADDITIF : l'atome garde son concept parent (on ne perd jamais la vue large),
# et gagne une précision quand le texte la donne. Aucun sous-concept n'est deviné : chacun a été
# compté dans le corpus avant d'être inscrit (effectif entre parenthèses).
SOUS_CONCEPTS = {
    "trieb": {
        "sexualtrieb": (["sexualtrieb"], 98),
        "todestrieb": (["todestrieb", "destruktionstrieb"], 20),
        "partialtrieb": (["partialtrieb"], 19),
        "ichtrieb": (["ichtrieb"], 13),
        "lebenstrieb": (["lebenstrieb", "erostrieb"], 11),
        "schautrieb": (["schautrieb"], 2),
    },
    "traum": {
        "angsttraum": (["angsttraum"], 38),
        "typischer_traum": ([r"typische[nr]? traum"], 22),
        "kindertraum": (["kindertraum"], 6),
    },
    "sexualitaet": {
        "inversion": (["inversion", "invertiert"], 104),
        "perversion": (["perversion", "pervers"], 115),
        "erogene_zone": (["erogen"], 78),
        "sadismus": (["sadismus", "sadist"], 31),
        "masochismus": (["masochis"], 24),
        "autoerotismus": (["autoerot"], 12),
    },
    "angst": {
        "angsttraum": (["angsttraum"], 38),
        "angstneurose": (["angstneurose"], 2),
    },
    "erinnerung": {
        "deckerinnerung": (["deckerinnerung"], 6),
        "kindheitserinnerung": (["kindheitserinnerung"], None),
    },
}

# « Ich » (le Moi) est le piège classique : en allemand c'est aussi le pronom « je », omniprésent
# chez Freud qui écrit à la première personne. On ne le capte donc QUE sous forme composée
# (« Ich-Ideal », « Ichs », « das Ich » suivi d'un verbe) — mieux vaut manquer une occurrence que
# taguer « topique » sur chaque phrase où Freud dit « je ». Rappel de la règle AXA : jamais de
# faux positif silencieux sur une donnée qui sera présentée comme un fait.
_RE_ICH_MOI = re.compile(r"\bdas ich\b|\bich-ideal\b|\bichs\b|\bdes ichs\b")


# ------------------------------------------------------------------ 3 bis. MOTIFS FRANÇAIS
# Les identifiants de concepts sont NEUTRES (hérités de l'allemand par histoire du projet) ; cette
# table donne leurs motifs français. Un concept absent d'ici n'est pas mesuré dans un texte
# français — il reste visible comme non-qualifié plutôt que d'être approximé. Chaque entrée est
# une décision de traduction assumée, pas un réflexe de dictionnaire : les correspondances
# douteuses sont REFUSÉES (voir les refus en fin de table, aussi importants que les entrées).
MOTIFS_FR = {
    # -- social : le cœur de Le Bon, et de la controverse avec Freud (1921).
    "masse": [r"\bfoules?\b"],
    "fuehrer": [r"\bmeneurs?\b"],
    "suggestion": ["suggestion", "suggestib", "suggestionn"],
    "ansteckung": ["contagion", "contagieu"],
    "prestige": ["prestige"],
    "nachahmung": ["imitation", "imitateur", r"\bimitent\b", r"\bimiter\b"],
    "panik": ["panique"],
    "kultur": ["civilisation"],
    "krieg": [r"\bguerres?\b"],
    "gesellschaft": [r"\bsocietes?\b"],
    "institution": ["institution"],
    # -- topique : Le Bon parle d'« inconscient » dès 1895 — vingt-cinq ans avant la métapsychologie.
    "unbewusst": ["inconscien"],
    # « conscien » nu prendrait AUSSI « inconscient » : l'exclusion sépare les deux concepts.
    "bewusstsein": [r"(?<!in)conscien"],
    # « l'âme des foules » : LE terme psychologique de Le Bon, qu'il pose lui-même en équivalent
    # de « psychologie » dans son introduction. Rattaché au psychisme, pas à la religion.
    "psychisme": [r"\bames?\b"],
    "phantasie": ["imagination"],
    # -- autres groupes touchés par le texte de 1895.
    "hypnose": ["hypnos", "hypnoti"],
    "erinnerung": [r"\bsouvenirs?\b"],
    "religion": ["religion", "religieu"],
    "gott": [r"\bdieux?\b"],
    "moral": [r"\bmoral(?:e|es|ite)?\b"],
    "verbrechen": [r"\bcrimes?\b", "criminel"],
    "wissenschaft": ["scientifique", r"\bsciences?\b"],
    "beobachtung": ["observation"],
    "theorie": ["theori"],
    # REFUS documentés — correspondances écartées après examen :
    #   • « instinct » ≠ trieb : la distinction Trieb/Instinkt est un débat de traduction célèbre ;
    #     l'« instinct des foules » de 1895 n'est pas la pulsion freudienne.
    #   • « état » ≠ staat : replié sans majuscule, « l'État » se confond avec « l'état mental ».
    #   • « rêve » ≠ traum : chez Le Bon le mot est métaphorique (« les rêves de nos pères »),
    #     jamais l'objet théorique de la Traumdeutung.
    #   • « illusion » ≠ wahn : le délire n'est pas l'illusion, et « Les illusions » de Le Bon
    #     (chapitre entier) parlent des croyances collectives, pas de la psychose.
}


# ==================================================================== AIGUILLAGE PAR AUTEUR
# Chaque auteur a SES catégories et se travaille séparément (voir `core/lexiques/__init__.py`
# pour la règle et sa justification). Ce module reste le MOTEUR — segmentation des motifs,
# multigroupe, statut le plus prudent — et ne contient plus qu'un seul jeu de données, celui de
# Freud, laissé ici parce que sept audits l'ont documenté ligne à ligne à cet endroit.
#
# Les fonctions publiques prennent donc `auteur`. Sans argument, c'est Freud : le corpus a
# commencé par lui, et l'immense majorité des appels existants le visent.
_FREUD = "Sigmund Freud"


class _TableFreud:
    """Le lexique freudien, présenté comme un module d'auteur pour que l'aiguillage soit uniforme."""
    LANGUE = "de"
    CONCEPTS = CONCEPTS
    FONCTIONS = FONCTIONS
    NOMS_AUTEURS = NOMS_AUTEURS
    MARQUEURS_STATUT = MARQUEURS_STATUT


def pour_auteur(auteur):
    """Table de l'auteur → module (ou équivalent). Un auteur sans lexique propre suit Freud.

    Ce repli n'est pas une commodité : il concerne les CONTRIBUTIONS insérées dans un volume
    freudien (l'appendice d'Otto Rank dans la Traumdeutung, les cas de Breuer dans les Studien).
    Ces pages appartiennent au livre de Freud, on les décrit avec les catégories de ce livre, et
    l'atome garde son vrai auteur pour qu'on puisse les isoler ensuite. Le jour où Rank est
    traité POUR LUI-MÊME — ce qui est le cas depuis 2026-07 —, ce sont ses cinq œuvres propres
    qui portent son lexique, pas les cent pages qu'il a écrites dans un livre de Freud.
    """
    from . import lexiques
    return lexiques.PAR_AUTEUR.get(auteur, _TableFreud)


_CACHE_TABLES = {}


def _compilee(auteur):
    """Motifs compilés de cet auteur, mémorisés (le corpus les demande une fois par atome)."""
    if auteur not in _CACHE_TABLES:
        t = pour_auteur(auteur)
        _CACHE_TABLES[auteur] = {
            "langue": t.LANGUE,
            "concepts": {(g, c): [re.compile(r"\b" + m) for m in motifs]
                         for g, meta in t.CONCEPTS.items()
                         for c, motifs in meta["termes"].items()},
            "fonctions": {f["id"]: [re.compile(m) for m in f["marqueurs"]] for f in t.FONCTIONS},
            "fiabilite": {f["id"]: f.get("fiabilite", "etablie") for f in t.FONCTIONS},
            "statuts": {k: [re.compile(m) for m in v] for k, v in t.MARQUEURS_STATUT.items()},
            "noms": re.compile(r"\b(" + "|".join(t.NOMS_AUTEURS) + r")\b") if t.NOMS_AUTEURS else None,
        }
    return _CACHE_TABLES[auteur]


def _compile(motifs):
    return [re.compile(m) for m in motifs]


_FONCTIONS_RE = {f["id"]: _compile(f["marqueurs"]) for f in FONCTIONS}
_STATUT_RE = {k: _compile(v) for k, v in MARQUEURS_STATUT.items()}
_AUTEURS_RE = re.compile(r"\b(" + "|".join(NOMS_AUTEURS) + r")\b")

_FONCTIONS_RE_FR = {fid: _compile(m) for fid, m in MARQUEURS_FONCTIONS_FR.items()}
_STATUT_RE_FR = {k: _compile(v) for k, v in MARQUEURS_STATUT_FR.items()}
_AUTEURS_RE_FR = re.compile(r"\b(" + "|".join(NOMS_AUTEURS_FR) + r")\b")
# Même convention que le chemin allemand : chaque motif est ancré sur une frontière de mot.
_MOTIFS_FR_RE = {c: [re.compile(r"\b" + m) for m in mots] for c, mots in MOTIFS_FR.items()}


FIABILITE = {f["id"]: f.get("fiabilite", "etablie") for f in FONCTIONS}


def fonctions_de(texte, auteur=_FREUD):
    """Fonctions argumentatives portées par la phrase (multigroupe, triées, jamais forcées)."""
    t = replier(texte)
    tab = _compilee(auteur)
    trouvees = {fid for fid, res in tab["fonctions"].items() if any(r.search(t) for r in res)}
    # Nommer un auteur que celui-ci discute, c'est rapporter un propos extérieur. La fonction
    # n'est ajoutée que si l'auteur la DÉCLARE : elle n'existe pas dans tous les lexiques.
    if tab["noms"] and "rapport_tiers" in tab["fonctions"] and tab["noms"].search(t):
        trouvees.add("rapport_tiers")
    return sorted(trouvees)


def fonctions_par_fiabilite(texte, auteur=_FREUD):
    """Sépare l'ACQUIS du SIGNALÉ → (fonctions_etablies, signaux_a_confirmer).

    Rien de ce qui n'est pas prouvé ne rejoint les faits : les signaux rares et précieux
    (révision, objection, auto-citation, et chez Rank l'écart déclaré avec Freud) forment une
    liste de travail à vérifier, exactement comme les éléments « à vérifier » de l'audit AXA.
    """
    fiab = _compilee(auteur)["fiabilite"]
    toutes = fonctions_de(texte, auteur)
    etablies = [f for f in toutes if fiab.get(f, "etablie") == "etablie"]
    a_confirmer = [f for f in toutes if fiab.get(f, "etablie") == "a_confirmer"]
    return etablies, a_confirmer


def statut_de(texte, auteur=_FREUD):
    """Statut épistémique — LE PLUS PRUDENT gagne (jamais d'affirmation durcie).

    Les quatre niveaux ne dépendent PAS de l'auteur : c'est une doctrine du projet, pas une
    propriété d'un corpus. Seuls les marqueurs qui les repèrent lui appartiennent.
    """
    t = replier(texte)
    tab = _compilee(auteur)["statuts"]
    for niveau in ("interrogatif", "rapporte", "modalise"):     # du plus prudent au moins
        if any(r.search(t) for r in tab.get(niveau, [])):
            return niveau
    return "affirme"


def concepts_de(texte, auteur=_FREUD):
    """Concepts touchés par la phrase → [{groupe, concept}], multigroupe, déterministe.

    Les concepts cherchés sont CEUX DE L'AUTEUR, jamais ceux d'un autre : c'est la règle
    fondatrice des lexiques séparés (voir `core/lexiques/__init__.py`). Un même nom de concept
    peut exister chez deux auteurs sans désigner la même chose — `geburt` est chez Rank le
    traumatisme d'origine, chez Freud un fait biologique parmi d'autres. Rien ici ne doit
    encourager à les additionner.
    """
    if auteur != _FREUD:
        t = replier(texte)
        return [{"groupe": g, "concept": c}
                for (g, c), res in _compilee(auteur)["concepts"].items()
                if any(r.search(t) for r in res)]
    # Chemin freudien : il porte des particularités qui n'existent que là — le ß conservé pour
    # séparer « Masse » de « Maße », les sous-concepts du 3e niveau, et le cas « Ich » (voir
    # _RE_ICH_MOI). Les mélanger au chemin générique le rendrait illisible pour rien.
    t = replier(texte)
    t_ss = replier_esszett(texte)      # variante où le ß subsiste (voir la convention « § »)
    trouves = []
    for groupe, meta in CONCEPTS.items():
        reserve = meta.get("auteurs")
        if auteur and reserve and auteur not in reserve:
            continue
        for concept, termes in meta["termes"].items():
            if isinstance(termes, dict):          # forme étendue : {motifs, auteurs}
                if auteur and termes.get("auteurs") and auteur not in termes["auteurs"]:
                    continue
                termes = termes["motifs"]
            if concept == "ich" and groupe == "topique":
                if _RE_ICH_MOI.search(t):
                    trouves.append({"groupe": groupe, "concept": "ich"})
                continue
            # Les termes sont des MOTIFS (écrits ici, jamais saisis par un utilisateur) : on ne
            # les échappe pas, ce qui autorise les exclusions fines indispensables — « traum(?!a) »
            # pour ne pas confondre Traum et Trauma, « lust(?!ig) » pour écarter « lustig ».
            # Un terme préfixé de « § » se juge sur le texte à ß CONSERVÉ : c'est le seul moyen de
            # séparer « Masse » (la foule) de « Maße » (les mesures), que le repliement ordinaire
            # rend identiques — une vingtaine de « in hohem Maße » rejoignaient la psychologie des
            # foules. Le préfixe est retiré avant la recherche.
            if any(re.search(r"\b" + (m[1:] if m.startswith("§") else m),
                             t_ss if m.startswith("§") else t) for m in termes):
                entree = {"groupe": groupe, "concept": concept}
                sous = _sous_concepts_de(t, concept)
                if sous:
                    entree["sous_concepts"] = sous
                trouves.append(entree)
    return trouves


def _sous_concepts_de(texte_replie, concept):
    """Précisions du 3e niveau portées par la phrase (additives : le concept parent reste)."""
    table = SOUS_CONCEPTS.get(concept)
    if not table:
        return []
    return sorted(nom for nom, (motifs, _) in table.items()
                  if any(re.search(r"\b" + m, texte_replie) for m in motifs))


def valider():
    """Contrôle d'intégrité du lexique : identifiants uniques, motifs compilables, groupes non vides.

    Appelé par les tests. Une taxonomie incohérente doit échouer BRUYAMMENT, jamais se rattraper
    en silence — c'est elle qui décide de tout le reste.
    """
    erreurs = []
    ids = [f["id"] for f in FONCTIONS]
    if len(ids) != len(set(ids)):
        erreurs.append("identifiants de fonction dupliqués")
    for f in FONCTIONS:
        if not f["marqueurs"]:
            erreurs.append("fonction sans marqueur : %s" % f["id"])
        for m in f["marqueurs"]:
            try:
                re.compile(m)
            except re.error as e:
                erreurs.append("motif invalide (%s) : %s — %s" % (f["id"], m, e))
    vus = set()
    for groupe, meta in CONCEPTS.items():
        if not meta.get("termes"):
            erreurs.append("groupe de concepts vide : %s" % groupe)
        for concept, termes in meta["termes"].items():
            if isinstance(termes, dict) and not termes.get("motifs"):
                erreurs.append("concept en forme étendue sans motifs : %s/%s" % (groupe, concept))
            cle = (groupe, concept)
            if cle in vus:
                erreurs.append("concept dupliqué : %s/%s" % cle)
            vus.add(cle)
    for niveau in MARQUEURS_STATUT:
        if niveau not in STATUTS:
            erreurs.append("statut inconnu dans les marqueurs : %s" % niveau)
    # LEXIQUES DES AUTRES AUTEURS — mêmes exigences, appliquées à chacun séparément. Un lexique
    # d'auteur mal formé doit échouer aussi bruyamment que celui de Freud : c'est lui qui décide
    # de tout ce qu'on lira de cet auteur.
    from . import lexiques
    for nom, module in sorted(lexiques.PAR_AUTEUR.items()):
        if module.LANGUE not in ("de", "fr"):
            erreurs.append("%s : langue inconnue %r" % (nom, module.LANGUE))
        ids = [f["id"] for f in module.FONCTIONS]
        if len(ids) != len(set(ids)):
            erreurs.append("%s : identifiants de fonction dupliqués" % nom)
        vus_c = set()
        for groupe, meta in module.CONCEPTS.items():
            if not meta.get("termes"):
                erreurs.append("%s : groupe vide %s" % (nom, groupe))
            for concept, motifs in meta["termes"].items():
                if concept in vus_c:
                    erreurs.append("%s : concept dupliqué %s" % (nom, concept))
                vus_c.add(concept)
                if not motifs:
                    erreurs.append("%s : concept sans motif %s/%s" % (nom, groupe, concept))
                for m in motifs:
                    try:
                        re.compile(m)
                    except re.error as e:
                        erreurs.append("%s : motif invalide (%s) %s — %s" % (nom, concept, m, e))
        for f in module.FONCTIONS:
            for m in f["marqueurs"]:
                try:
                    re.compile(m)
                except re.error as e:
                    erreurs.append("%s : motif de fonction invalide (%s) %s — %s"
                                   % (nom, f["id"], m, e))
        for niveau in module.MARQUEURS_STATUT:
            if niveau not in STATUTS:
                erreurs.append("%s : statut inconnu %s" % (nom, niveau))
    return {"ok": not erreurs, "erreurs": erreurs,
            "fonctions": len(FONCTIONS), "groupes": len(CONCEPTS),
            "concepts": sum(len(m["termes"]) for m in CONCEPTS.values()),
            "auteurs_avec_lexique_propre": sorted(lexiques.PAR_AUTEUR)}
