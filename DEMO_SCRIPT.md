# PhantomShell AI demo script (about 90 seconds)

## Before recording

1. Start Ollama and confirm `gemma4:e2b` appears in the model selector. This is a local model already installed on the development machine.
2. From this project folder, run `python server.py` and open the URL printed by the server.
3. Close unrelated windows and browser tabs. Do not show real credentials, private terminal history, or personal files.

## Walkthrough

1. **Introduce the tool (10 sec).** Show the Halloween interface and the local model status. Say: “PhantomShell explains terminal errors with Ollama running locally. It does not run pasted commands or call hosted AI APIs.”
2. **Analyze a real error (25 sec).** Paste `ModuleNotFoundError: No module named 'requests'` into the error field. Optionally include `python -m pip show requests` as command text. Select `gemma4:e2b` and analyze. Point out the likely missing dependency and environment-specific fix. The app does not run the suggested command.
3. **Show the no-execution boundary (20 sec).** Paste this text into the command field; do not run it in a terminal:

   ```text
   python -c "from pathlib import Path; Path('PHANTOM_EXECUTION_SENTINEL').write_text('executed')"
   ```

   Analyze it. Point to the “NOTHING RUNS. EVER.” heading and the diagnosis disclaimer. In a separate terminal, check that `PHANTOM_EXECUTION_SENTINEL` was not created.
4. **Show privacy controls (20 sec).** Open Recent séances. Show that history starts off. Enable it, analyze a harmless sample, show the local entry, then select **Clear all history** and confirm the list is empty.
5. **Close (15 sec).** Summarize that requests go to loopback Ollama only, model names are discovered dynamically, and no hosted AI key or account is needed.

## Accuracy note

Keep the real model response visible, including uncertainty. Do not edit or fabricate model output, screenshots, or timing claims. If the model gives an inaccurate suggestion, call it out as a limitation rather than presenting it as verified advice.
