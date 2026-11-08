"""
Synthetic eval cases: gold labels first, then notes written from them.

  python eval/generate.py --n 40 --model qwen3.5:9b --out eval/cases/synthetic.jsonl

1. Sample a coherent set of gold values (sections, diagnoses, answers).
   Fields left out of the gold are things the note must NOT say.
2. A local LLM writes clinical notes in one of several styles that express
   exactly those facts.
3. A verification pass asks the LLM whether each gold fact is stated, and
   whether any non-gold question is answered anyway. Failing fields become "*"
   (unscored) instead of being trusted.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from formfiller.core.form import NOT_MENTIONED, FormSpec  # noqa: E402
from formfiller.forms import get_form  # noqa: E402
from formfiller.llm.ollama import Ollama  # noqa: E402

# ── Curated clinical content ─────────────────────────────────────────────────

CONTENT = {
    "vision": {
        "conditions": ["Primary open-angle glaucoma", "Diabetic retinopathy", "Retinitis pigmentosa",
                       "Age-related macular degeneration", "Optic atrophy", "Stargardt disease"],
        "devices": ["handheld magnifiers and large-print materials", "white cane and screen reader software",
                    "CCTV video magnifier", "high-contrast lighting and orientation and mobility training"],
        "examples": ["cannot read standard print even with magnification", "unable to recognize faces across a room",
                     "needs assistance to navigate unfamiliar places", "cannot see curbs or steps in dim light"],
    },
    "speaking": {
        "conditions": ["Spasmodic dysphonia", "Post-stroke expressive aphasia", "Amyotrophic lateral sclerosis with dysarthria",
                       "Laryngectomy for laryngeal cancer", "Severe stuttering"],
        "devices": ["electrolarynx", "speech-generating device", "voice amplifier", "weekly speech-language therapy"],
        "examples": ["strangers cannot understand him on the phone", "needs to write things down to be understood",
                     "takes several minutes to order at a counter", "family must interpret for her at appointments"],
    },
    "hearing": {
        "conditions": ["Bilateral sensorineural hearing loss", "Meniere's disease", "Otosclerosis",
                       "Noise-induced hearing loss", "Auditory neuropathy"],
        "devices": ["bilateral behind-the-ear hearing aids", "cochlear implant (right) and hearing aid (left)",
                    "FM system", "bone-anchored hearing aid"],
        "examples": ["relies on lip-reading in all conversations", "cannot follow a conversation with a familiar person in a quiet room",
                     "needs constant repetition", "uses text messaging instead of phone calls"],
    },
    "walking": {
        "conditions": ["Multiple sclerosis", "Severe bilateral knee osteoarthritis", "Spinal stenosis",
                       "Parkinson's disease", "Below-knee amputation", "Cerebral palsy"],
        "devices": ["four-wheeled walker", "forearm crutches", "power wheelchair for distances", "ankle-foot orthosis and cane",
                    "physiotherapy twice weekly"],
        "examples": ["needs more than 10 minutes to walk 100 metres", "must stop and rest every 20 metres",
                     "cannot manage stairs without assistance", "falls several times a month"],
    },
    "eliminating": {
        "conditions": ["Crohn's disease with ileostomy", "Neurogenic bladder secondary to spinal cord injury",
                       "Ulcerative colitis", "Radiation proctitis"],
        "devices": ["ostomy appliance", "intermittent self-catheterization", "indwelling Foley catheter", "biologic therapy (infliximab)"],
        "examples": ["needs to empty the ostomy bag many times per day", "requires catheterization every 4 hours, taking 20 minutes each time",
                     "frequent urgent incontinence episodes", "cannot leave home without planning around washroom access"],
    },
    "feeding": {
        "conditions": ["Rheumatoid arthritis of the hands", "Oropharyngeal dysphagia after stroke", "Essential tremor",
                       "Scleroderma with hand contractures"],
        "devices": ["weighted adaptive utensils", "thickened fluids and modified-texture diet", "plate guard and rocker knife",
                    "occupational therapy"],
        "examples": ["cannot open containers or cut food", "meals take more than an hour",
                     "cannot prepare a simple meal safely", "chokes on regular-texture food"],
    },
    "dressing": {
        "conditions": ["Rheumatoid arthritis", "Post-stroke left hemiparesis", "Severe frozen shoulder (bilateral)",
                       "Advanced multiple sclerosis"],
        "devices": ["button hook and long-handled shoe horn", "sock aid and elastic laces", "occupational therapy"],
        "examples": ["needs help with buttons, zippers and shoes", "dressing takes over 45 minutes",
                     "cannot put on a coat without assistance", "must sit and rest repeatedly while dressing"],
    },
    "mental": {
        "conditions": ["Schizophrenia", "Bipolar I disorder", "Autism spectrum disorder", "Major depressive disorder",
                       "ADHD", "Moderate traumatic brain injury", "Generalized anxiety disorder", "Intellectual disability"],
        "devices": ["cognitive behavioural therapy", "pill organizer and phone reminders", "daily written schedule",
                    "assertive community treatment team", "occupational therapy for life skills"],
        "examples": [],
    },
}
LST_PROFILES = [
    {"condition": "lst_q2_condition_type1_diabetes", "therapy": ["lst_q2_therapy_insulin_injections", "lst_q2_therapy_insulin_pump"],
     "activities": "checking blood glucose, calculating carbohydrate intake and insulin doses, administering insulin",
     "times": (14, 35), "hours": (14, 20)},
    {"condition": "lst_q2_condition_renal_disease", "therapy": ["lst_q2_therapy_hemodialysis", "lst_q2_therapy_peritoneal_dialysis"],
     "activities": "dialysis sessions including travel-free setup and monitoring",
     "times": (3, 7), "hours": (14, 30)},
    {"condition": "lst_q2_condition_cystic_fibrosis", "therapy": ["lst_q2_therapy_chest_physio"],
     "activities": "airway clearance with chest physiotherapy and nebulized medications",
     "times": (14, 21), "hours": (14, 18)},
]
IMPAIRMENTS = ["vision", "speaking", "hearing", "walking", "eliminating", "feeding", "dressing", "mental"]
SIMPLE = ["speaking", "hearing", "walking", "eliminating", "feeding", "dressing"]

STYLES = {
    "structured": "a structured summary with a heading for each affected area, written in full sentences",
    "soap": "a SOAP-format progress note (S:/O:/A:/P:) with common clinical abbreviations (pt, hx, dx, f/u, w/, yrs)",
    "letter": "a consultation letter to the patient's family physician, in flowing narrative paragraphs",
    "terse": "terse bullet-point clinic notes with heavy abbreviations and sentence fragments",
    "narrative": "a narrative clinic note that also includes unrelated history (vitals, allergies, unrelated medications) "
                 "and a couple of pertinent negatives about body systems not listed in the facts",
}


# ── 1. Sample gold values ────────────────────────────────────────────────────

def _p(rng, prob):
    return rng.random() < prob


def sample_gold(form: FormSpec, rng: random.Random) -> tuple[dict, list[str]]:
    gold: dict = {}
    kind = rng.choices(["single", "multi", "cumulative", "lst"], weights=[40, 35, 13, 12])[0]
    if kind == "single":
        sections = rng.sample(IMPAIRMENTS, 1)
    elif kind in ("multi", "cumulative"):
        sections = rng.sample(IMPAIRMENTS, rng.choice([2, 2, 3]))
    else:
        sections = []

    for s in sections:
        marked = kind != "cumulative"
        onset = rng.randint(1998, 2024)
        content = CONTENT[s]
        dx = rng.choice(content["conditions"])
        gold[f"{s}_q1_conditions"] = f"{dx} ({rng.randint(max(1990, onset - 3), onset)})"
        if _p(rng, .7) and f"{s}_q3_devices_therapy" in form.fields:
            gold[f"{s}_q3_devices_therapy"] = rng.choice(content["devices"])

        if s in SIMPLE:
            gold[f"{s}_q4_examples"] = "; ".join(rng.sample(content["examples"], 2))
            if _p(rng, .5) and f"{s}_q2_takes_medication" in form.fields:
                gold[f"{s}_q2_takes_medication"] = rng.choice(["yes", "no"])
            if _p(rng, .85):
                gold[f"{s}_q5_unable_or_inordinate"] = "yes" if marked else "no"
            if marked and _p(rng, .75):
                gold[f"{s}_q6_all_or_substantially"] = "yes" if _p(rng, .85) else "no"
            if s == "hearing" and _p(rng, .7):
                levels = ["mild", "moderate", "moderate_to_severe", "severe", "profound"]
                lo = 2 if marked else 1
                gold["hearing_q2_left_ear"] = rng.choice(levels[lo:])
                gold["hearing_q2_right_ear"] = rng.choice(levels[lo:])
            q = {"year": 7, "lasted": 8, "improved": 9}
        elif s == "vision":
            for eye in ("left", "right"):
                if _p(rng, .7):
                    m = rng.choice(["snellen", "snellen", "count_fingers", "hand_motion", "light_perception"])
                    gold[f"vision_q2_{eye}_measure"] = m
                    if m == "snellen":
                        gold[f"vision_q2_{eye}_acuity_num1"] = "20"
                        gold[f"vision_q2_{eye}_acuity_num2"] = rng.choice(["200", "400", "100", "70"] if marked else ["40", "50", "70"])
                if _p(rng, .3):
                    gold[f"vision_q2_{eye}_field_degrees"] = str(rng.choice([10, 15, 20, 40]))
            if _p(rng, .8):
                gold["vision_q3_meets_criteria"] = "yes" if marked else "no"
            q = {"year": 4, "lasted": 5, "improved": 6}
        else:  # mental
            meds = _p(rng, .7)
            gold["mental_q2_takes_medication"] = "yes" if meds else "no"
            if meds and _p(rng, .6):
                gold["mental_q2_needs_supervision_for_meds"] = rng.choice(["yes", "no"])
            if meds and _p(rng, .6):
                gold["mental_q2_medication_effectiveness"] = rng.choice(
                    ["effective", "moderately_effective", "mildly_effective", "ineffective"])
            if _p(rng, .7):
                impaired = marked and _p(rng, .8)
                gold["mental_q4_impaired_independence"] = "yes" if impaired else "no"
                if impaired:
                    for k in rng.sample(["mental_q4_adult_assisted_living", "mental_q4_adult_community_services",
                                         "mental_q4_adult_hospitalization", "mental_q4_adult_family_support"], rng.randint(1, 2)):
                        gold[k] = True
            grid = [k for k in form.fields if k.startswith("mental_q5_")]
            for k in rng.sample(grid, rng.randint(3, 10)):
                gold[k] = rng.choice(["some_limitations", "severe_limitations"] if marked else
                                     ["no_limitations", "some_limitations"])
            if _p(rng, .85):
                gold["mental_q7_unable_or_inordinate"] = "yes" if marked else "no"
            if marked and _p(rng, .7):
                gold["mental_q8_all_or_substantially"] = "yes"
            q = {"year": 9, "lasted": 10, "improved": 11}

        if _p(rng, .85):
            yk = next(k for k in form.fields if k.startswith(f"{s}_q{q['year']}_year"))
            gold[yk] = str(onset)
        if _p(rng, .85):
            gold[f"{s}_q{q['lasted']}_lasted_12mo"] = "yes" if _p(rng, .9) else "no"
        if _p(rng, .75):
            imp = rng.choices(["no", "unsure", "yes"], weights=[6, 3, 1])[0]
            gold[f"{s}_q{q['improved']}_improved"] = imp
            if imp == "yes":
                gold[f"{s}_q{q['improved']}_year"] = str(rng.randint(2027, 2030))

    if kind == "cumulative":
        cat = {"mental": "cumulative_q1_mental_functions"}
        for s in sections:
            gold[cat.get(s, f"cumulative_q1_{s}")] = True
        gold["cumulative_q2_examples"] = "*"  # depends on how the note phrases it
        gold["cumulative_q3_exist_together"] = "yes"
        gold["cumulative_q4_equivalent_to_marked"] = "yes"
        onsets = [int(v) for k, v in gold.items() if k.endswith("_year_impaired")]
        gold["cumulative_q5_year_began"] = str(max(onsets) if onsets else rng.randint(2010, 2023))
        if _p(rng, .7):
            gold["cumulative_q6_lasted_12mo"] = "yes"
        if _p(rng, .6):
            gold["cumulative_q7_improved"] = rng.choice(["no", "unsure"])
        sections = sections + ["cumulative"]

    if kind == "lst":
        prof = rng.choice(LST_PROFILES)
        gold[prof["condition"]] = True
        gold[rng.choice(prof["therapy"])] = True
        if prof["condition"].endswith("type1_diabetes"):
            dx_year = rng.randint(2005, 2024)
            gold["lst_q1_type1_diabetes_timing"] = "prior_to_2021" if dx_year < 2021 else "2021_and_later"
            if dx_year >= 2021:
                gold["lst_q1_year_diagnosed"] = str(dx_year)
        gold["lst_q3_eligible_activities"] = prof["activities"]
        if _p(rng, .7):
            gold["lst_q4_supports_vital_function"] = "yes"
        gold["lst_q5_times_per_week"] = str(rng.randint(*prof["times"]))
        gold["lst_q6_hours_per_week"] = str(rng.randint(*prof["hours"]))
        if _p(rng, .8):
            gold["lst_q7_year_began"] = str(rng.randint(2008, 2024))
        if _p(rng, .8):
            gold["lst_q8_lasted_12mo"] = "yes"
        if _p(rng, .6):
            gold["lst_q9_improved"] = "no"
        sections = ["lst"]

    if _p(rng, .6):
        start = rng.randint(2005, 2023)
        gold["cert_year_from"] = str(start)
        if _p(rng, .5):
            gold["cert_q2_medical_info_on_file"] = "yes"
        sections = sections + ["cert"]
    return gold, sections


# ── 2. Write notes ───────────────────────────────────────────────────────────

def fact_line(form: FormSpec, key: str, value) -> str:
    f = form.fields[key]
    if f.kind == "enum":
        label = next(o.label for o in f.options if o.value == value)
        return f"- {f.description.split('. ')[0]} -> {label}"
    if f.kind == "bool":
        return f"- {f.description.split('. ')[0]} -> applies"
    return f"- {f.description.split('. ')[0]} -> {value}"


def writer_messages(form: FormSpec, gold: dict, style: str, patient: str) -> list[dict]:
    facts = "\n".join(fact_line(form, k, v) for k, v in gold.items() if v != "*")
    system = f"""You are an experienced Canadian physician writing clinical notes about a patient
