#!/usr/bin/env python3
"""LEXIQUE D'OTTO RANK (1884-1939) — construit sur SON vocabulaire, pas sur celui de Freud.

Rank n'est pas un freudien de plus. Son corpus le dit dès le comptage, avant toute lecture : la
constellation familiale y écrase tout (*Sohn* ×20,6 par rapport à Freud, *Gattin* ×46,2,
*Stiefmutter* ×20,2), le mythe et la légende y occupent la place que le rêve occupe chez Freud
(*Überlieferung* ×54, *Sage* ×11, *Mythus* ×7,4), la création littéraire y est un objet à part
entière (*Drama* ×26,2, *dichterisch* ×20,2), et ses propres concepts dominent là où Freud les
effleure (*Geburt* ×9,7, *Ödipus* ×15,2, *Projektion* ×14,2, *Inzest* ×12,7).

Le mesurer avec le lexique freudien reviendrait à ne voir de lui que ce qui ressemble à Freud —
et son motif central, l'ENFANT EXPOSÉ sauvé des eaux qui revient tuer son père, n'a aucune case
dans l'ontologie freudienne. Il serait purement et simplement invisible.

Toutes les fréquences citées dans ce fichier sont MESURÉES sur les cinq œuvres du corpus
(Mythus 1909, Lohengrinsage 1911, Inzest-Motiv 1912, Trauma der Geburt 1924, Genetische
Psychologie II 1928), soit 3,3 millions de signes. Aucun concept n'est entré sans son chiffre.
"""

LANGUE = "de"

