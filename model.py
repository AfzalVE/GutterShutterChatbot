import json
from openai import OpenAI
from pymongo import MongoClient

# 🔗 Connect to Ollama
client = OpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama"
)

# 🗄️ MongoDB Setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["gutter_chatbot"]
leads_collection = db["leads"]

# 📂 Load cleaned data
with open("final_cleaned_data.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)


# 🧠 Simple keyword detection for service intent
def is_service_request(text):
    keywords = [
        "install", "clean", "repair", "replace",
        "service", "quote", "price", "help",
        "fix", "gutter", "soffit", "fascia"
    ]
    text = text.lower()
    return any(word in text for word in keywords)


# 🧠 Get relevant data
def get_relevant_data(query, data):
    results = []
    query = query.lower()

    for category, items in data.items():
        for item in items:
            if query in item.lower():
                results.append(item)

    return results[:5]


# 🧠 Build system prompt
def build_system_prompt(relevant_data):
    return f"""
You are a friendly chatbot for a gutter service company.

Use this information to answer:
{relevant_data}

RULES:
- Be short and natural
- Sound like a human assistant
- Encourage booking if relevant
- If unsure, say "Please contact us for more details"
"""


# 🤖 Ask LLM
def ask_llm(user_input):
    relevant_data = get_relevant_data(user_input, knowledge)
    system_prompt = build_system_prompt(relevant_data)

    response = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content


# 💾 Save lead to MongoDB
def save_lead(name, phone, problem):
    lead = {
        "name": name,
        "phone": phone,
        "problem": problem
    }
    leads_collection.insert_one(lead)


# 💬 Chatbot
def chatbot():
    print("👋 Hello! Welcome to Gutter Shutter Services.")
    print("💬 Ask me anything about our services.\n")

    lead_mode = False
    name = ""
    phone = ""
    problem = ""

    while True:
        user_query = input("You: ")

        if user_query.lower() in ["exit", "quit"]:
            print("👋 Thanks for visiting! Have a great day.")
            break

        # 🚨 If user wants service → start lead collection
        if is_service_request(user_query) and not lead_mode:
            print("Bot: I'd be happy to help you with that! 😊")
            print("Bot: May I have your name?")
            lead_mode = True
            problem = user_query
            continue

        # 🧾 Collect name
        if lead_mode and name == "":
            name = user_query
            print("Bot: Thanks! Can I get your phone number?")
            continue

        # 📞 Collect phone
        if lead_mode and phone == "":
            phone = user_query
            print("Bot: Got it! Could you briefly describe your issue or service needed?")
            continue

        # 🛠️ Collect problem + save
        if lead_mode and problem != "" and phone != "":
            problem = user_query

            save_lead(name, phone, problem)

            print("\nBot: ✅ Thank you! Our team will contact you shortly.")
            print("Bot: We look forward to helping you! 🙌\n")

            # Reset
            lead_mode = False
            name = ""
            phone = ""
            problem = ""
            continue

        # 🤖 Normal Q&A
        reply = ask_llm(user_query)
        print("Bot:", reply)


# 🚀 Run
if __name__ == "__main__":
    chatbot()