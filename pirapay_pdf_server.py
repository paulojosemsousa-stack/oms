import json
import mimetypes
import os
import subprocess
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
GENERATOR = ROOT / "tmp/pdfs/generate_pirapay_pdf.py"
OUTPUT = ROOT / "output/pdf/PIRApay_Dashboard_Executivo_Plano_de_Negocio.pdf"
INDEX_FILE = ROOT / "PIRApayR.html"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[PIRApay] {self.address_string()} - {fmt % args}")

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_text(self, status, text):
        body = text.encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "text/plain;charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        if not path.exists() or not path.is_file():
            self._send_text(404, "Arquivo nao encontrado.")
            return
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        route = unquote(urlparse(self.path).path)
        if route == "/health":
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json;charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        if route == "/generate":
            self.send_response(303)
            self._cors()
            self.send_header("Location", "/")
            self.end_headers()
            return

        if route in ("", "/"):
            self._send_file(INDEX_FILE)
            return

        target = (ROOT / route.lstrip("/")).resolve()
        if ROOT not in target.parents and target != ROOT:
            self._send_text(403, "Caminho nao permitido.")
            return
        self._send_file(target)

    def do_POST(self):
        if urlparse(self.path).path != "/generate":
            self._send_text(404, "Endpoint nao encontrado.")
            return

        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            model = payload.get("model")
            if not isinstance(model, dict):
                raise ValueError("Payload sem model valido.")

            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["PIRAPAY_MODEL_JSON"] = json.dumps({"model": model}, ensure_ascii=False)
            env["PIRAPAY_PDF_OUTPUT"] = str(OUTPUT)
            subprocess.run([sys.executable, str(GENERATOR)], check=True, env=env, cwd=str(ROOT), capture_output=True, text=True)

            pdf = OUTPUT.read_bytes()
            stamp = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y%m%d_%H%M%S")
            filename = f"PIRApay_Dashboard_Executivo_{stamp}.pdf"
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(pdf)))
            self.end_headers()
            self.wfile.write(pdf)
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr or exc.stdout or str(exc)
            self._send_text(500, f"Erro ao gerar PDF:\n{detail}")
        except Exception as exc:
            self._send_text(500, str(exc))


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PIRApay ativo em http://{host}:{port}")
    print("Abra a pagina inicial e clique em Gerar PDF Executivo.")
    server.serve_forever()
