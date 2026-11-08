"""
Spoken star names, and spoken observations.

Dictating a variable star observation runs into one hard problem: speech
recognition has never heard of "SS Cyg". It returns what an English speaker
appears to have said - "SS Cygni", "ess ess signee", "S S Cygnus", sometimes
"as as signy" - and none of those is a catalogue designation.

So nothing here tries to understand free speech. Instead every object in the
catalogue is turned into the set of forms a person might plausibly say, the
heard text is pushed through the same normalisation, and the two are matched.
That way the answer is always a real object, and when it is wrong it is wrong
by picking the second-best real star rather than by inventing one.

The same table drives the other direction: given a designation, how to say it
out loud, and a respelling for the constellation genitives that are easy to
read and hard to pronounce (Ophiuchi, Coronae Borealis, Camelopardalis).
"""

import difflib
import re

# abbreviation: (nominative, genitive, respelled genitive)
CONSTELLATIONS = {
    'And': ('Andromeda', 'Andromedae', 'an-DROM-eh-dee'),
    'Ant': ('Antlia', 'Antliae', 'ANT-lee-ee'),
    'Aps': ('Apus', 'Apodis', 'AP-oh-diss'),
    'Aqr': ('Aquarius', 'Aquarii', 'ah-KWAIR-ee-eye'),
    'Aql': ('Aquila', 'Aquilae', 'AK-wil-ee'),
    'Ara': ('Ara', 'Arae', 'AIR-ee'),
    'Ari': ('Aries', 'Arietis', 'ah-RY-eh-tiss'),
    'Aur': ('Auriga', 'Aurigae', 'aw-RY-jee'),
    'Boo': ('Bootes', 'Bootis', 'boh-OH-tiss'),
    'Cae': ('Caelum', 'Caeli', 'SEE-lye'),
    'Cam': ('Camelopardalis', 'Camelopardalis', 'kah-mel-oh-PAR-dal-iss'),
    'Cnc': ('Cancer', 'Cancri', 'KANG-kry'),
    'CVn': ('Canes Venatici', 'Canum Venaticorum', 'KAY-num ven-at-ih-KOR-um'),
    'CMa': ('Canis Major', 'Canis Majoris', 'KAY-niss mah-JOR-iss'),
    'CMi': ('Canis Minor', 'Canis Minoris', 'KAY-niss my-NOR-iss'),
    'Cap': ('Capricornus', 'Capricorni', 'kap-rih-KOR-nye'),
    'Car': ('Carina', 'Carinae', 'kah-RY-nee'),
    'Cas': ('Cassiopeia', 'Cassiopeiae', 'kas-ee-oh-PEE-ee'),
    'Cen': ('Centaurus', 'Centauri', 'sen-TOR-eye'),
    'Cep': ('Cepheus', 'Cephei', 'SEE-fee-eye'),
    'Cet': ('Cetus', 'Ceti', 'SEE-tye'),
    'Cha': ('Chamaeleon', 'Chamaeleontis', 'kah-mee-lee-ON-tiss'),
    'Cir': ('Circinus', 'Circini', 'SIR-sin-eye'),
    'Col': ('Columba', 'Columbae', 'koh-LUM-bee'),
    'Com': ('Coma Berenices', 'Comae Berenices', 'KOH-mee bair-eh-NY-seez'),
    'CrA': ('Corona Australis', 'Coronae Australis', 'koh-ROH-nee aw-STRAL-iss'),
    'CrB': ('Corona Borealis', 'Coronae Borealis', 'koh-ROH-nee bor-ee-AL-iss'),
    'Crv': ('Corvus', 'Corvi', 'KOR-vye'),
    'Crt': ('Crater', 'Crateris', 'krah-TEER-iss'),
    'Cru': ('Crux', 'Crucis', 'KROO-siss'),
    'Cyg': ('Cygnus', 'Cygni', 'SIG-nye'),
    'Del': ('Delphinus', 'Delphini', 'del-FY-nye'),
    'Dor': ('Dorado', 'Doradus', 'doh-RAH-duss'),
    'Dra': ('Draco', 'Draconis', 'drah-KOH-niss'),
    'Equ': ('Equuleus', 'Equulei', 'eh-KWOO-lee-eye'),
    'Eri': ('Eridanus', 'Eridani', 'eh-RID-an-eye'),
    'For': ('Fornax', 'Fornacis', 'for-NAY-siss'),
    'Gem': ('Gemini', 'Geminorum', 'jem-ih-NOR-um'),
    'Gru': ('Grus', 'Gruis', 'GROO-iss'),
    'Her': ('Hercules', 'Herculis', 'HER-kyoo-liss'),
    'Hor': ('Horologium', 'Horologii', 'hor-oh-LOH-jee-eye'),
    'Hya': ('Hydra', 'Hydrae', 'HY-dree'),
    'Hyi': ('Hydrus', 'Hydri', 'HY-dry'),
    'Ind': ('Indus', 'Indi', 'IN-dye'),
    'Lac': ('Lacerta', 'Lacertae', 'lah-SIR-tee'),
    'Leo': ('Leo', 'Leonis', 'lee-OH-niss'),
    'LMi': ('Leo Minor', 'Leonis Minoris', 'lee-OH-niss my-NOR-iss'),
    'Lep': ('Lepus', 'Leporis', 'LEP-or-iss'),
    'Lib': ('Libra', 'Librae', 'LY-bree'),
    'Lup': ('Lupus', 'Lupi', 'LOO-pye'),
    'Lyn': ('Lynx', 'Lyncis', 'LIN-siss'),
    'Lyr': ('Lyra', 'Lyrae', 'LY-ree'),
    'Men': ('Mensa', 'Mensae', 'MEN-see'),
    'Mic': ('Microscopium', 'Microscopii', 'my-kroh-SKOH-pee-eye'),
    'Mon': ('Monoceros', 'Monocerotis', 'mon-oh-seh-ROH-tiss'),
    'Mus': ('Musca', 'Muscae', 'MUS-see'),
    'Nor': ('Norma', 'Normae', 'NOR-mee'),
    'Oct': ('Octans', 'Octantis', 'ok-TAN-tiss'),
    'Oph': ('Ophiuchus', 'Ophiuchi', 'off-ee-YOO-kye'),
    'Ori': ('Orion', 'Orionis', 'oh-RY-oh-niss'),
    'Pav': ('Pavo', 'Pavonis', 'pah-VOH-niss'),
    'Peg': ('Pegasus', 'Pegasi', 'PEG-ah-sye'),
    'Per': ('Perseus', 'Persei', 'PER-see-eye'),
    'Phe': ('Phoenix', 'Phoenicis', 'fee-NY-siss'),
    'Pic': ('Pictor', 'Pictoris', 'pik-TOR-iss'),
    'Psc': ('Pisces', 'Piscium', 'PISS-ee-um'),
    'PsA': ('Piscis Austrinus', 'Piscis Austrini', 'PISS-iss aw-STRY-nye'),
    'Pup': ('Puppis', 'Puppis', 'PUP-iss'),
    'Pyx': ('Pyxis', 'Pyxidis', 'PIK-sid-iss'),
    'Ret': ('Reticulum', 'Reticuli', 'reh-TIK-yoo-lye'),
    'Sge': ('Sagitta', 'Sagittae', 'sah-JIT-ee'),
    'Sgr': ('Sagittarius', 'Sagittarii', 'saj-ih-TAIR-ee-eye'),
    'Sco': ('Scorpius', 'Scorpii', 'SKOR-pee-eye'),
    'Scl': ('Sculptor', 'Sculptoris', 'skulp-TOR-iss'),
    'Sct': ('Scutum', 'Scuti', 'SKOO-tye'),
    'Ser': ('Serpens', 'Serpentis', 'sir-PEN-tiss'),
    'Sex': ('Sextans', 'Sextantis', 'sex-TAN-tiss'),
    'Tau': ('Taurus', 'Tauri', 'TOR-eye'),
    'Tel': ('Telescopium', 'Telescopii', 'tel-eh-SKOH-pee-eye'),
    'Tri': ('Triangulum', 'Trianguli', 'try-ANG-yoo-lye'),
    'TrA': ('Triangulum Australe', 'Trianguli Australis', 'try-ANG-yoo-lye aw-STRAL-iss'),
    'Tuc': ('Tucana', 'Tucanae', 'too-KAY-nee'),
    'UMa': ('Ursa Major', 'Ursae Majoris', 'UR-see mah-JOR-iss'),
    'UMi': ('Ursa Minor', 'Ursae Minoris', 'UR-see my-NOR-iss'),
    'Vel': ('Vela', 'Velorum', 'veh-LOR-um'),
    'Vir': ('Virgo', 'Virginis', 'VIR-jin-iss'),
    'Vol': ('Volans', 'Volantis', 'voh-LAN-tiss'),
    'Vul': ('Vulpecula', 'Vulpeculae', 'vul-PEK-yoo-lee'),
}

