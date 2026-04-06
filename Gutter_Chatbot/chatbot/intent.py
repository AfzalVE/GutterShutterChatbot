# ==============================
# 🧠 SERVICE INTENT
# ==============================
def is_service_request(text):
    keywords = [
        "install", "installation",
        "clean", "cleaning",
        "repair", "fix",
        "replace", "replacement",
        "quote", "price", "cost",
        "service", "help",
        "gutter", "soffit", "fascia",
        "leak", "drip", "overflow"
    ]
    return any(word in text.lower() for word in keywords)


# ==============================
# 📍 LOCATION INTENT
# ==============================
def is_location_query(text):
    keywords = [
        "where do you serve",
        "service area",
        "locations",
        "which cities",
        "do you work in",
        "available in",
        "coverage",
        "do you serve"
    ]
    return any(k in text.lower() for k in keywords)


# ==============================
# 👍 YES / ACCEPTANCE
# ==============================
def is_yes(text):
    return text.lower().strip() in [
        "yes", "yeah", "yup", "sure", "ok", "okay", "please do"
    ]


# ==============================
# 👎 NO / REJECTION
# ==============================
def is_no(text):
    return text.lower().strip() in [
        "no", "nope", "not now", "later"
    ]