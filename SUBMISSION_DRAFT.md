---
title: "PhantomShell AI: A Local-First Haunted Terminal Assistant"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26).*

## What I Built

PhantomShell AI is a Halloween-themed developer tool for understanding terminal errors. Paste a command, an error message, or both, and a locally running Ollama model explains likely causes and suggests practical next steps. Optional spooky commentary adds a seasonal touch.

The app is read-only. It never executes pasted commands, and its interface labels terminal text as user-provided rather than claiming to have run or verified it. Model output is displayed as text, and a reminder asks users to review suggestions before running anything.

## Demo

[Public demo URL needed. The real local browser recording is `demo-output/phantomshell-local-demo.webm`; upload it to an appropriate video host (for example, YouTube, Vimeo, or Loom) before adding an accessible URL here.]

## Code

[Public repository URL needed after creating `PhantomShellAI` under `shrey04kaitke-sys` and pushing the local commits.]

## How I Built It

The MVP uses Python’s standard library for a local HTTP server and Ollama integration, plus a dependency-free HTML, CSS, and JavaScript interface. It discovers available models from Ollama instead of assuming one is installed. Analysis uses Ollama’s local `/api/chat` endpoint; there are no hosted AI APIs or third-party runtime calls. System proxy settings are bypassed for the Ollama request.

History is opt-in, stored in the current browser’s local storage, limited to the 12 most recent results, and can be cleared in the app. The test suite covers input limits, model availability, loopback-only requests, proxy bypass, safe text rendering, history controls, and server routes.

The demo uses the locally installed `gemma4:e2b` model. Local model output can still be inaccurate, so the app explicitly tells people to review suggestions.

The source is available under the MIT License.

## Why Does Open Innovation Matter?

Running an open-weight model locally keeps terminal content on the developer’s own machine and lets people choose among the models they have installed. Once the model is present, analysis does not depend on a hosted AI service, an API key, or an internet connection. The local-first design also makes the privacy boundary inspectable: the browser talks to the local app, and the app talks only to loopback Ollama.

## My Agent Session

[Optional: add a real agent-session link if one is saved for this project.]

## The Spirit of It

Build errors are spooky enough. PhantomShell gives them a plain-language explanation, while keeping the shell itself untouched.

## Prize Categories

Best Use of Gemma — the demo runs the open-weight `gemma4:e2b` model locally through Ollama.
