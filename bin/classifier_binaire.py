#!/usr/bin/env python3
"""CLI des agents binaires Psychologie : registre, classification, verification chronologique."""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import classification_binaire, sources  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("registry")
    classify = sub.add_parser("classify")
    classify.add_argument("works", nargs="*", default=list(sources.OEUVRES))
    classify.add_argument("--limit-per-work", type=int)
    verify = sub.add_parser("verify")
    verify.add_argument("--limit", type=int, default=100)
    verify.add_argument("--force", action="store_true")
    resume = sub.add_parser("resume")
    resume.add_argument("--limit", type=int, default=100)
    resume.add_argument("--stale-after-seconds", type=int, default=3600)
    sub.add_parser("progress")
    args = parser.parse_args()

    orchestrator, verifier = classification_binaire.components()
    if args.command == "registry":
        result = orchestrator.registry.describe()
    elif args.command == "classify":
        result = classification_binaire.classify_works(
            args.works, limit_per_work=args.limit_per_work,
        )
    elif args.command == "verify":
        result = verifier.verify(limit=args.limit, force=args.force)
    elif args.command == "resume":
        result = orchestrator.recover_and_resume(
            classification_binaire.PROJECT_ID, limit=args.limit,
            stale_after_seconds=args.stale_after_seconds,
        )
    else:
        result = orchestrator.progress(classification_binaire.PROJECT_ID)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
