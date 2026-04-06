import json
import re

# ==============================
# 📂 LOAD KNOWLEDGE BASE
# ==============================
with open("data/final_cleaned_data.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)


# ==============================
# 📍 CONFIG
# ==============================
KNOWN_LOCATIONS = ["raleigh", "durham", "cary"]


# ==============================
# 🧠 TEXT CLEANING
# ==============================
def clean_text(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# ==============================
# 📍 EXTRACT LOCATIONS
# ==============================
def extract_locations(text_list):
    found = set()

    for text in text_list:
        lower = text.lower()
        for loc in KNOWN_LOCATIONS:
            if loc in lower:
                found.add(loc.capitalize())

    return list(found)


# ==============================
# 🧠 EXTRACT USER INFO FROM CHAT
# ==============================
def extract_user_memory(chat_history):
    """
    Extracts name, phone, and location from previous messages
    """

    name = None
    phone = None
    location = None

    for msg in chat_history:
        text = msg["message"]

        # NAME detection (simple heuristic)
        if not name and any(x in text.lower() for x in ["my name is", "i am", "this is"]):
            parts = text.split()
            if len(parts) >= 3:
                name = parts[-1].capitalize()

        # PHONE detection
        if not phone:
            match = re.search(r"\b\d{10}\b", text)
            if match:
                phone = match.group()

        # LOCATION detection
        if not location:
            for loc in KNOWN_LOCATIONS:
                if loc in text.lower():
                    location = loc.capitalize()

    return {
        "name": name,
        "phone": phone,
        "location": location
    }


# ==============================
# 🔍 SMART SEARCH (BETTER RAG)
# ==============================
def search_knowledge(query):
    query_words = query.lower().split()
    scored_results = []

    for items in knowledge.values():
        for item in items:
            item_lower = item.lower()

            score = sum(1 for word in query_words if word in item_lower)

            if score > 0:
                scored_results.append((score, clean_text(item)))

    # Sort by relevance
    scored_results.sort(reverse=True, key=lambda x: x[0])

    # Return top results
    return [item for _, item in scored_results[:5]]


# ==============================
# 🧠 MAIN RAG FUNCTION
# ==============================
def get_relevant_data(query, chat_history=None):
    """
    Returns structured context for LLM
    """

    # 🔍 Get relevant text
    relevant_text = search_knowledge(query)

    # 📍 Extract locations
    locations = extract_locations(relevant_text)

    # 🧠 Extract user memory
    user_memory = extract_user_memory(chat_history or [])

    # ==============================
    # 📦 STRUCTURED CONTEXT
    # ==============================
    context = {
        "text": relevant_text,
        "locations": locations,
        "user": user_memory
    }

    return context