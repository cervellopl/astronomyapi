# -*- coding: utf-8 -*-
"""
Interface language.

Translations are keyed on the English text itself rather than on symbolic ids.
The templates here are generated, so a key like ``nav.observations`` would have
to be invented and kept in step by hand for every string; keying on the English
means an untranslated string still renders as readable English instead of as a
missing key, and adding a language is adding a dictionary.

``translate`` is exposed to templates as ``_()``.
"""

LANGUAGES = [
    ('en', 'English'),
    ('pl', 'Polski'),
]

DEFAULT_LANGUAGE = 'en'

# Speech recognition and synthesis take BCP 47, not our two-letter codes.
SPEECH_LOCALES = {'en': 'en-GB', 'pl': 'pl-PL'}

PL = {
    # Navigation
    'Dashboard': 'Pulpit',
    'Observations': 'Obserwacje',
    'Objects': 'Obiekty',
    'Sessions': 'Sesje',
    'Instruments': 'Instrumenty',
    'Places': 'Miejsca',
    'Weather': 'Pogoda',
    'Sky History': 'Historia nieba',
    'Sky Map': 'Mapa nieba',
    'Saying Star Names': 'Wymowa nazw gwiazd',
    'Visibility Chart': 'Wykres widoczności',
    'Types': 'Typy',
    'Properties': 'Właściwości',
    'Search': 'Szukaj',
    'Settings': 'Ustawienia',
    'Backup': 'Kopia zapasowa',
    'Logout': 'Wyloguj',
    'Login': 'Zaloguj',
    'Observing Plans': 'Plany obserwacyjne',
    'Comets': 'Komety',
    'Import': 'Import',
    'Export': 'Eksport',
    'API Docs': 'Dokumentacja API',

    'Main': 'G\u0142\u00f3wne',
    'Data': 'Dane',
    'Tools': 'Narz\u0119dzia',
    'Account': 'Konto',
    'Backup &amp; Restore': 'Kopia i przywracanie',
    'Import Comets': 'Import komet',
    'Submit to AAVSO': 'Wy\u015blij do AAVSO',

    'Planning': 'Planowanie',
    'Path Chart': 'Mapa drogi',

    # Common actions
    'Save': 'Zapisz',
    'Save Observation': 'Zapisz obserwację',
    'Cancel': 'Anuluj',
    'Delete': 'Usuń',
    'Edit': 'Edytuj',
    'Add': 'Dodaj',
    'Back': 'Powrót',
    'Close': 'Zamknij',
    'Refresh now': 'Odśwież teraz',
    'Open': 'Otwórz',
    'Sites': 'Miejsca',
    'New observation': 'Nowa obserwacja',
    'Add New Observation': 'Nowa obserwacja',
    'Edit Observation': 'Edycja obserwacji',
    'Observation Details': 'Szczegóły obserwacji',

    # Observation form
    'Object': 'Obiekt',
    'Date & Time (UTC)': 'Data i godzina (UTC)',
    'Universal Time (UTC)': 'Czas uniwersalny (UTC)',
    'Place': 'Miejsce',
    'Instrument': 'Instrument',
    'Session': 'Sesja',
    'Notes': 'Notatki',
    'Magnitude': 'Jasność',
    'Uncertainty': 'Niepewność',
    'Comp Star 1': 'Gwiazda porównania 1',
    'Comp Star 2': 'Gwiazda porównania 2',
    'Check Star': 'Gwiazda kontrolna',
    'Chart ID': 'Numer mapki',
    'Visual magnitude': 'Jasność wizualna',
    'Chart label': 'Oznaczenie na mapce',
    'Type to search...': 'Wpisz, aby wyszukać...',
    'Comparison stars on chart': 'Gwiazdy porównania na mapce',

    # Voice
    'Dictate': 'Dyktuj',
    'Listening': 'Słucham',
    'Read back': 'Czytaj zwrotnie',
    'Saying star names': 'Wymowa nazw gwiazd',
    'Your stars': 'Twoje gwiazdy',
    'Constellations': 'Gwiazdozbiory',
    'Designation': 'Oznaczenie',
    'Name': 'Nazwa',
    'Say it': 'Wymowa',
    'Hear it': 'Posłuchaj',
    'Abbr': 'Skrót',
    'Constellation': 'Gwiazdozbiór',
    'Genitive': 'Dopełniacz',
    'field(s) filled': 'pole(a) wypełnione',
    'is not in your catalogue': 'nie ma w Twoim katalogu',
    'add it': 'dodaj',
    'Did you mean': 'Czy chodziło o',
    'Or': 'Albo',
    'Microphone permission was refused.': 'Odmówiono dostępu do mikrofonu.',
    'This browser has no speech recognition - Chrome or Edge does.':
        'Ta przeglądarka nie rozpoznaje mowy - Chrome lub Edge tak.',
    'Could not reach the parser.': 'Brak połączenia z analizatorem.',
    'Say it in one go: "SS Cygni magnitude nine point four comparison 95 and 102"':
        'Powiedz jednym ciągiem: "SS Łabędzia jasność dziewięć przecinek cztery porównania 95 i 102"',
    'Listening - say the star, then the magnitude and comparisons.':
        'Słucham - podaj gwiazdę, potem jasność i gwiazdy porównania.',

    'magnitude': 'jasno\u015b\u0107',
    'fainter than': 's\u0142absza ni\u017c',
    'comparison': 'por\u00f3wnania',
    'check': 'kontrolna',
    'and': 'i',
    'I did not catch the star': 'Nie rozpozna\u0142em gwiazdy',

    'The browser only allows the microphone over HTTPS.':
        'Przegl\u0105darka udost\u0119pnia mikrofon wy\u0142\u0105cznie przez HTTPS.',
    'Open this page over HTTPS': 'Otw\u00f3rz t\u0119 stron\u0119 przez HTTPS',
    'accept the certificate warning once': 'raz zaakceptuj ostrze\u017cenie o certyfikacie',

    # Weather
    'Default site': 'Domyślne miejsce',
    'Meteosat Third Generation': 'Meteosat trzeciej generacji',
    'Meteosat Second Generation': 'Meteosat drugiej generacji',
    'Day by day': 'Dzień po dniu',
    'Weather station': 'Stacja pogodowa',
    'Other services': 'Pozostałe serwisy',
    'Temp min': 'Temp. min',
    'Temp max': 'Temp. maks',
    'Wind max': 'Wiatr maks',
    'Gust max': 'Porywy maks',
    'Rain': 'Opad',
    'temperature': 'temperatura',
    'dew point': 'punkt rosy',
    'wind': 'wiatr',
    'gusts': 'porywy',
    'rain rate': 'natężenie opadu',
    'pressure': 'ciśnienie',
    'astronomical night': 'noc astronomiczna',

    # Sky statistics
    'Monthly and yearly statistics': 'Statystyki miesi\u0119czne i roczne',
    'Months': 'Miesi\u0105ce',
    'Years': 'Lata',
    'Period': 'Okres',
    'Clear': 'Pogodnie',
    'Dark hours': 'Godziny ciemne',
    'Clear hours': 'Godziny pogodne',
    'Nights': 'Noce',
    'With clear': 'Z przeja\u015bnieniem',
    'Usable': 'U\u017cyteczne',
    'Best night': 'Najlepsza noc',
    'Coverage': 'Pokrycie',
    'clear dark hours': 'godziny pogodne i ciemne',
    'cloudy dark hours': 'godziny ciemne z chmurami',
    'usable nights': 'noce u\u017cyteczne',
    'No sky record yet.': 'Brak jeszcze zapisu nieba.',
    'Dark means the Sun below -18 degrees. A night counts as usable with at least an hour of clear dark sky. Coverage is how much of the period the collector actually recorded - a month with low coverage is not a cloudy month, it is a missing one.':
        'Ciemno oznacza S\u0142o\u0144ce poni\u017cej -18 stopni. Noc jest u\u017cyteczna, gdy mia\u0142a co najmniej godzin\u0119 pogodnego ciemnego nieba. Pokrycie m\u00f3wi, jak\u0105 cz\u0119\u015b\u0107 okresu kolektor rzeczywi\u015bcie zapisa\u0142 - miesi\u0105c o niskim pokryciu nie jest miesi\u0105cem pochmurnym, tylko brakuj\u0105cym.',

    'Mean': '\u015arednia',
    'Pressure min': 'Ci\u015bnienie min',
    'Pressure max': 'Ci\u015bnienie maks',
    'Max rate': 'Maks. nat\u0119\u017cenie',
    'wet days': 'dni z opadem',
    'No station readings yet.': 'Brak jeszcze odczyt\u00f3w ze stacji.',

    # Dashboard / statistics
    'Observing statistics': 'Statystyka obserwacji',
    'Variable stars': 'Gwiazdy zmienne',
    'Variable Star': 'Gwiazda zmienna',
    'Comet': 'Kometa',
    'Star': 'Gwiazda',
    'Galaxy': 'Galaktyka',
    'Planet': 'Planeta',
    'Other': 'Inne',
    'Clear & dark': 'Czysto i ciemno',
    'Longest clear spell': 'Najdłuższe przejaśnienie',
    'Nights with any clear': 'Noce z przejaśnieniami',
    'Your observations': 'Twoje obserwacje',

    # Settings
    'Language': 'Język',
    'Interface language': 'Język interfejsu',
    'Profile': 'Profil',
    'Username': 'Nazwa użytkownika',
    'Email': 'E-mail',
    'Save Settings': 'Zapisz ustawienia',
    'Settings updated successfully!': 'Ustawienia zapisane!',
    'The language of the interface, and the one speech recognition listens for.':
        'Język interfejsu oraz język rozpoznawania mowy.',
}

CATALOGUES = {'pl': PL}


def available():
    return LANGUAGES


def normalise(code):
    code = (code or '').strip().lower()[:2]
    return code if code in dict(LANGUAGES) else DEFAULT_LANGUAGE


def speech_locale(code):
    return SPEECH_LOCALES.get(normalise(code), SPEECH_LOCALES[DEFAULT_LANGUAGE])


def translate(text, lang=None):
    """The text in ``lang``, or the English it was given back unchanged."""
    if not text:
        return text
    catalogue = CATALOGUES.get(normalise(lang))
    if not catalogue:
        return text
    return catalogue.get(text, text)


def catalogue(lang):
    """The whole dictionary, for the browser to translate its own strings."""
    return CATALOGUES.get(normalise(lang)) or {}


def coverage():
    """How much of each catalogue is filled in, for the settings page."""
    return {code: len(entries) for code, entries in CATALOGUES.items()}
