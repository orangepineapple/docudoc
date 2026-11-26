# FormFiller

Drafts the Canadian **T2201 Disability Tax Credit certificate** (Part B, the medical practitioner's section) from free-text clinical notes, using a **local LLM**. Patient notes never leave the machine.

The practitioner pastes notes and gets a draft of the form. Each answer is linked to the sentence in the notes it came from. They review and correct it, then download a filled, ready-to-sign PDF.

<!-- screenshot: docs/workspace.png -->

## Why this is harder than "LLM → JSON → PDF"

The first prototype did the obvious thing. It sent the field list to a 7B model, asked for JSON, and wrote the JSON into the PDF. It worked well enough to look convincing, which is the dangerous part. On the one case I had labelled, the output contained:

- **Inverted answers.** "Lasted 12+ months" was answered *No* when the notes say it has. The model was emitting raw PDF option codes (`/0`, `/1`), and those codes mean different things on different questions.
- **Hallucinated ratings.** When the notes rated 10 of the 28 mental-function items, the model filled in the other 18 with similar ratings.
- **Silent rendering bugs.** Dropdowns were written with their display text instead of export values. Acrobat ignored the values entirely because the CRA form also carries an XFA layer.

This version keeps JSON as the intermediate format but changes how it is produced and checked.

| Problem | Fix |
|---|---|
| Opaque option codes | The model sees readable enums (`yes`, `severe_limitations`). A codec maps them to PDF codes. All 68 radio groups were checked against the PDF's own XFA captions. |
| Free-form JSON | Ollama **constrained decoding** against a JSON Schema generated from the field map, so output is always valid. |
| No way to say "not stated" | Every choice has an explicit `not_mentioned` option, and the prompt says leaving fields empty is expected. |
| Unverifiable answers | Each answer comes with a **verbatim quote**. Quotes are fuzzy-matched against the notes. Unmatched ones are flagged in the UI, and matched ones are highlighted in the notes. |
| Long prompts for small models | A **router** call picks the relevant sections, and the large mental-functions section is split into three chunks. |
| Grid hallucination | **Select-then-fill** (`v3_select`): the model first lists the questions the notes answer, then fills only those. |
| Inconsistent answers | Deterministic **form rules**: mandatory examples, year formats, "improvement expected" ↔ year, at least 2 categories for cumulative effect, and so on. |
| Profile data in the prompt | Patient name, practitioner initials and signature block come from a profile and are never extracted. Initials are stamped on each completed section. |

## Evaluation

`eval/` is a small, honest benchmark:

- **Gold cases**
  - 1 hand-labelled case (the original sample notes).
  - Synthetic cases generated *labels first*. Coherent answers are sampled, and a local LLM writes notes in one of five styles: structured, SOAP, consult letter, terse bullets, or narrative with distractors.
  - A second LLM pass checks every gold fact is actually stated in the notes, and that nothing un-labelled leaked in. Fields that fail either check are left unscored rather than trusted.
- **Metrics**
  - Accuracy on stated facts and precision of filled answers.
  - **Hallucinations per form** (answers filled when the notes are silent).
  - Omissions and section-routing accuracy.
  - Latency and tokens.
  - How well the "no quote found" flag predicts wrong answers.
- **Configurations** cover models × pipeline variants (`v1_schema`, `v2_evidence`, `v3_select`). The original prototype prompt (`v0_baseline`, raw PDF codes in free-form JSON) was retired; its last measured numbers stay in `eval/results/hand.json`.
- **Grid hallucination probe** (`eval/grid_copy.py`, `make grid-check`): 21 variants of the hand case made by deleting or flipping one rating line in code, so gold is known by construction. On the 28-item mental-functions grid with `qwen2.5:7b`:

  | Pipeline | Invented ratings / form | Copied from a same-category item | Real ratings kept |
  |---|---:|---:|---:|
  | `v1_schema` | 13.8 | 10.3 | 200/200 |
  | `v2_evidence` | 4.5 | 3.6 | 198/200 |
  | `v3_select` (default) | 0.0 | 0.0 | 198/200 |

  Flipping one rated line changed the prediction for 9 of 17 unrated sibling items under `v1_schema` (0 under `v3_select`), which is what identifies copying as the cause. All variants derive from one patient's notes.

Results are in the app's **Evaluation** tab, and in [`eval/RESULTS.md`](eval/RESULTS.md).

## Running it

Requirements: Python 3.11+, Node 20.19+ (or 22.12+), and [Ollama](https://ollama.com) with a model pulled (`ollama pull qwen2.5:7b`).

```bash
make setup        # venv + backend + frontend deps
ollama serve      # in another terminal
make dev          # API on :8000, UI on http://localhost:5173
```

CLI:

```bash
venv/bin/python -m formfiller fill notes.txt -o draft.pdf --patient "Jane Doe" --initials AB
venv/bin/python -m formfiller extract notes.txt --variant v3_select --json result.json
```

Tests and eval:

```bash
make test                                   # 330 backend tests + frontend lint/build
make eval                                   # v1-v3 on the 6 notes in eval/cases/raw_note*.json
make eval-variants                          # v1-v3 on the notes + 25 controlled edits
make grid-check                             # grid-hallucination regression gate
```

## Layout

```
backend/formfiller/
  core/      form spec types, schema builder, codec, extraction pipeline, grounding, PDF fill
  forms/     one package per form: field map, template PDF, rules (T2201 today)
  llm/       Ollama client (native /api/chat, JSON-schema format)
  api/       FastAPI: form schema, SSE extraction stream, validate, fill, eval results
eval/        case generator, runner, metrics, cases/, results/
frontend/    React 19 + Vite 8 + Tailwind 4 review UI
prototype_PDF_filler/   the original prototype, kept for reference
```

Adding a form means adding `forms/<id>/` with a field map, the template and rules. The CPP Disability field map from the prototype is the next candidate.

## Limitations

- Synthetic notes are written by a model from the same family as the extractors, so the benchmark probably flatters them. The hand-labelled case and a manual review of samples are the reality check.
- A 7B model on a laptop takes minutes per form. The UI streams sections as they finish, but this is a drafting aid, not an instant one.
- This is a portfolio project, not a medical device. Every answer must be reviewed by the signing practitioner.