# ---------------------------------------------------------------------------
# POLISH
# ---------------------------------------------------------------------------
# A Polish recogniser hears Polish. It returns "es es Cygni" where an English
# one returns "ess ess Cygni", "dziewiec przecinek cztery" for 9.4, and the
# constellation in Polish - "SS Labedzia" - as often as in Latin. The Latin
# forms above stay valid in Polish: observers use them constantly. These tables
# are additional, not a replacement.

# Polish names, nominative and genitive. The genitive is what follows the
# variable star letters: "R Andromedy", "SS Labedzia".
CONSTELLATIONS_PL = {
    'And': (u'Andromeda', u'Andromedy'),
    'Ant': (u'Pompa', u'Pompy'),
    'Aps': (u'Ptak Rajski', u'Ptaka Rajskiego'),
    'Aqr': (u'Wodnik', u'Wodnika'),
    'Aql': (u'Orzeł', u'Orła'),
    'Ara': (u'Ołtarz', u'Ołtarza'),
    'Ari': (u'Baran', u'Barana'),
    'Aur': (u'Woźnica', u'Woźnicy'),
    'Boo': (u'Wolarz', u'Wolarza'),
    'Cae': (u'Rylec', u'Rylca'),
    'Cam': (u'Żyrafa', u'Żyrafy'),
    'Cnc': (u'Rak', u'Raka'),
    'CVn': (u'Psy Gończe', u'Psów Gończych'),
    'CMa': (u'Wielki Pies', u'Wielkiego Psa'),
    'CMi': (u'Mały Pies', u'Małego Psa'),
    'Cap': (u'Koziorožec', u'Koziorożca'),
    'Car': (u'Kil', u'Kilu'),
    'Cas': (u'Kasjopeja', u'Kasjopei'),
    'Cen': (u'Centaur', u'Centaura'),
    'Cep': (u'Cefeusz', u'Cefeusza'),
    'Cet': (u'Wieloryb', u'Wieloryba'),
    'Cha': (u'Kameleon', u'Kameleona'),
    'Cir': (u'Cyrkiel', u'Cyrkla'),
    'Col': (u'Gołąb', u'Gołębia'),
    'Com': (u'Warkocz Bereniki', u'Warkocza Bereniki'),
    'CrA': (u'Korona Południowa', u'Korony Południowej'),
    'CrB': (u'Korona Północna', u'Korony Północnej'),
    'Crv': (u'Kruk', u'Kruka'),
    'Crt': (u'Puchar', u'Pucharu'),
    'Cru': (u'Krzyż Południa', u'Krzyża Południa'),
    'Cyg': (u'Łabędź', u'Łabędzia'),
    'Del': (u'Delfin', u'Delfina'),
    'Dor': (u'Złota Ryba', u'Złotej Ryby'),
    'Dra': (u'Smok', u'Smoka'),
    'Equ': (u'Źrebię', u'Źrebięcia'),
    'Eri': (u'Erydan', u'Erydanu'),
    'For': (u'Piec', u'Pieca'),
    'Gem': (u'Bliźnięta', u'Bliźniąt'),
    'Gru': (u'Żuraw', u'Żurawia'),
    'Her': (u'Herkules', u'Herkulesa'),
    'Hor': (u'Zegar', u'Zegara'),
    'Hya': (u'Hydra', u'Hydry'),
    'Hyi': (u'Wąż Wodny', u'Węża Wodnego'),
    'Ind': (u'Indianin', u'Indianina'),
    'Lac': (u'Jaszczurka', u'Jaszczurki'),
    'Leo': (u'Lew', u'Lwa'),
    'LMi': (u'Mały Lew', u'Małego Lwa'),
    'Lep': (u'Zając', u'Zająca'),
    'Lib': (u'Waga', u'Wagi'),
    'Lup': (u'Wilk', u'Wilka'),
    'Lyn': (u'Ryś', u'Rysia'),
    'Lyr': (u'Lutnia', u'Lutni'),
    'Men': (u'Góra Stołowa', u'Góry Stołowej'),
    'Mic': (u'Mikroskop', u'Mikroskopu'),
    'Mon': (u'Jednorożec', u'Jednorożca'),
    'Mus': (u'Mucha', u'Muchy'),
    'Nor': (u'Węgielnica', u'Węgielnicy'),
    'Oct': (u'Oktant', u'Oktantu'),
    'Oph': (u'Wężownik', u'Wężownika'),
    'Ori': (u'Orion', u'Oriona'),
    'Pav': (u'Paw', u'Pawia'),
    'Peg': (u'Pegaz', u'Pegaza'),
    'Per': (u'Perseusz', u'Perseusza'),
    'Phe': (u'Feniks', u'Feniksa'),
    'Pic': (u'Malarz', u'Malarza'),
    'Psc': (u'Ryby', u'Ryb'),
    'PsA': (u'Ryba Południowa', u'Ryby Południowej'),
    'Pup': (u'Rufa', u'Rufy'),
    'Pyx': (u'Kompas', u'Kompasu'),
    'Ret': (u'Siatka', u'Siatki'),
    'Sge': (u'Strzała', u'Strzały'),
    'Sgr': (u'Strzelec', u'Strzelca'),
    'Sco': (u'Skorpion', u'Skorpiona'),
    'Scl': (u'Rzeźbiarz', u'Rzeźbiarza'),
    'Sct': (u'Tarcza', u'Tarczy'),
    'Ser': (u'Wąż', u'Węża'),
    'Sex': (u'Sekstant', u'Sekstantu'),
    'Tau': (u'Byk', u'Byka'),
    'Tel': (u'Teleskop', u'Teleskopu'),
    'Tri': (u'Trójkąt', u'Trójkąta'),
    'TrA': (u'Trójkąt Południowy', u'Trójkąta Południowego'),
    'Tuc': (u'Tukan', u'Tukana'),
    'UMa': (u'Wielka Niedźwiedzica', u'Wielkiej Niedźwiedzicy'),
    'UMi': (u'Mała Niedźwiedzica', u'Małej Niedźwiedzicy'),
    'Vel': (u'Żagiel', u'Żagla'),
    'Vir': (u'Panna', u'Panny'),
    'Vol': (u'Ryba Latająca', u'Ryby Latającej'),
    'Vul': (u'Lisek', u'Liska'),
}

