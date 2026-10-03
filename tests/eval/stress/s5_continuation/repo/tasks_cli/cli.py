import argparse
import json

ITEMS = [
    {"name": "write report", "priority": 2},
    {"name": "backup db", "priority": 1},
    {"name": "call vendor", "priority": 3},
    {"name": "archive logs", "priority": 2},
]


def main(argv=None):
    p = argparse.ArgumentParser(prog="tasks")
    p.add_argument("--json", action="store_true", help="print as JSON")
    args = p.parse_args(argv)
    items = list(ITEMS)
    if args.json:
        print(json.dumps({"items": items}))
    else:
        for it in items:
            print(f"{it['priority']} {it['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
