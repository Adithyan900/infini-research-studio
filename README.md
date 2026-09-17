# Infini | Research Studio

An AI-powered research planner by [Adithyan S](https://github.com/Adithyan900), built with Python, Streamlit, and the Gemini API.

Enter a topic and receive three focused research questions: the problem, possible approaches, and evidence needed to evaluate them. The interface uses a dark navy theme, mint accents, and rounded question cards.

## Current capabilities

- Topic-specific research plans generated with Gemini 3.1 Flash-Lite.
- Structured JSON output and validation for three non-empty, distinct questions.
- Chat-style interface, in-session history, and plain-text downloads.
- User-facing API error messages and environment-based credentials.
- A 2,000-character topic limit to bound input size.

This is a planning prototype, not a complete multi-agent researcher or RAG chatbot. It does not retrieve documents, search the web, verify facts, or generate evidence-backed reports. Each topic is processed independently; the displayed history is not sent to Gemini as conversational context.

## Run locally

Use Python 3.11 for a new environment. The original prototype ran on Python 3.9.6, but that environment showed end-of-life and LibreSSL warnings. Do not replace macOS system Python.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local `.env` file beside `app.py` containing:

```dotenv
GEMINI_API_KEY=YOUR_PRIVATE_KEY
```

Then launch:

```bash
python -m streamlit run app.py
```

Never share the real key or upload `.env`. `.env.example` contains no credential and may be committed.

## Deploy on Streamlit Community Cloud

1. Push the project contents to a GitHub repository. `app.py`, `planner.py`, and `requirements.txt` must be at the repository root; preserve `.streamlit/config.toml` in its folder.
2. At [Streamlit Community Cloud](https://share.streamlit.io/), create an app from that repository and its `main` branch.
3. Set the entrypoint to `app.py` and select Python 3.11 in Advanced settings if available.
4. In the private Secrets field, add a top-level TOML setting:

```toml
GEMINI_API_KEY = "YOUR_PRIVATE_KEY"
```

5. Deploy and test one public topic. Confirm that three cards render, downloads work, and clearing the conversation works before sharing the URL.

Streamlit makes root-level secrets available as environment variables, so the planner's `os.getenv` call can read the hosted key. Do not commit a real `.streamlit/secrets.toml` file.

See [Streamlit secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management) and [Community Cloud deployment secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## Privacy, limits, and public access

- Submitted topics are sent to Google. Use public/non-sensitive topics and review the provider's current data-use terms.
- Model availability and free-tier quotas can change. Check [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) and your account's tier before running.
- Visitors use the app owner's Gemini quota. There is no authentication or global rate limiter in this prototype. Input length limits do not prevent quota abuse. Keep access restricted while testing; do not enable paid billing without deliberate budget controls.
- API errors such as 429 (quota/rate limits) or 503 (temporary unavailability) may occur.
- Session history is not a database and may disappear when the browser session or app restarts. Download plans you want to keep.
- Prompt instructions and output validation do not guarantee useful or unbiased questions. Human review is required.

## Verification

```bash
python -m unittest discover -s tests -v
```

Tests cover validation, missing/invalid inputs, mocked model responses, and provider errors without using a real API key. A live deployed smoke test is still required. Dependencies are version-bounded rather than fully locked; freeze a tested deployment environment for stricter reproducibility.

## Planned next steps

- Document uploads and retrieval-augmented generation.
- Evidence-linked answers and source citations.
- Separate research and review stages.
- Authentication, global rate limiting, persistence, and deployment monitoring.

These are roadmap items, not implemented features. Live deployment is pending verification.