# How the Polish alphabet is said. "W" is "wu", which an English table would
# turn into a U, so these have to be consulted before the English ones.
LETTER_SOUNDS_PL = {
    u'a': 'a', u'be': 'b', u'ce': 'c', u'de': 'd', u'e': 'e', u'ef': 'f',
    u'gie': 'g', u'ha': 'h', u'cha': 'h', u'i': 'i', u'jot': 'j', u'ka': 'k',
    u'el': 'l', u'em': 'm', u'en': 'n', u'o': 'o', u'pe': 'p', u'ku': 'q',
    u'er': 'r', u'es': 's', u'te': 't', u'u': 'u', u'fau': 'v', u'wu': 'w',
    u'vu': 'w', u'iks': 'x', u'igrek': 'y', u'zet': 'z', u'ziet': 'z',
}

NUMBER_WORDS_PL = {
    u'zero': 0, u'jeden': 1, u'jedna': 1, u'dwa': 2, u'dwie': 2, u'trzy': 3,
    u'cztery': 4, u'pięć': 5, u'piec': 5, u'sześć': 6, u'szesc': 6,
    u'siedem': 7, u'osiem': 8, u'dziewięć': 9, u'dziewiec': 9,
    u'dziesięć': 10, u'dziesiec': 10, u'jedenaście': 11, u'jedenascie': 11,
    u'dwanaście': 12, u'dwanascie': 12, u'trzynaście': 13, u'trzynascie': 13,
    u'czternaście': 14, u'czternascie': 14, u'piętnaście': 15, u'pietnascie': 15,
    u'szesnaście': 16, u'szesnascie': 16, u'siedemnaście': 17, u'siedemnascie': 17,
    u'osiemnaście': 18, u'osiemnascie': 18, u'dziewiętnaście': 19,
    u'dziewietnascie': 19, u'dwadzieścia': 20, u'dwadziescia': 20,
    u'trzydzieści': 30, u'trzydziesci': 30, u'czterdzieści': 40,
    u'czterdziesci': 40, u'pięćdziesiąt': 50, u'piecdziesiat': 50,
    u'sześćdziesiąt': 60, u'szescdziesiat': 60, u'siedemdziesiąt': 70,
    u'siedemdziesiat': 70, u'osiemdziesiąt': 80, u'osiemdziesiat': 80,
    u'dziewięćdziesiąt': 90, u'dziewiecdziesiat': 90, u'sto': 100,
}

