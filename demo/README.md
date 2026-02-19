# easybib demo

This directory contains a minimal working example of easybib.

## Files

| File | Description |
|------|-------------|
| `paper.tex` | A short LaTeX document citing some papers |
| `easybib.config` | Config file setting preferred source and author limit |

`paper.tex` demonstrates all three supported citation key formats:

- **INSPIRE texkey** — `LIGOScientific:2016aoc`
- **ADS bibcode** — `2025ApJ...995L..18A`
- **arXiv ID** — `2508.18080`

## Running the demo

From this directory:

```bash
easybib paper.tex --config easybib.config
```

This will fetch BibTeX entries from INSPIRE (no API key required) and write
them to `references.bib`.

For the arXiv ID (`2508.18080`), easybib writes two entries: the full BibTeX
record under its natural citation key, plus a `@misc` crossref stub so that
`\cite{2508.18080}` resolves correctly in LaTeX:

```bibtex
@article{LIGOScientific:2025hdt,
  ...
}

@misc{2508.18080,
  crossref = {LIGOScientific:2025hdt}
}
```

## Config file

`easybib.config` sets:

```ini
[easybib]
preferred-source = inspire   # no ADS API key needed
max-authors = 5              # truncate long author lists
output = references.bib
```

You can override any setting on the command line, e.g.:

```bash
# Use ADS instead (requires ADS_API_KEY)
easybib paper.tex --config easybib.config --preferred-source ads

# Keep all authors
easybib paper.tex --config easybib.config --max-authors 0

# Write to a different file
easybib paper.tex --config easybib.config -o my_refs.bib
```

## Compiling the paper

Once `references.bib` has been generated:

```bash
pdflatex paper
bibtex paper
pdflatex paper
pdflatex paper
```
