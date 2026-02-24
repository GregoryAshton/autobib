"""BibTeX string transformations."""

import re


def replace_bibtex_key(bibtex, new_key):
    """Replace the citation key in a BibTeX entry with a new key."""
    # Match the entry type and key: @article{old_key,
    pattern = r"(@\w+\s*\{)\s*([^,\s]+)\s*,"
    return re.sub(pattern, rf"\g<1>{new_key},", bibtex, count=1)


def extract_bibtex_fields(bibtex, *field_names):
    """Extract field values from a BibTeX entry string.

    Returns a dict mapping field name to value for each field found.
    Handles both double-quoted and brace-delimited values.
    """
    result = {}
    for field in field_names:
        pattern = rf'^\s*{re.escape(field)}\s*=\s*(?:"([^"]+)"|\{{([^}}]+)\}})'
        match = re.search(pattern, bibtex, re.MULTILINE | re.IGNORECASE)
        if match:
            result[field] = (match.group(1) or match.group(2)).strip()
    return result


def extract_bibtex_key(bibtex):
    """Extract the citation key from a BibTeX entry string."""
    match = re.search(r'@\w+\s*\{\s*([^,\s]+)\s*,', bibtex)
    if match:
        return match.group(1)
    return None


def make_arxiv_crossref_stub(arxiv_id, bibtex_key):
    """Create a BibTeX @misc entry that cross-references the main entry."""
    return f"@misc{{{arxiv_id},\n  crossref = {{{bibtex_key}}}\n}}"


def parse_aas_macros(sty_content):
    """Parse AAS macro definitions from .sty file content.

    Returns a dict mapping macro name (without backslash) to its journal string.
    For example: {'apj': 'ApJ', 'mnras': 'MNRAS', ...}
    """
    macros = {}

    # Match \def\macroname{\ref@jnl{value}}
    for match in re.finditer(r'\\def\\(\w+)\{\\ref@jnl\{([^}]+)\}\}', sty_content):
        macros[match.group(1)] = match.group(2)

    # Match alias definitions like \def\alias{\original} or \let\alias\original
    for match in re.finditer(r'\\(?:def|let)\\(\w+)[{ \\]\\(\w+)[}]?', sty_content):
        alias, original = match.group(1), match.group(2)
        if alias not in macros and original in macros:
            macros[alias] = macros[original]

    return macros


def find_used_macros(bibtex_text, macros):
    """Find which AAS macros are used in the given BibTeX text.

    macros: dict mapping macro name (without backslash) to journal string.
    Returns a dict of {macro_name: journal_string} for macros that appear in the text.
    """
    used = {}
    for name, value in macros.items():
        # Match \macroname not immediately followed by another word character
        if re.search(r'\\' + re.escape(name) + r'(?!\w)', bibtex_text):
            used[name] = value
    return used


def expand_aas_macros(bibtex, macros):
    """Expand AAS journal macros inline in a BibTeX string.

    Replaces occurrences of \\macroname (not followed by a word character)
    with their plain-text expansion. For example, {\\apj} becomes {ApJ}.
    """
    for name, value in macros.items():
        bibtex = re.sub(r'\\' + re.escape(name) + r'(?!\w)', value, bibtex)
    return bibtex


def truncate_authors(bibtex, max_authors):
    """Truncate the author list in a BibTeX entry to max_authors.

    If there are more than max_authors, keep the first max_authors and add "and others".
    If max_authors is None or 0, no truncation is performed.
    """
    if not max_authors:
        return bibtex

    # Match the author field (handles multiline author fields)
    author_pattern = r"(\s*author\s*=\s*\{)(.+?)(\},?\s*\n)"
    match = re.search(author_pattern, bibtex, re.IGNORECASE | re.DOTALL)

    if not match:
        return bibtex

    prefix = match.group(1)
    authors_str = match.group(2)
    suffix = match.group(3)

    # Split authors by " and " (BibTeX standard separator)
    authors = [a.strip() for a in re.split(r"\s+and\s+", authors_str)]

    if len(authors) <= max_authors:
        return bibtex

    # Keep first max_authors and add "others"
    truncated_authors = authors[:max_authors] + ["others"]
    new_authors_str = " and ".join(truncated_authors)

    # Replace the author field
    new_author_field = f"{prefix}{new_authors_str}{suffix}"
    return bibtex[: match.start()] + new_author_field + bibtex[match.end() :]
