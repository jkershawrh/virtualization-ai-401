#!/usr/bin/env python3
import argparse, json
from urllib.request import Request, urlopen
p = argparse.ArgumentParser(); p.add_argument("request"); p.add_argument("--endpoint", default="http://virtualization-ai-401-adapter:8080/api/v1/modernize"); a = p.parse_args()
with urlopen(Request(a.endpoint, open(a.request,"rb").read(), {"Content-Type":"application/json"}, method="POST"), timeout=10) as r: print(json.dumps(json.loads(r.read()), indent=2))
