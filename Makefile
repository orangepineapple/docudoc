PY := venv/bin/python

.PHONY: setup dev api ui test eval generate grid-check

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

generate:         ## synthetic eval cases (see eval/generate.py)
	$(PY) eval/generate.py --n 40

eval:             ## score configs on the dev split (see eval/run.py)
	$(PY) eval/run.py --cases eval/cases/hand.jsonl eval/cases/synthetic.jsonl --split dev --run dev \
		--models qwen2.5:7b --variants v0_baseline v1_schema v2_evidence v3_select

grid-check:       ## regression gate for grid hallucination (needs `ollama serve`, ~30 min)
	$(PY) eval/grid_copy.py --variants v3_select --no-cache --max-copied 0.5
