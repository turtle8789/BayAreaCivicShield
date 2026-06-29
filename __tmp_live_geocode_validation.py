import ast
import json
import os
from pathlib import Path
import sys

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re


SOURCE_PATH = Path(__file__).with_name("civicshield_pro_app.py")
LOG_PATH = SOURCE_PATH.with_name("failed_geocoding_attempts.log")
OUTPUT_PATH = SOURCE_PATH.with_name("__tmp_live_geocode_validation_output.json")


def load_functions():
    source = SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SOURCE_PATH))
    selected = []

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEFAULT_HTTP_HEADERS":
                    selected.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in {"geocode_address", "fetch_lawhelp_resources"}:
            node.decorator_list = []
            selected.append(node)

    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)

    namespace = {
        "requests": requests,
        "BeautifulSoup": BeautifulSoup,
        "urljoin": urljoin,
        "json": json,
        "os": os,
        "datetime": datetime,
        "re": re,
        "print": lambda *args, **kwargs: None,
        "__file__": str(SOURCE_PATH),
    }
    exec(compile(module, str(SOURCE_PATH), "exec"), namespace)
    return namespace["fetch_lawhelp_resources"], namespace["geocode_address"]


def read_log_lines(limit=3):
    if not LOG_PATH.exists():
        return []
    return LOG_PATH.read_text(encoding="utf-8").splitlines()[:limit]


def read_last_log_entry():
    if not LOG_PATH.exists():
        return None
    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except Exception:
        return {"raw": lines[-1]}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"

    if LOG_PATH.exists():
        LOG_PATH.unlink()

    fetch_lawhelp_resources, geocode_address = load_functions()
    resources = fetch_lawhelp_resources()

    if mode == "sample":
        first_15 = []
        for resource in resources[:15]:
            coords = geocode_address(resource["address"])
            first_15.append(
                {
                    "name": resource["name"],
                    "address": resource["address"],
                    "coords": list(coords) if coords is not None else None,
                }
            )

        payload = {
            "resource_count": len(resources),
            "first_15": first_15,
            "log_exists": LOG_PATH.exists(),
            "log_lines": read_log_lines(),
        }
    else:
        full_run = {
            "completed": True,
            "processed": 0,
            "failed_count": 0,
            "blocker": None,
        }

        for resource in resources:
            coords = geocode_address(resource["address"])
            full_run["processed"] += 1
            if coords is None:
                full_run["failed_count"] += 1
                last_entry = read_last_log_entry()
                error_text = ""
                if isinstance(last_entry, dict):
                    error_text = last_entry.get("error", "")
                if error_text:
                    full_run["completed"] = False
                    full_run["blocker"] = {
                        "name": resource["name"],
                        "address": resource["address"],
                        "error": error_text,
                        "attempted_queries": last_entry.get("attempted_queries", []) if isinstance(last_entry, dict) else [],
                    }
                    break

        payload = {
            "resource_count": len(resources),
            "full_run": full_run,
            "log_exists": LOG_PATH.exists(),
            "log_lines": read_log_lines(),
        }

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    sys.stdout.write(str(OUTPUT_PATH) + "\n")


if __name__ == "__main__":
    main()