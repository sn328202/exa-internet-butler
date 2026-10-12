# AGENTS.md

Guidance for coding agents (Codex, Claude Code and others) working in this repo.

## What this project is

A starter for the Internet Butler hackathon challenge. The agent takes an everyday errand in plain language, researches it on the live web with Exa, works out the steps, and prepares the final action (an email, a form's contents, a letter) for the user to review and approve.

## How the code is organised

- `butler.py` is the whole app.
  - `exa_search()` is the only function that calls the Exa API. Add new Exa calls through it, or next to it, so auth and error handling stay in one place.
  - `prepare_action()` builds the request: a `deep` search with `ACTION_SCHEMA` as the structured output, plus `--country` (sent as `userLocation`) and `--language`.
  - `show()` prints the package for review. `submit_action()` saves an approved package to `out/`.
- `README.md` lists every kind of data Exa can return. Read the "What Exa can pull for your agent" section before adding a feature.

## Rules for changes

- Keep the review and approval step. The agent prepares actions; the user decides whether to send them.
- Show sources. Anything the agent tells the user should be traceable to the pages Exa returned.
- Never put an API key in code or commit one. Read it from `EXA_API_KEY`.
- Keep the examples European where possible. Hackathon participants are mostly in Europe.
- Places and Flights data cover the whole world. Transit, Products, Events and Podcasts are mostly US-focused, so do not build European features on them.
- Keep dependencies small. `requests` is the only one today.

## Exa API quick reference

- Endpoint: `POST https://api.exa.ai/search`, header `x-api-key`.
- `type`: `instant`, `fast`, `auto`, `deep-lite`, `deep`, `deep-reasoning`.
- `category`: `company`, `people`, `news`, `publication`, `personal site`, `financial report`.
- Useful options: `includeDomains`, `excludeDomains`, `startPublishedDate`, `endPublishedDate`, `userLocation`, `outputSchema`, `systemPrompt`, `contents` (`text`, `highlights`, `summary`), `subpages`, `maxAgeHours`, `snapshotAsOf`.
- With `outputSchema`, the structured result is in `output.content` and the citations are in `output.grounding`.
- Full docs: https://exa.ai/docs

## Checking your work

- `python -m py_compile butler.py`
- `python butler.py --help`
- A real run needs `EXA_API_KEY`, for example:
  `python butler.py "Claim EU261 compensation for my Helsinki to Berlin flight that landed 4 hours late" --country FI`
