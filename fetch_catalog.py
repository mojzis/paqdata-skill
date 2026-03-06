#!/usr/bin/env python3
"""
Fetch the complete DataPAQ variable catalog from api.datapaq.cz/variables.
Outputs a compact JSON index file that Claude Code can search through
to find relevant variables and construct datapaq.cz URLs.

Usage:
    python fetch_catalog.py                    # Save to datapaq_catalog.json
    python fetch_catalog.py --output my.json   # Custom output path
    python fetch_catalog.py --search "poverty"  # Fetch + search immediately
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.datapaq.cz"
VARIABLES_URL = f"{API_BASE}/variables"


def fetch_all_variables():
    """Fetch all pages of /variables and return the complete list."""
    all_variables = []
    url = VARIABLES_URL
    page = 1

    while url:
        print(f"Fetching page {page}...", file=sys.stderr)
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            break

        all_variables.extend(data.get("results", []))
        url = data.get("next")
        page += 1

    print(f"Fetched {len(all_variables)} variables total.", file=sys.stderr)
    return all_variables


def build_catalog(raw_variables):
    """
    Transform raw API response into a compact, searchable catalog.
    Each entry has everything needed to construct a datapaq.cz URL.
    """
    catalog = []
    for v in raw_variables:
        # Extract compact variant info
        variants = []
        for var in v.get("variants", []):
            variants.append({
                "key": var["key"],
                "name": var["name"],
                "type_key": var["values_type_key"],
                "period": var["period_key"],
                "data_type": var["type"],  # numerical_integer, numerical_decimal, categorical
                "granularities": var["available_granularities"],
                "visible": var.get("visible_in_picker", "not_visible") != "not_visible",
                # For categorical variables, include the label mapping
                **({"labels": var["display_categorical_labels"]}
                   if var.get("display_categorical_labels") else {}),
            })

        catalog.append({
            "id": v["id"],
            "key": v["key"],
            "name": v["name"],
            "description": _strip_html(v.get("description", "")),
            "sources": v.get("sources_rendered", v.get("sources", [])),
            "categories": v.get("categories", []),
            "visible": v.get("visible_in_picker", "not_visible") != "not_visible",
            "variants": variants,
        })

    return catalog


def _strip_html(text):
    """Remove HTML tags for cleaner text search."""
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def search_catalog(catalog, query, limit=20):
    """
    Search the catalog by keyword (case-insensitive, matches key, name, description).
    Returns matching variables sorted by relevance.
    """
    query_lower = query.lower()
    terms = query_lower.split()

    results = []
    for var in catalog:
        searchable = f"{var['key']} {var['name']} {var['description']}".lower()
        # Score: how many search terms match
        score = sum(1 for t in terms if t in searchable)
        # Bonus for key match
        if query_lower in var["key"].lower():
            score += 3
        # Bonus for name match
        if query_lower in var["name"].lower():
            score += 2
        # Bonus for visible variables
        if var["visible"]:
            score += 0.5

        if score > 0:
            results.append((score, var))

    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results[:limit]]


def print_variable(var, verbose=False):
    """Pretty-print a variable entry."""
    vis = "✓" if var["visible"] else "·"
    print(f"  {vis} {var['key']}")
    print(f"    {var['name']}")
    if verbose and var["description"]:
        desc = var["description"][:200]
        print(f"    {desc}{'...' if len(var['description']) > 200 else ''}")

    # Show available granularities and periods
    granularities = set()
    periods = []
    for v in var["variants"]:
        granularities.update(v["granularities"])
        if v["visible"]:
            periods.append(v["period"])
    print(f"    Granularities: {', '.join(sorted(granularities))}")
    if periods:
        print(f"    Periods: {', '.join(periods[:8])}{'...' if len(periods) > 8 else ''}")
    print()


def build_url(variable_key, period=None, granularity=None,
              variable2_key=None, period2=None,
              filter_code=None, vis=None):
    """
    Construct a datapaq.cz URL from variable parameters.

    Args:
        variable_key: Primary variable key (e.g. 'hustota_zalidneni')
        period: Period key for v1 (e.g. '2024')
        granularity: Geographic level ('obec', 'orp', 'okres', 'kraj')
        variable2_key: Optional second variable key
        period2: Period key for v2
        filter_code: Optional filter code (e.g. '3202' for a region)
        vis: Visualization type ('table', 'scatterplot', 'barchart', 'linechart')

    Returns:
        Complete datapaq.cz URL string
    """
    params = []
    if granularity:
        params.append(f"g={granularity}")
    params.append(f"v1={variable_key}")
    if period:
        params.append(f"v1p={period}")
    if variable2_key:
        params.append(f"v2={variable2_key}")
        if period2:
            params.append(f"v2p={period2}")
    if filter_code:
        params.append(f"fc={filter_code}")
    if vis:
        params.append(f"vis={vis}")

    return f"https://datapaq.cz/?{'&'.join(params)}"


def main():
    parser = argparse.ArgumentParser(description="DataPAQ variable catalog tool")
    parser.add_argument("--output", "-o", default="datapaq_catalog.json",
                        help="Output path for the catalog JSON")
    parser.add_argument("--search", "-s", help="Search for variables matching this query")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show descriptions in search results")
    parser.add_argument("--load", "-l", help="Load existing catalog instead of fetching")
    parser.add_argument("--list-categories", action="store_true",
                        help="List all category IDs found in the catalog")
    args = parser.parse_args()

    # Load or fetch catalog
    if args.load:
        with open(args.load) as f:
            catalog = json.load(f)
        print(f"Loaded {len(catalog)} variables from {args.load}", file=sys.stderr)
    else:
        raw = fetch_all_variables()
        catalog = build_catalog(raw)
        # Save catalog
        with open(args.output, "w") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        print(f"Saved catalog to {args.output}", file=sys.stderr)

    if args.list_categories:
        cats = {}
        for var in catalog:
            for c in var["categories"]:
                if c not in cats:
                    cats[c] = []
                cats[c].append(var["key"])
        print("\nCategories:")
        for cid in sorted(cats.keys()):
            examples = cats[cid][:3]
            print(f"  [{cid}] ({len(cats[cid])} vars) e.g. {', '.join(examples)}")
        return

    if args.search:
        results = search_catalog(catalog, args.search)
        if results:
            print(f"\nFound {len(results)} matches for '{args.search}':\n")
            for var in results:
                print_variable(var, verbose=args.verbose)
        else:
            print(f"No matches for '{args.search}'")
        return

    # Default: print summary
    visible = [v for v in catalog if v["visible"]]
    print(f"\nCatalog summary:")
    print(f"  Total variables: {len(catalog)}")
    print(f"  Visible in picker: {len(visible)}")
    granularity_counts = {"obec": 0, "orp": 0, "okres": 0, "kraj": 0, "stat": 0}
    for var in catalog:
        for v in var["variants"]:
            for g in v["granularities"]:
                if g in granularity_counts:
                    granularity_counts[g] += 1
    print(f"  Variants by granularity: {granularity_counts}")


if __name__ == "__main__":
    main()