FIELD_WORDS_PL = {
    u'jasność': 'magnitude', u'jasnosc': 'magnitude',
    u'magnitudo': 'magnitude', u'wielkość': 'magnitude', u'wielkosc': 'magnitude',
    u'porównania': 'comp', u'porownania': 'comp', u'porównawcza': 'comp',
    u'porownawcza': 'comp', u'porównawcze': 'comp', u'porownawcze': 'comp',
    u'kontrolna': 'check', u'kontrolka': 'check',
    u'mapka': 'chart', u'mapa': 'chart', u'sekwencja': 'chart',
    u'niepewność': 'uncertainty', u'niepewnosc': 'uncertainty',
    u'błąd': 'uncertainty', u'blad': 'uncertainty',
    u'filtr': 'band', u'pasmo': 'band',
    u'notatka': 'notes', u'uwaga': 'notes', u'uwagi': 'notes', u'komentarz': 'notes',
    u'słabsza': 'fainter', u'slabsza': 'fainter', u'słabsze': 'fainter',
}

# Dropped from a dictated sentence before anything else is read: Polish needs
# "niż" after "słabsza", and "gwiazda/gwiazdy" is said far more than "star" is.
NOISE_PL = {u'gwiazda', u'gwiazdy', u'gwiazd', u'zmienna', u'zmiennej'}

POLISH_DIACRITICS = {
    u'ą': 'a', u'ć': 'c', u'ę': 'e', u'ł': 'l', u'ń': 'n',
    u'ó': 'o', u'ś': 's', u'ź': 'z', u'ż': 'z',
    u'Ą': 'a', u'Ć': 'c', u'Ę': 'e', u'Ł': 'l', u'Ń': 'n',
    u'Ó': 'o', u'Ś': 's', u'Ź': 'z', u'Ż': 'z',
}


# The spoken name of each letter, for reading a designation to a Polish voice:
# "SS" is "es es", not the English "ess ess" a pl-PL synthesiser would mangle.
LETTER_NAMES_PL = {
    'A': u'a', 'B': u'be', 'C': u'ce', 'D': u'de', 'E': u'e', 'F': u'ef',
    'G': u'gie', 'H': u'ha', 'I': u'i', 'J': u'jot', 'K': u'ka', 'L': u'el',
    'M': u'em', 'N': u'en', 'O': u'o', 'P': u'pe', 'Q': u'ku', 'R': u'er',
    'S': u'es', 'T': u'te', 'U': u'u', 'V': u'fau', 'W': u'wu', 'X': u'iks',
    'Y': u'igrek', 'Z': u'zet',
}


def strip_diacritics(text):
    """Polish without its diacritics, so a missing tail never costs a match.

    Recognisers drop them, keyboards drop them, and "Labedzia" has to reach
    "Łabędzia" either way.
    """
    return ''.join(POLISH_DIACRITICS.get(ch, ch) for ch in (text or ''))


# How a recogniser spells out a letter it heard on its own. Applied only to
# whole tokens, and only inside the star-name part of a sentence, so ordinary
# words elsewhere ("see the chart") are left alone.
LETTER_SOUNDS = {
    'a': 'a', 'ay': 'a', 'eh': 'a',
    'b': 'b', 'bee': 'b', 'be': 'b',
    'c': 'c', 'cee': 'c', 'see': 'c', 'sea': 'c',
    'd': 'd', 'dee': 'd',
    'e': 'e', 'ee': 'e',
    'f': 'f', 'ef': 'f', 'eff': 'f',
    'g': 'g', 'gee': 'g', 'jee': 'g',
    'h': 'h', 'aitch': 'h', 'aych': 'h', 'haych': 'h', 'age': 'h',
    'i': 'i', 'eye': 'i',
    'j': 'j', 'jay': 'j',
    'k': 'k', 'kay': 'k',
    'l': 'l', 'el': 'l', 'ell': 'l',
    'm': 'm', 'em': 'm',
    'n': 'n', 'en': 'n',
    'o': 'o', 'oh': 'o',
    'p': 'p', 'pee': 'p', 'pea': 'p',
    'q': 'q', 'cue': 'q', 'queue': 'q', 'kew': 'q',
    'r': 'r', 'ar': 'r', 'are': 'r',
    's': 's', 'es': 's', 'ess': 's', 'as': 's',
    't': 't', 'tee': 't', 'tea': 't',
    'u': 'u', 'you': 'u', 'yu': 'u', 'ewe': 'u',
    'v': 'v', 'vee': 'v',
    'w': 'w', 'dub': 'w', 'dubya': 'w',
    'x': 'x', 'ex': 'x', 'eks': 'x',
    'y': 'y', 'why': 'y', 'wye': 'y',
    'z': 'z', 'zed': 'z', 'zee': 'z', 'zi': 'z',
}

