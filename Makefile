PY := venv/bin/python

.PHONY: setup dev api ui test eval eval-variants raw-notes grid-check

setup:            ## create venv, install backend + frontend deps
	python3 -m venv venv
	$(PY) -m pip install -e "backend[dev]"
	cd frontend && npm ci

dev:              ## API on :8000 and UI on :5173 (needs `ollama serve`)
	@trap 'kill 0' INT TERM; \
	$(MAKE) api & \
	$(MAKE) ui & \
	wait

api:
	cd backend && ../$(PY) -m uvicorn formfiller.api.main:app --reload --port 8000

ui:
	cd frontend && npm run dev

test:
	cd backend && ../$(PY) -m pytest -q
	cd frontend && npm run lint && npm run build

VARIANTS := v1_schema v2_evidence v3_select
RAW_NOTES := $(wildcard eval/cases/raw_note*.json)

eval:             ## v1-v3 on the 6 notes in eval/cases/raw_note*.json (needs `ollama serve`, ~70 min)
	$(PY) eval/run.py --cases $(RAW_NOTES) --run dev \
		--models qwen2.5:7b --variants $(VARIANTS)

eval-variants:    ## v1-v3 on the notes + 25 controlled edits (eval/cases/raw_note_variants.jsonl, ~6 h)
	$(PY) eval/run.py --cases eval/cases/raw_note_variants.jsonl --run raw_notes \
		--models qwen2.5:7b --variants $(VARIANTS)

raw-notes:        ## rebuild eval/cases/raw_note_variants.jsonl from the raw notes
	$(PY) eval/raw_notes.py --write-cases

grid-check:       ## regression gate for grid hallucination (needs `ollama serve`, ~30 min)
	$(PY) eval/grid_copy.py --variants v3_select --no-cache --max-copied 0.5
