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

from .segmentation import replier

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
        "marqueurs": [r"\beinwand", r"\beinwendung", r"\beinwenden\b", r"\bman koennte sagen\b",
                      r"\bdagegen spricht\b", r"\bfreilich\b"],
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
CONCEPTS = {
    "reve": {
        "label": "Rêve et travail du rêve",
        "termes": {
            "traum": ["traum", "traume", "traumes", "traeume", "traumen"],
            "traumdeutung": ["traumdeutung"],
            "traumarbeit": ["traumarbeit"],
            "traumgedanke": ["traumgedanke", "traumgedanken"],
            "trauminhalt": ["trauminhalt", "manifeste", "latente"],
            "verdichtung": ["verdichtung"],
            "verschiebung": ["verschiebung"],
            "entstellung": ["entstellung", "traumentstellung"],
            "symbol": ["symbol", "symbolik", "symbolisch"],
            "tagesrest": ["tagesrest", "tagesreste"],
        },
    },
    "topique": {
        "label": "Appareil psychique (topique)",
        "termes": {
            "unbewusst": ["unbewusst", "unbewusste", "unbewussten", "unbewusstes"],
            "vorbewusst": ["vorbewusst", "vorbewusste", "vorbewussten"],
            "bewusstsein": ["bewusstsein", "bewusst"],
            "zensur": ["zensur"],
            "ich": ["ich-", "ichs"],          # « Ich » nu est trop ambigu (pronom) — voir note ci-dessous
            "es": ["das es"],
            "ueberich": ["ueber-ich", "ueberich"],
        },
    },
    "pulsion": {
        "label": "Pulsion, libido, sexualité",
        "termes": {
            "trieb": ["trieb", "triebe", "triebes", "trieben"],
            "libido": ["libido"],
            "sexualitaet": ["sexualitat", "sexuell", "sexuelle", "sexualtrieb"],
            "lustprinzip": ["lustprinzip", "lust"],
            "realitaetsprinzip": ["realitatsprinzip"],
            "todestrieb": ["todestrieb"],
            "wiederholungszwang": ["wiederholungszwang"],
            "narzissmus": ["narzissmus", "narzisstisch"],
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


def concepts_de(texte):
    """Concepts psychanalytiques touchés → [{groupe, concept}], multigroupe, déterministe."""
    t = replier(texte)
    trouves = []
    for groupe, meta in CONCEPTS.items():
        for concept, termes in meta["termes"].items():
            if concept == "ich" and groupe == "topique":
                if _RE_ICH_MOI.search(t):
                    trouves.append({"groupe": groupe, "concept": "ich"})
                continue
            if any(re.search(r"\b" + re.escape(terme), t) for terme in termes):
                trouves.append({"groupe": groupe, "concept": concept})
    return trouves


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
        for concept in meta["termes"]:
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