GREEK = {
    'alpha': 'alpha', 'beta': 'beta', 'gamma': 'gamma', 'delta': 'delta',
    'epsilon': 'epsilon', 'zeta': 'zeta', 'eta': 'eta', 'theta': 'theta',
    'iota': 'iota', 'kappa': 'kappa', 'lambda': 'lambda', 'mu': 'mu',
    'nu': 'nu', 'xi': 'xi', 'omicron': 'omicron', 'pi': 'pi', 'rho': 'rho',
    'sigma': 'sigma', 'tau': 'tau', 'upsilon': 'upsilon', 'phi': 'phi',
    'chi': 'chi', 'psi': 'psi', 'omega': 'omega',
}

GREEK_LETTERS = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
    'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
    'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
    'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron', 'π': 'pi',
    'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
    'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
}

# "chi Cygni" is almost always heard as "kye" or "ki"; these are the misreads
# worth catching rather than a general phonetic model.
GREEK_SOUNDS = {
    'kye': 'chi', 'ki': 'chi', 'kai': 'chi', 'key': 'chi',
    'new': 'nu', 'knew': 'nu', 'mew': 'mu', 'myu': 'mu',
    'row': 'rho', 'roe': 'rho', 'fy': 'phi', 'fie': 'phi', 'figh': 'phi',
    'sy': 'psi', 'sigh': 'psi', 'zy': 'xi', 'zie': 'xi',
    'data': 'theta', 'beata': 'beta', 'bader': 'beta',
}

NUMBER_WORDS = {
    'zero': 0, 'oh': 0, 'one': 1, 'two': 2, 'to': 2, 'too': 2, 'three': 3,
    'four': 4, 'for': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
    'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
    'ninety': 90, 'hundred': 100,
}

# Where the star name stops and the rest of the observation starts.
FIELD_WORDS = {
    'magnitude': 'magnitude', 'mag': 'magnitude', 'brightness': 'magnitude',
    'comparison': 'comp', 'comp': 'comp', 'comps': 'comp',
    'comparisons': 'comp', 'compare': 'comp',
    'check': 'check',
    'chart': 'chart', 'sequence': 'chart',
    'uncertainty': 'uncertainty', 'error': 'uncertainty',
    'band': 'band', 'filter': 'band',
    'note': 'notes', 'notes': 'notes', 'comment': 'notes', 'comments': 'notes',
    'fainter': 'fainter', 'faint': 'fainter',
}

_PUNCT = re.compile(r"[^a-z0-9\s.]+")


def _tokens(text):
    text = strip_diacritics((text or '')).lower().strip()
    for symbol, name in GREEK_LETTERS.items():
        text = text.replace(symbol, ' ' + name + ' ')
    text = text.replace('-', ' ')
    text = _PUNCT.sub(' ', text)
    return [t for t in text.split() if t]


def normalise_name(text):
    """A spoken or written star name reduced to a comparable form.

    Letters said aloud become letters, Greek names are spelled out, and the
    constellation is left as a word so "Cygni", "Cygnus" and "Cyg" can all be
    recognised by the keys generated for the catalogue entry.
    """
    out = []
    tokens = _tokens(text)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        # "double u" and "double you" are one letter said as two words
        if token in ('double', 'dubble') and index + 1 < len(tokens) and \
                tokens[index + 1] in ('u', 'you', 'yu', 'ewe', 'w'):
            out.append('w')
            index += 2
            continue
        if token in ('star', 'variable') or token in _NOISE_PL_PLAIN:
            index += 1
            continue
        if token in _LETTER_SOUNDS_PL_PLAIN:
            out.append(_LETTER_SOUNDS_PL_PLAIN[token])
            index += 1
            continue
        if token in GREEK:
            out.append(token)
        elif token in GREEK_SOUNDS:
            out.append(GREEK_SOUNDS[token])
        elif token in LETTER_SOUNDS:
            out.append(LETTER_SOUNDS[token])
        elif token.isdigit():
            out.append(token)
        else:
            out.append(token)
        index += 1
    return ' '.join(out)


def _clean_designation(designation):
    """Catalogue designations arrive as 'V* SS Cyg'; the prefix is noise."""
    text = (designation or '').strip()
    if text.upper().startswith('V* '):
        text = text[3:].strip()
    for symbol, name in GREEK_LETTERS.items():
        text = text.replace(symbol, name + ' ')
    return ' '.join(text.split())


def split_designation(designation):
    """A designation as (prefix, constellation abbreviation), or (None, None)."""
    parts = _clean_designation(designation).split()
    if len(parts) < 2:
        return None, None
    tail = parts[-1]
    for abbr in CONSTELLATIONS:
        if abbr.lower() == tail.lower():
            return ' '.join(parts[:-1]), abbr
    return None, None


