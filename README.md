# paqdata-skill

A [Claude Code custom skill](https://docs.anthropic.com/en/docs/claude-code/skills) that helps you explore Czech socioeconomic data on [datapaq.cz](https://datapaq.cz) interactive maps.

[DataPAQ](https://datapaq.cz) by [PAQ Research](https://www.paqresearch.cz/) provides 781 variables covering demographics, education, poverty, elections, housing, employment, social services, municipal finance, and more — at municipality, microregion, district, and region level.

## Installation

Copy (or symlink) the `.claude/skills/paqdata` directory into your project's `.claude/skills/` folder. Claude Code will pick it up automatically.

## What you can ask

Once installed, just ask Claude Code questions about Czech regional data in natural language. The skill will find the right variables and give you a clickable datapaq.cz link.

**Compare regions:**
- "Show me child poverty across Czech microregions"
- "Compare population density and out-migration for municipalities near Holice"
- "Which districts have the highest share of people in debt execution?"

**Look up a specific place:**
- "Show me education data for Brno"
- "What does the poverty index look like in okres Beroun?"

**Explore relationships:**
- "Is there a correlation between poverty and educational failure across Czech regions?"
- "Plot rental prices vs. unemployment as a scatterplot"

**Get tables:**
- "Give me a table of all municipalities in ORP Pardubice with their population"

The skill knows all 781 variables, 6,258 municipality codes, and the full URL format — so you don't have to.

## Example output

Ask: *"Show me child poverty across Czech microregions"*

Claude will return a link like:
```
https://datapaq.cz/?g=orp&v1=dest_chudoba&v1t=hodnoty&v1p=2025
```
Click it to open an interactive choropleth map on datapaq.cz.

## What's inside

- `SKILL.md` — instructions that teach Claude the URL format, parameters, and validation rules
- `data/datapaq_catalog.json` — full catalogue of 781 variables from the DataPAQ API
- `data/area_codes.json` — all Czech administrative area codes (obec, ORP, okres, kraj)
- `scripts/fetch_catalog.py` — script to refresh the catalogue or search it from the command line

## Data sources

ČSÚ, MŠMT, MPSV, MF ČR, ČŠI, Exekutorská komora, ASZ, Úřad práce, SLDB 2021 (census), PAQ Research.
