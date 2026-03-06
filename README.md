# paqdata-skill

A [Claude Code custom skill](https://docs.anthropic.com/en/docs/claude-code/skills) that helps construct [datapaq.cz](https://datapaq.cz) URLs for visualizing Czech socioeconomic data on interactive maps.

[DataPAQ](https://datapaq.cz) by [PAQ Research](https://www.paqresearch.cz/) provides 781 variables covering demographics, education, poverty, elections, housing, employment, social services, municipal finance, and more — at municipality (`obec`), microregion (`orp`), district (`okres`), and region (`kraj`) level.

## What this skill does

When installed in Claude Code, the skill teaches Claude how to:

1. **Find variables** — search through the 781-variable catalogue by topic or keyword
2. **Build valid URLs** — construct `datapaq.cz` query strings with the correct parameter format
3. **Validate parameters** — check that variable keys, periods, and granularities are compatible

## Installation

Copy (or symlink) the `.claude/skills/paqdata` directory into your project's `.claude/skills/` folder. Claude Code will pick it up automatically.

## The variable catalogue

The skill includes a Python script that downloads and indexes the full variable catalogue from the DataPAQ API.

The catalogue is pre-built and committed at `.claude/skills/paqdata/data/datapaq_catalog.json`.

### Search for variables

```bash
SKILL=.claude/skills/paqdata

# By topic keyword
python3 $SKILL/scripts/fetch_catalog.py --load $SKILL/data/datapaq_catalog.json --search "chudoba"
python3 $SKILL/scripts/fetch_catalog.py --load $SKILL/data/datapaq_catalog.json --search "population"

# With descriptions
python3 $SKILL/scripts/fetch_catalog.py --load $SKILL/data/datapaq_catalog.json --search "exekuce" -v

# List all categories
python3 $SKILL/scripts/fetch_catalog.py --load $SKILL/data/datapaq_catalog.json --list-categories
```

### Refresh the catalogue

If new variables have been added to the API:

```bash
python3 .claude/skills/paqdata/scripts/fetch_catalog.py
```

This fetches all pages from `https://api.datapaq.cz/variables` and overwrites the bundled catalogue.

## URL format

All DataPAQ map views are encoded as query parameters:

```
https://datapaq.cz/?g={granularity}&v1={variable_key}&v1p={period}[&v2=...&v2p=...][&fc={filter}][&vis={type}]
```

Key parameters:

| Param | Description |
|-------|-------------|
| `g` | Geographic level: `obec`, `orp` (default), `okres`, `kraj` |
| `v1` | Primary variable key |
| `v1p` | Period for v1 (e.g. `2024`, `2022-2023`) |
| `v2`, `v2p` | Optional second variable + period (enables comparison) |
| `fc` | Filter by area code (Czech administrative codes) |
| `vis` | Visualization: `table`, `scatterplot`, `barchart`, `linechart` |

## Examples

### 1. Child poverty index across microregions

Show the destabilising poverty index (`dest_chudoba`) at ORP level:

```
https://datapaq.cz/?g=orp&v1=dest_chudoba&v1t=hodnoty&v1p=2025
```

This opens a choropleth map coloring all 206 Czech microregions by their poverty index score.

### 2. Population density vs. out-migration, filtered to Brno

Compare two variables at the municipality level, filtered to a specific city:

```
https://datapaq.cz/?g=obec&v1=hustota_zalidneni&v1p=2024&v2=vystehovali&v2p=2024&fc=582786
```

- `g=obec` — municipality-level granularity
- `v1=hustota_zalidneni` — population density
- `v2=vystehovali` — out-migration count
- `fc=582786` — filter to Brno (codes are in `.claude/skills/paqdata/data/area_codes.json`)

### 3. Education failure vs. poverty as a scatterplot

Plot two indicators against each other to explore their relationship:

```
https://datapaq.cz/?g=orp&v1=dest_chudoba&v1t=hodnoty&v1p=2025&v2=vzdel_neuspesnost__kvintily_2021&vis=scatterplot
```

Each dot is one ORP microregion. The x-axis shows poverty, the y-axis shows educational failure quintiles.

## Geographic granularities

| Code | Czech | Count | Description |
|------|-------|-------|-------------|
| `obec` | Obec | ~6,258 | Municipalities |
| `orp` | ORP | 206 | Microregions (default, analytically richest) |
| `okres` | Okres | 77 | Districts |
| `kraj` | Kraj | 14 | Regions |

## Data sources

ČSÚ (statistics), MŠMT (education), MPSV (labour), MF ČR (finance), ČŠI (school inspection), Exekutorská komora, ASZ (social inclusion), Úřad práce, SLDB 2021 (census), PAQ Research (composite indices).
