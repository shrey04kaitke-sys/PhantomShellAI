---
title: "PhantomShell AI: A Local-First Haunted Terminal Assistant"
published: false
tags: devchallenge, hf26challenge
---

This is my submission for the [Hacktoberfest Open-Source AI Challenge: Week 4](https://dev.to/challenges/hacktoberfest-week4-2026-10-26), themed around building with open-source AI.

## What I Built

PhantomShell AI is a small, Halloween-themed troubleshooting assistant for terminal errors. A developer pastes a command, an error message, or both, selects an Ollama model, and gets a structured explanation with a likely cause, practical next steps, and prevention tips.

The important boundary is that PhantomShell is read-only. It does not have a shell runner, does not execute pasted commands, and does not claim that pasted commands were run or verified. The interface labels terminal content as user-provided text, and the response includes a reminder to review suggestions before running anything.

I also made model availability visible instead of assuming one fixed model. PhantomShell discovers the models installed in the local Ollama instance, so the same interface can work with different local models.

## Demo

The demo recording is prepared locally at `demo-output/phantomshell-local-demo.webm`. It has a WebM/EBML container signature and is 1,303,128 bytes. The project’s demo script covers local model discovery, error analysis, the no-execution boundary, and opt-in history controls; I still need to review the recording’s rendered contents after uploading it.

There is no public demo URL yet. I will upload this recording to a public video host and replace this paragraph with the resulting URL before publishing. I will also review the uploaded playback and make sure it does not expose private terminal data.

## Code

The project is intended to be published as a public GitHub repository, but this local checkout currently has no Git remote and no public `PhantomShell` repository exists under my GitHub account. I will create or push the repository, verify that it opens while signed out, and replace this paragraph with the verified repository URL before publishing.

## How I Built It

PhantomShell uses Python’s standard library for a local HTTP server and Ollama integration, with a dependency-free HTML, CSS, and JavaScript frontend.

- `server.py` serves the interface and exposes `GET /api/status` and `POST /api/analyze` on loopback.
- `analyzer.py` discovers installed models through Ollama’s local `/api/tags` endpoint and sends analysis requests to `/api/chat`.
- `OLLAMA_HOST` is restricted to `localhost`, `127.0.0.1`, or `::1`; credentials and URL paths are rejected.
- Requests use an opener with system proxies disabled, so pasted terminal text is not redirected through a configured HTTP proxy.
- The browser renders model output with `textContent`, not `innerHTML`.
- History is off by default. If enabled, up to 12 results are stored in the current browser’s `localStorage` and can be cleared from the interface.
- Inputs are limited to 15,000 characters per field and 25,000 characters combined.

The demo uses `gemma4:e2b`, a Gemma 4 model installed in Ollama on my development machine. I verified live local inference by sending a sample `ModuleNotFoundError` through PhantomShell and receiving a real model diagnosis. The automated test suite also passes all 25 tests, covering validation, model discovery and selection, loopback enforcement, proxy bypass, prompt safety, safe rendering, history behavior, and server routes.

PhantomShell has no hosted AI API, analytics, external application calls, or external assets. Local inference improves the privacy boundary, but it does not magically redact secrets: users should avoid pasting sensitive values and should keep Ollama bound to loopback. Model output can still be inaccurate, so it is advice to review, not verified execution output.

The project is released under the [MIT License](./LICENSE).

## Why Does Open Innovation Matter?

Open innovation makes useful AI experimentation accessible without requiring a hosted account or an API key. With Ollama and Gemma running locally, terminal text can stay on the developer’s machine while they choose the model that fits their hardware.

It also makes the trust boundary easier to inspect. This project is small enough to read: the browser talks to a local Python server, and the server talks to Ollama over loopback. The app’s safety decisions—no command execution, no remote Ollama host, proxy bypass, escaped model output, and opt-in browser history—are visible in the source instead of being hidden behind a hosted service.

## My Agent Session

I do not have a public agent-session link to include. I will leave this section without an invented URL rather than pointing readers to a session that they cannot open.

## The Spirit of It

Terminal errors already feel haunted. PhantomShell turns them into a calmer explanation without touching the shell itself: paste the evidence, ask a local model for context, and decide yourself what—if anything—to try next.

## Prize Categories

**Best Use of Gemma** — eligible. The Week 4 category asks participants to use Google’s open-weight Gemma model by running it locally, fine-tuning it, or serving it through Google Cloud or another provider. PhantomShell uses the locally installed `gemma4:e2b` model through Ollama for its live analysis flow.

#devchallenge #hf26challenge
