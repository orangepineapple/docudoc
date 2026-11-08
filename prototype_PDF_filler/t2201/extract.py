import json
import re
import asyncio
from openai import AsyncOpenAI
from field_map import FIELD_MAP

# Group fields by section
SECTIONS = {
    "vision":      {k: v for k, v in FIELD_MAP.items() if k.startswith("vision_")},
    "speaking":    {k: v for k, v in FIELD_MAP.items() if k.startswith("speaking_")},
    "hearing":     {k: v for k, v in FIELD_MAP.items() if k.startswith("hearing_")},
    "walking":     {k: v for k, v in FIELD_MAP.items() if k.startswith("walking_")},
    "eliminating": {k: v for k, v in FIELD_MAP.items() if k.startswith("eliminating_")},
    "feeding":     {k: v for k, v in FIELD_MAP.items() if k.startswith("feeding_")},
    "dressing":    {k: v for k, v in FIELD_MAP.items() if k.startswith("dressing_")},
    "mental":      {k: v for k, v in FIELD_MAP.items() if k.startswith("mental_")},
    "cumulative":  {k: v for k, v in FIELD_MAP.items() if k.startswith("cumulative_")},
    "lst":         {k: v for k, v in FIELD_MAP.items() if k.startswith("lst_")},
    "cert":        {k: v for k, v in FIELD_MAP.items() if k.startswith("cert_")},
}

def build_section_schema(section_fields: dict) -> str:
    lines = []
    for key, field in section_fields.items():
        if "patient_name" in key:
            continue
        desc = field["description"]
        ftype = field["type"]
        if ftype == "radio_group":
            opts = " | ".join(f'{v}="{label}"' for v, label in field["options"].items())
            lines.append(f'  "{key}": ""  // {desc}. Options: {opts}')
        elif ftype == "choice":
            opts = " | ".join(f'"{o}"' for o in field["options"])
            lines.append(f'  "{key}": ""  // {desc}. Options: {opts}')
        elif ftype == "checkbox":
            lines.append(f'  "{key}": false  // {desc}. Set true to check.')
        else:
            lines.append(f'  "{key}": ""  // {desc}')
    return "{\n" + "\n".join(lines) + "\n}"


async def extract_section(
    client: AsyncOpenAI,
    model: str,
    section_name: str,
    section_fields: dict,
    doctor_notes: str,
) -> dict:
    schema = build_section_schema(section_fields)

    system_prompt = f"""You are filling the {section_name.upper()} section of a Canadian T2201 
Disability Tax Credit form based on doctor's notes.

If the notes contain NO information about {section_name}, return an empty JSON object: {{}}

Otherwise extract relevant information and return ONLY valid JSON matching this schema:
{schema}

Rules:
- Return ONLY valid JSON. No explanation, no markdown, no code fences.
- Leave fields as "" or false if not mentioned in the notes.
- For radio fields use the option code exactly e.g. "/0" or "/1"
- For year fields use 4-digit year only e.g. "2019"
- For improvement questions check exactly ONE of _yes, _no, or _unsure"""

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": doctor_notes},
        ],
        max_tokens=1024,
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

    #TODO make it automatically run for multiple notes
    with open(f"prototype_PDF_filler/t2201/test_outputs/{section_name}.txt", 'w') as f:
        f.write(raw)

    if not raw or raw == "{}":
        print(f"  [{section_name}] skipped — not relevant")
        return {}

    result = json.loads(raw)
    print(f"  [{section_name}] filled {len([v for v in result.values() if v and v != ''])} fields")
    

    
    return result

async def extract_fields(
    doctor_notes: str,
    model: str = "qwen2.5:7b",
    base_url: str = "http://localhost:11434/v1",
    patient_name: str = "",
) -> dict:
    client = AsyncOpenAI(base_url=base_url, api_key="none")

    print("Extracting sections...")

    # Run all sections concurrently
    tasks = {
        name: extract_section(client, model, name, fields, doctor_notes)
        for name, fields in SECTIONS.items()
    }
    results = await asyncio.gather(*tasks.values())

    # Merge all section results into one flat dict
    merged = {}
    for result in results:
        merged.update(result)

    # Stamp patient name on every page
    if patient_name:
        for key in FIELD_MAP:
            if "patient_name" in key:
                merged[key] = patient_name

    return merged