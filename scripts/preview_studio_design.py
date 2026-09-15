"""Read-only local preview of generated public pages and management markup.

No production APIs, credentials, records, or login session are copied. Management
HTML can be inspected locally; operations are deliberately unavailable.
"""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--release", type=Path, required=True)
parser.add_argument("--port", type=int, default=8768)
args = parser.parse_args()
release = args.release.resolve()
source = (release / "runtime/worker/admin-assets.generated.mjs").read_text(encoding="utf-8")
admin = json.loads(source.split("export default ", 1)[1].strip().removesuffix(";"))
login_module = (release / "runtime/worker/login-page.mjs").as_uri()
login = subprocess.check_output(["node", "--input-type=module", "-e", f"import {{loginPage}} from {json.dumps(login_module)}; process.stdout.write(loginPage('/admin'));" ]).decode("utf-8")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *values, **kwargs):
        super().__init__(*values, directory=str(release / "public"), **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        asset = admin.get(path.rstrip("/") if path == "/admin/" else path)
        if path == "/preview-login":
            asset = {"body": login, "type": "text/html; charset=utf-8"}
        if asset:
            body = asset["body"].encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", asset["type"])
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()


print(f"Read-only design preview: http://127.0.0.1:{args.port}", flush=True)
ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