def spoken_keys(name, designation):
    """Every form of one object a person might reasonably say."""
    keys = set()
    for text in (name, _clean_designation(designation)):
        if text:
            keys.add(normalise_name(text))

    prefix, abbr = split_designation(designation)
    if not prefix:
        prefix, abbr = split_designation(name)
    if prefix and abbr:
        nominative, genitive, _ = CONSTELLATIONS[abbr]
        tails = [abbr, nominative, genitive]
        polish = CONSTELLATIONS_PL.get(abbr)
        if polish:
            tails.extend(strip_diacritics(form) for form in polish)
        spoken_prefix = normalise_name(prefix)
        # A two-letter prefix is said both ways: "ess ess" and "SS"
        spaced = ' '.join(spoken_prefix.replace(' ', ''))
        for head in {spoken_prefix, spaced, spoken_prefix.replace(' ', '')}:
            for tail in tails:
                keys.add(normalise_name(head + ' ' + tail))
    return {k for k in keys if k}


def pronounce(name, designation, lang='en'):
    """How to say an object, and how to read it.

    ``say`` is fed to speech synthesis, so the prefix letters are spaced out
    to stop "SS" being read as a word, and the constellation is given in the
    genitive an observer would actually use.
    """
    prefix, abbr = split_designation(designation)
    if not prefix:
        prefix, abbr = split_designation(name)

    # A star with a proper name is called by it. Saying "beta Persei" when the
    # observer said "Algol" would be correct and useless.
    # "SS Cygni" is the designation written out, not a proper name, so it is
    # tested by whether its tail is a constellation rather than by whether it
    # ends in a three-letter abbreviation.
    label = (name or '').strip()
    name_tokens = normalise_name(label).split()
    tail_is_constellation = bool(name_tokens) and \
        resolve_constellation(name_tokens)[0] is not None and \
        resolve_constellation(name_tokens)[1] < len(name_tokens)
    if label and not tail_is_constellation and \
            label.lower() != _clean_designation(designation).lower():
        spoken = {'say': label, 'written': label, 'respell': ''}
        if prefix and abbr:
            formal = pronounce(_clean_designation(designation), designation, lang)
            spoken['also_say'] = formal['say']
            spoken['also_written'] = formal['written']
            spoken['respell'] = formal['respell']
            spoken['constellation'] = formal.get('constellation')
        return spoken

    if not prefix or not abbr:
        label = label or _clean_designation(designation) or ''
        return {'say': label, 'written': label, 'respell': ''}

    nominative, genitive, respell = CONSTELLATIONS[abbr]
    polish = CONSTELLATIONS_PL.get(abbr)
    if lang == 'pl' and polish:
        # Polish observers decline the constellation: "SS Labedzia", not
        # "SS Cygni", and the letters have Polish names of their own.
        nominative, genitive = polish
        respell = genitive

    spoken_prefix = prefix
    if re.fullmatch(r'[A-Za-z]{1,2}', prefix):
        if lang == 'pl':
            spoken_prefix = ' '.join(LETTER_NAMES_PL.get(ch, ch)
                                     for ch in prefix.upper())
            prefix_respell = '-'.join(LETTER_NAMES_PL.get(ch, ch)
                                      for ch in prefix.upper())
        else:
            spoken_prefix = ' '.join(prefix.upper())
            prefix_respell = '-'.join(prefix.upper())
    elif prefix.lower() in GREEK:
        prefix_respell = prefix.lower()
    else:
        prefix_respell = prefix
    return {
        'say': '%s %s' % (spoken_prefix, genitive),
        'written': '%s %s' % (prefix, genitive),
        'respell': '%s %s' % (prefix_respell, respell),
        'constellation': nominative,
    }


def _sound_key(word):
    """A crude phonetic form, enough to see past a recogniser's spelling.

    "Cygni" heard as "signee" is the normal case, not an edge case: the
    constellation genitives are Latin and the recogniser is guessing English.
    Comparing sound rather than letters is what lets those meet.
    """
    text = word.lower().replace('ph', 'f').replace('ch', 'k').replace('qu', 'kw')
    out = []
    for index, letter in enumerate(text):
        following = text[index + 1] if index + 1 < len(text) else ''
        if letter == 'c':
            out.append('s' if following in 'eiy' else 'k')
        elif letter in 'yj':
            out.append('i')
        elif letter == 'z':
            out.append('s')
        else:
            out.append(letter)
    text = ''.join(out).replace('ae', 'e').replace('oe', 'e')
    squeezed = []
    for letter in text:
        if not squeezed or squeezed[-1] != letter:
            squeezed.append(letter)
    return ''.join(squeezed)


_LETTER_SOUNDS_PL_PLAIN = {strip_diacritics(k): v for k, v in LETTER_SOUNDS_PL.items()}
_NOISE_PL_PLAIN = {strip_diacritics(w) for w in NOISE_PL}
_NUMBER_WORDS_PL_PLAIN = {strip_diacritics(k): v for k, v in NUMBER_WORDS_PL.items()}
_FIELD_WORDS_PL_PLAIN = {strip_diacritics(k): v for k, v in FIELD_WORDS_PL.items()}

_CONSTELLATION_SOUNDS = {}
for _abbr, (_nom, _gen, _resp) in CONSTELLATIONS.items():
    _forms = [_abbr, _nom, _gen]
    _pl = CONSTELLATIONS_PL.get(_abbr)
    if _pl:
        _forms.extend(strip_diacritics(form) for form in _pl)
    for _form in _forms:
        _CONSTELLATION_SOUNDS.setdefault(_sound_key(_form.replace(' ', '')), set()).add(_abbr)