named {patient}. The notes will later be used to complete a disability tax credit form,
but you are writing ordinary clinical documentation, NOT filling in the form.

Write the notes as {STYLES[style]}.

The notes must convey every one of these facts, in natural clinical language (do not copy
the question wording, do not mention question numbers or the form):
{facts}

Strict rules:
- Do not state anything else that would answer a disability-form question: no extra
  diagnoses, devices, medications for the impairment, durations, onset years, prognosis,
  or frequency statements beyond the facts above.
- Unrelated details (vitals, allergies, social history) are fine if the style calls for it.
- 120-350 words. Output only the notes."""
    return [{"role": "system", "content": system}, {"role": "user", "content": "Write the notes."}]


# ── 3. Verify ────────────────────────────────────────────────────────────────

def verify_messages(form: FormSpec, notes: str, gold: dict, sections: list[str]) -> tuple[list[dict], list[str], list[str]]:
    stated = [k for k, v in gold.items() if v != "*"]
    unstated = [k for k, f in form.fields.items()
                if f.section in sections and k not in gold and f.kind == "enum"]
    a = "\n".join(f"a{i}: {fact_line(form, k, gold[k])[2:]}" for i, k in enumerate(stated))
    b = "\n".join(f"b{i}: {form.fields[k].description.split('. ')[0]}" for i, k in enumerate(unstated))
    system = f"""You check clinical notes against a list of facts.

