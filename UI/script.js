
const BASE_URL="https://afzalve-guttershutterchatbot.hf.space";
const API_URL = `${BASE_URL}/chat/stream`;
const RESET_URL = `${BASE_URL}/reset`;

// 🔐 Session
function generateSessionId() {
    return crypto.randomUUID();
}

let session_id = generateSessionId();

// 🧠 State
let isSending = false;
let controller = null;

// 🖥️ DOM
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");

// 💬 Add message
function addMessage(text, sender, isHTML = false) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);

    if (isHTML) {
        msg.innerHTML = text;
    } else {
        msg.innerText = text;
    }

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}

// ⏳ Typing animation
function showTyping(el) {
    el.innerHTML = `<span class="typing"></span>`;
}

// 🚀 Send message (STREAM)
async function sendMessage() {
    const message = input.value.trim();
    if (!message || isSending) return;

    isSending = true;

    addMessage(message, "user");
    input.value = "";

    const botMessageEl = addMessage("", "bot", true);
    showTyping(botMessageEl);

    // cancel previous request
    if (controller) controller.abort();
    controller = new AbortController();

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            signal: controller.signal,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: session_id,
                message: message
            })
        });

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;

            botMessageEl.innerText = fullText;
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (err) {
        if (err.name !== "AbortError") {
            botMessageEl.innerText = "⚠️ Server error";
        }
    }

    isSending = false;
}

// 🔄 Reset chat
async function resetChat() {
    try {
        await fetch(RESET_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: session_id
            })
        });
    } catch (e) {}

    // ✅ New session
    session_id = generateSessionId();

    chatBox.innerHTML = "";
    addMessage("New session started. How can I help?", "bot");
}

// ⌨️ Enter support
input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// 👋 Welcome
addMessage("Welcome. How can I assist you?", "bot");
