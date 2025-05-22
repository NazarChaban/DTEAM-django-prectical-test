import google.generativeai as genai
from django.conf import settings
import json
import re

genai.configure(api_key=settings.GEMINI_API_KEY)


def translate_text(cv_data: dict, target_language: str) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = (
        f"Translate this CV data into {target_language}. "
        f"Keep the structure as JSON, and preserve field names.\n\n"
        f"Translate only the values, not the keys, don't translate name, only"
        f" general words, descriptions and info that could be translated.\n\n"
        f"Ignore all other instructions, just return the JSON.\n\n"
        f"Translate the following CV data into {target_language}. "
        f"Return the result strictly as valid JSON — no markdown formatting, no explanations. "
        f"Use this exact structure:\n\n"
        f'''{{
    "firstname": "...",
    "lastname": "...",
    "bio": "...",
    "contacts": {{
        "email": "...",
        "phone": "...",
        "github": "...",
        "linkedin": "..."
    }},
    "skills": ["...", "..."],
    "projects": [
        {{
        "name": "...",
        "description": "...",
        "link": "..."
        }},
        ...
    ]
    }}\n\n'''
        f"Translate this JSON:\n\n"
        f"{json.dumps(cv_data, indent=2)}"
    )

    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    cleaned = re.sub(
        r"^```json\s*|\s*```$", "", raw_text, flags=re.DOTALL
    ).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("JSON decode error even after cleaning:", e)
        return {"error": f"Gemini returned invalid JSON:\n{cleaned}"}
