#!/usr/bin/env python3
"""
compare_models.py

Fetch active (non-deprecated, non-withdrawn) Watsonx foundation models
from multiple regions, then display:

 1. Active model counts per region
 2. Which models are missing (per region) compared to US-South
 3. Which models are unique to each region
 4. Models common to all regions
 5. A master list of all models and the regions (short codes) in which each appears
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Set, List, Any

import requests

try:
    from tabulate import tabulate
except ImportError:
    print("ERROR: This script requires the 'tabulate' library.\n"
          "Install with: pip install tabulate")
    sys.exit(1)


# ——— Configuration ————————————————————————————————————————————————

BASE_URLS = [
    "https://us-south.ml.cloud.ibm.com",
    "https://eu-de.ml.cloud.ibm.com",
    "https://jp-tok.ml.cloud.ibm.com",
    "https://au-syd.ml.cloud.ibm.com",
]

ENDPOINT = "/ml/v1/foundation_model_specs"
PARAMS = {
    "version": "2024-09-16",
    "filters": "function_embedding,!lifecycle_withdrawn"
}
TODAY = datetime.today().strftime("%Y-%m-%d")

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


# ——— Helpers ———————————————————————————————————————————————————

def is_deprecated_or_withdrawn(lifecycle: List[Dict[str, Any]]) -> bool:
    for entry in lifecycle:
        if entry.get("id") in {"deprecated", "withdrawn"} and entry.get("start_date", "") <= TODAY:
            return True
    return False


def fetch_active_models() -> Dict[str, Set[str]]:
    """Fetch and return a mapping of region → active model_ids."""
    model_sets: Dict[str, Set[str]] = {}
    for base in BASE_URLS:
        url = f"{base}{ENDPOINT}"
        logging.info("Fetching from %s", url)
        try:
            resp = requests.get(url, params=PARAMS, timeout=10)
            resp.raise_for_status()
            resources = resp.json().get("resources", [])
            active = {
                m["model_id"]
                for m in resources
                if not is_deprecated_or_withdrawn(m.get("lifecycle", []))
            }
            model_sets[base] = active
            logging.info(" → %d active models", len(active))
        except requests.RequestException as e:
            logging.error("Failed to fetch from %s: %s", base, e)
            model_sets[base] = set()
    return model_sets


# ——— Printing ——————————————————————————————————————————————————

def print_region_summary(model_sets: Dict[str, Set[str]]):
    rows = [
        [url.split("//")[1].split(".")[0], len(models)]
        for url, models in model_sets.items()
    ]
    print("\nActive Models per Region:")
    print(tabulate(rows, headers=["Region", "Count"], tablefmt="github"))


def print_pairwise_list(title: str, data: Dict[str, List[str]]):
    """
    Print a two-column table of (Region, Model ID) for each entry in data.
    If no entries exist, print a placeholder line.
    """
    print(f"\n{title}:")
    rows = []
    for region, models in data.items():
        short = region.split("//")[1].split(".")[0]
        for m in models:
            rows.append([short, m])
    if rows:
        print(tabulate(rows, headers=["Region", "Model ID"], tablefmt="github"))
    else:
        print("  — None —")


def print_common_models(common: List[str]):
    print("\nModels present in ALL regions:")
    if common:
        for m in common:
            print(f"  • {m}")
    else:
        print("  — None —")


def print_model_regions(model_sets: Dict[str, Set[str]]):
    """
    Print a table listing every model and the short region codes
    in which it appears.
    """
    model_to_regions: Dict[str, List[str]] = {}
    for base, models in model_sets.items():
        short = base.split("//")[1].split(".")[0]
        for m in models:
            model_to_regions.setdefault(m, []).append(short)

    rows = [
        [model, ", ".join(sorted(regions))]
        for model, regions in sorted(model_to_regions.items())
    ]
    print("\nAll Models and Their Regions (short codes):")
    print(tabulate(rows, headers=["Model ID", "Regions"], tablefmt="github"))


# ——— Comparisons ——————————————————————————————————————————————

def compare_to_reference(
    model_sets: Dict[str, Set[str]], ref_region: str
) -> (Dict[str, List[str]], Dict[str, List[str]], List[str]):
    ref = model_sets.get(ref_region, set())
    missing = {
        base: sorted(ref - models)
        for base, models in model_sets.items()
        if base != ref_region
    }
    unique = {
        base: sorted(models - ref)
        for base, models in model_sets.items()
        if base != ref_region
    }
    common = sorted(set.intersection(*model_sets.values()))
    return missing, unique, common


# ——— Main Entry Point ——————————————————————————————————————

def main():
    logging.info("Starting comparison tool")
    model_sets = fetch_active_models()

    # 1) Active model counts
    print_region_summary(model_sets)

    # 2–4) Pairwise vs US-South
    ref = "https://us-south.ml.cloud.ibm.com"
    missing, unique, common = compare_to_reference(model_sets, ref)

    print_pairwise_list(
        f"Models in {ref.split('//')[1].split('.')[0]} but MISSING elsewhere", missing
    )
    print_pairwise_list(
        f"Models UNIQUE to each region (not in {ref.split('//')[1].split('.')[0]})", unique
    )
    print_common_models(common)

    # 5) Master list of all models and their regions (short codes)
    print_model_regions(model_sets)

    logging.info("Done.")


if __name__ == "__main__":
    main()
