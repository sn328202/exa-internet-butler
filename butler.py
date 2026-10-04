"""Internet Butler starter.

Give the agent an errand in plain language. It researches the errand on the live
web with Exa, works out the steps, and prepares the final action (an email, a
form's contents or a letter) for you to review and approve.

Usage:
    python butler.py "Claim compensation for my delayed flight from Helsinki to Berlin"
    python butler.py "Cancel my gym membership" --details "Name: Alex Doe, member ID 12345"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

EXA_SEARCH_URL = "https://api.exa.ai/search"

# Free credits for hackathon participants. Redeem in the Exa dashboard.
HACKATHON_CREDIT_CODE = "EXA5OCT4HACK"
HACKATHON_CREDIT_URL = f"https://dashboard.exa.ai/billing?coupon={HACKATHON_CREDIT_CODE}"
OUTPUT_DIR = Path(__file__).parent / "out"

# The shape of the action package the agent prepares. Exa's deep search fills
# this in from the sources it reads, with citations returned as "grounding".
ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "Two or three sentences on what the user needs to do and whether they are likely eligible.",
        },
        "steps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The steps to complete the task, in order.",
        },
        "what_you_need": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Documents, details, deadlines or fees the user needs before submitting.",
        },
        "where_to_submit": {
            "type": "string",
            "description": "The official web page, email address or contact where the action is submitted.",
        },
        "draft": {
            "type": "object",
            "description": "The prepared action, ready for the user to approve.",
            "properties": {
                "kind": {"type": "string", "description": "email, form, letter or message"},
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
        },
        "open_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Details the user must confirm or fill in before submitting.",
        },
    },
}

SYSTEM_PROMPT = (
    "You are an internet butler. Research the user's errand using official and "
    "reliable sources, such as company policy pages, government sites and regulator "
    "guidance. Work out exactly what the user needs to do, then prepare the final "
    "action so the user only has to review and approve it. Use only facts found in "
    "the sources. Where a detail about the user is missing, leave a clear "
    "placeholder like [BOOKING REFERENCE] and list it under open_questions."
)


def exa_search(payload: dict) -> dict:
    """Call the Exa search endpoint and return the JSON response."""
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        sys.exit(
            "Set EXA_API_KEY first. Get a key at https://dashboard.exa.ai/api-keys\n"
            f"Hackathon participants: claim free credits at {HACKATHON_CREDIT_URL}"
        )

    response = requests.post(
        EXA_SEARCH_URL,
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if response.status_code == 402:
        sys.exit(
            "Exa returned 402: your account is out of credits.\n"
            f"Claim free hackathon credits at {HACKATHON_CREDIT_URL}"
        )
    if response.status_code != 200:
        sys.exit(f"Exa returned {response.status_code}: {response.text[:500]}")
    return response.json()


def prepare_action(errand: str, details: str, notes: str = "") -> dict:
    """Research the errand and prepare an action package for approval."""
    instructions = SYSTEM_PROMPT
    if details:
        instructions += f"\n\nWhat the user has told you about themselves: {details}"
    if notes:
        instructions += f"\n\nThe user reviewed an earlier draft and asked for these changes: {notes}"

    data = exa_search(
        {
            "query": errand,
            "type": "deep",
            "numResults": 10,
            "systemPrompt": instructions,
            "outputSchema": ACTION_SCHEMA,
            "contents": {"highlights": {"maxCharacters": 800}},
        }
    )

    output = data.get("output") or {}
    content = output.get("content") or {}
    if isinstance(content, str):
        # Some responses return the structured output as a JSON string.
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {"summary": content}

    return {
        "errand": errand,
        "action": content,
        "grounding": output.get("grounding", []),
        "sources": [
            {"title": r.get("title"), "url": r.get("url")} for r in data.get("results", [])
        ],
    }


def show(package: dict) -> None:
    """Print the action package for the user to review."""
    action = package["action"]
    line = "-" * 70

    print(f"\n{line}\nERRAND: {package['errand']}\n{line}")
    print(f"\n{action.get('summary', '(no summary returned)')}\n")

    if action.get("steps"):
        print("Steps:")
        for i, step in enumerate(action["steps"], 1):
            print(f"  {i}. {step}")
    if action.get("what_you_need"):
        print("\nWhat you need:")
        for item in action["what_you_need"]:
            print(f"  - {item}")
    if action.get("where_to_submit"):
        print(f"\nWhere to submit: {action['where_to_submit']}")

    draft = action.get("draft") or {}
    if draft:
        print(f"\n{line}\nPREPARED {str(draft.get('kind', 'action')).upper()}\n{line}")
        if draft.get("to"):
            print(f"To: {draft['to']}")
        if draft.get("subject"):
            print(f"Subject: {draft['subject']}")
        print(f"\n{draft.get('body', '')}")

    if action.get("open_questions"):
        print(f"\n{line}\nCONFIRM BEFORE SENDING")
        for q in action["open_questions"]:
            print(f"  - {q}")

    if package["sources"]:
        print(f"\n{line}\nSOURCES")
        for s in package["sources"]:
            print(f"  - {s['title']}: {s['url']}")
    print()


def submit_action(package: dict) -> Path:
    """Save the approved action.

    This is where a team would connect the final step: sending the email,
    filling the form with a browser automation tool, or handing off to an
    inbox. The starter saves the approved package so nothing is sent without
    the user knowing.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"approved_{datetime.now():%Y%m%d_%H%M%S}.json"
    path.write_text(json.dumps(package, indent=2))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Internet Butler starter, powered by Exa")
    parser.add_argument("errand", help="The task, in plain language")
    parser.add_argument("--details", default="", help="Facts about the user to fill into the draft")
    parser.add_argument("--yes", action="store_true", help="Skip the approval prompt and save the result")
    args = parser.parse_args()

    notes = ""
    while True:
        print("Researching with Exa deep search. This can take up to a minute...")
        package = prepare_action(args.errand, args.details, notes)
        show(package)

        if args.yes:
            choice = "y"
        else:
            choice = input("Approve this action? [y]es / [e]dit / [n]o: ").strip().lower()

        if choice.startswith("y"):
            path = submit_action(package)
            print(f"Approved and saved to {path}")
            return
        if choice.startswith("e"):
            notes = input("What should change? ")
            continue
        print("Discarded. Nothing was saved or sent.")
        return


if __name__ == "__main__":
    main()
