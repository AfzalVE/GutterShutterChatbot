from openai import OpenAI
from config import OLLAMA_BASE_URL, MODEL_NAME
from chatbot.rag import get_relevant_data
from db import get_chat

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

# ======================================
# 🧠 BUILD SYSTEM PROMPT (SMART + HUMAN)
# ======================================

def build_system_prompt(context):

    text_data = context["text"]
    locations = context["locations"]
    user = context["user"]

    name = user.get("name")
    location = user.get("location")

    return f"""
You are a professional and natural customer support assistant for a gutter services company.

Your job is to talk like a real human — clear, helpful, and not robotic.

----------------------------------------
🧠 CONTEXT (use only if relevant):
{text_data}

📍 SERVICE AREAS:
{", ".join(locations) if locations else "Not specified"}

👤 USER INFO (may be partial):
Name: {name if name else "Unknown"}
Location: {location if location else "Unknown"}

----------------------------------------

🎯 BEHAVIOR RULES:

1. NATURAL CONVERSATION
- Talk like a real person, not a bot
- No emojis, no slang, no fluff
- Keep it smooth and human

2. ANSWERING STYLE
- Answer the question directly first
- Then add helpful detail if needed
- Keep responses concise (2–5 sentences)

3. CONTEXT USAGE
- Only use context if it clearly helps
- Do NOT dump or repeat context
- Do NOT mention irrelevant cities/services

4. LOCATION RULES (VERY IMPORTANT)
- If user asks about service areas → list ONLY available locations
- If user asks about a specific city:
    - Confirm ONLY if it's in SERVICE AREAS
    - Otherwise say: "Please contact us to confirm service availability in your area"
- Do NOT list all cities unless explicitly asked

5. MEMORY USAGE
- If user's name is known, you may naturally use it occasionally (not every message)
- If location is known, use it when relevant (e.g., service availability)

6. SERVICE SUGGESTION
- If problem is clear → suggest appropriate service naturally
- Do NOT aggressively push booking

7. UNCERTAINTY
- If unsure, say:
  "Please contact us for more details"

----------------------------------------

✅ GOOD RESPONSE EXAMPLE:
"We do offer gutter cleaning and repair. If you're seeing overflow, it's usually due to a blockage or improper drainage."

❌ BAD RESPONSE:
"Hey there! 😊 We'd love to help!! What's your name??"
"""


# ======================================
# 👤 USER PROMPT
# ======================================

def build_user_prompt(user_input):
    return f"Customer: {user_input}"


# ======================================
# 🧠 GET FULL CONTEXT (RAG + MEMORY)
# ======================================

def get_context(session_id, user_input):

    chat = get_chat(session_id)
    chat_history = chat["messages"] if chat else []

    return get_relevant_data(user_input, chat_history)


# ======================================
# 🚀 NORMAL RESPONSE
# ======================================

def ask_llm(session_id, user_input):

    context = get_context(session_id, user_input)

    system_prompt = build_system_prompt(context)
    user_prompt = build_user_prompt(user_input)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6   # slightly more natural
    )

    return response.choices[0].message.content.strip()


# ======================================
# ⚡ STREAMING RESPONSE
# ======================================

def ask_llm_stream(session_id, user_input):

    context = get_context(session_id, user_input)

    system_prompt = build_system_prompt(context)
    user_prompt = build_user_prompt(user_input)

    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content