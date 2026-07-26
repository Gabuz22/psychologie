#!/usr/bin/env python3
"""SOURCES — chargement des œuvres et TRAÇABILITÉ de leur provenance.

Reprend la doctrine éprouvée sur le corpus AXA : on ne présente jamais comme certain ce qui ne
l'est pas, et on rend chaque affirmation re-vérifiable dans la source. Ici, deux vérités
inconfortables doivent être portées par les DONNÉES elles-mêmes, jamais tues :

  1. LES TEXTES NE SONT PAS DES PREMIÈRES ÉDITIONS. « Die Traumdeutung » disponible est la 4e éd.
     (1914) d'une œuvre de 1900 ; « Drei Abhandlungen » la 4e éd. (1920) d'une œuvre de 1905.

  2. LES COUCHES D'AJOUT SONT INVISIBLES. Freud écrit lui-même, préface à la 3e éd. des « Drei
     Abhandlungen » : « Ich habe in dieser dritten Auflage reichliche Einschaltungen vorgenommen,
     aber darauf verzichtet, dieselben wie in der vorigen Auflage durch besondere Zeichen
     kenntlich zu machen. » (« j'ai fait d'abondantes insertions, mais j'ai renoncé à les signaler
     par des signes particuliers comme dans l'édition précédente »).

Conséquence directe sur le modèle de données : un atome n'est JAMAIS daté de l'année de l'œuvre.
Il est « attesté AU PLUS TARD » dans l'édition lue (terminus ante quem). Dater un atome « 1900 »
alors qu'il vient d'un ajout de 1914 fausserait toute analyse chronologique — c'est-à-dire l'objet
même du projet. Seules les préfaces, que Freud signe et date, sont datées avec certitude.

La levée de cette incertitude est possible mais reste À FAIRE : elle demande une COLLATION entre
éditions (la 1re éd. est disponible en fac-similé). C'est un chantier distinct, pas une supposition.
"""
import hashlib
import json
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_DE = os.path.join(RACINE, "sources", "freud", "de")

# Bornes du texte utile dans un fichier Project Gutenberg (l'en-tête et la licence n'appartiennent
# pas à l'œuvre : les inclure polluerait les atomes avec du texte administratif anglais).
_DEBUT = re.compile(r"\*\*\* ?START OF TH[EI][^\n]*\*\*\*[^\n]*\n")
_FIN = re.compile(r"\*\*\* ?END OF TH[EI][^\n]*\*\*\*")

# PARATEXTE DU TRANSCRIPTEUR — à l'INTÉRIEUR des bornes ci-dessus, donc invisible au premier
# nettoyage. Deux blocs, vérifiés présents dans les trois œuvres :
#   • en tête  : « Produced by … » + « [ Anmerkungen zur Transkription: … ] » (conventions de
#                transcription : _ = espacé, ~ = italique, # = gras) ;
#   • en queue : « [ Im folgenden werden alle geänderten Textzeilen angeführt … ] », la liste des
#                coquilles corrigées, sous forme de paires avant/après (~25 000 signes dans la
#                Traumdeutung — soit autant de faux atomes si on l'oublie).
# Les laisser produisait des atomes administratifs (« Produced by Jana Srna… ») mêlés à l'œuvre.
_NOTE_TETE = re.compile(r"\A.{0,400}?\[\s*Anmerkungen zur Transkription:.*?^\s*\]\s*$",
                        re.S | re.M)
_NOTE_QUEUE = re.compile(r"^\s*\[\s*Im folgenden werden alle geänderten Textzeilen.*\Z", re.S | re.M)

# Registre des œuvres. `annee_edition` = ce qu'on LIT ; `annee_oeuvre` = première parution.
# L'écart entre les deux EST l'incertitude de datation, portée explicitement.
OEUVRES = {
    "traumdeutung": {
        "fichier": "1900_traumdeutung.pg.txt",
        "titre": "Die Traumdeutung",
        "titre_fr": "L'interprétation des rêves",
        "annee_oeuvre": 1900,
        "annee_edition": 1914,
        "edition": "4. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #40739 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/40739",
        "fac_simile": "https://archive.org/details/Freud_1900_Die_Traumdeutung_k (1re éd., scan)",
    },
    "drei_abhandlungen": {
        "fichier": "1905_drei_abhandlungen.pg.txt",
        "titre": "Drei Abhandlungen zur Sexualtheorie",
        "titre_fr": "Trois essais sur la théorie sexuelle",
        "annee_oeuvre": 1905,
        "annee_edition": 1920,
        "edition": "4. Auflage",
        "editeur": "Franz Deuticke, Leipzig/Wien",
        "source": "Project Gutenberg #39938 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/39938",
        "fac_simile": "https://archive.org/details/Freud_1905_Drei_Abhandlungen (1re éd., scan)",
    },
    "jenseits": {
        "fichier": "1920_jenseits_lustprinzips.pg.txt",
        "titre": "Jenseits des Lustprinzips",
        "titre_fr": "Au-delà du principe de plaisir",
        "annee_oeuvre": 1920,
        "annee_edition": 1921,
        "edition": "1re/2e Auflage (à confirmer par collation)",
        "editeur": "Internationaler Psychoanalytischer Verlag, Leipzig/Wien/Zürich",
        "source": "Project Gutenberg #28220 (relu par Distributed Proofreaders)",
        "url": "https://www.gutenberg.org/ebooks/28220",
        "fac_simile": "https://archive.org/details/II_Freud_1920_Jenseits_k (1re éd., scan)",
    },
}

