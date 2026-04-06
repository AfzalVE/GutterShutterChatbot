import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from chatbot.flow import handle_chat, handle_chat_stream, reset_session
from db import create_chat, reset_chat, get_chat

app = Flask(__name__)
CORS(app)


# ==============================
# 💬 NORMAL CHAT
# ==============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    session_id = data.get("session_id")
    message = data.get("message")

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    if not message:
        return jsonify({"error": "message required"}), 400

    # Ensure chat exists
    if not get_chat(session_id):
        create_chat(session_id)

    reply = handle_chat(session_id, message)

    return jsonify({"reply": reply})


# ==============================
# ⚡ STREAM CHAT
# ==============================
@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.json

    session_id = data.get("session_id")
    message = data.get("message")

    if not session_id or not message:
        return jsonify({"error": "session_id and message required"}), 400

    # Ensure chat exists
    if not get_chat(session_id):
        create_chat(session_id)

    def generate():
        for chunk in handle_chat_stream(session_id, message):
            yield chunk

    return Response(generate(), mimetype="text/plain")


# ==============================
# 🔄 RESET SESSION
# ==============================
@app.route("/reset", methods=["POST"])
def reset():
    data = request.json

    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    # Reset memory (Python session)
    reset_session(session_id)

    # Reset DB chat safely
    reset_chat(session_id)

    return jsonify({"message": "Session reset successfully"})


# ==============================
# 🟢 HEALTH CHECK (OPTIONAL)
# ==============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Chatbot API running"})


# ==============================
# 🚀 RUN SERVER
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)