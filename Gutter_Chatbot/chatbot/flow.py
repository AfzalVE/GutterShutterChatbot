from chatbot.llm import ask_llm, ask_llm_stream
from chatbot.intent import is_service_request, is_yes, is_no
from db import get_chat, create_chat, update_chat, save_lead
import re

sessions = {}


# ==============================
# 🧠 INIT SESSION
# ==============================
def init_session(session_id):
    sessions[session_id] = {
        "lead_mode": False,
        "step": None,
        "name": None,
        "phone": None,
        "location": None,
        "problem": None,
        "asked_for_booking": False
    }


def reset_session(session_id):
    if session_id in sessions:
        del sessions[session_id]


# ==============================
#  MEMORY EXTRACTION
# ==============================
def update_session_memory(session, message):

    text = message.lower()

    # NAME
    if not session["name"] and any(x in text for x in ["my name is", "i am", "this is"]):
        parts = message.split()
        if len(parts) >= 3:
            session["name"] = parts[-1]

    # PHONE
    if not session["phone"]:
        import re
        match = re.search(r"\b\d{10}\b", message)
        if match:
            session["phone"] = match.group()

    # LOCATION (ONLY EXPLICIT)
    if not session["location"]:
        explicit = ["i am in", "i live in", "located in", "based in"]
        if any(p in text for p in explicit):
            for loc in ["raleigh", "durham", "cary"]:
                if loc in text:
                    session["location"] = loc.capitalize()


# ==============================
#  BOOKING INTENT
# ==============================
def is_booking_intent(text):
    keywords = [
        "book", "booking",
        "schedule", "appointment",
        "i want service",
        "send someone",
        "get service",
        "come check",
        "visit my home"
    ]
    return any(k in text.lower() for k in keywords)


# ==============================
#  LEAD FLOW HANDLER (FIXED)
# ==============================
def handle_lead_flow(session_id, session, message):


    msg = message.strip()

    # ==============================
    # STEP 1: NAME
    # ==============================
    if session["name"] is None:

        if not re.match(r"^[A-Za-z ]{2,}$", msg):
            reply = "Please enter a valid name (only letters)."
            update_chat(session_id, "bot", reply)
            return reply

        session["name"] = msg
        reply = "Got it. What's the best phone number to reach you?"
        update_chat(session_id, "bot", reply)
        return reply

    # ==============================
    # STEP 2: PHONE
    # ==============================
    elif session["phone"] is None:

        if not re.match(r"^\d{10}$", msg):
            reply = "Please enter a valid 10-digit phone number."
            update_chat(session_id, "bot", reply)
            return reply

        session["phone"] = msg
        reply = "Thanks. Which city are you located in?"
        update_chat(session_id, "bot", reply)
        return reply

    # ==============================
    # STEP 3: LOCATION
    # ==============================
    elif session["location"] is None:

        # Reject numbers or very short inputs
        if msg.isdigit() or len(msg) < 2:
            reply = "Please enter a valid city name."
            update_chat(session_id, "bot", reply)
            return reply

        session["location"] = msg
        reply = "Understood. What issue are you facing with your gutters?"
        update_chat(session_id, "bot", reply)
        return reply

    # ==============================
    # STEP 4: PROBLEM
    # ==============================
    elif session["problem"] is None:

        if len(msg) < 3:
            reply = "Please briefly describe your issue."
            update_chat(session_id, "bot", reply)
            return reply

        session["problem"] = msg

        save_lead(
            session_id,
            session["name"],
            session["phone"],
            session["problem"],
            session["location"]
        )

        reply = "Thanks. Our team will contact you shortly to schedule the service."
        update_chat(session_id, "bot", reply)

        reset_session(session_id)
        return reply

