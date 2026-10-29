"""Small local web server for PhantomShell AI. No shell execution is provided."""

from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from analyzer import AnalyzerError, analyze, discover_models

ROOT = Path(__file__).resolve().parent
DEFAULT_PORT = 8000


class LocalHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False


class PhantomShellHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; "
            "img-src 'self' data:; font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
        )
        super().end_headers()

    def do_GET(self):
        if urlsplit(self.path).path == "/api/status":
            try:
                self._json(200, {"available": True, "models": discover_models()})
            except AnalyzerError as exc:
                self._json(503, {"available": False, "models": [], "error": str(exc)})
            return
        if urlsplit(self.path).path.startswith("/api/"):
            self._json(404, {"error": "API endpoint not found."})
            return
        if urlsplit(self.path).path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/analyze":
            self._json(404, {"error": "API endpoint not found."})
            return
        try:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._json(400, {"error": "Content-Length must be a valid integer."})
                return
            if length <= 0 or length > 60_000:
                self._json(400, {"error": "Request body must be between 1 byte and 60 KB."})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise AnalyzerError("Expected a JSON object containing your pasted text.")
            answer = analyze(payload.get("command"), payload.get("error"), payload.get("model"), payload.get("spooky", False))
            self._json(200, {"analysis": answer})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Request must contain valid JSON."})
        except AnalyzerError as exc:
            self._json(400 if "Ollama" not in str(exc) else 503, {"error": str(exc)})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            self.log_error("Unexpected error while handling an analysis request")
            self._json(500, {"error": "Something went wrong. Check the server console and try again."})

    def log_message(self, format, *args):
        # Keep requests quiet so pasted content is never accidentally logged.
        if self.path.startswith("/api/"):
            return
        super().log_message(format, *args)


def create_server(requested_port: int = DEFAULT_PORT) -> LocalHTTPServer:
    try:
        return LocalHTTPServer(("127.0.0.1", requested_port), PhantomShellHandler)
    except OSError:
        if requested_port == 0:
            raise
        return LocalHTTPServer(("127.0.0.1", 0), PhantomShellHandler)


def main() -> None:
    try:
        requested_port = int(os.environ.get("PHANTOMSHELL_PORT", DEFAULT_PORT))
    except ValueError as exc:
        raise SystemExit("PHANTOMSHELL_PORT must be a number from 0 to 65535.") from exc
    if not 0 <= requested_port <= 65535:
        raise SystemExit("PHANTOMSHELL_PORT must be a number from 0 to 65535.")
    server = create_server(requested_port)
    if server.server_address[1] != requested_port:
        print(f"Port {requested_port} is unavailable; using an available local port instead.")
    actual_port = server.server_address[1]
    print(f"PhantomShell AI is ready at http://127.0.0.1:{actual_port}")
    print("Only the local Ollama service is used for AI analysis. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nClosing PhantomShell AI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
