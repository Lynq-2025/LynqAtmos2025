import json
import os
import random
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Fixed model
MODEL_NAME = "gemini-2.5-flash"

# Config (editable inside file if desired)
PHISH_PCT = 0.3
EDGE_PCT = 0.15
MAX_RETRIES_PER_MESSAGE = 2
RETRY_DELAY_SECONDS = 0.6
DEFAULT_OUTFILE = "labeled_batch_generated_gemini.json"

# Create client (assumes environment credentials configured)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)


# Helper: extract JSON object from model text
def extract_json_from_text(text):
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"(\{(?:.|\n)*\})", text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    raise ValueError("No JSON object found in model output.")


# Ask Gemini to generate one message of a given kind
def ask_gemini_for(kind):
    prompt = f"""
You are an email/message generator. Output ONLY a single JSON object with EXACT keys:
  "sender", "subject", "body"

Rules:
- 'sender' must be a plausible email address string.
- 'subject' must be a short subject line.
- 'body' must be a multi-line realistic message [about 4 sentences (3-4 lines), concise].
- Do NOT output any extra text or commentary — only the JSON object.

If kind is PHISHING:
 - Include urgency, social-engineering cues, and at least one suspicious example link (http://...).
If kind is LEGITIMATE:
 - Produce normal internal/external message content (no malicious links).
If kind is EDGE:
 - Produce an ambiguous/borderline message (might look suspicious).

Kind: {kind}

Return the JSON object only.
""".strip()

    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="text/plain",
            max_output_tokens=700,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    text = resp.text
    return extract_json_from_text(text)


# Generate with retries and validate keys
def generate_one_with_retries(
    kind, max_retries=MAX_RETRIES_PER_MESSAGE, delay=RETRY_DELAY_SECONDS
):
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            email = ask_gemini_for(kind)

            if not isinstance(email, dict):
                raise ValueError("Model output not a JSON object.")
            
            missing = [k for k in ("sender", "subject", "body") if k not in email]

            if missing:
                raise ValueError(f"Missing keys: {missing}")

            for k in ("sender", "subject", "body"):
                email[k] = str(email[k]).strip()

            return email

        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(delay * (2**attempt))
            else:
                raise last_exc


# Generate a labeled batch
def generate_batch(
    count, phish_pct=PHISH_PCT, edge_pct=EDGE_PCT, seed=None, delay_between=0.2
):
    if phish_pct + edge_pct > 1.0:
        raise ValueError("phish_pct + edge_pct must be <= 1.0")
    if seed is not None:
        random.seed(seed)
    batch = []
    for i in range(count):
        r = random.random()
        if r < phish_pct:
            kind = "PHISHING"
        elif r < phish_pct + edge_pct:
            kind = "EDGE"
        else:
            kind = "LEGITIMATE"

        print(f"[{i + 1}/{count}] Generating {kind} ...", flush=True)

        try:
            email = generate_one_with_retries(kind)
        except Exception as e:
            print(
                f"[error] generation failed for item {i + 1}: {e}; inserting fallback message."
            )
            email = {
                "email": {
                    "sender": f"failed-{i + 1}@example.com",
                    "subject": f"generation_failed_{i + 1}",
                    "body": f"Generation failed: {str(e)[:200]}",
                }
            }
        # attach the ground-truth label so organizers have answers
        batch.append({"email": email, "label": kind})
        time.sleep(delay_between)
    return batch


def create_batch(num_messages: int):
    batch = generate_batch(num_messages)
    with open("emails.json", "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False)


def main():
    # batch = generate_batch(10)
    # print(json.dumps(batch, ensure_ascii=False))
    create_batch(20)


if __name__ == "__main__":
    main()

# CLI entrypoint
# def main():
# parser = argparse.ArgumentParser()
# parser.add_argument(
#     "--count", type=int, help="Number of messages to generate (required)"
# )
# parser.add_argument(
#     "--out", type=str, default=DEFAULT_OUTFILE, help="Output JSON filename"
# )
# parser.add_argument(
#     "--phish-pct", type=float, default=PHISH_PCT, help="Fraction phishing (0-1)"
# )
# parser.add_argument(
#     "--edge-pct", type=float, default=EDGE_PCT, help="Fraction edge cases (0-1)"
# )
# parser.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
# args = parser.parse_args()

# if args.count is None or args.count <= 0:
#     print("Please provide a positive --count value, e.g. --count 20")
#     return

# print("Generating", args.count, "messages...")
# batch = generate_batch(
#     args.count, phish_pct=args.phish_pct, edge_pct=args.edge_pct, seed=args.seed
# )

# # Save labeled batch (organizer copy)
# with open(args.out, "w", encoding="utf-8") as f:
#     json.dump(batch, f, indent=2, ensure_ascii=False)
# print(f"Saved labeled batch ({len(batch)} items) to {args.out}")

# # Also save an unlabelled version for participants (optional convenience)
# participant_out = args.out.replace(".json", "_for_participants.json")
# unlabeled = [{k: v for k, v in item.items() if k != "label"} for item in batch]
# with open(participant_out, "w", encoding="utf-8") as f:
#     json.dump(unlabeled, f, indent=2, ensure_ascii=False)
# print(f"Saved participant copy (no labels) to {participant_out}")


# if __name__ == "__main__":
#     main()
