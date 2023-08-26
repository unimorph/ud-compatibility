from collections import namedtuple
from typing import List


class LanguageCoding(namedtuple("LanguageCoding", "ud um name")):
    __slots__ = ()


_languages = [
    # These are needed to provide paths to the datasets.
    #  - The two-letter helps identify the UD filename.
    #  - The three-letter helps identify the UniMorph folder and filename.
    #  - The full name identifies the UD folder and the Translator object.
    # (ISO 693-1 (usually), ISO 693-3, English name)
    ("ar", "ara", "Arabic"),
    ("eu", "eus", "Basque"),
    ("bg", "bul", "Bulgarian"),
    ("ca", "cat", "Catalan"),
    ("cs", "ces", "Czech"),
    ("da", "dan", "Danish"),
    ("nl", "nld", "Dutch"),
    ("en", "eng", "English"),
    ("fi", "fin", "Finnish"),
    ("fr", "fra", "French"),
    ("de", "deu", "German"),
    ("he", "heb", "Hebrew"),
    ("hi", "hin", "Hindi"),
    ("hu", "hun", "Hungarian"),
    ("ga", "gle", "Irish"),
    ("it", "ita", "Italian"),
    ("la", "lat", "Latin"),
    ("lv", "lav", "Latvian"),
    ("lt", "lit", "Lithuanian"),
    ("no_bokmaal", "nob", "Norwegian-Bokmaal"),
    ("no_nynorsk", "nno", "Norwegian-Nynorsk"),
    ("fa", "fas", "Persian"),
    ("pl", "pol", "Polish"),
    ("pt", "por", "Portuguese"),
    ("ro", "ron", "Romanian"),
    ("ru", "rus", "Russian"),
    ("sl", "slv", "Slovenian"),
    ("es", "spa", "Spanish"),
    ("sv", "swe", "Swedish"),
    ("tr", "tur", "Turkish"),
    ("uk", "ukr", "Ukrainian"),
    ("ur", "urd", "Urdu"),
]


languages: List[LanguageCoding] = [LanguageCoding._make(l) for l in _languages]


def get_lang(needle: str) -> LanguageCoding:
    for language in languages:
        if needle == language.ud:
            return language
    else:
        raise KeyError(needle)
