# easybib

[![Tests](https://github.com/GregoryAshton/easybib/actions/workflows/tests.yml/badge.svg)](https://github.com/GregoryAshton/easybib/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/GregoryAshton/easybib/branch/main/graph/badge.svg)](https://codecov.io/gh/GregoryAshton/easybib)

Automatically fetch BibTeX entries from [INSPIRE](https://inspirehep.net/), [NASA/ADS](https://ui.adsabs.harvard.edu/), and [Semantic Scholar](https://www.semanticscholar.org/) for LaTeX projects.

easybib scans your `.tex` files for citation keys, looks them up on INSPIRE, ADS, and/or Semantic Scholar, and writes a `.bib` file with the results. It handles INSPIRE texkeys (e.g. `Author:2020abc`), ADS bibcodes (e.g. `2016PhRvL.116f1102A`), and arXiv IDs (e.g. `2508.18080`).

## Installation

```bash
pip install easybib
```

## Usage

```bash
easybib /path/to/latex/project
easybib paper.tex
```

Pass a directory to scan all `.tex` files recursively, or a single `.tex` file. BibTeX entries are fetched and written to `references.bib`.

### Options

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output BibTeX file (default: `references.bib`) |
| `-s`, `--preferred-source` | Preferred source: `ads` (default), `inspire`, `auto`, or `semantic-scholar` |
| `-a`, `--max-authors` | Truncate author lists (default: 3, use 0 for no limit) |
| `-l`, `--list-keys` | List found citation keys and exit (no fetching) |
| `--fresh` | Ignore existing output file and start from scratch |
| `--ads-api-key` | ADS API key (overrides `ADS_API_KEY` environment variable) |
| `--semantic-scholar-api-key` | Semantic Scholar API key (overrides `SEMANTIC_SCHOLAR_API_KEY` environment variable) |
| `--config` | Path to config file (default: `~/.easybib.config`) |

### Examples

```bash
# Scan a directory
easybib ./paper --preferred-source inspire

# Scan a single file
easybib paper.tex

# Use a custom output file
easybib ./paper -o paper.bib

# List citation keys without fetching
easybib ./paper -l

# Keep all authors
easybib ./paper -a 0
```

### Config file

You can create a config file at `~/.easybib.config` to set persistent defaults, so you don't have to pass the same flags every time:

```ini
[easybib]
output = references.bib
max-authors = 3
preferred-source = ads
ads-api-key = your-key-here
semantic-scholar-api-key = your-key-here
```

All fields are optional. CLI flags override config file values, which override the built-in defaults.

To use a config file at a different location:

```bash
easybib ./paper --config /path/to/my.config
```

### Source selection

The `--preferred-source` flag controls where BibTeX entries are fetched from. The source determines which service provides the BibTeX data, regardless of the key format used in your `.tex` files.

- **`ads`** (default) — Fetches BibTeX from ADS. If you use an INSPIRE-style key (e.g. `Author:2020abc`), easybib will cross-reference it via INSPIRE to find the corresponding ADS record, then pull the BibTeX from ADS. Falls back to INSPIRE, then Semantic Scholar, if ADS lookup fails.
- **`inspire`** — Fetches BibTeX from INSPIRE. Falls back to ADS, then Semantic Scholar, if the INSPIRE lookup fails. Does not require an ADS API key unless the fallback is triggered.
- **`auto`** — Chooses the source based on the key format: ADS bibcodes (e.g. `2016PhRvL.116f1102A`) are fetched from ADS, while INSPIRE-style keys are fetched from INSPIRE. Falls back to the other source, then Semantic Scholar, if the preferred one fails.
- **`semantic-scholar`** — Fetches BibTeX from Semantic Scholar first, falling back to INSPIRE then ADS. Does not require an ADS API key unless the fallback is triggered.

### arXiv IDs as citation keys

You can cite papers directly by their arXiv ID:

```latex
\cite{2508.18080}
```

easybib fetches the BibTeX entry from your preferred source (searching by arXiv ID) and writes two entries to the `.bib` file: the full entry under its natural citation key, plus a `@misc` stub so that `\cite{2508.18080}` resolves correctly:

```bibtex
@article{LIGOScientific:2025hdt,
  author = {Abbott, R. and others},
  title  = {...},
  ...
}

@misc{2508.18080,
  crossref = {LIGOScientific:2025hdt}
}
```

Both the new-style format (`2508.18080`) and the old-style format (`hep-ph/9905318`) are supported.

### ADS API key

When using ADS as the source (the default), provide your API key either via the command line:

```bash
easybib ./paper --ads-api-key your-key-here
```

Or as an environment variable:

```bash
export ADS_API_KEY="your-key-here"
```

Get a key from https://ui.adsabs.harvard.edu/user/settings/token.

### Semantic Scholar API key

Semantic Scholar's API works without a key but is rate-limited. For heavier use, provide an API key either via the command line:

```bash
easybib ./paper --semantic-scholar-api-key your-key-here
```

Or as an environment variable:

```bash
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"
```

Get a key from https://www.semanticscholar.org/product/api.

## How it works

1. Scans `.tex` files for `\cite{...}`, `\citep{...}`, `\citet{...}`, and related commands
2. Accepts INSPIRE texkeys (`Author:2020abc`), ADS bibcodes (`2016PhRvL.116f1102A`), and arXiv IDs (`2508.18080` or `hep-ph/9905318`); warns and skips anything else
3. Fetches BibTeX from the preferred source, with automatic fallback
4. For INSPIRE/ADS keys: replaces the citation key to match what is in your `.tex` file
5. For arXiv IDs: keeps the entry's natural key and appends a `@misc` crossref stub so `\cite{arxiv_id}` resolves correctly
6. Truncates long author lists
7. Skips keys already present in the output file (use `--fresh` to override)