def resolve_constellation(tokens):
    """Which constellation the tail of a spoken name refers to.

    Returns (abbreviation, tokens consumed, score). Two tokens are tried first
    so "Canis Minoris" and "Ursae Majoris" are not read as "Minoris" alone.
    """
    best = (None, 0, 0.0)
    for take in (1, 2, 3):
        if len(tokens) < take:
            continue
        sound = _sound_key(''.join(tokens[-take:]))
        exact = _CONSTELLATION_SOUNDS.get(sound)
        if exact:
            return sorted(exact)[0], take, 1.0
        for key, abbrs in _CONSTELLATION_SOUNDS.items():
            ratio = difflib.SequenceMatcher(None, sound, key).ratio()
            # Strictly greater, so a tie keeps the shorter tail: squashing the
            # prefix into the constellation ("s s signee" as one word) scores
            # the same as the constellation alone and must not win.
            if ratio > best[2]:
                best = (sorted(abbrs)[0], take, ratio)
    if best[2] >= 0.78:
        return best
    return None, 0, best[2]


def resolve_star(text, candidates, limit=5):
    """Resolve a spoken star name, saying how it was resolved.

    Separating this from the ranking matters for one case: a designation that
    parses cleanly but is not in the catalogue. Offering the nearest other star
    would quietly file the observation against the wrong object, so that case
    is reported as a miss with the designation that was understood.
    """
    heard = normalise_name(text)
    out = {'heard': heard, 'designation': None, 'constellation': None,
           'in_catalogue': False, 'matches': [], 'suggestions': []}
    if not heard:
        return out

    tokens = heard.split()
    abbr, taken, _ = resolve_constellation(tokens)
    if abbr and 0 < taken < len(tokens):
        prefix = ''.join(tokens[:-taken])
        if re.fullmatch(r'[a-z]{1,2}\d*|v\d+|[a-z]+', prefix):
            out['constellation'] = abbr
            out['designation'] = '%s %s' % (prefix.upper(), abbr)

    ranked = match_object(text, candidates, limit=limit)
    certain = ranked and ranked[0]['score'] >= 0.999

    # Two things are being separated here. ``matches`` is what the form may be
    # filled from; ``suggestions`` is what to offer the observer to choose.
    # A designation that parses cleanly but is absent from the catalogue -
    # "RR Lyr" when only RR Hya is held - must never be silently filed against
    # the nearest other star, so it yields no match at all.
    if out['designation'] and not certain:
        out['suggestions'] = ranked
        return out

    if certain:
        out['in_catalogue'] = True
        out['matches'] = [m for m in ranked if m['score'] >= 0.999]
        out['suggestions'] = [m for m in ranked if m['score'] < 0.999]
        if not out['designation']:
            out['designation'] = _clean_designation(
                out['matches'][0].get('designation')) or out['matches'][0].get('name')
    elif ranked and ranked[0]['score'] >= 0.85:
        out['matches'] = ranked[:1]
        out['suggestions'] = ranked[1:]
        out['in_catalogue'] = True
    else:
        out['suggestions'] = ranked
    return out


def match_object(text, candidates, limit=5):
    """Rank catalogue objects against a spoken name.

    Candidates are dicts with id/name/designation. The result is always drawn
    from them, so a wrong answer is a real star rather than an invention.
    """
    heard = normalise_name(text)
    if not heard:
        return []
    squashed = heard.replace(' ', '')

    # Structured first: a designation that resolves letter-for-letter beats any
    # amount of fuzzy similarity, and tells us when the star is simply absent
    # from the catalogue rather than merely hard to hear.
    exact = []
    tokens = heard.split()
    abbr, taken, _ = resolve_constellation(tokens)
    if abbr and taken < len(tokens):
        prefix = ''.join(tokens[:-taken])
        wanted = ('%s %s' % (prefix, abbr)).lower()
        for candidate in candidates:
            designation = _clean_designation(candidate.get('designation')) or candidate.get('name') or ''
            if designation.lower() == wanted:
                exact.append(candidate)
        if exact:
            return [{'id': c.get('id'), 'name': c.get('name'),
                     'designation': c.get('designation'), 'score': 1.0}
                    for c in exact[:limit]]

    scored = []
    for candidate in candidates:
        best = 0.0
        for key in candidate.get('keys') or spoken_keys(candidate.get('name'),
                                                        candidate.get('designation')):
            if key == heard or key.replace(' ', '') == squashed:
                best = 1.0
                break
            ratio = difflib.SequenceMatcher(None, heard, key).ratio()
            squeeze = difflib.SequenceMatcher(None, squashed, key.replace(' ', '')).ratio()
            best = max(best, ratio, squeeze)
        if best > 0.55:
            scored.append((best, candidate))

    scored.sort(key=lambda row: (-row[0], row[1].get('name') or ''))
    return [{'id': c.get('id'), 'name': c.get('name'),
             'designation': c.get('designation'),
             'score': round(score, 3)} for score, c in scored[:limit]]


def _number_word(token):
    """A spoken number in either language, or None."""
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    return _NUMBER_WORDS_PL_PLAIN.get(token)