CONCEPTS = {
    # ------------------------------------------------------------------ LE NOYAU DE RANK
    # Ce groupe n'existe pas chez Freud, et c'est le plus dense du corpus de Rank : la parenté
    # n'y est pas un décor du complexe, elle EST l'objet. Rank compte les places (fils, fille,
    # frère, sœur, époux, marâtre) parce que le mythe les permute, et c'est cette permutation
    # qu'il décrit livre après livre.
    "parente": {
        "label": "Constellation familiale — les places et leurs permutations",
        "termes": {
            "vater": ["vater"],
            "mutter": ["mutter"],
            # Distingués de « mutter »/« vater » : ce sont des places de SUBSTITUTION, le ressort
            # du conte (Blanche-Neige, Cendrillon) et un cas que Rank suit expressément.
            "stiefeltern": ["stiefmutter", "stiefvater", "pflegemutter", "pflegevater",
                            "ziehmutter", "ziehvater", "nahrmutter"],
            "sohn": ["sohn", "sohne", "sohnes"],
            "tochter": ["tochter"],
            "bruder": ["bruder", "brudern", "bruderlich"],
            "schwester": ["schwester"],
            "geschwister": ["geschwister", "zwilling"],
            "eltern": ["eltern"],
            "gatte": ["gatte", "gatten", "gattin", "ehe\\b", "ehemann", "ehefrau", "heirat",
                      "vermahl", "braut", "brautigam"],
            "kind": ["kind", "knabe", "knaben", "madchen", "saugling"],
            # La royauté est chez Rank une FORME de la famille, pas un fait politique : le roi
            # est le père, la reine la mère, la princesse la fille. C'est le déguisement sous
            # lequel le mythe raconte la parenté. Les compter à part rend ce déguisement visible.
            "koenigsfamilie": ["konig", "konigin", "konigs", "konigstochter", "konigssohn",
                               "prinz", "prinzessin", "fursten"],
        },
    },
    # ------------------------------------------------------------------ LE MYTHE
    # Chez Freud, le matériau premier est le rêve ; chez Rank, c'est la légende transmise.
    # « Überlieferung » (la transmission) est 54 fois plus fréquent chez lui que chez Freud —
    # l'écart le plus fort de tout le corpus, et le meilleur résumé de ce qui les sépare.
    "mythe": {
        "label": "Mythe, légende, transmission",
        "termes": {
            "mythus": ["mythus", "mythos", "mythen", "mythisch", "mythologi"],
            "sage": ["sage\\b", "sagen\\b", "sagenhaft", "sagenkreis", "legende"],
            "marchen": ["marchen"],
            "ueberlieferung": ["uberliefer"],
            "held": ["held", "heldin", "heldentum", "heroisch"],
            # LE motif de Rank, celui qui donne son titre au livre de 1909 : l'enfant qu'on
            # abandonne aux eaux et qui survit (Sargon, Moïse, Œdipe, Romulus, Cyrus, Karna).
            # 134 occurrences ; aucun équivalent dans l'ontologie freudienne.
            "aussetzung": ["aussetzung", "ausgesetzt", "aussetzen", "korbchen", "korb\\b"],
            "rettung": ["rettung", "gerettet", "retter", "errettung"],
            "motiv": ["motiv"],
            "orakel": ["orakel", "prophezei", "weissagung", "traumdeutung"],
            "wunder": ["wunder"],
        },
    },
    # ------------------------------------------------------------------ LA CRÉATION
    # Rank a écrit « Der Künstler » avant tout le reste, et il n'a jamais cessé de traiter
    # l'œuvre d'art comme un objet psychologique de plein droit — non comme une illustration
    # clinique. *Drama* ×26,2 et *dichterisch* ×20,2 par rapport à Freud le mesurent.
    "creation": {
        "label": "Création littéraire et artistique",
        "termes": {
            "dichter": ["dichter", "dichtung", "dichterisch", "gedicht"],
            "kunstler": ["kunstler", "kunstlerisch", "kunst\\b"],
            "schoepfung": ["schopfung", "schopferisch", "schaffen", "schaffens"],
            "drama": ["drama", "dramat", "tragodie", "tragisch", "buhne"],
            "stoff": ["stoff", "thema", "fabel"],
            "gestalt": ["gestalt"],
            "roman": ["roman\\b", "romane", "novelle", "erzahlung"],
        },
    },
    # ------------------------------------------------------------------ LA THÈSE DE 1924
    # C'est ici que Rank rompt avec Freud, et le lexique doit le rendre MESURABLE : il place à
    # l'origine de toute angoisse le traumatisme de la naissance, là où Freud met le complexe
    # d'Œdipe. Sans ces concepts, la divergence la plus documentée de l'histoire du mouvement
    # psychanalytique ne laisserait aucune trace dans les données.
    "naissance": {
        "label": "Naissance, matrice, angoisse originaire",
        "termes": {
            "geburt": ["geburt", "geboren", "gebar", "entbind"],
            "geburtstrauma": ["geburtstrauma", "urtrauma", "geburtsakt", "geburtsangst"],
            "mutterleib": ["mutterleib", "mutterschoss", "intrauterin", "embryo", "fotal",
                           "foetal", "pranatal"],
            "angst": ["angst", "angstlich"],
            "trennung": ["trennung", "getrennt", "loslosung", "ablosung"],
            "wiedergeburt": ["wiedergeburt", "wiedergeboren", "unsterblich"],
        },
    },
    # ------------------------------------------------------------------ L'INTERDIT
    # *Inzest* ×12,7, *inzestuös* ×28,2, *Ödipus* ×15,2 : Rank emploie ces termes bien plus que
    # Freud, parce qu'il les cherche dans mille récits au lieu de les déduire de quelques cures.
    "interdit": {
        "label": "Inceste, meurtre du père, interdit",
        "termes": {
            "inzest": ["inzest", "inzestuos", "blutschande"],
            "oedipus": ["odipus", "odipal"],
            "vatermord": ["vatermord", "vatertotung", "konigsmord", "muttermord"],
            "verbot": ["verbot", "verboten", "untersagt"],
            "strafe": ["strafe", "bestraf", "suhne", "busse"],
            "schuld": ["schuld", "schuldgefuhl", "schuldig"],
        },
    },
    # ------------------------------------------------------------------ LES AFFECTS
    # Rank raconte des passions, pas des symptômes : *Hass* ×8,5, *Leidenschaft* ×9,2,
    # *Verrat* ×6,1, *Rache*. Ce registre n'a pas de groupe chez Freud, dont le vocabulaire
    # affectif passe par l'économie (investissement, décharge).
    "passions": {
        "label": "Passions : amour, haine, jalousie, vengeance",
        "termes": {
            "liebe": ["liebe", "liebt", "geliebt", "verliebt"],
            "hass": ["hass", "hasst", "gehasst", "verhasst"],
            "eifersucht": ["eifersucht", "eifersuchtig"],
            "leidenschaft": ["leidenschaft"],
            "rache": ["rache", "racher", "gerachet"],
            "verrat": ["verrat", "verrater", "verraten"],
            "neigung": ["neigung"],
        },
    },
    # ------------------------------------------------------------------ LES MÉCANISMES
    # Vocabulaire commun avec Freud — mais Rank en fait un usage propre, et c'est justement ce
    # qu'un lexique séparé permet de mesurer : sa `projektion` est 14,2 fois plus fréquente que
    # chez Freud, parce qu'il en fait le mécanisme de formation du mythe lui-même.
    "mecanismes": {
        "label": "Mécanismes psychiques",
        "termes": {
            "verdraengung": ["verdrang"],
            "projektion": ["projektion", "projizier"],
            "identifizierung": ["identifizierung", "identifizier"],
            "ersatz": ["ersatz", "ersetz"],
            "phantasie": ["phantasie", "phantasier"],
            "symbol": ["symbol"],
            "unbewusst": ["unbewusst"],
            "widerstand": ["widerstand"],
            "uebertragung": ["ubertragung"],
        },
    },
    # ------------------------------------------------------------------ LA CURE, TARDIVE
    # Présent surtout dans la « Genetische Psychologie » (1928), où Rank a quitté Vienne et
    # défend une technique à lui — la fin de cure fixée d'avance, la volonté du patient comme
    # ressort. Ce groupe est petit à dessein : Rank n'est pas d'abord un clinicien.
    "cure": {
        "label": "Cure et technique (Rank tardif)",
        "termes": {
            "analytiker": ["analytiker", "analytisch"],
            "patient": ["patient", "neurotiker"],
            "therapie": ["therapie", "therapeutisch", "heilung"],
            # LE concept du dernier Rank, celui qui le sépare définitivement de Freud : la
            # volonté comme force positive, non comme résistance à réduire. On exige la forme
            # nominale — « will » seul est le verbe « wollen », omniprésent et sans rapport.
            "wille": ["wille", "willen\\b", "willens", "willkur"],
            "selbstaendigkeit": ["selbstandig", "unabhangig", "abhangigkeit"],
        },
    },
    # ------------------------------------------------------------------ LA MORT (audit 2)
    # 1 310 occurrences — le plus gros manque du premier lexique. Chez Rank la mort n'est pas un
    # thème parmi d'autres : le héros TUE le père, les frères s'entretuent, l'exposition de
    # l'enfant est une mise à mort déguisée. Sans ce groupe, un quart de ses récits parlait dans
    # le vide.
    "mort": {
        "label": "Mort, meurtre, deuil",
        "termes": {
            # « tot » exclut « total » et « Totem » — deux mots sans rapport que le motif nu
            # ramassait (leçon des audits freudiens : vérifier les FORMES réellement captées).
            "tod": ["tod", r"tot(?!al|em)", "sterb", "gestorben", "todlich"],
            "toetung": ["totung", "mord", "ermord", "erschlag", "opfertod"],
            "trauer": ["trauer", "klage\\b"],
            "unterwelt": ["unterwelt", "grab\\b", "graber", "hades", "jenseits\\b"],
        },
    },
    # ------------------------------------------------------------------ LA VIE PSYCHIQUE (audit 2)
    # Vocabulaire que Rank partage avec la psychologie de son temps, et qui manquait entièrement :
    # Seele 589, Entwicklung 563, Charakter 492, Gefühl 453. « Charakter und Selbst » est un
    # chapitre entier de la Genetische Psychologie — l'omettre revenait à ne pas voir son dernier
    # livre.
    "vie_psychique": {
        "label": "Âme, caractère, développement, affect",
        "termes": {
            "seele": ["seele", "seelisch", "seelen"],
            "charakter": ["charakter"],
            "entwicklung": ["entwicklung", "entwickel", "entwickl"],
            "gefuehl": ["gefuhl"],
            "erinnerung": ["erinner", "gedachtnis"],
            # Le piège Traum/Trauma, déjà mesuré chez Freud : « traum(?!a) » rejetterait
            # « Traumarbeit ». On discrimine sur la FAMILLE MORPHOLOGIQUE attestée, jamais sur la
            # lettre suivante. Motif repris tel quel du lexique freudien, où il a été éprouvé.
            "traum": [r"traum(?!a(?:s?\b|ti(?:sch|sier)|tolog))"],
            "schlaf": ["schlaf"],
            "ideal": ["ideal"],
            # 756 occurrences. Chez le dernier Rank, « Leben » n'est plus un mot ordinaire : il
            # s'oppose à l'analyse elle-même (« zurück ins Leben », le patient qu'on rend à la
            # vie plutôt qu'on ne le maintient dans la cure). C'est le tournant vitaliste qui
            # l'éloigne définitivement de Freud.
            "leben": ["leben", "lebendig", "lebens"],
        },
    },
    # ------------------------------------------------------------------ SEXUALITÉ (audit 2)
    # 851 occurrences. Rank ne parle pas de sexualité comme Freud — il l'aborde par la GÉNÉALOGIE
    # (qui engendre qui, avec qui) plutôt que par la pulsion. D'où un groupe distinct de
    # `interdit`, qui, lui, porte la transgression.
    "sexualite": {
        "label": "Sexualité, génération, différence des sexes",
        "termes": {
            "sexualitaet": ["sexual", "sexuell", "geschlechtlich"],
            "geschlecht": [r"geschlecht(?!lich)"],
            "zeugung": ["zeugung", "erzeugt", "fortpflanz", "empfangnis"],
            "kastration": ["kastration"],
            "libido": ["libido", "libidin"],
            "narzissmus": ["narziss"],
        },
    },
    # ------------------------------------------------------------------ CLINIQUE (audit 2)
    # Petit mais réel : Rank reste analyste praticien, surtout dans le Trauma der Geburt.
    "clinique": {
        "label": "Névrose et symptôme",
        "termes": {
            "neurose": ["neuros", "neurotik", "nervos"],
            "hysterie": ["hysteri"],
            "symptom": ["symptom"],
            "fixierung": ["fixier"],
            "regression": ["regress"],
        },
    },
    # ------------------------------------------------------------------ MÉTA-DISCOURS (audit 2)
    # 794 occurrences : Rank parle beaucoup de la psychanalyse elle-même — de ce qu'elle peut,
    # de ce qu'elle a manqué. C'est là que se joue sa séparation, et le corpus doit pouvoir
    # retrouver ces passages.
    "episteme": {
        "label": "La psychanalyse prise pour objet",
        "termes": {
            "psychoanalyse": ["psychoanaly", "psychologi"],
            "problem": ["problem"],
            "forschung": ["forschung", "wissenschaft", "erkenntnis"],
        },
    },
    # ------------------------------------------------------------------ LE DÉCOR MYTHIQUE
    # Ces éléments ne sont pas des ornements : chez Rank, l'eau est la matrice, l'animal le
    # sauveteur, la montagne l'exposition. Il les lit comme des signes réguliers, et leur
    # récurrence chiffrée (Wasser 270, Tier 199) est un fait sur sa méthode.
    "decor_mythique": {
        "label": "Éléments récurrents du récit mythique",
        "termes": {
            "wasser": ["wasser", "fluss", "meer\\b", "strom\\b", "flut"],
            "tier": ["tier", "wolf", "hirsch", "hund\\b", "vogel", "schwan"],
            "gott": ["gott", "gotter", "gottlich", "gottheit"],
            "berg_hoehle": [r"berg\b", r"berge\b", "hohle", r"wald\b"],
            "baum": ["baum", "baume"],
            # AUDIT 3 (2026-07-28) — le décor restant du récit, relevé dans les phrases pleines
            # encore non qualifiées. Cohérent avec ce groupe, qui traite déjà l'eau et l'animal
            # comme des signes réguliers et non comme des ornements : chez Rank la nuit est le
            # moment de l'exposition, l'épée l'instrument de la reconnaissance, la maison le lieu
            # dont le héros est chassé.
            "nacht": ["nacht", "nachts", "nachte", "dunkel", "finster"],
            "waffe": ["schwert", "waffe", "speer", "pfeil", "bogen\\b"],
            "haus": [r"haus\b", "hause", "hauses", "hof\\b", "burg\\b", "palast"],
            "auge": ["auge", "augen", r"blick\b", "blind"],
        },
    },
}


