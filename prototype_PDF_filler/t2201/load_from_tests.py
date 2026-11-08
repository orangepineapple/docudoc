# test_fill.py  — place this in your prototype_PDF_filler folder
import json
import os
from fill_PDF import fill_pdf
from field_map import FIELD_MAP
from summary import print_summary

TEST_OUTPUTS_DIR = "prototype_PDF_filler/t2201/test_outputs"
TEMPLATE_PDF = "prototype_PDF_filler/t2201/t2201-fill-23e.pdf"

def load_test_outputs(directory: str) -> dict:
    merged = {}
    
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue
        
        filepath = os.path.join(directory, filename)
        with open(filepath) as f:
            raw = f.read().strip()
        
        if not raw or raw == "{}":
            print(f"  [{filename}] empty, skipping")
            continue
        
        try:
            data = json.loads(raw)
            merged.update(data)
            filled = len([v for v in data.values() if v and v != "" and v is not False])
            print(f"  [{filename}] loaded {filled} fields")
        except json.JSONDecodeError as e:
            print(f"  [{filename}] JSON error: {e}")
    
    return merged

print("Loading test outputs...")
fields = load_test_outputs(TEST_OUTPUTS_DIR)

# Stamp patient name on every page
patient_name = "Test Patient"
for key in FIELD_MAP:
    if "patient_name" in key:
        fields[key] = patient_name

print(f"\nTotal fields loaded: {len(fields)}")
print("Filling PDF...")

fill_pdf(TEMPLATE_PDF, fields, "test_filled.pdf")
print_summary(fields, "TEST", "test_filled.pdf")