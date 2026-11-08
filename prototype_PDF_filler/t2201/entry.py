"""
cli.py — T2201 Part B filler CLI
Usage:
    python -m t2201 notes.txt --patient "John Smith" -o filled.pdf
    python -m t2201 - --patient "John Smith"   # read from stdin
"""
import argparse
import asyncio
import sys
from extract import extract_fields
from fill_PDF import fill_pdf

TEMPLATE_PDF = "prototype_PDF_filler/t2201/t2201-fill-23e.pdf"   # blank template — keep alongside this package


async def main():

    
    with open("prototype_PDF_filler/t2201/sample_notes.txt") as f:
        raw_text = f.read()

    print(f"Extracting fields for patient: TEST")
    fields = await extract_fields(
        raw_text,
        patient_name="TEST"
    )


    import json
    # Show only non-empty fields
    non_empty = {k: v for k, v in fields.items() if v and v != "" and v is not False}
    print(json.dumps(non_empty, indent=2))

    fill_pdf(TEMPLATE_PDF, fields, "filled.pdf")

    return


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()