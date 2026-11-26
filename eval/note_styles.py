"""
How does grid extraction hold up across different kinds of notes?

Cases are generated from templates in code (no LLM writes notes), so the gold
label of every grid item is known by construction. Each case rates a random
subset of the 28 mental-function items; all other items must stay empty.

Styles
  structured   "- Judgment — understand consequences: some limitations" (control)
  sparse       clinic shorthand, 1-3 items rated, little else in the note
  paraphrase   item and scale reworded: "moderate difficulty staying focused"
  functional   no ratings at all, only behaviour: "Cannot complete a purchase;
               spouse handles all money". Severity is implied by the behaviour.
  distractor   paraphrased ratings buried in off-topic material, plus traps:
               a family member's mental problems and physically caused
               limitations, which must not be rated for the patient

Gold mapping (a judgement call, documented here so it can be challenged):
  some_limitations   mild / moderate difficulty; does it with reminders,
                     extra time or occasional help
  severe_limitations marked / extreme difficulty; cannot do it, or someone
                     else has to do it for them
  no_limitations     intact / does it independently

  python eval/note_styles.py --variants v1_schema v3_select
  python eval/note_styles.py --write-cases   # also save eval/cases/note_styles.jsonl
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import grid_copy as gc  # noqa: E402

P = gc.GRID_PREFIX
RATINGS = ("no_limitations", "some_limitations", "severe_limitations")

# key suffix -> (structured label, shorthand, paraphrased gerund phrase,
#                functional: none, some, severe)
ITEMS: dict[str, tuple[str, str, str, str, str, str]] = {
    "adaptive_adapt_to_change": (
        "Adaptive functioning — adapt to change", "adapting to chg", "coping when plans or routines change",
        "Copes well when plans change at short notice.",
        "Gets unsettled when routines change but settles with some reassurance.",
        "Any change to the daily routine leads to a shutdown lasting hours; family must plan every day in advance."),
    "adaptive_express_needs": (
        "Adaptive functioning — express basic needs", "expressing needs", "communicating basic needs such as hunger or pain",
        "Communicates needs such as hunger or pain without difficulty.",
        "Sometimes does not mention pain unless asked directly.",
        "Does not communicate hunger, thirst or pain; caregivers have to anticipate all basic needs."),
    "adaptive_go_into_community": (
        "Adaptive functioning — go into the community", "community access", "leaving the house and getting around the community",
        "Goes out to shops and appointments alone.",
        "Goes out alone to familiar places only and avoids busy areas.",
        "Has not left the house without a family member in over a year because of anxiety."),
    "adaptive_transactions": (
        "Adaptive functioning — simple transactions", "transactions", "handling simple purchases or banking",
        "Pays for groceries and handles banking independently.",
        "Can buy small items but needs help checking change.",
        "Cannot complete a purchase; spouse handles all money and transactions."),
    "adaptive_hygiene": (
        "Adaptive functioning — basic hygiene/self-care", "self-care", "washing, grooming and personal care",
        "Maintains personal hygiene independently.",
        "Needs reminders to shower most days.",
        "Will not wash or change clothes unless a caregiver assists every day."),
    "adaptive_everyday_tasks": (
        "Adaptive functioning — everyday tasks", "daily tasks", "managing routine daily tasks",
        "Manages household chores independently.",
        "Completes chores but takes much longer than expected and needs a written list.",
        "Cannot complete basic daily tasks such as preparing a simple meal unless someone does it with them."),
    "attention_danger_awareness": (
        "Attention — awareness of danger", "safety awareness", "recognizing danger and risk",
        "Shows good awareness of safety risks.",
        "Has occasionally left the stove on without noticing.",
        "Has walked into traffic twice this year and cannot be left alone near roads."),
    "attention_impulse_control": (
        "Attention — impulse control", "impulse ctrl", "controlling impulses",
        "No problems with impulsivity.",
        "Occasionally interrupts others and makes impulsive purchases.",
        "Acts on impulses constantly, including spending all savings in one day and walking out of work mid-shift."),
    "concentration_focus": (
        "Concentration — focus on simple tasks", "focus", "staying focused on a simple task",
        "Can focus on a task for an hour without difficulty.",
        "Loses focus on simple tasks after 10-15 minutes.",
        "Cannot stay on a simple task such as folding laundry for more than a minute or two."),
    "concentration_short_term_memory": (
        "Concentration — short-term information", "STM", "taking in and recalling new information",
        "Takes in and recalls new information well.",
        "Needs new information repeated a few times before it is retained.",
        "Cannot recall what was said a few minutes earlier, even after repetition."),
    "goal_make_plans": (
        "Goal-setting — make and carry out plans", "planning", "planning and following through on daily plans",
        "Plans the day and follows through.",
        "Makes plans but often needs help to follow through.",
        "Cannot make or follow even a simple plan for the day without step-by-step direction."),
    "goal_self_direct": (
        "Goal-setting — self-direct to begin tasks", "initiation", "starting tasks without being prompted",
        "Starts tasks independently.",
        "Usually needs one prompt to start morning tasks.",
        "Will not begin any task, including getting out of bed, unless prompted repeatedly."),
    "judgment_clothing": (
        "Judgment — weather-appropriate clothing", "clothing choice", "dressing appropriately for the weather",
        "Dresses appropriately for the weather.",
        "Sometimes underdresses in cold weather.",
        "Regularly goes out in winter in shorts and sandals unless someone chooses their clothes."),
    "judgment_own_treatment": (
        "Judgment — decisions about own treatment", "tx decisions", "making decisions about their own care and welfare",
        "Makes informed decisions about their own treatment.",
        "Needs help weighing treatment options but can decide with support.",
        "Cannot make decisions about treatment; a substitute decision-maker has been appointed."),
    "judgment_exploitation_risk": (
        "Judgment — risk of being taken advantage of", "exploitation risk", "recognizing when they are being taken advantage of",
        "Recognizes scams and is not easily taken advantage of.",
        "Was nearly caught by a phone scam last year before a friend intervened.",
        "Has repeatedly given money to strangers and does not recognize when being exploited."),
    "judgment_consequences": (
        "Judgment — understand consequences", "consequences", "understanding the consequences of their actions",
        "Understands the consequences of their decisions.",
        "Sometimes does not think through the consequences of decisions.",
        "Does not grasp consequences: quit their job and stopped paying rent without concern."),
    "memory_personal_info": (
        "Memory — basic personal information", "personal info recall", "recalling their own address and date of birth",
        "Knows their address and date of birth.",
        "Occasionally has to check their own address.",
        "Cannot state their own address or date of birth."),
    "memory_important_info": (
        "Memory — material of importance", "recall of important info", "remembering things that matter to them",
        "Remembers appointments and important events.",
        "Forgets some appointments unless they are written down.",
        "Forgets important events such as a family death and has to be told again."),
    "memory_simple_instructions": (
        "Memory — simple instructions", "instructions", "remembering simple instructions",
        "Remembers simple instructions.",
        "Needs simple instructions repeated once or twice.",
        "Cannot retain a two-step instruction even when it is repeated."),
    "perception_reality": (
        "Perception — understanding of reality", "reality testing", "understanding what is real around them",
        "Reality testing intact.",
        "At times misinterprets ordinary events as being about them.",
        "Holds a fixed belief that neighbours are controlling their thoughts."),
    "perception_delusions": (
        "Perception — reality vs delusions/hallucinations", "hallucinations", "telling hallucinations apart from reality",
        "No hallucinations or delusions.",
        "Hears voices occasionally but recognizes they are not real.",
        "Hears voices daily and acts on them, believing them to be real."),
    "problem_identify": (
        "Problem-solving — identify everyday problems", "problem ID", "noticing everyday problems",
        "Notices everyday problems readily.",
        "Sometimes does not notice problems such as an overdue bill until reminded.",
        "Does not recognize problems such as a flooded kitchen or an empty fridge."),
    "problem_implement": (
        "Problem-solving — implement solutions", "problem solving", "working out how to fix simple problems",
        "Solves everyday problems independently.",
        "Can fix simple problems with some guidance.",
        "Cannot work out what to do about even simple problems, such as a burnt-out light bulb."),
    "regulation_behaviour": (
        "Regulation — appropriate behaviour", "behaviour", "behaving appropriately in social situations",
        "Behaviour appropriate in all settings.",
        "Occasionally makes inappropriate comments in public.",
        "Frequent outbursts in public; has been asked to leave stores several times."),
    "regulation_emotions": (
        "Regulation — emotional responses", "emotional responses", "showing emotions that fit the situation",
        "Emotional responses are appropriate.",
        "Emotional reactions are sometimes out of proportion.",
        "Laughs at sad news and becomes tearful for no reason several times a day."),
    "regulation_mood": (
        "Regulation — mood (risk of harm)", "mood", "keeping their mood stable enough to stay safe",
        "Mood stable with no safety concerns.",
        "Mood swings occasionally lead to risky behaviour such as reckless driving.",
        "Mood swings have led to self-harm twice this year."),
    "comprehension_nonverbal": (
        "Comprehension — non-verbal information", "non-verbal comprehension", "reading facial expressions and body language",
        "Reads non-verbal cues well.",
        "Sometimes misses non-verbal cues.",
        "Cannot interpret facial expressions or gestures at all."),
    "comprehension_verbal": (
        "Comprehension — verbal information", "verbal comprehension", "understanding spoken information",
        "Understands spoken information without difficulty.",
        "Needs complex spoken information simplified.",
        "Does not understand simple spoken requests."),
}

STRUCT_WORD = {"no_limitations": "no limitations", "some_limitations": "some limitations",
               "severe_limitations": "severe limitations"}
SHORT_WORD = {"no_limitations": "WNL", "some_limitations": "mild-mod impairment",
              "severe_limitations": "marked impairment"}
PARA_ADJ = {"some_limitations": ["mild difficulty", "moderate difficulty", "some trouble"],
            "severe_limitations": ["marked difficulty", "extreme difficulty", "profound difficulty"]}

DIAGNOSES = ["ADHD", "Major depressive disorder", "Generalized anxiety disorder", "Bipolar I disorder",
             "Schizophrenia", "Autism spectrum disorder", "Mild intellectual disability", "PTSD"]

OFF_TOPIC = [
    "Social history: lives in a rented apartment, smokes about half a pack a day (12 pack-years), drinks socially.",
    "Physical exam: BP 128/82, HR 74, BMI 31. Heart sounds normal, chest clear.",
    "Labs from March: LDL 3.9, HbA1c 6.1, TSH normal. Repeat lipids in 6 months.",
    "Other medications: ramipril 5 mg daily, vitamin D 1000 IU. Flu shot given today.",
    "Screening: colonoscopy due next year. Declined shingles vaccine for now.",
    "Right knee osteoarthritis, managed with physiotherapy and acetaminophen as needed.",
    "Seasonal allergies, uses cetirizine in spring. No known drug allergies.",
    "Reports poor sleep, around 5 hours a night; sleep hygiene discussed.",
]

# Traps: sentences that sound like a grid rating but are not about the patient's
# mental functions. The listed item must stay empty (it is never rated in that case).
TRAPS = {
    "memory_personal_info": "Patient's mother, who has Alzheimer's, can no longer remember her own address or date of birth.",
    "adaptive_transactions": "Patient's brother, who lives with them, cannot handle money and has been scammed several times.",
    "attention_impulse_control": "Patient's son has severe ADHD with very poor impulse control, which is a major family stressor.",
    "regulation_mood": "Spouse reports that their own mood has been low since the patient's diagnosis.",
    "adaptive_go_into_community": "Rarely goes out in winter because of knee pain and icy sidewalks.",
    "adaptive_everyday_tasks": "Housework is slow because of right knee pain when kneeling or using stairs.",
}

STYLES = ("structured", "sparse", "paraphrase", "functional", "distractor")


def _rate(rng: random.Random, n: int) -> dict[str, str]:
    keys = rng.sample(sorted(ITEMS), n)
    return {P + k: rng.choices(RATINGS, weights=(1, 2, 2))[0] for k in keys}


def _para_line(rng: random.Random, suffix: str, rating: str) -> str:
    gerund = ITEMS[suffix][2]
    if rating == "no_limitations":
        return rng.choice([f"No difficulty {gerund}.", f"{gerund[0].upper()}{gerund[1:]} is not a concern."])
    return f"Has {rng.choice(PARA_ADJ[rating])} with {gerund}."


def render(rng: random.Random, style: str, rated: dict[str, str], dx: list[str], traps: list[str]) -> str:
    items = list(rated.items())
    rng.shuffle(items)
    sfx = [(k[len(P):], v) for k, v in items]
    head = f"Diagnoses: {', '.join(dx)}."

    if style == "structured":
        body = "\n".join(f"- {ITEMS[s][0]}: {STRUCT_WORD[v]}" for s, v in sfx)
        return f"{head}\n\nMental function ratings compared to peers:\n{body}\n"
    if style == "sparse":
        body = ". ".join(f"{ITEMS[s][1][0].upper()}{ITEMS[s][1][1:]}: {SHORT_WORD[v]}" for s, v in sfx)
        return f"Pt w/ {dx[0]}. Seen today for DTC form. {body}.\n"
    if style == "paraphrase":
        return f"{head}\n\n" + " ".join(_para_line(rng, s, v) for s, v in sfx) + "\n"
    if style == "functional":
        idx = {"no_limitations": 3, "some_limitations": 4, "severe_limitations": 5}
        return f"{head}\n\nFunctional history (from patient and family):\n" + \
            " ".join(ITEMS[s][idx[v]] for s, v in sfx) + "\n"
    if style == "distractor":
        paras = rng.sample(OFF_TOPIC, 5) + [TRAPS[t] for t in traps]
        mental = "Mental health: " + " ".join(_para_line(rng, s, v) for s, v in sfx)
        rng.shuffle(paras)
        paras.insert(rng.randrange(1, len(paras)), mental)
        return f"{head}\n\n" + "\n\n".join(paras) + "\n"
    raise ValueError(style)


def make_cases(n_per_style: int = 8, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    cases = []
    for style in STYLES:
        for i in range(n_per_style):
            rated = _rate(rng, rng.randint(1, 3) if style == "sparse" else rng.randint(4, 10))
            traps = []
            if style == "distractor":
                free = [t for t in TRAPS if P + t not in rated]
                traps = rng.sample(free, min(2, len(free)))
            dx = rng.sample(DIAGNOSES, rng.randint(1, 2))
            cases.append({"id": f"{style}-{i:02d}", "source": "note_styles", "style": style, "split": "dev",
                          "notes": render(rng, style, rated, dx, traps), "gold": rated,
                          "traps": [P + t for t in traps]})
    return cases


# ── Scoring ──────────────────────────────────────────────────────────────────

def summarize(grid_keys: list[str], cases: list[dict], preds: dict[str, dict]) -> dict:
    by_style: dict[str, Counter] = defaultdict(Counter)
    n: Counter = Counter()
    for c in cases:
        if c["id"] not in preds:
            continue
        p = preds[c["id"]]
        s = gc.score_grid(grid_keys, c["gold"], p)
        by_style[c["style"]].update(s["counts"])
        by_style[c["style"]]["trap_items"] += len(c["traps"])
        by_style[c["style"]]["trap_filled"] += sum(p.get(t) not in gc.EMPTY for t in c["traps"])
        n[c["style"]] += 1
    out = {}
    for style, c in by_style.items():
        rated = c["correct"] + c["wrong"] + c["omitted"]
        halluc = c["copied"] + c["other"] + c["fabricated"]
        out[style] = {"n_cases": n[style], "counts": dict(c),
                      "rated_accuracy": c["correct"] / rated if rated else None,
                      "wrong": c["wrong"], "omitted": c["omitted"],
                      "halluc_per_case": halluc / n[style],
                      "copied_per_case": c["copied"] / n[style],
                      "trap_filled": c["trap_filled"], "trap_items": c["trap_items"]}
    return out


# ── Runner ───────────────────────────────────────────────────────────────────

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--variants", nargs="+", default=["v1_schema", "v3_select"],
                    choices=["v1_schema", "v2_evidence", "v3_select"])
    ap.add_argument("--per-style", type=int, default=8)
    ap.add_argument("--styles", nargs="+", default=list(STYLES), choices=STYLES)
    ap.add_argument("--write-cases", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT.parent / "backend"))
    from formfiller.forms import get_form
    from formfiller.llm.ollama import Ollama

    form = get_form("t2201")
    chunk = next(c for c in form.chunks if c.id == gc.GRID_CHUNK)
    grid_keys = list(chunk.keys)
    cases = [c for c in make_cases(args.per_style) if c["style"] in args.styles]
    if args.write_cases:
        out = ROOT / "cases" / "note_styles.jsonl"
        out.write_text("".join(json.dumps(c) + "\n" for c in cases))
        print(f"wrote {len(cases)} cases to {out}")

    summary_path = ROOT / "results" / "note_styles.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    async with Ollama() as llm:
        for variant in args.variants:
            name = f"{args.model}|{variant}"
            raw = ROOT / "results" / "raw" / "note_styles" / name.replace(":", "-").replace("|", "__")
            raw.mkdir(parents=True, exist_ok=True)
            preds = {}
            print(f"\n== {name} on {len(cases)} cases", flush=True)
            for i, c in enumerate(cases, 1):
                f = raw / f"{c['id']}.json"
                if f.exists() and not args.no_cache:
                    r = json.loads(f.read_text())
                else:
                    r = await gc.predict(form, chunk, c["notes"], variant, args.model, llm)
                    f.write_text(json.dumps(r))
                    print(f"  {i}/{len(cases)} {c['id']} {r['ms'] / 1000:.0f}s"
                          f"{'  ERR ' + '; '.join(r['errors']) if r['errors'] else ''}", flush=True)
                preds[c["id"]] = r["values"]
            summary[name] = summarize(grid_keys, cases, preds)
            summary_path.write_text(json.dumps(summary, indent=1))

    print("\n| Pipeline | Style | Cases | Rated acc. | Wrong | Omitted | Halluc/case | Copied/case | Traps filled |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, by_style in summary.items():
        for style in STYLES:
            s = by_style.get(style)
            if not s:
                continue
            acc = f"{s['rated_accuracy']:.0%}" if s["rated_accuracy"] is not None else "–"
            traps = f"{s['trap_filled']}/{s['trap_items']}" if s["trap_items"] else "–"
            print(f"| `{name}` | {style} | {s['n_cases']} | {acc} | {s['wrong']} | {s['omitted']} | "
                  f"{s['halluc_per_case']:.1f} | {s['copied_per_case']:.1f} | {traps} |")


if __name__ == "__main__":
    asyncio.run(main())
