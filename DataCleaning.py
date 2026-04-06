import json
import re

# Load your scraped data
with open("website_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

clean_data = {
    "services": set(),
    "product_info": [],
    "benefits": [],
    "locations": set(),
    "about": []
}

# Keywords to classify data
SERVICE_KEYWORDS = ["installation", "cleaning", "replacement", "service"]
PRODUCT_KEYWORDS = ["gutter shutter", "system"]
BENEFIT_KEYWORDS = ["no clog", "guarantee", "lifetime", "durable", "strong"]
LOCATION_KEYWORDS = ["raleigh", "durham", "cary", "north carolina"]

def clean_text(text):
    text = text.strip()
    
    # remove junk
    if len(text) < 20:
        return None
    if "read more" in text.lower():
        return None
    
    # remove weird characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return text

for page in raw_data:
    # Combine headings + paragraphs
    content = page["headings"] + page["paragraphs"]

    for text in content:
        text = clean_text(text)
        if not text:
            continue

        lower = text.lower()

        # Categorize
        if any(k in lower for k in SERVICE_KEYWORDS):
            clean_data["services"].add(text)

        elif any(k in lower for k in PRODUCT_KEYWORDS):
            clean_data["product_info"].append(text)

        elif any(k in lower for k in BENEFIT_KEYWORDS):
            clean_data["benefits"].append(text)

        elif any(k in lower for k in LOCATION_KEYWORDS):
            clean_data["locations"].add(text)

        else:
            clean_data["about"].append(text)

# Convert sets to lists
clean_data["services"] = list(clean_data["services"])
clean_data["locations"] = list(clean_data["locations"])

# Save cleaned data
with open("cleaned_data.json", "w", encoding="utf-8") as f:
    json.dump(clean_data, f, indent=4, ensure_ascii=False)

print("✅ Cleaned data saved to cleaned_data.json")