# Domaine public : Freud est mort en 1939 → libre de droits (vie + 70 ans) depuis 2010, et les
# éditions utilisées sont antérieures à 1931 (règle américaine). Le texte allemand ORIGINAL est
# donc libre ; c'est aussi ce qui garantit au lecteur la citation authentique, sans intermédiaire
# de traduction.
LICENCE = ("Domaine public — Sigmund Freud (1856-1939), œuvre libre de droits depuis 2010 "
           "(vie + 70 ans). Éditions utilisées antérieures à 1931. Texte allemand original.")


def charger(cle):
    """Charge une œuvre → {texte, meta}. `texte` = l'œuvre SEULE (hors en-tête/licence Gutenberg)."""
    if cle not in OEUVRES:
        raise KeyError("œuvre inconnue : %s (connues : %s)" % (cle, ", ".join(sorted(OEUVRES))))
    meta = dict(OEUVRES[cle])
    chemin = os.path.join(DOSSIER_DE, meta["fichier"])
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    texte, bornage = _extraire_corps(brut)
    meta.update({
        "cle": cle,
        "empreinte_fichier": hashlib.sha256(brut.encode("utf-8")).hexdigest()[:16],
        "caracteres_fichier": len(brut),
        "caracteres_oeuvre": len(texte),
        "bornage_gutenberg": bornage,
        "licence": LICENCE,
        "datation": datation(meta),
    })
    return {"texte": texte, "meta": meta}


def _extraire_corps(brut):
    """Retire l'en-tête/licence Gutenberg PUIS le paratexte du transcripteur.

    Si une borne manque, on le DIT dans le rapport plutôt que de laisser croire à un texte propre :
    un corpus silencieusement pollué est pire qu'un corpus dont on connaît le défaut.
    """
    d = _DEBUT.search(brut)
    f = _FIN.search(brut)
    if not d or not f or f.start() <= d.end():
        return brut, "bornes Gutenberg introuvables — texte pris intégralement, À VÉRIFIER"
    corps = brut[d.end():f.start()]
    notes = []
    corps, n = _NOTE_TETE.subn("", corps)
    notes.append("note de transcription en tête %s" % ("retirée" if n else "absente"))
    corps, n = _NOTE_QUEUE.subn("", corps)
    notes.append("liste d'errata en queue %s" % ("retirée" if n else "absente"))
    return corps.strip(), "bornes Gutenberg retirées ; " + " ; ".join(notes)


def datation(meta):
    """Statut de datation d'un atome issu de cette œuvre — honnête par construction.

    `precise=False` signifie : on connaît une borne SUPÉRIEURE (l'édition lue), pas la date réelle
    d'écriture du passage. Toute analyse chronologique doit lire ce champ avant de conclure.
    """
    ecart = meta["annee_edition"] - meta["annee_oeuvre"]
    return {
        "annee_oeuvre": meta["annee_oeuvre"],
        "annee_edition_lue": meta["annee_edition"],
        "fenetre_incertitude_annees": ecart,
        "precise": ecart == 0,
        "regle": "attesté au plus tard dans l'édition %d ; première apparition inconnue dans [%d, %d]"
                 % (meta["annee_edition"], meta["annee_oeuvre"], meta["annee_edition"]),
        "levee_possible_par": "collation avec la 1re édition (fac-similé) — chantier distinct, non fait",
    }


def manifeste():
    """Manifeste de provenance de tout le corpus — ce qu'un chercheur doit pouvoir vérifier."""
    entrees = []
    for cle in OEUVRES:
        chemin = os.path.join(DOSSIER_DE, OEUVRES[cle]["fichier"])
        present = os.path.exists(chemin)
        e = dict(OEUVRES[cle], cle=cle, present=present)
        if present:
            with open(chemin, "rb") as f:
                donnees = f.read()
            e["empreinte_fichier"] = hashlib.sha256(donnees).hexdigest()[:16]
            e["octets"] = len(donnees)
            e["datation"] = datation(OEUVRES[cle])
        entrees.append(e)
    return {
        "version": "1.0.0",
        "licence": LICENCE,
        "avertissement_datation": (
            "Aucune de ces éditions n'est une première édition. Freud a renoncé, à partir de la 3e "
            "édition des Drei Abhandlungen, à signaler ses ajouts. Les couches d'écriture sont donc "
            "INDISCERNABLES dans le texte : un atome est attesté au plus tard dans l'édition lue, "
            "jamais daté de l'année de l'œuvre."),
        "oeuvres": entrees,
    }


if __name__ == "__main__":
    print(json.dumps(manifeste(), ensure_ascii=False, indent=1))
