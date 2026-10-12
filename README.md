# Internet Butler starter

A small working agent for the Internet Butler challenge. You give it an errand in plain language. It researches the errand on the live web with [Exa](https://exa.ai), works out the steps, and prepares the final action (an email, a form's contents or a letter) for you to review and approve.

It is meant as a starting point. Fork it, replace parts, or use it only as a reference for calling Exa.

## Setup

You need Python 3.9 or later and an Exa API key from [dashboard.exa.ai](https://dashboard.exa.ai/api-keys).

> **Free credits for hackathon participants:** after creating your account, [claim your free API credits here](https://dashboard.exa.ai/billing?coupon=EXA5OCT4HACK) (code **`EXA5OCT4HACK`** is applied automatically), or scan the QR code below.
>
> <img src="assets/free-credits-qr.png" alt="QR code for free Exa credits" width="160">

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
python butler.py "Claim EU261 compensation for my Helsinki to Berlin flight that landed 4 hours late" --country FI
```

Add `--country` with a two-letter code so the agent looks for that country's rules and companies, and `--language` to get the draft in the local language. Add `--details` so the draft comes back filled in:

```bash
python butler.py "Cancel my gym membership in Berlin" --country DE --language German \
  --details "Name: Alex Doe, member ID 12345, joined March 2025"
```

More errands to try:

- "Return a faulty pair of headphones I bought online from a shop in the Netherlands, within the EU 14-day withdrawal period" `--country NL`
- "Register a used car I bought in Sweden after moving it to Finland" `--country FI --language Finnish`
- "Get a refund for a Deutsche Bahn train that arrived 90 minutes late" `--country DE`
- "Find out how to replace a lost national ID card in Spain" `--country ES --language Spanish`

The agent prints a summary, the steps, what you need, where to submit, the prepared draft, anything you still need to confirm, and the sources it used. You can then approve it, ask for changes, or discard it. Approved actions are saved to `out/`.

## How it works

1. **Research and prepare.** `prepare_action()` sends the errand to Exa's search endpoint with `type: "deep"`. Deep search reads across many sources and fills in a JSON schema (`ACTION_SCHEMA`) with the summary, steps, requirements and a draft. It also returns the sources and field-level citations (`grounding`).
2. **Review.** `show()` prints the package so the user can check it.
3. **Approve.** `submit_action()` saves the approved package. This is the place to connect a real final step if your team wants one.

All the Exa usage is in one function, `exa_search()`, so it is easy to swap in the `exa-py` or `exa-js` SDK.

## What Exa can pull for your agent

The starter only uses one search call. Exa can give your agent much more than that, and the best butlers will combine several of these.

**The web**

| What | What you get | How a butler might use it |
| --- | --- | --- |
| Web search | Search over billions of pages by meaning, in fast, balanced or deep research modes | Find the right policy, form or rule from a plain-language question |
| Categories | Results limited to news, companies, people, research papers, personal sites or financial reports | Check a company's track record, or find a person to contact |
| Page contents | Full text, short highlights, summaries, and links and images from any page | Read the fine print without loading whole pages into your model |
| Subpages | Crawl up to 100 pages of a single site | Dig through a company or government site to find the buried cancellation page |
| Filters | Publish date ranges, and up to 1,200 domains to include or exclude | Stick to official sources, or only use news from the last week |
| Freshness and history | Fetch a page live right now, or get a page as it looked on a past date | Check today's prices, or prove what a policy said when you signed up |
| Structured output | Results returned as JSON in a schema you define, with citations for each field | Turn messy research into a checklist, a comparison table or a filled-in form |
| Location | Results tuned to the country the user is searching from | Get the rules and companies that apply where the user lives |

**Lists and tracking**

| What | What you get | How a butler might use it |
| --- | --- | --- |
| Websets | Lists of companies, people or opportunities, each checked against your criteria and enriched with extra details | Build a list of every energy supplier in a city with their current tariffs |
| Monitors | Searches that re-run on a schedule and report what changed | Watch for a price drop, a policy change or a reply deadline |
| Agent API | Long-running research jobs that you start and check back on | Hand off a big research task and pick up the result later |
| MCP server | Exa as a tool for Claude, Cursor and other MCP clients | Give an existing assistant live web search with no extra code |

**Structured data (new)**

| What | Coverage | How a butler might use it |
| --- | --- | --- |
| Places | 210M+ points of interest, worldwide | Find a notary, repair shop or pharmacy that is open now and nearby |
| Flights | 37M scheduled flights through October 2027, worldwide (no prices yet) | Find alternative flights when one is cancelled |
| Transit | 860 transit operators | Plan a route around a train strike or delay |
| Products | 10M+ products from major retailers | Compare replacement parts or find a cheaper equivalent |
| Events | 1M+ events from 10 platforms | Find what's on near a hotel during a trip |
| Podcasts | 2.7M+ episodes from 100k+ shows | Find what an expert or company said on a topic |

Places and Flights cover the whole world. Transit, Products, Events and Podcasts are mostly US-focused for now, so for European errands lean on web search, Places and Flights.

These can be combined in one agent. For example, a trip butler could check the flight schedule, then find places near the hotel, then find events during the stay.

## Build with Codex

The repo is set up for [Codex](https://openai.com/codex) (and works the same way with Claude Code and other coding agents).

- **`AGENTS.md`** tells the coding agent how the project is organised, where the Exa calls live, and the rules to keep (approval step, sources, no keys in code). Codex reads it automatically.
- **`.codex/config.toml`** connects Exa's hosted MCP server, so Codex can search the web, read pages and run research while it helps you build. Codex loads it once you trust the project, and it uses the same `EXA_API_KEY` as the starter.

To get started:

```bash
export EXA_API_KEY=your_key_here
codex
```

Then ask for what you want, for example:

- "Add a Places lookup so the butler finds a notary that is open now near the user."
- "When a flight is cancelled, use Flights data to suggest alternatives, then find a hotel near the airport."
- "Restrict research to official government and company sites for the user's country."

Prefer not to use the project config? Install the Exa plugin from [chatgpt.com/plugins/exa](https://chatgpt.com/plugins/exa) instead, or add the server yourself with `codex mcp add exa --url https://mcp.exa.ai/mcp` (free, rate-limited use without a key).

## Ideas for taking it further

- Put a web or chat interface in front of it.
- Crawl a specific company or government site with Exa's `subpages` option to find buried policies and forms.
- Use Exa's `includeDomains` filter to restrict research to official sources.
- Add an LLM conversation step that asks the user for missing details before drafting.
- Connect the final step to an email inbox or a browser automation tool, with the user's approval in between.
- Use Exa Monitors to follow up, for example by watching for a policy change or a reply deadline.
- Combine web research with Places or Flights data, for example rebooking around a cancelled flight and finding somewhere nearby to stay.

## Useful links

- Free hackathon credits (code `EXA5OCT4HACK`): https://dashboard.exa.ai/billing?coupon=EXA5OCT4HACK
- Exa docs: https://exa.ai/docs
- Search API reference: https://exa.ai/docs/reference/search
- Exa demos: https://demos.exa.ai