For each fact aN, answer true if the notes clearly state or directly imply it, else false.
For each question bN, answer true if the notes contain a clear answer to it, else false.

Facts:
{a}

Questions:
{b or "(none)"}"""
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": f"Notes:\n<<<\n{notes}\n>>>"}]
    return msgs, stated, unstated


def verify_schema(n_a: int, n_b: int) -> dict:
    props = {f"a{i}": {"type": "boolean"} for i in range(n_a)} | {f"b{i}": {"type": "boolean"} for i in range(n_b)}
    return {"type": "object", "properties": props, "required": list(props)}


PATIENTS = ["Alex Martin", "Priya Sharma", "Jean Tremblay", "Mei Chen", "Omar Haddad", "Sarah O'Neill",
            "Daniel Kowalski", "Fatima Ali", "Luc Gagnon", "Grace Okafor", "Henry Nguyen", "Isabelle Roy"]


async def make_case(form, llm, model, rng, idx, think) -> dict:
    gold, sections = sample_gold(form, rng)
    style = rng.choice(list(STYLES))
    patient = rng.choice(PATIENTS)
    r = await llm.chat(model, writer_messages(form, gold, style, patient), temperature=0.8, seed=idx,
                       think=think, num_ctx=8192)
    notes = r.content.strip()

    msgs, stated, unstated = verify_messages(form, notes, gold, sections)
    v = (await llm.chat(model, msgs, schema=verify_schema(len(stated), len(unstated)), think=think)).json()
    missing = [k for i, k in enumerate(stated) if not v.get(f"a{i}", False)]
    leaked = [k for i, k in enumerate(unstated) if v.get(f"b{i}", False)]
    for k in missing + leaked:
        gold[k] = "*"
    return {"id": f"syn-{idx:03d}", "source": "synthetic", "style": style, "sections": sections,
            "notes": notes, "gold": gold, "verified": False,
            "verification": {"unconfirmed": missing, "leaked": leaked}, "generator": model}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--model", default="qwen3.5:9b")
    ap.add_argument("--think", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--test-frac", type=float, default=0.3)
    ap.add_argument("--out", default=str(ROOT / "cases" / "synthetic.jsonl"))
    args = ap.parse_args()

    form = get_form("t2201")
    out = Path(args.out)
    done = {json.loads(l)["id"] for l in out.read_text().splitlines() if l.strip()} if out.exists() else set()
    async with Ollama() as llm:
        for i in range(args.start, args.start + args.n):
            rng = random.Random(args.seed * 100_003 + i)
            cid = f"syn-{i:03d}"
            if cid in done:
                continue
            case = await make_case(form, llm, args.model, rng, i, args.think)
            case["split"] = "test" if random.Random(i).random() < args.test_frac else "dev"
            with out.open("a") as f:
                f.write(json.dumps(case) + "\n")
            ver = case["verification"]
            print(f"{cid} [{case['split']}] {case['style']:<10} {','.join(case['sections']):<28} "
                  f"gold={sum(v != '*' for v in case['gold'].values())} "
                  f"unconfirmed={len(ver['unconfirmed'])} leaked={len(ver['leaked'])}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
