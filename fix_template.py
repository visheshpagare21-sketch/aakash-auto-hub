"""
Run this from the project root:
    python fix_template.py

It patches templates/base.html in place, fixing the multi-line
{% if %} tag that breaks Django's template parser.
"""
import re
from pathlib import Path

path = Path("templates/base.html")

if not path.exists():
    raise SystemExit(f"Could not find {path.resolve()} - run this script from the project root folder.")

text = path.read_text(encoding="utf-8")

broken = (
    "{% if not business_info.phone_number and not business_info.whatsapp_number and not\n"
    "                    business_info.email %}\n"
    "                    <li class=\"footer-muted\">Contact details will appear here after they are added in Business Info.\n"
    "                    </li>\n"
    "                    {% endif %}"
)

fixed = (
    "{% if not business_info.phone_number and not business_info.whatsapp_number and not business_info.email %}\n"
    "                    <li class=\"footer-muted\">Contact details will appear here after they are added in Business Info.</li>\n"
    "                    {% endif %}"
)

if broken in text:
    text = text.replace(broken, fixed)
    path.write_text(text, encoding="utf-8")
    print("Patched successfully! The multi-line 'if' tag has been fixed.")
else:
    # Fallback: use a regex in case whitespace differs slightly
    pattern = re.compile(
        r"\{% if not business_info\.phone_number and not business_info\.whatsapp_number and not\s*\n\s*business_info\.email %\}\s*\n"
        r"(\s*)<li class=\"footer-muted\">Contact details will appear here after they are added in Business Info\.\s*\n\s*</li>",
        re.MULTILINE,
    )
    new_text, count = pattern.subn(
        lambda m: (
            "{% if not business_info.phone_number and not business_info.whatsapp_number and not business_info.email %}\n"
            + m.group(1)
            + '<li class="footer-muted">Contact details will appear here after they are added in Business Info.</li>'
        ),
        text,
    )
    if count:
        path.write_text(new_text, encoding="utf-8")
        print(f"Patched successfully via regex fallback ({count} replacement(s)).")
    else:
        print("Could not find the exact broken block automatically.")
        print("Open templates/base.html yourself, go to around line 141-145,")
        print("and make sure this whole block is on ONE line:")
        print()
        print('{% if not business_info.phone_number and not business_info.whatsapp_number and not business_info.email %}')