# ======================================
#  NORMAL CHAT
# ======================================
def handle_chat(session_id, message):

    # Ensure DB chat
    if not get_chat(session_id):
        create_chat(session_id)

    # Init session
    if session_id not in sessions:
        init_session(session_id)

    session = sessions[session_id]

    # ✅ FIX: ONLY update memory OUTSIDE lead flow
    if not session["lead_mode"]:
        update_session_memory(session, message)

    # Save user message
    update_chat(session_id, "user", message)

    # ==============================
    # 🧾 LEAD FLOW (TOP PRIORITY)
    # ==============================
    if session["lead_mode"]:
        return handle_lead_flow(session_id, session, message)

    # ==============================
    #  DIRECT BOOKING TRIGGER
    # ==============================
    if is_booking_intent(message):

        session["lead_mode"] = True

        if session["name"] is None:
            reply = "Sure. Can I have your name?"
        elif session["phone"] is None:
            reply = "Can I get your phone number?"
        elif session["location"] is None:
            reply = "Which city are you located in?"
        else:
            reply = "What issue are you facing with your gutters?"

        update_chat(session_id, "bot", reply)
        return reply

    # ==============================
    # 🟢 YES → START BOOKING
    # ==============================
    if is_yes(message) and session["asked_for_booking"]:

        session["lead_mode"] = True

        if session["name"] is None:
            reply = "Sure. Can I have your name?"
        elif session["phone"] is None:
            reply = "Can I get your phone number?"
        elif session["location"] is None:
            reply = "Which city are you located in?"
        else:
            reply = "What issue are you facing with your gutters?"

        update_chat(session_id, "bot", reply)
        return reply

    # ==============================
    # 👎 USER SAID NO
    # ==============================
    if is_no(message):
        session["asked_for_booking"] = False

    # ==============================
    # 🤖 LLM RESPONSE
    # ==============================
    reply = ask_llm(session_id, message)
    update_chat(session_id, "bot", reply)

    # ==============================
    # 🧠 SMART BOOKING TRIGGER
    # ==============================
    if is_service_request(message) and not session["asked_for_booking"]:

        follow_up = "\n\nIf you'd like, I can help schedule a service for you."

        session["asked_for_booking"] = True
        update_chat(session_id, "bot", follow_up)

        return reply + follow_up

    return reply


# ======================================
# ⚡ STREAMING VERSION
# ======================================
def handle_chat_stream(session_id, message):

    if not get_chat(session_id):
        create_chat(session_id)

    if session_id not in sessions:
        init_session(session_id)

    session = sessions[session_id]

    # ✅ FIX: block memory during lead flow
    if not session["lead_mode"]:
        update_session_memory(session, message)

    update_chat(session_id, "user", message)

    # ==============================
    # 🧾 LEAD FLOW
    # ==============================
    if session["lead_mode"]:
        reply = handle_lead_flow(session_id, session, message)
        yield reply
        return

    # ==============================
    # 🚀 BOOKING INTENT
    # ==============================
    if is_booking_intent(message):

        session["lead_mode"] = True

        if session["name"] is None:
            reply = "Sure. Can I have your name?"
        elif session["phone"] is None:
            reply = "Can I get your phone number?"
        elif session["location"] is None:
            reply = "Which city are you located in?"
        else:
            reply = "What issue are you facing with your gutters?"

        update_chat(session_id, "bot", reply)
        yield reply
        return

    # ==============================
    # 🟢 YES
    # ==============================
    if is_yes(message) and session["asked_for_booking"]:
        session["lead_mode"] = True
        reply = "Sure. Can I have your name?"
        update_chat(session_id, "bot", reply)
        yield reply
        return

    # ==============================
    # 🤖 STREAM LLM
    # ==============================
    full_reply = ""

    for chunk in ask_llm_stream(session_id, message):
        full_reply += chunk
        yield chunk

    update_chat(session_id, "bot", full_reply)

    # ==============================
    # 🧠 BOOKING TRIGGER
    # ==============================
    if is_service_request(message) and not session["asked_for_booking"]:

        follow_up = "\n\nIf you'd like, I can help schedule a service for you."

        session["asked_for_booking"] = True
        update_chat(session_id, "bot", follow_up)

        yield follow_up  