def _number_from_words(tokens):
    """Spoken digits or number words to a value, with the AAVSO shorthand.

    Observers read a magnitude as "nine point four", as "nine four", and often
    as "ninety four" meaning 9.4 - a bare integer far too large to be a
    magnitude is read as tenths rather than rejected.
    """
    if not tokens:
        return None, False
    tokens = [t for t in tokens if t not in ('przecinek', 'kropka')] or tokens
    joined = ' '.join(tokens)
    direct = re.fullmatch(r'(\d+(?:\.\d+)?)', joined.replace(' ', ''))
    if direct and '.' in direct.group(1):
        return float(direct.group(1)), False

    words = []
    for token in tokens:
        if token in ('point', 'dot', 'przecinek', 'kropka'):
            words.append('.')
        elif token.isdigit():
            words.append(token)
        elif token in NUMBER_WORDS or token in _NUMBER_WORDS_PL_PLAIN:
            words.append(str(_number_word(token)))
        else:
            break
    if not words:
        return None, False

    if '.' in words:
        split = words.index('.')
        whole = ''.join(words[:split]) or '0'
        frac = ''.join(words[split + 1:]) or '0'
        try:
            return float('%s.%s' % (int(whole), frac)), False
        except ValueError:
            return None, False

    # "twenty one" is 20 + 1, but "nine four" is the digits 9 and 4
    numbers = [int(w) for w in words]
    if len(numbers) == 2 and numbers[0] >= 20 and numbers[0] % 10 == 0 and numbers[1] < 10:
        value = numbers[0] + numbers[1]
    else:
        value = int(''.join(words))

    if value > 30:               # no star anyone reports visually is this faint
        return value / 10.0, True
    return float(value), False


def parse_observation(text, candidates=None):
    """Pull an observation out of one spoken sentence.

    The star name is whatever comes before the first field word, which is what
    keeps "comp 95 and 102" from being read as part of a name containing "And".
    """
    tokens = _tokens(text)
    result = {
        'heard': (text or '').strip(),
        'star_phrase': '',
        'magnitude': None,
        'magnitude_assumed_tenths': False,
        'uncertainty': None,
        'comparisons': [],
        'check': None,
        'chart': None,
        'band': None,
        'fainter_than': False,
        'notes': None,
        'matches': [],
        'suggestions': [],
        'designation': None,
        'in_catalogue': False,
        'unparsed': [],
    }

    sections = []
    current = ('star', [])
    for token in tokens:
        field = FIELD_WORDS.get(token) or _FIELD_WORDS_PL_PLAIN.get(token)
        if field:
            sections.append(current)
            current = (field, [])
        else:
            current[1].append(token)
    sections.append(current)

    for field, words in sections:
        if not words and field != 'fainter':
            continue
        if field == 'star':
            result['star_phrase'] = ' '.join(words)
        elif field == 'magnitude':
            value, assumed = _number_from_words(words)
            if value is not None:
                result['magnitude'] = value
                result['magnitude_assumed_tenths'] = assumed
        elif field == 'uncertainty':
            value, _ = _number_from_words(words)
            if value is not None:
                result['uncertainty'] = value
        elif field == 'fainter':
            result['fainter_than'] = True
            rest = [w for w in words if w not in ('than', 'niz', 'od')]
            value, assumed = _number_from_words(rest)
            if value is not None and result['magnitude'] is None:
                result['magnitude'] = value
                result['magnitude_assumed_tenths'] = assumed
        elif field == 'comp':
            result['comparisons'] = _labels(words)
        elif field == 'check':
            labels = _labels(words)
            result['check'] = labels[0] if labels else None
        elif field == 'chart':
            result['chart'] = _chart_id(words)
        elif field == 'band':
            result['band'] = (words[0] or '').upper()[:3] if words else None
        elif field == 'notes':
            result['notes'] = ' '.join(words)

    if result['star_phrase'] and candidates:
        resolved = resolve_star(result['star_phrase'], candidates)
        result['matches'] = resolved['matches']
        result['suggestions'] = resolved['suggestions']
        result['designation'] = resolved['designation']
        result['in_catalogue'] = resolved['in_catalogue']

    return result


# "and", and its Polish equivalents, between two chart labels. They are tested
# before the letter tables, since "i" is also a letter.
_LABEL_SEPARATORS = {'and', 'i', 'oraz', 'plus'}


def _labels(words):
    """Comparison and check stars are chart labels: '95', '102', 'A'.

    A label said as a whole number comes back as one token ("102"), while one
    said digit by digit comes back as several ("one oh two"). So single digits
    are joined and anything longer stands on its own - otherwise "85 and 102"
    collapses into the single nonexistent label 85102.
    """
    out = []
    pending = []

    def flush():
        if pending:
            out.append(''.join(pending))
            del pending[:]

    for token in words:
        digits = None
        if token.isdigit():
            digits = token
        elif _number_word(token) is not None:
            digits = str(_number_word(token))

        if token in _LABEL_SEPARATORS:
            flush()
        elif digits is not None and len(digits) > 1:
            flush()
            out.append(digits)
        elif digits is not None:
            pending.append(digits)
        else:
            flush()
            if len(token) <= 2 and token.isalpha():
                out.append(token.upper())
    flush()
    return out


def _chart_id(words):
    """AAVSO chart ids are said letter by letter: 'X one two three four five A B'."""
    out = []
    for token in words:
        if token.isdigit():
            out.append(token)
        elif _number_word(token) is not None:
            out.append(str(_number_word(token)))
        elif token in _LETTER_SOUNDS_PL_PLAIN:
            out.append(_LETTER_SOUNDS_PL_PLAIN[token].upper())
        elif token in LETTER_SOUNDS:
            out.append(LETTER_SOUNDS[token].upper())
        elif token.isalnum():
            out.append(token.upper())
    return ''.join(out) or None
