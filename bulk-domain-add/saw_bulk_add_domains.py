#!/usr/bin/env python3
"""Bulk add domains to Probely via the API.

Usage:
  probely_bulk_add.py -a API_KEY -f INPUT_FILE [-o OUTPUT_FILE]

Reads newline-delimited hostnames from INPUT_FILE and calls the Probely
Create Domain API for each. Prints a human-readable result for each call
to stdout and optionally appends the results to OUTPUT_FILE.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List
import os

import requests


API_URL = "https://api.probely.com/domains/"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bulk add domains to Probely")
    p.add_argument(
        "-a",
        "--api-key",
        required=False,
        help="Probely API key (JWT token). If omitted, reads from SAW_API env var",
    )
    p.add_argument("-f", "--file", required=True, help="Input file with newline-delimited domains")
    p.add_argument("-o", "--output", help="Optional output file to append results to")
    return p.parse_args()


def read_domains(path: str) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Input file not found: {path}")
    lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines()]
    domains = [l for l in lines if l]
    return domains


def add_domain(api_key: str, hostname: str) -> dict:
    headers = {
        "Authorization": f"JWT {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"hostname": hostname}
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    result = {"status_code": resp.status_code, "text": resp.text}
    try:
        result["json"] = resp.json()
    except Exception:
        result["json"] = None
    return result


def format_result(hostname: str, res: dict) -> str:
    sc = res.get("status_code")
    j = res.get("json")
    if sc == 201 and isinstance(j, dict):
        did = j.get("id")
        verified = j.get("verified")
        vmethod = j.get("verification_method")
        return f"OK: {hostname} -> id={did} verified={verified} method={vmethod}"
    else:
        err = None
        if isinstance(j, dict):
            err = j.get("detail") or j.get("error") or json.dumps(j)
        else:
            err = res.get("text")
        return f"ERROR: {hostname} -> status={sc} error={err}"


def append_line(path: Path, line: str) -> None:
    if path.exists():
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    else:
        with path.open("w", encoding="utf-8") as fh:
            fh.write(line + "\n")


def main() -> None:
    args = parse_args()

    api_key = args.api_key or os.environ.get("SAW_API")
    if not api_key:
        raise SystemExit("API key required: provide -a/--api-key or set SAW_API environment variable")

    domains = read_domains(args.file)
    out_path = Path(args.output) if args.output else None

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    for hostname in domains:
        try:
            res = add_domain(api_key, hostname)
        except requests.RequestException as e:
            line = f"ERROR: {hostname} -> request failed: {e}"
            print(line)
            if out_path:
                append_line(out_path, line)
            continue

        line = format_result(hostname, res)
        print(line)
        if out_path:
            append_line(out_path, line)


if __name__ == "__main__":
    main()
