#!/usr/bin/env python3
"""LEXIQUE DE GUSTAVE LE BON (1841-1931) — ses catégories, en français, pour « Psychologie des
foules » (1895).

HISTORIQUE À CONNAÎTRE. Le Bon est entré au corpus AVANT que la règle « un lexique par auteur »
ne soit posée : ses concepts étaient alors des identifiants freudiens (`masse`, `fuehrer`,
`suggestion`) auxquels on avait attaché des motifs français. Cela fonctionnait, mais au prix
exact que la nouvelle règle refuse : sa `foule` s'appelait `masse` et se confondait, dans toute
lecture rapide, avec la *Masse* de Freud — qui désigne autre chose, écrit vingt-six ans plus tard,
en discutant précisément ce livre-ci.

Ses concepts portent donc désormais SES noms. Ce n'est pas cosmétique : c'est ce qui interdit
d'additionner par mégarde deux notions homonymes, et ce qui oblige à déclarer explicitement le
rapprochement Le Bon/Freud le jour où on le mesurera.

Toutes les fréquences citées sont mesurées sur l'édition Alcan de 1895 (1 485 atomes).
Les motifs sont en forme REPLIÉE : minuscules, sans accents (« peut-être » → « peut-etre »).
"""

LANGUE = "fr"

CONCEPTS = {
    # ------------------------------------------------------------------ LE NOYAU DU LIVRE
    # 420 atomes sur 1 485 parlent de la foule : c'est le seul objet du volume, et son unité
    # d'analyse. Le Bon la définit comme un être NOUVEAU, distinct de la somme des individus —
    # d'où la nécessité de séparer les deux termes.
    "foule": {
        "label": "La foule comme être collectif",
        "termes": {
            "foule": [r"foules?\b"],
            "individu": ["individu", "individuel", "isole"],
            "collectivite": [r"collectivites?\b", "collectif", "agglomeration", "assemblee"],
            "race": [r"races?\b", r"peuples?\b", "nation"],
            "classe": [r"classes?\b", r"castes?\b"],
        },
    },
    # ------------------------------------------------------------------ LES TROIS MÉCANISMES
    # Le cœur théorique : Le Bon explique la foule par trois ressorts, qu'il énumère lui-même.
    # Freud reprendra les trois termes en 1921 pour les discuter un par un — c'est sur ce groupe
    # que la controverse se mesurera, le jour où la couche de comparaison sera construite.
    "mecanismes": {
        "label": "Suggestion, contagion, prestige — les trois ressorts",
        "termes": {
            "suggestion": ["suggestion", "suggestib", "suggestionn", "hypnos", "hypnoti"],
            "contagion": ["contagion", "contagieu"],
            "prestige": ["prestige"],
            "imitation": ["imitation", "imitateur", r"imite", r"imiter\b"],
            "meneur": [r"meneurs?\b", r"chefs?\b", r"conducteurs?\b"],
            "affirmation_repetition": [r"affirmations?\b", r"repetitions?\b"],
        },
    },
    # ------------------------------------------------------------------ LA VIE MENTALE
    # Le Bon écrit « inconscient » dès 1895 — vingt-cinq ans avant la métapsychologie freudienne,
    # et dans un tout autre sens : un fonds héréditaire de race, non un refoulé. Le mot est le
    # même, la chose ne l'est pas ; c'est le cas d'école qui justifie les lexiques séparés.
    "vie_mentale": {
        "label": "Inconscient, conscience, âme collective",
        "termes": {
            "inconscient": ["inconscien"],
            "conscient": [r"(?<!in)conscien"],
            # « l'âme des foules », « l'âme des races » : LE terme psychologique de Le Bon,
            # qu'il pose lui-même en équivalent de « caractère mental » dans son introduction.
            "ame": [r"ames?\b"],
            "imagination": ["imagination", "imaginat"],
            "sentiment": [r"sentiments?\b", "emotion", "passion"],
            "raisonnement": ["raisonn", r"logiques?\b", r"raison\b", "intelligence"],
            "croyance": ["croyance", "croire", "conviction", "foi\\b"],
            "illusion": ["illusion", "chimere"],
        },
    },
    # ------------------------------------------------------------------ CE QUI FAIT AGIR
    "action": {
        "label": "Ce qui met la foule en mouvement",
        "termes": {
            "image_mot_formule": [r"images?\b", r"mots?\b", r"formules?\b", "vocable"],
            "meneur_moyens": ["autorite", "domination", "obeissance", "discipline"],
            "violence": ["violen", "massacre", "destruction", "fureur", "crime", "criminel"],
            "heroisme": ["heroisme", "heroique", "devouement", "sacrifice", "martyr"],
            "impulsivite": ["impulsi", "mobilite", "irritabilite", "versatil"],
            "credulite": ["credul", "naif", "naivete"],
        },
    },
    # ------------------------------------------------------------------ LES IDÉES (audit 2)
    # OMISSION FLAGRANTE du premier lexique : `idee` compte 142 occurrences et Le Bon consacre un
    # CHAPITRE ENTIER aux « idées des foules » (livre I, ch. III, § 1). Le titre même du chapitre
    # ne trouvait aucune case. C'est le rappel que le vocabulaire d'un auteur se relève dans son
    # texte, jamais dans l'idée qu'on se fait de son sujet.
    "pensee": {
        "label": "Idées, opinions, esprit",
        "termes": {
            "idee": [r"idees?\b"],
            "opinion": [r"opinions?\b"],
            "esprit": [r"esprits?\b", "mental", "intellectuel"],
            "caractere": ["caractere"],
            "volonte": ["volonte", r"vouloir\b", r"veulent\b"],
        },
    },
    # ------------------------------------------------------------------ FORCE ET ACTION (audit 2)
    # Le Bon écrit une psychologie du POUVOIR : ce qui fait agir, ce qui domine, ce qui réussit.
    # 182 + 110 occurrences, et rien pour les entendre dans le premier lexique.
    "puissance": {
        "label": "Force, pouvoir, action",
        "termes": {
            "force": [r"forces?\b", "puissance", "pouvoir", "energie"],
            "acte": [r"actes?\b", r"agir\b", "action"],
            "succes": ["succes", "triomph", "victoire", "echec", "defaite"],
            "besoin": ["besoin", "instinct", "appetit", "desir"],
            "armee": ["armee", "soldat", "militaire", r"general\b"],
        },
    },
    # ------------------------------------------------------------------ LA PREUVE (audit 2)
    # Le Bon argumente en naturaliste — il invoque le fait, la loi, l'expérience. Ce registre
    # épistémique est absent de sa théorie mais partout dans sa prose.
    "episteme": {
        "label": "Fait, loi, preuve",
        "termes": {
            "fait": [r"faits?\b", "phenomene", "observation"],
            "loi": [r"lois?\b", "regle", "principe"],
            "preuve": ["preuve", "demontr", "prouv", "experience", "experim"],
            "morale": ["moral", "vertu", r"devoir\b", "honneur"],
        },
    },
    # ------------------------------------------------------------------ L'HISTOIRE
    # Le Bon écrit une psychologie POLITIQUE : la Révolution, la Terreur, le suffrage universel,
    # les assemblées parlementaires. C'est son terrain d'observation, comme la cure est celui
    # de Freud — et cela n'a aucun équivalent dans l'ontologie freudienne.
    "politique": {
        "label": "Institutions, histoire, opinion",
        "termes": {
            "revolution": ["revolution", "terreur", "convention", "jacobin", "insurrection"],
            "institution": ["institution", "gouvernement", r"etats?\b", "parlement", "assemblee"],
            "suffrage": ["suffrage", "electeur", "electoral", "vote", "candidat", "comite"],
            "civilisation": ["civilisation", "civilise", "barbarie", "decadence"],
            "education": ["education", "instruction", "enseignement", "examen", "diplome"],
            "religion": ["religion", "religieu", r"dieux?\b", "divinite", "culte", "fanatis"],
            "tradition": ["tradition", "heredite", "ancetre", "passe\\b"],
        },
    },
}


