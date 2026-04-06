from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

chats_collection = db["chats"]
leads_collection = db["leads"]


# ==============================
# 💬 CHAT FUNCTIONS
# ==============================
def create_chat(session_id):
    chats_collection.insert_one({
        "session_id": session_id,
        "messages": [],
        "created_at": datetime.utcnow()
    })


def get_chat(session_id):
    return chats_collection.find_one({"session_id": session_id})


def update_chat(session_id, role, message):
    chats_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "message": message,
                    "timestamp": datetime.utcnow()
                }
            }
        }
    )


def reset_chat(session_id):
    chats_collection.update_one(
        {"session_id": session_id},
        {"$set": {"messages": []}},
        upsert=True
    )


# ==============================
# 📞 LEAD FUNCTIONS
# ==============================
def save_lead(session_id, name, phone, problem, location):
    """
    Save structured lead with agent tracking
    """
    leads_collection.insert_one({
        "session_id": session_id,
        "name": name,
        "phone": phone,
        "location": location,
        "problem": problem,
        "agent_contacted": False,   # ✅ NEW FLAG
        "created_at": datetime.utcnow()
    })


def mark_agent_contacted(session_id):
    """
    Mark that agent has contacted the user
    """
    leads_collection.update_one(
        {"session_id": session_id},
        {"$set": {"agent_contacted": True, "contacted_at": datetime.utcnow()}}
    )


def get_lead(session_id):
    return leads_collection.find_one({"session_id": session_id})