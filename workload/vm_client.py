#!/usr/bin/env python3
"""Reference VM-side client; observations must be supplied by the platform collector."""
import argparse
import json
from urllib.request import Request, urlopen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--endpoint", default="http://virtualization-ai-401-adapter:8080/api/v1/modernize")
    args = parser.parse_args()
    payload = open(args.request, encoding="utf-8").read().encode()
    request = Request(args.endpoint, payload, {"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        print(json.dumps(json.loads(response.read()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
