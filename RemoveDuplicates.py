import json
import re
from difflib import SequenceMatcher

# Load your cleaned data
with open("cleaned_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)


def normalize_text(text):
    text = text.lower().strip()

    # Fix broken words (like "g utter" → "gutter")
    text = re.sub(r'\b(\w)\s+(\w)\b', r'\1\2', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove weird characters
    text = re.sub(r'[^\w\s]', '', text)

    return text


def is_duplicate(text, unique_list, threshold=0.85):
    for existing in unique_list:
        similarity = SequenceMatcher(None, text, existing).ratio()
        if similarity > threshold:
            return True
    return False


def clean_list(text_list):
    unique = []
    original_map = {}

    for text in text_list:
        if not text or len(text.strip()) < 20:
            continue

        normalized = normalize_text(text)

        if not is_duplicate(normalized, unique):
            unique.append(normalized)
            original_map[normalized] = text.strip()

    # Return original (cleaned) versions
    return list(original_map.values())


# Apply cleaning to each category
for key in data:
    if isinstance(data[key], list):
        data[key] = clean_list(data[key])


# Save cleaned file
with open("final_cleaned_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ Final cleaned data saved to final_cleaned_data.json")