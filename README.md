# PhantomShell AI 🕯️

**Decode the dark.** PhantomShell AI is a small, Halloween-themed terminal troubleshooting assistant. Paste a command, an error, or both; a locally running Ollama model explains what happened and suggests practical fixes. Optional spooky commentary adds a little seasonal flavor.

## Privacy and safety

- PhantomShell **never executes pasted commands**. It has no shell runner or command execution API.
- Terminal text is sent only to the Ollama service on this computer (`127.0.0.1:11434`). The server rejects non-loopback `OLLAMA_HOST` values.
- There are no hosted AI APIs, analytics, external app calls, or external assets; the interface works offline apart from local Ollama inference.
- Analysis history is off by default. Turn it on in **Recent séances** to save up to 12 results in this browser’s `localStorage`; clear saved results there at any time. Clearing browser site data also removes it.
- Pasted content is sent to your local model as untrusted text. Don’t treat model suggestions as commands to run without reviewing them.
- Local model responses can be inaccurate or describe pasted commands as if they ran; PhantomShell itself is read-only and displays a reminder with each diagnosis.

## Requirements

- Python 3.10 or newer (verified with Python 3.13)
- [Ollama](https://ollama.com/download) installed and running locally
- At least one model downloaded in Ollama

The app discovers installed models at startup; it does not assume a particular model exists. With Ollama running, download a model if needed:

```powershell
ollama pull qwen2.5:3b
```

You can substitute another model supported by your hardware. Ollama’s model size affects disk space, RAM/VRAM use, and response speed.

## Launch

From the project folder:

```powershell
python server.py
```

Open the URL printed in the terminal (normally [http://127.0.0.1:8000](http://127.0.0.1:8000)). If port 8000 is unavailable, PhantomShell automatically chooses an available local port. Keep Ollama running in the background. If you start Ollama after opening PhantomShell, refresh the page to rediscover models. Stop the app with **Ctrl+C**.

Optional: set `OLLAMA_HOST` to another loopback address (for example `http://localhost:11434`). Non-local hosts are rejected to protect pasted terminal contents.
Optional: set `PHANTOMSHELL_PORT` to choose the preferred web port. The server falls back to an available loopback port if that port is already in use.

## Use

1. Select one of the installed local models.
2. Paste a command, an error message/output, or both. Neither field is required if the other has content.
3. Optionally enable **Spooky commentary**.
4. Select **Summon an explanation**. The response appears below with an explanation, likely cause, practical next steps, and prevention tips.
5. Optionally open the history icon and enable local history to revisit recent results; use **Clear all history** to remove saved results.

Inputs are capped at 15,000 characters per field and 25,000 characters combined.

## Architecture

- `index.html`, `styles.css`, and `app.js` provide a dependency-free browser interface served from the local Python server.
- `server.py` exposes only local static files and two JSON endpoints: `GET /api/status` discovers models from Ollama; `POST /api/analyze` validates the request and returns analysis.
- `analyzer.py` calls Ollama’s `/api/tags` and non-streaming `/api/chat` endpoints over loopback. It disables system HTTP proxies and rejects non-loopback `OLLAMA_HOST` values.
- The browser renders model output using `textContent`; no model text is interpreted as HTML. Optional history is stored only in browser `localStorage`, is off by default, and can be cleared in the history drawer.

```text
Browser (127.0.0.1:<web-port>) ── /api/status, /api/analyze ──> PhantomShell server
Browser localStorage (opt-in)                                  │
                                                              └── HTTP loopback ──> Ollama (127.0.0.1:11434)
```

## Limitations

- Model availability and quality depend on the Ollama service, installed model, and machine resources.
- Local models can hallucinate, misunderstand pasted output, or suggest an unsafe or irrelevant command. PhantomShell never executes suggestions; review them before use.
- The app does not redact secrets before local inference. Keep Ollama bound to loopback and avoid saving sensitive analyses in browser history.
- Browser history is limited to 12 recent results and is not encrypted; it is stored by the browser profile when enabled.
- This project currently has no license file; choose a license before inviting reuse or redistribution.

## Hacktoberfest Week 4 preparation

- [Demo script](DEMO_SCRIPT.md) describes a short, reproducible local walkthrough, including an execution-sentinel check.
- [DEV submission draft](SUBMISSION_DRAFT.md) follows the current Week 4 template. It contains placeholders for the repository and demo URLs and has not been published.
- The official challenge requires the `devchallenge` and `hf26challenge` tags. Entries are due October 31, 2026 at 11:59 PM PDT. Check the [official Week 4 challenge page](https://dev.to/challenges/hacktoberfest-week4-2026-10-26) before publishing in case its rules change.

## Tests

The automated tests use Python’s built-in `unittest`; no extra packages are needed:

```powershell
python -m unittest discover -s tests -v
```

Tests cover validation limits, model discovery, model selection, loopback-only enforcement, prompt safety, and the local Ollama request path. The live Ollama API is not required to run the unit suite.

## Project layout

```text
PhantomShell/
├── analyzer.py          # validation and local Ollama API integration
├── server.py            # standard-library local web server and JSON endpoints
├── index.html            # interface structure
├── styles.css           # responsive Halloween-themed styling
├── app.js               # browser UI, model status, and local history
├── .gitignore           # Python cache and virtual-environment ignores
└── tests/
    ├── test_analyzer.py # validation and local model unit tests
    └── test_server.py   # local HTTP route smoke tests
```

## Troubleshooting

- **Ollama offline:** Start the Ollama app/service and refresh PhantomShell.
- **No models found:** Download one with `ollama pull <model-name>` and refresh.
- **Slow response:** Choose a smaller model suitable for your computer, or reduce the pasted output to the relevant lines.
- **Server uses another port:** Open the URL printed at startup. PhantomShell falls back to an available local port if 8000 is occupied.

## License

PhantomShell AI is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.