# --------------------------------------------------------------------------- FONCTIONS
# Rank cite, compare et rapporte bien plus qu'il ne conduit d'analyses : sa méthode est
# COMPARATIVE (il aligne des dizaines de versions d'un même récit), là où celle de Freud est
# clinique. Les marqueurs le suivent — d'où une fonction « comparaison » qui n'existe pas chez
# Freud, et l'absence de « association libre », qui n'a pas de sens dans son travail.
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
        "id": "comparaison",
        "label": "Comparaison de versions",
        "aide": "LE geste propre à Rank : aligner plusieurs récits d'un même motif pour en tirer "
                "la forme commune. C'est sa méthode, comme l'analyse de rêve est celle de Freud.",
        "marqueurs": [r"\bahnlich", r"\bebenso wie\b", r"\bin gleicher weise\b", r"\bparallel",
                      r"\bvariante", r"\bfassung\b", r"\bversion", r"\bvergleich",
                      r"\bentspricht\b", r"\bwiederkehr"],
    },
    {
        "id": "recit",
        "label": "Récit rapporté",
        "aide": "Rank raconte le mythe avant de l'interpréter ; ces passages sont du matériau, "
                "pas de la thèse. Les distinguer évite de lire une narration comme une position.",
        "marqueurs": [r"\berzahlt\b", r"\blautet\b", r"\bberichtet\b", r"\bheisst es\b",
                      r"\bder sage nach\b", r"\bnach der uberlieferung\b", r"\bes war einmal\b"],
    },
    {
        "id": "methode",
        "label": "Énoncé méthodologique",
        "marqueurs": [r"\bdeutung", r"\bmethode\b", r"\bverfahren\b", r"\bauffassung\b",
                      r"\banalyse", r"\buntersuchung"],
    },
    {"id": "question", "label": "Question de recherche", "marqueurs": [r"\?"]},
    {
        "id": "savoir_etabli",
        "label": "Renvoi à un savoir établi",
        "marqueurs": [r"\bbekanntlich\b", r"\bwir wissen\b", r"\bbekannt ist\b", r"\bwie bekannt\b"],
    },
    # -------- SIGNAUX À CONFIRMER : jamais des faits, seulement une liste de travail.
    # Même doctrine que pour Freud — un marqueur lexical peut SIGNALER une révision, il ne peut
    # pas l'ÉTABLIR. Ces trois-là sont particulièrement précieux chez Rank : c'est par eux qu'on
    # suivra sa séparation d'avec Freud, entre 1909 et 1928.
    {
        "id": "objection",
        "label": "Objection anticipée",
        "fiabilite": "a_confirmer",
        # « einwand » exclut « einwandfrei » (irréprochable — un ÉLOGE) et toute la famille
        # « einwandern / Einwanderung » (immigrer, migration). Le lexique freudien écarte la
        # seconde par `(?!ern)`, ce qui suffit au VERBE mais laisse passer le SUBSTANTIF : chez
        # Rank, « vor der dorischen Einwanderung » était compté comme une objection. On exclut
        # donc « er » et non « ern ». Le corpus de Freud, lui, ne contient aucune occurrence du
        # substantif — le défaut y était latent, jamais déclenché.
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
        "id": "ecart_freud",
        "label": "Écart déclaré avec Freud",
        "aide": "SIGNAL CENTRAL POUR CET AUTEUR : Rank nomme Freud 273 fois. Ces passages sont "
                "la matière première de sa divergence — mais un marqueur ne peut que les "
                "DÉSIGNER, jamais décider s'ils marquent un accord, une nuance ou une rupture. "
                "Ils vont donc en liste à vérifier, et seront lus un par un.",
        "fiabilite": "a_confirmer",
        "marqueurs": [r"\bfreud\b.{0,60}?\b(gegen|anders|abweich|nicht zu|unterschied|jedoch)\b",
                      r"\b(gegen|anders als|abweichend von|im gegensatz zu)\b.{0,30}?\bfreud",
                      r"\bfreud\w*\s+(auffassung|ansicht|annahme|lehre|meinung)\b",
                      r"\bim gegensatz zur psychoanalyse\b"],
    },
]

# Auteurs que Rank discute — pour l'essentiel des mythologues, des germanistes et des
# folkloristes, non des cliniciens : c'est la bibliothèque d'un comparatiste.
NOMS_AUTEURS = ["freud", "grimm", "winckler", "siecke", "lessmann", "frobenius", "golther",
                "herodot", "ktesias", "jeremias", "bachofen", "wundt", "abraham", "jung",
                "rohde", "usener", "gervinus", "schiller", "goethe", "shakespeare"]

# Statuts épistémiques — mêmes niveaux que pour tout le corpus (la doctrine ne dépend pas de
# l'auteur), mais marqueurs relevés dans SA prose.
MARQUEURS_STATUT = {
    "modalise":     [r"\bvielleicht\b", r"\bwahrscheinlich\b", r"\bvermutlich\b", r"\bscheint\b",
                     r"\bdurfte\b", r"\bwohl\b", r"\bmoglicherweise\b", r"\bkaum\b", r"\betwa\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"\berzahlt\b", r"\bberichtet\b", r"\bnach \w+\b", r"\bzitiert\b",
                     r"\blautet\b", r"\bangeblich\b", r"\bder sage nach\b"],
}