# --------------------------------------------------------------------------- FONCTIONS
# Le Bon affirme : 90 % de ses atomes sont au statut « affirmé » (1 335 sur 1 485), contre une
# prose freudienne constamment modalisée. Son appareil argumentatif est donc mince, et le
# lexique ne doit pas inventer des nuances qu'il ne prend pas.
#
# DEUX FONCTIONS SONT VOLONTAIREMENT ABSENTES, et l'absence est le résultat :
#   • « association libre » — l'Einfall est un terme technique de la cure, sans objet ici ;
#   • « révision » — aucune formule de correction de soi n'est attestée dans le volume. Sur LE
#     signal central du projet, mieux vaut aucun marqueur que des marqueurs faibles.
FONCTIONS = [
    {
        "id": "inference",
        "label": "Inférence / conclusion",
        "marqueurs": [r"\bdonc\b", r"\bpar consequent\b", r"\bdes lors\b", r"\bil en resulte\b",
                      r"\bil s'ensuit\b", r"\bc'est pourquoi\b", r"\bpar suite\b",
                      r"\bon peut conclure\b", r"\bnous pouvons conclure\b"],
    },
    {
        "id": "hypothese",
        "label": "Hypothèse / conjecture",
        "marqueurs": [r"\bpeut-etre\b", r"\bprobablement\b", r"\bvraisemblablement\b",
                      r"\bsans doute\b", r"\bil semble\b", r"\bil est possible\b",
                      r"\bsupposons\b", r"\bsi l'on admet\b", r"\bon peut supposer\b"],
    },
    {
        "id": "methode",
        "label": "Énoncé méthodologique",
        # « procédé » est ÉCARTÉ : replié, il devient « procede » et se confond avec le verbe
        # « procède » (« ces sentiments procèdent de… »), fréquent dans la prose de 1895.
        "marqueurs": [r"\bmethodes?\b", r"\banalyse", r"\bexamen\b", r"\bclassification\b"],
    },
    {"id": "question", "label": "Question / interrogation", "marqueurs": [r"\?"]},
    {
        "id": "analogie",
        "label": "Analogie / métaphore",
        "marqueurs": [r"\bcomme si\b", r"\bsemblables? a\b", r"\bpareils? a\b", r"\bcomparable",
                      r"\bde meme que\b", r"\bpar exemple\b", r"\ba la facon de\b", r"\banalog"],
    },
    {
        "id": "savoir_etabli",
        "label": "Renvoi à un savoir établi",
        "marqueurs": [r"\bon sait que\b", r"\bchacun sait\b", r"\bnul n'ignore\b",
                      r"\bil est bien connu\b", r"\bcomme on le sait\b", r"\bnous savons\b"],
    },
    {
        "id": "exemple_historique",
        "label": "Exemple historique",
        "aide": "Le Bon prouve par l'Histoire — la Révolution, les croisades, Napoléon — comme "
                "Freud prouve par la cure. C'est son mode d'administration de la preuve.",
        "marqueurs": [r"\brevolution\b", r"\bcroisades?\b", r"\bnapoleon\b", r"\bterreur\b",
                      r"\bhistoire nous\b", r"\bl'histoire montre\b", r"\bsaint-barthelemy\b"],
    },
    {
        "id": "rapport_tiers",
        "label": "Rapport d'un tiers",
        # « cite » est ÉCARTÉ : replié, « la cité » (Fustel de Coulanges a écrit « La Cité
        # antique », que Le Bon discute) devient « la cite » et se compterait comme citation.
        # « rapporte » exclut « se rapporte à » (= concerner), très fréquent en 1895.
        "marqueurs": [r"\bd'apres \w+", r"\bselon \w+", r"(?<!se )\brapporte\b", r"\braconte\b",
                      r"\becrivait\b", r"\becrit que\b"],
    },
    {
        "id": "objection",
        "label": "Objection anticipée",
        "fiabilite": "a_confirmer",
        "marqueurs": [r"\bon objectera\b", r"\bon pourrait objecter\b", r"\bl'objection\b",
                      r"\bon dira que\b", r"\bon repondra\b"],
    },
    {
        "id": "auto_citation",
        "label": "Renvoi à son propre travail",
        "fiabilite": "a_confirmer",
        "marqueurs": [r"\bnous avons vu\b", r"\bnous avons dit\b",
                      r"\bnous l'avons (?:vu|dit|montre)\b", r"\bj'ai montre\b",
                      r"\bcomme je l'ai (?:dit|montre)\b", r"\bdit plus haut\b",
                      r"\bavons montre\b"],
    },
]

# Auteurs que Le Bon discute nommément dans le volume de 1895.
NOMS_AUTEURS = ["taine", "tocqueville", "spencer", "tarde", "ribot", "fustel de coulanges"]

MARQUEURS_STATUT = {
    "modalise":     [r"\bpeut-etre\b", r"\bprobablement\b", r"\bsans doute\b", r"\bsemble",
                     r"\bparait\b", r"\bvraisemblablement\b", r"\ba peine\b", r"\bpourrait\b"],
    "interrogatif": [r"\?"],
    "rapporte":     [r"(?<!se )\brapporte\b", r"\braconte\b", r"\bd'apres \w+", r"\bselon \w+",
                     r"\bpretend", r"\bdit-on\b", r"\bparait-il\b"],
}
