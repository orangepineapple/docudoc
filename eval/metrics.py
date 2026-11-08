"""
Score extraction results against gold labels.

Gold convention: only non-empty values are listed; anything absent is expected
to be empty (not_mentioned / false / ""). A gold value of "*" means "any answer
is acceptable" and the field is not scored.

Every scored field lands in exactly one bucket:
  correct        gold set,   prediction matches
  wrong          gold set,   prediction set but different
  omitted        gold set,   prediction empty
  hallucinated   gold empty, prediction set
  true_empty     gold empty, prediction empty
"""
from __future__ import annotations

from collections import Counter, defaultdict

from rapidfuzz import fuzz

from formfiller.core.form import NOT_MENTIONED, FormSpec

ANY = "*"
TEXT_MATCH = 60          # token_set_ratio needed for short text answers
PRESENCE_ONLY = ("_examples", "_details")  # free-form prose: scored on presence


def is_empty(v) -> bool:
    return v in (None, "", False, NOT_MENTIONED)


def field_match(form: FormSpec, key: str, gold, pred) -> bool:
    f = form.fields[key]
    if f.kind in ("enum", "bool"):
        return gold == pred
    g, p = str(gold).strip().lower(), str(pred).strip().lower()
    if f.kind in ("year", "number"):
        return g == p
    if key.endswith(PRESENCE_ONLY):
        return bool(p)
    return fuzz.token_set_ratio(g, p) >= TEXT_MATCH


def score_case(form: FormSpec, gold: dict, result: dict) -> dict:
    pred = result["values"]
    buckets: dict[str, list[str]] = defaultdict(list)
    by_kind: dict[str, Counter] = defaultdict(Counter)
    by_section: dict[str, Counter] = defaultdict(Counter)

    for key, f in form.fields.items():
        g = gold.get(key, f.empty_value())
        if g == ANY:
            continue
        p = pred.get(key, f.empty_value())
        if is_empty(g):
            b = "true_empty" if is_empty(p) else "hallucinated"
        elif is_empty(p):
            b = "omitted"
        else:
            b = "correct" if field_match(form, key, g, p) else "wrong"
        buckets[b].append(key)
        by_kind[f.kind][b] += 1
        by_section[f.section][b] += 1

    gold_sections = {form.fields[k].section for k, v in gold.items() if not is_empty(v) and v != ANY}
    pred_sections = {form.fields[k].section for k, v in pred.items() if not is_empty(v)}

    # Does the "ungrounded" flag separate wrong answers from right ones?
    grounding = Counter()
    for key, meta in result.get("fields", {}).items():
        if is_empty(pred.get(key)) or gold.get(key) == ANY:
            continue
        g = gold.get(key, form.fields[key].empty_value())
        ok = not is_empty(g) and field_match(form, key, g, pred[key])
        grounding[("grounded" if meta.get("grounded") else "ungrounded") + ("_correct" if ok else "_incorrect")] += 1

    return {
        "counts": {b: len(ks) for b, ks in buckets.items()},
        "errors": {b: ks for b, ks in buckets.items() if b in ("wrong", "omitted", "hallucinated")},
        "by_kind": {k: dict(c) for k, c in by_kind.items()},
        "by_section": {k: dict(c) for k, c in by_section.items()},
        "sections": {"gold": sorted(gold_sections), "pred": sorted(pred_sections),
                     "tp": len(gold_sections & pred_sections), "fp": len(pred_sections - gold_sections),
                     "fn": len(gold_sections - pred_sections)},
        "grounding": dict(grounding),
        "stats": result["stats"],
    }


def _rates(c: Counter) -> dict:
    gold_set = c["correct"] + c["wrong"] + c["omitted"]
    pred_set = c["correct"] + c["wrong"] + c["hallucinated"]
    gold_empty = c["true_empty"] + c["hallucinated"]
    recall = c["correct"] / gold_set if gold_set else None
    precision = c["correct"] / pred_set if pred_set else None
    f1 = (2 * precision * recall / (precision + recall)) if precision and recall else 0.0
    return {
        "accuracy": recall,              # share of gold facts filled correctly
        "precision": precision,          # share of filled fields that are right
        "f1": f1,
        "hallucination_rate": c["hallucinated"] / gold_empty if gold_empty else None,
        "omission_rate": c["omitted"] / gold_set if gold_set else None,
        "wrong_rate": c["wrong"] / gold_set if gold_set else None,
        "n_gold": gold_set,
        "hallucinations_per_case": None,  # filled in by aggregate()
    }


def aggregate(scores: list[dict]) -> dict:
    total, kinds, sections, grounding, sec = Counter(), defaultdict(Counter), defaultdict(Counter), Counter(), Counter()
    ms, ptok, otok, errs = [], 0, 0, 0
    for s in scores:
        total.update(s["counts"])
        for k, c in s["by_kind"].items():
            kinds[k].update(c)
        for k, c in s["by_section"].items():
            sections[k].update(c)
        grounding.update(s["grounding"])
        sec.update({k: s["sections"][k] for k in ("tp", "fp", "fn")})
        ms.append(s["stats"]["ms"])
        ptok += s["stats"]["prompt_tokens"]
        otok += s["stats"]["output_tokens"]
        errs += s["stats"]["errors"]

    overall = _rates(total)
    overall["hallucinations_per_case"] = total["hallucinated"] / len(scores)
    g = grounding
    flagged = g["ungrounded_correct"] + g["ungrounded_incorrect"]
    incorrect = g["grounded_incorrect"] + g["ungrounded_incorrect"]
    ms_sorted = sorted(ms)
    return {
        "n_cases": len(scores),
        "overall": overall,
        "by_kind": {k: _rates(c) for k, c in kinds.items()},
        "by_section": {k: _rates(c) for k, c in sections.items()},
        "section_detection": {
            "precision": sec["tp"] / (sec["tp"] + sec["fp"]) if sec["tp"] + sec["fp"] else None,
            "recall": sec["tp"] / (sec["tp"] + sec["fn"]) if sec["tp"] + sec["fn"] else None,
        },
        "grounding": {
            **dict(g),
            # Of fields flagged "ungrounded", how many were actually wrong?
            "flag_precision": g["ungrounded_incorrect"] / flagged if flagged else None,
            # Of wrong fields, how many did the flag catch?
            "flag_recall": g["ungrounded_incorrect"] / incorrect if incorrect else None,
        },
        "latency_ms": {"mean": sum(ms) / len(ms), "p50": ms_sorted[len(ms) // 2], "max": ms_sorted[-1]},
        "tokens_per_case": {"prompt": ptok / len(scores), "output": otok / len(scores)},
        "schema_errors": errs,
        "counts": dict(total),
    }
