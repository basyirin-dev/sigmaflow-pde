#!/usr/bin/env python3
"""Create the OSF project shell for σFlow-PDE pre-registration pipeline.

Usage:
    export OSF_TOKEN=your_token_here
    python scripts/setup_osf.py

Requires: requests (pip install requests)
"""

import os
import sys
import json
import yaml
from pathlib import Path

import requests

# ── Configuration ──────────────────────────────────────────────────────────────

API = "https://api.osf.io/v2"

# Load .env from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
dotenv_path = REPO_ROOT / ".env"
if dotenv_path.exists():
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

TOKEN = os.getenv("OSF_TOKEN")
if not TOKEN:
    print("❌ OSF_TOKEN environment variable not set.")
    print("   Run: export OSF_TOKEN=your_token_here")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/vnd.api+json",
}

ROOT_TITLE = "σFlow-PDE: H-Bar Phase Engine for Compositional Neural Operators"
COMPONENTS = [
    "01_Preregistration",
    "02_Code_Materials",
    "03_Data_Benchmark",
    "04_Analysis_Falsification",
    "05_Manuscript_Docs",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIGS_DIR = REPO_ROOT / "configs"
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────


def create_node(title: str, parent_id: str | None = None) -> str:
    """Create an OSF node (project or component). Returns the node ID (e.g. 'abc12').

    Note: OSF API v2 accepts only 'project' (or other legacy values like 'hypothesis',
    'method', etc.) as category. Child nodes are just nested projects.
    """
    data = {
        "data": {
            "type": "nodes",
            "attributes": {
                "title": title,
                "category": "project",
                "public": True,
            },
        }
    }
    if parent_id:
        url = f"{API}/nodes/{parent_id}/children/"
    else:
        url = f"{API}/nodes/"

    resp = requests.post(url, json=data, headers=HEADERS)
    if resp.status_code == 409:
        # Node may already exist — try to look it up by title
        print(f"  ⚠  409 Conflict for '{title}' (may already exist). Skipping.")
        return _find_node_id(title, parent_id)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def _find_node_id(title: str, parent_id: str | None = None) -> str:
    """Search for an existing node by title."""
    params = {"filter[title]": title}
    if parent_id:
        url = f"{API}/nodes/{parent_id}/children/"
    else:
        url = f"{API}/nodes/"
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    nodes = resp.json().get("data", [])
    if nodes:
        return nodes[0]["id"]
    raise RuntimeError(f"Could not find or create node '{title}'")


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    print("🔧 Creating OSF project shell for σFlow-PDE...\n")

    # 1. Create root project
    root_id = create_node(ROOT_TITLE)
    root_url = f"https://osf.io/{root_id}"
    print(f"✅ Root project created: {root_url}")
    print(f"   ID: {root_id}")

    # 2. Create child components
    component_ids: dict[str, str] = {}
    for comp in COMPONENTS:
        comp_id = create_node(comp, parent_id=root_id)
        comp_url = f"https://osf.io/{comp_id}"
        component_ids[comp] = comp_id
        print(f"   ✅ {comp}: {comp_url}")

    # 3. Save IDs to configs/osf_ids.yaml
    osf_ids = {
        "root": {
            "id": root_id,
            "url": root_url,
            "title": ROOT_TITLE,
        },
        "components": component_ids,
    }
    ids_path = CONFIGS_DIR / "osf_ids.yaml"
    with open(ids_path, "w") as f:
        yaml.dump(osf_ids, f, default_flow_style=False, sort_keys=False)
    print(f"\n📄 Component IDs saved to: {ids_path}")

    # 4. Print summary for CI
    print("\n📋 CI Environment Variables:")
    print(f"   OSF_ROOT_ID={root_id}")
    for name, cid in component_ids.items():
        print(f"   OSF_COMPONENT_{name.upper()}_ID={cid}")

    print(
        "\n✅ Done. Next step: upload preregistration.json to 01_Preregistration via OSF web UI."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
