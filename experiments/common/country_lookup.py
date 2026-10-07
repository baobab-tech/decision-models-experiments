"""Country-name lookup for excerpt geography (the same rule as experiments/02-fine-tuning/train_encoder.py, which
keeps its own copy so HF Jobs can run it as a single file).

Searches the excerpt, title and Document Start of a `doc_summary` input (not the summaries, which mention
comparison and donor countries). Needs pycountry.
"""

from __future__ import annotations

import re

CONTEXT_HEADING = "## CONTEXT SECTIONS"

COUNTRY_ALIASES = {  # names pycountry does not list, or lists differently
    "vietnam": "VN", "tanzania": "TZ", "bolivia": "BO", "laos": "LA", "lao pdr": "LA", "syria": "SY", "iran": "IR",
    "russia": "RU", "south korea": "KR", "north korea": "KP", "moldova": "MD", "drc": "CD", "dr congo": "CD",
    "democratic republic of the congo": "CD", "republic of congo": "CG", "côte d'ivoire": "CI", "cote d'ivoire": "CI",
    "ivory coast": "CI", "palestine": "PS", "gaza": "PS", "west bank": "PS", "uk": "GB", "united kingdom": "GB",
    "usa": "US", "united states": "US", "venezuela": "VE", "turkey": "TR", "türkiye": "TR", "czech republic": "CZ",
    "kyrgyzstan": "KG", "cape verde": "CV", "eswatini": "SZ", "swaziland": "SZ", "burma": "MM", "myanmar": "MM",
    "macedonia": "MK", "kosovo": "XK", "micronesia": "FM", "taiwan": "TW", "the gambia": "GM", "gambia": "GM",
}



def country_lookup():
    """Returns a function: input text -> set of ISO alpha-2 codes."""
    import pycountry
    names = {n.lower(): c.alpha_2 for c in pycountry.countries
             for n in {c.name, getattr(c, "common_name", None), getattr(c, "official_name", None)} - {None}}
    names.update(COUNTRY_ALIASES)
    pat = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b", re.I)

    def find(input_text: str) -> set[str]:
        i = input_text.find(CONTEXT_HEADING)
        excerpt, context = (input_text, "") if i < 0 else (input_text[:i], input_text[i:])
        text = excerpt + "\n" + context.split("### Executive Summary")[0].split("### Abstract")[0]
        return {names[m.group(1).lower()] for m in pat.finditer(text)}
    return find
