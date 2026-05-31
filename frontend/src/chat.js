import React, { useState } from "react";
import { sendMessage } from "./api";

function Chat() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || isSending) {
      return;
    }

    const userMsg = { role: "user", text: trimmedMessage };

    setChat((prev) => [...prev, userMsg]);
    setMessage("");
    setIsSending(true);

    try {
      const data = await sendMessage(trimmedMessage);

      const botMsg = {
        role: "bot",
        text: data.response || data.error || "No response received",
        risk: data.risk_analysis,
      };

      setChat((prev) => [...prev, botMsg]);
    } catch (error) {
      const serverMessage =
        error.response?.data?.error ||
        error.message ||
        "Error connecting to server";

      setChat((prev) => [
        ...prev,
        {
          role: "bot",
          text: `Error connecting to server: ${serverMessage}`,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {chat.map((c, i) => (
          <div
            key={i}
            className={c.role === "user" ? "user-msg" : "bot-msg"}
          >
            <p>{c.text}</p>

            {c.risk && (
              <small>
                Risk: {c.risk.risk_level} | Blocked:{" "}
                {c.risk.blocked ? "YES" : "NO"}
              </small>
            )}
          </div>
        ))}
      </div>

      <div className="input-box">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSend();
            }
          }}
          placeholder="Type your message..."
          disabled={isSending}
        />
        <button onClick={handleSend} disabled={isSending}>
          {isSending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default Chat;
