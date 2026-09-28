"""Run example requests against a locally running service and write actual JSON outputs."""
import json, pathlib, urllib.request
root=pathlib.Path(__file__).parent
out=[]
for line in (root/'examples/requests.jsonl').read_text().splitlines():
    req=urllib.request.Request('http://127.0.0.1:8000/v1/visualizations',data=line.encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=45) as r: out.append(json.load(r))
(root/'examples/outputs.json').write_text(json.dumps(out,indent=2))
