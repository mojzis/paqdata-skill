---
name: datapaq
description: >
  Construct datapaq.cz URLs to visualize Czech socioeconomic data on interactive maps.
  Use this skill whenever the user wants to look up, compare, or visualize Czech regional
  statistics — demographics, education, poverty, elections, housing, employment, social
  services, municipal finance — at the municipality (obec), ORP, district (okres), or
  region (kraj) level. Also triggers on mentions of DataPAQ, PAQ Research, Czech regional
  data, "mapa vzdělávání", or any request to show Czech data on a map. The API at
  api.datapaq.cz provides 781 variables. This skill helps you pick the right variable
  keys and construct working URLs.
---

# DataPAQ — Constructing Map URLs for Czech Regional Data

DataPAQ (datapaq.cz) by PAQ Research visualizes 781 socioeconomic indicators across
Czech municipalities, districts, and regions. This skill helps you **find the right
variables and build working URLs** that open specific data views on the map.

## Step 1: Search the Variable Catalog

A pre-built catalog of all variables is bundled at `data/datapaq_catalog.json`
(relative to this skill's directory). Use the bundled script to search it:

```bash
# Search by topic
python /path/to/this/skill/scripts/fetch_catalog.py --load /path/to/this/skill/data/datapaq_catalog.json --search "population density"
python /path/to/this/skill/scripts/fetch_catalog.py --load /path/to/this/skill/data/datapaq_catalog.json --search "chudoba"
python /path/to/this/skill/scripts/fetch_catalog.py --load /path/to/this/skill/data/datapaq_catalog.json --search "volby elections"

# List all categories
python /path/to/this/skill/scripts/fetch_catalog.py --load /path/to/this/skill/data/datapaq_catalog.json --list-categories
```

To refresh the catalog from the API (if variables have been added or changed):

```bash
python /path/to/this/skill/scripts/fetch_catalog.py
```

This fetches all pages of `https://api.datapaq.cz/variables` and overwrites
`data/datapaq_catalog.json`.

## Step 2: Construct the URL

### URL Format

All DataPAQ views are encoded as query parameters on a single page:

```
https://datapaq.cz/?g={granularity}&v1={variable_key}&v1p={period}[&v2=...&v2p=...][&fc={filter}][&vis={type}]
```

### Parameters

| Param | Required | Description | Values |
|-------|----------|-------------|--------|
| `g` | No (defaults to orp) | Geographic level | `obec`, `orp`, `okres`, `kraj` |
| `v1` | **Yes** | Primary variable key | Any `key` from the API |
| `v1p` | Recommended | Period for v1 | Period key from variant, e.g. `2024`, `2022-2023` |
| `v1t` | No | Value subtype for v1 | `hodnoty`, `pasma`, `kapacita_sluzeb`, etc. |
| `v2` | No | Second variable (enables comparison) | Same as v1 |
| `v2p` | If v2 set | Period for v2 | Same as v1p |
| `v2t` | No | Value subtype for v2 | Same as v1t |
| `v3` | No | Third variable | Same as v1 |
| `v3p` | If v3 set | Period for v3 | Same as v1p |
| `fc` | No | Filter: area code(s) | Dash-separated codes, e.g. `3202` or `542105-542431` |
| `ft` | No | Filter type | `obec`, `kraj`, `variable` |
| `fmk` | No | Filter by categorical variable | Variable key |
| `vis` | No | Visualization | `table`, `scatterplot`, `barchart`, `linechart` |
| `b_sortby` | No | Sort column | Column name |
| `t_sortdir` | No | Sort direction | `asc`, `desc` |

### Worked Examples

**Example 1: Two variables on a municipality map, filtered to Brno**
```
https://datapaq.cz/?g=obec&v1=hustota_zalidneni&v1p=2024&v2=vystehovali&v2p=2024&fc=582786
```
- `g=obec` → municipality level
- `v1=hustota_zalidneni` → population density
- `v1p=2024` → year 2024
- `v2=vystehovali` → out-migration
- `v2p=2024` → year 2024
- `fc=582786` → filter to Brno (look up codes in `data/area_codes.json`)

**Example 2: Poverty index across all ORP microregions**
```
https://datapaq.cz/?g=orp&v1=dest_chudoba&v1t=hodnoty&v1p=2025
```

**Example 3: Poverty vs. educational failure scatterplot**
```
https://datapaq.cz/?g=orp&v1=dest_chudoba&v1t=hodnoty&v1p=2025&v2=vzdel_neuspesnost__kvintily_2021&vis=scatterplot
```

**Example 4: Table of specific municipalities**
```
https://datapaq.cz/?g=obec&v1=pocet_obyvatel&v1p=2023&ft=obec&fc=542105-542431-532177&vis=table
```

**Example 5: Children in housing need by district**
```
https://datapaq.cz/?g=okres&v1=podil_deti_v_bytove_nouzi_2022_vyber&v1p=2022
```

## Step 3: Validate Before Sharing

Before sharing a URL, verify:

1. **Variable key exists** — check it's in the catalog
2. **Period is valid** — the variable's variants must include that period_key
3. **Granularity is available** — check `available_granularities` in the variant
4. **Two-variable URLs** — both variables must be available at the same granularity

If a variable only has ORP-level data, don't use `g=obec`.

---

## Reference: Geographic Granularities

| Code | Czech | Count | Description |
|------|-------|-------|-------------|
| `obec` | Obec | ~6,258 | Municipalities (most granular) |
| `orp` | ORP | 206 | Microregions (default, analytically richest) |
| `okres` | Okres | 77 | Districts |
| `kraj` | Kraj | 14 | Regions (broadest) |
| `stat` | Stát | 1 | Whole country |

## Reference: Filter Codes (`fc`)

Filter codes are **Czech administrative area numeric codes** from the ČSÚ
classification system (CISOB codelist). A bundled lookup file is available at
`data/area_codes.json` (relative to this skill's directory) containing all codes
for obec (6,258), ORP (206), okres (77), and kraj (14).

Examples:
- `582786` — obec Brno
- `542105` — obec Olomouc

Multiple codes are dash-separated: `fc=582786-542105`.

## Reference: Period Key Patterns

| Pattern | Example | Meaning |
|---------|---------|---------|
| `YYYY` | `2024` | Calendar year |
| `YYYY-YYYY` | `2022-2023` | School year or range |
| `mesic-YYYY` | `leden-2024` | Specific month (Czech month names) |
| `YYYY-YYYY_avg` | `2020-2022_avg` | Multi-year average |
| `MM_YYYY` | `01_2026` | Month/year compact format |

Czech month names: leden, únor, březen, duben, květen, červen,
červenec, srpen, září, říjen, listopad, prosinec.

## Reference: Value Types (`v1t`)

| Key | Use for |
|-----|---------|
| `hodnoty` | Raw numeric values or index scores (default, most common) |
| `pasma` | Expert categorical bands (1–5: velmi nízká → velmi vysoká) |
| `kapacita_sluzeb` | Service capacity (beds/places) |
| `pocet_organizaci` | Organization/facility count |
| `podilObci` | Share of municipalities (%) |
| `podilOsob` | Share of persons (%) |

Most variables default to `hodnoty` — you can usually omit `v1t`.

## Reference: Common Variable Keys (Sample — ~50 of 781)

### Demographics
| Key | Name | Granularities |
|-----|------|---------------|
| `pocet_obyvatel` | Population | obec → stat |
| `hustota_zalidneni` | Population density | obec → stat |
| `celkovy_prirustek` | Total population change | obec → stat |
| `celkovy_prirustek_na_1000_obyvatel` | Pop. change per 1,000 | obec → stat |
| `pristehovali` | In-migration | obec → stat |
| `vystehovali` | Out-migration | obec → stat |
| `zive_narozeni` | Live births | obec → stat |

### Poverty & Social Conditions
| Key | Name | Granularities |
|-----|------|---------------|
| `dest_chudoba` | Destabilising poverty index | orp → stat |
| `podil_deti_v_bytove_nouzi_2022_vyber` | Children in housing need | orp → stat |
| `podil_deti_v_azylovych_domech_a_ubytovnach` | Children in shelters | orp → stat |
| `podil_deti_v_prelidnenych_bytech` | Children in overcrowded flats | orp → stat |

### Education
| Key | Name | Granularities |
|-----|------|---------------|
| `vzdel_neuspesnost__kvintily_2021` | Educational failure quintiles | orp |
| `podil_zaku_se_svp` | Pupils with special needs | orp → stat |
| `podil_skol_bez_psychologa` | Schools without psychologist | orp → stat |
| `deti_2lete_v_ms` | 2-year-olds in kindergarten | orp → stat |
| `deti_3-5let_v_ms` | 3-5yr-olds in kindergarten | orp → stat |

### Employment (Census 2021)
| Key | Name | Granularities |
|-----|------|---------------|
| `zamestnani_celkem` | Total employed | obec → stat |
| `PrcTrhStruc_PrumyslZemedelstviStavebnictvi` | % in industry/agriculture | obec → stat |
| `PrcTrhStruc_SluzbyPokrocile` | % in advanced services | obec → stat |
| `PrcTrhStruc_SluzbyZakladni` | % in basic services | obec → stat |

### Elections
| Key | Name | Granularities |
|-----|------|---------------|
| `volby_prez2023_1kolo_total_hlasu` | Votes, pres. 2023 round 1 | orp → stat |
| `volby_prez2023_2kolo_total_hlasu` | Votes, pres. 2023 round 2 | orp → stat |

### Housing & Finance
| Key | Name | Granularities |
|-----|------|---------------|
| `najemni_ceny_paq25` | 25th pctl rental prices | okres |
| `celkove_danove_prijmy_obci` | Municipal tax revenues | obec → stat |
| `RUD_prijmy_obci_naOsobu` | RUD tax per capita | obec → stat |

### Social Services
| Key | Name | Granularities |
|-----|------|---------------|
| `azylove_domy` | Shelters | obec → stat |
| `denni_sluzby` | Day service centres | obec → stat |
| `chranene_bydleni` | Supported housing | obec → stat |

**⚠ This is only ~50 of 781 variables.** Always run `fetch_catalog.py` or paginate
through the API to find the exact variable you need. Topics not listed here include:
crime, health, detailed party election results, school funding per pupil, commuting,
age structure, detailed social benefits, and many more.

---

## Python Helper

The `build_url()` function in `scripts/fetch_catalog.py` can construct URLs:

```python
from scripts.fetch_catalog import build_url

url = build_url(
    variable_key="hustota_zalidneni",
    period="2024",
    granularity="obec",
    variable2_key="vystehovali",
    period2="2024",
    filter_code="582786"
)
# → https://datapaq.cz/?g=obec&v1=hustota_zalidneni&v1p=2024&v2=vystehovali&v2p=2024&fc=582786
```

## Data Sources

ČSÚ (statistics), MŠMT (education), MPSV (labour), MF ČR (finance), ČŠI (school
inspection), Exekutorská komora (executors), ASZ (social inclusion), Úřad práce
(labour office), SLDB 2021 (census), PAQ Research (composite indices).
