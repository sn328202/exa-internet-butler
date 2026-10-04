# Internet Butler starter

A small working agent for the Internet Butler challenge. You give it an errand in plain language. It researches the errand on the live web with [Exa](https://exa.ai), works out the steps, and prepares the final action (an email, a form's contents or a letter) for you to review and approve.

It is meant as a starting point. Fork it, replace parts, or use it only as a reference for calling Exa.

## Setup

You need Python 3.9 or later and an Exa API key from [dashboard.exa.ai](https://dashboard.exa.ai/api-keys).

```bash
git clone <this repo>
cd internet-butler-starter
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
export EXA_API_KEY=your_key_here # on Windows: set EXA_API_KEY=your_key_here
```

## Run it

```bash
python butler.py "Claim compensation for my delayed flight from Helsinki to Berlin last week"
```

Add details about yourself so the draft comes back filled in:

```bash
python butler.py "Cancel my gym membership at FitLife" --details "Name: Alex Doe, member ID 12345, joined March 2025"
```

The agent prints a summary, the steps, what you need, where to submit, the prepared draft, anything you still need to confirm, and the sources it used. You can then approve it, ask for changes, or discard it. Approved actions are saved to `out/`.

## How it works

1. **Research and prepare.** `prepare_action()` sends the errand to Exa's search endpoint with `type: "deep"`. Deep search reads across many sources and fills in a JSON schema (`ACTION_SCHEMA`) with the summary, steps, requirements and a draft. It also returns the sources and field-level citations (`grounding`).
2. **Review.** `show()` prints the package so the user can check it.
3. **Approve.** `submit_action()` saves the approved package. This is the place to connect a real final step if your team wants one.

All the Exa usage is in one function, `exa_search()`, so it is easy to swap in the `exa-py` or `exa-js` SDK.

## Ideas for taking it further

- Put a web or chat interface in front of it.
- Crawl a specific company or government site with Exa's `subpages` option to find buried policies and forms.
- Use Exa's `includeDomains` filter to restrict research to official sources.
- Add an LLM conversation step that asks the user for missing details before drafting.
- Connect the final step to an email inbox or a browser automation tool, with the user's approval in between.
- Use Exa Monitors to follow up, for example by watching for a policy change or a reply deadline.

## Useful links

- Exa docs: https://exa.ai/docs
- Search API reference: https://exa.ai/docs/reference/search
- Exa demos: https://demos.exa.ai
