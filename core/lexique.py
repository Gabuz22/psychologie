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

LEXIQUE_VERSION = "1.0.0"

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
        "marqueurs": [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bduerfte\b",
                      r"\bscheint\b", r"\bes ist moeglich\b", r"\bich vermute\b", r"\banzunehmen\b",
                      r"\bnehmen wir an\b", r"\bwenn wir annehmen\b"],
    },
    {
        "id": "methode",
        "label": "Énoncé méthodologique",
        "aide": "Description du procédé analytique lui-même (analyse, déchiffrement, technique).",
        "mesure_traumdeutung": 496,
        "marqueurs": [r"\banalyse", r"\bdeutung", r"\bverfahren\b", r"\bmethode\b", r"\btechnik\b",
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
        "marqueurs": [r"\bnach \w+s (ansicht|meinung)\b", r"\bberichtet\b", r"\bzitiert\b",
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

MARQUEURS_STATUT = {
    "modalise":     [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bscheint\b",
                     r"\bduerfte\b", r"\bwohl\b", r"\bmoeglicherweise\b", r"\betwa\b", r"\bkaum\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"\bberichtet\b", r"\berzahlt\b", r"\bnach \w+\b", r"\bzitiert\b",
                     r"\bsoll \w+ haben\b", r"\bangeblich\b"],
}

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
            "ich": ["ich-", "ichs"],          # « Ich » nu est trop ambigu (pronom) — voir note ci-dessous
            # « es » est le pronom « il/cela » en allemand : impossible à capter nu sans tout
            # ramasser. On ne le prend donc qu'après un déterminant, là où il désigne l'instance
            # (« das Es », « vom Es »). Comme pour « Ich », mieux vaut manquer que sur-détecter.
            "es": [r"(?:das|des|dem|vom|im|ins) es\b"],
            # PIÈGE DE TRANSLITTÉRATION, resté invisible jusqu'à l'arrivée des « Neue Folge » :
            # ces termes étaient écrits « ueber-ich », comme si le ü devenait « ue ». Or le
            # repliement SUPPRIME les diacritiques : « Über-Ich » donne « uber-ich ». Résultat,
            # le SURMOI — l'une des trois instances de la seconde topique — n'était détecté nulle
            # part dans le corpus (48 mentions manquées dans les seules Neue Folge).
            # Les deux graphies sont gardées : le corpus mélange « Über-Ich » et « Überich ».
            "ueberich": ["uber-ich", "uberich"],
            # L'« appareil psychique » est le modèle central du chapitre VII — il manquait.
            "apparat": ["apparat", "instanz", "system"],
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
            "besetzung": ["besetzung", "besetzt", "gegenbesetzung"],
            "spannung": ["spannung"],
            "abfuhr": ["abfuhr", "entladung"],
            "energie": ["energie", "quantitat", "intensitat"],
            "reiz": ["reizschutz", "reizmenge"],
        },
    },
    # NOUVEAU GROUPE — mémoire et oubli : 266 « Erinnerung » ignorées, alors que le souvenir
    # d'enfance et le refoulement du souvenir sont la matière première de la méthode.
    "memoire": {
        "label": "Mémoire, souvenir, oubli",
        "termes": {
            "erinnerung": ["erinnerung", "erinnert", "erinnern"],
            "gedaechtnis": ["gedachtnis"],
            "vergessen": ["vergessen", "vergesslichkeit"],
            "deckerinnerung": ["deckerinnerung"],
            "spur": ["erinnerungsspur", "gedachtnisspur"],
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
            "erogene_zone": ["erogen"],
        },
    },
    "conflit": {
        "label": "Conflit, défense, symptôme",
        "termes": {
            "verdraengung": ["verdrangung", "verdrangt", "verdrangen"],
            "widerstand": ["widerstand", "widerstande"],
            "symptom": ["symptom", "symptome"],
            "neurose": ["neurose", "neurotisch", "hysterie", "hysterisch", "zwangsneurose"],
            "angst": ["angst", "angstlich"],
            "abwehr": ["abwehr"],
            "konflikt": ["konflikt"],
            "wahn": ["wahn", "wahnsinn", "paranoi"],
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
            "verbot": ["verbot", "verboten"],
            "animismus": ["animismus", "animistisch", "magie", "zauber"],
            "urhorde": ["urhorde", "urvater", "urzeit"],
            "primitiv": ["primitiv", "wilde", "wilden", "volker"],
            "beruehrung": ["beruhrung", "beruhrungsangst"],
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
            "kunst": ["kunstwerk", "asthetik", "asthetisch"],
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
            "namenvergessen": ["namenvergessen", "namensvergessen"],
            "aberglaube": ["aberglaube", "abergläubisch", "aberglaubisch"],
        },
    },
    "cure": {
        "label": "Cure et relation analytique",
        "termes": {
            "uebertragung": ["ubertragung"],
            "psychoanalyse": ["psychoanalyse", "psychoanalytisch"],
            "patient": ["patient", "patientin", "kranke", "kranken"],
            "assoziation": ["assoziation", "einfall", "einfalle"],
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


def _compile(motifs):
    return [re.compile(m) for m in motifs]


_FONCTIONS_RE = {f["id"]: _compile(f["marqueurs"]) for f in FONCTIONS}
_STATUT_RE = {k: _compile(v) for k, v in MARQUEURS_STATUT.items()}
_AUTEURS_RE = re.compile(r"\b(" + "|".join(NOMS_AUTEURS) + r")\b")


FIABILITE = {f["id"]: f.get("fiabilite", "etablie") for f in FONCTIONS}


def fonctions_de(texte):
    """Fonctions argumentatives portées par la phrase (multigroupe, triées, jamais forcées)."""
    t = replier(texte)
    trouvees = {fid for fid, res in _FONCTIONS_RE.items() if any(r.search(t) for r in res)}
    if _AUTEURS_RE.search(t):
        trouvees.add("rapport_tiers")
    return sorted(trouvees)


def fonctions_par_fiabilite(texte):
    """Sépare l'ACQUIS du SIGNALÉ → (fonctions_etablies, signaux_a_confirmer).

    Rien de ce qui n'est pas prouvé ne rejoint les faits : les signaux rares et précieux
    (révision, objection, auto-citation) forment une liste de travail à vérifier, exactement
    comme les éléments « à vérifier » de l'audit de traçabilité AXA.
    """
    toutes = fonctions_de(texte)
    etablies = [f for f in toutes if FIABILITE.get(f, "etablie") == "etablie"]
    a_confirmer = [f for f in toutes if FIABILITE.get(f, "etablie") == "a_confirmer"]
    return etablies, a_confirmer


def statut_de(texte):
    """Statut épistémique — LE PLUS PRUDENT gagne (jamais d'affirmation durcie)."""
    t = replier(texte)
    for niveau in ("interrogatif", "rapporte", "modalise"):     # ordre = du plus prudent au moins
        if any(r.search(t) for r in _STATUT_RE[niveau]):
            return niveau
    return "affirme"


def concepts_de(texte, auteur=None):
    """Concepts psychanalytiques touchés → [{groupe, concept}], multigroupe, déterministe.

    `auteur` restreint aux concepts pertinents pour lui : un concept marqué `auteurs: ["jung"]`
    n'est pas cherché chez Freud, qui ne l'employait pas. Sans argument, tout est cherché — c'est
    le comportement actuel, le lexique étant encore entièrement freudien.
    """
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
    return {"ok": not erreurs, "erreurs": erreurs,
            "fonctions": len(FONCTIONS), "groupes": len(CONCEPTS),
            "concepts": sum(len(m["termes"]) for m in CONCEPTS.values())}
