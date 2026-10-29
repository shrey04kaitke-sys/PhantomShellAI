import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from analyzer import AnalyzerError
from server import ROOT, LocalHTTPServer, PhantomShellHandler, create_server


class ServerRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = LocalHTTPServer(("127.0.0.1", 0), PhantomShellHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_homepage_is_served(self):
        with urlopen(self.base + "/") as response:
            html = response.read().decode("utf-8")
        self.assertIn("Decode the", html)
        self.assertIn("NOTHING RUNS. EVER.", html)

    def test_status_discovers_available_local_models(self):
        with patch("server.discover_models", return_value=["qwen2.5:7b"]):
            with urlopen(self.base + "/api/status") as response:
                data = json.loads(response.read())
        self.assertEqual(data, {"available": True, "models": ["qwen2.5:7b"]})

    def test_status_reports_ollama_unavailable(self):
        with patch("server.discover_models", side_effect=AnalyzerError("Can't reach Ollama.")):
            with self.assertRaises(HTTPError) as raised:
                urlopen(self.base + "/api/status")
        self.assertEqual(raised.exception.code, 503)
        self.assertEqual(json.loads(raised.exception.read()), {
            "available": False, "models": [], "error": "Can't reach Ollama."
        })

    def test_analyze_route_returns_model_output(self):
        with patch("server.analyze", return_value="A useful local diagnosis.") as analyze_mock:
            body = json.dumps({"command": "npm test", "error": "missing script", "model": "qwen2.5:7b"}).encode()
            request = Request(self.base + "/api/analyze", data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request) as response:
                data = json.loads(response.read())
        self.assertEqual(data, {"analysis": "A useful local diagnosis."})
        analyze_mock.assert_called_once()

    def test_submitted_git_status_is_forwarded_as_text_without_execution(self):
        with patch("server.analyze", return_value="A diagnosis.") as analyze_mock:
            body = json.dumps({"command": "git status", "error": "", "model": "qwen2.5:3b"}).encode()
            request = Request(self.base + "/api/analyze", data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(request) as response:
                self.assertEqual(json.loads(response.read()), {"analysis": "A diagnosis."})
        analyze_mock.assert_called_once_with("git status", "", "qwen2.5:3b", False)

    def test_model_output_is_inserted_as_text_and_local_history_is_opt_in(self):
        script = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("resultContent.textContent = data.analysis", script)
        self.assertNotIn("innerHTML", script)
        self.assertIn("if (!historyEnabled()) return;", script)
        self.assertIn("localStorage.removeItem(HISTORY_KEY)", script)

    def test_source_has_no_command_execution_hooks(self):
        source = (ROOT / "server.py").read_text(encoding="utf-8") + (ROOT / "analyzer.py").read_text(encoding="utf-8")
        for execution_hook in ("subprocess.", "os.system(", "Popen(", "create_subprocess"):
            self.assertNotIn(execution_hook, source)

    def test_server_falls_back_to_an_available_port_when_requested_port_is_busy(self):
        blocker = LocalHTTPServer(("127.0.0.1", 0), PhantomShellHandler)
        try:
            fallback = create_server(blocker.server_port)
            try:
                self.assertEqual(fallback.server_address[0], "127.0.0.1")
                self.assertNotEqual(fallback.server_port, blocker.server_port)
            finally:
                fallback.server_close()
        finally:
            blocker.server_close()

    def test_malformed_json_gets_a_clear_400(self):
        request = Request(self.base + "/api/analyze", data=b"{", headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(HTTPError) as raised:
            urlopen(request)
        self.assertEqual(raised.exception.code, 400)
        self.assertIn("valid JSON", raised.exception.read().decode())


if __name__ == "__main__":
    unittest.main()
